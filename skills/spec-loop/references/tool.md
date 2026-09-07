# Local tool contract

Version 0.2 adds read-only `doctor`, frozen releases, and observations linked to a release. Read [release history](history.md) for `release-seal`, `release-inspect`, `release-observe`, and `release-learn`. Use [host acceptance](../../../docs/HOST_ACCEPTANCE.md) for environment checks, actual installation validation, packaging, and upgrade behavior.

Resolve the plugin root as two directories above the spec-loop skill directory. The executable is scripts/spec_loop.py under that root. Use Python 3.10+ and Git. Call --help for the exact command interface.

The project owns .spec-loop/project.json, state.json, changes/CHG-*.json, artifacts/, and evidence/. Do not place source code under .spec-loop; that directory is excluded from the source snapshot. Keep authoritative docs in declared artifacts and operational observations in .spec-loop/artifacts.

Initialize once:
```bash
python3 /path/to/spec-loop/scripts/spec_loop.py --root /path/to/project init --name "My product" --profile product
python3 /path/to/spec-loop/scripts/spec_loop.py --root /path/to/project new CHG-001 --title "First useful change"
```

New drafts are incomplete and fail readiness. Fill them from actual context. Read [the change schema](../../../schemas/change.schema.json) and [the example contract](../../../examples/reading-list/.spec-loop/changes/CHG-001.json). Read the source schema if a record fails validation. Arrays with no items allow a draft; the ready gate enforces completeness.

Every requirement has source_ids and criteria. Each criterion has an AC ID and an observable statement. Checks have covers links; an acceptance check must cover at least one criterion. Other checks can have an empty covers list. Every requirement has a task. Do not duplicate reverse coverage lists.

Each check has kind, purpose, covers, argv, procedure, and timeout_seconds. Automated checks need a non-empty argv array. Manual checks need a procedure and an empty argv. Time limits range from 1 to 600 seconds. All checks selected by a gate are required.

A product profile needs design and architecture artifact files. A high risk change uses the critical profile and also needs a security artifact and a manual security check. Before collecting release evidence, create the release and operations artifacts and define release and operations checks. Late edits to these inputs stale earlier evidence.

Run an inspected check:
```bash
python3 /path/to/spec-loop/scripts/spec_loop.py --root /path/to/project run CHG-001 --check CHK-001 --observer codex
python3 /path/to/spec-loop/scripts/spec_loop.py --root /path/to/project gate CHG-001 --stage verify
```

Record a real manual observation with record, --result, --note, --artifact, and --observer. The observation file must exist inside the project. Do not fabricate research or sign-offs. Automated evidence cannot be replaced by record.

Evidence is bound to the contract, declared artifacts, dependency contracts, project policy, engine version, and current source snapshot. Tracked and non-ignored untracked files are included. Relevant ignored config and external environment state need explicit reviewed records. Symlinks and submodules are not supported in source snapshots.

Only phase and task progress are excluded from the contract digest. A reported phase never proves completion. Latest failures, stale hashes, changed observation files, expiry, and invalid timestamps block the selected gate. Output is JSON; exit 0 is success, 1 is a failed gate or check, and 2 is invalid input or execution error.

The tool does not sandbox command programs. It does not authenticate observers or sign evidence. It retains output hashes, not raw test output. Diagnose a failed command through the host's normal execution tools and save a reviewed artifact if needed.

Use impact for transitive declared dependents, then inspect undeclared code, API, data, and service impact. Use context to load a bounded packet. If over budget, split the change or raise an explicit budget; no requirements are silently truncated.

Use checkpoint with the revision from state.json. A conflict means reread and reconcile. Do not remove an active .lock. The last 50 checkpoint events are a convenience history, not an immutable audit ledger.

The schemas use type, properties, required, additionalProperties, enum, minLength, pattern, minItems, uniqueItems, items, minimum, and maximum. The bundled validator implements this subset and treats blank strings as empty where minLength applies. It is not a general JSON Schema engine.
