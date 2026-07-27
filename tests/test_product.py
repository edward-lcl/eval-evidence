import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema

from eval_evidence.adapters import GenericManifestAdapter, discover_runs
from eval_evidence.core import (
    BUNDLE_SCHEMA_VERSION,
    IntegrityError,
    build_bundle,
    canonical_json_bytes,
    verify_bundle,
    verify_referenced_files,
)
from eval_evidence.demo import materialize_generic_demo, materialize_harbor_demo

ROOT = Path(__file__).resolve().parents[1]
BUNDLE_SCHEMA = ROOT / "eval_evidence/schemas/eval-evidence-bundle-v0.1.schema.json"
RUN_SCHEMA = ROOT / "eval_evidence/schemas/eval-evidence-run-v0.1.schema.json"
GENERIC_GOLDEN = "d60b0eaa1f9239eb57430a86b7831d893bb92111064c323671e2830325ba4cf9"
HARBOR_GOLDEN = "b17e1b6788a40e4cb0731714a5fcf5b080bba204bc1c12f09c148c120da07e1f"


class ProductTests(unittest.TestCase):
    def test_generic_demo_is_schema_valid_and_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_generic_demo(Path(directory) / "run")
            run = GenericManifestAdapter().load(root)
            bundle = build_bundle(run)
            self.assertEqual(bundle["schema_version"], BUNDLE_SCHEMA_VERSION)
            self.assertEqual(bundle["bundle_digest"]["value"], GENERIC_GOLDEN)
            self.assertEqual(verify_bundle(bundle, schema_path=BUNDLE_SCHEMA), [])
            self.assertEqual(verify_referenced_files(bundle, root), [])
            self.assertIsNone(bundle["attestation"]["signature"])
            self.assertEqual(bundle["source"]["adapter"], "generic")

    def test_harbor_is_first_class_adapter_not_canonical_format(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_harbor_demo(Path(directory) / "run")
            match = discover_runs(root)[0]
            bundle = build_bundle(match.adapter.load(match.root))
            self.assertEqual(match.adapter.name, "harbor")
            self.assertEqual(bundle["source"]["format"], "harbor-trial-directory")
            self.assertEqual(bundle["bundle_digest"]["value"], HARBOR_GOLDEN)
            self.assertEqual(verify_bundle(bundle, schema_path=BUNDLE_SCHEMA), [])
            self.assertEqual(verify_referenced_files(bundle, root), [])
            self.assertEqual(bundle["item_validity"]["status"], "unavailable")

    def test_generic_manifest_wins_when_both_shapes_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_generic_demo(Path(directory) / "run")
            (root / "agent").mkdir()
            for relative in ("result.json", "config.json", "agent/trajectory.json"):
                path = root / relative
                path.write_text("{}\n", encoding="utf-8")
            match = discover_runs(root)[0]
            self.assertEqual(match.adapter.name, "generic")
            self.assertEqual(match.confidence, 100)

    def test_generic_manifest_validates_against_published_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_generic_demo(Path(directory) / "run")
            document = json.loads((root / "eval-run.json").read_text())
            jsonschema.validate(document, json.loads(RUN_SCHEMA.read_text()))
            document["run"].pop("task_id")
            (root / "eval-run.json").write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(IntegrityError, "Generic manifest schema error at run"):
                GenericManifestAdapter().load(root)

    def test_reference_mutation_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_generic_demo(Path(directory) / "run")
            bundle = build_bundle(GenericManifestAdapter().load(root))
            (root / "outputs/scores.json").write_text("{}\n", encoding="utf-8")
            errors = verify_referenced_files(bundle, root)
            self.assertTrue(any("size mismatch" in error or "digest mismatch" in error for error in errors))

    def test_textual_path_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_generic_demo(Path(directory) / "run")
            document = json.loads((root / "eval-run.json").read_text())
            document["references"][0]["path"] = "../secret.txt"
            (root / "eval-run.json").write_text(json.dumps(document), encoding="utf-8")
            run = GenericManifestAdapter().load(root)
            with self.assertRaisesRegex(IntegrityError, "Unsafe run-relative path"):
                build_bundle(run)

    @unittest.skipIf(os.name == "nt", "symlink permissions vary on Windows")
    def test_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = materialize_generic_demo(base / "run")
            outside = base / "outside.json"
            outside.write_text("{}\n", encoding="utf-8")
            target = root / "outputs/scores.json"
            target.unlink()
            target.symlink_to(outside)
            with self.assertRaisesRegex(IntegrityError, "escapes root through symlink"):
                build_bundle(GenericManifestAdapter().load(root))

    def test_cli_two_command_path_and_advanced_verify(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "run"
            bundle = base / "bundle.json"
            commands = [
                [sys.executable, "-m", "eval_evidence", "demo", "-o", str(root)],
                [sys.executable, "-m", "eval_evidence", "check", str(root)],
                [sys.executable, "-m", "eval_evidence", "bundle", str(root), "-o", str(bundle)],
                [sys.executable, "-m", "eval_evidence", "verify", str(bundle), "--run-root", str(root)],
            ]
            outputs = []
            for command in commands:
                result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                outputs.append(json.loads(result.stdout))
            self.assertTrue(outputs[1]["valid"])
            self.assertTrue(outputs[3]["valid"])
            self.assertEqual(
                bundle.read_bytes(),
                canonical_json_bytes(json.loads(bundle.read_text())) + b"\n",
            )

    def test_multi_run_output_collision_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for name in ("one", "two"):
                root = materialize_generic_demo(base / name)
                document = json.loads((root / "eval-run.json").read_text())
                document["run"]["id"] = "../../same"
                (root / "eval-run.json").write_text(json.dumps(document), encoding="utf-8")
            output = base / "bundles"
            result = subprocess.run(
                [sys.executable, "-m", "eval_evidence", "bundle", str(base), "-o", str(output)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("same output filename", result.stderr)
            self.assertFalse(output.exists())

    def test_cli_plain_error_has_no_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-m", "eval_evidence", "check", directory],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("No supported evaluation run", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_archive_check_isolates_malformed_run(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            materialize_generic_demo(base / "good")
            bad = materialize_generic_demo(base / "bad")
            (bad / "eval-run.json").write_text("{\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "eval_evidence", "check", str(base)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertEqual(report["discovered_runs"], 2)
            self.assertEqual(report["summary"]["ok"], 1)
            self.assertEqual(report["summary"]["failed"], 1)

    def test_schema_ids_and_wire_ids_are_distinct_and_explicit(self):
        for path in sorted((ROOT / "eval_evidence/schemas").glob("*.json")):
            document = json.loads(path.read_text())
            if "$id" in document:
                self.assertTrue(document["$id"].startswith("https://raw.githubusercontent.com/edward-lcl/eval-evidence/"))
        schema = json.loads(BUNDLE_SCHEMA.read_text())
        self.assertEqual(schema["properties"]["schema_version"]["const"], BUNDLE_SCHEMA_VERSION)

    def test_composite_action_rejects_escape_patterns_before_cli(self):
        action = (ROOT / "action.yml").read_text()
        self.assertIn("supplied.is_absolute()", action)
        self.assertIn('".." in supplied.parts', action)
        self.assertIn("candidate.relative_to(root)", action)
        self.assertNotIn('$GITHUB_WORKSPACE/$EVAL_', action)


if __name__ == "__main__":
    unittest.main()
