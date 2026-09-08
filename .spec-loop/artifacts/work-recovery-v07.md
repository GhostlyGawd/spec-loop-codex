# Spec Loop recovery

Recovered all **149 files (789,870 bytes)** from [GhostlyGawd/spec-loop-codex at 74b97535b94424226757ef8c5263672bb911c12d](https://github.com/GhostlyGawd/spec-loop-codex/commit/74b97535b94424226757ef8c5263672bb911c12d) into `project/`. Every blob, all 37 trees, and the reconstructed signed commit match their Git identities. Root tree: `1eef81a7b5a4173ee2b6ddc059b85205477a3441`. The exact selected snapshot is recovered; parent history was not requested or fetched and is represented by a local shallow boundary.

The installed **spec-loop** catalog entry matched this recovery/resume task. I loaded it through `skills.read`, followed its Work setup, main workflow, protocol, product and tool resources, and executed the native commands from the filesystem root returned by that provider. `skill-selection.json` records the selection and loading details. The bundle manifest reports v0.7.0 and the same source tree as the selected remote commit; its different source commit identifier is an unsigned bundle provenance claim, not a substituted project revision.

Doctor, `context CHG-HOST`, and `roadmap show` completed with exit 0 using installed resources. Doctor validated Python, Git, source snapshot, two change contracts and product revision 2. Context and roadmap inspected gates without running application checks. They refreshed only the derived `.spec-loop/product/roadmap.json`. All 149 original files, including product intent and checkpoint, remain byte-identical; Git status is clean. Reports and command output are outside `project/`.

## Current roadmap

Refreshed **2026-09-08 16:17:39 UTC**, current only at that check. The objective remains **keep product intent recoverable**: recover goals, current delivery state and the next decision without silently changing intent.

| Horizon | Initiative and intended result | Delivery and blocker | Next decision |
| --- | --- | --- | --- |
| Now | Portable installation diagnostics: compare source, copied resources and package identity | 1 task reported done; candidate unverified. Acceptance, release and operations evidence are stale. Historical coverage exists in `REL-V06-LOCAL`. | Collect the missing real builder outcome for the identified historical release; fresh candidate checks would require a separate execution scope. |
| Next | ChatGPT Work setup and builder pilot: load saved skill, resume and observe builder use | Active `CHG-HOST`; 1 task todo. Acceptance, release and operations evidence missing; no release coverage. | Observe a fresh user Work chat selecting the saved skill and completing a builder task. |
| Later, parked | Scoped GitHub product-file sync | No linked change; unverified | Review intent and define the first change when resumed. |
| Later, parked | Continuous product review runner | No linked change; unverified | Review intent and define the first change when resumed. |

Both contracts pass their **ready** gate; neither passes current **verify** or **release** gates. WIP limit is 1; current active-Now count is 1. Available capacity is recorded as zero days with unknown effort estimates, so there is no supported delivery forecast.

## Evidence limits and next useful action

- `WORK_STATE.md` and `AGENTS.md` are absent from the selected remote tree. Neither was invented. The native checkpoint identifies `CHG-HOST` but is stale because its saved source hash differs from the recovered snapshot. This limits the saved handoff, not the completeness of the requested commit recovery.
- `REL-V06-LOCAL` is a local, untrusted historical envelope targeting `local-diagnostics-evaluation`, with artifact `scripts/install_check.py` at SHA-256 `18c0a451e87638aecc13d49b0995ced8c46a77a3903fbb17e60f42bd80658e72`. Its outcome check is missing. Historical coverage does not prove current readiness, deployment or builder value.
- This run demonstrates catalog selection, provider resource loading and actual native command execution in an **independent delegated agent session inside the existing user conversation**. It is **not a new user chat**, so it does not satisfy `CHG-HOST`'s fresh-chat acceptance criterion or establish a real builder outcome.
- No application tests, installs, deployments, remote writes or schedules were executed. All remote reads used GitHub MCP. Existing local checkouts, prior local logs and other conversations were not read. Saved repository log files were recovered as snapshot bytes, not treated as newly executed evidence.
- Native sync reports `local-on-invocation`, external sync `not-configured`. A saved workflow file does not establish a live schedule; no current scheduling claim was verified.

**Next useful action:** start a genuinely new user Work chat and ask it to recover this pinned product and complete one real builder task, without supplying the skill path. Observe skill selection, loaded resources, onboarding/resume and the builder's result separately. Preserve the current horizons until an authorized product decision changes them. Recording that observation into native evidence is a later mutation; this recovery leaves the original records intact.

Saved companion evidence: work-recovery-v07.json, work-skill-selection-v07.json, work-recovery-after-v07.json. Detailed command outputs were inspected in the recovery workspace.
