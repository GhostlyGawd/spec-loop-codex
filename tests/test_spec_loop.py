"""Behavior tests on disposable projects; no live services or credentials."""
import argparse
from datetime import timedelta
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("spec_loop", PLUGIN / "scripts/spec_loop.py")
loop = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(PLUGIN / "scripts"))
sys.modules["spec_loop"] = loop
spec.loader.exec_module(loop)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        shutil.copytree(PLUGIN / "examples/reading-list", self.root)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def change(self, change_id="CHG-001"):
        return loop.read_json(self.root / ".spec-loop/changes" / (change_id + ".json"))

    def save_change(self, change):
        loop.atomic_json(self.root / ".spec-loop/changes" / (change["id"] + ".json"), change)

    def run_check(self, check_id="CHK-001", change_id="CHG-001"):
        return loop.run_check(self.root, argparse.Namespace(change=change_id, check=check_id, observer="synthetic-test"))

    def manual(self, check_id, result="pass"):
        relative = ".spec-loop/artifacts/test-observation-" + check_id + ".md"
        (self.root / relative).write_text("Synthetic observation used only by the tool test suite.\n")
        return loop.record_manual(self.root, argparse.Namespace(change="CHG-001", check=check_id,
            observer="synthetic-test", note="Synthetic test fixture; no real review or release.",
            artifact=relative, result=result))

    def verify(self):
        return loop.gate(self.root, "CHG-001", "verify")

    def test_ready_and_automated_verification_work(self):
        self.assertTrue(loop.gate(self.root, "CHG-001", "ready")["passed"])
        self.assertEqual(self.run_check()["result"], "pass")
        self.assertTrue(self.verify()["passed"])

    def test_missing_evidence_does_not_pass(self):
        self.assertEqual(self.verify()["checks"]["CHK-001"], "missing")
        self.assertFalse(self.verify()["passed"])

    def test_source_edit_stales_evidence(self):
        self.run_check()
        with (self.root / "app.py").open("a") as stream:
            stream.write("\n# A later source change\n")
        self.assertEqual(self.verify()["checks"]["CHK-001"], "stale")

    def test_contract_edit_stales_evidence(self):
        self.run_check()
        change = self.change()
        change["intent"]["outcome"] = "A different outcome"
        self.save_change(change)
        self.assertEqual(self.verify()["checks"]["CHK-001"], "stale")

    def test_artifact_edit_stales_evidence(self):
        self.run_check()
        (self.root / ".spec-loop/artifacts/release-plan.md").write_text("Changed plan\n")
        self.assertEqual(self.verify()["checks"]["CHK-001"], "stale")

    def test_policy_edit_stales_evidence(self):
        self.run_check()
        path = self.root / ".spec-loop/project.json"
        config = loop.read_json(path)
        config["evidence_ttl_hours"] = 12
        loop.atomic_json(path, config)
        self.assertEqual(self.verify()["checks"]["CHK-001"], "stale")

    def test_phase_is_not_proof_and_does_not_change_contract(self):
        self.run_check()
        change = self.change()
        change["phase"] = "released"
        self.save_change(change)
        self.assertTrue(self.verify()["passed"])
        self.assertFalse(loop.gate(self.root, "CHG-001", "release")["passed"])

    def test_later_failure_cannot_reuse_older_pass(self):
        self.run_check()
        record_path = next((self.root / ".spec-loop/evidence/CHG-001").glob("*.json"))
        record = loop.read_json(record_path)
        record.update(id="EV-" + "b" * 32, result="fail", exit_code=1,
            observed_at=loop.stamp(loop.now() + timedelta(seconds=1)))
        loop.atomic_json(record_path.parent / (record["id"] + ".json"), record)
        self.assertEqual(self.verify()["checks"]["CHK-001"], "fail")

    def test_expired_evidence_fails(self):
        self.run_check()
        path = next((self.root / ".spec-loop/evidence/CHG-001").glob("*.json"))
        record = loop.read_json(path)
        record.update(observed_at=loop.stamp(loop.now()-timedelta(hours=2)),
            expires_at=loop.stamp(loop.now()-timedelta(hours=1)))
        loop.atomic_json(path, record)
        self.assertEqual(self.verify()["checks"]["CHK-001"], "expired")

    def test_future_timestamp_is_invalid(self):
        self.run_check()
        path = next((self.root / ".spec-loop/evidence/CHG-001").glob("*.json"))
        record = loop.read_json(path)
        record["observed_at"] = loop.stamp(loop.now()+timedelta(days=1))
        loop.atomic_json(path, record)
        self.assertEqual(self.verify()["checks"]["CHK-001"], "invalid timestamp")

    def test_incomplete_manual_release_blocks(self):
        self.run_check()
        self.manual("CHK-002")
        report = loop.gate(self.root, "CHG-001", "release")
        self.assertFalse(report["passed"])
        self.assertEqual(report["checks"]["CHK-003"], "missing")

    def test_release_and_learning_require_distinct_evidence(self):
        self.run_check()
        self.manual("CHK-002")
        self.manual("CHK-003")
        self.assertTrue(loop.gate(self.root, "CHG-001", "release")["passed"])
        self.assertFalse(loop.gate(self.root, "CHG-001", "learn")["passed"])
        self.manual("CHK-004")
        self.assertTrue(loop.gate(self.root, "CHG-001", "learn")["passed"])

    def test_modified_observation_is_rejected(self):
        self.run_check()
        self.manual("CHK-002")
        self.manual("CHK-003")
        (self.root / ".spec-loop/artifacts/test-observation-CHK-002.md").write_text("Changed\n")
        report = loop.gate(self.root, "CHG-001", "release")
        self.assertEqual(report["checks"]["CHK-002"], "observation artifact changed or missing")

    def test_manual_record_cannot_replace_automated_result(self):
        with self.assertRaisesRegex(loop.LoopError, "Automated checks require run"):
            self.manual("CHK-001")

    def test_criterion_without_check_blocks_ready(self):
        change = self.change()
        change["checks"][0]["covers"].remove("AC-003")
        self.save_change(change)
        self.assertIn("AC-003: no acceptance check", loop.gate(self.root, "CHG-001", "ready")["errors"])

    def test_unknown_and_duplicate_ids_are_rejected(self):
        change = self.change()
        change["requirements"][0]["source_ids"] = ["SRC-999"]
        change["requirements"][1]["criteria"][0]["id"] = "AC-001"
        self.save_change(change)
        report = loop.gate(self.root, "CHG-001", "ready")
        self.assertTrue(any("unknown source" in error for error in report["errors"]))
        self.assertIn("Duplicate criterion ID", report["errors"])

    def test_task_and_change_cycles_are_rejected(self):
        change = self.change()
        change["tasks"][0]["depends_on"] = ["TASK-001"]
        change["depends_on"] = ["CHG-001"]
        self.save_change(change)
        report = loop.gate(self.root, "CHG-001", "ready")
        self.assertIn("Task dependency cycle", report["errors"])
        self.assertIn("Change dependency cycle", report["errors"])

    def test_high_risk_has_critical_floor(self):
        change = self.change()
        change["risk"] = "high"
        self.save_change(change)
        report = loop.gate(self.root, "CHG-001", "ready")
        self.assertEqual(report["profile"], "critical")
        self.assertFalse(report["passed"])
        self.assertTrue(any("security" in error for error in report["errors"]))

    def test_high_impact_open_assumption_blocks(self):
        change = self.change()
        change["assumptions"][0].update(impact="high", status="open")
        self.save_change(change)
        self.assertTrue(any("assumption is open" in x for x in loop.gate(self.root,"CHG-001","ready")["errors"]))

    def test_dependency_change_stales_consumer_and_impact_is_transitive(self):
        child = self.change()
        child.update(id="CHG-002", depends_on=["CHG-001"])
        self.save_change(child)
        grandchild = self.change()
        grandchild.update(id="CHG-003", depends_on=["CHG-002"])
        self.save_change(grandchild)
        self.run_check(change_id="CHG-003")
        parent = self.change()
        parent["intent"]["outcome"] = "Changed dependency outcome"
        self.save_change(parent)
        self.assertEqual(loop.gate(self.root,"CHG-003","verify")["checks"]["CHK-001"], "stale")
        self.assertEqual(loop.impact(self.root,"CHG-001")["review"], ["CHG-002","CHG-003"])

    def test_unrelated_draft_does_not_block_valid_change(self):
        loop.new_change(self.root, argparse.Namespace(change="CHG-009",title="Draft",risk="low"))
        self.assertTrue(loop.gate(self.root,"CHG-001","ready")["passed"])
        self.assertFalse(loop.gate(self.root,"CHG-009","ready")["passed"])

    def test_init_and_new_never_overwrite(self):
        old = (self.root / ".spec-loop/project.json").read_bytes()
        with self.assertRaises(loop.LoopError):
            loop.create_project(self.root,argparse.Namespace(name="Other",profile="quick"))
        with self.assertRaises(loop.LoopError):
            loop.new_change(self.root,argparse.Namespace(change="CHG-001",title="Other",risk="low"))
        self.assertEqual(old,(self.root / ".spec-loop/project.json").read_bytes())

    def test_checkpoint_detects_conflict_and_stale_source(self):
        args = argparse.Namespace(change="CHG-001",expect_revision=0,summary="Checked",next_action="Review",blocker=[])
        result = loop.checkpoint(self.root,args)
        self.assertEqual(result["revision"],1)
        with self.assertRaisesRegex(loop.LoopError,"Checkpoint conflict"):
            loop.checkpoint(self.root,args)
        ctxargs=argparse.Namespace(change="CHG-001",max_chars=None)
        self.assertFalse(loop.context(self.root,ctxargs)["checkpoint_stale"])
        change = self.change()
        change["intent"]["outcome"] = "Updated intent after the checkpoint"
        self.save_change(change)
        self.assertTrue(loop.context(self.root,ctxargs)["checkpoint_stale"])
        args.expect_revision = 1
        loop.checkpoint(self.root,args)
        self.assertFalse(loop.context(self.root,ctxargs)["checkpoint_stale"])
        (self.root/"new-file.txt").write_text("New source\n")
        self.assertTrue(loop.context(self.root,ctxargs)["checkpoint_stale"])

    def test_active_lock_blocks_a_write(self):
        with loop.writer(self.root):
            with self.assertRaisesRegex(loop.LoopError,"Another write"):
                loop.new_change(self.root,argparse.Namespace(change="CHG-002",title="Other",risk="low"))

    def test_context_budget_does_not_silently_truncate(self):
        with self.assertRaisesRegex(loop.LoopError,"No constraints were silently dropped"):
            loop.context(self.root,argparse.Namespace(change="CHG-001",max_chars=100))

    def test_parent_and_symlink_paths_are_rejected(self):
        with self.assertRaises(loop.LoopError):
            loop.inside(self.root,"../outside")
        (self.root/"link").symlink_to(self.root/"app.py")
        with self.assertRaises(loop.LoopError):
            loop.snapshot(self.root)

    def test_source_mutation_during_check_is_invalid(self):
        change = self.change()
        change["checks"][0]["argv"] = [sys.executable,"-c","from pathlib import Path; Path('app.py').write_text('# changed')"]
        self.save_change(change)
        self.assertEqual(self.run_check()["result"],"invalid")

    def test_nonzero_command_records_failure(self):
        change=self.change()
        change["checks"][0]["argv"]=[sys.executable,"-c","raise SystemExit(7)"]
        self.save_change(change)
        result=self.run_check()
        self.assertEqual(result["result"],"fail")
        self.assertEqual(result["exit_code"],7)
        self.assertFalse(self.verify()["passed"])

    def test_timeout_is_not_a_pass(self):
        change=self.change()
        change["checks"][0].update(argv=[sys.executable,"-c","import time; time.sleep(3)"],timeout_seconds=1)
        self.save_change(change)
        self.assertEqual(self.run_check()["result"],"timeout")
        self.assertEqual(self.verify()["checks"]["CHK-001"],"timeout")

    def test_unknown_schema_and_malformed_evidence_fail_closed(self):
        change=self.change()
        change["schema_version"]=999
        self.save_change(change)
        with self.assertRaises(loop.LoopError):
            loop.gate(self.root,"CHG-001","ready")
        change["schema_version"]=1
        self.save_change(change)
        folder=self.root/".spec-loop/evidence/CHG-001"
        folder.mkdir(parents=True)
        (folder/"bad.json").write_text("{}")
        with self.assertRaises(loop.LoopError):
            self.verify()

    def test_command_arguments_do_not_expand_as_shell_code(self):
        change=self.change()
        literal="$(touch should-not-exist)"
        change["checks"][0]["argv"]=[sys.executable,"-c","import sys; assert sys.argv[1].startswith('$(')",literal]
        self.save_change(change)
        self.assertEqual(self.run_check()["result"],"pass")
        self.assertFalse((self.root/"should-not-exist").exists())

    def test_raw_output_is_not_retained(self):
        change=self.change()
        marker="SYNTHETIC_PRIVATE_OUTPUT_123"
        change["checks"][0]["argv"]=[sys.executable,"-c","print('SYNTHETIC_'+'PRIVATE_OUTPUT_123')"]
        self.save_change(change)
        self.run_check()
        record_path=next((self.root/".spec-loop/evidence/CHG-001").glob("*.json"))
        self.assertNotIn(marker,record_path.read_text())
        self.assertGreater(loop.read_json(record_path)["output_bytes"],0)


if __name__ == "__main__":
    unittest.main()
