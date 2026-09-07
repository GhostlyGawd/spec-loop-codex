"""GitHub sync invariants with synthetic connector snapshots; live checks are separate."""
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
from test_spec_loop import loop, PLUGIN
from test_product import intent
import product
import github_sync as sync


class GitHubTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'project'
        shutil.copytree(PLUGIN/'examples/reading-list',self.root)
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        self.actor={'actor':'test','authority_ref':'Synthetic test only','reason':'Exercise sync'}
        product.execute(loop,self.root,argparse.Namespace(command='product',action='init',**self.actor))
        body=intent();body['opportunities'][0]['privacy']='public';self.apply(body)
        self.config={'repository':'example/test','repository_id':'123','branch':'test-sync','path':'docs/product.json','visibility':'public'}
        sync.execute(loop,self.root,argparse.Namespace(action='configure',**self.config,**self.actor))

    def body(self): return product.read(loop,self.root)['body']
    def apply(self,body):
        filename='.spec-loop/artifacts/draft.json';loop.atomic_json(self.root/filename,body)
        product.apply(loop,self.root,argparse.Namespace(file=filename,expect_digest=product.read(loop,self.root)['digest'],**self.actor))
    def snapshot(self,body=None,status=None,**overrides):
        content='' if body is None else sync.content_for(body)
        snap={**self.config,'observed_at':loop.stamp(),'status':status or ('absent' if body is None else 'present'),
            'content':content,'blob_sha':sync.blob_sha(content) if content else '', 'branch_sha':'a'*40,
            'basis':'Synthetic branch/directory read confirms the fixture',**overrides}
        filename='.spec-loop/artifacts/github-snapshot.json';loop.atomic_json(self.root/filename,snap)
        return filename
    def plan(self,snapshot,**overrides):
        args={'snapshot':snapshot,'reviewed_public':True,'resolved_file':None,'expect_conflict':None,**self.actor,**overrides}
        return sync.prepare(loop,self.root,argparse.Namespace(**args))
    def confirm(self,plan,body=None):
        return sync.confirm(loop,self.root,argparse.Namespace(operation=plan['operation']['id'],snapshot=self.snapshot(body or plan['operation']['candidate'])))
    def baseline(self):
        plan=self.plan(self.snapshot());self.confirm(plan);return copy.deepcopy(self.body())

    def test_create_then_readback_and_noop(self):
        before=product.read(loop,self.root)['revision']
        plan=self.plan(self.snapshot())
        self.assertEqual(plan['tool_request']['tool'],'github_create_file')
        self.assertNotIn('sha',plan['tool_request']['arguments'])
        self.assertIsNone(sync.read(loop,self.root)['baseline'])
        self.confirm(plan)
        self.assertEqual(product.read(loop,self.root)['revision'],before)
        again=self.plan(self.snapshot(self.body()))
        self.assertIsNone(again['tool_request']);self.confirm(again)
        self.assertEqual(sync.status(loop,self.root)['status'],'current-at-check')

    def test_independent_local_remote_fields_merge_and_record_decision(self):
        base=self.baseline();local=copy.deepcopy(base);remote=copy.deepcopy(base)
        local['initiatives'][0]['horizon']='next';self.apply(local)
        remote['initiatives'][0]['owner']='Remote owner'
        plan=self.plan(self.snapshot(remote))
        candidate=plan['operation']['candidate']
        self.assertEqual(candidate['initiatives'][0]['horizon'],'next')
        self.assertEqual(candidate['initiatives'][0]['owner'],'Remote owner')
        self.assertEqual(plan['tool_request']['arguments']['sha'],sync.blob_sha(sync.content_for(remote)))
        before=product.read(loop,self.root)['revision'];self.confirm(plan)
        self.assertEqual(self.body(),candidate)
        self.assertEqual(product.read(loop,self.root)['revision'],before+1)

    def test_overlapping_edits_conflict_and_need_current_resolution_token(self):
        base=self.baseline();local=copy.deepcopy(base);remote=copy.deepcopy(base)
        local['initiatives'][0]['horizon']='next';remote['initiatives'][0]['horizon']='later';self.apply(local)
        snap=self.snapshot(remote);report=self.plan(snap)
        self.assertFalse(report['passed']);self.assertIn('horizon',report['conflicts'][0]['path'])
        self.assertEqual(sync.status(loop,self.root)['status'],'conflict')
        self.assertIsNone(sync.read(loop,self.root)['active'])
        filename='.spec-loop/artifacts/resolved.json';loop.atomic_json(self.root/filename,local)
        with self.assertRaises(loop.LoopError): self.plan(snap,resolved_file=filename,expect_conflict='wrong')
        plan=self.plan(snap,resolved_file=filename,expect_conflict=report['conflict_digest'])
        self.confirm(plan)

    def test_delete_edit_conflict_and_independent_additions(self):
        base=[{'id':'one','title':'a'}]
        _,conflicts=sync.merge(base,[],[{'id':'one','title':'edited'}],'$.initiatives')
        self.assertTrue(conflicts)
        result,conflicts=sync.merge(base,base+[{'id':'two','title':'b'}],base+[{'id':'three','title':'c'}],'$.initiatives')
        self.assertFalse(conflicts);self.assertEqual({x['id'] for x in result},{'one','two','three'})

    def test_no_baseline_different_existing_file_is_conflict(self):
        remote=copy.deepcopy(self.body());remote['strategy']['positioning']='Already different'
        self.assertFalse(self.plan(self.snapshot(remote))['passed'])

    def test_remote_delete_is_not_silently_recreated(self):
        self.baseline();self.assertFalse(self.plan(self.snapshot())['passed'])

    def test_unavailable_and_stale_snapshots_cannot_mean_absence(self):
        for overrides in [{'status':'unavailable'},{'observed_at':loop.stamp(loop.now()-timedelta(minutes=16))},
                          {'observed_at':loop.stamp(loop.now()+timedelta(minutes=2))},{'branch_sha':''}]:
            with self.subTest(overrides=overrides),self.assertRaises(loop.LoopError): self.plan(self.snapshot(**overrides))
            self.assertIsNone(sync.read(loop,self.root)['active'])

    def test_target_and_blob_hash_mismatch_rejected(self):
        for change in [{'repository_id':'999'},{'branch':'other'},{'path':'docs/other.json'},{'blob_sha':'f'*40}]:
            with self.subTest(change=change),self.assertRaises(loop.LoopError): self.plan(self.snapshot(self.body(),**change))

    def test_public_disclosure_blocks_internal_feedback(self):
        with self.assertRaises(loop.LoopError): self.plan(self.snapshot(),reviewed_public=False)
        body=copy.deepcopy(self.body());body['opportunities'][0]['privacy']='restricted';self.apply(body)
        with self.assertRaisesRegex(loop.LoopError,'restricted'): self.plan(self.snapshot())

    def test_second_plan_and_target_reconfiguration_refused(self):
        self.plan(self.snapshot())
        with self.assertRaisesRegex(loop.LoopError,'pending'): self.plan(self.snapshot())
        with self.assertRaisesRegex(loop.LoopError,'exists'):
            sync.execute(loop,self.root,argparse.Namespace(action='configure',**self.config,**self.actor))

    def test_remote_mismatch_never_completes(self):
        plan=self.plan(self.snapshot());remote=copy.deepcopy(self.body());remote['strategy']['positioning']='different'
        with self.assertRaisesRegex(loop.LoopError,'does not match'): self.confirm(plan,remote)
        self.assertIsNone(sync.read(loop,self.root)['baseline'])

    def test_local_edit_after_remote_write_is_preserved(self):
        plan=self.plan(self.snapshot());body=copy.deepcopy(self.body());body['strategy']['positioning']='New user decision';self.apply(body)
        before=product.read(loop,self.root)['digest']
        with self.assertRaisesRegex(loop.LoopError,'local product changed'): self.confirm(plan)
        self.assertEqual(before,product.read(loop,self.root)['digest'])
        self.assertEqual(sync.read(loop,self.root)['active']['phase'],'remote-confirmed')

    def test_retry_after_local_commit_does_not_duplicate_decision(self):
        base=self.baseline();remote=copy.deepcopy(base);remote['strategy']['positioning']='Remote edit'
        plan=self.plan(self.snapshot(remote));before=product.read(loop,self.root)['revision']
        original=sync.save;count=0
        def fail_last(*args):
            nonlocal count
            count+=1
            if count==2: raise OSError('Simulated crash after product write')
            return original(*args)
        with patch.object(sync,'save',side_effect=fail_last),self.assertRaises(OSError): self.confirm(plan)
        self.assertEqual(product.read(loop,self.root)['revision'],before+1)
        self.confirm(plan)
        self.assertEqual(product.read(loop,self.root)['revision'],before+1)
        result=self.confirm(plan)
        self.assertEqual(result['status'],'already-completed')

    def test_cancel_preserves_baseline_and_does_not_undo_remote(self):
        self.baseline();plan=self.plan(self.snapshot(self.body()))
        before=copy.deepcopy(sync.read(loop,self.root)['baseline'])
        sync.execute(loop,self.root,argparse.Namespace(action='cancel',operation=plan['operation']['id'],**self.actor))
        self.assertEqual(sync.read(loop,self.root)['baseline'],before)
        self.assertEqual(sync.status(loop,self.root)['status'],'needs-reconciliation')

    def test_status_expires_and_shows_local_changes(self):
        self.baseline();clock=loop.now()
        with patch.object(loop,'now',return_value=clock+timedelta(minutes=16)):
            self.assertEqual(sync.status(loop,self.root)['status'],'stale')
        body=copy.deepcopy(self.body());body['initiatives'][0]['owner']='new';self.apply(body)
        self.assertEqual(sync.status(loop,self.root)['status'],'local-changed')

    def test_remote_scope_change_requires_new_alignment(self):
        config,_,change=loop.select(self.root,'CHG-001')
        product.align(loop,self.root,argparse.Namespace(change='CHG-001',expect_digest=product.read(loop,self.root)['digest'],
            expect_contract=loop.contract_hash(self.root,config,change),**self.actor))
        self.assertTrue(loop.gate(self.root,'CHG-001','ready')['passed'])
        remote=self.baseline();remote['objectives'][0]['target']='Three participants'
        plan=self.plan(self.snapshot(remote));self.confirm(plan)
        self.assertFalse(loop.gate(self.root,'CHG-001','ready')['passed'])

    def test_failed_read_invalidates_current_label_but_preserves_baseline(self):
        base=self.baseline()
        with self.assertRaises(loop.LoopError): self.plan(self.snapshot(status='unavailable'))
        self.assertEqual(sync.status(loop,self.root)['status'],'read-failed')
        self.assertEqual(sync.read(loop,self.root)['baseline'],base)

    def test_independent_valid_edits_that_form_a_cycle_cannot_be_prepared(self):
        body=copy.deepcopy(self.body())
        other=copy.deepcopy(body['initiatives'][0]);other['id']='INI-002';body['initiatives'].append(other)
        self.apply(body);base=self.baseline()
        local=copy.deepcopy(base);remote=copy.deepcopy(base)
        local['initiatives'][0]['depends_on']=['INI-002'];self.apply(local)
        remote['initiatives'][1]['depends_on']=['INI-001']
        with self.assertRaisesRegex(loop.LoopError,'cycle'): self.plan(self.snapshot(remote))
        self.assertIsNone(sync.read(loop,self.root)['active'])
        self.assertEqual(sync.status(loop,self.root)['status'],'needs-reconciliation')

    def test_status_cli_is_read_only_and_roadmap_exposes_sync(self):
        before={p.relative_to(self.root):p.read_bytes() for p in (self.root/'.spec-loop').rglob('*') if p.is_file()}
        result=subprocess.run(['python3',str(PLUGIN/'scripts/spec_loop.py'),'--root',str(self.root),'github','status'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        after={p.relative_to(self.root):p.read_bytes() for p in (self.root/'.spec-loop').rglob('*') if p.is_file()}
        self.assertEqual(before,after)
        self.assertEqual(product.refresh(loop,self.root)['sync']['mode'],'agent-mediated-github-file')


if __name__=='__main__': unittest.main()
