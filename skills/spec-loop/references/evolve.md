# Learn, scale, refactor, and retire

For product goals, priorities, linked scope, and current roadmap facts, use [the product workflow](product.md). Read it when product state exists or this stage changes a product decision.
For a result tied to an earlier release, read [release history](history.md). Use `release-learn` for frozen evidence and `gate --stage learn` for the current tree. Never treat a historical pass as proof of the current candidate.

Read the shared protocol and the [learning template](../../../templates/learning.md).

Compare product outcomes with the baseline, target, cohort, and observation window. Check sample quality and limits before inferring a cause. A feature can pass code checks and fail to create value. Use the keep/change/stop rule from the brief and update the roadmap from observed results.

For scale work, identify the measured constraint: user flow, query, CPU, memory, storage, queue, provider quota, failure isolation, or cost. State the workload and current quality. Compare a small number of changes, including a simpler option. Verify improvement, failure behavior, and unit cost at the intended load.

For refactoring, preserve the external contract unless the user accepts a behavior change. Link debt to a real consequence. Use characterization and regression evidence for the affected behavior. Remove obsolete code and flags only within the agreed scope.

For retirement, use the [retirement template](../../../templates/retirement.md). Map active users, consumers, stored data, exports, notice, deletion, backups, access, and residual costs. Prepare concrete actions and reuse applicable authority. Check each actual shutdown or data operation; do not infer completion from a plan.

Create a new change for the next useful result. Link the observation to its reason. Archive superseded decisions and remove stale current-state claims. The local learn gate checks the current candidate; use release-bound records for observations spanning later versions.
