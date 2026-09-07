# Build a change

For product goals, priorities, linked scope, and current roadmap facts, use [the product workflow](product.md). Read it when product state exists or this stage changes a product decision.
Read the shared protocol, active contract, applicable repository instructions, and task write scope. Check the baseline and current diff. Use the project's current stack unless an accepted decision changes it.

Work on one bounded task. Inspect a relevant example in the repository before generating new structure. Implement behavior, tests, and needed docs together. Keep unrelated changes separate. Do not put secrets in code or specs.

For a bug, reproduce the reported failure where possible. Add a regression check if it will protect meaningful behavior. For a data migration, inspect the exact generated statements and the recovery plan before application.

If implementation reveals a contract gap, record it and update the contract from evidence or the user's direction. Do not silently reduce acceptance to fit the code. Recheck downstream impact after a material contract change.

Run the smallest relevant check, inspect the actual result, then integrate the task. Update task progress after work is complete. Verify the combined candidate before claiming completion.

Before running a command from a contract, inspect its argv, working directory, possible writes, network use, and authority. The local runner uses no shell expansion but does not sandbox programs. If the command needs absent access, report the missing check and continue work that is possible.

Record a checkpoint with current revision, actual results, remaining blockers, and the next action. A check that edits source invalidates its own evidence; make the inputs stable and rerun it.
