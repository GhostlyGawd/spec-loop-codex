#!/usr/bin/env python3
"""Inspect a Spec Loop source package or compare a host's resolved copy. No writes."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

GROUPS = ('.codex-plugin', 'scripts', 'skills', 'schemas', 'templates', 'docs', 'examples')
LIMIT = 8 * 1024 * 1024
TOTAL_LIMIT = 64 * 1024 * 1024
FILE_COUNT = 10000
REQUIRED = ('.codex-plugin/plugin.json', 'scripts/spec_loop.py', 'scripts/product.py',
            'scripts/review_runner.py', 'scripts/install_check.py', 'scripts/package.py',
            'skills/spec-loop/SKILL.md', 'skills/loop-product/SKILL.md',
            'schemas/project.schema.json', 'schemas/change.schema.json', 'docs/HOST_ACCEPTANCE.md')


class Invalid(ValueError):
    pass


def safe(root, relative):
    p = Path(relative)
    if not relative or p.is_absolute() or '..' in p.parts:
        raise Invalid('Unsafe package path: ' + str(relative))
    result = root / p
    for part in [result, *result.parents]:
        if part.is_symlink():
            raise Invalid('Symlink path: ' + str(relative))
        if part == root:
            break
    if not result.resolve().is_relative_to(root.resolve()):
        raise Invalid('Package path escapes root')
    return result


def content(path):
    if not path.is_file():
        raise Invalid('Required file is missing: ' + str(path))
    if path.stat().st_size > LIMIT:
        raise Invalid('File exceeds 8 MiB: ' + str(path))
    return path.read_bytes()


def hashed(value):
    return hashlib.sha256(value).hexdigest()


def digest_inventory(files):
    return hashed(json.dumps(files, sort_keys=True, separators=(',', ':')).encode())


def version(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d+\.\d+\.\d+(?:\+codex\.[A-Za-z0-9._-]+)?', value):
        raise Invalid('Unsupported Spec Loop version')
    return value.split('+')[0]


def inspect(root):
    root = root.absolute()
    if any(p.is_symlink() for p in [root, *root.parents]):
        raise Invalid('Plugin root cannot use symlinks')
    manifest = json.loads(content(safe(root, '.codex-plugin/plugin.json')))
    if not isinstance(manifest, dict) or manifest.get('name') != 'spec-loop' or manifest.get('skills') != './skills/':
        raise Invalid('Expected the Spec Loop manifest and ./skills/ entrypoint')
    base_version = version(manifest.get('version'))
    for relative in REQUIRED:
        content(safe(root, relative))
    tree = ast.parse(content(safe(root, 'scripts/spec_loop.py')))
    versions = [node.value.value for node in tree.body if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'VERSION' for t in node.targets)
                and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)]
    if versions != [base_version]:
        raise Invalid('Manifest and engine versions differ')
    files, size = {}, 0
    for group in GROUPS:
        folder = safe(root, group)
        if not folder.is_dir():
            raise Invalid('Required resource directory is missing: ' + group)
        for p in folder.rglob('*'):
            relative = p.relative_to(root).as_posix()
            safe(root, relative)
            if '__pycache__' in p.parts or p.suffix == '.pyc':
                continue
            if not p.is_file():
                if not p.is_dir():
                    raise Invalid('Unsupported package entry: ' + relative)
                continue
            data = content(p)
            size += len(data)
            if size > TOTAL_LIMIT or len(files) >= FILE_COUNT:
                raise Invalid('Package exceeds the 64 MiB or 10000-file budget')
            files[relative] = hashed(data)
            if p.suffix == '.json':
                json.loads(data)
            if p.suffix == '.md':
                for target in re.findall(r'\]\(([^)]+)\)', data.decode()):
                    if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', target) or target.startswith('#'):
                        continue
                    candidate = p.parent / target.split('#')[0]
                    if not candidate.resolve().is_relative_to(root.resolve()):
                        raise Invalid('Bundled link leaves plugin: ' + relative)
                    linked = candidate.resolve().relative_to(root.resolve()).as_posix()
                    # Check unresolved components as well; resolving alone can hide a symlink.
                    current = candidate
                    while current != root and current != current.parent:
                        if current.is_symlink():
                            raise Invalid('Bundled link uses symlink: ' + relative)
                        current = current.parent
                    if not safe(root, linked).exists():
                        raise Invalid('Missing bundled link in ' + relative + ': ' + target)
    normalized = dict(manifest, version=base_version)
    files['.codex-plugin/plugin.json'] = digest_inventory(normalized)
    skills = []
    for folder in sorted((root/'skills').iterdir()):
        if not folder.is_dir() or folder.name == '__pycache__':
            continue
        text = content(safe(root, f'skills/{folder.name}/SKILL.md')).decode()
        front = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)', text, re.S)
        if not front:
            raise Invalid('Missing skill frontmatter: ' + folder.name)
        fields = dict(re.findall(r'^(name|description):\s*(.+)$', front[1], re.M))
        if fields.get('name', '').strip('"\'') != folder.name or not fields.get('description', '').strip():
            raise Invalid('Invalid skill identity: ' + folder.name)
        skills.append(folder.name)
    return {'name': 'spec-loop', 'version': manifest['version'], 'engine_version': base_version,
            'skills': skills, 'payload_digest': digest_inventory(files), 'files': files}


def verify_package(root):
    p = safe(root, 'package-manifest.json')
    metadata = json.loads(content(p))
    if not isinstance(metadata, dict) or metadata.get('name') != 'spec-loop' or not isinstance(metadata.get('files'), dict):
        raise Invalid('Invalid package manifest')
    version(metadata.get('version'))
    if not re.fullmatch(r'[0-9a-f]{40}', str(metadata.get('source_commit', ''))):
        raise Invalid('Invalid package source commit')
    expected = metadata['files']
    if not expected or len(expected) > FILE_COUNT or 'source-history.bundle' not in expected:
        raise Invalid('Package inventory is incomplete or too large')
    total = 0
    for relative, digest in expected.items():
        if not isinstance(relative, str) or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise Invalid('Invalid package hash entry')
        data = content(safe(root, relative)); total += len(data)
        if total > TOTAL_LIMIT:
            raise Invalid('Package exceeds 64 MiB')
        if hashed(data) != digest:
            raise Invalid('Package hash mismatch: ' + relative)
    actual = set()
    for path in root.rglob('*'):
        relative = path.relative_to(root).as_posix()
        safe(root, relative)
        if '__pycache__' in path.parts or path.suffix == '.pyc':
            continue
        if path.is_file():
            actual.add(relative)
        if len(actual) > FILE_COUNT + 1:
            raise Invalid('Package inventory is too large')
    if actual != set(expected) | {'package-manifest.json'}:
        raise Invalid('Package inventory differs from its manifest')
    manifest = json.loads(content(safe(root, '.codex-plugin/plugin.json')))
    if metadata['version'] != manifest.get('version'):
        raise Invalid('Package version differs from plugin manifest')
    return {'verified': True, 'source_commit': metadata['source_commit'], 'files': len(expected),
            'trust': 'Unsigned inventory; compare the archive digest with a trusted release.'}


def check(root, installed=None, package=False, expected_digest=None):
    source = inspect(root)
    if expected_digest and source['payload_digest'] != expected_digest:
        raise Invalid('Source payload differs from the expected digest')
    result = {'passed': True, 'source': {k:v for k,v in source.items() if k != 'files'},
              'host_loading': 'unverified', 'codex_cli_available': shutil.which('codex') is not None,
              'mutations': False, 'installed_copy': {'status': 'not-supplied'}}
    if package:
        result['package'] = verify_package(root)
    if installed:
        other = inspect(installed)
        a, b = source['files'], other['files']
        missing, extra = sorted(a.keys()-b.keys()), sorted(b.keys()-a.keys())
        changed = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
        same = not (missing or extra or changed)
        result['installed_copy'] = {'status': 'matches-source' if same else 'differs',
                                    'missing': missing, 'extra': extra, 'changed': changed,
                                    'version': other['version']}
        result['passed'] = same
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--installed-root', type=Path)
    parser.add_argument('--package', action='store_true', help='Validate an extracted source archive inventory')
    parser.add_argument('--expected-digest')
    args = parser.parse_args()
    try:
        result = check(args.root, args.installed_root, args.package, args.expected_digest)
        print(json.dumps(result, indent=2))
        return 0 if result['passed'] else 1
    except (Invalid, OSError, ValueError, SyntaxError, UnicodeError, RecursionError, TypeError) as exc:
        print(json.dumps({'passed': False, 'host_loading': 'unverified', 'mutations': False, 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
