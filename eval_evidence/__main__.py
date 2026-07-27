"""Command-line interface for Eval Evidence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from . import __version__
from .adapters import ADAPTERS, discover_runs
from .core import (
    IntegrityError,
    build_bundle,
    canonical_json_bytes,
    load_json,
    safe_run_path,
    verify_bundle,
    verify_referenced_files,
)
from .demo import materialize_generic_demo, materialize_harbor_demo

PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_BUNDLE_SCHEMA = PACKAGE_ROOT / "schemas" / "eval-evidence-bundle-v0.1.schema.json"


def emit(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _add_run_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", type=Path, help="run directory or archive tree")
    parser.add_argument(
        "--adapter",
        choices=["auto", *(adapter.name for adapter in ADAPTERS)],
        default="auto",
        help="input adapter (default: auto-detect)",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_BUNDLE_SCHEMA,
        help="bundle JSON Schema",
    )


def _evaluate(path: Path, adapter_name: str, schema: Path, max_runs: int | None = None) -> dict:
    if max_runs is not None and max_runs < 1:
        raise IntegrityError("--max-runs must be positive")
    matches = discover_runs(path, adapter_name)
    selected = matches[:max_runs] if max_runs is not None else matches
    rows = []
    failures = 0
    unavailable_heavy = 0
    referenced_file_fail = 0
    for match in selected:
        try:
            run = match.adapter.load(match.root)
            bundle = build_bundle(run)
            schema_errors = verify_bundle(bundle, schema_path=schema)
            reference_errors = verify_referenced_files(bundle, match.root)
            errors = schema_errors + reference_errors
            fields = bundle["instrument_manifest"]["fields"]
            unavailable = sum(value["status"] == "unavailable" for value in fields.values())
            heavy = bool(fields and unavailable / len(fields) >= 0.5)
            unavailable_heavy += int(heavy)
            referenced_file_fail += int(bool(reference_errors))
            failures += int(bool(errors))
            rows.append(
                {
                    "root": str(match.root),
                    "adapter": match.adapter.name,
                    "run_id": run.run_id,
                    "task_id": run.task_id,
                    "valid": not errors,
                    "bundle_digest": bundle["bundle_digest"]["value"],
                    "instrument_coverage": bundle["instrument_manifest"]["coverage"],
                    "unavailable_heavy": heavy,
                    "errors": errors,
                }
            )
        except Exception as exc:  # isolate malformed runs in an archive
            failures += 1
            rows.append(
                {
                    "root": str(match.root),
                    "adapter": match.adapter.name,
                    "valid": False,
                    "errors": [f"{type(exc).__name__}: {exc}"],
                }
            )
    return {
        "valid": failures == 0,
        "root": str(path.resolve()),
        "discovered_runs": len(matches),
        "checked_runs": len(selected),
        "truncated": len(selected) != len(matches),
        "summary": {
            "ok": len(selected) - failures,
            "failed": failures,
            "unavailable_heavy": unavailable_heavy,
            "referenced_file_fail": referenced_file_fail,
        },
        "runs": rows,
        "scope": (
            "schema, bundle digest, and local referenced-file identity; no model "
            "execution, trusted-runner signature, or physical-truth claim"
        ),
    }


def command_check(args: argparse.Namespace) -> int:
    report = _evaluate(args.path, args.adapter, args.schema, args.max_runs)
    emit(report)
    return 0 if report["valid"] else 1


def _safe_output_stem(run_id: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", run_id).strip(".-")
    if not stem:
        raise IntegrityError("run_id cannot produce a safe output filename")
    return stem[:160]


def command_bundle(args: argparse.Namespace) -> int:
    matches = discover_runs(args.path, args.adapter)
    output: Path = args.output
    if len(matches) > 1 and output.suffix:
        raise IntegrityError("--output must be a directory when multiple runs are discovered")
    prepared: list[tuple[Path, dict, object, object]] = []
    destinations: set[Path] = set()
    for match in matches:
        run = match.adapter.load(match.root)
        bundle = build_bundle(run)
        errors = verify_bundle(bundle, schema_path=args.schema)
        errors += verify_referenced_files(bundle, match.root)
        if errors:
            raise IntegrityError("Generated bundle failed validation: " + "; ".join(errors))
        destination = output
        if len(matches) > 1 or not output.suffix:
            destination = output / f"{_safe_output_stem(run.run_id)}.eval-evidence.json"
        resolved_destination = destination.resolve()
        if resolved_destination in destinations:
            raise IntegrityError(
                f"Multiple runs map to the same output filename: {destination.name}"
            )
        referenced_paths = {
            safe_run_path(run.root, reference.path) for reference in run.references
        }
        if resolved_destination in referenced_paths:
            raise IntegrityError(
                f"Refusing to overwrite referenced source file: {destination}"
            )
        destinations.add(resolved_destination)
        prepared.append((destination, bundle, match, run))

    written = []
    for destination, bundle, match, run in prepared:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(canonical_json_bytes(bundle) + b"\n")
        written.append(
            {
                "root": str(match.root),
                "adapter": match.adapter.name,
                "output": str(destination),
                "bundle_digest": bundle["bundle_digest"]["value"],
            }
        )
    emit({"written": written})
    return 0


def command_verify(args: argparse.Namespace) -> int:
    bundle = load_json(args.bundle)
    if not isinstance(bundle, dict):
        raise IntegrityError("Bundle must be a JSON object")
    errors = verify_bundle(bundle, schema_path=args.schema)
    if args.run_root is not None:
        errors += verify_referenced_files(bundle, args.run_root)
    emit(
        {
            "valid": not errors,
            "bundle": str(args.bundle),
            "bundle_digest": bundle.get("bundle_digest"),
            "referenced_files_checked": args.run_root is not None,
            "errors": errors,
            "scope": "content/schema identity only; not trusted attestation",
        }
    )
    return 0 if not errors else 1


def command_inspect(args: argparse.Namespace) -> int:
    rows = []
    for match in discover_runs(args.path, args.adapter):
        run = match.adapter.load(match.root)
        bundle = build_bundle(run)
        fields = bundle["instrument_manifest"]["fields"]
        rows.append(
            {
                "root": str(match.root),
                "adapter": match.adapter.name,
                "run_id": run.run_id,
                "task_id": run.task_id,
                "source_format": run.source_format,
                "coverage": bundle["instrument_manifest"]["coverage"],
                "available_fields": sorted(k for k, v in fields.items() if v["status"] != "unavailable"),
                "unavailable_fields": sorted(k for k, v in fields.items() if v["status"] == "unavailable"),
                "item_validity_status": bundle["item_validity"]["status"],
                "verifier_evidence_status": bundle["verifier_evidence"]["status"],
            }
        )
    emit({"runs": rows})
    return 0


def command_demo(args: argparse.Namespace) -> int:
    if args.output.exists():
        raise IntegrityError(f"Demo output already exists: {args.output}")
    trial = (
        materialize_generic_demo(args.output)
        if args.format == "generic"
        else materialize_harbor_demo(args.output)
    )
    emit(
        {
            "root": str(trial),
            "format": args.format,
            "synthetic": True,
            "next": f"eval-evidence check {trial}",
        }
    )
    return 0


def parser() -> argparse.ArgumentParser:
    invoked = Path(sys.argv[0]).name
    program = "eval-evidence" if invoked == "eval-evidence" else "python -m eval_evidence"
    ap = argparse.ArgumentParser(
        prog=program,
        description="Build and verify machine-checkable evidence for AI evaluation runs.",
    )
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = ap.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="auto-detect, build, and verify runs in one step")
    _add_run_options(check)
    check.add_argument("--max-runs", type=int)
    check.set_defaults(func=command_check)

    bundle = sub.add_parser("bundle", aliases=["build"], help="write canonical evidence bundles")
    _add_run_options(bundle)
    bundle.add_argument("--output", "-o", type=Path, required=True)
    bundle.set_defaults(func=command_bundle)

    inspect = sub.add_parser("inspect", help="show adapter and evidence coverage without writing")
    _add_run_options(inspect)
    inspect.set_defaults(func=command_inspect)

    verify = sub.add_parser("verify", help="verify an existing evidence bundle")
    verify.add_argument("bundle", type=Path)
    verify.add_argument("--run-root", "--trial-dir", dest="run_root", type=Path)
    verify.add_argument("--schema", type=Path, default=DEFAULT_BUNDLE_SCHEMA)
    verify.set_defaults(func=command_verify)

    audit = sub.add_parser("audit", help="compatibility alias for check")
    _add_run_options(audit)
    audit.add_argument("--max-runs", "--max-trials", dest="max_runs", type=int)
    audit.set_defaults(func=command_check)

    demo = sub.add_parser("demo", help="write a deterministic synthetic example run")
    demo.add_argument("--output", "-o", type=Path, required=True)
    demo.add_argument("--format", choices=["generic", "harbor"], default="generic")
    demo.set_defaults(func=command_demo)
    return ap


def main() -> int:
    args = parser().parse_args()
    try:
        return int(args.func(args))
    except IntegrityError as exc:
        print(f"eval-evidence: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
