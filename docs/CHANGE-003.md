# CHG-003 — a product roadmap that stays current locally

Status: implemented; 67 tests, structural validators, a local CLI workflow, and an isolated agent exercise passed. Actual host loading and external integration remain open. Date: 7 September 2026.

The user approved the product management implementation plan. This release delivers the complete local product workflow. External sync and continuous runners remain later integration stages; no remote destination is configured.

| Requirement | Acceptance |
| --- | --- |
| PM-001 Product intent | Versioned strategy, objectives, opportunities, initiatives, priorities, dates, owners, capacity, and discovery records. Strict schemas, unique IDs, valid references, and cycle detection. Unknown evidence remains unknown. |
| PM-002 Decisions | Compare-and-swap edits with an input digest; actor, authority reference, reason, and before/after hashes retained atomically. Reject a stale writer and invalid input without changing intent. Names and hashes do not authenticate authority. |
| PM-003 Roadmap | Derive Now/Next/Later and parked/retired views from intent and current change gates. Show task reports separately from verified evidence; expose dependencies, partial historical release coverage, per-release outcomes, and suggested next decisions. Never infer remote deployment or product value. |
| PM-004 Automatic refresh | Refresh after relevant CLI mutations and when showing the roadmap or resuming context. Check input revisions before writing; expose invalid inputs and conflicts. Repeated identical inputs have identical content. Time-based evidence expiry must change the view even with unchanged files. |
| PM-005 Scope alignment | Bind each linked change to the reviewed semantic product scope. Goal/scope changes block readiness until contract review and explicit alignment; alignment changes the contract hash and invalidates current evidence. Priority/date/display changes do not invalidate product evidence. Historical v0.2 records remain readable. |
| PM-006 Recovery | Read-only inventory with unknown intent, bounded context, product backups, restore as a new revision, and unknown-schema rejection. Preserve historical decisions and v0.2 project formats. |
| PM-007 Agent use | Product routing and lifecycle guidance use the same records. A fresh agent can interpret failures, distinguish release history from deployment and outcomes, and leave product decisions within existing authority. |

Validation: regression tests of these invariants, one complete local workflow, isolated agent use, manifest/skill checks, and verified source packaging. Actual host and external connector acceptance require their own observed results.
