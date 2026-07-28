# Harbor adapter mapping review

This is the review surface for Terminal-Bench/Harbor maintainers. Rows marked
`real-trial` were confirmed on 2026-07-28 by running the protocol in `DOGFOOD.md`
against a private seven-trial genuine job and spot-checking source values, unavailable
fields, and optional-file absence. The only permitted values in the `verified?` column
are `inferred` and `real-trial`. This local review does not make G2 met: regular CI
still needs an approved sanitized fixture or secure fixture access.

The reviewed trajectories declared `ATIF-v1.5` or `ATIF-v1.6`, while the adapter's
recognized allowlist remains `ATIF-v1.7`. Both observed versions correctly emitted
non-fatal compatibility warnings and remain unrecognized pending a semantic shape
review; the local run did not widen the allowlist.

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
| `tools` | `config.json:agent.skills` and `config.json:agent.mcp_servers` | derived configured values | real-trial |
| `max_turns` | `config.json:agent.kwargs.max_turns`, then `.max_steps` | observed when present | real-trial |
| `max_wall_time_s` | `config.json:agent.override_timeout_sec`, then `.max_timeout_sec`, then `result.json:agent_result.timeout_sec` when configured values are absent or null | observed when present | real-trial |
| `effort_or_thinking` | `config.json:agent.kwargs.effort`, `.thinking`, `.reasoning_effort`, then `.thinking_budget` | observed when present | real-trial |
| `sampling_parameters` | selected sampling keys under `config.json:agent.kwargs` | observed when non-empty | real-trial |
| `system_prompt_sha256` | not mapped | unavailable | real-trial |
| `policy_profile_id` | not mapped | unavailable | real-trial |
| `task_checksum` | `result.json:task_checksum` | observed when present | real-trial |
| `environment_image_digest` | not mapped | unavailable | real-trial |
| `verifier_digest` | not mapped | unavailable | real-trial |
| `network_policy` | `config.json:environment.extra_allowed_hosts` | derived configured values, not enforcement proof | real-trial |

The synthetic fixture deliberately places `override_timeout_sec` under `agent`, not
`verifier`. A verifier timeout is retained separately in
`verifier_evidence.claims.configured_verifier` and is not treated as an agent wall-time
budget.

## Other review-sensitive mappings

| bundle field | source JSON path | status | verified? |
|---|---|---|---|
| `execution.metrics.input_tokens` | `result.json:agent_result.n_input_tokens`, then `agent/trajectory.json:final_metrics.total_prompt_tokens` when the first value is absent or null | raw value or null | real-trial |
| `execution.metrics.cache_tokens` | `result.json:agent_result.n_cache_tokens`, then `agent/trajectory.json:final_metrics.total_cached_tokens` when the first value is absent or null | raw value or null | real-trial |
| `execution.metrics.output_tokens` | `result.json:agent_result.n_output_tokens`, then `agent/trajectory.json:final_metrics.total_completion_tokens` when the first value is absent or null | raw value or null | real-trial |
| `execution.metrics.cost_usd` | `result.json:agent_result.cost_usd`, then `agent/trajectory.json:final_metrics.total_cost_usd` when the first value is absent or null | raw value or null | real-trial |
| `outcome.termination_reason` | `result.json:exception_info.exception_type`, otherwise `completed` | raw value/default | real-trial |
| `extensions.harbor.trajectory_step_count` | length of `agent/trajectory.json:steps` when it is an array | derived count or null | real-trial |
| `extensions.harbor.adapter_compat` | `agent/trajectory.json:schema_version` compared with adapter allowlist | derived compatibility signal | real-trial |

Use `eval-evidence inspect PATH --adapter harbor --explain` to print every available
instrument field and its source string without writing a bundle.
