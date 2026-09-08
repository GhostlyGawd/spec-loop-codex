import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import review_health as health

NOW = datetime(2026, 9, 8, 16, tzinfo=timezone.utc)
POLICY = {'schema_version': 1, 'repository': 'owner/product', 'branch': 'main',
          'workflow': '.github/workflows/product-review.yml', 'cron': '17 7 * * *',
          'grace_hours': 6, 'max_observation_age_minutes': 15}


def fixture():
    run = {'id': 1, 'event': 'schedule', 'head_sha': 'a' * 40, 'run_attempt': 1,
           'head_branch': 'main', 'path': POLICY['workflow'], 'repository': {'full_name': 'owner/product'},
           'html_url': 'https://github.com/owner/product/actions/runs/1',
           'status': 'completed', 'conclusion': 'success', 'created_at': '2026-09-08T12:10:40Z'}
    job = {'id': 10, 'run_id': 1, 'run_attempt': 1, 'head_sha': 'a' * 40, 'name': 'review',
           'status': 'completed', 'conclusion': 'success',
           'steps': [{'name': health.RECEIPT_STEP, 'status': 'completed', 'conclusion': 'success'}]}
    artifact = {'id': 20, 'name': 'product-review-1-1', 'expired': False, 'size_in_bytes': 20,
                'expires_at': '2026-09-22T12:11:00Z', 'created_at': '2026-09-08T12:11:00Z',
                'workflow_run': {'id': 1, 'head_sha': 'a' * 40}, 'digest': 'sha256:example'}
    return {'schema_version': 1, 'observed_at': NOW.isoformat(),
            'target': {k: POLICY[k] for k in ('repository', 'branch', 'workflow', 'cron')} |
                      {'commit': 'a' * 40, 'tree': 'b' * 40, 'version': '0.8.0'},
            'runs': {'total_count': 1, 'scope': {'repository': 'owner/product', 'branch': 'main'},
                     'workflow_runs': [run]},
            'details': {'1': {'jobs': {'total_count': 1, 'jobs': [job]},
                              'artifacts': {'total_count': 1, 'artifacts': [artifact]}}}}


class HealthTests(unittest.TestCase):
    def test_delayed_schedule_and_current_commit_separate(self):
        s = fixture()
        s['target']['commit'] = 'c' * 40
        report = health.evaluate(s, POLICY, NOW)
        self.assertEqual(report['schedule']['status'], 'passed')
        self.assertEqual(report['schedule']['created_delay_seconds'], 17620)
        self.assertEqual(report['current_commit_review']['status'], 'missing')
        self.assertTrue(report['attention'])

    def test_push_and_manual_do_not_prove_schedule(self):
        for event in ('push', 'workflow_dispatch', 'pull_request'):
            s = fixture()
            s['runs']['workflow_runs'][0]['event'] = event
            self.assertEqual(health.evaluate(s, POLICY, NOW)['schedule']['status'], 'missed')

    def test_missing_waits_only_until_deadline(self):
        s = fixture()
        s['runs'].update(total_count=0, workflow_runs=[])
        for hour, expected in ((8, 'waiting'), (14, 'missed')):
            now = NOW.replace(hour=hour)
            s['observed_at'] = now.isoformat()
            self.assertEqual(health.evaluate(s, POLICY, now)['schedule']['status'], expected)

    def test_failed_latest_is_not_hidden_by_older_success(self):
        s = fixture()
        r = copy.deepcopy(s['runs']['workflow_runs'][0])
        r.update(id=2, html_url='https://github.com/owner/product/actions/runs/2',
                 created_at='2026-09-08T15:00:00Z', conclusion='failure')
        s['runs']['workflow_runs'].append(r)
        s['runs']['total_count'] = 2
        self.assertEqual(health.evaluate(s, POLICY, NOW)['schedule']['status'], 'failed')

    def test_missing_or_bad_receipt_artifact_attempt_never_pass(self):
        for kind in ('receipt', 'expired', 'artifact-count', 'job-count', 'attempt', 'sha', 'artifact-sha'):
            s = fixture()
            d = s['details']['1']
            if kind == 'receipt':
                d['jobs']['jobs'][0]['steps'][0]['conclusion'] = 'skipped'
            elif kind == 'expired':
                d['artifacts']['artifacts'][0]['expired'] = True
            elif kind == 'artifact-count':
                d['artifacts']['total_count'] = 2
            elif kind == 'job-count':
                d['jobs']['total_count'] = 2
            elif kind == 'attempt':
                d['jobs']['jobs'][0]['run_attempt'] = 2
            elif kind == 'sha':
                d['jobs']['jobs'][0]['head_sha'] = 'c' * 40
            else:
                d['artifacts']['artifacts'][0]['workflow_run']['head_sha'] = 'c' * 40
            with self.subTest(kind=kind):
                self.assertEqual(health.evaluate(s, POLICY, NOW)['schedule']['status'], 'unverified')

    def test_stale_future_partial_and_wrong_target_rejected(self):
        for kind in ('stale', 'future', 'partial', 'cron', 'repo', 'scope'):
            s = fixture()
            if kind in ('stale', 'future'):
                s['observed_at'] = (NOW + timedelta(minutes=-16 if kind == 'stale' else 1)).isoformat()
            elif kind == 'partial':
                s['runs']['total_count'] = 2
            elif kind == 'cron':
                s['target']['cron'] = '18 7 * * *'
            elif kind == 'repo':
                s['runs']['workflow_runs'][0]['repository']['full_name'] = 'other/repo'
            else:
                s['runs']['scope']['branch'] = 'feature'
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                health.evaluate(s, POLICY, NOW)

    def test_other_workflow_branch_and_previous_day_do_not_count(self):
        for field, value in (('path', 'other.yml'), ('head_branch', 'feature'),
                             ('created_at', '2026-09-07T12:10:40Z')):
            s = fixture()
            s['runs']['workflow_runs'][0][field] = value
            self.assertEqual(health.evaluate(s, POLICY, NOW)['schedule']['status'], 'missed')

    def test_incomplete_run_overdue_and_late_success(self):
        s = fixture()
        s['runs']['workflow_runs'][0]['status'] = 'in_progress'
        r = health.evaluate(s, POLICY, NOW)
        self.assertTrue(r['schedule']['overdue'])
        self.assertNotEqual(r['schedule']['status'], 'passed')
        s = fixture()
        s['runs']['workflow_runs'][0]['created_at'] = '2026-09-08T14:00:00Z'
        s['details']['1']['artifacts']['artifacts'][0]['created_at'] = '2026-09-08T14:01:00Z'
        r = health.evaluate(s, POLICY, NOW)
        self.assertEqual(r['schedule']['status'], 'passed')
        self.assertEqual(r['schedule']['timing'], 'after-grace')
        self.assertTrue(r['attention'])

    def test_installed_version_source_and_corruption(self):
        meta = {'version': '0.7.0', 'source_tree': 'b' * 40, 'payload_digest': 'digest'}
        actual = {'engine_version': '0.7.0', 'payload_digest': 'digest'}
        with patch.object(health, 'read_json', return_value=meta), patch.object(health.install_check, 'inspect', return_value=actual):
            target = fixture()['target']
            self.assertEqual(health.installed_status(Path('/unused'), target)['status'], 'update-available')
            target['version'] = '0.7.0'
            self.assertEqual(health.installed_status(Path('/unused'), target)['status'], 'current')
            target['tree'] = 'c' * 40
            self.assertEqual(health.installed_status(Path('/unused'), target)['status'], 'source-differs')
            actual['payload_digest'] = 'different'
            with self.assertRaises(ValueError):
                health.installed_status(Path('/unused'), target)

    def test_cli_is_read_only_and_stale_input_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            snapshot = fixture()
            snapshot['observed_at'] = '2000-01-01T00:00:00Z'
            (root / 'snapshot.json').write_text(json.dumps(snapshot))
            (root / 'policy.json').write_text(json.dumps(POLICY))
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            result = subprocess.run([sys.executable, health.__file__, '--snapshot', str(root / 'snapshot.json'),
                                     '--policy', str(root / 'policy.json')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)['status'], 'unverified')
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})


if __name__ == '__main__':
    unittest.main()
