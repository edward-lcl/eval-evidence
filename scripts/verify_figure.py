#!/usr/bin/env python3
"""Verify figure content, accessibility proxies, and deterministic source/SVG linkage."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
SOURCE = FIGURES / "eval-evidence-lifecycle.figure.json"
RENDER_SOURCE = FIGURES / "eval-evidence-lifecycle.render.json"
SVG = FIGURES / "eval-evidence-lifecycle.svg"
PNG = FIGURES / "eval-evidence-lifecycle.png"
COMMAND_SOURCE = FIGURES / "eval-evidence-command-path.figure.json"
COMMAND_RENDER_SOURCE = FIGURES / "eval-evidence-command-path.render.json"
COMMAND_SVG = FIGURES / "eval-evidence-command-path.svg"
COMMAND_PNG = FIGURES / "eval-evidence-command-path.png"
BRIEF_SCHEMA = FIGURES / "figure-brief.schema.json"
RENDER = ROOT / "scripts" / "render_figure.py"
OUTCOME_CARD_WIDTH = 340
OUTCOME_CONTENT_INSET = 20
OUTCOME_CONTENT_WIDTH = OUTCOME_CARD_WIDTH - 2 * OUTCOME_CONTENT_INSET
OUTCOME_FONT_SIZE = 22
# Fixed Arial advance-width factors (em) for a deterministic layout proxy. The
# table deliberately uses no installed font metrics, so it is stable offline.
ARIAL_WIDTHS = {
    " ": 0.278, "/": 0.278, "I": 0.278, "J": 0.389, "M": 0.833, "W": 0.944,
    "f": 0.278, "i": 0.222, "j": 0.222, "l": 0.222, "m": 0.833, "t": 0.278,
    "w": 0.722,
}


def estimated_arial_width(text: str, font_size: int = OUTCOME_FONT_SIZE) -> float:
    """Return a stable Arial-width proxy for deterministic card-bound checks."""
    def factor(character: str) -> float:
        if character in ARIAL_WIDTHS:
            return ARIAL_WIDTHS[character]
        if character.isupper():
            return 0.667
        if character.islower() or character.isdigit():
            return 0.556
        return 0.5
    return sum(factor(character) for character in text) * font_size


def outcome_text_bound_errors(outcomes: list[dict]) -> list[str]:
    """Report outcome label/detail lines whose fixed-width proxy exceeds 300px."""
    errors = []
    for outcome in outcomes:
        for field in ("label_lines", "detail_lines"):
            for index, line in enumerate(outcome.get(field, []), start=1):
                width = estimated_arial_width(line)
                if width > OUTCOME_CONTENT_WIDTH:
                    errors.append(
                        f'{outcome.get("label", "outcome")} {field}[{index}] estimated width '
                        f'{width:.1f}px exceeds {OUTCOME_CONTENT_WIDTH}px content width'
                    )
    return errors


def command_text_bound_errors(commands: list[dict]) -> list[str]:
    """Check fixed command-switchboard columns with deterministic width proxies."""
    errors = []
    checks = (
        ("action_lines", 25, 290),
        ("output_lines", 24, 245),
        ("proof", 21, 286),
        ("limit", 21, 286),
    )
    for command in commands:
        for field, size, maximum in checks:
            values = command[field] if isinstance(command[field], list) else [command[field]]
            for index, line in enumerate(values, start=1):
                width = estimated_arial_width(line, size)
                if width > maximum:
                    errors.append(
                        f'{command["command"]} {field}[{index}] estimated width '
                        f'{width:.1f}px exceeds {maximum}px content width'
                    )
    return errors


def contrast(hex_color: str, background: str = "#FFFFFF") -> float:
    def luminance(value: str) -> float:
        values = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
        return .2126 * linear[0] + .7152 * linear[1] + .0722 * linear[2]
    return (max(luminance(hex_color), luminance(background)) + .05) / (min(luminance(hex_color), luminance(background)) + .05)


def png_dimensions(data: bytes) -> tuple[int, int]:
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("not a PNG with IHDR")
    return struct.unpack(">II", data[16:24])


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def verify_common(
    errors: list[str],
    source: dict,
    source_bytes: bytes,
    render: dict,
    render_bytes: bytes,
    svg_path: Path,
    png_path: Path,
    builder: Path,
) -> tuple[str, str, str, str]:
    """Verify source linkage, accessibility, labels, claims, and dimensions."""
    schema = json.loads(BRIEF_SCHEMA.read_text(encoding="utf-8"))
    for violation in sorted(Draft202012Validator(schema).iter_errors(source), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in violation.path) or "root"
        fail(errors, f"{svg_path.name} brief schema violation at {location}: {violation.message}")
    source_ids = {entry.get("id") for entry in source.get("evidence_sources", [])}
    for label in source.get("labels", []):
        unknown = set(label.get("source_ids", [])) - source_ids
        if unknown:
            fail(errors, f"{svg_path.name} label references unknown source ids: {sorted(unknown)}")
    for entry in source.get("evidence_sources", []):
        relative = Path(entry.get("path", ""))
        if relative.is_absolute() or ".." in relative.parts or not (ROOT / relative).is_file():
            fail(errors, f"{svg_path.name} source-map path does not resolve safely: {relative}")
    svg_text = svg_path.read_text(encoding="utf-8")
    brief_digest = hashlib.sha256(source_bytes).hexdigest()
    render_digest = hashlib.sha256(render_bytes).hexdigest()
    if f"brief-sha256={brief_digest}" not in svg_text:
        fail(errors, f"{svg_path.name} semantic-brief digest does not match")
    if f"render-sha256={render_digest}" not in svg_text:
        fail(errors, f"{svg_path.name} render-manifest digest does not match")
    generated = subprocess.run(
        [sys.executable, str(builder), "--check"], capture_output=True, text=True
    )
    if generated.returncode:
        fail(errors, f"{svg_path.name} is not reproducible from its frozen brief")
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as exc:
        fail(errors, f"{svg_path.name} is not well-formed XML: {exc}")
        root = None
    if root is not None:
        if root.attrib.get("role") != "img" or root.attrib.get("aria-labelledby") != "figure-title figure-desc":
            fail(errors, f"{svg_path.name} lacks the required image accessibility semantics")
        ids = {element.attrib.get("id") for element in root.iter()}
        if not {"figure-title", "figure-desc"}.issubset(ids):
            fail(errors, f"{svg_path.name} lacks title or description")
    svg_labels = " ".join(root.itertext()) if root is not None else ""
    normalized_labels = re.sub(r"\s+", " ", svg_labels)
    for label in [item["text"] for item in source["labels"]]:
        if label not in svg_labels and label not in normalized_labels:
            fail(errors, f"{svg_path.name} required label missing: {label}")
    for claim in render["forbidden_claims"]:
        if re.search(re.escape(claim), svg_text, re.IGNORECASE):
            fail(errors, f"{svg_path.name} forbidden claim in SVG: {claim}")
    minimum = source["accessibility"]["minimum_text_px"]
    sizes = [int(value) for value in re.findall(r'font-size="(\d+)"', svg_text)]
    if not sizes or min(sizes) < minimum:
        fail(errors, f"{svg_path.name} font size below brief minimum ({minimum})")
    if not png_path.exists():
        fail(errors, f"{png_path.name} is missing; run scripts/render_figure.py")
    else:
        try:
            dimensions = png_dimensions(png_path.read_bytes())
            expected = (render["canvas"]["png_width"], render["canvas"]["png_height"])
            if dimensions != expected:
                fail(errors, f"{png_path.name} dimensions {dimensions} != {expected}")
        except ValueError as exc:
            fail(errors, f"{png_path.name}: {exc}")
    return (
        brief_digest,
        render_digest,
        hashlib.sha256(svg_path.read_bytes()).hexdigest(),
        hashlib.sha256(png_path.read_bytes()).hexdigest() if png_path.exists() else "missing",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-overflow", action="store_true", help="prove the card text-bound check rejects an overflowing line")
    args = parser.parse_args()
    errors: list[str] = []
    source_bytes = SOURCE.read_text(encoding="utf-8").encode("utf-8")
    source = json.loads(source_bytes)
    render_bytes = RENDER_SOURCE.read_text(encoding="utf-8").encode("utf-8")
    render = json.loads(render_bytes)
    if args.fixture_overflow:
        fixture = [dict(outcome) for outcome in render["outcomes"]]
        fixture[-1]["detail_lines"] = ["W" * 100]
        errors.extend(outcome_text_bound_errors(fixture))
        if errors:
            print("FIGURE VERIFICATION FAILED", file=sys.stderr)
            print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
            return 1
        print("fixture unexpectedly fit", file=sys.stderr)
        return 0
    provenance = subprocess.run([sys.executable, str(RENDER), "--check-provenance"], capture_output=True, text=True)
    if provenance.returncode:
        fail(errors, "renderer/font provenance does not match the local lock")
    lifecycle_hashes = verify_common(
        errors, source, source_bytes, render, render_bytes, SVG, PNG, ROOT / "scripts" / "build_figure.py"
    )
    command_source_bytes = COMMAND_SOURCE.read_text(encoding="utf-8").encode("utf-8")
    command_source = json.loads(command_source_bytes)
    command_render_bytes = COMMAND_RENDER_SOURCE.read_text(encoding="utf-8").encode("utf-8")
    command_render = json.loads(command_render_bytes)
    command_hashes = verify_common(
        errors,
        command_source,
        command_source_bytes,
        command_render,
        command_render_bytes,
        COMMAND_SVG,
        COMMAND_PNG,
        ROOT / "scripts" / "build_command_figure.py",
    )
    for outcome in render["outcomes"]:
        if "detail_lines" not in outcome or " ".join(outcome["detail_lines"]) != outcome["detail"]:
            fail(errors, f'{outcome["label"]} detail_lines must preserve the single-line detail')
    errors.extend(outcome_text_bound_errors(render["outcomes"]))
    errors.extend(command_text_bound_errors(command_render["commands"]))
    colors = (
        {stage["color"] for stage in render["stages"]}
        | {outcome["color"] for outcome in render["outcomes"]}
        | {command["color"] for command in command_render["commands"]}
    )
    low_contrast = sorted(color for color in colors if contrast(color) < 3.0)
    if low_contrast:
        fail(errors, "low-contrast semantic colors: " + ", ".join(low_contrast))
    if errors:
        print("FIGURE VERIFICATION FAILED", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print("figure verification passed")
    print(f"lifecycle_brief_sha256={lifecycle_hashes[0]}")
    print(f"lifecycle_render_sha256={lifecycle_hashes[1]}")
    print(f"lifecycle_svg_sha256={lifecycle_hashes[2]}")
    print(f"lifecycle_png_sha256={lifecycle_hashes[3]}")
    print(f"command_brief_sha256={command_hashes[0]}")
    print(f"command_render_sha256={command_hashes[1]}")
    print(f"command_svg_sha256={command_hashes[2]}")
    print(f"command_png_sha256={command_hashes[3]}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
