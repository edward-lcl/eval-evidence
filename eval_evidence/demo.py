"""Deterministic synthetic demos containing no benchmark or user data."""

from __future__ import annotations

import json
from pathlib import Path

from .core import RUN_SCHEMA_VERSION


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(payload)


def materialize_generic_demo(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=False)
    _write(root / "outputs" / "scores.json", {"accuracy": 0.75, "n": 4})
    _write(root / "logs" / "events.json", [{"event": "completed", "step": 4}])
    _write(
        root / "eval-run.json",
        {
            "schema_version": RUN_SCHEMA_VERSION,
            "run": {
                "id": "synthetic-run-001",
                "task_id": "synthetic-arithmetic",
                "task_revision": "demo-v1",
                "started_at": "2026-01-01T00:00:00Z",
                "finished_at": "2026-01-01T00:00:02Z",
            },
            "instrument": {
                "model_id": "synthetic-model",
                "model_provider": "example",
                "harness_name": "generic-demo",
                "harness_version": "1.0",
                "max_turns": 8,
                "sampling_parameters": {"temperature": 0, "seed": 7},
            },
            "provenance": {
                "model_id": {"status": "operator_asserted", "source": "demo fixture"},
                "model_provider": {"status": "operator_asserted", "source": "demo fixture"},
            },
            "metrics": {
                "input_tokens": 120,
                "cache_tokens": 0,
                "output_tokens": 24,
                "cost_usd": 0.001,
            },
            "outcome": {
                "reward": 0.75,
                "scores": {"accuracy": 0.75},
                "termination_reason": "completed",
            },
            "references": [
                {"path": "outputs/scores.json", "role": "score-output"},
                {"path": "logs/events.json", "role": "execution-log"},
                {"path": "optional/debug.txt", "role": "debug-log", "required": False},
            ],
            "item_validity": {
                "status": "reported",
                "claims": {
                    "oracle_check": {
                        "value": "pass",
                        "status": "operator_asserted",
                        "source": "demo fixture",
                    }
                },
                "note": "Synthetic demonstration only.",
            },
            "verifier_evidence": {
                "status": "reported",
                "claims": {
                    "score_file_present": {
                        "value": True,
                        "status": "derived",
                        "source": "outputs/scores.json",
                    }
                },
                "note": "No trusted runner or physical attestation.",
            },
            "extensions": {"example.org/demo": {"synthetic": True}},
        },
    )
    return root


def materialize_harbor_demo(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=False)
    _write(
        root / "result.json",
        {
            "id": "00000000-0000-0000-0000-000000000001",
            "task_name": "synthetic-harbor-task",
            "trial_name": "synthetic-harbor-task__demo",
            "task_checksum": "a" * 64,
            "started_at": "2026-01-01T00:00:00Z",
            "finished_at": "2026-01-01T00:00:02Z",
            "agent_info": {
                "name": "synthetic-agent",
                "version": "1.0",
                "model_info": {"name": "synthetic-model", "provider": "example"},
            },
            "agent_result": {"n_input_tokens": 10, "n_output_tokens": 5, "cost_usd": 0.001},
            "verifier_result": {"rewards": {"reward": 1.0}},
            "exception_info": None,
        },
    )
    _write(
        root / "config.json",
        {
            "task": {"path": "tasks/synthetic", "git_commit_id": "demo-v1"},
            "timeout_multiplier": 1.0,
            "agent_timeout_multiplier": 1.0,
            "agent": {
                "name": "synthetic-agent",
                "model_name": "example/synthetic-model",
                "override_timeout_sec": 60,
                "skills": [],
                "mcp_servers": [],
                "kwargs": {"max_turns": 8, "temperature": 0, "seed": 7},
            },
            "environment": {"type": "docker", "extra_allowed_hosts": []},
            "verifier": {"disable": False, "override_timeout_sec": 60},
        },
    )
    _write(
        root / "agent" / "trajectory.json",
        {
            "schema_version": "ATIF-v1.7",
            "session_id": "synthetic-session",
            "agent": {"name": "synthetic-agent", "version": "1.0", "model_name": "synthetic-model"},
            "steps": [{"step_id": 1, "source": "user", "message": "synthetic task"}],
            "final_metrics": {"total_prompt_tokens": 10, "total_completion_tokens": 5, "total_cost_usd": 0.001},
        },
    )
    (root / "verifier").mkdir()
    (root / "verifier" / "reward.txt").write_bytes(b"1\n")
    return root
