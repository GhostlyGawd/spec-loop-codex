# Release and recover

For product goals, priorities, linked scope, and current roadmap facts, use [the product workflow](product.md). Read it when product state exists or this stage changes a product decision.
To preserve an observed release for later inspection, read [release history](history.md). A frozen record preserves local evidence; it does not perform or authenticate a deployment.

Read the shared protocol and the [release template](../../../templates/release.md). Prepare all reviewable release material before requesting missing authority. Existing applicable user authority remains valid.

Identify the exact source, build artifact, target environment, configuration, feature flags, migrations, and affected users. Link included changes and current verification. Check the deployment service's real state and the available tool schema.

Prepare rollout steps, smoke checks, success and stop thresholds, observation window, owner, rollback or forward repair, and data recovery. A source rollback does not reverse a destructive migration. Rehearse recovery for the actual risk.

Run the local release gate. It checks evidence readiness only. It cannot grant permission or verify the identity of a remote deployment. Check authority separately against the action and target. If authority is absent, finish the concrete candidate and ask one direct question about the pending action.

For an authorized release, use the real connected deployment tools. Apply a staged rollout where useful. Record the actual service receipt, artifact digest, target, timestamps, and smoke results. Inspect state before retrying after an uncertain timeout; use an idempotency key where supported.

If thresholds fail, use the authorized recovery plan and verify restoration. Report the actual deployment and user-visible result. Do not claim success from a queued deployment, a build pass, or a drafted receipt. Do not send launch or incident messages without explicit authority.
