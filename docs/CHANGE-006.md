# CHG-006 — Installation diagnostics and native product pilot

Status: implementation and local technical cycle complete; actual host and builder gates remain open. 8 September 2026.

The user approved installation validation and a real product pilot after v0.5. The current workspace has no Codex CLI or exposed local-plugin installation action. Complete the portable diagnostics, package and native workflow now; keep actual host loading and human outcomes open until observed. Do not describe file copies as host installations.

| Requirement | Acceptance |
| --- | --- |
| INS-001 | Inspect the source package without executing inspected code or changing files. Validate the manifest, engine version, skill names, required resources and bundled links. |
| INS-002 | Compare an explicitly identified installed copy with reviewed source. Detect missing, changed and extra payload files. Ignore only documented generated Python cache files and the Codex cachebuster suffix. Matching files leave host loading unverified. |
| INS-003 | Reject symlink paths, unsupported versions, malformed inputs and excessive input sizes. Return a useful diagnostic and nonzero exit on failure. |
| INS-004 | Verify extracted package-manifest hashes and inventory, including the Git bundle. Never extract an untrusted archive or install a marketplace from this tool. |
| PIL-001 | Manage this release with native strategy, initiative, contract, design and architecture records. Derive delivery from current evidence in Actions. Do not invent evidence for old planning initiatives. |
| PIL-002 | Exercise the actual local diagnostics release, resume, source-change invalidation, historical release inspection and upgrade recovery. Keep missing host and human outcome checks visible. |
| PIL-003 | Publish a precise host handoff with current official source references and pass criteria. A source-package release is separate from the host-installation milestone. |

Product scope: help the builder distinguish valid source, a matching installed copy, successful host loading and observed product value. The primary path is diagnose source, install through the chosen host, compare the resolved copy, start a new chat, and run a small native project. Errors must name the missing resource or mismatch. No installer, credential handling, default telemetry, scheduler mutation, or unattended sync writer is added in this milestone.

Validation: installation diagnostics tests, all existing tests, native pilot evidence, package extraction in a disposable directory, independent agent use when useful, and live PR Actions. A real builder trial requires the builder; agent observations cannot fill that result.
