"""Canonical Eval Evidence bundle construction and verification.

Hashes establish byte identity. They do not establish trusted execution, physical
truth, complete provider disclosure, or publication rights.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from .models import EVIDENCE_STATUSES, EvidenceValue, FileReference, NormalizedRun, unavailable

BUNDLE_SCHEMA_VERSION = "eval-evidence.bundle/v0.1"
MANIFEST_SCHEMA_VERSION = "eval-evidence.instrument/v0.1"
RUN_SCHEMA_VERSION = "eval-evidence.run/v0.1"

STANDARD_INSTRUMENT_FIELDS = (
    "model_id",
    "model_provider",
    "response_model",
    "agent_name",
    "agent_version",
    "agent_binary_sha256",
    "harness_name",
    "harness_version",
    "harness_commit",
    "tools",
    "max_turns",
    "max_wall_time_s",
    "effort_or_thinking",
    "sampling_parameters",
    "system_prompt_sha256",
    "policy_profile_id",
    "task_checksum",
    "environment_image_digest",
    "verifier_digest",
    "network_policy",
)


class IntegrityError(ValueError):
    """Raised when an input or bundle violates the integrity contract."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_nonfinite_json(value: str) -> None:
    raise IntegrityError(f"Non-finite JSON number is not permitted: {value}")


def load_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"), parse_constant=_reject_nonfinite_json
        )
    except FileNotFoundError as exc:
        raise IntegrityError(f"Missing required file: {path}") from exc
    except UnicodeDecodeError as exc:
        raise IntegrityError(f"File is not valid UTF-8: {path}") from exc
    except json.JSONDecodeError as exc:
        raise IntegrityError(
            f"Invalid JSON in {path}: line {exc.lineno}, column {exc.colno}"
        ) from exc


def safe_run_path(root: Path, relative: str) -> Path:
    """Resolve a run-relative path while rejecting textual and symlink escapes."""
    relpath = Path(relative)
    if not relative or relpath.is_absolute() or ".." in relpath.parts:
        raise IntegrityError(f"Unsafe run-relative path: {relative!r}")
    run_root = root.resolve()
    resolved = (run_root / relpath).resolve()
    try:
        resolved.relative_to(run_root)
    except ValueError as exc:
        raise IntegrityError(f"Run path escapes root through symlink: {relative!r}") from exc
    return resolved


def file_record(root: Path, reference: FileReference) -> dict[str, Any]:
    path = safe_run_path(root, reference.path)
    present = path.is_file()
    if reference.required and not present:
        raise IntegrityError(f"Missing required run file: {reference.path}")
    return {
        "path": reference.path,
        "role": reference.role,
        "required": reference.required,
        "present": present,
        "sha256": sha256_file(path) if present else None,
        "bytes": path.stat().st_size if present else None,
    }


def evidence_dict(value: EvidenceValue) -> dict[str, Any]:
    if value.status not in EVIDENCE_STATUSES:
        raise IntegrityError(f"Invalid evidence status: {value.status!r}")
    if not value.source:
        raise IntegrityError("Evidence source must be non-empty")
    return value.as_dict()


def _instrument_manifest(run: NormalizedRun) -> dict[str, Any]:
    fields = dict(run.instrument)
    for name in STANDARD_INSTRUMENT_FIELDS:
        fields.setdefault(name, unavailable(f"{name} was not captured by the {run.adapter} adapter"))
    serialized = {name: evidence_dict(value) for name, value in sorted(fields.items())}
    counts = {status: 0 for status in sorted(EVIDENCE_STATUSES)}
    for item in serialized.values():
        counts[item["status"]] += 1
    available = sum(item["status"] != "unavailable" for item in serialized.values())
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "fields": serialized,
        "coverage": {
            "available_fraction": available / len(serialized),
            "field_count": len(serialized),
            "status_counts": counts,
        },
    }


def _unavailable_item_validity(task_id: str) -> dict[str, Any]:
    return {
        "status": "unavailable",
        "claims": {},
        "note": (
            f"No item-validity evidence was supplied for {task_id!r}; absence is not "
            "evidence that the item is valid, invalid, easy, or hard."
        ),
    }


def _unavailable_verifier_evidence() -> dict[str, Any]:
    return {
        "status": "unavailable",
        "claims": {},
        "note": "No reward-independent verifier evidence was supplied.",
    }


def build_bundle(run: NormalizedRun) -> dict[str, Any]:
    """Build one deterministic framework-neutral evidence bundle."""
    root = run.root.resolve()
    if not run.run_id or not run.task_id:
        raise IntegrityError("Normalized run requires non-empty run_id and task_id")
    records = [file_record(root, reference) for reference in run.references]
    if len({record["path"] for record in records}) != len(records):
        raise IntegrityError("Run references must use unique paths")

    payload: dict[str, Any] = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "source": {
            "adapter": run.adapter,
            "format": run.source_format,
            "run_id": run.run_id,
            "task_id": run.task_id,
            "task_revision": run.task_revision,
        },
        "inputs": records,
        "instrument_manifest": _instrument_manifest(run),
        "execution": {
            "started_at": run.started_at,
            "finished_at": run.finished_at,
            "metrics": {
                "input_tokens": run.metrics.get("input_tokens"),
                "cache_tokens": run.metrics.get("cache_tokens"),
                "output_tokens": run.metrics.get("output_tokens"),
                "cost_usd": run.metrics.get("cost_usd"),
            },
        },
        "outcome": {
            "reward": run.reward,
            "scores": run.scores,
            "termination_reason": run.termination_reason,
        },
        "item_validity": run.item_validity or _unavailable_item_validity(run.task_id),
        "verifier_evidence": run.verifier_evidence or _unavailable_verifier_evidence(),
        "attestation": {
            "type": "content-digest-only",
            "signature": None,
            "claim": (
                "The digest identifies these serialized claims; it is not a "
                "trusted-runner signature or proof of physical truth."
            ),
        },
        "extensions": run.extensions,
    }
    payload["bundle_digest"] = {
        "algorithm": "sha256",
        "value": sha256_bytes(canonical_json_bytes(payload)),
    }
    return payload


def iter_file_records(bundle: dict[str, Any]) -> Iterable[dict[str, Any]]:
    inputs = bundle.get("inputs")
    if isinstance(inputs, list):
        yield from (item for item in inputs if isinstance(item, dict))


def verify_referenced_files(bundle: dict[str, Any], run_root: Path) -> list[str]:
    """Re-hash local references without trusting paths from the bundle."""
    errors: list[str] = []
    seen: set[str] = set()
    for record in iter_file_records(bundle):
        relative = record.get("path")
        if not isinstance(relative, str) or not relative:
            errors.append("Referenced file record has no path")
            continue
        if relative in seen:
            errors.append(f"Duplicate referenced path: {relative}")
            continue
        seen.add(relative)
        try:
            path = safe_run_path(run_root, relative)
        except IntegrityError as exc:
            errors.append(str(exc))
            continue
        expected_present = bool(record.get("present"))
        actual_present = path.is_file()
        if expected_present != actual_present:
            errors.append(
                f"Referenced file presence mismatch for {relative}: "
                f"bundle={expected_present}, local={actual_present}"
            )
            continue
        if not expected_present:
            continue
        if record.get("bytes") != path.stat().st_size:
            errors.append(f"Referenced file size mismatch for {relative}")
        if record.get("sha256") != sha256_file(path):
            errors.append(f"Referenced file digest mismatch for {relative}")
    return errors


def verify_bundle(bundle: dict[str, Any], *, schema_path: Path | None = None) -> list[str]:
    """Return deterministic validation errors; an empty list means valid."""
    errors: list[str] = []
    if bundle.get("schema_version") != BUNDLE_SCHEMA_VERSION:
        errors.append(f"Unsupported schema_version: {bundle.get('schema_version')!r}")
    digest = bundle.get("bundle_digest")
    if not isinstance(digest, dict) or digest.get("algorithm") != "sha256" or not digest.get("value"):
        errors.append("bundle_digest must contain sha256 algorithm and value")
    else:
        payload = dict(bundle)
        payload.pop("bundle_digest", None)
        actual = sha256_bytes(canonical_json_bytes(payload))
        if actual != digest.get("value"):
            errors.append(
                f"Bundle digest mismatch: expected {digest.get('value')}, computed {actual}"
            )
    fields = bundle.get("instrument_manifest", {}).get("fields")
    if not isinstance(fields, dict):
        errors.append("instrument_manifest.fields must be an object")
    else:
        for name, item in fields.items():
            if (
                not isinstance(item, dict)
                or item.get("status") not in EVIDENCE_STATUSES
                or not item.get("source")
            ):
                errors.append(f"Invalid evidence field: instrument_manifest.fields.{name}")
        coverage = bundle.get("instrument_manifest", {}).get("coverage")
        expected_counts = {status: 0 for status in sorted(EVIDENCE_STATUSES)}
        for item in fields.values():
            if isinstance(item, dict) and item.get("status") in EVIDENCE_STATUSES:
                expected_counts[item["status"]] += 1
        expected_available = sum(
            count
            for status, count in expected_counts.items()
            if status != "unavailable"
        )
        expected_fraction = expected_available / len(fields) if fields else 0
        if not isinstance(coverage, dict):
            errors.append("instrument_manifest.coverage must be an object")
        else:
            recorded_field_count = coverage.get("field_count")
            if (
                not isinstance(recorded_field_count, int)
                or isinstance(recorded_field_count, bool)
                or recorded_field_count != len(fields)
            ):
                errors.append(
                    "Instrument coverage field_count mismatch: "
                    f"recorded={recorded_field_count!r}, computed={len(fields)}"
                )
            if coverage.get("status_counts") != expected_counts:
                errors.append(
                    "Instrument coverage status_counts mismatch: "
                    f"recorded={coverage.get('status_counts')!r}, "
                    f"computed={expected_counts!r}"
                )
            recorded_fraction = coverage.get("available_fraction")
            if (
                not isinstance(recorded_fraction, (int, float))
                or isinstance(recorded_fraction, bool)
                or recorded_fraction != expected_fraction
            ):
                errors.append(
                    "Instrument coverage available_fraction mismatch: "
                    f"recorded={recorded_fraction!r}, "
                    f"computed={expected_fraction!r}"
                )
    if schema_path is not None:
        try:
            import jsonschema
        except ImportError as exc:  # pragma: no cover
            raise IntegrityError("jsonschema is required for schema validation") from exc
        schema = load_json(schema_path)
        validator = jsonschema.Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(bundle), key=lambda e: tuple(str(p) for p in e.path)):
            location = ".".join(str(part) for part in error.path) or "$"
            errors.append(f"JSON Schema error at {location}: {error.message}")
    return errors
