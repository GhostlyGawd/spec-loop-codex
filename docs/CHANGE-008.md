# CHANGE-008: Review health and recoverable Work handoff

## Need and authority

The user asked to work through the merge, recovery, real feature and unattended-review steps in order. Spec Loop itself is the product for this bounded technical cycle. The first scheduled review was created 4h53m40s after the expected time. A clean delegated recovery restored the exact v0.7 commit, but found no committed WORK_STATE.md. These are technical observations; no human builder outcome has been collected.

## Design and acceptance

Present three independent results: scheduled execution, review of current main, and installed skill provenance. Show the actual run link and checked commit. A recent merge need not have a scheduled event yet, so its push review is shown separately. Keep the current product roadmap and its missing human evidence visible.

1. Push/manual events, older success, wrong target, incomplete pages and stale observations cannot prove a current scheduled pass.
2. A pass needs the current attempt's review job, receipt-validation step and nonexpired artifact metadata. Waiting, missed, failed and unverified remain distinct.
3. An explicit installed bundle is checked locally, then its version and declared source tree are compared. No automatic overwrite.
4. The report performs no remote actions or project writes. Resume can find a committed handoff. Original product priorities and historical evidence remain intact.

## Architecture and boundaries

Use a small standard-library observer over a bounded JSON snapshot collected by GitHub MCP. It has no credentials, network client, schedule writer or dispatch capability. The collector owns completeness, fresh read-back and target authenticity; the report is not a signed attestation. Version 1 supports one daily UTC cron only. Six hours of grace is an explicit provisional alert threshold informed by the observed delay, not a GitHub SLA. Review after more observations. Maximum snapshot age is 15 minutes.

See [the collection and operation guide](REVIEW_HEALTH.md). Local acceptance covers adversarial evidence cases. The release target is a local technical module, followed by a reviewed source PR and Work bundle update. Roll back by selecting the prior source/bundle; preserve records. No production deployment or human value is implied.

## Feedback

The independent v0.7 recovery found missing handoff and stale checkpoint/evidence. This change adds the handoff and preserves stale historical records. The live health observation distinguishes today's v0.5 schedule from v0.7 main's push and compares the actual installed v0.7 bundle. A new user Work chat, builder feedback and sustained unattended reliability remain open.
