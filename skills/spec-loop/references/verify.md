# Verify implementation

For product goals, priorities, linked scope, and current roadmap facts, use [the product workflow](product.md). Read it when product state exists or this stage changes a product decision.
For a past release, read [release history](history.md). Inspect the frozen release separately from current-tree gates and product outcome evidence.

Read the shared protocol, contract, diff, and test procedures. Use [tool guidance](tool.md). Evaluate the actual candidate.

First check whether the criteria express the user's intended behavior. Then check whether each test can detect a violation. Passing a command with no relevant assertions is weak evidence even if the exit code is zero.

Use appropriate unit, property, integration, contract, end to end, visual, accessibility, security, performance, migration, and recovery checks. Select from actual risk. Inspect denied access and invalid input paths where present. Run integrated checks after merges or other input changes.

Inspect each automated command before using run. Record actual manual observations with record, a named observer, an explanatory note, and an existing observation file. A manual note cannot replace an automated check. Keep raw user data and secrets out of records.

Use the gate for the requested stage. Missing, failed, timed out, expired, stale, or malformed evidence cannot pass. A reported phase or a task marked done is not proof. Preserve failures; diagnose the cause and run the corrected candidate.

Classify findings as requirement defect, code defect, environment gap, evidence gap, or product uncertainty. State their effect and the next action. If a tool or service is unavailable, show that limit and do not label the check as passed.

For independent review, use a separate authorized reviewer with raw artifacts and the task. Do not share the expected answer or the author's preferred diagnosis. If independence is unavailable, state that the review was by the implementing agent.
