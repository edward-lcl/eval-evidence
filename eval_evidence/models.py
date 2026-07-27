"""Framework-neutral normalized run model used by Eval Evidence adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

EVIDENCE_STATUSES = {
    "observed",
    "derived",
    "operator_asserted",
    "provider_asserted",
    "unavailable",
}


@dataclass(frozen=True)
class EvidenceValue:
    value: Any
    status: str
    source: str
    note: str | None = None

    def as_dict(self) -> dict[str, Any]:
        item: dict[str, Any] = {
            "value": self.value,
            "status": self.status,
            "source": self.source,
        }
        if self.note:
            item["note"] = self.note
        return item


@dataclass(frozen=True)
class FileReference:
    path: str
    role: str
    required: bool = True


@dataclass
class NormalizedRun:
    root: Path
    adapter: str
    source_format: str
    run_id: str
    task_id: str
    task_revision: str | None = None
    references: list[FileReference] = field(default_factory=list)
    instrument: dict[str, EvidenceValue] = field(default_factory=dict)
    started_at: str | None = None
    finished_at: str | None = None
    metrics: dict[str, int | float | None] = field(default_factory=dict)
    reward: Any = None
    scores: Any = None
    termination_reason: str = "completed"
    item_validity: dict[str, Any] | None = None
    verifier_evidence: dict[str, Any] | None = None
    extensions: dict[str, Any] = field(default_factory=dict)


def observed(value: Any, source: str, note: str | None = None) -> EvidenceValue:
    if value is None:
        return EvidenceValue(None, "unavailable", "not captured", note or f"{source} was absent")
    return EvidenceValue(value, "observed", source, note)


def derived(value: Any, source: str, note: str | None = None) -> EvidenceValue:
    if value is None:
        return EvidenceValue(None, "unavailable", "not captured", note or f"{source} was absent")
    return EvidenceValue(value, "derived", source, note)


def unavailable(note: str) -> EvidenceValue:
    return EvidenceValue(None, "unavailable", "not captured", note)
