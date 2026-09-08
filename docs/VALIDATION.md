# v0.6 validation — 8 September 2026

All 116 local tests pass (105 prior tests and 11 installation cases). Plugin and all 11 skills pass their validators. The source diagnostic passes and identifies host_loading as unverified. An independent offline agent found the changed product.py in a purported resolved copy and did not claim an installation. See [the exercise](evaluation/installation-exercise.md).

The native product pilot completed 19 CLI operations on actual plugin source. CHG-006 covers local diagnostics; CHG-HOST remains open for actual host loading and builder observations. Local acceptance, context resume, source invalidation, v0.5-to-v0.6 evidence recovery, archive extraction checks, local release sealing and historical inspection passed. The host and human gates correctly remained open. Native artifacts retain exact source identities and results. Live PR CI results are reported on the PR after execution. No Codex CLI or local-plugin install action is exposed in this workspace. A copied directory or direct skill read does not substitute for loading the plugin in a host.

A clean-checkout test exposed an omitted initial native resume-state file. It is now committed and CI explicitly runs the native context command. The source checker also passes from outside the plugin directory.

Prior release validation follows.

# v0.5 validation — 7 September 2026

The bounded review worker is implemented on a review branch. All 105 local tests, all 11 skills, the plugin manifest and local Markdown links passed. Independent offline use passed 19 CLI invocations. Actual push and PR Actions runs passed both review and regression jobs. No default-branch schedule or actual Codex installation is claimed.

The worker reads native gates or exchange planning data, checks optional supplied signals, and writes dated receipts outside the source project. Tests cover unchanged intent, unknown exchange delivery, expiry after missed runs, input conflicts, interrupted publication, failed attempts, disclosure, budgets and CLI status. Fixtures contain no actual user telemetry. Read [CHG-005](CHANGE-005.md) and [the runner guide](../skills/spec-loop/references/review-runner.md) for acceptance and operating boundaries.

Live evidence: [GitHub run record](evidence/v05-live-github.json), [test log](evidence/v05-tool-tests.txt), and [independent exercise](evaluation/background-review-exercise.md). The first run created and uploaded a report artifact. Its signed download returned HTTP 403 when this environment tried to materialize it, so artifact bytes were not inspected here. The added receipt-read step passed in push run 34167714700 and PR run 34167716926 at head 8b0e8e3263bd72cb81a6cc6d72287d1d06f905eb. The job reported current-at-read for the generated receipt against that exact checkout. This validates JSON integrity, age and input binding inside the runtime; it does not replace a local inspection of the downloaded ZIP.

The independent exercise found that the Markdown view hid concrete gate blockers. The report now exposes up to five distinct blockers per change, with remaining detail in JSON. A native-mode regression assertion checks the alignment blocker. Final local tests include this change and an ignored-artifact byte-budget check. These refinements were not independently re-exercised. A final regression verifies that the report budget measures the actual formatted output bytes; this brought the local suite to 105 tests. Live runs recorded below preceded that final budget refinement and ran 104 tests. The PR checks identify the tested final head.

Limits: no default-branch schedule observation, sustained pilot, independent missing-run notification service, real telemetry collector, unattended bidirectional sync, marketplace installation or authenticated receipts. CI and push/PR worker execution are now tested. Scheduled delivery still needs observation after merge.

Prior release validation follows.

# Validation record

## Version 0.4.0 — 7 September 2026

**86 tests pass**: the prior 67 tests and 19 GitHub sync tests. The supplied plugin validator and all 11 skill validators pass. This release also has actual GitHub MCP file-operation evidence. It has not been installed through an actual Codex host, and no remote CI job or background runner was tested.

| Contract | Observed result |
| --- | --- |
| GH-001 Target | Repository ID/name, branch, JSON path, visibility, and no-target-overwrite rules are checked. |
| GH-002 Snapshot | Wrong targets, bad blob SHA, unknown branch, stale/future times, and unavailable reads are rejected. Failed reads remove the current label without deleting the common baseline. |
| GH-003 Compare | Independent fields/additions merge. Overlapping edits, delete/edit races, first-contact differences, and remote deletion conflict. A merged dependency cycle is rejected before an operation is prepared. |
| GH-004 Outbox | Create/update/no-write requests are distinct. Updates carry the observed blob SHA. Only one pending operation is allowed. |
| GH-005 Completion | Mismatched read-back fails. Newer local decisions survive remote success. Interrupted completion and repeated confirmation do not duplicate the product decision. |
| GH-006 Recovery | Pending/conflict/read-failed/local-changed/stale states are tested; cancel preserves the baseline and does not claim a remote undo. |
| GH-007 Disclosure | Public candidates require review and reject internal/restricted opportunities. |
| GH-008 Live integration | Actual selected-repository create/read-back, no-op, and independent local/remote field merge/update/read-back succeeded on codex/github-product-sync. |

Raw results: [86 tests](evidence/v04-tool-tests.txt), [plugin validator](evidence/v04-plugin-validation.txt), [skill validators](evidence/v04-skill-validation.txt), and [live GitHub receipts](evidence/v04-live-github.json).

The source baseline was uploaded to GhostlyGawd/spec-loop-codex through GitHub MCP. Its GitHub tree SHA exactly matched the reviewed v0.3 local source tree. The review branch then received the public product file. A repeat comparison emitted no write. A remote edit to strategy.review_trigger and an independent local edit to the existing initiative priority reason were preserved in the merged result. A fresh read verified the merged blob. This was a real connector operation; it was not a deployment or real-user study.

An [independent offline agent exercise](evaluation/github-sync-exercise.md) used a clearly synthetic snapshot, prepared the merge, retained the local horizon and remote owner, and left it pending for actual service reads and confirmation. It made no external calls and did not change product intent. The later failed-read freshness correction and merged-cycle case were validated by the final tests, not a repeated agent exercise or live failure injection.

Current limits: one configured JSON product file through an active agent; no GitHub Issues/Projects adapter, webhook, scheduler, independent service identity, or signed local receipt. File SHA checks do not provide a whole-branch transaction. Local snapshots and authority references remain editable claims. Cross-platform behavior, permission variations, rate-limit failures on the actual service, and long-running builder use remain open.


## Version 0.3.0 — 7 September 2026

The complete regression suite passes **67 tests**: 47 existing tests and 20 product workflow tests. The supplied plugin validator passes and all **11 skills** pass their validator. Tests ran on Linux with Python 3.12.13 and Git 2.51.1. The local Codex CLI is still absent; actual plugin loading remains untested.

| Contract | Observed validation |
| --- | --- |
| PM-001 Product intent | Strict shape, duplicate IDs, unknown links, cycles, date types, estimate ranges, shared work capacity, and initiative risk floors are tested. |
| PM-002 Decisions | Stale writers and stale alignment tokens cannot replace newer intent/contracts. Actual previous/new values are retained and replay-checked. Invalid or altered state fails closed. |
| PM-003 Roadmap | Current candidate gates, missing change links, dependency blockers, partial historical coverage, and release-specific failed/missing outcomes are tested. Refresh leaves priority unchanged. |
| PM-004 Refresh | The actual CLI refreshes after evidence writes. Same-input content is stable; expiry is reevaluated as time passes. A simulated input race preserves the prior view and reports it as stale or unavailable. |
| PM-005 Alignment | Goal/scope changes block readiness; reviewed alignment invalidates old evidence. Priority-only edits preserve valid evidence. A retained synthetic v0.2 release fixture passes the v0.3 reader. |
| PM-006 Recovery | Inventory is read-only with unverified intent. Backup restores as a new revision without removing intervening decisions. Context resume carries linked goals and respects the output budget. |
| PM-007 Agent use | The isolated product review recomputed facts, found the missing current implementation, distinguished synthetic outcome failure from real-user evidence, and left product decisions unchanged. |

Evidence: [67 tests](evidence/v03-tool-tests.txt), [plugin validator](evidence/v03-plugin-validation.txt), [11 skill validators](evidence/v03-skill-validation.txt), and [independent product review](evaluation/product-roadmap-exercise.md). The agent exercise was performed before the final decision-history value/replay and product-doctor hardening; those additions were checked by the final regression suite, not a second independent review.

The author also ran the [complete CLI workflow](evidence/v03-workflow.json) in a separate disposable project: product init/apply/align, readiness, actual acceptance execution, observed duplicate/invalid/retry/empty-process behavior, local release sealing, roadmap display, product backup/restore, and context resume. Current local release readiness passed. The historical learn check correctly failed because no real person was observed. No remote deployment or account action occurred.

Product state and authority references remain editable local records. The tool does not prove semantic review quality, measurement quality, authentication, or causality. Product records have an 8 MiB limit. Large-repository performance, full schema migrations, external backlog import, remote sync, continuous jobs, actual host installation, and builder pilots remain open. Inventory is a basic read-only local inventory; backup/restore covers product intent and decisions, not the full repository or service.


## Version 0.2.0 — 7 September 2026

The full local suite passes **47 tests**: the original 32 tests and 15 release, outcome, preflight, and packaging tests. The supplied plugin validator passes and all ten skills pass their supplied validator. These checks use Linux, Python 3.12.13, and Git 2.51.1; they do not establish actual Codex host installation or product value.

| Contract | Validation and result |
| --- | --- |
| REQ-HISTORY | Pass: stale current evidence cannot be sealed, release IDs cannot be overwritten, dependency contracts and their evidence are frozen together, and historical inspection survives later source/config changes and removal of original attachments. |
| REQ-INTEGRITY | Pass: malformed envelopes, altered hashes and embedded bytes are rejected; validity is evaluated at seal time. Local hashes remain unsigned and editable. |
| REQ-OUTCOME | Pass: outcomes bind to one release and frozen check; cross-release evidence, missing observations, and later failures cannot pass. Historical observations survive current source edits and loss of the original attachment. Automated historical outcome collection is unsupported. |
| REQ-PREFLIGHT | Pass: valid and invalid project checks behave as specified without writes or application execution. CLI dispatch loads the new module. Codex CLI absence is reported separately from project validity. |
| REQ-PACKAGE | Pass: same-commit archives match in the tested environment, untracked files are excluded, dirty tracked source is refused, and archive entries are verified. Cross-version Git/compression determinism is untested. |

Raw results: [47 tool tests](evidence/v02-tool-tests.txt), [plugin validation](evidence/v02-plugin-validation.txt), and [skill validation](evidence/v02-skill-validation.txt).

An independent agent used loop-verify on an isolated synthetic release whose source was subsequently replaced with an unfinished candidate. It correctly reported valid frozen historical evidence, stale current verification/release evidence, and a missing real-user outcome. It did not run application code, modify source, create observations, or deploy. The [full review](evaluation/historical-release-exercise.md) records the actual commands and limitations. This single exercise demonstrates the distinction in this fixture, not general reliability across products.

Release records embed small reviewed attachments and identify the source and build artifact by hashes; they do not archive the historical implementation or build binary. Observer identity, authority references, receipt authenticity, and actual deployment require external verification. Outcome records are historical observations and do not establish current service health. [Host acceptance](HOST_ACCEPTANCE.md) remains an explicit uncompleted procedure. No live integrations, actual user pilot, or comparative benchmark was performed.


## Version 0.1.0 historical record

Date: 6 September 2026. Version: 0.1.0. Environment: Linux, Python 3.12.13, Git 2.51.1.

This record separates mechanical checks, agent exercises, and validation that still needs a real host or users. All product examples are synthetic. No service was deployed, no account was changed, and no real user study was conducted.

## Design checks

The lifecycle review covered orientation, discovery, commercial scope, product and visual design, functional rules, architecture, data, integrations, security, privacy, AI features, planning, build, verification, release, operation, learning, scaling, and retirement.

Each stage has an input, output, validation method, and next decision in SYSTEM_SPEC.md. The record model links user evidence to requirements, criteria, tasks, checks, releases, and outcomes. System requirements SYS-001 through SYS-020 define verification methods and open evaluation work.

The design distinguishes user intent from existing code, assumptions from observations, local hashes from signed provenance, gate results from authority, code correctness from product value, and a proposed schedule from an actual scheduled task.

## Mechanical checks

| Check | Actual result | What it establishes |
| --- | --- | --- |
| Supplied Codex plugin validator | Pass | Current manifest follows the supplied ingestion contract |
| Supplied skill validator | All 10 skills pass | Required frontmatter, names, and scaffold completion |
| Local tool behavior suite | 32 tests pass | Selected state, contract, dependency, and evidence invariants |
| Example product unit suite | 3 test methods pass, with multiple invalid-input cases | The example meets its enumerated local behavior checks |
| Original malformed-host and malformed-port commands after repair | Both reject with exit code 1 | The independent review's two reproduced defects are fixed |

The tool suite covers missing criterion checks, unknown and duplicate IDs, task and change cycles, risk floors, high impact open assumptions, stale source/spec/artifact/policy/dependency evidence, later failures, expiry, future timestamps, manual evidence integrity, release and learning separation, source changes during a check, timeouts, nonzero commands, conflicts, active locks, context size, unrelated drafts, path escape, symlinks, no overwrite, unsupported schema versions, malformed evidence, shell argument handling, and raw output retention.

The checkpoint check also confirms that a later contract change marks the previous handoff stale. A source-only stale check would have missed an intent change stored under .spec-loop; the implementation was corrected to bind the checkpoint to both source and contract.

## Independent agent exercise: release review

A fresh agent received only the loop-verify skill, the isolated example project, and this task: determine whether CHG-001 is complete and ready for release; run relevant checks; do not change app code or deploy.

The agent ran the supplied acceptance command and then additional CLI cases. The unit suite passed. Two extra cases failed the requirement:

| Input | Original result | Expected result |
| --- | --- | --- |
| https://bad host/ | Stored the URL; exit 0 | Reject invalid internal whitespace |
| https://example.com:abc/ | Stored the URL; exit 0 | Reject malformed port |

The agent recorded release failure, recorded the bounded local operations observation, reopened the implementation task as blocked, and left the outcome check open because no person participated. It changed only records in its assigned project. It did not treat the passing unit suite as proof of release readiness.

The package author then repaired URL validation, added regression cases, and made the example's validation policy explicit. Internal whitespace and control characters, malformed or out-of-range ports, and empty credential markers are rejected. DNS resolution and complete URL canonicalization remain outside the example. The repair was checked by the author with the same failing inputs and the test suite; it was not a second independent review.

This exercise validates a useful failure mode: the skill can challenge incomplete tests and preserve a failed release decision. One exercise does not prove generalization across products.

## Independent agent exercise: discovery and planning

The separate exercise asked a fresh agent to prepare a build ready spec and ordered tasks for a local book tracker with persistence, without implementing it. It produced seven requirements, sixteen criteria, and four ordered tasks. The ready gate passed, the checkpoint was current, and all build tasks stayed todo. No product source or tests were created or run. The observed result is recorded in evaluation/discovery-exercise.md.

## Corrected example flow

The author copied the repaired example to another disposable Git repository and ran the inspected acceptance command. Actual duplicate, malformed input, and fresh-process CLI results were recorded. Manual release and operations evidence was limited to the local demonstration. The ready, verify, and release gates passed. The learn gate correctly failed on the missing real-user outcome observation. This was not a deployment.

Raw results are in evidence/fixed-example-gates.json and evidence/fixed-example-observations.json. The test and structural validator outputs are also retained under evidence/.

## Limits and remaining gates

- Actual Codex plugin loading and installation were not tested; the Codex CLI is absent in this environment.
- No GitHub write, live CI, cloud deployment, database migration, scheduler, or telemetry adapter was exercised.
- The local evidence format is editable and unsigned. Observer names are recorded, not authenticated.
- The tool has been tested on one Linux/Python/Git combination and small repositories. Cross-platform behavior and large-project performance remain open.
- Ignored files and external environment changes need explicit reviewed records. Symlinks and submodules are rejected.
- Semantic requirement quality and risk classification need agent judgment. No static tool can establish demand or full accessibility by itself.
- Real builder trials, long running maintenance, retirement exercises, and comparative best in class benchmarks remain open.

The package is suitable for local evaluation and a controlled first pilot. The full system design includes the path to stronger service integration and release controls; those future capabilities are not claimed as implemented.

## v0.7 ChatGPT Work compatibility

- All 121 regression tests passed in the Work runtime: the prior 116 plus five Work-bundle tests. The five focused tests passed again after adding source-tree provenance. [Captured suite output](evidence/v07-tests.txt).
- The plugin manifest, main skill and source resources passed their validators. Codex CLI was absent; it is not required by the engine.
- Work bundles use committed, bounded resources, preserve relative paths, exclude root native project/CI records and untracked files, and record commit/tree and hashes. Tests cover portability, overwrite/dirty-source refusal, symlinks, budgets, failed-export cleanup and changed-bundle detection.
- The isolated Work skill trial exercised the real bundled CLI: product init/apply/align, acceptance, roadmap, checkpoint, full-project save/restore and fresh checks. Changing app.py made verification stale; rerunning the check restored verification. Product intent remained unchanged. [Trial record](evaluation/work-mode-exercise.md).
- During source review, the public roadmap snapshot was corrected to retain its schema_version/product envelope. Its product body was checked against native intent. No sync target or priority order changed.
- This validates Work command execution and resource use. The personal-skill save result is recorded in the conversation after its actual read-back. A fresh Work conversation must still demonstrate automatic selection. No human builder outcome, deployment or universal-directory publication is claimed. Codex desktop loading remains an optional separate test.

- The initial personal-skill save rejected multiple nested SKILL.md entries. The Work export now uses one installed entry and GUIDE.md lifecycle resources with adjusted local links. Explicit --work-bundle checks validate this layout; default plugin checks still require SKILL.md. Source plugins retain all eleven skill entries.
