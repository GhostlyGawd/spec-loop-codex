# Independent release exercise

The following is the reviewer's observed result on the original example, before repair. Referenced project records belong to that isolated exercise. It is an agent review, not a human study.

# CHG-001 verification review

Observer: codex-release-review. Date: 2026-09-06. Scope: the current local Python example only.

CHG-001 is not complete or recommended for release. REQ-001 says invalid URLs are rejected, but the current candidate accepts malformed host and port input. TASK-001 has been reopened as blocked; the phase remains building. No application or test code was changed.

The project uses the quick profile and low risk classification. That is appropriate for this deterministic, local, in-memory example with no accounts, network requests, persistence, money movement, or deployment. The accepted exact trimmed-string duplicate rule remains in scope; canonicalization is excluded. No independent sign-off or real user study is claimed.

## Executed checks and observations

- CHK-001: the inspected command `python3 -m unittest -v` passed through the Spec Loop runner with exit 0. Its three test methods make relevant assertions for trimming, the enumerated invalid inputs, and duplicate additions. Evidence: `.spec-loop/evidence/CHG-001/EV-b4aa10aa43f046619fe686591f503ad3.json`.
- Local CLI observations: seven of nine scenarios behaved as expected. A trimmed duplicate produced one entry; HTTP input was accepted; unsupported schemes, missing hosts, and embedded nonempty credentials were rejected; a corrected invocation succeeded; a fresh process had an empty list. Exact commands, outputs, exit codes, observer, timestamps, and source hashes are in `CHG-001-cli-observations.json`.
- Release check CHK-002: fails. `python3 app.py 'https://bad host/'` returned exit 0 and stored that string. `python3 app.py 'https://example.com:abc/'` also returned exit 0 and stored that string. These malformed URLs should have been rejected under REQ-001. The duplicate and baseline invalid-input portions of the procedure passed.
- Operations check CHK-003: passes within the declared local scope. Inspection of all 23 lines of `app.py` found only JSON serialization, argument/error handling, URL parsing, and in-memory list operations; there are no network or persistence calls. The invalid-input command returned exit 1 with a validation message. A later corrected-input command returned exit 0 with the requested entry, and a separate empty invocation returned `[]`. This is source inspection plus local process observation, not production monitoring or packet tracing.
- Outcome check CHK-004 remains unperformed: no person participated. Agent-executed CLI checks do not establish whether a person can complete the task. The outcome check belongs to the learning gate, not the release gate.

## Findings and next action

1. Code defect, release blocker: `app.py` tests only the scheme, presence of a parsed hostname, and nonempty credentials. It does not validate hostname whitespace or port syntax. Correct validation and add regression coverage for the reproduced failures before release.
2. Requirement and evidence gap: AC-002 and the current automated examples enumerate several invalid inputs but omit malformed hosts and ports. A passing CHK-001 therefore does not demonstrate the whole invalid-URL promise in REQ-001. Align the criteria and regression checks with that promise; do not narrow the requirement merely to make the gate pass.
3. Product uncertainty: the synthetic source is an assumption, not research. CHK-004 needs an actual observed participant before claiming an outcome or closing the learning loop. This is separate from the code defect blocking release.

Next: fix URL validation and add meaningful regression checks in an authorized implementation task, then rerun acceptance and local release/operations evidence on the corrected candidate. Source or contract changes make the existing evidence stale. Obtain a real participant observation only if making a product-outcome or full completion claim.

No dependency changes or installations, external service access, publication, or deployment occurred. Review records and the checkpoint are the only intentional project changes. Gate results are stored separately in `CHG-001-gates.json` after recording these observations.
