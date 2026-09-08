# Review health

Use this read-only check when a builder asks whether product reviews ran or whether the Work skill is current. The agent collects evidence and runs the command; the builder does not need a terminal.

```sh
python3 scripts/review_health.py --snapshot /path/observation.json --policy docs/review-health-policy.json --installed-bundle /actual/skill/bundle
```

Exit 0 means no attention condition in the checked dimensions; an omitted installed bundle is explicitly not checked. Exit 1 means attention is needed. Exit 2 means the observation cannot be evaluated. The script prints JSON and never fetches, dispatches, syncs, installs or repairs.

## Collect through GitHub MCP

Read the configured repository's default branch and current commit/tree, manifest version, and exact committed workflow. Confirm its only schedule is the policy's daily UTC cron with no timezone override. If not, stop with a configuration mismatch; do not copy policy values into an observation without reading the workflow.

Collect the complete main-branch run inventory using `/repos/OWNER/REPO/actions/runs?branch=main&per_page=100` and every page. Do not filter to successful events. Retain the API total_count, all unique run IDs, event, created_at, head_sha, head_branch, path, html_url, run_attempt, status, conclusion and repository.full_name. Set runs.scope to the actual queried repository and branch. For large histories, version 1 intentionally reports unverified if the bounded complete inventory cannot be collected. Do not falsely set total_count to the page length.

For the latest schedule created in the current daily slot and latest push/schedule/manual run on current main, collect complete jobs and artifacts inventories. Store each under details keyed by run ID, with jobs and artifacts API response envelopes. Preserve job attempt, commit, review steps, artifact expiry and workflow_run identity. Re-read the run identities and branch after collection; retry if the commit or latest attempt changed. Set observed_at to collection start in UTC. Finish within the policy's maximum age. An API error, denied path or incomplete page is unverified, not missing or success. Do not bypass connector restrictions.

The snapshot envelope is schema_version 1, observed_at, target, runs and details. Target contains repository, branch, workflow, cron, commit, tree and version from the actual reads. The saved technical observation in `.spec-loop/artifacts/health-observation.json` illustrates the format; it is historical evidence and must not be relabeled fresh. Jobs and artifact metadata are evidence of execution and upload, not downloaded artifact-byte verification.

## Interpret

Schedule status is waiting before the grace deadline, missed after the deadline without a matching event, queued/in_progress while active, failed for a completed unsuccessful run, unverified for incomplete proof, or passed. created_delay_seconds compares API creation with the nominal slot. It does not establish GitHub's delay cause or scheduler attribution across dates. A run created in a later daily slot cannot prove that an earlier slot executed. A passed run created after grace remains an attention condition. One pass never proves sustained reliability.

Current-commit review is separate: a scheduled review of an earlier main can pass while the latest main review is missing or failed. Installed status can be current, update-available, installed-ahead, source-differs, not-checked or unverified. Local payload checks cannot authenticate unsigned source declarations. Use trusted saved provenance and the supported skill update flow; never overwrite the installed copy from a background task.

## Unattended checks and safe sync

A separately configured ChatGPT task may collect these read-only observations and alert the owner on missing, failed, overdue, late or unverified reviews. A task must be actually created and read back before saying it is enabled. Its first future execution and sustained reliability require later evidence. Keep the GitHub schedule unchanged. With no scheduling capability, leave this as an on-demand check and state that limitation.

Roadmap refresh automatically recomputes delivery facts on resume and native writes. Remote intent sync stays agent-mediated: fetch fresh target-bound snapshots, preserve three-way conflicts, apply only authorized decisions, and confirm read-back before advancing the baseline. A watchdog does not mutate intent, sync baselines, code, permissions or schedules. The older demonstration adapter points at a different branch; do not silently retarget it.

GitHub documents possible schedule delay and dropped queued jobs in [workflow troubleshooting](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows). That general possibility does not diagnose this repository's observed delay.
