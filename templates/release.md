# Release record

## Candidate
State release ID, included change IDs, source revision, artifact digest, build provenance, target environment, configuration, flags, and migrations.

## Readiness
Link current acceptance and quality evidence. Record known limits, unresolved risks, and the authority reference that applies to the exact action and target.

## Rollout
State ordered actions, exposure stages, owner, idempotency keys where supported, smoke checks, measurement window, success limits, and stop conditions.

## Recovery
Define rollback or forward repair, data recovery, dependencies, owner, expected recovery time, and rehearsal evidence. Do not assume a code rollback restores data.

## Actual result
After execution, record service operation IDs, artifact and target identity, timestamps, observed smoke results, and any recovery. Leave unexecuted steps explicitly unexecuted.

## Communication
Draft release notes and support guidance. Record sending only after an authorized action actually occurs.
