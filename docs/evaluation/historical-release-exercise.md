# REL-001 history and CHG-001 candidate review

Reviewed on 2026-09-07 using the supplied Spec Loop loop-verify skill. This is a review of existing records and static files, not a new product observation.

REL-001 has an internally valid frozen local evidence record. The current CHG-001 candidate is not verified or release-ready. The records do not establish that real users received the intended value.

| Question | Actual result | Meaning |
| --- | --- | --- |
| Historical REL-001 | `release-inspect REL-001`: pass, exit 0 | Frozen evidence validates at seal time, independently of later source edits. |
| Contract readiness | `gate CHG-001 --stage ready`: pass, exit 0 | The quick-profile contract meets this gate's structural requirements; no execution checks were selected. |
| Current verification | `gate CHG-001 --stage verify`: fail, exit 1 | CHK-001 is stale. |
| Current release readiness | `gate CHG-001 --stage release`: fail, exit 1 | CHK-001, CHK-002, and CHK-003 are stale. |
| Historical user outcome | `release-learn REL-001`: fail, exit 1 | CHK-004 is missing; no other validation errors were reported. |

## What the historical record establishes

The stored release is REL-001 for CHG-001, sealed at `2026-09-07T14:13:14.010005+00:00`, using engine version `0.2.0`. Its target is `synthetic-local`, observer is `fixture-builder`, and authority reference is `Local evaluation only`.

- Artifact: `app.py`, recorded size 1,021 bytes.
- Artifact SHA-256: `c469e26c6c709f8106356260b3d021c4ad830e54b8c40a6090c59a71ef084585`.
- Frozen source hash: `fdc048a8063f797be63136fb9c6c224e09e96edb634aa64e9870bd791fa4c695`.
- Release record digest: `7a45e11a7734bf196b2d62f542855f027c39726085e929111cfe9bd0f200dc7a`.

The frozen contract calls for valid HTTP/HTTPS URLs to be trimmed, invalid URLs to be rejected, and duplicate trimmed strings to leave one entry. It excludes persistence, accounts, network requests, and production deployment. The record embeds passing automated acceptance evidence for CHK-001 (`python3 -m unittest -v`, recorded exit code 0), plus passing manual release and operations evidence for CHK-002 and CHK-003. These records date from immediately before sealing and identify the same frozen source and contract hashes.

The release embeds release and operations plans and a receipt. The receipt explicitly describes a synthetic local teaching fixture and says no remote deployment, approval, or real user observation occurred. Both manual records likewise say this was a synthetic test fixture with no live service. They do not provide detailed per-input output or recovery results.

The inspection therefore establishes consistency and completeness under the frozen local gate rules. It does not independently authenticate execution, observer identity, authority, or a remote target. The record is locally editable and unsigned (`local-untrusted`); its digest is not protection against a writer who can recalculate hashes. The automated evidence retains an output hash and byte count, not raw test output. The release records the app artifact's identity but does not embed the historical app or test source, so this review cannot reconstruct or inspect their exact historical implementation. Nothing establishes a currently deployed artifact. Later edits and ordinary evidence expiry do not invalidate the frozen seal-time result.

## Why the current candidate is not ready

Current `app.py` consists solely of the comment: “Later unfinished candidate. The earlier implementation is no longer here.” It defines no `add_item` function or application behavior. Current `test_app.py` imports `add_item` and asserts trimming, rejection of several invalid input forms, and duplicate idempotency. Static inspection establishes a code defect: the API required by the tests is absent. No application or test code was executed during this review; an import failure is an inference from the files, not a newly observed test result.

The current tests contain relevant assertions for AC-001 through AC-003, but they cannot establish real-user value. Their invalid-input examples are finite, and they are not proof of every possible invalid URL. The ready gate passing does not outweigh the missing implementation or stale evidence. The quick profile and low risk are consistent with the declared disposable local teaching scope.

The verification and release gates directly establish that the existing passing evidence cannot be reused for the current source. Git status shows the visible project files as untracked; the empty tracked diff supplies no useful before/after history. The frozen release remains the historical evidence anchor.

The checkpoint is also outdated: state revision 0 says evidence has not been collected, while stored evidence and REL-001 exist. The task is marked done despite the missing current implementation. These summaries are not proof of current completion. State and contract were left unchanged because this request permits only a review report.

## Whether users received the intended value

There is an evidence gap and product uncertainty. Frozen CHK-004 requires observing a person complete the local task and explicitly leaving the check open if nobody participated. `release-learn` reports it missing. The receipt confirms no real user observation, and SRC-001 identifies the supposed user need as an assumption in a synthetic scenario, not user research. No recorded cohort, measurement window, or task-completion observation establishes actual value for users. This is absence of evidence, not evidence that users failed or received no value.

## Next action and review limits

For a later authorized implementation task, restore or complete the intended current behavior, inspect and execute acceptance checks, and collect fresh release and operations evidence for the resulting candidate. To assess REL-001's user outcome, obtain an actual observation explicitly tied to its identified artifact and frozen CHK-004, including a named observer, cohort, measurement window, and limitations. Do not attribute an observation of a later candidate to REL-001 merely because the change ID matches.

This review read only this project and the supplied plugin. No application code was run, source changed, observations created, account accessed, installation performed, or deployment attempted. Only this report was written under `.spec-loop/artifacts`; no checkpoint or evidence records were modified. All listed Spec Loop checks were read-only metadata/evidence evaluations. The report records their actual results without treating them as fresh application tests or user observations.
