# CHANGE-007: ChatGPT Work support

## Need and authority

The user builds in ChatGPT Work and requested compatibility there. Earlier setup guidance incorrectly made a Codex desktop handoff the next required action. The engine already runs without Codex; the missing parts are Work entry, resource packaging and persistence guidance.

## Change

- Keep the shared plugin format and native product engine.
- Add one self-contained personal-skill entry for Work, with the existing lifecycle resources.
- Package bounded committed resources with provenance; omit the plugin repository's root product state, CI and untracked files.
- Route Work setup and resume by actual execution, storage and connector access.
- Keep native roadmap refresh, authority and evidence rules unchanged.

## Acceptance

1. A bundle can execute doctor, acceptance, verification and roadmap commands from another working directory without Codex.
2. Resume from a restored project recomputes evidence; a changed source fails the current gate.
3. Export refuses overwrite, dirty tracked source, unsupported links and excessive payloads; untracked data is excluded.
4. The Work entry and all required resources are saved through the personal-skill mechanism when available; verify the saved resource paths.
5. Reports distinguish saved skill, observed Work command execution and fresh-chat automatic selection. No invented install or human outcome.

## Limits

This change does not publish a universal-directory listing, enable a new schedule, add unattended sync or prove user demand. Version 0.7 invalidates earlier current-engine evidence; frozen v0.6 releases remain historical records. Codex installation stays a separate optional host test.
