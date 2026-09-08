# Spec Loop Work technical trial

Completed with the real bundled Spec Loop 0.7.0 Python CLI on 8 September 2026. Read the explicitly identified personal skill and Work workflow directly; automatic skill selection in a new conversation was not tested. All created files are inside `work-v07-trial`; no tools were installed, global settings changed, or external services mutated.

The raw reading-list example was copied with its native records. Its existing quick profile is appropriate to this reversible, low-risk exercise. The inspected acceptance command is `python3 -m unittest -v`: three tests assert trimming valid URLs, invalid-input rejection, and deduplication. All three passed. The supplied one-person product target remains an unobserved synthetic objective, not research evidence.

## Current roadmap

Fresh at `2026-09-08T15:41:59.542141+00:00`, after checking the edited, restored candidate:

| Horizon | Initiative / intended result | Current delivery | Blocker | Next decision |
| --- | --- | --- | --- | --- |
| Now | INI-001: collect valid URLs once; linked to OBJ-001 and CHG-001 | Acceptance verified; 1 task reported done | Release/operations observations missing; human outcome unknown | Resolve delivery gaps only if that scope is authorized |
| Next | None recorded | — | — | No added commitment |
| Later | None recorded | — | — | No added commitment |

Owner: Builder. WIP 1/1; synthetic effort estimate 1–2 days within 2-day capacity. No date commitment. The roadmap refresh computes delivery facts; it does not change goals, scope, priority, or owner. Product revision stayed 1 and product digest stayed `fa74579e6048b4cc24b3481f34b8b21c6c6ef936ab0aa49b1947b09c6db20bb9`. Original and restored product state are byte-identical, including after the source edit and refresh. Their body exactly matches the bundled draft (`34-intent-preservation.json`).

## Commands and observed results

CLI prefix: `python3 /workspace/scratch/c574d7af1897/personal-skills/spec-loop/bundle/scripts/spec_loop.py --root PROJECT`. Every exact command, working directory, exit code and output is in `commands.jsonl`; numbered JSON receipts make individual results easy to inspect. Drivers: `run_trial.py`, then `resume_trial.py` (already executed; do not rerun over existing folders).

| Operation | Result |
| --- | --- |
| Copy bundled example; `git init -q`; `doctor` | Python 3.12.13, Git and source snapshot passed. Codex CLI unavailable and unnecessary. Existing native state reused; no reinitialization over records. |
| `product inventory`, `product init`, `product show`, `product apply --file .spec-loop/artifacts/product-draft.json --expect-digest …` | Recorded synthetic intent and decision provenance using current tokens. |
| `product align CHG-001 --expect-digest … --expect-contract …` | Reviewed linked contract against unchanged intended behavior; recorded binding before checks. |
| `gate CHG-001 --stage ready`; `run CHG-001 --check CHK-001 --observer codex-work-trial`; `gate CHG-001 --stage verify` | All exit 0; acceptance and verify passed. Direct unittest output also saved. |
| `checkpoint CHG-001 --expect-revision 0 …`; local Git commit; full tar archive | Saved code, contracts, product history, evidence, checkpoint and WORK_STATE.md. Derived roadmap cache excluded for rebuilding. Git identity supplied per command, without settings changes. |
| Restore archive in `resumed/reading-list`; inspect state and Git diff; `doctor`; `context CHG-001`; `roadmap show`; `gate CHG-001 --stage verify` | All succeeded. Empty diff, same Git revision, 59 exact file hashes matched. Saved evidence remained current in the different folder. |
| Append a comment to restored `app.py`; `gate CHG-001 --stage verify`; `roadmap show` | Gate exit 1: `CHK-001: stale`. Fresh roadmap correctly showed candidate `unverified` despite unchanged behavior. |
| Rerun `run … --check CHK-001`; `gate … --stage verify`; checkpoint; roadmap | Exit 0; new source evidence passes. Edited working copy remains visibly changed from the saved commit. |

Saved commit: `36b9a3bf1ff065018fb13afc08ce692768f48f6e`.
Archive: `saved-project.tar.gz`, SHA-256 `5bf58167ca570c0a706e89fe010537881d095c027c28bbf2a450de6639f97ce3`.
Restore and file-hash proof: `19-resume-proof.json`.

## Limits and blocked behavior

A read-only release gate returned exit 1 because CHK-002 and CHK-003 have no manual evidence; roadmap `plan_ready` is false. No release or deployment action occurred. CHK-004 requires a person and remains unobserved, outside this exercise. No outcome success was invented.

This proves local full-project recovery into a different folder, not cross-conversation durable retrieval. The archive and both projects remain local under the requested write boundary. No external persistence or schedule is configured; a saved skill alone does not save the product. On another session, provide the archive and the skill, restore the full project, then inspect WORK_STATE.md/state/diff and run doctor, context, roadmap and verify again. Evidence freshness must be recomputed.

The source repository preserves selected raw results in [the Work trial evidence](../evidence/v07-work-trial.json). The full command log and local archive remain in the isolated evaluation workspace.
