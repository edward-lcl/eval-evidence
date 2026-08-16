"""Regression coverage for the deterministic static figure verifier."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FigurePipelineTests(unittest.TestCase):
    def test_canonical_svgs_match_their_briefs(self) -> None:
        for script in (
            "scripts/build_figure.py",
            "scripts/build_command_figure.py",
            "scripts/build_story_figures.py",
            "scripts/build_mobile_figures.py",
        ):
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, script, "--check"],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_figure_verifier_accepts_current_figures_when_renderer_matches(self) -> None:
        provenance = subprocess.run(
            [sys.executable, "scripts/render_figure.py", "--check-provenance"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if provenance.returncode:
            self.skipTest("local renderer/font does not match figures/renderer.lock")
        result = subprocess.run(
            [sys.executable, "scripts/verify_figure.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_evidence_state_figure_uses_the_exact_wire_enum(self) -> None:
        render = json.loads(
            (ROOT / "figures/eval-evidence-evidence-states.render.json").read_text()
        )
        statuses = {status for group in render["groups"] for status in group["statuses"]}
        self.assertEqual(
            statuses,
            {"observed", "derived", "operator_asserted", "provider_asserted", "unavailable"},
        )

    def test_tamper_story_reuses_one_digest_pair(self) -> None:
        render = json.loads(
            (ROOT / "figures/eval-evidence-tamper-story.render.json").read_text()
        )
        self.assertEqual(render["before"]["digest"], render["verify"]["expected"])
        self.assertEqual(render["after"]["digest"], render["verify"]["actual"])


if __name__ == "__main__":
    unittest.main()
