#!/usr/bin/env python3
"""Read a bounded GitHub observation; never fetch, dispatch, sync or repair."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re

import install_check

RECEIPT_STEP = 'Validate the published receipt against this checkout'
MAX_BYTES = 8 * 1024 * 1024


def stamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timestamps must include a timezone')
    return result.astimezone(timezone.utc)


def read_json(path):
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('Observation exceeds 8 MiB')
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inventory(value, key):
    items = value[key]
    require(isinstance(items, list) and len(items) <= 10000,
            'Invalid inventory')
    require(type(value['total_count']) is int and value['total_count'] == len(items),
            'Incomplete inventory: collect every page before reporting success')
    require(len({item['id'] for item in items}) == len(items), 'Duplicate inventory IDs')
    return items


def execution(run, snapshot, now):
    if run is None:
        return {'status': 'missing'}
    result = {key: run[key] for key in ('id', 'event', 'head_sha', 'html_url', 'run_attempt')}
    result['status'] = run['status']
    if run['status'] != 'completed':
        require(run['status'] in ('queued', 'in_progress', 'waiting', 'pending', 'requested'),
                'Unknown run status')
        return result
    if run['conclusion'] != 'success':
        return dict(result, status='failed', conclusion=run['conclusion'])
    detail = snapshot['details'].get(str(run['id']))
    require(detail is not None, 'Missing job or artifact observations')
    jobs = inventory(detail['jobs'], 'jobs')
    reviews = [job for job in jobs if job['name'] == 'review']
    require(len(reviews) == 1, 'Expected exactly one review job')
    job = reviews[0]
    require(job['run_id'] == run['id'] and job['run_attempt'] == run['run_attempt']
            and job['head_sha'] == run['head_sha'], 'Job identity or attempt mismatch')
    require(job['status'] == 'completed' and job['conclusion'] == 'success',
            'Successful review job not observed')
    steps = [step for step in job['steps'] if step['name'] == RECEIPT_STEP]
    require(len(steps) == 1 and steps[0]['status'] == 'completed'
            and steps[0]['conclusion'] == 'success', 'Receipt validation not successful')
    name = f"product-review-{run['id']}-{run['run_attempt']}"
    artifacts = [a for a in inventory(detail['artifacts'], 'artifacts') if a['name'] == name]
    require(len(artifacts) == 1, 'Expected review artifact metadata not found')
    artifact = artifacts[0]
    require(artifact['expired'] is False and stamp(artifact['expires_at']) > now
            and artifact['size_in_bytes'] > 0, 'Review artifact expired or empty')
    require(artifact['workflow_run']['id'] == run['id']
            and artifact['workflow_run']['head_sha'] == run['head_sha'], 'Artifact identity mismatch')
    require(stamp(run['created_at']) <= stamp(artifact['created_at']) <= now,
            'Artifact time is outside observation window')
    return dict(result, status='passed', review_job=job['id'], artifact_id=artifact['id'],
                artifact_digest=artifact.get('digest'), proof='job-steps-and-artifact-metadata')


def installed_status(bundle, target):
    if bundle is None:
        return {'status': 'not-checked'}
    meta = read_json(bundle / 'work-bundle.json')
    actual = install_check.inspect(bundle, work_bundle=True)
    require(actual['payload_digest'] == meta['payload_digest'], 'Installed payload differs from inventory')
    require(actual['engine_version'] == meta['version'], 'Installed version differs from inventory')
    current = tuple(map(int, install_check.version(target['version']).split('.')))
    installed = tuple(map(int, install_check.version(meta['version']).split('.')))
    status = 'update-available' if installed < current else 'installed-ahead' if installed > current else (
        'current' if meta['source_tree'] == target['tree'] else 'source-differs')
    return {'status': status, 'installed_version': meta['version'], 'repository_version': target['version'],
            'source_tree': meta['source_tree'], 'payload_digest': actual['payload_digest'],
            'provenance': 'unsigned-declared-source; payload checked locally'}


def evaluate(snapshot, policy, now=None, bundle=None):
    now = now or datetime.now(timezone.utc)
    require(snapshot['schema_version'] == 1 and policy['schema_version'] == 1, 'Unknown schema version')
    target = snapshot['target']
    for key in ('repository', 'branch', 'workflow', 'cron'):
        require(target[key] == policy[key], 'Target or schedule changed: ' + key)
    require(re.fullmatch(r'[0-9a-f]{40}', target['commit']) is not None
            and re.fullmatch(r'[0-9a-f]{40}', target['tree']) is not None, 'Invalid source identity')
    age = (now - stamp(snapshot['observed_at'])).total_seconds()
    require(0 <= age <= policy['max_observation_age_minutes'] * 60, 'Stale or future observation')
    require(0 < policy['max_observation_age_minutes'] <= 60, 'Invalid observation age policy')
    require(0 <= policy['grace_hours'] <= 12, 'Invalid schedule grace')
    match = re.fullmatch(r'(\d{1,2}) (\d{1,2}) \* \* \*', policy['cron'])
    require(match is not None, 'Only one daily UTC schedule is supported')
    minute, hour = map(int, match.groups())
    slot = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if slot > now:
        slot -= timedelta(days=1)
    deadline = slot + timedelta(hours=policy['grace_hours'])
    runs = inventory(snapshot['runs'], 'workflow_runs')
    require(snapshot['runs']['scope'] == {'repository': policy['repository'], 'branch': policy['branch']},
            'Run inventory scope differs from target')
    selected = []
    for run in runs:
        require(stamp(run['created_at']) <= now, 'Run timestamp is in the future')
        if run['path'] != policy['workflow'] or run['head_branch'] != policy['branch']:
            continue
        require(run['repository']['full_name'] == policy['repository'], 'Run repository mismatch')
        require(run['html_url'] == f"https://github.com/{policy['repository']}/actions/runs/{run['id']}",
                'Run URL does not match identity')
        require(type(run['run_attempt']) is int and run['run_attempt'] > 0
                and re.fullmatch(r'[0-9a-f]{40}', run['head_sha']) is not None, 'Invalid run identity')
        selected.append(run)
    selected.sort(key=lambda r: (stamp(r['created_at']), r['id']), reverse=True)
    scheduled = next((r for r in selected if r['event'] == 'schedule' and stamp(r['created_at']) >= slot), None)
    current = next((r for r in selected if r['head_sha'] == target['commit']
                    and r['event'] in ('push', 'schedule', 'workflow_dispatch')), None)
    def inspect_run(run):
        try:
            return execution(run, snapshot, now)
        except (KeyError, ValueError, TypeError, AttributeError) as error:
            return {'status': 'unverified', 'reason': str(error),
                    'id': run['id'] if run else None,
                    'html_url': run['html_url'] if run else None,
                    'head_sha': run['head_sha'] if run else None}
    schedule = inspect_run(scheduled)
    schedule.update(expected_at=slot.isoformat(), deadline=deadline.isoformat())
    if scheduled:
        schedule['created_delay_seconds'] = int((stamp(scheduled['created_at']) - slot).total_seconds())
        schedule['timing'] = 'after-grace' if stamp(scheduled['created_at']) > deadline else 'within-grace'
    elif now < deadline:
        schedule['status'] = 'waiting'
    else:
        schedule['status'] = 'missed'
    schedule['overdue'] = now >= deadline and schedule['status'] != 'passed'
    current_report = inspect_run(current)
    try:
        installed = installed_status(bundle, target)
    except (OSError, ValueError, KeyError, TypeError, SyntaxError, AttributeError) as error:
        installed = {'status': 'unverified', 'reason': str(error)}
    return {'schema_version': 1, 'checked_at': now.isoformat(), 'observed_at': snapshot['observed_at'],
            'target': target, 'schedule': schedule, 'current_commit_review': current_report,
            'installed_skill': installed,
            'attention': schedule['status'] in ('missed', 'failed', 'unverified') or schedule['overdue']
            or schedule.get('timing') == 'after-grace' or current_report['status'] != 'passed'
            or installed['status'] not in ('current', 'not-checked'),
            'limits': 'Observation supplied by collector, not authenticated here. Metadata is not artifact-byte verification. One run does not prove sustained reliability. No writes or repairs.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--installed-bundle', type=Path)
    args = parser.parse_args()
    try:
        report = evaluate(read_json(args.snapshot), read_json(args.policy), bundle=args.installed_bundle)
        code = 1 if report['attention'] else 0
    except (OSError, ValueError, KeyError, TypeError, OverflowError, AttributeError) as error:
        report, code = {'status': 'unverified', 'attention': True, 'reason': str(error)}, 2
    print(json.dumps(report, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
