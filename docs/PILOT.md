# Native Spec Loop product pilot

Status: local technical cycle passed; host loading and human outcomes remain open. This is internal use of the real Spec Loop source. It is not an independent builder study or host installation.

The user approved v0.6 installation and pilot work on 8 September 2026. The native product state imports prior planning as an initial recorded decision, then records the approved installation sequence. INI-INSTALL links CHG-006; INI-PILOT links CHG-HOST. Earlier GitHub/runner plans are parked without backfilling native implementation evidence. The JSON exchange file reflects that recorded intent, while Actions now reads native state. No pending v0.4 sync operation or live evaluation target is changed.

CHG-006 has requirements, acceptance checks, tasks, design, architecture, release and operations records for the actual installation checker. CHG-HOST has a separate unfinished task and manual acceptance check for host loading. Both have open human outcome checks. This lets source-package work complete without implying an installed product or proven builder value.

Validation procedure: run acceptance against a clean committed checkout, inspect the actual diagnostic output, build and verify a source package, record the actual local operational exercise, then seal a local source-package release. Resume through context; modify source in a disposable copy and verify current evidence becomes stale while frozen release history remains readable. Read a v0.5 native project with the new engine and collect new evidence after review/alignment. Keep the exact results in the native artifacts and release envelope. Failure is useful pilot feedback; do not change evidence to hide it.

Host and human cases remain open until a selected host loads the plugin and a real builder completes the task. The next observer should record host/version, actual loaded path, task result, recovery behavior and friction. Success criteria are correct skill/resource resolution, accurate roadmap status after a source change, and recovery of the next action without reconstructing the project from chat history. No time-saving percentage, adoption metric or demand claim is inferred from local tests.

## Observed local cycle

The clean-checkout pilot completed 19 actual CLI operations. Acceptance, context resume, source-change invalidation, old-engine evidence rejection under v0.6, new-engine evidence collection, extracted package verification, local release sealing and historical inspection all passed. The native roadmap showed INI-INSTALL release-ready with local historical coverage; INI-PILOT stayed unverified. The human outcome check remained missing. Exact checked commit, command output and artifact hashes are retained in `.spec-loop/artifacts/pilot-results.json`, `pilot-cli-log.json` and the local release record. The sealed artifact is the diagnostics module, with a receipt for the separately checked source package; no host or deployment receipt is invented.

The first checkout failed context resume because its initial native state file had not been committed. That file is now included, and CI checks native context from its clean checkout. The successful local cycle followed that fix. Source edits after evaluation invalidate current evidence, so final evidence is recollected against the final source before handoff. Later metadata-only evidence commits do not change the source digest.

The exchange JSON is a snapshot exported with the recorded v0.6 decision. Native product state is authoritative for this pilot; the GitHub runner reads it directly. Future external exchange updates must use the reviewed product-sync workflow. No continuous two-way export is claimed.
