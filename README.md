# Spec Loop

A plugin for spec driven product development in ChatGPT Work and Codex.

Use it to move from a user need through product design, architecture, implementation, verification, release, operation, and improvement. Keep specs and evidence with the project so work can resume over time.

Version: 0.8.0. This is a source package and working local reference implementation. Source is available in GhostlyGawd/spec-loop-codex. Actual Codex installation remains untested.

## Review health in 0.8

Read-only schedule, current-commit review and installed Work version checks now share an evidence report. See [review health](docs/REVIEW_HEALTH.md) and the saved [project handoff](https://github.com/GhostlyGawd/spec-loop-codex/blob/main/WORK_STATE.md). A health check does not create a watchdog or enable unattended sync.

## ChatGPT Work mode in 0.7

Use [the Work mode guide](skills/spec-loop/references/work-mode.md) to start or resume in ChatGPT Work. The engine needs Python and Git, not the Codex app or CLI. A self-contained personal `spec-loop` skill can package the same lifecycle resources with the host's skill-creator. Once saved, request “Use Spec Loop to continue my product” or select it with `@` when available.

`scripts/work_bundle.py` copies committed resources into a new bundle directory. It excludes this repository's root product records, CI and untracked files, validates resource paths, and records hashes and source identity. The helper creates files; the host's personal-skill save process performs installation. Native project state must be saved separately to resume after a workspace reset.

The original plugin format remains supported. Public catalog distribution, personal-skill persistence and actual host selection are separate checks; see [validation](docs/VALIDATION.md).

## Installation and native pilot in 0.6

Use [the installation guide](skills/spec-loop/references/install.md) to check source resources, verify an extracted source archive, and compare an explicitly identified installed copy. Run `python3 scripts/install_check.py --root /path/to/spec-loop`. Host loading remains unverified until an actual host selects and runs the skills.

Spec Loop now uses native product records for its own installation milestone. Scheduled reports derive evidence for CHG-006 and keep CHG-HOST open. [The pilot record](docs/PILOT.md) separates the source-package release from actual host and builder acceptance. This repository is plugin source, not a registered marketplace catalog; use the host's plugin-creator to connect a personal local marketplace.

## Start here

- Read [the full system specification](docs/SYSTEM_SPEC.md) for the design, scope, architecture, gates, and roadmap.
- Read [validation results](docs/VALIDATION.md) for checks that actually ran and remaining limits.
- Ask ChatGPT Work or Codex to use the main skill at skills/spec-loop/SKILL.md in this extracted package. This is a local evaluation path, not a plugin installation.
- Use [the reading list example](examples/reading-list/README.md) for a small complete contract and runnable code.

Normal requests include “Turn this idea into a small first version,” “Add this feature using the current specs,” “Check whether this change is ready,” and “Help me reduce this product's cost.”

## Included

Eleven skills cover the full lifecycle. Nine templates define product, design, architecture, security, release, operations, learning, and retirement records. Eleven JSON schemas define project, change, ordinary evidence, release, outcome, product intent/state, GitHub file snapshots, and background review inputs/receipts. A Python tool checks links, dependencies, evidence freshness, release readiness, and local state conflicts.

The workflow has three profiles: quick, product, and critical. More impact requires stronger evidence. A small change can use a short contract and a focused check.

## Local tool

Use Python 3.10 or later. Evidence requires Git at the project root. No Python packages, accounts, or network services are required by the tool itself.

```bash
python3 /path/to/spec-loop/scripts/spec_loop.py --help
python3 /path/to/spec-loop/scripts/spec_loop.py --root /path/to/project init --name "My product" --profile product
python3 /path/to/spec-loop/scripts/spec_loop.py --root /path/to/project new CHG-001 --title "First useful change"
```

Use `doctor` to check local requirements without changes. Fill the draft from the user request and actual evidence. Then use gate, run, record, impact, context, and checkpoint. Read [the tool guide](skills/spec-loop/references/tool.md) for the contract. Use [release history](skills/spec-loop/references/history.md) to preserve a release and connect later product results to it.

Run the tool tests from this plugin directory:

```bash
python3 -m unittest discover -s tests -v
```

The runner executes an explicitly selected command after the agent inspects it. It is not a sandbox. Gate success does not grant permission, authenticate an observer, prove demand, or deploy a product.

## Product management and roadmap in 0.3

Use “Show my roadmap”, “What should I build next?”, or “Capture this feedback” with the new loop-product skill. It manages strategy, goals, opportunities, initiatives, priority reasons, capacity, dates, and recorded decisions. [The product guide](skills/spec-loop/references/product.md) describes the commands and the example.

The roadmap refreshes on show/resume and after relevant CLI writes. It derives delivery facts from existing contracts, checks, releases, and observations. Goal/scope changes require contract alignment and fresh evidence. Priority-only edits preserve valid product test evidence. Product backup/restore preserves decision history.

Roadmap refresh occurs on invocation. A configured product file can also sync through GitHub MCP as described below. The optional v0.5 workflow adds scheduled derived review reports. A local release envelope does not prove remote deployment; an outcome check does not prove causation or market demand. The roadmap retains these distinctions.

## GitHub file sync in 0.4

The adapter compares local intent with one configured GitHub JSON file, merges independent edits, reports conflicts, and prepares an exact MCP file request. It verifies read-back before applying inbound intent or updating the last common version. A durable pending operation supports timeout and local-crash recovery. Public transfers require review and reject internal/restricted opportunity records.

Read [the GitHub guide](skills/spec-loop/references/github.md) for configure, plan, confirm, status, and cancel. [The public product roadmap record](docs/product-roadmap.json) is a snapshot of recorded native product intent; delivery evidence comes from the native contracts and records. [Live check results](docs/evidence/v04-live-github.json) record actual file creation, no-op comparison, and independent local/remote edits on the review branch.

This is agent-mediated product-file sync. It does not provide GitHub Issues/Projects sync, a continuous service, or authenticated local receipts.

## Background product reviews in 0.5

The optional GitHub Actions workflow reviews committed product inputs daily at 07:17 UTC and on manual, push and PR events. Each review publishes a JSON receipt and readable roadmap report in Actions. Native projects derive current gates and evidence; exchange-only projects show delivery as unknown. Reviewed feedback/telemetry records can flag negative results and stale observations without changing priorities.

Read [the runner guide](skills/spec-loop/references/review-runner.md) for setup, input limits, receipt validation and missed-run recovery. A receipt reader checks present inputs and a default 36-hour expiry. Workflow execution has time/concurrency bounds and no model calls. One default-branch schedule event passed on 8 September 2026, almost five hours after its nominal time. Sustained operation remains unverified. Reports do not rewrite the committed planning file or perform unattended bidirectional sync.

## Release history and packaging

- Freeze a passing release with its original contracts, evidence, reviewed attachments, artifact digest, and receipt.
- Inspect it after the current files change, and record later outcomes against that release.
- Check the local environment with `doctor` without writes or application commands.
- Build a verified source archive from a commit with `scripts/package.py`.

Read [host acceptance and upgrades](docs/HOST_ACCEPTANCE.md) for exact evaluation and packaging steps. Records are unsigned local evidence; no deployment or approval is performed.

## Distribution and compatibility

The manifest is .codex-plugin/plugin.json and skills are bundled under skills/. The package uses no hooks or MCP server. For account installation or publication, select the destination and follow the current [OpenAI plugin guide](https://learn.chatgpt.com/docs/plugins). Validate an actual installation before claiming host compatibility.

Tested in this session on Linux with Python 3.12 and Git. Other operating systems, Python versions, actual Codex loading, deployment services, and sustained scheduled operation remain untested; see the validation record for CI results. Source snapshots reject symlinks and submodules. Evidence is conservative and can become stale after unrelated source changes.

All connected service actions must use real available tools and current user authority. The GitHub product-file adapter is implemented. Other service adapters and signed release evidence remain future work.
