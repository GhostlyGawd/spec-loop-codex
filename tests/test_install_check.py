"""Installation resource checks on disposable copies; no host installation claim."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_spec_loop import PLUGIN
import install_check as install


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'source'
        self.root.mkdir()
        for group in install.GROUPS:
            shutil.copytree(PLUGIN/group, self.root/group, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for name in ('README.md', 'LICENSE'):
            if (PLUGIN/name).exists(): shutil.copy(PLUGIN/name, self.root/name)

    def copy(self):
        other = Path(self.temp.name)/'installed'
        shutil.copytree(self.root, other)
        return other

    def manifest(self, root, **values):
        p=root/'.codex-plugin/plugin.json'
        value=json.loads(p.read_text());value.update(values);p.write_text(json.dumps(value))

    def package_manifest(self):
        (self.root/'source-history.bundle').write_bytes(b'Synthetic inventory test; not a real Git bundle')
        files={p.relative_to(self.root).as_posix():install.hashed(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}
        manifest=json.loads((self.root/'.codex-plugin/plugin.json').read_text())
        data={'name':'spec-loop','version':manifest['version'],'source_commit':'1'*40,'files':files}
        (self.root/'package-manifest.json').write_text(json.dumps(data))
        return data

    def test_source_valid_copy_matches_without_claiming_host_loading(self):
        other=self.copy()
        before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result=install.check(self.root,other)
        self.assertTrue(result['passed'])
        self.assertEqual(result['installed_copy']['status'],'matches-source')
        self.assertEqual(result['host_loading'],'unverified')
        self.assertIn('loop-product',result['source']['skills'])
        self.assertEqual(before,{p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_stale_or_extra_installed_resource_is_visible(self):
        other=self.copy()
        (other/'scripts/product.py').write_text('# old copy\n')
        (other/'scripts/extra.py').write_text('# extra\n')
        result=install.check(self.root,other)
        self.assertFalse(result['passed'])
        self.assertIn('scripts/product.py',result['installed_copy']['changed'])
        self.assertIn('scripts/extra.py',result['installed_copy']['extra'])

    def test_codex_cachebuster_and_python_cache_do_not_hide_real_changes(self):
        other=self.copy()
        original=json.loads((other/'.codex-plugin/plugin.json').read_text())['version']
        self.manifest(other,version=original+'+codex.local-20260908')
        (other/'scripts/__pycache__').mkdir(exist_ok=True)
        (other/'scripts/__pycache__/x.pyc').write_bytes(b'cache')
        self.assertTrue(install.check(self.root,other)['passed'])
        self.manifest(other,description='Changed metadata')
        self.assertFalse(install.check(self.root,other)['passed'])

    def test_missing_resource_and_engine_mismatch_fail(self):
        (self.root/'scripts/product.py').unlink()
        with self.assertRaisesRegex(install.Invalid,'missing'): install.check(self.root)
        shutil.copy(PLUGIN/'scripts/product.py',self.root/'scripts/product.py')
        self.manifest(self.root,version='9.0.0')
        with self.assertRaisesRegex(install.Invalid,'versions differ'): install.check(self.root)

    def test_invalid_frontmatter_and_missing_reference_fail(self):
        skill=self.root/'skills/loop-product/SKILL.md'
        original=skill.read_text();skill.write_text(original.replace('name: loop-product','name: wrong'))
        with self.assertRaisesRegex(install.Invalid,'identity'): install.check(self.root)
        skill.write_text(original+'\n[Missing](not-present.md)\n')
        with self.assertRaisesRegex(install.Invalid,'Missing bundled link'): install.check(self.root)

    def test_symlink_and_parent_escape_refused(self):
        p=self.root/'scripts/linked.py';p.symlink_to(self.root/'scripts/spec_loop.py')
        with self.assertRaisesRegex(install.Invalid,'Symlink'): install.check(self.root)
        with self.assertRaisesRegex(install.Invalid,'Unsafe'):install.safe(self.root,'../outside')

    def test_inspection_does_not_execute_target_code(self):
        marker=Path(self.temp.name)/'executed'
        with (self.root/'scripts/spec_loop.py').open('a') as stream:
            stream.write('\nraise RuntimeError("Do not execute inspected source")\n')
        self.assertTrue(install.check(self.root)['passed'])
        self.assertFalse(marker.exists())

    def test_budget_and_expected_digest_fail_closed(self):
        with patch.object(install,'TOTAL_LIMIT',100):
            with self.assertRaisesRegex(install.Invalid,'budget'):install.check(self.root)
        with self.assertRaisesRegex(install.Invalid,'expected digest'):install.check(self.root,expected_digest='0'*64)

    def test_package_hashes_and_inventory(self):
        self.package_manifest()
        self.assertTrue(install.check(self.root,package=True)['package']['verified'])
        (self.root/'scripts/product.py').write_text('# modified\n')
        with self.assertRaisesRegex(install.Invalid,'hash mismatch'):install.check(self.root,package=True)

    def test_package_extra_file_and_malicious_path_fail(self):
        data=self.package_manifest()
        (self.root/'unexpected.txt').write_text('extra')
        with self.assertRaisesRegex(install.Invalid,'inventory differs'):install.check(self.root,package=True)
        (self.root/'unexpected.txt').unlink()
        data['files']['../outside']='0'*64
        (self.root/'package-manifest.json').write_text(json.dumps(data))
        with self.assertRaisesRegex(install.Invalid,'Unsafe'):install.check(self.root,package=True)

    def test_cli_from_another_working_directory(self):
        result=subprocess.run(['python3',str(PLUGIN/'scripts/install_check.py'),'--root',str(self.root)],
                              cwd=self.temp.name,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout)['host_loading'],'unverified')


if __name__ == '__main__':
    unittest.main()
