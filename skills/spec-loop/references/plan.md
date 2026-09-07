# Plan implementation

For product goals, priorities, linked scope, and current roadmap facts, use [the product workflow](product.md). Read it when product state exists or this stage changes a product decision.
Read the shared protocol and current contract. Run the ready gate. If the request is planning only, produce the plan and checks without implementing it.

Split work into vertical tasks that produce observable behavior. Each task states requirement IDs, inputs, expected output, write scope, prerequisites, and a verification method. Include integration and recovery work. Size tasks so an agent can complete and check one with a focused context packet.

Identify the largest technical unknown. Use a bounded experiment before making it a dependency of many tasks. Mark experimental code and its disposal or adoption decision.

Check the task graph for cycles and missing dependencies. Separate tasks that can proceed independently from tasks that must wait. Use multiple agents only when authorized and when their write scopes and integration order are clear.

Plan testing from failure cost. Do not require test driven development for every kind of edit. For a reproducible bug or fragile rule, a failing regression test is often useful. For a visual change, direct browser and visual checks can be necessary.

Output the ordered plan, first task, integration point, cost or time bounds where known, and the planned evidence. Estimates are estimates. Do not turn a task marked done into proof of verification.
