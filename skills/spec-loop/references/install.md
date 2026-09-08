# Install and prove the loaded copy

Use this guide for first installation, a stale installed copy, or an upgrade. Resolve scripts from the plugin location supplied by the host. A source check cannot establish that the host loaded a skill.

## Check the source

Use Python 3.10+:

```bash
python3 /path/to/spec-loop/scripts/install_check.py --root /path/to/spec-loop
```

This read-only check validates Spec Loop's required resources, skill identities, relative Markdown links and manifest/engine versions. It parses inspected Python as syntax; it does not execute that Python. The result includes a payload digest and skill inventory. It always reports host loading as unverified. `codex_cli_available` only reports executable discovery.

For an extracted archive made by `scripts/package.py`, add `--package`. This also checks every listed file and the archive inventory, including the Git bundle bytes. Compare the archive SHA256 with the reviewed release record first: the internal package manifest is unsigned. This checker does not extract archives, validate Git bundle semantics, install code, or prove that arbitrary Python is safe.

Use a clean extraction for package verification. An added `.git` directory changes that inventory. Generated `__pycache__` directories and `.pyc` files are excluded. Source/copy comparison covers `.codex-plugin`, scripts, skills, schemas, templates, docs and examples; it is not a general-purpose filesystem comparator. Other source files are covered by the package manifest when `--package` is selected.

## Install through the actual host

In the ChatGPT desktop/Codex host that will use the plugin, make the reviewed source folder available, then ask its plugin-creator:

> Add this existing Spec Loop folder to my personal local marketplace. Preserve its source files and other marketplace entries. Install it through the supported local-plugin flow, then tell me which installed copy the host resolves.

Use the actual local path in that request. Follow the host's built-in plugin-creator process for marketplace configuration; do not paste the repository URL into a marketplace installer and assume the repo is a catalog. This repository contains plugin source, not a registered marketplace. No account installation was completed by the source check.

The [official packaging guide](https://developers.openai.com/plugins/build/plugins) describes local marketplace setup and the installed cache. The [plugin guide](https://learn.chatgpt.com/docs/plugins) describes installation and starting a new chat. These references were checked on 8 September 2026. Host availability and permissions still need an actual check in the selected account.

## Compare and test

Obtain the installed directory from the host; do not guess a cache path or scan unrelated plugin installations. Compare that copy:

```bash
python3 /path/to/spec-loop/scripts/install_check.py --root /path/to/spec-loop --installed-root /actual/installed/copy
```

Matching payload files return `matches-source`. A Codex `+codex.*` cachebuster is normalized; other manifest changes, engine changes and payload differences remain visible. A missing required file fails. Use `--expected-digest` with the source payload digest from a trusted prior check when you need to detect a changed source itself. The comparator does not change or refresh the installed copy.

Start a new host chat. Request: “Use Spec Loop to start a small product in this empty project.” Confirm the host selects Spec Loop, resolves a stage guide and its bundled script, and runs doctor/init against the intended Git project. Then use the focused product skill to create intent, link a change, align its scope and show the roadmap. Record actual host/version, plugin version, selected skill, resolved directory, command result and an evidence attachment. Use the [host acceptance cases](../../../docs/HOST_ACCEPTANCE.md). A direct skill-file read in a development chat is a local evaluation only.

For this repository's native pilot, CHG-006 covers the portable diagnostics release. CHG-HOST separately covers actual loading and the builder pilot. Keep CHG-HOST open until its cases are observed. Do not record a human outcome for an agent-only evaluation.

## Upgrade and recovery

Keep a trusted copy of the prior release and a project backup. Check the new source, use the host's supported update/reinstall flow, and compare the newly resolved copy. Start a new chat and rerun the host cases. Version changes invalidate current contract evidence; collect new evidence through the normal CLI. Do not change evidence hashes to make an upgrade pass.

If an installed copy differs, stop using its result as proof for the new version. Reinstall from the confirmed source and repeat the comparison. If rollback is needed, select the prior trusted plugin through the supported host flow and restore compatible project records from a backup. Product backup/restore changes intent history only; Git or a full project backup is needed for code and evidence. Historical release inspection remains separate from current readiness.

Return the source/copy result, observed host result, useful next action and any missing case. Do not claim installation merely because package checks pass.
