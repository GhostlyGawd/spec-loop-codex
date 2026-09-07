#!/usr/bin/env python3
"""Create a checked source archive from one committed plugin revision."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise ValueError("Git operation failed: " + " ".join(args[:2]))
    return result.stdout


def build(root, output):
    root, output = root.resolve(), output.resolve()
    if Path(git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve() != root:
        raise ValueError("Use the Git root.")
    if output.exists():
        raise ValueError("Output already exists; choose a new filename.")
    commit = git(root, "rev-parse", "HEAD").decode().strip()
    if git(root, "diff", "HEAD", "--name-only"):
        raise ValueError("Commit tracked changes before packaging.")
    entries = []
    for line in git(root, "ls-tree", "-r", "-z", "--full-tree", commit).split(b"\0"):
        if not line:
            continue
        meta, name = line.split(b"\t", 1)
        mode, kind, object_id = meta.decode().split()
        relative = name.decode("utf-8")
        if kind != "blob" or mode not in ("100644", "100755"):
            raise ValueError("Source archives do not support symlinks or submodules.")
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError("Invalid source path.")
        entries.append((relative, int(mode, 8) & 0o777, git(root, "cat-file", "blob", object_id)))
    manifest_bytes = next((data for path, _, data in entries if path == ".codex-plugin/plugin.json"), None)
    if manifest_bytes is None:
        raise ValueError("Plugin manifest is missing from the commit.")
    plugin = json.loads(manifest_bytes)
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", plugin["name"]):
        raise ValueError("Invalid plugin name.")
    reserved = {"package-manifest.json", "source-history.bundle"}
    if any(path in reserved for path, _, _ in entries):
        raise ValueError("Generated package files must not be tracked as source.")
    with tempfile.TemporaryDirectory() as temporary:
        bundle = Path(temporary) / "history.bundle"
        git(root, "bundle", "create", str(bundle), "HEAD")
        git(root, "bundle", "verify", str(bundle))
        history = bundle.read_bytes()
        if git(root, "rev-parse", "HEAD").decode().strip() != commit:
            raise ValueError("Source revision changed during packaging; no archive was written.")
    files = {path: hashlib.sha256(data).hexdigest() for path, _, data in entries}
    files["source-history.bundle"] = hashlib.sha256(history).hexdigest()
    metadata = {"name": plugin["name"], "version": plugin["version"], "source_commit": commit,
                "files": files, "scope": "Committed source only; no working-tree files or credentials."}
    entries.extend([("source-history.bundle", 0o644, history),
                    ("package-manifest.json", 0o644, (json.dumps(metadata, sort_keys=True, indent=2)+"\n").encode())])
    output.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with output.open("xb") as stream:
            created = True
            with gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as compressed:
                with tarfile.open(mode="w|", fileobj=compressed, format=tarfile.USTAR_FORMAT) as archive:
                    for relative, mode, data in sorted(entries):
                        info = tarfile.TarInfo(plugin["name"] + "/" + relative)
                        info.mode, info.size, info.mtime = mode, len(data), 0
                        archive.addfile(info, io.BytesIO(data))
        with tarfile.open(output, "r:gz") as archive:
            if len(archive.getmembers()) != len(entries):
                raise ValueError("Archive inventory mismatch.")
            for relative, _, data in entries:
                member = archive.getmember(plugin["name"] + "/" + relative)
                if not member.isfile() or hashlib.sha256(archive.extractfile(member).read()).hexdigest() != hashlib.sha256(data).hexdigest():
                    raise ValueError("Archive content verification failed.")
    except BaseException:
        if created:
            output.unlink(missing_ok=True)
        raise
    return {"archive": str(output), "source_commit": commit, "source_files": len(files)-1,
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "verified": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.root, args.output), indent=2))
    except (OSError, ValueError, KeyError, tarfile.TarError) as error:
        print(json.dumps({"error": str(error)}))
        raise SystemExit(2)
