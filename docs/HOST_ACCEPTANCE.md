# Host acceptance and local evaluation

Status: v0.6 installation diagnostics and native source pilot are implemented; actual Codex installation remains untested. The current environment has no Codex CLI binary. That does not determine which plugins a Work host can load.

## Installation diagnostic

Read [the installation guide](../skills/spec-loop/references/install.md). Run `python3 scripts/install_check.py --root /path/to/spec-loop` from any working directory. For an extracted source archive, add `--package`. Supply `--installed-root /resolved/host/copy` only when that path is actually known. File equality never completes the host-loading gate.

The native product records in this repository separate CHG-006 (portable diagnostics) from CHG-HOST (actual installation and builder outcomes). Keep the latter open until the host cases below are observed. [The pilot record](PILOT.md) states what was exercised and what remains missing.

## Read-only preflight

In a project Git root, run:

```bash
python3 /path/to/spec-loop/scripts/spec_loop.py --root /path/to/project doctor
```

The output checks the Python version, Git, the correct repository root, supported source paths, and existing project records. It reports CLI presence separately. It runs no project checks, installs nothing, and writes no files. A new project can pass preflight before init. A wrong root or malformed initialized project fails.

## Local workflow evaluation

Copy examples/reading-list, including .spec-loop, to a disposable directory. Initialize Git in that copy. Ask Codex to read the extracted main skill. Run doctor, ready, the inspected acceptance check, and verify. Run and record the real local release observations before sealing a local demonstration. Leave human outcome checks open when no person participated.

## Actual host installation gate

Use the chosen Codex host's current supported plugin installation process. The source package supplies .codex-plugin/plugin.json and its skills. Register a personal or team marketplace only when that destination is part of the authorized task. Do not change a live marketplace as part of local evaluation.

After actual installation, record the host, version, plugin source/version, installation receipt or visible state, and these observed results:

| Case | Acceptance |
| --- | --- |
| Discovery | Spec Loop and a focused lifecycle skill appear through the host's supported skill interface |
| Main skill | A simple request loads the router and relevant guide |
| Bundled paths | Scripts, schemas, and templates resolve from the installed plugin location |
| Local checks | The isolated example passes doctor, ready, and verify after its real check runs |
| Product workflow | Product init/apply/align, roadmap show, and context resolve from installed resources; factual refresh preserves intent |
| Historical use | The same host can seal and inspect an authorized local demonstration |
| Access boundary | Missing service access remains explicit; no deployment or permission is invented |
| Version update | The new package is loaded and old current-tree evidence is reported stale where expected |

All actual host cases remain open in this delivery. Do not substitute a schema check for an installation test.

## Package and upgrade

After committing the intended source, run:

```bash
python3 scripts/package.py --root . --output /outside-the-project/spec-loop-0.6.0.tar.gz
```

The command refuses tracked changes and existing output. It packages the commit, excludes untracked temporary files, preserves Git history in a bundle, and checks every archive entry. Fixed archive metadata makes repeated packaging of the same commit byte-identical in the tested environment. Different Git or compression versions are not covered by that test.

Project, change, and ordinary evidence schema version 1 remains supported. Frozen release and outcome records each use their own version 1 schema. Upgrading the engine invalidates current-tree evidence through its version digest. Re-run those checks; do not rewrite old evidence hashes. Historical releases use their recorded engine identity and frozen inputs.

## Product upgrade and recovery

v0.3 adds product intent/state schema version 1 and optional `product_scope`/`product_review` change fields. Existing v0.2 projects continue to load. Product initialization is explicit and non-destructive. A regression fixture checks a real synthetic v0.2 release envelope with the v0.3 reader.

Product backup/restore preserves intent/history only and restores as a new revision. It is not a full repository or deployment rollback. Unknown schema versions are rejected. Corrupt state requires recovery from a reviewed project backup; there is no automatic schema migration or repair claim.

## GitHub adapter acceptance

A live file sequence was exercised through GitHub MCP in GhostlyGawd/spec-loop-codex on codex/github-product-sync. It established file create/read-back, a no-write comparison, SHA-bound update, and preservation of independent local/remote planning fields. Those v0.4 checks did not test host skill installation or other adapters. v0.5 later passed remote CI and one actual scheduled review; host loading, Issues/Projects and organization-wide permission differences remain untested.

The installed skill must resolve the GitHub guide and snapshot schema, discover the actual connector, and preserve missing access as a failure. GitHub branch names with slashes can require the branch collection route in this connector. Unknown local sync state is rejected. Product and prior release formats remain supported.
