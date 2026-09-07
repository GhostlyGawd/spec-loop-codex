# Offline product-file sync review

Prepared a conflict-free **pending update**, operation `SYNC-1e8f4b1a0ca246968f30ee82eb377a2a`, at 2026-09-07T16:56:21.242026+00:00. This is a synthetic, offline plan based only on the supplied fixture. No service was contacted, no remote write or confirmation occurred, and sync is not complete. The existing completed history is also labeled synthetic; it proves no real GitHub success.

Target: public repository `example/test`, repository ID `123`, branch `test-sync`, file `docs/product.json`. These identities are configured fixture claims, not independently verified service metadata.

| INI-001 field | Common baseline | Local intent | Saved snapshot | Proposed candidate |
|---|---|---|---|---|
| Horizon | now | next | now | next |
| Initiative owner | Builder | Builder | Remote planning owner | Remote planning owner |

The edits affect independent fields and merge without a conflict. Relative to the snapshot, the candidate changes the horizon from now to next. Upon a later authorized, successful confirmation, local initiative ownership would change from Builder to Remote planning owner. The local owner is still Builder today. OBJ-001's owner remains Builder. Every other product value is unchanged; serialized key order also changes in the generated exchange file. No scope or goal change is proposed.

The full candidate was reviewed for public disclosure: strategy, objectives, initiative, capacity and the single opportunity contain synthetic example values; OPP-001 is public and explicitly an assumption with no observation. `--reviewed-public` records this limited content review, not authorization to publish or accept inbound intent.

Snapshot observed time: 2026-09-07T16:55:16.035729+00:00. It passed the planner's 15-minute freshness, full-target, schema, and Git blob hash checks at preparation. It expires after 2026-09-07T17:10:16.035729+00:00. Its basis says “Synthetic branch/directory read confirms the fixture”; its branch SHA is `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`. Neither timestamp nor valid hash makes this a real remote read.

Expected local digest: `1b97c75849a072a82db9c2252d2e0363002b55925ef0179b0d0d82dcd1602e29`. Expected existing-file blob SHA: `9589a60ace17b791621a5d76a3ffbe812562d91f`. The action is update, not create or no-op. The saved common baseline has not advanced.

| Horizon | Initiative / intended result | Current delivery | Blocker / next decision | Freshness |
|---|---|---|---|---|
| Now | None | — | — | Local view checked 2026-09-07T16:56:21.302220+00:00 |
| Next | INI-001: add valid URLs without duplicates | CHG-001 reports 1/1 tasks done; candidate unverified; no release records; deployment unverified | Ready, verify and release gates require product scope contract review and alignment; resolve delivery gaps | Local view current at checked time; sync pending on synthetic snapshot |
| Later | None | — | — | Same local check |

Capacity is 2 available days, WIP limit 1, with a 1–2 day estimate for CHG-001. No initiatives are in Now, so current Now effort is zero. No application checks were run and no evidence was created. The example's acceptance, release, operations and person-observed outcome evidence remains uncollected; objective baseline and real-user outcome are unknown. Owner/horizon-only merging does not introduce a semantic binding change, but the pre-existing contract alignment gap still blocks delivery gates. Product-file sync cannot fix or prove these delivery or outcome facts.

Before real sync can be called complete:

1. Obtain authority for the real target, public write, and inbound owner decision; today's authority covers offline planning only. Verify repository metadata, ID, selected branch, relevant rules/instructions, access, and full target contents through GitHub MCP. Capture an actual fresh snapshot; the supplied synthetic record cannot serve as real execution evidence.
2. Re-read local product intent and compare its digest plus remote SHA/absence with the pending operation immediately before any authorized write. If either changed, cancel the old operation and replan from the fresh inputs. Preserve all newer decisions and resolve any new conflicts explicitly. Review the entire candidate again if it changes. Do not execute this fixture request on assumed authority.
3. If the reviewed operation is still valid and authorized, use its exact existing-file update request and observed blob SHA. On a timeout, read the target before retrying; a returned commit ID alone is insufficient.
4. Fetch the complete target after the write and save a real fresh read-back snapshot. Only a matching candidate read-back can support `github confirm`. Confirmation would apply the inbound owner decision and advance the common baseline. The current planning-only authority must not be reused to authorize that intent mutation; reprepare under the proper authority if needed. If local intent changed after preparation, preserve it and cancel/replan for reconciliation.
5. Verify there is no unresolved pending/reconciliation state and report the actual remote checked time. Freshness lasts 15 minutes, and this workflow has no background synchronization. Contract alignment and evidence work remain a separate delivery task.

Only `.spec-loop/github/state.json` (pending planning state), `.spec-loop/product/roadmap.json` (derived view), and this report were written. Hash checks confirmed product intent/history, contract, code, project/checkpoint state, input snapshot and existing artifact files stayed unchanged.

The exact generated request below is for review only and has not been executed. Its content is the complete proposed exchange file, containing exactly schema_version and product.

```json
{
  "tool": "github_update_file",
  "arguments": {
    "repository_full_name": "example/test",
    "branch": "test-sync",
    "path": "docs/product.json",
    "content": "{\n  \"schema_version\": 1,\n  \"product\": {\n    \"capacity\": {\n      \"wip_limit\": 1,\n      \"available_days\": 2,\n      \"estimates\": [\n        {\n          \"change\": \"CHG-001\",\n          \"low_days\": 1,\n          \"high_days\": 2\n        }\n      ]\n    },\n    \"initiatives\": [\n      {\n        \"changes\": [\n          \"CHG-001\"\n        ],\n        \"confidence\": \"low\",\n        \"date\": {\n          \"kind\": \"none\",\n          \"value\": \"\"\n        },\n        \"depends_on\": [],\n        \"horizon\": \"next\",\n        \"id\": \"INI-001\",\n        \"non_goals\": [\n          \"Persistence\"\n        ],\n        \"objectives\": [\n          \"OBJ-001\"\n        ],\n        \"opportunities\": [\n          \"OPP-001\"\n        ],\n        \"owner\": \"Remote planning owner\",\n        \"partial_release\": \"all_required\",\n        \"priority_reason\": \"Small first useful result\",\n        \"review_trigger\": \"After the first real task observation\",\n        \"risk\": \"low\",\n        \"scope\": \"Add valid URLs without duplicates\",\n        \"status\": \"active\",\n        \"title\": \"Local URL collection\"\n      }\n    ],\n    \"objectives\": [\n      {\n        \"id\": \"OBJ-001\",\n        \"title\": \"Save a URL once\",\n        \"metric\": \"Task completion\",\n        \"baseline\": \"Unknown\",\n        \"target\": \"One person completes the task\",\n        \"cohort\": \"No participants yet\",\n        \"window\": \"After release\",\n        \"guardrails\": [\n          \"No network calls\"\n        ],\n        \"owner\": \"Builder\"\n      }\n    ],\n    \"opportunities\": [\n      {\n        \"id\": \"OPP-001\",\n        \"title\": \"Collect a link\",\n        \"source\": \"Synthetic assumption\",\n        \"observed_at\": \"No observation\",\n        \"evidence\": \"assumption\",\n        \"privacy\": \"public\",\n        \"status\": \"new\",\n        \"experiment\": \"Observe a person use the released artifact\",\n        \"stop_rule\": \"Reconsider if unusable\",\n        \"objectives\": [\n          \"OBJ-001\"\n        ]\n      }\n    ],\n    \"strategy\": {\n      \"audience\": \"Local example user\",\n      \"problem\": \"Collect URLs once\",\n      \"positioning\": \"Synthetic teaching fixture\",\n      \"business_model\": \"No commercial claim\",\n      \"constraints\": [],\n      \"non_goals\": [],\n      \"review_trigger\": \"Review before committing implementation\"\n    }\n  }\n}\n",
    "message": "Sync product intent SYNC-1e8f4b1a0ca246968f30ee82eb377a2a",
    "sha": "9589a60ace17b791621a5d76a3ffbe812562d91f"
  },
  "before_write": "Fetch the target again. If it differs, cancel/replan; after a timeout, compare remote content before any retry."
}
```
