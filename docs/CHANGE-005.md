# CHG-005 — Bounded background product reviews

Status: implemented; 105 local tests pass. Live push/PR jobs and the in-job receipt reader passed; see the validation record for checked revisions. Date: 7 September 2026.

The user approved the staged build and asked to continue after merging v0.4. Add a GitHub Actions review runner. Keep the product-file adapter's conflict and decision rules intact.

| Requirement | Acceptance |
| --- | --- |
| RUN-001 Inputs | Explicit native or exchange mode. Validate config, product and optional signal records. Native mode derives existing gates without running application commands. Exchange mode reports delivery as unknown. |
| RUN-002 Reports | Produce an immutable JSON receipt per run ID and a Markdown view, bound to checked inputs and Git commit. Detect input changes during review. Never alter product intent or acknowledge a remote sync. |
| RUN-003 Freshness | Reader checks receipt integrity, current input identity and age. Missing, failed, future, changed and expired receipts cannot report current. A reader detects missed runs even if the scheduler stops. |
| RUN-004 Signals | Accept bounded, reviewed feedback/telemetry records with objective, source, observer, time, privacy and explicit result. Stale signals and negative results request review. No inference of causation or automatic priority changes. |
| RUN-005 Recovery | Exclusive output lock; atomic receipt; same run ID cannot change inputs. Replays do not renew the original checked time. Failure leaves a failed receipt, not old success. New attempts use new IDs. |
| RUN-006 Bounds | No model calls, network client, application commands, or repository writes. Linux CLI deadline 60 seconds; input/report limits; workflow timeout 5 minutes, one active job per ref and 14-day artifact retention. These are execution bounds, not an account billing cap. |
| RUN-007 Operation | Daily 07:17 UTC, manual, push and PR checks. Read-only repository token, SHA-pinned actions, no persisted credentials. Separate test job. Review reports in Actions artifacts and job summary. Schedule activates only on default branch. |
| RUN-008 Validation | Regression tests for real input/state invariants and a live workflow attempt on a review branch. Record permission or runtime failures honestly. A first successful job does not prove sustained scheduling. |

No unattended bidirectional MCP sync, Issues/Projects adapter, model-driven strategy, webhook/telemetry collector, independent alert service, or authenticated receipt is included. In this repository, the exchange file contains planning data and no native change evidence. Automatic reports must make this gap explicit. Reports do not update the committed planning file. Local native roadmap refresh and v0.4 file sync remain available to agents.

GitHub may delay/drop scheduled runs and disable public schedules after 60 inactive days. The stopped service cannot notify on its own. The reader's 36-hour freshness window and documented external check provide a visible boundary; an independent watchdog remains a later deployment choice.
