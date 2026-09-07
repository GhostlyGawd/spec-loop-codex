"""Background review invariants; synthetic inputs, no network or real telemetry."""
import argparse
import copy
from datetime import timedelta
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_spec_loop import PLUGIN, loop
from test_product import intent
import product
import review_runner as runner


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        self.output = Path(self.temp.name) / 'reports'
        shutil.copytree(PLUGIN / 'examples/reading-list', self.root)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.config = {'schema_version': 1, 'mode': 'exchange', 'product_file': 'docs/product.json',
                       'signals_file': 'docs/signals.json', 'visibility': 'private', 'max_age_hours': 36}
        self.body = intent()
        self.signals = {'schema_version': 1, 'signals': []}
        self.save()
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                        'commit', '-qm', 'Synthetic review fixture'], check=True)

    def save(self):
        loop.atomic_json(self.root / 'docs/review-config.json', self.config)
        loop.atomic_json(self.root / 'docs/product.json', {'schema_version': 1, 'product': self.body})
        loop.atomic_json(self.root / 'docs/signals.json', self.signals)

    def run_review(self, run_id='test-1'):
        return runner.run(self.root, 'docs/review-config.json', self.output, run_id)

    def signal(self):
        return {'id': 'SIG-001', 'objective': 'OBJ-001', 'kind': 'telemetry',
                'source': 'Synthetic fixture', 'observer': 'Test', 'observed_at': loop.stamp(loop.now()-timedelta(hours=1)),
                'privacy': 'internal', 'reviewed': True, 'result': 'negative', 'summary': 'Synthetic only',
                'method': 'One fabricated sample; no real users', 'window': 'Synthetic hour', 'max_age_hours': 24}

    def test_exchange_reports_unknown_delivery_without_mutations(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch.object(loop, 'run_check', side_effect=AssertionError('Must not run app')):
            receipt = self.run_review()
        self.assertEqual(receipt['status'], 'complete')
        self.assertEqual(receipt['roadmap']['initiatives'][0]['delivery']['candidate'], 'unknown')
        self.assertEqual(receipt['roadmap']['sync']['status'], 'not-checked')
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(runner.read_receipt(self.output/'test-1.json'), receipt)

    def test_native_reads_actual_missing_evidence_and_does_not_run_it(self):
        args = argparse.Namespace(actor='Test', reason='Synthetic setup', authority_ref='Fixture')
        product.store_intent(loop, self.root, self.body, None, args)
        self.config.update(mode='native', product_file='.spec-loop/product/state.json')
        self.save()
        with patch.object(loop, 'run_check', side_effect=AssertionError('Must not execute')):
            receipt = self.run_review()
        self.assertEqual(receipt['status'], 'complete')
        self.assertFalse(receipt['roadmap']['changes']['CHG-001']['verify']['passed'])
        self.assertEqual(receipt['roadmap']['initiatives'][0]['delivery']['candidate'], 'unverified')
        self.assertIn('Product scope needs contract review', (self.output/'test-1.md').read_text())

    def test_reader_detects_expiry_and_changed_source(self):
        receipt = self.run_review()
        identity = runner.inputs(self.root, 'docs/review-config.json')[1]
        self.assertEqual(runner.freshness(receipt, identity, loop.now()), 'current-at-read')
        self.assertEqual(runner.freshness(receipt, identity, loop.now()+timedelta(hours=37)), 'stale')
        (self.root/'app.py').write_text('# Changed after review\n')
        self.assertEqual(runner.freshness(receipt, runner.inputs(self.root, 'docs/review-config.json')[1], loop.now()), 'inputs-changed')

    def test_replay_preserves_age_and_repairs_missing_markdown(self):
        receipt = self.run_review()
        (self.output/'test-1.md').unlink()
        with patch.object(loop, 'now', return_value=loop.now()+timedelta(hours=40)):
            replay = self.run_review()
        self.assertEqual(replay, receipt)
        self.assertTrue((self.output/'test-1.md').is_file())

    def test_reusing_run_id_after_change_preserves_original_receipt(self):
        receipt = self.run_review()
        self.body['initiatives'][0]['horizon'] = 'later'; self.save()
        with self.assertRaisesRegex(loop.LoopError, 'conflict'):
            self.run_review()
        self.assertEqual(runner.read_receipt(self.output/'test-1.json'), receipt)

    def test_failures_publish_failed_attempt_without_overwriting_prior_success(self):
        good = self.run_review()
        self.config['schema_version'] = 2; self.save()
        failed = self.run_review('test-2')
        self.assertEqual(failed['status'], 'failed')
        self.assertEqual(failed['roadmap'], {})
        self.assertEqual(runner.read_receipt(self.output/'test-1.json'), good)
        self.assertEqual(runner.freshness(failed, '', loop.now()), 'failed')

    def test_input_race_never_publishes_success(self):
        original = runner.inputs
        count = 0
        def changed(*args):
            nonlocal count
            count += 1
            if count == 2:
                (self.root/'app.py').write_text('# Race\n')
            return original(*args)
        with patch.object(runner, 'inputs', side_effect=changed):
            self.assertEqual(self.run_review()['status'], 'failed')

    def test_negative_and_stale_signals_request_review_without_reprioritizing(self):
        self.signals['signals'] = [self.signal()]
        old = copy.deepcopy(self.body)
        self.save()
        first = self.run_review()
        self.assertEqual(first['signals'][0]['state_at_check'], 'negative')
        with patch.object(loop, 'now', return_value=loop.now()+timedelta(hours=25)):
            later = self.run_review('test-2')
        self.assertEqual(later['signals'][0]['state_at_check'], 'stale')
        self.assertEqual(loop.read_json(self.root/'docs/product.json')['product'], old)

    def test_invalid_signals_fail_closed(self):
        for index, field in enumerate(('objective', 'observed_at', 'reviewed', 'duplicate', 'future')):
            item = self.signal()
            self.signals['signals'] = [item]
            if field == 'objective': item[field] = 'OBJ-missing'
            if field == 'observed_at': item[field] = 'yesterday'
            if field == 'reviewed': item[field] = False
            if field == 'duplicate': self.signals['signals'].append(copy.deepcopy(item))
            if field == 'future': item['observed_at'] = loop.stamp(loop.now()+timedelta(days=1))
            self.save()
            with self.subTest(field=field):
                self.assertEqual(self.run_review('bad-'+str(index))['status'], 'failed')

    def test_public_review_rejects_private_product_or_signal_data(self):
        self.config['visibility'] = 'public'; self.save()
        self.assertEqual(self.run_review()['status'], 'failed')
        self.body['opportunities'][0]['privacy'] = 'public'
        self.signals['signals'] = [self.signal()]; self.save()
        self.assertEqual(self.run_review('test-2')['status'], 'failed')
        self.signals['signals'][0]['privacy'] = 'public'; self.save()
        self.assertEqual(self.run_review('test-3')['status'], 'complete')

    def test_budget_failure_and_deadline_are_explicit_failures(self):
        with patch.object(runner, 'TOTAL_LIMIT', 10):
            self.assertEqual(self.run_review()['status'], 'failed')
        with patch.object(runner, 'review', side_effect=loop.LoopError('deadline')):
            self.assertEqual(self.run_review('test-2')['status'], 'failed')

    def test_ignored_declared_artifact_is_in_byte_budget(self):
        artifact = self.root/'ignored-artifact.txt'
        artifact.write_text('x' * 50000)
        (self.root/'.gitignore').write_text('ignored-artifact.txt\n')
        change_path = self.root/'.spec-loop/changes/CHG-001.json'
        change = loop.read_json(change_path)
        change['artifacts'][0]['path'] = 'ignored-artifact.txt'
        loop.atomic_json(change_path, change)
        with patch.object(runner, 'FILE_LIMIT', 40000):
            self.assertEqual(self.run_review()['status'], 'failed')

    def test_report_budget_counts_the_actual_published_bytes(self):
        receipt = self.run_review()
        compact = len(loop.canonical(receipt))
        pretty = (self.output/'test-1.json').stat().st_size
        self.assertGreater(pretty, compact)
        with patch.object(runner, 'REPORT_LIMIT', (compact + pretty)//2):
            rejected = self.run_review('test-2')
        self.assertEqual(rejected['status'], 'failed')
        self.assertEqual(rejected['roadmap'], {})

    def test_lock_and_in_project_output_prevent_publication(self):
        with self.assertRaises(loop.LoopError):
            runner.run(self.root, 'docs/review-config.json', self.root/'reports', 'test')
        with runner.output_lock(self.root, self.output), self.assertRaises(loop.LoopError):
            self.run_review()
        with loop.writer(self.root):
            self.assertEqual(self.run_review()['status'], 'failed')

    def test_symlink_input_and_output_are_refused(self):
        (self.root/'docs/product.json').unlink()
        (self.root/'docs/product.json').symlink_to(PLUGIN/'docs/product-roadmap.json')
        self.assertEqual(self.run_review()['status'], 'failed')
        elsewhere = Path(self.temp.name)/'elsewhere'; elsewhere.mkdir()
        (self.output/'test-2.json').symlink_to(elsewhere/'target')
        with self.assertRaises(loop.LoopError): self.run_review('test-2')
        self.assertFalse((elsewhere/'target').exists())

    def test_receipt_corruption_future_and_excessive_expiry_are_not_current(self):
        receipt = self.run_review()
        receipt['status'] = 'failed'
        loop.atomic_json(self.output/'test-1.json', receipt)
        with self.assertRaisesRegex(loop.LoopError, 'digest'): runner.read_receipt(self.output/'test-1.json')
        receipt['status'] = 'complete'
        self.assertEqual(runner.freshness(receipt, receipt['input_digest'], loop.now()-timedelta(days=1)), 'invalid-time')
        receipt['expires_at'] = loop.stamp(loop.now()+timedelta(days=8))
        self.assertEqual(runner.freshness(receipt, receipt['input_digest'], loop.now()), 'invalid-time')

    def test_cli_run_status_and_missing_receipt(self):
        cmd = ['python3', str(PLUGIN/'scripts/review_runner.py'), '--root', str(self.root)]
        run = subprocess.run(cmd+['run', '--output', str(self.output), '--run-id', 'cli-1'], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout+run.stderr)
        status = subprocess.run(cmd+['status', '--receipt', str(self.output/'cli-1.json')], capture_output=True, text=True)
        self.assertEqual(json.loads(status.stdout)['freshness'], 'current-at-read')
        missing = subprocess.run(cmd+['status', '--receipt', str(self.output/'missing.json')], capture_output=True, text=True)
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(json.loads(missing.stdout)['freshness'], 'unavailable')

    def test_markup_in_product_text_is_escaped(self):
        self.body['initiatives'][0]['title'] = '<script>alert(1)</script>|\nNext'
        self.save(); self.run_review()
        rendered = (self.output/'test-1.md').read_text()
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)

    def test_past_dates_and_wip_limit_generate_findings(self):
        self.body['capacity']['wip_limit'] = 1
        second = copy.deepcopy(self.body['initiatives'][0]); second['id'] = 'INI-002'
        self.body['initiatives'].append(second)
        self.body['initiatives'][0]['date'] = {'kind': 'forecast', 'value': '2020-01-01'}
        self.save()
        kinds = {f['kind'] for f in self.run_review()['findings']}
        self.assertTrue({'capacity', 'date-review'} <= kinds)


if __name__ == '__main__':
    unittest.main()
