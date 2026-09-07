# Independent discovery and planning exercise

A fresh agent used the main Spec Loop skill on an empty, isolated Git repository. Its request was to prepare a build ready product spec and ordered tasks for a single-user Python book tracker. The product must add titles and authors, mark books read, list unread books, and retain local data between runs. Accounts, network, paid services, and implementation were excluded.

The agent produced a product brief, behavior specification, architecture, ordered tasks, change contract, document review records, and a current checkpoint. It selected standard-library Python and SQLite, made the data path and command contract explicit, and addressed data integrity and recovery. Those choices were design decisions, not executed product behavior.

Observed results:

- Seven requirements, sixteen acceptance criteria, and four ordered tasks.
- The ready gate passed.
- Document links passed the agent's check.
- The context packet was 22,147 characters and reported a current checkpoint.
- Every implementation task remained todo.
- No product source or test file was created. No product test, install, publication, or external service action ran.
- Manual evidence was labeled as agent document review.
- The user's future runtime and a real usability observation remained unverified.

The package author inspected the produced product spec, task plan, validation JSON, and checkpoint. The outputs respected the design-only request and contained a usable handoff. This is one bounded agent exercise. It is not a real builder trial or a completed implementation.

The raw validation summary is preserved in ../evidence/discovery-validation.json. The generated product is an evaluation fixture, not an additional product requested for delivery.
