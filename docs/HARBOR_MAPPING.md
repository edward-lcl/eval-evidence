# Harbor adapter mapping review

This is the review surface for Terminal-Bench/Harbor maintainers. Rows marked
`real-trial` were confirmed on 2026-07-28 by running the protocol in `DOGFOOD.md`
against a private seven-trial genuine job and spot-checking source values, unavailable
fields, and optional-file absence. In the `verified?` column, `real-trial` means the
private execution review, `source-review` means comparison with current public Harbor
models, and `mixed` means both informed the row. This local review does not make G2 met:
regular CI
still needs an approved sanitized fixture or secure fixture access.

The reviewed trajectories declared `ATIF-v1.5` or `ATIF-v1.6`. The adapter recognizes
those versions plus current `ATIF-v1.7` for the small stable surface it reads: root
`agent`, `steps`, and `final_metrics`. Harbor's published trajectory documentation and
current `Trajectory` model list all three shapes, and v1.5/v1.6 changes are additive for
this surface. Other versions still produce a non-fatal compatibility warning.

This review also compared the adapter with Harbor's current public `TrialConfig`,
`TrialResult`, `Trajectory`, and `JobResult` models. That source review identifies gaps;
it is not a substitute for executing each current layout.

## Core run, outcome, and reference fields

| bundle field | source or behavior | status |
|---|---|---|
| `source.run_id` | `result.json:trial_name`, then `id`, then trial-directory name | raw identifier |
| `source.task_id` | `result.json:task_name`; a missing/empty value fails loading | raw identifier |
| `source.task_revision` | `config.json:task.git_commit_id`, then `.ref` | raw value or null |
| `execution.started_at` / `finished_at` | matching top-level `result.json` fields | raw values or null |
| `outcome.reward` | `verifier_result.rewards.reward`; otherwise the non-empty rewards mapping | raw value or null |
| `outcome.scores` | complete `verifier_result.rewards` mapping | raw value or null |
| `outcome.termination_reason` | `exception_info.exception_type`; otherwise `completed` only when `finished_at` is non-null; otherwise `unavailable` | raw value/derived finalization state |
| `item_validity` | no Harbor mapping in v0.2 | `unavailable` |
| `verifier_evidence.raw_reward` | same reported verifier reward, with observed provenance | reported run output, not independent correctness evidence |
| `verifier_evidence.configured_verifier` | selected `config.json:verifier` fields: `disable`, `override_timeout_sec`, `max_timeout_sec` | observed non-secret configuration subset or unavailable; env, kwargs, import paths, and log filters are not copied |
| required hashed references | `result.json`, `config.json`, `agent/trajectory.json` | bundle fails if any required reference is absent or differs at verification |
| optional hashed references | `verifier/reward.txt`, `verifier/ctrf.json`, `verifier/test-stdout.txt`, `artifacts/manifest.json` | presence and digest recorded; absence does not invalidate the bundle |
| not copied into bundle | trajectory, prompt, verifier logs, artifacts, credentials | only selected relative paths, sizes, and SHA-256 values are carried |

## Instrument fields

| bundle field | source JSON path | status | verified? |
|---|---|---|---|
| `model_id` | `result.json:agent_info.model_info.name`, then `config.json:agent.model_name`, then `agent/trajectory.json:agent.model_name` | observed when present | real-trial |
| `model_provider` | `result.json:agent_info.model_info.provider` | observed when present | real-trial |
| `response_model` | not mapped | unavailable | real-trial |
| `agent_name` | `result.json:agent_info.name`, then `agent/trajectory.json:agent.name` | observed when present | real-trial |
| `agent_version` | `result.json:agent_info.version`, then `agent/trajectory.json:agent.version` | observed when present | real-trial |
| `agent_binary_sha256` | not mapped | unavailable | real-trial |
| `harness_name` | recognized `result.json` + `config.json` + `agent/trajectory.json` layout | derived as `harbor` | real-trial |
| `harness_version` | not mapped | unavailable | real-trial |
| `harness_commit` | not mapped | unavailable | real-trial |
| `tools` | counts and canonical SHA-256 values of `config.json:agent.skills` and `.mcp_servers` lists | derived configured identities without copying paths, URLs, or names | mixed |
| `max_turns` | `config.json:agent.kwargs.max_turns`, then `.max_steps` | observed when present | real-trial |
| `max_wall_time_s` | when `config.json:agent.override_timeout_sec` supplies the base, computes `min(base, agent.max_timeout_sec or infinity) * multiplier`, where a non-null top-level `agent_timeout_multiplier` takes precedence over top-level `timeout_multiplier` (default `1.0`); when that base is absent, uses legacy `result.json:agent_result.timeout_sec` without reapplying a multiplier; a cap alone is never treated as a budget | derived for a computed effective budget, observed for a legacy recorded effective budget, otherwise unavailable because the task-defined base is outside trial `config.json` | mixed |
| `effort_or_thinking` | `config.json:agent.kwargs.effort`, `.thinking`, `.reasoning_effort`, then `.thinking_budget` | observed when present | real-trial |
| `sampling_parameters` | selected sampling keys under `config.json:agent.kwargs` | observed when non-empty | real-trial |
| `system_prompt_sha256` | not mapped | unavailable | real-trial |
| `policy_profile_id` | not mapped | unavailable | real-trial |
| `task_checksum` | `result.json:task_checksum` | observed when present | real-trial |
| `environment_image_digest` | not mapped | unavailable | real-trial |
| `verifier_digest` | not mapped | unavailable | real-trial |
| `network_policy` | `config.json:environment.extra_allowed_hosts` and `agent.extra_allowed_hosts` | derived configured layers, not enforcement proof | mixed |

The environment baseline is retained as `extra_allowed_hosts`; current Harbor's
agent-phase additions are retained separately as `agent_extra_allowed_hosts`. Keeping
the layers distinct avoids implying that configuration proves the effective merged
allowlist or enforcement.

The synthetic fixture deliberately places `override_timeout_sec` under `agent`, not
`verifier`. A verifier timeout is retained separately in
`verifier_evidence.claims.configured_verifier` and is not treated as an agent wall-time
budget.

`extensions.harbor.timeout` preserves the configured/resolution components without
changing the standard instrument denominator: `base_sec`, `base_source`, `cap_sec`,
`multiplier`, `multiplier_source`, `effective_sec`, and `resolution`. Resolution is
`computed`, `legacy_recorded`, or `unresolved`; absent components are `null`, never
infinity. The formula and top-level multiplier locations were source-reviewed against
local Harbor commit `9073b960dd739e0c28464d135217baa17a8d217b`; maintainers still need
to confirm the current-release contract and the task-config base source.

## Other review-sensitive mappings

| bundle field | source JSON path | status | verified? |
|---|---|---|---|
| `execution.metrics.input_tokens` | `result.json:agent_result.n_input_tokens`, then `agent/trajectory.json:final_metrics.total_prompt_tokens` when the first value is absent or null | raw value or null | real-trial |
| `execution.metrics.cache_tokens` | `result.json:agent_result.n_cache_tokens`, then `agent/trajectory.json:final_metrics.total_cached_tokens` when the first value is absent or null | raw value or null | real-trial |
| `execution.metrics.output_tokens` | `result.json:agent_result.n_output_tokens`, then `agent/trajectory.json:final_metrics.total_completion_tokens` when the first value is absent or null | raw value or null | real-trial |
| `execution.metrics.cost_usd` | `result.json:agent_result.cost_usd`, then `agent/trajectory.json:final_metrics.total_cost_usd` when the first value is absent or null | raw value or null | real-trial |
| `extensions.harbor.trajectory_step_count` | length of `agent/trajectory.json:steps` when it is an array | derived count or null | real-trial |
| `extensions.harbor.adapter_compat` | `agent/trajectory.json:schema_version` compared with adapter allowlist | derived compatibility signal | real-trial |

Harbor's current `AgentContext` defines `n_input_tokens` as total input **including**
cache tokens. Eval Evidence preserves that raw meaning and also records
`n_cache_tokens` separately; consumers must not add the two to compute total input.
Trajectory fallback totals retain ATIF's own field semantics and are used only when the
result-level value is absent or null.

Use `eval-evidence inspect PATH --adapter harbor --explain` to print every available
instrument field and its source string without writing a bundle.

## Layout support and known gaps

| Harbor surface | v0.2 behavior |
|---|---|
| Single-step trial `result.json` | Reads top-level `agent_result`, `verifier_result`, `exception_info`, and timestamps |
| Trial without `agent/trajectory.json` | Not detected; v0.2 cannot claim complete job coverage when an agent omits ATIF |
| Trial `config.json` | Reads selected task, agent, environment, and verifier configuration |
| ATIF v1.5–v1.7 | Reads root agent identity, step count, and final metric totals |
| Job directory | Discovers qualifying child trials deterministically; does not bundle the job-level files |
| Multi-step `step_results` | Not aggregated; top-level/trajectory fallbacks may be incomplete, so this layout is not yet supported for metric or outcome claims |
| Regraded trials | `source_trial` lineage is not mapped |
| Job stats/retries/cancellations | Not represented; v0.2 cannot establish campaign denominators or exclusions |
| Harbor version/commit | Unavailable because no mapped artifact establishes it |

These gaps are intentionally visible before Terminal-Bench/Harbor review. In
particular, a directory-wide `check` validates discovered qualifying trial envelopes;
it does not reconcile discovery with Harbor's job trial count, prove which trials formed
an aggregate score, or establish that two jobs are comparable.

Public Harbor references used for this source review:

- [Evals and job layout](https://www.harborframework.com/docs/run-jobs/run-evals)
- [ATIF format and supported versions](https://www.harborframework.com/docs/agents/trajectory-format)
- [`TrialResult` model](https://github.com/harbor-framework/harbor/blob/main/src/harbor/models/trial/result.py)
- [`JobResult` model](https://github.com/harbor-framework/harbor/blob/main/src/harbor/models/job/result.py)
