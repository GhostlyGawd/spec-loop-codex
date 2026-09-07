"""Local product intent, decisions, scope alignment, and derived roadmap views."""
import argparse
import copy
from datetime import date
import json
from pathlib import Path
import uuid

LIMIT = 8 * 1024 * 1024


def path(core, root, suffix='state.json'):
    return core.inside(root, f'{core.META}/product/{suffix}')


def bounded(core, p):
    if p.stat().st_size > LIMIT:
        raise core.LoopError('Product record exceeds the 8 MiB limit; split or archive the product history.')
    return core.read_json(p)


def hashed(core, value):
    return core.digest(core.canonical(value))


def validate_body(core, body, changes=None):
    errors = core.schema_errors(body, core.read_json(core.PLUGIN / 'schemas/product.schema.json'))
    if errors:
        raise core.LoopError('Invalid product: ' + '; '.join(errors))
    groups = {}
    for name in ('objectives', 'opportunities', 'initiatives'):
        groups[name] = {x['id']: x for x in body[name]}
        if len(groups[name]) != len(body[name]):
            errors.append(f'Duplicate {name} ID')
    for opportunity in body['opportunities']:
        if any(x not in groups['objectives'] for x in opportunity['objectives']):
            errors.append(f"{opportunity['id']}: unknown objective")
    for item in body['initiatives']:
        for field, group in [('objectives', 'objectives'), ('opportunities', 'opportunities'), ('depends_on', 'initiatives')]:
            if any(x not in groups[group] for x in item[field]):
                errors.append(f"{item['id']}: unknown {field}")
        if changes is not None and any(x not in changes for x in item['changes']):
            errors.append(f"{item['id']}: unknown change")
        if not item['objectives']:
            errors.append(f"{item['id']}: link at least one objective")
        when = item['date']
        if when['kind'] == 'none':
            if when['value']:
                errors.append(f"{item['id']}: date must be empty for kind none")
        else:
            try:
                parsed = date.fromisoformat(when['value'])
                if parsed.isoformat() != when['value']:
                    raise ValueError()
            except ValueError:
                errors.append(f"{item['id']}: date must be YYYY-MM-DD")
    if core.cycles({k: x['depends_on'] for k, x in groups['initiatives'].items()}):
        errors.append('Initiative dependency cycle')
    estimates = body['capacity']['estimates']
    if len({x['change'] for x in estimates}) != len(estimates):
        errors.append('Duplicate capacity estimate for one change')
    for estimate in estimates:
        if estimate['low_days'] > estimate['high_days']:
            errors.append('Capacity estimate range is reversed')
        if changes is not None and estimate['change'] not in changes:
            errors.append('Capacity estimate refers to an unknown change')
    if errors:
        raise core.LoopError('Invalid product: ' + '; '.join(errors))


def validate_state(core, state):
    errors = core.schema_errors(state, core.read_json(core.PLUGIN / 'schemas/product-state.schema.json'))
    if errors:
        raise core.LoopError('Invalid product state: ' + '; '.join(errors))
    validate_body(core, state['body'])
    payload = {k: v for k, v in state.items() if k != 'digest'}
    if hashed(core, payload) != state['digest']:
        raise core.LoopError('Product digest mismatch. Use product apply with a separate draft; do not edit stored state.')
    decisions = state['decisions']
    if len(decisions) != state['revision'] + 1:
        raise core.LoopError('Product decision history is incomplete')
    previous, reconstructed = '', {}
    for i, decision in enumerate(decisions):
        if decision['revision'] != i or decision['before'] != previous:
            raise core.LoopError('Product decision history is inconsistent')
        sections = [x['section'] for x in decision['changes']]
        if len(set(sections)) != len(sections) or sorted(sections) != decision['changed_sections']:
            raise core.LoopError('Product decision change list is inconsistent')
        for edit in decision['changes']:
            try:
                before, after = json.loads(edit['before_json']), json.loads(edit['after_json'])
            except ValueError as exc:
                raise core.LoopError('Product decision has invalid historical values') from exc
            if reconstructed.get(edit['section']) != before:
                raise core.LoopError('Product decision before-value does not match history')
            reconstructed[edit['section']] = after
        if hashed(core, reconstructed) != decision['after']:
            raise core.LoopError('Product decision after-value does not match history')
        previous = decision['after']
    if previous != hashed(core, state['body']):
        raise core.LoopError('Product intent differs from the last decision')
    return state


def read(core, root):
    return validate_state(core, bounded(core, path(core, root)))


def default_body():
    return {'strategy': {'audience': 'Unknown — capture the intended user', 'problem': 'Unknown — capture the need',
        'positioning': 'Unknown', 'business_model': 'Unknown', 'constraints': [], 'non_goals': [],
        'review_trigger': 'Review before committing implementation'}, 'objectives': [], 'opportunities': [],
        'initiatives': [], 'capacity': {'wip_limit': 1, 'available_days': 0, 'estimates': []}}


def store_intent(core, root, body, old, args):
    for key in ('actor', 'reason', 'authority_ref'):
        if not getattr(args, key, '').strip():
            raise core.LoopError(f'{key} is required')
    revision = 0 if old is None else old['revision'] + 1
    decision = {'revision': revision, 'at': core.stamp(), 'actor': args.actor,
        'authority_ref': args.authority_ref, 'reason': args.reason,
        'before': '' if old is None else hashed(core, old['body']), 'after': hashed(core, body),
        'changed_sections': sorted(k for k in body if old is None or body[k] != old['body'][k])}
    decision['changes'] = [{'section': k,
        'before_json': json.dumps(None if old is None else old['body'][k], sort_keys=True, ensure_ascii=False),
        'after_json': json.dumps(body[k], sort_keys=True, ensure_ascii=False)} for k in decision['changed_sections']]
    value = {'schema_version': 1, 'revision': revision, 'body': body,
        'decisions': ([] if old is None else old['decisions']) + [decision]}
    value['digest'] = hashed(core, value)
    validate_state(core, value)
    if len((json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode()) > LIMIT:
        raise core.LoopError('Product history exceeds the 8 MiB limit; no intent was written')
    core.atomic_json(path(core, root), value)
    return {'revision': revision, 'digest': value['digest'], 'decision': decision,
            'trust': 'Local editable decision record; authority is not authenticated.'}


def apply(core, root, args):
    with core.writer(root):
        _, changes = core.load_project(root)
        old = read(core, root)
        if old['digest'] != args.expect_digest:
            raise core.LoopError('Product conflict: read the current digest and reconcile the draft')
        body = bounded(core, core.inside(root, args.file))
        validate_body(core, body, changes)
        if read(core, root)['digest'] != old['digest']:
            raise core.LoopError('Product conflict: intent changed while the draft was checked')
        if body == old['body']:
            return {'revision': old['revision'], 'digest': old['digest'], 'changed': False}
        return store_intent(core, root, body, old, args)


def scope(core, body, change_id):
    """Only requirement-relevant fields enter the change's semantic binding."""
    objectives = {x['id']: x for x in body['objectives']}
    linked = []
    for item in sorted(body['initiatives'], key=lambda x: x['id']):
        if change_id in item['changes']:
            linked.append({'initiative': item['id'], 'scope': item['scope'], 'non_goals': item['non_goals'], 'risk': item['risk'],
                'objectives': [{k: v for k, v in objectives[key].items() if k not in ('owner', 'title')} for key in sorted(item['objectives'])]})
    return hashed(core, linked) if linked else ''


def alignment_errors(core, root, change):
    if not path(core, root).exists():
        return ['Product state is missing for the bound change'] if change.get('product_scope') else []
    state = read(core, root)
    expected = scope(core, state['body'], change['id'])
    actual = change.get('product_scope', '')
    if expected != actual:
        return ['Product scope needs contract review and product align']
    rank = {'low': 0, 'medium': 1, 'high': 2}
    if any(change['id'] in x['changes'] and rank[x['risk']] > rank[change['risk']] for x in state['body']['initiatives']):
        return ['Change risk is below its linked initiative risk; review the contract risk']
    if expected and change.get('product_review', {}).get('scope') != expected:
        return ['Product scope lacks a recorded contract review']
    return []


def align(core, root, args):
    with core.writer(root):
        state = read(core, root)
        config, _, change = core.select(root, args.change)
        if state['digest'] != args.expect_digest or core.contract_hash(root, config, change) != args.expect_contract:
            raise core.LoopError('Alignment conflict: product or contract changed; review current inputs')
        for key in ('actor', 'reason', 'authority_ref'):
            if not getattr(args, key, '').strip():
                raise core.LoopError(f'{key} is required')
        expected = scope(core, state['body'], args.change)
        if expected:
            change['product_scope'] = expected
            change['product_review'] = {'scope': expected, 'actor': args.actor, 'reason': args.reason,
                                       'authority_ref': args.authority_ref, 'at': core.stamp()}
        else:
            # Unlinking also changes the contract hash and therefore invalidates old evidence.
            change.pop('product_scope', None)
            change.pop('product_review', None)
        core.atomic_json(core.inside(root, f'{core.META}/changes/{args.change}.json'), change)
        return {'change': args.change, 'contract_hash': core.contract_hash(root, config, change),
                'scope': expected, 'review': 'Recorded review, not a semantic proof. Collect fresh evidence.'}


def inventory(core, root):
    config, changes = core.load_project(root)
    return {'project': config['name'], 'source_hash': core.snapshot(root), 'intent': 'unverified',
        'changes': [{'id': k, 'title': v['title'], 'phase_reported': v['phase'],
                     'tasks_reported': len(v['tasks'])} for k, v in sorted(changes.items())],
        'next': 'Review existing contracts, code, and user evidence before linking initiatives. No product history was invented.'}


def input_hash(core, root):
    inputs = [['source', core.snapshot(root)], ['engine', core.VERSION]]
    folder = core.inside(root, core.META)
    for p in sorted(folder.rglob('*')):
        rel = p.relative_to(root).as_posix()
        parts = p.relative_to(folder).parts
        if parts[:2] in (('product', 'roadmap.json'), ('product', 'backups')) or any(x == '.lock' or x.startswith('.write-') for x in parts):
            continue
        core.inside(root, rel)
        if p.is_file():
            inputs.append([rel, core.digest(p.read_bytes())])
    # A declared artifact can be Git-ignored and outside the metadata directory.
    _, changes = core.load_project(root)
    for change in changes.values():
        for artifact in change['artifacts']:
            p = core.inside(root, artifact['path'])
            inputs.append([artifact['path'], core.digest(p.read_bytes()) if p.is_file() else 'missing'])
    return hashed(core, inputs)


def derive(core, root):
    import release_ledger
    state = read(core, root)
    body = state['body']
    config, changes = core.load_project(root)
    warnings, reports, releases = [], {}, []
    linked_ids = {k for x in body['initiatives'] for k in x['changes']}
    for key in sorted(linked_ids):
        if key not in changes:
            reports[key] = {'state': 'unknown', 'errors': ['Linked change is missing']}
            continue
        change = changes[key]
        try:
            reports[key] = {'ready': core.gate(root, key, 'ready'), 'verify': core.gate(root, key, 'verify'),
                'release': core.gate(root, key, 'release'), 'contract_hash': core.contract_hash(root, config, change),
                'tasks_reported': {status: sum(t['status'] == status for t in change['tasks'])
                                   for status in ('todo', 'doing', 'blocked', 'done')}}
        except (core.LoopError, OSError) as exc:
            reports[key] = {'state': 'unknown', 'errors': [str(exc)]}
    release_folder = core.inside(root, f'{core.META}/releases')
    for p in sorted(release_folder.glob('*.json')):
        try:
            rec, entries = release_ledger.read_release(core, root, p.stem)
            if not linked_ids.intersection(entries):
                continue
            result = {'id': rec['id'], 'sealed_at': rec['sealed_at'], 'changes': sorted(entries),
                'target_reported': rec['target'], 'artifact': rec['artifact'], 'trust': rec['trust'],
                'deployment': 'unverified'}
            try:
                result['outcomes'] = release_ledger.learn(core, root, rec['id'])
            except (core.LoopError, OSError) as exc:
                result['outcomes'] = {'passed': False, 'checks': {}, 'errors': [str(exc)]}
            releases.append(result)
        except (core.LoopError, OSError) as exc:
            warnings.append(f'{p.name}: {exc}')
    rows = []
    for item in body['initiatives']:
        ids = item['changes']
        current = [reports[k] for k in ids]
        blocked = [k for k in ids if not reports[k].get('release', {}).get('passed', False)]
        history = [r for r in releases if set(ids).intersection(r['changes'])]
        covered = {k for r in history for k in r['changes'] if k in ids}
        missing = sorted(set(ids) - covered)
        verified = bool(ids) and all(r.get('verify', {}).get('passed', False) for r in current)
        ready = bool(ids) and all(r.get('release', {}).get('passed', False) for r in current)
        facts = {'candidate': 'release-ready' if ready else 'verified' if verified else 'unverified',
            'blocking_changes': blocked, 'historical_coverage': 'none' if not covered else 'complete' if not missing else 'partial',
            'historical_missing_changes': missing, 'deployment': 'unverified', 'releases': [r['id'] for r in history]}
        suggestion = 'Review intent and define the first change' if not ids else 'Resolve current delivery gaps' if blocked else 'Review the release action within existing authority'
        if history:
            latest = max(history, key=lambda r: (r['sealed_at'], r['id']))
            if any(v == 'fail' for v in latest['outcomes'].get('checks', {}).values()):
                suggestion = 'Review the failed outcome and propose keep/change/stop; do not change priority automatically'
            elif not latest['outcomes']['passed']:
                suggestion = 'Collect missing outcome evidence for the identified release'
        rows.append({**item, 'delivery': facts, 'next_decision': suggestion})
    by_id = {r['id']: r for r in rows}
    for row in rows:
        # Transitive dependencies must each have current release readiness; history is insufficient.
        pending, visited, blocked = list(row['depends_on']), set(), []
        while pending:
            key = pending.pop()
            if key in visited:
                continue
            visited.add(key)
            dependency = by_id[key]
            if dependency['delivery']['candidate'] != 'release-ready' or dependency['status'] != 'active':
                blocked.append(key)
            pending.extend(dependency['depends_on'])
        row['delivery']['blocking_initiatives'] = sorted(blocked)
        row['delivery']['plan_ready'] = row['delivery']['candidate'] == 'release-ready' and not blocked
    now_items = [x for x in rows if x['horizon'] == 'now' and x['status'] == 'active']
    now_changes = sorted({k for x in now_items for k in x['changes']})
    estimates = {x['change']: x for x in body['capacity']['estimates']}
    unknown = [k for k in now_changes if k not in estimates]
    low = sum(estimates[k]['low_days'] for k in now_changes if k in estimates)
    high = sum(estimates[k]['high_days'] for k in now_changes if k in estimates)
    capacity = {**body['capacity'], 'active_now': len(now_items), 'unique_now_changes': now_changes,
        'estimated_days': {'low': low, 'high': high}, 'unknown_estimates': unknown,
        'wip_exceeded': len(now_items) > body['capacity']['wip_limit'],
        'effort_exceeds_capacity': high > body['capacity']['available_days']}
    if capacity['wip_exceeded'] or capacity['effort_exceeds_capacity'] or unknown:
        warnings.append('Review capacity; ranges are planning estimates, not delivery forecasts')
    sync = {'mode': 'local-on-invocation', 'external': 'not-configured'}
    import github_sync
    if github_sync.path(core, root).exists():
        try:
            sync = github_sync.status(core, root)
        except (core.LoopError, OSError, ValueError) as exc:
            sync = {'mode': 'agent-mediated-github-file', 'status': 'unavailable', 'error': str(exc)}
    return {'schema_version': 1, 'product_revision': state['revision'], 'product_digest': state['digest'],
        'strategy': body['strategy'], 'objectives': body['objectives'], 'opportunities': body['opportunities'],
        'initiatives': rows, 'changes': reports, 'releases': releases, 'capacity': capacity,
        'warnings': warnings, 'sync': sync,
        'trust': 'Local editable records. Historical coverage does not prove one combined deployment or product value.'}


def refresh(core, root):
    with core.writer(root):
        before = input_hash(core, root)
        view = derive(core, root)
        if input_hash(core, root) != before:
            raise core.LoopError('Roadmap conflict: inputs changed during refresh; retry after reconciliation')
        view['input_digest'] = before
        view['content_digest'] = hashed(core, view)
        target = path(core, root, 'roadmap.json')
        # Stable content, fresh evaluation time. Evidence expiry is evaluated on every invocation.
        view['checked_at'] = core.stamp()
        view['freshness'] = 'current-at-check'
        core.atomic_json(target, view)
        return view


def refresh_status(core, root):
    try:
        view = refresh(core, root)
        return {'freshness': view['freshness'], 'checked_at': view['checked_at'],
                'content_digest': view['content_digest'], 'path': f'{core.META}/product/roadmap.json'}
    except (core.LoopError, OSError, ValueError, RecursionError) as exc:
        return {'freshness': 'stale-or-unavailable', 'error': str(exc),
                'next': 'Reconcile the inputs and run roadmap refresh. The prior saved view is not current.'}


def context_view(core, root, change_id):
    view = refresh(core, root)
    rows = [x for x in view['initiatives'] if change_id in x['changes']]
    objectives = {k for row in rows for k in row['objectives']}
    return {'product_digest': view['product_digest'], 'checked_at': view['checked_at'],
        'strategy': view['strategy'], 'objectives': [x for x in view['objectives'] if x['id'] in objectives],
        'initiatives': rows, 'sync': view['sync']}


def add_parser(sub):
    command = sub.add_parser('product', help='Manage local product intent and explicit decisions')
    actions = command.add_subparsers(dest='action', required=True)
    for name in ('init', 'show', 'apply', 'align', 'inventory', 'backup', 'restore'):
        p = actions.add_parser(name)
        if name in ('init', 'apply', 'align', 'restore'):
            for key in ('actor', 'reason', 'authority-ref'):
                p.add_argument('--'+key, required=True)
        if name in ('apply', 'align', 'restore'):
            p.add_argument('--expect-digest', required=True)
        if name in ('apply', 'restore'):
            p.add_argument('--file', required=True, help='Relative project path; use .spec-loop/artifacts for drafts')
        if name == 'align':
            p.add_argument('change')
            p.add_argument('--expect-contract', required=True)
    command = sub.add_parser('roadmap', help='Recompute and display current local roadmap facts')
    command.add_argument('action', choices=('show', 'refresh'))
    command.add_argument('--max-chars', type=int)


def execute(core, root, args):
    if args.command == 'roadmap':
        view = refresh(core, root)
        config, _ = core.load_project(root)
        limit = args.max_chars if args.max_chars is not None else config['context_max_chars']
        size = len(json.dumps(view, indent=2, ensure_ascii=False))
        if size > limit:
            raise core.LoopError(f'Roadmap needs {size} characters; budget is {limit}. View saved; raise the explicit budget or use context for one change. No constraints were silently dropped.')
        return view
    if args.action == 'show':
        result = read(core, root)
        result['contract_hashes'] = {k: core.contract_hash(root, config, c) for config, changes in [core.load_project(root)] for k, c in changes.items()}
        return result
    if args.action == 'inventory':
        return inventory(core, root)
    if args.action == 'apply':
        return apply(core, root, args)
    if args.action == 'align':
        return align(core, root, args)
    if args.action == 'init':
        core.load_project(root)
        with core.writer(root):
            if path(core, root).exists():
                raise core.LoopError('Product state already exists; no file was replaced')
            return store_intent(core, root, default_body(), None, args)
    if args.action == 'backup':
        with core.writer(root):
            state = read(core, root)
            target = path(core, root, f'backups/BKP-{uuid.uuid4().hex}.json')
            core.atomic_json(target, state)
            return {'backup': target.relative_to(root).as_posix(), 'digest': state['digest'], 'scope': 'Product intent and decision history only; use Git/project backups for code and evidence.'}
    if args.action == 'restore':
        with core.writer(root):
            old = read(core, root)
            if old['digest'] != args.expect_digest:
                raise core.LoopError('Product restore conflict; read the current state')
            backup = validate_state(core, bounded(core, core.inside(root, args.file)))
            _, changes = core.load_project(root)
            validate_body(core, backup['body'], changes)
            return store_intent(core, root, backup['body'], old, args)
    raise core.LoopError('Unknown product action')
