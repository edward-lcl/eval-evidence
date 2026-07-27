"""Input adapters for generic Eval Evidence manifests and Harbor trial directories."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from .core import IntegrityError, RUN_SCHEMA_VERSION, load_json, safe_run_path
from .models import EvidenceValue, FileReference, NormalizedRun, derived, observed, unavailable

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


def _reward(result: dict[str, Any]) -> Any:
    rewards = _get(result, "verifier_result", "rewards")
    if not isinstance(rewards, dict):
        return None
    return rewards.get("reward", rewards or None)


def _evidence_claim(value: Any, default_source: str) -> EvidenceValue:
    if isinstance(value, dict) and {"value", "status", "source"}.issubset(value):
        return EvidenceValue(
            value.get("value"),
            str(value.get("status")),
            str(value.get("source")),
            value.get("note"),
        )
    return observed(value, default_source)


def _claims(document: Any, default_source: str) -> dict[str, dict[str, Any]]:
    if not isinstance(document, dict):
        return {}
    return {
        str(name): _evidence_claim(value, f"{default_source}:{name}").as_dict()
        for name, value in sorted(document.items())
    }


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
                instrument[name] = observed(value, f"{GENERIC_MANIFEST}:instrument.{name}")
            elif isinstance(declaration, dict):
                instrument[name] = EvidenceValue(
                    value,
                    str(declaration.get("status", "observed")),
                    str(declaration.get("source", f"{GENERIC_MANIFEST}:instrument.{name}")),
                    declaration.get("note"),
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
        kwargs = agent_config.get("kwargs") if isinstance(agent_config.get("kwargs"), dict) else {}
        environment = config.get("environment") if isinstance(config.get("environment"), dict) else {}
        task_config = config.get("task") if isinstance(config.get("task"), dict) else {}
        verifier_config = config.get("verifier") if isinstance(config.get("verifier"), dict) else {}
        model_name = model_info.get("name") or agent_config.get("model_name") or _get(trajectory, "agent", "model_name")
        effort = _first(kwargs, "effort", "thinking", "reasoning_effort", "thinking_budget")
        sampling_names = (
            "temperature", "top_p", "top_k", "seed", "max_tokens",
            "frequency_penalty", "presence_penalty", "stop_sequences",
        )
        sampling = {name: kwargs[name] for name in sampling_names if kwargs.get(name) is not None}
        tools = {
            "skills": agent_config.get("skills") or [],
            "mcp_servers": agent_config.get("mcp_servers") or [],
        }
        instrument = {
            "model_id": observed(model_name, "Harbor result/config/trajectory"),
            "model_provider": observed(model_info.get("provider"), "Harbor result.json:agent_info.model_info.provider"),
            "agent_name": observed(agent_info.get("name") or _get(trajectory, "agent", "name"), "Harbor result/trajectory"),
            "agent_version": observed(agent_info.get("version") or _get(trajectory, "agent", "version"), "Harbor result/trajectory"),
            "harness_name": derived("harbor", "recognized Harbor trial layout"),
            "tools": derived(tools, "Harbor config.json:agent", "Configured tools may omit provider-side effective definitions"),
            "max_turns": observed(_first(kwargs, "max_turns", "max_steps"), "Harbor config.json:agent.kwargs"),
            "max_wall_time_s": observed(_first(agent_config, "override_timeout_sec", "max_timeout_sec"), "Harbor config.json:agent"),
            "effort_or_thinking": observed(effort, "Harbor config.json:agent.kwargs"),
            "sampling_parameters": observed(sampling or None, "Harbor config.json:agent.kwargs"),
            "task_checksum": observed(result.get("task_checksum"), "Harbor result.json:task_checksum"),
            "network_policy": derived(
                {"extra_allowed_hosts": environment.get("extra_allowed_hosts") or []},
                "Harbor config.json:environment.extra_allowed_hosts",
                "Configuration is not proof of effective enforcement",
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
        agent_result = result.get("agent_result") if isinstance(result.get("agent_result"), dict) else {}
        final_metrics = trajectory.get("final_metrics") if isinstance(trajectory.get("final_metrics"), dict) else {}
        rewards = _get(result, "verifier_result", "rewards")
        verifier_evidence = {
            "status": "run_outputs_only",
            "claims": {
                "raw_reward": observed(_reward(result), "Harbor result.json:verifier_result.rewards").as_dict(),
                "configured_verifier": observed(verifier_config or None, "Harbor config.json:verifier").as_dict(),
            },
            "note": "Reward is a reported outcome, not reward-independent proof of correctness.",
        }
        return NormalizedRun(
            root=root,
            adapter=self.name,
            source_format="harbor-trial-directory",
            run_id=str(run_id),
            task_id=task_id,
            task_revision=task_config.get("git_commit_id") or task_config.get("ref"),
            references=references,
            instrument=instrument,
            started_at=result.get("started_at"),
            finished_at=result.get("finished_at"),
            metrics={
                "input_tokens": agent_result.get("n_input_tokens", final_metrics.get("total_prompt_tokens")),
                "cache_tokens": agent_result.get("n_cache_tokens", final_metrics.get("total_cached_tokens")),
                "output_tokens": agent_result.get("n_output_tokens", final_metrics.get("total_completion_tokens")),
                "cost_usd": agent_result.get("cost_usd", final_metrics.get("total_cost_usd")),
            },
            reward=_reward(result),
            scores=rewards,
            termination_reason=str(_get(result, "exception_info", "exception_type") or "completed"),
            verifier_evidence=verifier_evidence,
            extensions={
                "harbor": {
                    "trajectory_schema_version": trajectory.get("schema_version"),
                    "trajectory_session_id": trajectory.get("session_id") or trajectory.get("trajectory_id"),
                    "trajectory_step_count": len(trajectory.get("steps") or []) if isinstance(trajectory.get("steps"), list) else None,
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
