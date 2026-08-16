#!/usr/bin/env python3
"""Verify figure semantics, accessibility, provenance, density, and raster outputs."""
from __future__ import annotations

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
BRIEF_SCHEMA = FIGURES / "figure-brief.schema.json"
RENDERER = ROOT / "scripts" / "render_figure.py"
FIGURES_AND_BUILDERS = {
    "eval-evidence-lifecycle": ROOT / "scripts" / "build_figure.py",
    "eval-evidence-command-path": ROOT / "scripts" / "build_command_figure.py",
    "eval-evidence-envelope-anatomy": ROOT / "scripts" / "build_story_figures.py",
    "eval-evidence-evidence-states": ROOT / "scripts" / "build_story_figures.py",
    "eval-evidence-tamper-story": ROOT / "scripts" / "build_story_figures.py",
}
MAX_TEXT_NODES = 32


def png_dimensions(data: bytes) -> tuple[int, int]:
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("not a PNG with IHDR")
    return struct.unpack(">II", data[16:24])


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def verify_flow_connectors(errors: list[str], figure_id: str, suffix: str, expected: int) -> None:
    """Reject head-only connectors and short shafts in the two sequential stories."""
    path = FIGURES / f"{figure_id}{suffix}.svg"
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    bodies = [element for element in root.iter() if element.attrib.get("class") == "flow-arrow-body"]
    heads = [element for element in root.iter() if element.attrib.get("class") == "flow-arrow-head"]
    if len(bodies) != expected or len(heads) != expected:
        errors.append(
            f"{path.name}: expected {expected} complete flow connectors, "
            f"found {len(bodies)} bodies and {len(heads)} heads"
        )
        return
    for body in bodies:
        x1, y1 = float(body.attrib["x1"]), float(body.attrib["y1"])
        x2, y2 = float(body.attrib["x2"]), float(body.attrib["y2"])
        if ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 < 20:
            errors.append(f"{path.name}: flow connector shaft is too short to remain visible")


def verify_svg(
    errors: list[str],
    figure_id: str,
    brief: dict,
    brief_bytes: bytes,
    render: dict,
    render_bytes: bytes,
    suffix: str,
    canvas_key: str,
) -> tuple[str, str]:
    svg_path = FIGURES / f"{figure_id}{suffix}.svg"
    png_path = FIGURES / f"{figure_id}{suffix}.png"
    svg_text = svg_path.read_text(encoding="utf-8") if svg_path.exists() else ""
    brief_digest = hashlib.sha256(brief_bytes).hexdigest()
    render_digest = hashlib.sha256(render_bytes).hexdigest()
    if f"brief-sha256={brief_digest}" not in svg_text:
        errors.append(f"{svg_path.name}: semantic-brief digest does not match")
    if f"render-sha256={render_digest}" not in svg_text:
        errors.append(f"{svg_path.name}: render-manifest digest does not match")
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as exc:
        errors.append(f"{svg_path.name}: malformed SVG: {exc}")
        return "missing", "missing"
    if root.attrib.get("role") != "img" or root.attrib.get("aria-labelledby") != "figure-title figure-desc":
        errors.append(f"{svg_path.name}: missing image accessibility semantics")
    ids = {element.attrib.get("id") for element in root.iter()}
    if not {"figure-title", "figure-desc"}.issubset(ids):
        errors.append(f"{svg_path.name}: missing title or description")
    visible = normalized(" ".join(root.itertext()))
    for label in brief["labels"]:
        if normalized(label["text"]) not in visible:
            errors.append(f'{svg_path.name}: required label missing: {label["text"]}')
    for claim in render["forbidden_claims"]:
        if re.search(re.escape(claim), visible, re.IGNORECASE):
            errors.append(f"{svg_path.name}: forbidden claim rendered: {claim}")
    if suffix == "-mobile":
        for field in ("title", "takeaway"):
            if normalized(brief[field]) not in visible:
                errors.append(f"{svg_path.name}: complete {field} is not present; mobile text may be truncated")
    text_nodes = [element for element in root.iter() if element.tag.endswith("text")]
    if len(text_nodes) > MAX_TEXT_NODES:
        errors.append(f"{svg_path.name}: {len(text_nodes)} text nodes exceed the {MAX_TEXT_NODES}-node cognitive-density budget")
    sizes = [int(value) for value in re.findall(r'font-size="(\d+)"', svg_text)]
    if not sizes or min(sizes) < brief["accessibility"]["minimum_text_px"]:
        errors.append(f'{svg_path.name}: font size below brief minimum {brief["accessibility"]["minimum_text_px"]}')
    canvas = render[canvas_key]
    expected_svg = (str(canvas["width"]), str(canvas["height"]))
    if (root.attrib.get("width"), root.attrib.get("height")) != expected_svg:
        errors.append(f"{svg_path.name}: SVG dimensions do not match {canvas_key}")
    if not png_path.exists():
        errors.append(f"{png_path.name}: missing")
    else:
        expected_png = (canvas["png_width"], canvas["png_height"])
        try:
            if png_dimensions(png_path.read_bytes()) != expected_png:
                errors.append(f"{png_path.name}: PNG dimensions do not match {expected_png}")
        except ValueError as exc:
            errors.append(f"{png_path.name}: {exc}")
    return hashlib.sha256(svg_path.read_bytes()).hexdigest(), hashlib.sha256(png_path.read_bytes()).hexdigest() if png_path.exists() else "missing"


def main() -> int:
    errors: list[str] = []
    schema = json.loads(BRIEF_SCHEMA.read_text(encoding="utf-8"))
    provenance = subprocess.run([sys.executable, str(RENDERER), "--check-provenance"], capture_output=True, text=True)
    if provenance.returncode:
        errors.append("renderer/font provenance does not match the local lock")
    hashes: dict[str, tuple[str, str, str, str]] = {}
    questions: set[str] = set()
    for figure_id, builder in FIGURES_AND_BUILDERS.items():
        brief_path = FIGURES / f"{figure_id}.figure.json"
        render_path = FIGURES / f"{figure_id}.render.json"
        brief_bytes = brief_path.read_text(encoding="utf-8").encode("utf-8")
        render_bytes = render_path.read_text(encoding="utf-8").encode("utf-8")
        brief, render = json.loads(brief_bytes), json.loads(render_bytes)
        for violation in Draft202012Validator(schema).iter_errors(brief):
            location = ".".join(str(part) for part in violation.path) or "root"
            errors.append(f"{brief_path.name}: brief schema violation at {location}: {violation.message}")
        if brief["question"] in questions:
            errors.append(f"{brief_path.name}: duplicates another figure question")
        questions.add(brief["question"])
        source_ids = {item["id"] for item in brief["evidence_sources"]}
        for item in brief["evidence_sources"]:
            relative = Path(item["path"])
            if relative.is_absolute() or ".." in relative.parts or not (ROOT / relative).is_file():
                errors.append(f"{brief_path.name}: unsafe or missing source-map path: {relative}")
        for label in brief["labels"]:
            unknown = set(label["source_ids"]) - source_ids
            if unknown:
                errors.append(f"{brief_path.name}: label references unknown sources: {sorted(unknown)}")
        if render.get("figure_id") != figure_id or brief["output"]["path"] != f"figures/{figure_id}.svg":
            errors.append(f"{figure_id}: figure identity paths disagree")
        check = subprocess.run([sys.executable, str(builder), "--check"], capture_output=True, text=True)
        if check.returncode:
            errors.append(f"{figure_id}: canonical desktop SVG is stale")
        wide = verify_svg(errors, figure_id, brief, brief_bytes, render, render_bytes, "", "canvas")
        mobile = verify_svg(errors, figure_id, brief, brief_bytes, render, render_bytes, "-mobile", "mobile_canvas")
        if figure_id == "eval-evidence-command-path":
            verify_flow_connectors(errors, figure_id, "", 3)
            verify_flow_connectors(errors, figure_id, "-mobile", 3)
        elif figure_id == "eval-evidence-tamper-story":
            verify_flow_connectors(errors, figure_id, "", 2)
            verify_flow_connectors(errors, figure_id, "-mobile", 2)
        hashes[figure_id] = (*wide, *mobile)
    mobile_check = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_mobile_figures.py"), "--check"], capture_output=True, text=True)
    if mobile_check.returncode:
        errors.append("canonical mobile SVGs are stale")
    statuses = json.loads((FIGURES / "eval-evidence-evidence-states.render.json").read_text(encoding="utf-8"))["groups"]
    actual_statuses = {status for group in statuses for status in group["statuses"]}
    expected_statuses = {"observed", "derived", "operator_asserted", "provider_asserted", "unavailable"}
    if actual_statuses != expected_statuses:
        errors.append(f"evidence-state figure enum differs from the code contract: {sorted(actual_statuses ^ expected_statuses)}")
    tamper = json.loads((FIGURES / "eval-evidence-tamper-story.render.json").read_text(encoding="utf-8"))
    if tamper["before"]["digest"] != tamper["verify"]["expected"] or tamper["after"]["digest"] != tamper["verify"]["actual"]:
        errors.append("tamper figure expected/actual digests do not reuse the before/after source values")
    if errors:
        print("FIGURE VERIFICATION FAILED", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print("figure verification passed")
    for figure_id, values in hashes.items():
        print(f"{figure_id}_svg_sha256={values[0]}")
        print(f"{figure_id}_png_sha256={values[1]}")
        print(f"{figure_id}_mobile_svg_sha256={values[2]}")
        print(f"{figure_id}_mobile_png_sha256={values[3]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
