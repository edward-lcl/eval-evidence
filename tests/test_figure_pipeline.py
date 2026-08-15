"""Regression coverage for the deterministic static figure verifier."""
from __future__ import annotations

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

    def test_figure_verifier_rejects_overflow_fixture(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/verify_figure.py", "--fixture-overflow"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("estimated width", result.stderr)
        self.assertIn("exceeds 300px content width", result.stderr)


if __name__ == "__main__":
    unittest.main()
