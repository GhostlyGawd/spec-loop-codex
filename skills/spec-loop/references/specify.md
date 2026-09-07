# Specify behavior and architecture

For product goals, priorities, linked scope, and current roadmap facts, use [the product workflow](product.md). Read it when product state exists or this stage changes a product decision.
Read the shared protocol and [tool contract](tool.md). Use the [architecture template](../../../templates/architecture.md) for consequential choices. Read the bundled change schema before creating JSON by hand.

For a new contract:
1. State the user, problem, outcome, and non-goals.
2. Link each requirement to source IDs. Define observable acceptance criteria with unique AC IDs.
3. Cover invalid input, authorization, concurrency, retries, compatibility, and recovery where relevant.
4. Link each criterion to an acceptance check. Record the command or manual procedure; do not invent a result.
5. Define tasks linked to requirements, prerequisites, and write scopes.
6. Record assumptions with impact, status, and basis. Keep unresolved high impact assumptions open.
7. Link design, architecture, and any required security artifacts. Add release and operations artifacts before collecting evidence that will be used for release.
8. Run the ready gate and review the meaning of the criteria.

For architecture, define boundaries, data model, invariants, APIs, events, external dependencies, secrets, and failure behavior. State quality limits with a workload and a measurement method. Compare viable choices against the existing system and current scale. Record substantial decisions and their review trigger.

For a data change, define migration order, mixed version compatibility, backfill, integrity checks, lock risk, recovery, and restore evidence. For AI behavior, define model and prompt versions, evaluation data, allowed tools, cost, latency, uncertainty behavior, and failure limits.

For an existing repository without specs, inspect instructions and tests, run a safe baseline, map one user journey, and record observed behavior. Mark inferred intent as an assumption. Create a contract for the requested delta; do not reverse engineer the entire repository before a small change.

Validate contradictions across brief, design, API, data, acceptance, and code. Mechanical schema success does not establish that a requirement is useful or correct.
