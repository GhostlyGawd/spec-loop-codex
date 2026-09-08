#!/usr/bin/env python3
"""Copy committed plugin resources into a self-contained Work skill bundle."""
import argparse
import json
from pathlib import Path
import re
import shutil

import install_check
from package import git


def build(root, output):
    root, output = Path(root).resolve(), Path(output).absolute()
    if any(p.is_symlink() for p in [output, *output.parents]):
        raise ValueError('Output cannot use symlinks.')
    if output.exists() or output.resolve().is_relative_to(root):
        raise ValueError('Use a new output directory outside the source project.')
    if not output.parent.is_dir():
        raise ValueError('Output parent must already exist.')
    if Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()).resolve() != root:
        raise ValueError('Use the source Git root.')
    commit = git(root, 'rev-parse', 'HEAD').decode().strip()
    if git(root, 'diff', 'HEAD', '--name-only'):
        raise ValueError('Commit tracked changes before building a Work bundle.')
    entries, size = {}, 0
    for line in git(root, 'ls-tree', '-r', '-z', '--full-tree', commit).split(b'\0'):
        if not line:
            continue
        meta, raw_name = line.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        name = raw_name.decode('utf-8')
        path = Path(name)
        # Ship plugin resources, not this product's own live state or CI settings.
        if path.parts[0] not in install_check.GROUPS and name not in ('README.md', 'LICENSE'):
            continue
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError('Work bundles do not support symlinks or submodules.')
        install_check.safe(output, name)
        blob_size = int(git(root, 'cat-file', '-s', oid))
        size += blob_size
        if blob_size > install_check.LIMIT or size > install_check.TOTAL_LIMIT or len(entries) >= install_check.FILE_COUNT:
            raise ValueError('Work bundle exceeds resource limits.')
        data = git(root, 'cat-file', 'blob', oid)
        # Personal skill saving accepts one SKILL.md entry. Lifecycle workflows
        # stay readable resources; the original plugin retains its skill entries.
        if path.name == 'SKILL.md' and path.parts[0] == 'skills':
            name = str(path.with_name('GUIDE.md'))
        if path.suffix == '.md':
            text = data.decode('utf-8')
            text = re.sub(r'(\]\([^\s)]*)SKILL\.md(?=[#)])', r'\1GUIDE.md', text)
            data = text.encode('utf-8')
        entries[name] = data
    # Reserve the destination exclusively. Never replace an existing skill bundle.
    output.mkdir()
    try:
        for name, data in entries.items():
            target = install_check.safe(output, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        source = install_check.inspect(output, work_bundle=True)
        if git(root, 'rev-parse', 'HEAD').decode().strip() != commit or git(root, 'diff', 'HEAD', '--name-only'):
            raise ValueError('Source changed during bundling.')
        result = {'name': 'spec-loop', 'version': source['engine_version'],
                  'source_commit': commit,
                  'source_tree': git(root, 'rev-parse', commit + '^{tree}').decode().strip(),
                  'payload_digest': source['payload_digest'],
                  'files': {k: install_check.hashed(v) for k, v in sorted(entries.items())},
                  'scope': 'Committed plugin resources. Excludes root project state, CI and untracked files.',
                  'layout': 'work-guides-v1',
                  'host_loading': 'unverified', 'installation': 'not-performed'}
        (output / 'work-bundle.json').write_text(json.dumps(result, indent=2) + '\n')
        return result
    except BaseException:
        shutil.rmtree(output)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build(args.root, args.output)
        print(json.dumps({k: v for k, v in result.items() if k != 'files'}, indent=2))
    except (OSError, ValueError, SyntaxError, TypeError) as error:
        print(json.dumps({'error': str(error), 'installation': 'not-performed'}))
        raise SystemExit(2)
