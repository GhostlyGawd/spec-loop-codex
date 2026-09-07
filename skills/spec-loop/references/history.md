# Release history and later outcomes

Use this guide to preserve the evidence for an observed release, inspect an earlier release, or record product results after the current code changes. Use the shared protocol and tool guide first.

Keep current-tree evidence and historical evidence distinct. `gate` checks the current files. `release-inspect` checks the frozen record at its seal time. An earlier passing release does not prove the current candidate is ready.

## Seal an observed release

Create a reviewed receipt file under .spec-loop/artifacts. It must identify the actual local or remote action, target, result, and source/artifact identity. For a local demonstration, state that no deployment occurred. A note cannot authenticate a remote service or supply absent user authority.

Run the current release gate. If it passes and the actual released artifact and receipt are available, use:

```bash
python3 /path/to/spec-loop/scripts/spec_loop.py --root /path/to/project release-seal CHG-001 --release REL-001 --target local-demo --artifact app.py --receipt .spec-loop/artifacts/release-receipt.md --authority-ref "Authorized local demonstration only" --observer codex
```

Supply real values for the actual case. The command does not deploy or approve. It captures the change and its dependencies, required evidence, reviewed attachments, source digest, artifact digest, target, observer, and authority reference. Each small attachment is copied into the record, with a 4 MiB per-file limit. The record limit is 24 MiB. Large build artifacts are hashed, not embedded. Never include secrets or raw customer data.

The tool refuses to replace an existing release ID. Keep a correction as a new release record with an explanation. Commit the release record under the project's retention policy. It is locally editable and unsigned; its digest detects ordinary corruption, not a writer who can recalculate all hashes.

## Inspect history

Use `release-inspect REL-001`. The tool validates embedded content and evaluates the frozen evidence at seal time. It does not read current project configuration, source, or original attachments. Later changes and ordinary build-evidence expiry do not rewrite history. Unknown schemas and broken evidence fail visibly.

Report the release ID, recorded target, artifact digest, original engine version, and scope of proof. Do not infer that the same artifact is still deployed or that a stored receipt is independently authenticated.

## Record an outcome

Use `release-observe` only for an actual observation that applies to the frozen main change's manual outcome check. Provide the result, observer, observation file, note, cohort, and measurement window:

```bash
python3 /path/to/spec-loop/scripts/spec_loop.py --root /path/to/project release-observe REL-001 --check CHK-004 --result pass --observer "Actual observer" --artifact .spec-loop/artifacts/outcome.md --note "Actual observed result and limits" --cohort "Observed participant group" --window-start 2026-09-07T10:00:00+00:00 --window-end 2026-09-07T11:00:00+00:00
```

The command above is a format example. Replace every observation value with evidence from the real case. Do not execute it to invent a user trial. A baseline window may start before sealing, but the observer must establish that the result concerns the named release. The tool validates chronology, not causality, sample quality, or identity.

Run `release-learn REL-001`. Every frozen outcome check needs its own result. A missing check, a later failure, an altered record, or an observation copied from another release prevents a pass. Automated historical outcome collection is not supported yet. The current-tree learn gate remains available for a stable current candidate.

Outcome records are historical facts and do not expire automatically. New windows use new observations; the newest result per check controls the local learning report. The report is not a live product-health signal.
