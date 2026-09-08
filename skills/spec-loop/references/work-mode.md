# ChatGPT Work mode

Use Spec Loop in the user's current Work conversation. A Codex app or CLI is not required. Read this guide for setup, unavailable tools, project persistence or resume after a workspace reset.

## Load the workflow

If the host supplies Spec Loop as a plugin, use its resource root. If it supplies the personal Spec Loop skill, its `bundle/` folder is the plugin root. Read [the main skill](../SKILL.md) and its selected stage guide from that root. Focused lifecycle skills in a personal bundle are resources; they are not eleven separate installed entries.

If no installed entry is available but the user has provided the source in this conversation, read it directly and continue. Report this as source use in Work. Do not require a desktop installation to run the local workflow. Do not claim automatic skill discovery from a direct file read.

With a resource provider, read resources using that provider and use its returned filesystem root for commands. With a filesystem skill, resolve paths from its actual directory. Never reuse an old session's absolute path without checking it.

## Select actions from observed access

| Available capability | Useful action |
| --- | --- |
| Readable skills and project files | Research, design, specs, planning and review of supplied evidence |
| Python 3.10+, Git, writable project and command execution | Native contracts, checks, evidence, product intent, roadmap and checkpoint |
| Connected GitHub tools | Authorized reads, changes, PRs and the configured product-file sync |
| Available deployment or design integration | Use its own setup and actual results for the requested stage |
| Verified scheduling service | Run the explicitly configured review; inspect dated receipts |

Use `python3 /actual/plugin/root/scripts/spec_loop.py --root /actual/project doctor` before native work. `doctor` checks local requirements without writes. CLI presence is informational. Missing Python or Git limits native verification; continue useful design work and keep executable gates unknown. Do not invent a connector, credential, installed plugin, persistent filesystem or active schedule.

For a new product, select a writable project folder. Initialize Git only for an explicitly new project; do not nest a new repository inside an existing one. Run `init`, then follow [product setup](product.md) and [contracts](specify.md). Have the agent execute commands; the user does not need to use a terminal. Application checks must be inspected before execution.

## Preserve work across conversations

The installed skill stores workflow resources. The project owns code, `.spec-loop` records and its `WORK_STATE.md`. These are separate lifetimes.

At a useful boundary, run `checkpoint` with the current revision and active change. Update the project state summary with intent, source revision, evidence, open blockers and next action. Do not store credentials or unrelated conversation content. A checkpoint is not a full backup.

For a GitHub project, save the reviewed code, contracts, state, evidence and release records through the connected repository tools. Read back the resulting commit/tree before reporting that work is saved. Keep generated roadmap caches out of source; rebuild them on resume. Do not force-push or confuse a local transferred history with the remote history. Untracked files need an explicit save decision; a local commit alone is not remote persistence.

For a project without a repository, use a durable file destination permitted by the current host and user. Save the full project with its records, not just a roadmap screenshot or product-intent backup. When durable storage is unavailable, say exactly which work remains local. Never search unrelated conversations or files to recover a project.

On resume, retrieve only the user's identified project and revision through available tools. Read `WORK_STATE.md`, native project/state files and the current diff. Then run `doctor`, `context` for the active change and `roadmap show` when product state exists. Recompute freshness; a saved success may now be stale. If source or native records are missing, recover the saved project before native writes. Do not silently initialize over a partial project.

## Roadmap behavior

The same [product workflow](product.md) applies in Work and Codex. Roadmap show/resume and relevant native writes refresh derived facts. They preserve goals and priorities. GitHub product-file sync remains agent-mediated and needs a configured target and read-back. Scheduled reviews are separate from this chat; installing this skill does not create one. No unattended two-way sync or continuous monitoring is implied.

## Installation and verification

Use the current host's personal-skill creation/install capability when it is available. Initialize one personal skill named `spec-loop` with the host's skill-creator. Populate it with `templates/work-skill.txt` as `SKILL.md` and use `scripts/work_bundle.py --root /committed/plugin --output /personal/skill/bundle` for its resources. The helper requires a new output folder, validates committed resources and does not install anything itself. Use the host's save/verify process to persist the complete personal skill. Do not write a guessed marketplace or create a Codex deep link for Work.

The bundle records source commit, file hashes and payload digest in `work-bundle.json`. It excludes the plugin repository's root product records and untracked files; bundled examples remain synthetic. Compare `install_check.py --expected-digest` with a trusted recorded digest when checking a restored copy. Hash inventories are unsigned. For an update, prepare and validate the new bundle before replacing only this skill's old bundle through its supported save flow; preserve other personal skills.

Validate three separate results: (1) the saved entry and resources, (2) actual commands from those resources in Work, and (3) automatic selection in a fresh Work conversation. Only mark each result complete when observed. A direct resource read proves neither automatic selection nor a human product outcome.

OpenAI documents the shared format and Work support in [Build plugins](https://learn.chatgpt.com/docs/build-plugins) and [Use plugins](https://learn.chatgpt.com/docs/plugins), checked 8 September 2026. Account installation controls and source availability vary; use the capabilities actually exposed in the current session.
