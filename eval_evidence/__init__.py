"""Eval Evidence: machine-checkable evidence for AI evaluation runs."""

__version__ = "0.2.0"

from .adapters import ADAPTERS, GenericManifestAdapter, HarborAdapter, discover_runs
from .core import (
    BUNDLE_SCHEMA_VERSION,
    MANIFEST_SCHEMA_VERSION,
    RUN_SCHEMA_VERSION,
    IntegrityError,
    build_bundle,
    canonical_json_bytes,
    verify_bundle,
    verify_referenced_files,
)
from .models import EvidenceValue, FileReference, NormalizedRun

__all__ = [
    "__version__",
    "ADAPTERS",
    "BUNDLE_SCHEMA_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "RUN_SCHEMA_VERSION",
    "EvidenceValue",
    "FileReference",
    "GenericManifestAdapter",
    "HarborAdapter",
    "IntegrityError",
    "NormalizedRun",
    "build_bundle",
    "canonical_json_bytes",
    "discover_runs",
    "verify_bundle",
    "verify_referenced_files",
]
