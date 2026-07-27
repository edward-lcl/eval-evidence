#!/usr/bin/env python3
"""Audit Eval Evidence wheel/sdist scope and release metadata without publishing."""

from __future__ import annotations

import argparse
import email.parser
import json
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

PACKAGE = "eval-evidence"
VERSION = "0.1.0"
EXPECTED_SCHEMAS = {
    "eval-evidence-bundle-v0.1.schema.json",
    "eval-evidence-instrument-v0.1.schema.json",
    "eval-evidence-run-v0.1.schema.json",
    "otel-genai-crosswalk-v0.1.json",
}
FORBIDDEN_PARTS = {"paper", "derived", "sources", "trajectories", "prs", "site", ".git"}
FORBIDDEN_SUFFIXES = {".parquet", ".csv", ".jsonl", ".pdf", ".tex"}


def members(path: Path) -> list[str]:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            return sorted(name.rstrip("/") for name in archive.namelist() if not name.endswith("/"))
    if path.name.endswith(".tar.gz"):
        with tarfile.open(path, "r:gz") as archive:
            return sorted(item.name.rstrip("/") for item in archive.getmembers() if item.isfile())
    raise ValueError(f"unsupported archive: {path}")


def strip_sdist_root(items: list[str]) -> list[str]:
    roots = {PurePosixPath(item).parts[0] for item in items}
    if len(roots) != 1 or not next(iter(roots)).startswith("eval_evidence-"):
        raise ValueError(f"unexpected sdist root: {sorted(roots)}")
    return [str(PurePosixPath(*PurePosixPath(item).parts[1:])) for item in items]


def metadata(wheel: Path) -> email.message.Message:
    with zipfile.ZipFile(wheel) as archive:
        names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(names) != 1:
            raise ValueError(f"expected one METADATA member, found {names}")
        return email.parser.Parser().parsestr(archive.read(names[0]).decode("utf-8"))


def forbidden(items: list[str]) -> list[str]:
    return [
        item
        for item in items
        if FORBIDDEN_PARTS.intersection(PurePosixPath(item).parts)
        or PurePosixPath(item).suffix.lower() in FORBIDDEN_SUFFIXES
    ]


def audit(dist: Path) -> dict:
    wheels = sorted(dist.glob("eval_evidence-*.whl"))
    sdists = sorted(dist.glob("eval_evidence-*.tar.gz"))
    errors: list[str] = []
    if len(wheels) != 1 or len(sdists) != 1:
        return {
            "technical_valid": False,
            "authorized_for_distribution": False,
            "errors": [f"expected one wheel and one sdist; found {len(wheels)} and {len(sdists)}"],
        }
    wheel, sdist = wheels[0], sdists[0]
    wheel_items = members(wheel)
    sdist_items = strip_sdist_root(members(sdist))
    bad = forbidden(wheel_items) + forbidden(sdist_items)
    if bad:
        errors.append(f"forbidden data/repository members: {bad}")
    wheel_schemas = {
        PurePosixPath(item).name
        for item in wheel_items
        if item.startswith("eval_evidence/schemas/") and item.endswith(".json")
    }
    if wheel_schemas != EXPECTED_SCHEMAS:
        errors.append(f"wheel schema mismatch: {sorted(wheel_schemas ^ EXPECTED_SCHEMAS)}")
    required_sdist = {"LICENSE", "NOTICE", "SECURITY.md", "README.md", "action.yml", "pyproject.toml"}
    missing = required_sdist.difference(sdist_items)
    if missing:
        errors.append(f"sdist missing release files: {sorted(missing)}")
    parsed = metadata(wheel)
    if parsed.get("Name") != PACKAGE or parsed.get("Version") != VERSION:
        errors.append(f"unexpected identity: {parsed.get('Name')} {parsed.get('Version')}")
    license_expression = parsed.get("License-Expression") or parsed.get("License")
    if license_expression != "Apache-2.0":
        errors.append(f"unexpected license expression: {license_expression!r}")
    source_urls = parsed.get_all("Project-URL") or []
    if not any(value.startswith("Source, https://github.com/edward-lcl/eval-evidence") for value in source_urls):
        errors.append("source URL does not identify the approved repository")
    authorized = not errors and license_expression == "Apache-2.0"
    return {
        "package": PACKAGE,
        "version": VERSION,
        "technical_valid": not errors,
        "authorized_for_distribution": authorized,
        "wheel": str(wheel),
        "wheel_file_count": len(wheel_items),
        "sdist": str(sdist),
        "sdist_file_count": len(sdist_items),
        "packaged_schemas": sorted(wheel_schemas),
        "forbidden_member_count": len(bad),
        "license_expression": license_expression,
        "errors": errors,
        "claim_boundary": "archive and metadata audit only; not trusted execution or rights beyond LICENSE/NOTICE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist", type=Path)
    args = parser.parse_args()
    result = audit(args.dist)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["technical_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
