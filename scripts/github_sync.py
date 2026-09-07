"""Agent-mediated GitHub product-file sync. No network or credential access."""
import argparse
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
import uuid
import product

MAX_AGE = 900
MISSING = object()


def path(core, root):
    return core.inside(root, f'{core.META}/github/state.json')


def hash_value(core, value):
    return core.digest(core.canonical(value))


def blob_sha(content):
    raw = content.encode('utf-8')
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def clock(core, value):
    try:
        result = datetime.fromisoformat(value)
        if result.tzinfo is None:
            raise ValueError()
        return result.astimezone(timezone.utc)
    except (ValueError, TypeError) as exc:
        raise core.LoopError('Use a timezone-aware snapshot time') from exc


def config_valid(core, config):
    expected = {'repository', 'repository_id', 'branch', 'path', 'visibility'}
    if not isinstance(config, dict) or set(config) != expected or not all(isinstance(v, str) and v.strip() for v in config.values()):
        raise core.LoopError('Invalid GitHub target config')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', config['repository']):
        raise core.LoopError('Use owner/repository')
    if not config['repository_id'].isdigit() or config['visibility'] not in ('public', 'private'):
        raise core.LoopError('Invalid repository ID or visibility')
    branch = config['branch']
    if any(x in branch for x in ('..', '@{', '\\', ':', ' ', '~', '^', '?', '*', '[')) or branch.startswith(('/', '-')) or branch.endswith(('/', '.', '.lock')):
        raise core.LoopError('Invalid target branch')
    target = config['path']
    if not target.startswith(('docs/', '.spec-loop/exchange/')) or not target.endswith('.json') or '..' in target.split('/') or '\\' in target:
        raise core.LoopError('Use a JSON path under docs/ or .spec-loop/exchange/')


def read(core, root):
    state = product.bounded(core, path(core, root))
    keys = {'schema_version', 'config', 'revision', 'baseline', 'active', 'history', 'last_check', 'status', 'digest'}
    if not isinstance(state, dict) or set(state) != keys or type(state['schema_version']) is not int or state['schema_version'] != 1:
        raise core.LoopError('Invalid or unsupported GitHub sync state')
    if hash_value(core, {k:v for k,v in state.items() if k != 'digest'}) != state['digest']:
        raise core.LoopError('GitHub sync state digest mismatch')
    config_valid(core, state['config'])
    if type(state['revision']) is not int or not isinstance(state['history'], list) or not isinstance(state['last_check'], dict):
        raise core.LoopError('Invalid sync revision or history')
    if state['last_check'] and set(state['last_check']) != {'at','blob_sha'}:
        raise core.LoopError('Invalid last-check record')
    if state['baseline'] is not None:
        product.validate_body(core, state['baseline'])
    if state['active'] is not None:
        plan = state['active']
        if not isinstance(plan, dict) or not {'id','candidate','expected_local','local_body_hash','remote_sha','action','at','actor','authority_ref','reason','phase'}.issubset(plan):
            raise core.LoopError('Invalid pending operation')
        product.validate_body(core, plan['candidate'])
    return state


def save(core, root, state):
    state = copy.deepcopy(state)
    state['revision'] += 1
    state.pop('digest', None)
    state['digest'] = hash_value(core, state)
    if len(json.dumps(state, ensure_ascii=False, indent=2).encode()) > product.LIMIT:
        raise core.LoopError('Sync history exceeds 8 MiB; no state was replaced')
    core.atomic_json(path(core, root), state)
    return state


def identity(args):
    result = {k:getattr(args,k,'') for k in ('actor','authority_ref','reason')}
    if any(not v.strip() for v in result.values()):
        raise ValueError('Actor, reason, and authority reference are required')
    return result


def read_snapshot(core, root, relative, config):
    value = product.bounded(core, core.inside(root, relative))
    errors = core.schema_errors(value, core.read_json(core.PLUGIN/'schemas/github-snapshot.schema.json'))
    if errors:
        raise core.LoopError('Invalid GitHub snapshot: ' + '; '.join(errors))
    if any(value[k] != config[k] for k in config):
        raise core.LoopError('Snapshot target does not match configured repository, branch, path, or visibility')
    age = (core.now()-clock(core,value['observed_at'])).total_seconds()
    if age < -30 or age > MAX_AGE:
        raise core.LoopError('Snapshot is stale or in the future; fetch the current target')
    if value['status'] == 'unavailable':
        raise core.LoopError('GitHub is unavailable: ' + value['basis'])
    if not re.fullmatch(r'[a-f0-9]{40}', value['branch_sha']):
        raise core.LoopError('Snapshot needs an observed branch commit')
    if value['status'] == 'absent':
        if value['content'] or value['blob_sha'] or not value['basis'].strip():
            raise core.LoopError('Absence needs a branch/directory observation, empty content, and no blob SHA')
        return value, None
    if blob_sha(value['content']) != value['blob_sha']:
        raise core.LoopError('Snapshot Git blob SHA does not match its content')
    try:
        document = json.loads(value['content'])
    except ValueError as exc:
        raise core.LoopError('Remote content is not a product JSON document') from exc
    if not isinstance(document,dict) or set(document) != {'schema_version','product'} or document['schema_version'] != 1:
        raise core.LoopError('Remote file is not a supported product exchange document')
    product.validate_body(core, document['product'])
    return value, document['product']


def display(value):
    return {'exists': value is not MISSING, 'value': None if value is MISSING else value}


def merge(base, local, remote, location='$'):
    """Merge independent fields; record arrays use IDs, ordinary arrays are atomic."""
    if local == remote:
        return copy.deepcopy(local) if local is not MISSING else MISSING, []
    if local == base:
        return copy.deepcopy(remote) if remote is not MISSING else MISSING, []
    if remote == base:
        return copy.deepcopy(local) if local is not MISSING else MISSING, []
    if all(isinstance(x,dict) for x in (base,local,remote)):
        result, conflicts = {}, []
        for key in sorted(set(base)|set(local)|set(remote)):
            value, problems = merge(base.get(key,MISSING), local.get(key,MISSING), remote.get(key,MISSING),location+'.'+key)
            if value is not MISSING: result[key] = value
            conflicts.extend(problems)
        return result, conflicts
    if all(isinstance(x,list) for x in (base,local,remote)):
        key = 'change' if location.endswith('.estimates') else 'id'
        if all(all(isinstance(item,dict) and key in item for item in group) for group in (base,local,remote)):
            indexed = [{x[key]:x for x in group} for group in (base,local,remote)]
            result, conflicts = merge(*indexed,location)
            return [result[k] for k in sorted(result)], conflicts
    return copy.deepcopy(local) if local is not MISSING else MISSING, [{'path':location,'base':display(base),'local':display(local),'remote':display(remote)}]


def content_for(body):
    return json.dumps({'schema_version':1,'product':body},ensure_ascii=False,indent=2)+'\n'


def request_for(state):
    plan, config = state['active'], state['config']
    if plan['action'] == 'none': return None
    args = {'repository_full_name': config['repository'], 'branch':config['branch'], 'path':config['path'],
            'content':content_for(plan['candidate']), 'message':'Sync product intent '+plan['id']}
    if plan['action'] == 'update': args['sha'] = plan['remote_sha']
    return {'tool':'github_'+('create_file' if plan['action']=='create' else 'update_file'), 'arguments':args,
            'before_write':'Fetch the target again. If it differs, cancel/replan; after a timeout, compare remote content before any retry.'}


def prepare(core, root, args):
    with core.writer(root):
        state = read(core, root)
        if state['active'] is not None:
            raise core.LoopError('An operation is pending; confirm or cancel it before preparing another')
        local_state = product.read(core, root)
        try:
            snapshot, remote = read_snapshot(core,root,args.snapshot,state['config'])
        except core.LoopError as exc:
            state['status']='read-failed'
            state['history'].append({'id':'READ-'+uuid.uuid4().hex,'at':core.stamp(),'phase':'read-failed','error':str(exc)})
            save(core,root,state)
            raise
        if state['baseline'] is not None and remote != state['baseline']:
            state.update(status='needs-reconciliation',last_check={'at':snapshot['observed_at'],'blob_sha':snapshot['blob_sha']})
            state=save(core,root,state)
        local, baseline = local_state['body'], state['baseline']
        if remote is None:
            if baseline is None:
                candidate, conflicts = local, []
            else:
                candidate, conflicts = local, [{'path':'$', 'base':display(baseline),'local':display(local),'remote':display(MISSING)}]
        elif baseline is None:
            candidate = local
            conflicts = [] if local == remote else [{'path':'$', 'base':display(MISSING),'local':display(local),'remote':display(remote)}]
        else:
            candidate, conflicts = merge(baseline,local,remote)
        conflict_digest = hash_value(core, {'local':local_state['digest'],'remote':snapshot['blob_sha'], 'conflicts':conflicts})
        if args.resolved_file:
            if not conflicts or args.expect_conflict != conflict_digest:
                raise core.LoopError('Conflict resolution does not match the current comparison')
            candidate = product.bounded(core,core.inside(root,args.resolved_file))
        elif conflicts:
            state.update(status='conflict',last_check={'at':snapshot['observed_at'],'blob_sha':snapshot['blob_sha']})
            save(core,root,state)
            return {'passed':False,'status':'conflict','conflict_digest':conflict_digest,'conflicts':conflicts,
                    'next':'Reconcile a complete product body, then prepare with --resolved-file and --expect-conflict. No remote write was prepared.'}
        _, changes = core.load_project(root)
        product.validate_body(core,candidate,changes)
        if state['config']['visibility'] == 'public':
            if not args.reviewed_public:
                raise core.LoopError('Review the entire candidate for public disclosure and use --reviewed-public')
            if any(x['privacy'] != 'public' for x in candidate['opportunities']):
                raise core.LoopError('Internal or restricted opportunities cannot be synchronized to a public repository')
        if product.read(core,root)['digest'] != local_state['digest']:
            raise core.LoopError('Product changed during comparison; replan')
        operation = {'id':'SYNC-'+uuid.uuid4().hex,'candidate':candidate,'expected_local':local_state['digest'],
            'local_body_hash':hash_value(core,local),'remote_sha':snapshot['blob_sha'],
            'action':'create' if remote is None else 'none' if candidate==remote else 'update',
            'at':core.stamp(),'phase':'prepared',**identity(args)}
        state.update(active=operation,status='pending',last_check={'at':snapshot['observed_at'],'blob_sha':snapshot['blob_sha']})
        state=save(core,root,state)
        return {'status':'pending','operation':operation,'tool_request':request_for(state),
                'next':'Re-read before a remote write; then fetch a fresh snapshot and github confirm. Do not infer success from this plan.'}


def confirm(core, root, args):
    with core.writer(root):
        state = read(core,root)
        if state['active'] is None:
            completed = next((x for x in reversed(state['history']) if x['id']==args.operation and x['phase']=='completed'),None)
            if completed:
                return {'status':'already-completed','operation':args.operation,'at':completed['completed_at'],
                        'note':'No new remote check occurred; use github status for freshness'}
            raise core.LoopError('No matching active operation')
        active = state['active']
        if active['id'] != args.operation: raise core.LoopError('Operation ID does not match')
        snapshot, remote = read_snapshot(core,root,args.snapshot,state['config'])
        if remote != active['candidate']:
            raise core.LoopError('Remote content does not match the proposed result; do not mark sync complete')
        # Preserve remote success before a local conflict/crash; a later confirm can resume.
        active.update(phase='remote-confirmed',observed_blob_sha=snapshot['blob_sha'])
        state['last_check']={'at':snapshot['observed_at'],'blob_sha':snapshot['blob_sha']}
        state=save(core,root,state)
        active=state['active']
        current=product.read(core,root)
        if current['digest'] != active['expected_local'] and current['body'] != active['candidate']:
            raise core.LoopError('Remote result recorded, but local product changed. Preserve it; cancel/replan from a fresh snapshot to reconcile.')
        _, changes=core.load_project(root)
        product.validate_body(core,active['candidate'],changes)
        if current['body'] != active['candidate']:
            product.store_intent(core,root,active['candidate'],current,argparse.Namespace(actor=active['actor'],
                authority_ref=active['authority_ref'],reason=active['reason']+'; GitHub sync '+active['id']))
        event={**active,'phase':'completed','completed_at':core.stamp()}
        state.update(baseline=active['candidate'],active=None,status='current-at-check',history=state['history']+[event])
        save(core,root,state)
        return {'status':'current-at-check','operation':args.operation,'remote_blob_sha':snapshot['blob_sha'],
                'checked_at':snapshot['observed_at'],'trust':'Agent-supplied GitHub read-back; local receipt is unsigned.'}


def status(core, root):
    state=read(core,root)
    current=product.read(core,root)
    label=state['status']
    if state['active'] is not None:
        label=state['active']['phase']
    elif label in ('conflict', 'needs-reconciliation', 'read-failed'):
        pass
    elif state['baseline'] is not None and current['body'] != state['baseline']:
        label='local-changed'
    elif state['last_check'] and (core.now()-clock(core,state['last_check']['at'])).total_seconds()>MAX_AGE:
        label='stale'
    return {'mode':'agent-mediated-github-file','status':label,'target':state['config'],
        'last_check':state['last_check'],'pending_operation':state['active']['id'] if state['active'] else None,
        'external':'Last observed file only; refresh requires an actual GitHub MCP read. No background job.'}


def add_parser(sub):
    p=sub.add_parser('github',help='Prepare and reconcile product-file operations for GitHub MCP')
    actions=p.add_subparsers(dest='action',required=True)
    for name in ('configure','status','plan','confirm','cancel'):
        a=actions.add_parser(name)
        if name in ('configure','plan','cancel'):
            for k in ('actor','reason','authority-ref'): a.add_argument('--'+k,required=True)
        if name=='configure':
            for k in ('repository','repository-id','branch','path'): a.add_argument('--'+k,required=True)
            a.add_argument('--visibility',choices=('public','private'),required=True)
        if name in ('plan','confirm'): a.add_argument('--snapshot',required=True)
        if name=='plan':
            a.add_argument('--reviewed-public',action='store_true')
            a.add_argument('--resolved-file')
            a.add_argument('--expect-conflict')
        if name in ('confirm','cancel'): a.add_argument('operation')


def execute(core,root,args):
    if args.action=='status': return status(core,root)
    if args.action=='plan': return prepare(core,root,args)
    if args.action=='confirm': return confirm(core,root,args)
    if args.action=='configure':
        product.read(core,root)
        config={k:getattr(args,k) for k in ('repository','repository_id','branch','path','visibility')}
        config_valid(core,config)
        with core.writer(root):
            if path(core,root).exists(): raise core.LoopError('Sync config already exists; no target was replaced')
            save(core,root,{'schema_version':1,'config':config,'revision':-1,'baseline':None,'active':None,
                'history':[{'id':'configuration','at':core.stamp(),**identity(args)}], 'last_check':{},'status':'not-checked'})
        return status(core,root)
    if args.action=='cancel':
        with core.writer(root):
            state=read(core,root)
            if state['active'] is None or state['active']['id']!=args.operation: raise core.LoopError('No matching active operation')
            event={**state['active'],'phase':'cancelled','cancelled_at':core.stamp(),'cancellation':identity(args)}
            state.update(active=None,status='needs-reconciliation',history=state['history']+[event])
            save(core,root,state)
        return {'status':'needs-reconciliation','note':'Cancellation records the local decision; it does not undo any remote write.'}
    raise core.LoopError('Unknown GitHub action')
