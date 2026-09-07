---
name: loop-verify
description: Check a Spec Loop implementation or release candidate against its contract and current evidence.
---

# Verify a change

Read [the shared protocol](../spec-loop/references/protocol.md), then [the verify guide](../spec-loop/references/verify.md). Resolve bundled paths from this skill directory.

Use the latest user request and current project records. Preserve the requested scope and valid authority. Load only relevant artifacts. Perform the stage work, check its actual result, and update the current checkpoint.

For schemas, evidence, or state commands, read [the tool contract](../spec-loop/references/tool.md). The executable is ../../scripts/spec_loop.py relative to this skill directory.

Report the outcome, evidence, material limits, and next action. A file or a phase label alone is not proof that the product works.
