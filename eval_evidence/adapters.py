"""Input adapters for generic Eval Evidence manifests and Harbor trial directories."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from .core import (
    IntegrityError,
    RUN_SCHEMA_VERSION,
    canonical_json_bytes,
    load_json,
    safe_run_path,
    sha256_bytes,
)
from .models import (
    EVIDENCE_STATUSES,
    EvidenceValue,
    FileReference,
    NormalizedRun,
    derived,
    observed,
    operator_asserted,
    unavailable,
)

GENERIC_MANIFEST = "eval-run.json"
RUN_SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "eval-evidence-run-v0.1.schema.json"


class RunAdapter(Protocol):
    name: str

    def detect(self, path: Path) -> int: ...
    def discover(self, path: Path) -> list[Path]: ...
    def load(self, path: Path) -> NormalizedRun: ...


def _get(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _first(mapping: dict[str, Any], *names: str) -> Any:
    for name in names:
        if mapping.get(name) is not None:
            return mapping[name]
    return None


def _declared_evidence(
    value: Any,
    status: Any,
    source: Any,
    note: Any = None,
    *,
    location: str,
) -> EvidenceValue:
    """Validate the value/status boundary shared by declared evidence inputs."""
    normalized_status = str(status)
    if normalized_status not in EVIDENCE_STATUSES:
        raise IntegrityError(f"Invalid evidence status at {location}: {status!r}")
    if not isinstance(source, str) or not source:
        raise IntegrityError(f"Evidence source must be non-empty at {location}")
    if (normalized_status == "unavailable") != (value is None):
        raise IntegrityError(
            f"Contradictory provenance at {location}: status {normalized_status!r} "
            f"requires value {'null' if normalized_status == 'unavailable' else 'non-null'}"
        )
    return EvidenceValue(value, normalized_status, source, note)


def _candidate(source: str, value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    return {"source": source, "value": value}


def _task_identity_candidate(source: str, value: Any) -> dict[str, Any] | None:
    """Represent a Harbor task identity without copying private local paths."""
    if not isinstance(value, dict):
        return None
    if isinstance(value.get("name"), str):
        kind = "package"
        name = (
            f"{value['org']}/{value['name']}"
            if isinstance(value.get("org"), str)
            else value["name"]
        )
        identity = {"name": name, "ref": value.get("ref")}
    elif isinstance(value.get("path"), str):
        kind = "git" if value.get("git_url") else "local"
        name = Path(value["path"]).name
        identity = {
            key: value.get(key)
            for key in ("path", "git_url", "git_commit_id")
            if value.get(key) is not None
        }
    else:
        return None
    return {
        "source": source,
        "value": {
            "kind": kind,
            "name": name,
            "identity_sha256": sha256_bytes(canonical_json_bytes(identity)),
        },
    }


def _resolve_candidates(
    candidates: list[dict[str, Any] | None],
    *,
    field: str,
    normalize: Callable[[Any], Any] | None = None,
) -> tuple[Any, dict[str, Any] | None]:
    """Return one value or a structured conflict without silently choosing."""
    present = [candidate for candidate in candidates if candidate is not None]
    if not present:
        return None, None
    normalize = normalize or (lambda value: value)
    distinct = {
        canonical_json_bytes(normalize(candidate["value"])) for candidate in present
    }
    if len(distinct) == 1:
        return present[0]["value"], None
    return None, {
        "field": field,
        "resolution": "unavailable",
        "candidates": present,
        "note": "Retained Harbor sources disagree; no precedence winner was selected.",
    }


def _reward(result: dict[str, Any]) -> Any:
    rewards = _get(result, "verifier_result", "rewards")
    if not isinstance(rewards, dict):
        return None
    return rewards.get("reward", rewards or None)


def _evidence_claim(value: Any, default_source: str) -> EvidenceValue:
    if isinstance(value, dict) and {"value", "status", "source"}.issubset(value):
        return _declared_evidence(
            value.get("value"),
            value.get("status"),
            value.get("source"),
            value.get("note"),
            location=default_source,
        )
    return operator_asserted(value, default_source)


def _claims(document: Any, default_source: str) -> dict[str, dict[str, Any]]:
    if not isinstance(document, dict):
        return {}
    return {
        str(name): _evidence_claim(value, f"{default_source}:{name}").as_dict()
        for name, value in sorted(document.items())
    }


def _harbor_agent_timeout(
    config: dict[str, Any],
    agent_config: dict[str, Any],
    agent_result: dict[str, Any],
) -> tuple[EvidenceValue, dict[str, Any]]:
    """Resolve Harbor's agent budget as ``min(base, cap) * multiplier``.

    This mirrors Harbor ``Trial._compute_agent_timeout_sec`` and
    ``Trial._resolve_timeout_sec``. The trial config only contains an agent timeout
    base when ``agent.override_timeout_sec`` is set; the task-defined base is not
    serialized into the per-trial ``config.json`` consumed by this adapter.
    """
    override_timeout_sec = agent_config.get("override_timeout_sec")
    base_sec = override_timeout_sec or None
    cap_sec = agent_config.get("max_timeout_sec")
    agent_multiplier = config.get("agent_timeout_multiplier")
    global_multiplier = config.get("timeout_multiplier")
    if agent_multiplier is not None:
        multiplier = agent_multiplier
        multiplier_source = "Harbor config.json:agent_timeout_multiplier"
    elif global_multiplier is not None:
        multiplier = global_multiplier
        multiplier_source = "Harbor config.json:timeout_multiplier"
    else:
        multiplier = 1.0
        multiplier_source = "Harbor TrialConfig default timeout_multiplier"

    timeout = {
        "base_sec": base_sec,
        "base_source": (
            "Harbor config.json:agent.override_timeout_sec" if base_sec is not None else None
        ),
        "cap_sec": cap_sec,
        "multiplier": multiplier,
        "multiplier_source": multiplier_source,
        "effective_sec": None,
        "resolution": "unresolved",
    }
    if base_sec is not None:
        capped_base = min(base_sec, cap_sec) if cap_sec else base_sec
        effective_sec = capped_base * multiplier
        timeout["effective_sec"] = effective_sec
        timeout["resolution"] = "computed"
        return (
            derived(
                effective_sec,
                "Harbor config.json:agent.override_timeout_sec, "
                "agent.max_timeout_sec, agent_timeout_multiplier/timeout_multiplier",
                "Effective agent budget per Harbor min(base, cap) * multiplier",
            ),
            timeout,
        )

    legacy_timeout_sec = agent_result.get("timeout_sec")
    if legacy_timeout_sec is not None:
        timeout["effective_sec"] = legacy_timeout_sec
        timeout["resolution"] = "legacy_recorded"
        return (
            observed(
                legacy_timeout_sec,
                "Harbor result.json:agent_result.timeout_sec",
                "Legacy recorded effective budget; multiplier was not reapplied",
            ),
            timeout,
        )

    return (
        unavailable(
            "Agent timeout base lives in the task definition "
            "(task config agent.timeout_sec), not the trial config.json"
        ),
        timeout,
    )


class GenericManifestAdapter:
    """Adapter for the small, framework-neutral ``eval-run.json`` contract."""

    name = "generic"

    def detect(self, path: Path) -> int:
        return 100 if (path / GENERIC_MANIFEST).is_file() else 0

    def discover(self, path: Path) -> list[Path]:
        path = path.resolve()
        if self.detect(path):
            return [path]
        if not path.is_dir():
            return []
        return sorted({candidate.parent for candidate in path.rglob(GENERIC_MANIFEST)})

    def load(self, path: Path) -> NormalizedRun:
        root = path.resolve()
        manifest_path = safe_run_path(root, GENERIC_MANIFEST)
        document = load_json(manifest_path)
        if not isinstance(document, dict):
            raise IntegrityError(f"{GENERIC_MANIFEST} must be a JSON object")
        try:
            import jsonschema
        except ImportError as exc:  # pragma: no cover
            raise IntegrityError("jsonschema is required to validate generic manifests") from exc
        validator = jsonschema.Draft202012Validator(load_json(RUN_SCHEMA_PATH))
        manifest_errors = sorted(
            validator.iter_errors(document), key=lambda error: tuple(str(part) for part in error.path)
        )
        if manifest_errors:
            error = manifest_errors[0]
            location = ".".join(str(part) for part in error.path) or "$"
            raise IntegrityError(f"Generic manifest schema error at {location}: {error.message}")
        if document.get("schema_version") != RUN_SCHEMA_VERSION:
            raise IntegrityError(
                f"Unsupported generic manifest schema_version: {document.get('schema_version')!r}"
            )
        run = document.get("run")
        outcome = document.get("outcome")
        if not isinstance(run, dict) or not isinstance(outcome, dict):
            raise IntegrityError(f"{GENERIC_MANIFEST} requires run and outcome objects")
        run_id = run.get("id")
        task_id = run.get("task_id")
        if not isinstance(run_id, str) or not run_id or not isinstance(task_id, str) or not task_id:
            raise IntegrityError(f"{GENERIC_MANIFEST} requires non-empty run.id and run.task_id")

        references = [FileReference(GENERIC_MANIFEST, "manifest", True)]
        for index, item in enumerate(document.get("references") or []):
            if not isinstance(item, dict):
                raise IntegrityError(f"references[{index}] must be an object")
            relative = item.get("path")
            role = item.get("role")
            if not isinstance(relative, str) or not relative or not isinstance(role, str) or not role:
                raise IntegrityError(f"references[{index}] requires non-empty path and role")
            references.append(FileReference(relative, role, bool(item.get("required", True))))

        instrument_doc = document.get("instrument") or {}
        if not isinstance(instrument_doc, dict):
            raise IntegrityError("instrument must be an object")
        provenance = document.get("provenance") or {}
        if not isinstance(provenance, dict):
            raise IntegrityError("provenance must be an object")
        extra_provenance = sorted(set(provenance).difference(instrument_doc))
        if extra_provenance:
            raise IntegrityError(
                f"provenance names fields absent from instrument: {extra_provenance}"
            )
        instrument: dict[str, EvidenceValue] = {}
        for name, value in instrument_doc.items():
            declaration = provenance.get(name)
            if declaration is None:
                instrument[name] = operator_asserted(
                    value, f"{GENERIC_MANIFEST}:instrument.{name}"
                )
            elif isinstance(declaration, dict):
                instrument[name] = _declared_evidence(
                    value,
                    declaration.get("status"),
                    declaration.get("source"),
                    declaration.get("note"),
                    location=f"provenance.{name}",
                )
            else:
                raise IntegrityError(f"provenance.{name} must be an object")

        metrics = document.get("metrics") or {}
        if not isinstance(metrics, dict):
            raise IntegrityError("metrics must be an object")
        item_doc = document.get("item_validity")
        verifier_doc = document.get("verifier_evidence")
        item_validity = None
        if isinstance(item_doc, dict):
            item_validity = {
                "status": item_doc.get("status", "reported"),
                "claims": _claims(item_doc.get("claims"), f"{GENERIC_MANIFEST}:item_validity.claims"),
                "note": item_doc.get("note"),
            }
        verifier_evidence = None
        if isinstance(verifier_doc, dict):
            verifier_evidence = {
                "status": verifier_doc.get("status", "reported"),
                "claims": _claims(verifier_doc.get("claims"), f"{GENERIC_MANIFEST}:verifier_evidence.claims"),
                "note": verifier_doc.get("note"),
            }
        extensions = document.get("extensions") or {}
        if not isinstance(extensions, dict):
            raise IntegrityError("extensions must be an object")

        return NormalizedRun(
            root=root,
            adapter=self.name,
            source_format=RUN_SCHEMA_VERSION,
            run_id=run_id,
            task_id=task_id,
            task_revision=run.get("task_revision"),
            references=references,
            instrument=instrument,
            started_at=run.get("started_at"),
            finished_at=run.get("finished_at"),
            metrics=metrics,
            reward=outcome.get("reward"),
            scores=outcome.get("scores"),
            termination_reason=str(outcome.get("termination_reason") or "completed"),
            item_validity=item_validity,
            verifier_evidence=verifier_evidence,
            extensions=extensions,
        )


class HarborAdapter:
    """Adapter for Harbor's result/config/ATIF trajectory directory shape."""

    name = "harbor"
    required = ("result.json", "config.json", "agent/trajectory.json")
    KNOWN_TRAJECTORY_SCHEMA_VERSIONS: frozenset[str] = frozenset(
        {"ATIF-v1.5", "ATIF-v1.6", "ATIF-v1.7"}
    )

    def detect(self, path: Path) -> int:
        return 80 if all((path / relative).is_file() for relative in self.required) else 0

    def discover(self, path: Path) -> list[Path]:
        path = path.resolve()
        if self.detect(path):
            return [path]
        if not path.is_dir():
            return []
        return sorted(
            {
                candidate.parent
                for candidate in path.rglob("result.json")
                if self.detect(candidate.parent)
            }
        )

    def load(self, path: Path) -> NormalizedRun:
        root = path.resolve()
        for relative in self.required:
            safe_run_path(root, relative)
        result = load_json(safe_run_path(root, "result.json"))
        config = load_json(safe_run_path(root, "config.json"))
        trajectory = load_json(safe_run_path(root, "agent/trajectory.json"))
        if not all(isinstance(value, dict) for value in (result, config, trajectory)):
            raise IntegrityError("Harbor result, config, and trajectory must be JSON objects")
        task_id = result.get("task_name")
        run_id = result.get("trial_name") or result.get("id") or root.name
        if not isinstance(task_id, str) or not task_id:
            raise IntegrityError("Harbor result.json requires a non-empty task_name")

        agent_info = result.get("agent_info") if isinstance(result.get("agent_info"), dict) else {}
        model_info = agent_info.get("model_info") if isinstance(agent_info.get("model_info"), dict) else {}
        agent_config = config.get("agent") if isinstance(config.get("agent"), dict) else {}
        agent_result = result.get("agent_result") if isinstance(result.get("agent_result"), dict) else {}
        result_config = result.get("config") if isinstance(result.get("config"), dict) else {}
        result_agent_config = (
            result_config.get("agent")
            if isinstance(result_config.get("agent"), dict)
            else {}
        )
        kwargs = agent_config.get("kwargs") if isinstance(agent_config.get("kwargs"), dict) else {}
        environment = config.get("environment") if isinstance(config.get("environment"), dict) else {}
        task_config = config.get("task") if isinstance(config.get("task"), dict) else {}
        verifier_config = config.get("verifier") if isinstance(config.get("verifier"), dict) else {}
        source_conflicts: dict[str, dict[str, Any]] = {}

        def resolve(
            field: str,
            candidates: list[dict[str, Any] | None],
            *,
            normalize: Callable[[Any], Any] | None = None,
        ) -> Any:
            value, conflict = _resolve_candidates(
                candidates, field=field, normalize=normalize
            )
            if conflict is not None:
                source_conflicts[field] = conflict
            return value

        result_model_name = model_info.get("name")
        config_model_name = agent_config.get("model_name")
        trajectory_model_name = _get(trajectory, "agent", "model_name")
        model_name = resolve(
            "instrument.model_id",
            [
                _candidate(
                    "Harbor result.json:agent_info.model_info.name",
                    result_model_name,
                ),
                _candidate("Harbor config.json:agent.model_name", config_model_name),
                _candidate(
                    "Harbor result.json:config.agent.model_name",
                    result_agent_config.get("model_name"),
                ),
                _candidate(
                    "Harbor agent/trajectory.json:agent.model_name",
                    trajectory_model_name,
                ),
            ],
            normalize=lambda value: value.split("/", 1)[-1]
            if isinstance(value, str)
            else value,
        )
        config_model_provider = (
            config_model_name.split("/", 1)[0]
            if isinstance(config_model_name, str) and "/" in config_model_name
            else None
        )
        result_config_model_name = result_agent_config.get("model_name")
        result_config_model_provider = (
            result_config_model_name.split("/", 1)[0]
            if isinstance(result_config_model_name, str)
            and "/" in result_config_model_name
            else None
        )
        model_provider = resolve(
            "instrument.model_provider",
            [
                _candidate(
                    "Harbor result.json:agent_info.model_info.provider",
                    model_info.get("provider"),
                ),
                _candidate(
                    "Harbor config.json:agent.model_name provider prefix",
                    config_model_provider,
                ),
                _candidate(
                    "Harbor result.json:config.agent.model_name provider prefix",
                    result_config_model_provider,
                ),
            ],
        )
        agent_name = resolve(
            "instrument.agent_name",
            [
                _candidate("Harbor result.json:agent_info.name", agent_info.get("name")),
                _candidate(
                    "Harbor result.json:config.agent.name",
                    result_agent_config.get("name"),
                ),
                _candidate(
                    "Harbor agent/trajectory.json:agent.name",
                    _get(trajectory, "agent", "name"),
                ),
            ],
        )
        agent_version = resolve(
            "instrument.agent_version",
            [
                _candidate(
                    "Harbor result.json:agent_info.version", agent_info.get("version")
                ),
                _candidate(
                    "Harbor agent/trajectory.json:agent.version",
                    _get(trajectory, "agent", "version"),
                ),
            ],
        )
        task_identity_candidates = [
            _task_identity_candidate(
                "Harbor result.json:task_id", result.get("task_id")
            ),
            _task_identity_candidate("Harbor config.json:task", task_config),
            _task_identity_candidate(
                "Harbor result.json:config.task", result_config.get("task")
            ),
        ]
        _, task_identity_conflict = _resolve_candidates(
            task_identity_candidates, field="source.task_identity"
        )
        if task_identity_conflict is not None:
            task_identity_conflict["resolution"] = "primary_retained_for_bundle_addressing"
            task_identity_conflict["note"] = (
                "Retained Harbor task identities disagree. result.json:task_name is "
                "retained only as the bundle address; comparison readiness is unresolved."
            )
            source_conflicts["source.task_identity"] = task_identity_conflict
        result_task_id = result.get("task_id") if isinstance(result.get("task_id"), dict) else {}
        result_task_revision = result_task_id.get("git_commit_id") or result_task_id.get("ref")
        result_config_task = (
            result_config.get("task")
            if isinstance(result_config.get("task"), dict)
            else {}
        )
        task_revision = resolve(
            "source.task_revision",
            [
                _candidate("Harbor result.json:task_id revision", result_task_revision),
                _candidate(
                    "Harbor config.json:task revision",
                    task_config.get("git_commit_id") or task_config.get("ref"),
                ),
                _candidate(
                    "Harbor result.json:config.task revision",
                    result_config_task.get("git_commit_id")
                    or result_config_task.get("ref"),
                ),
            ],
        )
        effort = _first(kwargs, "effort", "thinking", "reasoning_effort", "thinking_budget")
        max_wall_time, timeout_components = _harbor_agent_timeout(
            config, agent_config, agent_result
        )
        sampling_names = (
            "temperature", "top_p", "top_k", "seed", "max_tokens",
            "frequency_penalty", "presence_penalty", "stop_sequences",
        )
        sampling = {name: kwargs[name] for name in sampling_names if kwargs.get(name) is not None}
        tools_config_present = "skills" in agent_config and "mcp_servers" in agent_config
        configured_skills = agent_config.get("skills")
        configured_mcp_servers = agent_config.get("mcp_servers")
        tools = None
        if (
            tools_config_present
            and isinstance(configured_skills, list)
            and isinstance(configured_mcp_servers, list)
        ):
            tools = {
                "skill_count": len(configured_skills),
                "skills_sha256": sha256_bytes(canonical_json_bytes(configured_skills)),
                "mcp_server_count": len(configured_mcp_servers),
                "mcp_servers_sha256": sha256_bytes(
                    canonical_json_bytes(configured_mcp_servers)
                ),
            }
        network_config_present = (
            "extra_allowed_hosts" in environment
            and "extra_allowed_hosts" in agent_config
        )
        network_policy = None
        if (
            network_config_present
            and isinstance(environment.get("extra_allowed_hosts"), list)
            and isinstance(agent_config.get("extra_allowed_hosts"), list)
        ):
            network_policy = {
                "extra_allowed_hosts": environment["extra_allowed_hosts"],
                "agent_extra_allowed_hosts": agent_config["extra_allowed_hosts"],
            }
        safe_verifier_config = {
            name: verifier_config[name]
            for name in ("disable", "override_timeout_sec", "max_timeout_sec")
            if verifier_config.get(name) is not None
        }
        instrument = {
            "model_id": observed(model_name, "consistent Harbor result/config/trajectory candidates"),
            "model_provider": observed(model_provider, "consistent Harbor result/config candidates"),
            "agent_name": observed(agent_name, "consistent Harbor result/trajectory candidates"),
            "agent_version": observed(agent_version, "consistent Harbor result/trajectory candidates"),
            "harness_name": derived("harbor", "recognized Harbor trial layout"),
            "tools": derived(
                tools,
                "Harbor config.json:agent.skills/mcp_servers",
                (
                    "Configured tools may omit provider-side effective definitions"
                    if tools is not None
                    else "One or both list keys were absent; producer version/default serialization cannot be established"
                ),
            ),
            "max_turns": observed(_first(kwargs, "max_turns", "max_steps"), "Harbor config.json:agent.kwargs"),
            "max_wall_time_s": max_wall_time,
            "effort_or_thinking": observed(effort, "Harbor config.json:agent.kwargs"),
            "sampling_parameters": observed(sampling or None, "Harbor config.json:agent.kwargs"),
            "task_checksum": observed(result.get("task_checksum"), "Harbor result.json:task_checksum"),
            "network_policy": derived(
                network_policy,
                "Harbor config.json:environment/agent.extra_allowed_hosts",
                (
                    "Configured layers are not proof of effective enforcement"
                    if network_policy is not None
                    else "One or both list keys were absent; producer version/default serialization cannot be established"
                ),
            ),
        }
        references = [
            FileReference("result.json", "result"),
            FileReference("config.json", "configuration"),
            FileReference("agent/trajectory.json", "trajectory"),
            FileReference("verifier/reward.txt", "verifier-output", False),
            FileReference("verifier/ctrf.json", "verifier-output", False),
            FileReference("verifier/test-stdout.txt", "verifier-output", False),
            FileReference("artifacts/manifest.json", "artifact-manifest", False),
        ]
        final_metrics = trajectory.get("final_metrics") if isinstance(trajectory.get("final_metrics"), dict) else {}
        rewards = _get(result, "verifier_result", "rewards")
        verifier_evidence = {
            "status": "run_outputs_only",
            "claims": {
                "raw_reward": observed(_reward(result), "Harbor result.json:verifier_result.rewards").as_dict(),
                "configured_verifier": observed(
                    safe_verifier_config or None,
                    "selected non-secret Harbor config.json:verifier fields",
                    "Environment, kwargs, import paths, and log filters are not copied",
                ).as_dict(),
            },
            "note": "Reward is a reported outcome, not reward-independent proof of correctness.",
        }
        trajectory_schema_version = trajectory.get("schema_version")
        trajectory_schema_recognized = (
            isinstance(trajectory_schema_version, str)
            and trajectory_schema_version in self.KNOWN_TRAJECTORY_SCHEMA_VERSIONS
        )
        metric_candidates = {
            "input_tokens": (
                agent_result.get("n_input_tokens"),
                final_metrics.get("total_prompt_tokens"),
            ),
            "cache_tokens": (
                agent_result.get("n_cache_tokens"),
                final_metrics.get("total_cached_tokens"),
            ),
            "output_tokens": (
                agent_result.get("n_output_tokens"),
                final_metrics.get("total_completion_tokens"),
            ),
            "cost_usd": (
                agent_result.get("cost_usd"),
                final_metrics.get("total_cost_usd"),
            ),
        }
        metric_sources = {
            "input_tokens": (
                "Harbor result.json:agent_result.n_input_tokens",
                "Harbor agent/trajectory.json:final_metrics.total_prompt_tokens",
            ),
            "cache_tokens": (
                "Harbor result.json:agent_result.n_cache_tokens",
                "Harbor agent/trajectory.json:final_metrics.total_cached_tokens",
            ),
            "output_tokens": (
                "Harbor result.json:agent_result.n_output_tokens",
                "Harbor agent/trajectory.json:final_metrics.total_completion_tokens",
            ),
            "cost_usd": (
                "Harbor result.json:agent_result.cost_usd",
                "Harbor agent/trajectory.json:final_metrics.total_cost_usd",
            ),
        }
        metrics = {
            name: resolve(
                f"execution.metrics.{name}",
                [
                    _candidate(metric_sources[name][0], values[0]),
                    _candidate(metric_sources[name][1], values[1]),
                ],
            )
            for name, values in metric_candidates.items()
        }

        return NormalizedRun(
            root=root,
            adapter=self.name,
            source_format="harbor-trial-directory",
            run_id=str(run_id),
            task_id=task_id,
            task_revision=task_revision,
            references=references,
            instrument=instrument,
            started_at=result.get("started_at"),
            finished_at=result.get("finished_at"),
            metrics=metrics,
            reward=_reward(result),
            scores=rewards,
            termination_reason=str(
                _get(result, "exception_info", "exception_type")
                or ("completed" if result.get("finished_at") is not None else "unavailable")
            ),
            verifier_evidence=verifier_evidence,
            extensions={
                "harbor": {
                    "adapter_compat": {
                        "trajectory_schema_version": trajectory_schema_version,
                        "recognized": trajectory_schema_recognized,
                        "tested_against": sorted(self.KNOWN_TRAJECTORY_SCHEMA_VERSIONS),
                    },
                    "timeout": timeout_components,
                    "trajectory_schema_version": trajectory_schema_version,
                    "trajectory_session_id": trajectory.get("session_id") or trajectory.get("trajectory_id"),
                    "trajectory_step_count": len(trajectory.get("steps") or []) if isinstance(trajectory.get("steps"), list) else None,
                    "source_conflicts": source_conflicts,
                }
            },
        )


ADAPTERS: tuple[RunAdapter, ...] = (GenericManifestAdapter(), HarborAdapter())


@dataclass(frozen=True)
class AdapterMatch:
    root: Path
    adapter: RunAdapter
    confidence: int


def discover_runs(path: Path, adapter_name: str = "auto") -> list[AdapterMatch]:
    """Discover deterministic runs and select exactly one highest-confidence adapter."""
    path = path.resolve()
    candidates = ADAPTERS if adapter_name == "auto" else tuple(a for a in ADAPTERS if a.name == adapter_name)
    if not candidates:
        raise IntegrityError(f"Unknown adapter {adapter_name!r}; choose auto, generic, or harbor")
    matches: dict[Path, AdapterMatch] = {}
    for adapter in candidates:
        for root in adapter.discover(path):
            confidence = adapter.detect(root)
            current = matches.get(root)
            if current is None or confidence > current.confidence:
                matches[root] = AdapterMatch(root, adapter, confidence)
            elif confidence == current.confidence and adapter.name != current.adapter.name:
                raise IntegrityError(
                    f"Ambiguous adapter detection for {root}: {current.adapter.name} and {adapter.name}"
                )
    if not matches:
        raise IntegrityError(
            f"No supported evaluation run found under {path}. Need {GENERIC_MANIFEST} "
            "or Harbor result.json + config.json + agent/trajectory.json"
        )
    return [matches[root] for root in sorted(matches)]
