# CHG-002 — preserve release evidence and make local evaluation repeatable

Status: implemented; 47 regression tests and the independent use check passed. Packaging is verified by the release procedure. Date: 7 September 2026.

Source: the user requested continuation of the complete Codex plugin. The 0.1 design identifies historical release evidence and actual host validation as open gaps.

## Outcome and scope

An owner can inspect the evidence for an earlier release after current files change, and record later product observations for that release. A new builder can check local requirements and reproduce the source package. No live deployment, account installation, or authenticated approval is implied.

| Requirement | Acceptance |
| --- | --- |
| REQ-HISTORY | Seal only after the current release gate passes. Capture contracts, dependencies, required evidence, reviewed attachments, source and artifact digests, target, observer, and receipt. Refuse to replace a release ID. |
| REQ-INTEGRITY | Inspect a frozen record without reading current source, config, or original attachments. Reject malformed records, digest mismatches, and invalid frozen evidence. Clearly label local editable trust. |
| REQ-OUTCOME | Record a manual outcome against the frozen release and check definition. Later source edits do not invalidate it. Missing, later failed, or altered observations cannot pass a release learning report. Never reuse an outcome from another release. |
| REQ-PREFLIGHT | Report Python, Git root, source snapshot support, project format, and local Codex CLI presence without writes, installs, or application command execution. CLI absence does not prove that the Work host cannot load the plugin. |
| REQ-PACKAGE | Package only committed source, with fixed metadata and per-file hashes. Refuse tracked changes. Exclude temporary files. Produce identical bytes for the same commit in the tested Git/compression environment and verify the archive. |

## Tasks

1. Add the frozen release and outcome schemas and commands. Verify good and bad evidence, changes after release, and no overwrite.
2. Add preflight and the deterministic package command. Verify read-only behavior and repeatability.
3. Update the skill guides, version, system spec, host acceptance procedure, and compatibility notes.
4. Run the full regression suite and one isolated agent use case. Preserve evidence, commit the result, and save the new release package.

## Boundaries

Receipts and observer names are supplied records. Hashes detect ordinary changes; they do not authenticate the writer or remote service. Commands do not deploy, install, send messages, or schedule work. Small reviewed attachments are embedded; large build artifacts are represented by a streamed digest. Existing project/change/evidence schema version 1 stays readable. A new engine version invalidates current-tree evidence; frozen historical records retain their original engine identity.
