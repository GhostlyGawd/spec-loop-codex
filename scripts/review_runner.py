#!/usr/bin/env python3
"""Read-only product review worker and receipt reader. Linux CLI, Python 3.10+."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta
import html
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys

import spec_loop as core
import product

FILE_LIMIT = 8 * 1024 * 1024
TOTAL_LIMIT = 64 * 1024 * 1024
COUNT_LIMIT = 10000
REPORT_LIMIT = 8 * 1024 * 1024


def bounded(path):
    if path.stat().st_size > FILE_LIMIT:
        raise core.LoopError('Input exceeds 8 MiB')
    return core.read_json(path)


def validate(value, name):
    errors = core.schema_errors(value, core.read_json(core.PLUGIN / 'schemas' / name))
    if errors:
        # Do not echo arbitrary input values into public job logs.
        raise core.LoopError('Invalid ' + name)


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            raise ValueError()
        return parsed
    except (TypeError, ValueError) as exc:
        raise core.LoopError('Timestamp must include a timezone') from exc


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, timeout=10)
    if result.returncode:
        raise core.LoopError('Git review input is unavailable')
    return result.stdout


def preflight(root):
    if core.inside(root, '.spec-loop/.lock').exists():
        raise core.LoopError('Product writer is active; retry later')
    paths = set(os.fsdecode(x) for x in git(root, 'ls-files', '-z', '--cached', '--others', '--exclude-standard').split(b'\0') if x)
    # Include ignored native records because they can change gates and observations.
    folder = core.inside(root, '.spec-loop')
    if folder.exists():
        for p in folder.rglob('*'):
            core.inside(root, p.relative_to(root).as_posix())
            if p.is_file():
                paths.add(p.relative_to(root).as_posix())
            if len(paths) > COUNT_LIMIT:
                raise core.LoopError('Review exceeds file count budget')
    if core.inside(root, '.spec-loop/project.json').exists():
        _, changes = core.load_project(root)
        for change in changes.values():
            paths.update(item['path'] for item in change['artifacts'])
    if len(paths) > COUNT_LIMIT:
        raise core.LoopError('Review exceeds file count budget')
    total = 0
    for rel in paths:
        p = core.inside(root, rel)
        if p.is_file():
            size = p.stat().st_size
            total += size
            if size > FILE_LIMIT or total > TOTAL_LIMIT:
                raise core.LoopError('Review exceeds input byte budget')


def inputs(root, config_path):
    preflight(root)
    config = bounded(core.inside(root, config_path))
    validate(config, 'review-config.schema.json')
    if config['mode'] == 'native':
        if config['product_file'] != '.spec-loop/product/state.json':
            raise core.LoopError('Native product_file must be .spec-loop/product/state.json')
        body = product.read(core, root)['body']
        identity = product.input_hash(core, root)
    else:
        envelope = bounded(core.inside(root, config['product_file']))
        if not isinstance(envelope, dict) or set(envelope) != {'schema_version', 'product'} or type(envelope['schema_version']) is not int or envelope['schema_version'] != 1:
            raise core.LoopError('Invalid product exchange envelope')
        body = envelope['product']
        product.validate_body(core, body)
        identity = product.hashed(core, body)
    source = core.snapshot(root)
    signals = {'schema_version': 1, 'signals': []}
    if config['signals_file']:
        signals = bounded(core.inside(root, config['signals_file']))
    validate(signals, 'review-signals.schema.json')
    if len(signals['signals']) > 1000:
        raise core.LoopError('Review exceeds signal count budget')
    if len({s['id'] for s in signals['signals']}) != len(signals['signals']):
        raise core.LoopError('Duplicate signal ID')
    objectives = {o['id'] for o in body['objectives']}
    for item in signals['signals']:
        if item['objective'] not in objectives:
            raise core.LoopError('Signal refers to an unknown objective')
        timestamp(item['observed_at'])
        if not item['reviewed']:
            raise core.LoopError('Signal needs disclosure review')
    if config['visibility'] == 'public' and (
        any(o['privacy'] != 'public' for o in body['opportunities']) or
        any(s['privacy'] != 'public' for s in signals['signals'])
    ):
        raise core.LoopError('Public report contains non-public records')
    commit = git(root, 'rev-parse', 'HEAD').decode().strip()
    value = {'config': config, 'product': body, 'signals': signals,
             'commit': commit, 'source_hash': source, 'native_identity': identity,
             'engine': core.VERSION}
    return value, product.hashed(core, value)


def review(value, root, clock):
    config, body = value['config'], value['product']
    if config['mode'] == 'native':
        view = product.derive(core, root)
    else:
        rows = [{**item, 'delivery': {'candidate': 'unknown', 'deployment': 'unknown'},
                 'next_decision': 'Link native change contracts and current evidence'} for item in body['initiatives']]
        view = {**body, 'initiatives': rows, 'changes': {}, 'releases': [],
                'warnings': ['Exchange planning data has no native delivery evidence'],
                'sync': {'status': 'not-checked', 'mode': 'committed-exchange-review'}}
    findings = [{'kind': 'roadmap', 'reason': w} for w in view['warnings']]
    active = [x for x in body['initiatives'] if x['status'] == 'active' and x['horizon'] == 'now']
    if len(active) > body['capacity']['wip_limit']:
        findings.append({'kind': 'capacity', 'reason': 'Active Now initiatives exceed the WIP limit'})
    for item in body['initiatives']:
        if item['status'] == 'active' and item['date']['kind'] != 'none' and item['date']['value'] < clock.date().isoformat():
            findings.append({'kind': 'date-review', 'initiative': item['id'], 'reason': 'Planned date is past; review the commitment or forecast'})
    signal_rows = []
    for item in value['signals']['signals']:
        age = (clock - timestamp(item['observed_at'])).total_seconds()
        if age < 0:
            raise core.LoopError('Signal observation is in the future')
        stale = age > item['max_age_hours'] * 3600
        state = 'stale' if stale else item['result']
        signal_rows.append({**item, 'state_at_check': state})
        if state in ('stale', 'negative', 'unknown'):
            findings.append({'kind': 'signal-review', 'signal': item['id'], 'objective': item['objective'], 'reason': state})
    if not signal_rows:
        findings.append({'kind': 'measurement-gap', 'reason': 'No reviewed feedback or telemetry was supplied'})
    return view, signal_rows, findings


def seal(value):
    return {**value, 'digest': product.hashed(core, value)}


def read_receipt(path):
    value = bounded(path)
    validate(value, 'review-report.schema.json')
    payload = {k: v for k, v in value.items() if k != 'digest'}
    if product.hashed(core, payload) != value['digest']:
        raise core.LoopError('Review receipt digest mismatch')
    timestamp(value['checked_at'])
    timestamp(value['expires_at'])
    if value['status'] == 'complete' and (not value['commit'] or not value['input_digest'] or value['mode'] == 'unknown' or not isinstance(value['roadmap'].get('initiatives'), list)):
        raise core.LoopError('Complete review receipt is missing input or roadmap data')
    return value


def freshness(receipt, identity, clock):
    checked, expires = timestamp(receipt['checked_at']), timestamp(receipt['expires_at'])
    if checked > clock or expires <= checked or expires > checked + timedelta(hours=168):
        return 'invalid-time'
    if receipt['status'] != 'complete':
        return 'failed'
    if receipt['input_digest'] != identity:
        return 'inputs-changed'
    if clock >= expires:
        return 'stale'
    return 'current-at-read'


def safe_cell(value):
    return html.escape(str(value)).replace('|', '&#124;').replace('\n', ' ').replace('\r', ' ').replace('`', '&#96;')


def markdown(receipt):
    lines = ['# Spec Loop product review', '',
        f"Run: {safe_cell(receipt['run_id'])}. Status: {receipt['status']}.",
        f"Checked: {receipt['checked_at']}. Expires: {receipt['expires_at']}.",
        f"Commit: {receipt['commit'] or 'unavailable'}.", '',
        'This is a snapshot. Recheck receipt age and current inputs before use.', '',
        '| Initiative | Horizon | Delivery evidence | Next decision |', '| --- | --- | --- | --- |']
    for item in receipt['roadmap'].get('initiatives', []):
        lines.append('| ' + ' | '.join(safe_cell(x) for x in [item['title'], item['horizon'], item['delivery']['candidate'], item['next_decision']]) + ' |')
    lines.extend(['', f"Review findings: {len(receipt['findings'])}. Supplied signals: {len(receipt['signals'])}.", ''])
    for finding in receipt['findings']:
        lines.append('- ' + safe_cell(finding))
    for change_id, checks in receipt['roadmap'].get('changes', {}).items():
        blockers = list(checks.get('errors', []))
        for stage in ('ready', 'verify', 'release'):
            gate = checks.get(stage, {})
            blockers.extend(gate.get('errors', []))
            blockers.extend(f'{stage}: {key} = {state}' for key, state in gate.get('checks', {}).items() if state != 'pass')
        unique = list(dict.fromkeys(blockers))
        for reason in unique[:5]:
            lines.append('- ' + safe_cell(change_id + ': ' + reason))
        if len(unique) > 5:
            lines.append('- ' + safe_cell(change_id) + ': additional blockers are in the JSON receipt.')
    if receipt['error']:
        lines.extend(['', receipt['error']])
    lines.extend(['', 'No product decision, external sync confirmation, deployment or causal claim is made.', ''])
    return '\n'.join(lines)


@contextmanager
def output_lock(root, output):
    # Reports outside the project cannot contaminate the evidence source hash.
    output = output.absolute()
    if output.resolve().is_relative_to(root.resolve()):
        raise core.LoopError('Report directory must be outside the project')
    if any(p.is_symlink() for p in [output, *output.parents]):
        raise core.LoopError('Report directory cannot use symlinks')
    output.mkdir(parents=True, exist_ok=True)
    lock = output / '.review-lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise core.LoopError('Review output is locked; inspect the owner before recovery') from exc
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(str(os.getpid()))
        yield
    finally:
        lock.unlink(missing_ok=True)


def run(root, config_path, output, run_id):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', run_id):
        raise core.LoopError('Use a run ID of 1-100 letters, digits, underscores or hyphens')
    with output_lock(root, output):
        target = output / (run_id + '.json')
        if target.is_symlink() or (output / (run_id + '.md')).is_symlink():
            raise core.LoopError('Report files cannot be symlinks')
        if target.exists():
            prior = read_receipt(target)
            _, identity = inputs(root, config_path)
            if prior['run_id'] != run_id or prior['input_digest'] != identity:
                raise core.LoopError('Run ID conflict; use a new attempt ID')
            # Recreate a missing Markdown view after interrupted publication, without renewing time.
            (output / (run_id + '.md')).write_text(markdown(prior), encoding='utf-8')
            return prior
        clock = core.now()
        record = {'schema_version': 1, 'engine_version': core.VERSION, 'run_id': run_id,
            'status': 'failed', 'checked_at': core.stamp(clock), 'expires_at': core.stamp(clock + timedelta(hours=36)),
            'commit': '', 'input_digest': '', 'source_hash': '', 'mode': 'unknown',
            'roadmap': {}, 'signals': [], 'findings': [], 'error': '',
            'trust': 'Unsigned local snapshot; signal results are reported observations, not causal proof.'}
        try:
            value, identity = inputs(root, config_path)
            record.update(input_digest=identity, commit=value['commit'], source_hash=value['source_hash'],
                mode=value['config']['mode'], expires_at=core.stamp(clock + timedelta(hours=value['config']['max_age_hours'])))
            view, signals, findings = review(value, root, clock)
            if inputs(root, config_path)[1] != identity:
                raise core.LoopError('Inputs changed during review')
            record.update(status='complete', roadmap=view, signals=signals, findings=findings)
            if len((json.dumps(seal(record), ensure_ascii=False, indent=2) + '\n').encode()) > REPORT_LIMIT:
                raise core.LoopError('Report exceeds byte budget')
        except (core.LoopError, OSError, ValueError, RecursionError, subprocess.SubprocessError):
            record.update(status='failed', roadmap={}, signals=[], findings=[],
                error='Review failed. Check input schemas, disclosure, timestamps, budgets and repository state; retry with a new run ID.')
        receipt = seal(record)
        core.atomic_json(target, receipt)
        (output / (run_id + '.md')).write_text(markdown(receipt), encoding='utf-8')
        return receipt


def deadline(signum, frame):
    raise core.LoopError('Review exceeded the 60-second deadline')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--config', default='docs/review-config.json')
    sub = parser.add_subparsers(dest='command', required=True)
    start = sub.add_parser('run')
    start.add_argument('--output', type=Path, required=True)
    start.add_argument('--run-id', required=True)
    status = sub.add_parser('status')
    status.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    if not hasattr(signal, 'SIGALRM'):
        parser.exit(2, 'The review CLI requires Linux/POSIX deadline support.\n')
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(60)
    try:
        root = args.root.resolve()
        if args.command == 'run':
            result = run(root, args.config, args.output, args.run_id)
            print(json.dumps({'status': result['status'], 'run_id': result['run_id'], 'digest': result['digest']}))
            return 0 if result['status'] == 'complete' else 2
        receipt = read_receipt(args.receipt)
        _, identity = inputs(root, args.config)
        state = freshness(receipt, identity, core.now())
        print(json.dumps({'freshness': state, 'run_id': receipt['run_id'], 'checked_at': receipt['checked_at']}))
        return 0 if state == 'current-at-read' else 2
    except (core.LoopError, OSError, ValueError, RecursionError, subprocess.SubprocessError):
        print(json.dumps({'freshness': 'unavailable', 'error': 'Cannot complete review operation; inspect inputs, receipt and output lock.'}))
        return 2
    finally:
        signal.alarm(0)


if __name__ == '__main__':
    sys.exit(main())
