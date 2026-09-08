"""Work resource portability and publication boundaries."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_spec_loop import PLUGIN
import install_check
import work_bundle


class WorkBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.root = self.parent / 'source'
        self.root.mkdir()
        for group in install_check.GROUPS:
            shutil.copytree(PLUGIN / group, self.root / group,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        shutil.copy(PLUGIN / 'README.md', self.root / 'README.md')
        (self.root / '.spec-loop').mkdir()
        (self.root / '.spec-loop/state.json').write_text('{"private_project":true}')
        self.git('init', '-q')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.commit()
        self.output = self.parent / 'bundle'

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'Fixture')

    def test_bundle_is_self_contained_and_excludes_live_and_untracked_data(self):
        (self.root / 'scripts/private-untracked.txt').write_text('do not distribute')
        data = work_bundle.build(self.root, self.output)
        self.assertFalse((self.output / '.spec-loop').exists())
        self.assertFalse((self.output / 'scripts/private-untracked.txt').exists())
        self.assertEqual(data['host_loading'], 'unverified')
        self.assertEqual(data['installation'], 'not-performed')
        self.assertFalse(list(self.output.rglob('SKILL.md')))
        self.assertTrue((self.output / 'skills/spec-loop/GUIDE.md').is_file())
        self.assertTrue(install_check.check(self.output, expected_digest=data['payload_digest'], work_bundle=True)['passed'])
        with self.assertRaisesRegex(ValueError, 'missing'):
            install_check.check(self.output)
        with self.assertRaisesRegex(ValueError, 'not a source archive'):
            install_check.check(self.output, package=True, work_bundle=True)
        for name, digest in data['files'].items():
            self.assertEqual(install_check.hashed((self.output / name).read_bytes()), digest)
        # Resource resolution must work outside the plugin folder, without a Codex executable.
        result = subprocess.run(['python3', str(self.output / 'scripts/spec_loop.py'), '--version'],
                                cwd=self.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), data['version'])

    def test_overwrite_dirty_source_and_source_child_are_refused(self):
        self.output.mkdir()
        sentinel = self.output / 'keep.txt'
        sentinel.write_text('keep')
        with self.assertRaisesRegex(ValueError, 'new output'): work_bundle.build(self.root, self.output)
        self.assertEqual(sentinel.read_text(), 'keep')
        with self.assertRaisesRegex(ValueError, 'outside'): work_bundle.build(self.root, self.root / 'bundle')
        (self.root / 'README.md').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'Commit tracked'): work_bundle.build(self.root, self.parent / 'new')

    def test_symlink_and_budget_fail_without_output(self):
        (self.root / 'scripts/link').symlink_to('spec_loop.py')
        self.commit()
        with self.assertRaisesRegex(ValueError, 'symlinks'): work_bundle.build(self.root, self.output)
        self.assertFalse(self.output.exists())
        (self.root / 'scripts/link').unlink()
        self.commit()
        with patch.object(install_check, 'TOTAL_LIMIT', 100):
            with self.assertRaisesRegex(ValueError, 'limits'): work_bundle.build(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_invalid_resources_remove_only_created_output(self):
        (self.root / 'scripts/product.py').unlink()
        self.commit()
        with self.assertRaisesRegex(ValueError, 'missing'): work_bundle.build(self.root, self.output)
        self.assertFalse(self.output.exists())
        self.assertTrue(self.root.exists())

    def test_stale_bundle_is_detected_and_repeat_export_is_identical(self):
        first = work_bundle.build(self.root, self.output)
        second = work_bundle.build(self.root, self.parent / 'second')
        self.assertEqual(first, second)
        with (self.output / 'scripts/product.py').open('a') as f:
            f.write('\n# changed after export\n')
        with self.assertRaisesRegex(ValueError, 'expected digest'):
            install_check.check(self.output, expected_digest=first['payload_digest'], work_bundle=True)


if __name__ == '__main__':
    unittest.main()
