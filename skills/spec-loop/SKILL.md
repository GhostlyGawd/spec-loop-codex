---
name: spec-loop
description: Build and maintain software from linked product specs, tasks, and evidence. Use for an end to end Spec Loop workflow, a new product, an existing project with missing specs, or resuming Spec Loop work.
---

# Spec Loop

Turn the user's outcome into a small change that can be checked and maintained.

Read [the operating protocol](references/protocol.md). Read only the stage guide needed for the next useful action. Resolve all bundled paths from this skill's location, not the project working directory.

| Need | Guide |
| --- | --- |
| Install, compare a loaded copy, or validate an upgrade | [Installation](references/install.md) |
| Compare or sync product intent with a GitHub file | [GitHub sync](references/github.md) |
| Manage goals, priorities, capacity, or a current roadmap | [Product workflow](references/product.md) |
| Understand a need, scope an idea, test demand | [Discovery](references/discover.md) |
| Design a journey, interface, or interaction | [Product design](references/design.md) |
| Define behavior, data, architecture, or import an existing system | [Contracts](references/specify.md) |
| Sequence work and define task boundaries | [Planning](references/plan.md) |
| Implement a scoped change | [Build](references/build.md) |
| Check implementation and evidence | [Verification](references/verify.md) |
| Prepare and perform an authorized release | [Release](references/release.md) |
| Maintain service or handle an incident | [Operation](references/operate.md) |
| Measure value, scale, refactor, or retire | [Evolution](references/evolve.md) |
| Use the local tool or fix a record format | [Tool contract](references/tool.md) |
| Inspect an earlier release or record later product results | [Release history](references/history.md) |

Start from the user's request and current project state. Keep the project stack and scope unless evidence supports a change. Use the quick, product, or critical profile according to actual impact.

Use the included [Python tool](../../scripts/spec_loop.py) for state, contract checks, dependency impact, context, and evidence. It has no cloud dependency. It does not approve, deploy, schedule, or prove user value.

At a stage boundary, state the result, evidence, remaining uncertainty, and next action. Continue authorized work without routine confirmation. If the user requested design only, complete the design and its checks without starting unrelated implementation.
