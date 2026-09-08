# Spec Loop project handoff

## Goal

Build and maintain a spec-driven product system for ChatGPT Work and Codex. The user uses ChatGPT Work. Keep specs, product decisions, roadmap facts and release evidence linked. GitHub is the saved source for this project.

## Current work

CHG-008 adds read-only review health and this handoff. Read docs/CHANGE-008.md and docs/REVIEW_HEALTH.md. Native .spec-loop/product/state.json owns product intent; rebuild the roadmap rather than treating this summary as authority. Read the current commit and diff before acting.

PR #4 merged v0.7 at 74b97535b94424226757ef8c5263672bb911c12d. Its main push run 34249471582 passed both jobs. Independent recovery restored all 149 files, 37 trees and the exact commit; the installed skill loaded and doctor/context/roadmap commands succeeded. This was a delegated agent context inside the same user conversation, not a new user chat.

The first scheduled review was run 34224621873 on 550e15e8da293adaa0c24cb7172ed7c25139fc80, created 2026-09-08T12:10:40Z. Review, receipt validation and artifact metadata passed. Nominal time was 07:17 UTC; delay was 4h53m40s. This proves one scheduled execution only.

## Resume

Run the selected Spec Loop resource's doctor, context CHG-008, and roadmap show against this complete Git root. Inspect active native state and evidence before continuing. A stale checkpoint or older release does not establish current readiness. The installed skill stores workflow resources; it does not save project files or create background tasks.

## Open checks

- New user Work conversation and real builder outcomes remain unobserved; keep CHG-HOST open.
- v0.6 evidence is historical and can be stale under the current engine/source. Do not relabel old receipts.
- Sustained schedule timing and the first independent watchdog execution need future evidence.
- Unattended two-way sync and production deployment are not implemented. The old demonstration sync branch must not be silently retargeted.

## Next action

Inspect current CHG-008 release evidence, then use the installed skill in a new user Work conversation to resume an actual builder task. Collect real feedback before changing product priorities. Repository source, native records and handoff must be saved together; never force remote refs when transferred local and remote histories differ.
