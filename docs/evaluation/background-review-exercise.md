# Independent offline product-review exercise

Request: Run a product review, say what to build next, and say whether the roadmap remains current if the daily job stops.

Inputs: Copied bundled reading-list example into a disposable Git project. Used its explicitly synthetic product-draft.json; no users or analytics were observed. Read loop-product, product, protocol and review-runner guides. No network, external mutation, application execution or plugin source edit was performed. Initial stale documentation was corrected concurrently by the implementation agent and re-read.

## Actual results

- Initialized native product state and applied the synthetic draft with the actual CLI and current digest.
- Refreshed roadmap, then ran native private review forward-001. Review exit 0; receipt status complete; reader current-at-read.
- Verified product state bytes were unchanged by review.
- Removed Markdown and repeated same run ID. Receipt bytes and checked time were unchanged; Markdown recovered.
- Changed app.py with a synthetic comment. Receipt reader exited 2 with inputs-changed. Reusing the original run ID exited 2. New run forward-002 completed and reader returned current-at-read.
- Invoked the actual CLI main with only its clock replaced by checked time plus 37 hours. Reader exited 2 with stale. This is a simulated reader clock; no daily job or passage of 37 real hours is claimed.
- Changed visibility to public while retaining an internal opportunity. Review failed with exit 2 and empty roadmap/signals in its failure receipt. Restored private config afterward.
- A nonexistent receipt returned unavailable with exit 2.

## Answer supported by the exercise

Keep Local URL collection in Now. Before adding scope, review and align CHG-001 with the product scope, then execute its required checks. The current candidate is unverified, release/deployment evidence is absent, and user outcome is unknown. The task count of one done does not override the failing readiness gate.

The roadmap is a checked snapshot. A stopped daily job does not update it or alert by itself. At the next receipt read, unchanged inputs expire after the configured 36 hours; changed inputs invalidate it earlier. A separate monitor is required for unattended missing-run alerts. Scheduled report production does not automatically write product priorities or perform external two-way sync. No schedule was installed or tested in this offline exercise.

## Review observations

No blocking defect was observed. The initial Markdown view only said Resolve current delivery gaps; the concrete alignment blocker was discoverable in JSON roadmap.changes. Surfacing gate blockers in Markdown would make the next action clearer for a novice using Actions summaries. Feedback was sent to the implementation agent.

Evidence: commands.json contains command arguments, exit codes and exact stdout/stderr for 19 local invocations. reports contains unchanged success receipts and the intentionally failed privacy receipt. All fixtures and observations are synthetic.
