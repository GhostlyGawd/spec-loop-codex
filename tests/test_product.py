"""Product workflow invariants on disposable local projects; no live observations."""
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
import product
import release_ledger as ledger


def intent():
    body = product.default_body()
    body['strategy'].update(audience='Local example user', problem='Collect URLs once',
        positioning='Synthetic teaching fixture', business_model='No commercial claim')
    body['objectives'] = [{'id': 'OBJ-001', 'title': 'Save a URL once', 'metric': 'Task completion',
        'baseline': 'Unknown', 'target': 'One person completes the task', 'cohort': 'No participants yet',
        'window': 'After release', 'guardrails': ['No network calls'], 'owner': 'Builder'}]
    body['opportunities'] = [{'id': 'OPP-001', 'title': 'Collect a link', 'source': 'Synthetic assumption',
        'observed_at': 'No observation', 'evidence': 'assumption', 'privacy': 'internal', 'status': 'new',
        'experiment': 'Observe a person use the released artifact', 'stop_rule': 'Reconsider if unusable', 'objectives': ['OBJ-001']}]
    body['initiatives'] = [{'id': 'INI-001', 'title': 'Local URL collection', 'scope': 'Add valid URLs without duplicates',
        'non_goals': ['Persistence'], 'objectives': ['OBJ-001'], 'opportunities': ['OPP-001'],
        'horizon': 'now', 'status': 'active', 'owner': 'Builder', 'priority_reason': 'Small first useful result',
        'confidence': 'low', 'risk': 'low', 'depends_on': [], 'changes': ['CHG-001'], 'partial_release': 'all_required',
        'date': {'kind': 'none', 'value': ''}, 'review_trigger': 'After the first real task observation'}]
    body['capacity'] = {'wip_limit': 1, 'available_days': 2,
        'estimates': [{'change': 'CHG-001', 'low_days': 1, 'high_days': 2}]}
    return body


class ProductTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        shutil.copytree(PLUGIN / 'examples/reading-list', self.root)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.args = {'actor': 'test', 'authority_ref': 'synthetic local test', 'reason': 'Test decision'}
        product.execute(loop, self.root, argparse.Namespace(command='product', action='init', **self.args))
        self.apply(intent())

    def state(self):
        return product.read(loop, self.root)

    def apply(self, body, expected=None):
        filename = '.spec-loop/artifacts/product-draft.json'
        loop.atomic_json(self.root / filename, body)
        return product.apply(loop, self.root, argparse.Namespace(file=filename,
            expect_digest=expected or self.state()['digest'], **self.args))

    def align(self, change='CHG-001'):
        config, _, contract = loop.select(self.root, change)
        return product.align(loop, self.root, argparse.Namespace(change=change, expect_digest=self.state()['digest'],
            expect_contract=loop.contract_hash(self.root, config, contract), **self.args))

    def ready(self):
        self.align()
        loop.run_check(self.root, argparse.Namespace(change='CHG-001', check='CHK-001', observer='test'))
        note = '.spec-loop/artifacts/synthetic.md'
        (self.root / note).write_text('Synthetic fixture: no deployment, user study, or authenticated approval.\n')
        for check in ('CHK-002', 'CHK-003'):
            loop.record_manual(self.root, argparse.Namespace(change='CHG-001', check=check,
                observer='test', result='pass', note='Synthetic only', artifact=note))
        return note

    def seal(self):
        note = self.ready()
        ledger.seal(loop, self.root, argparse.Namespace(change='CHG-001', release='REL-001', target='synthetic-local',
            artifact='app.py', receipt=note, authority_ref='Fixture only', observer='test'))
        return note

    def view(self):
        return product.refresh(loop, self.root)

    def test_scope_review_then_end_to_end_history_and_missing_outcome(self):
        self.assertFalse(loop.gate(self.root, 'CHG-001', 'ready')['passed'])
        self.seal()
        view = self.view()
        row = view['initiatives'][0]
        self.assertEqual(row['delivery']['candidate'], 'release-ready')
        self.assertEqual(row['delivery']['historical_coverage'], 'complete')
        self.assertEqual(row['delivery']['deployment'], 'unverified')
        self.assertFalse(view['releases'][0]['outcomes']['passed'])
        self.assertEqual(self.state()['body']['objectives'][0]['baseline'], 'Unknown')

    def test_priority_change_preserves_test_evidence_scope_change_blocks_and_stales(self):
        self.ready()
        original = loop.gate(self.root, 'CHG-001', 'verify')
        self.assertTrue(original['passed'])
        body = copy.deepcopy(self.state()['body'])
        body['initiatives'][0].update(priority_reason='New order', horizon='next')
        self.apply(body)
        self.assertTrue(loop.gate(self.root, 'CHG-001', 'verify')['passed'])
        body['objectives'][0]['target'] = 'Three people complete the task'
        self.apply(body)
        self.assertFalse(loop.gate(self.root, 'CHG-001', 'ready')['passed'])
        self.align()
        self.assertEqual(loop.gate(self.root, 'CHG-001', 'verify')['checks']['CHK-001'], 'stale')

    def test_stale_product_writer_cannot_overwrite_new_decision(self):
        previous = self.state()['digest']
        body = copy.deepcopy(self.state()['body'])
        body['initiatives'][0]['horizon'] = 'next'
        self.apply(body)
        before = product.path(loop, self.root).read_bytes()
        with self.assertRaisesRegex(loop.LoopError, 'conflict'):
            self.apply(intent(), expected=previous)
        self.assertEqual(before, product.path(loop, self.root).read_bytes())

    def test_invalid_draft_leaves_intent_unchanged(self):
        before = product.path(loop, self.root).read_bytes()
        for mutate in ('unknown', 'duplicate', 'cycle', 'date', 'capacity', 'schema'):
            body = intent()
            if mutate == 'unknown': body['initiatives'][0]['changes'] = ['CHG-404']
            if mutate == 'duplicate': body['objectives'].append(copy.deepcopy(body['objectives'][0]))
            if mutate == 'cycle': body['initiatives'][0]['depends_on'] = ['INI-001']
            if mutate == 'date': body['initiatives'][0]['date'] = {'kind': 'commitment', 'value': 'soon'}
            if mutate == 'capacity': body['capacity']['estimates'][0]['low_days'] = 8
            if mutate == 'schema': body['surprise'] = True
            with self.subTest(mutate=mutate), self.assertRaises(loop.LoopError): self.apply(body)
            self.assertEqual(before, product.path(loop, self.root).read_bytes())

    def test_outcome_failure_does_not_rewrite_priority(self):
        note = self.seal()
        state = product.path(loop, self.root).read_bytes()
        clock = loop.now()
        for result in ('pass', 'fail'):
            ledger.observe(loop, self.root, argparse.Namespace(release='REL-001', check='CHK-004',
                result=result, observer='test', note='Synthetic only', artifact=note,
                cohort='Synthetic fixture', window_start=loop.stamp(clock-timedelta(minutes=1)), window_end=loop.stamp(clock)))
        view = self.view()
        self.assertFalse(view['releases'][0]['outcomes']['passed'])
        self.assertIn('failed outcome', view['initiatives'][0]['next_decision'])
        self.assertEqual(state, product.path(loop, self.root).read_bytes())
        (self.root / 'app.py').write_text('# unfinished candidate\n')
        view = self.view()
        self.assertEqual(view['initiatives'][0]['delivery']['candidate'], 'unverified')
        self.assertEqual(view['initiatives'][0]['delivery']['historical_coverage'], 'complete')

    def test_capacity_counts_shared_change_once_and_dependencies_block(self):
        body = intent()
        second = copy.deepcopy(body['initiatives'][0])
        second.update(id='INI-002', horizon='now', depends_on=['INI-001'])
        body['initiatives'].append(second)
        self.apply(body)
        view = self.view()
        self.assertEqual(view['capacity']['estimated_days']['high'], 2)
        self.assertTrue(view['capacity']['wip_exceeded'])
        self.assertEqual(view['initiatives'][1]['delivery']['blocking_initiatives'], ['INI-001'])

    def test_partial_history_does_not_claim_full_delivery(self):
        change = loop.read_json(self.root / '.spec-loop/changes/CHG-001.json')
        change['id'] = 'CHG-002'
        loop.atomic_json(self.root / '.spec-loop/changes/CHG-002.json', change)
        body = intent()
        body['initiatives'][0]['changes'].append('CHG-002')
        self.apply(body)
        self.seal()
        row = self.view()['initiatives'][0]
        self.assertEqual(row['delivery']['historical_coverage'], 'partial')
        self.assertEqual(row['delivery']['historical_missing_changes'], ['CHG-002'])
        self.assertEqual(row['delivery']['candidate'], 'unverified')

    def test_same_inputs_stable_content_but_expiry_is_rechecked(self):
        self.ready()
        first, second = self.view(), self.view()
        self.assertEqual(first['content_digest'], second['content_digest'])
        clock = loop.now()
        with patch.object(loop, 'now', return_value=clock+timedelta(days=8)):
            later = self.view()
        self.assertEqual(first['input_digest'], later['input_digest'])
        self.assertNotEqual(first['content_digest'], later['content_digest'])
        self.assertEqual(later['changes']['CHG-001']['verify']['checks']['CHK-001'], 'expired')

    def test_refresh_race_keeps_prior_view(self):
        self.view()
        before = product.path(loop, self.root, 'roadmap.json').read_bytes()
        with patch.object(product, 'input_hash', side_effect=['before', 'after']):
            result = product.refresh_status(loop, self.root)
        self.assertEqual(result['freshness'], 'stale-or-unavailable')
        self.assertIn('conflict', result['error'])
        self.assertEqual(before, product.path(loop, self.root, 'roadmap.json').read_bytes())

    def test_backup_restore_adds_revision_and_keeps_decisions(self):
        old = self.state()
        backup = product.execute(loop, self.root, argparse.Namespace(command='product', action='backup'))
        body = intent(); body['initiatives'][0]['horizon'] = 'later'; self.apply(body)
        product.execute(loop, self.root, argparse.Namespace(command='product', action='restore', file=backup['backup'],
            expect_digest=self.state()['digest'], **self.args))
        restored = self.state()
        self.assertEqual(restored['body'], old['body'])
        self.assertEqual(restored['revision'], old['revision']+2)
        self.assertEqual(restored['decisions'][:len(old['decisions'])], old['decisions'])

    def test_unknown_version_and_tampering_fail_closed(self):
        for kind in ('version', 'body'):
            saved = self.state()
            bad = copy.deepcopy(saved)
            if kind == 'version': bad['schema_version'] = 99
            else: bad['body']['strategy']['problem'] = 'Changed outside decision command'
            loop.atomic_json(product.path(loop, self.root), bad)
            with self.assertRaises(loop.LoopError): product.read(loop, self.root)
            self.assertEqual(product.refresh_status(loop, self.root)['freshness'], 'stale-or-unavailable')
            loop.atomic_json(product.path(loop, self.root), saved)

    def test_inventory_is_read_only_and_marks_intent_unknown(self):
        before = {p.relative_to(self.root):p.read_bytes() for p in (self.root/'.spec-loop').rglob('*') if p.is_file()}
        self.assertEqual(product.inventory(loop, self.root)['intent'], 'unverified')
        after = {p.relative_to(self.root):p.read_bytes() for p in (self.root/'.spec-loop').rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_missing_link_is_unknown_not_success(self):
        self.ready()
        (self.root / '.spec-loop/changes/CHG-001.json').unlink()
        view = self.view()
        self.assertEqual(view['changes']['CHG-001']['state'], 'unknown')
        self.assertEqual(view['initiatives'][0]['delivery']['candidate'], 'unverified')

    def test_path_escape_and_active_writer_fail_without_intent_mutation(self):
        old = self.state()['digest']
        with self.assertRaises(loop.LoopError):
            product.apply(loop, self.root, argparse.Namespace(file='../outside.json', expect_digest=old, **self.args))
        with loop.writer(self.root), self.assertRaisesRegex(loop.LoopError, 'lock'):
            self.view()
        self.assertEqual(old, self.state()['digest'])

    def test_decisions_preserve_actual_previous_and_new_values(self):
        body = intent(); body['initiatives'][0]['horizon'] = 'next'; self.apply(body)
        edit = self.state()['decisions'][-1]['changes'][0]
        self.assertEqual(json.loads(edit['before_json'])[0]['horizon'], 'now')
        self.assertEqual(json.loads(edit['after_json'])[0]['horizon'], 'next')

    def test_changed_historical_value_rejected_with_recomputed_envelope_hash(self):
        state = self.state()
        state['decisions'][-1]['changes'][0]['before_json'] = '"different"'
        state.pop('digest'); state['digest'] = product.hashed(loop, state)
        loop.atomic_json(product.path(loop, self.root), state)
        with self.assertRaisesRegex(loop.LoopError, 'before-value'):
            self.state()
        self.assertFalse(loop.doctor(self.root)['passed'])

    def test_v02_release_remains_readable_after_upgrade(self):
        record = loop.read_json(PLUGIN / 'tests/fixtures/v02-release.json')
        self.assertEqual(record['engine_version'], '0.2.0')
        entries, _ = ledger.validate_release(loop, record, record['id'])
        self.assertIn('CHG-001', entries)

    def test_initiative_risk_cannot_weaken_change_floor(self):
        body = intent(); body['initiatives'][0]['risk'] = 'high'; self.apply(body)
        self.align()
        report = loop.gate(self.root, 'CHG-001', 'ready')
        self.assertFalse(report['passed'])
        self.assertTrue(any('risk' in x for x in report['errors']))

    def test_alignment_conflict_preserves_contract(self):
        config, _, change = loop.select(self.root, 'CHG-001')
        old_contract = loop.contract_hash(self.root, config, change)
        change['intent']['outcome'] = 'Revised acceptance intent'
        target = self.root / '.spec-loop/changes/CHG-001.json'
        loop.atomic_json(target, change)
        before = target.read_bytes()
        with self.assertRaisesRegex(loop.LoopError, 'conflict'):
            product.align(loop, self.root, argparse.Namespace(change='CHG-001', expect_digest=self.state()['digest'],
                expect_contract=old_contract, **self.args))
        self.assertEqual(before, target.read_bytes())

    def test_cli_refresh_after_evidence_and_context_resume(self):
        self.align()
        proc = subprocess.run(['python3', str(PLUGIN/'scripts/spec_loop.py'), '--root', str(self.root),
            'run', 'CHG-001', '--check', 'CHK-001', '--observer', 'test'], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout+proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['roadmap_refresh']['freshness'], 'current-at-check')
        self.assertTrue(loop.read_json(product.path(loop, self.root, 'roadmap.json'))['changes']['CHG-001']['verify']['passed'])
        bundle = loop.context(self.root, argparse.Namespace(change='CHG-001', max_chars=100000))
        self.assertEqual(bundle['product']['objectives'][0]['id'], 'OBJ-001')
        with self.assertRaisesRegex(loop.LoopError, 'budget'):
            loop.context(self.root, argparse.Namespace(change='CHG-001', max_chars=20))


if __name__ == '__main__':
    unittest.main()
