#!/usr/bin/env python3
"""Render the canonical SVG with the lock-pinned local renderer and font."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
LOCK = FIGURES / "renderer.lock"
FIGURE_IDS = ("eval-evidence-lifecycle", "eval-evidence-command-path")


def require_local_provenance(config: dict) -> str:
    """Return the renderer executable after fail-closed renderer/font checks."""
    renderer = config["renderer"]
    executable = shutil.which(renderer)
    if executable is None:
        raise SystemExit(f"required local renderer is unavailable: {renderer}")
    version = subprocess.run([executable, "--version"], text=True, capture_output=True, check=True).stdout
    expected = f"version {config['version']}"
    if expected not in version:
        raise SystemExit(f"renderer version mismatch: expected {expected!r}, got {version.splitlines()[0]!r}")

    font = config["font"]
    fc_match = shutil.which("fc-match")
    if fc_match is None:
        raise SystemExit("required local font resolver is unavailable: fc-match")
    resolved = subprocess.run(
        [fc_match, "--format=%{file}", font["fontconfig_pattern"]],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    font_path = Path(resolved)
    if not font_path.is_file():
        raise SystemExit("declared font did not resolve to a readable local file")
    actual_hash = hashlib.sha256(font_path.read_bytes()).hexdigest()
    if font_path.name != font["file_name"] or actual_hash != font["sha256"]:
        raise SystemExit(
            "resolved font identity/hash mismatch; refusing to render with an unpinned fallback"
        )
    return executable


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-provenance", action="store_true", help="validate renderer and resolved-font lock without writing PNG")
    args = parser.parse_args()
    config = json.loads(LOCK.read_text(encoding="utf-8"))
    executable = require_local_provenance(config)
    if args.check_provenance:
        print(f"renderer={config['renderer']} version={config['version']}")
        print(f"font={config['font']['family']} sha256={config['font']['sha256']}")
        return 0
    for figure_id in FIGURE_IDS:
        canvas = json.loads((FIGURES / f"{figure_id}.render.json").read_text(encoding="utf-8"))["canvas"]
        subprocess.run([
            executable, "--width", str(canvas["png_width"]), "--height", str(canvas["png_height"]),
            "--output", str(FIGURES / f"{figure_id}.png"), str(FIGURES / f"{figure_id}.svg"),
        ], check=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
