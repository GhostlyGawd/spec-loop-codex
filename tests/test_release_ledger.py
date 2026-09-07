"""Release-history tests use synthetic observations and disposable local projects."""
import argparse
from datetime import timedelta
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from test_spec_loop import PLUGIN, loop

module = importlib.util.spec_from_file_location("release_ledger", PLUGIN / "scripts/release_ledger.py")
ledger = importlib.util.module_from_spec(module)
module.loader.exec_module(ledger)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        shutil.copytree(PLUGIN / "examples/reading-list", self.root)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.note = ".spec-loop/artifacts/synthetic-observation.md"
        (self.root / self.note).write_text("Synthetic evidence for a software test. No actual user or deployment.\n")
        loop.run_check(self.root, argparse.Namespace(change="CHG-001", check="CHK-001", observer="test"))
        for check in ("CHK-002", "CHK-003"):
            loop.record_manual(self.root, argparse.Namespace(change="CHG-001", check=check,
                observer="test", result="pass", note="Synthetic fixture only", artifact=self.note))

    def seal(self, release="REL-001", change="CHG-001"):
        return ledger.seal(loop, self.root, argparse.Namespace(change=change, release=release,
            target="synthetic-local", artifact="app.py", receipt=self.note,
            authority_ref="test fixture; no service action", observer="test"))

    def observe(self, release="REL-001", result="pass", check="CHK-004"):
        clock = loop.now()
        return ledger.observe(loop, self.root, argparse.Namespace(release=release, check=check,
            result=result, observer="test", note="Synthetic result; no real study", artifact=self.note,
            window_start=loop.stamp(clock-timedelta(minutes=1)), window_end=loop.stamp(clock), cohort="synthetic fixture"))

    def test_frozen_release_survives_source_specs_and_original_file_changes(self):
        self.seal()
        (self.root / "app.py").write_text("# a different candidate\n")
        (self.root / self.note).unlink()
        (self.root / ".spec-loop/project.json").unlink()
        (self.root / ".spec-loop/artifacts/release-plan.md").unlink()
        record, _ = ledger.read_release(loop, self.root, "REL-001")
        self.assertEqual(record["target"], "synthetic-local")

    def test_dependency_contracts_and_evidence_are_frozen_together(self):
        change = loop.read_json(self.root / ".spec-loop/changes/CHG-001.json")
        change.update(id="CHG-002", depends_on=["CHG-001"])
        loop.atomic_json(self.root / ".spec-loop/changes/CHG-002.json", change)
        loop.run_check(self.root, argparse.Namespace(change="CHG-002", check="CHK-001", observer="test"))
        for check in ("CHK-002", "CHK-003"):
            loop.record_manual(self.root, argparse.Namespace(change="CHG-002", check=check,
                observer="test", result="pass", note="Synthetic dependency fixture", artifact=self.note))
        self.seal(change="CHG-002")
        shutil.rmtree(self.root / ".spec-loop/changes")
        _, entries = ledger.read_release(loop, self.root, "REL-001")
        self.assertEqual(set(entries), {"CHG-001", "CHG-002"})

    def test_cannot_seal_failed_or_stale_candidate(self):
        (self.root / "app.py").write_text("# changed after tests\n")
        with self.assertRaisesRegex(loop.LoopError, "Release gate failed"):
            self.seal()
        self.assertFalse((self.root / ".spec-loop/releases/REL-001.json").exists())

    def test_existing_release_id_is_preserved(self):
        self.seal()
        path = self.root / ".spec-loop/releases/REL-001.json"
        before = path.read_bytes()
        with self.assertRaisesRegex(loop.LoopError, "already exists"):
            self.seal()
        self.assertEqual(before, path.read_bytes())

    def test_modified_record_and_bad_schema_fail(self):
        self.seal()
        path = self.root / ".spec-loop/releases/REL-001.json"
        record = loop.read_json(path)
        record["target"] = "different"
        loop.atomic_json(path, record)
        with self.assertRaisesRegex(loop.LoopError, "digest does not match"):
            ledger.read_release(loop, self.root, "REL-001")
        record["schema_version"] = 9
        loop.atomic_json(path, record)
        with self.assertRaisesRegex(loop.LoopError, "Invalid archive"):
            ledger.read_release(loop, self.root, "REL-001")

    def test_changed_frozen_attachment_rejected_even_with_new_envelope_digest(self):
        self.seal()
        path = self.root / ".spec-loop/releases/REL-001.json"
        record = loop.read_json(path)
        record["files"][0]["content_base64"] = "Y2hhbmdlZA=="
        record.pop("digest")
        loop.atomic_json(path, ledger.with_digest(loop, record))
        with self.assertRaisesRegex(loop.LoopError, "attachment size or digest"):
            ledger.read_release(loop, self.root, "REL-001")

    def test_outcome_is_missing_until_recorded_and_survives_source_changes(self):
        self.seal()
        self.assertFalse(ledger.learn(loop, self.root, "REL-001")["passed"])
        (self.root / "app.py").write_text("# later version\n")
        self.observe()
        (self.root / self.note).unlink()
        self.assertTrue(ledger.learn(loop, self.root, "REL-001")["passed"])

    def test_later_failed_outcome_overrides_pass(self):
        self.seal()
        self.observe()
        self.observe(result="fail")
        report = ledger.learn(loop, self.root, "REL-001")
        self.assertFalse(report["passed"])
        self.assertEqual(report["checks"]["CHK-004"], "fail")

    def test_outcome_cannot_be_reused_for_another_release(self):
        self.seal()
        self.seal("REL-002")
        self.observe()
        self.assertFalse(ledger.learn(loop, self.root, "REL-002")["passed"])
        old = next((self.root / ".spec-loop/releases/REL-001/observations").glob("*.json"))
        target = self.root / ".spec-loop/releases/REL-002/observations" / old.name
        target.parent.mkdir(parents=True)
        shutil.copyfile(old, target)
        with self.assertRaisesRegex(loop.LoopError, "does not match"):
            ledger.learn(loop, self.root, "REL-002")

    def test_acceptance_check_cannot_be_recorded_as_outcome(self):
        self.seal()
        with self.assertRaisesRegex(loop.LoopError, "manual outcome"):
            self.observe(check="CHK-001")

    def test_frozen_evidence_expiry_is_evaluated_at_seal_time(self):
        self.seal()
        record, _ = ledger.read_release(loop, self.root, "REL-001")
        # Simulate later wall-clock time without changing the frozen input record.
        original = loop.now
        try:
            loop.now = lambda: original() + timedelta(days=400)
            ledger.validate_release(loop, record, "REL-001")
        finally:
            loop.now = original

    def test_doctor_does_not_write_or_run_product_checks(self):
        def inventory():
            return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        before = inventory()
        report = loop.doctor(self.root)
        self.assertTrue(report["passed"])
        self.assertFalse(report["mutations"])
        self.assertEqual(before, inventory())

    def test_doctor_reports_invalid_project(self):
        (self.root / ".spec-loop/project.json").write_text("{}")
        self.assertFalse(loop.doctor(self.root)["passed"])

    def test_release_cli_loads_the_module(self):
        self.seal()
        result = subprocess.run(["python3", str(PLUGIN / "scripts/spec_loop.py"), "--root", str(self.root),
                                 "release-inspect", "REL-001"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(json.loads(result.stdout)["passed"])


class PackageTests(unittest.TestCase):
    def test_package_repeats_and_excludes_untracked_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "spec-loop"
            root.mkdir()
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            for key, value in (("user.name", "Test"), ("user.email", "test@local.invalid")):
                subprocess.run(["git", "-C", str(root), "config", key, value], check=True)
            (root / ".codex-plugin").mkdir()
            (root / ".codex-plugin/plugin.json").write_text('{"name":"spec-loop","version":"0.2.0"}')
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
            (root / "not-source.txt").write_text("Untracked fixture")
            script = PLUGIN / "scripts/package.py"
            archives = [Path(directory) / "one.tar.gz", Path(directory) / "two.tar.gz"]
            for output in archives:
                result = subprocess.run(["python3", str(script), "--root", str(root), "--output", str(output)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(archives[0].read_bytes(), archives[1].read_bytes())
            import tarfile
            with tarfile.open(archives[0]) as archive:
                self.assertNotIn("spec-loop/not-source.txt", archive.getnames())
            (root / ".codex-plugin/plugin.json").write_text("{}")
            result = subprocess.run(["python3", str(script), "--root", str(root), "--output", str(Path(directory)/"dirty.tar.gz")], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("Commit tracked changes", result.stdout)


if __name__ == "__main__":
    unittest.main()
