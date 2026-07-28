import copy
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
    sha256_bytes,
    verify_bundle,
    verify_referenced_files,
)
from eval_evidence.demo import materialize_generic_demo, materialize_harbor_demo

ROOT = Path(__file__).resolve().parents[1]
BUNDLE_SCHEMA = ROOT / "eval_evidence/schemas/eval-evidence-bundle-v0.1.schema.json"
RUN_SCHEMA = ROOT / "eval_evidence/schemas/eval-evidence-run-v0.1.schema.json"
GENERIC_GOLDEN = "d60b0eaa1f9239eb57430a86b7831d893bb92111064c323671e2830325ba4cf9"
HARBOR_GOLDEN = "6730c2ff3f6791740ddc0b9ebc978cf24f5bd655e6d211ad9d0280be0f0093bd"


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
            self.assertNotEqual(
                bundle["instrument_manifest"]["fields"]["max_wall_time_s"]["status"],
                "unavailable",
            )
            self.assertTrue(
                bundle["extensions"]["harbor"]["adapter_compat"]["recognized"]
            )

    def test_harbor_metrics_fall_back_when_primary_value_is_null(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_harbor_demo(Path(directory) / "run")
            result_path = root / "result.json"
            result = json.loads(result_path.read_text())
            result["agent_result"]["n_cache_tokens"] = None
            result_path.write_text(json.dumps(result), encoding="utf-8")
            trajectory_path = root / "agent/trajectory.json"
            trajectory = json.loads(trajectory_path.read_text())
            trajectory["final_metrics"]["total_cached_tokens"] = 3
            trajectory_path.write_text(json.dumps(trajectory), encoding="utf-8")
            match = discover_runs(root)[0]
            bundle = build_bundle(match.adapter.load(root))
            self.assertEqual(bundle["execution"]["metrics"]["cache_tokens"], 3)

    def test_harbor_wall_time_falls_back_to_result_timeout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_harbor_demo(Path(directory) / "run")
            config_path = root / "config.json"
            config = json.loads(config_path.read_text())
            config["agent"]["override_timeout_sec"] = None
            config["agent"]["max_timeout_sec"] = None
            config_path.write_text(json.dumps(config), encoding="utf-8")
            result_path = root / "result.json"
            result = json.loads(result_path.read_text())
            result["agent_result"]["timeout_sec"] = 900
            result_path.write_text(json.dumps(result), encoding="utf-8")
            match = discover_runs(root)[0]
            bundle = build_bundle(match.adapter.load(root))
            field = bundle["instrument_manifest"]["fields"]["max_wall_time_s"]
            self.assertEqual(field["value"], 900)
            self.assertEqual(field["status"], "observed")
            self.assertEqual(
                field["source"], "Harbor result.json:agent_result.timeout_sec"
            )

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

    def test_nonfinite_json_and_orphan_provenance_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_generic_demo(Path(directory) / "run")
            (root / "eval-run.json").write_text('{"value": NaN}', encoding="utf-8")
            with self.assertRaisesRegex(IntegrityError, "Non-finite JSON number"):
                GenericManifestAdapter().load(root)
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_generic_demo(Path(directory) / "run")
            document = json.loads((root / "eval-run.json").read_text())
            document["provenance"]["not_an_instrument_field"] = {
                "status": "observed", "source": "bad"
            }
            (root / "eval-run.json").write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(IntegrityError, "fields absent from instrument"):
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

    def test_cli_quickstart_both_formats(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for format_name in ("generic", "harbor"):
                root = base / format_name
                bundle = base / f"{format_name}.json"
                commands = [
                    [
                        sys.executable,
                        "-m",
                        "eval_evidence",
                        "demo",
                        "--format",
                        format_name,
                        "-o",
                        str(root),
                    ],
                    [sys.executable, "-m", "eval_evidence", "check", str(root)],
                    [
                        sys.executable,
                        "-m",
                        "eval_evidence",
                        "bundle",
                        str(root),
                        "-o",
                        str(bundle),
                    ],
                    [
                        sys.executable,
                        "-m",
                        "eval_evidence",
                        "verify",
                        str(bundle),
                        "--run-root",
                        str(root),
                    ],
                ]
                outputs = []
                for command in commands:
                    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    outputs.append(json.loads(result.stdout))
                self.assertTrue(outputs[1]["valid"])
                self.assertEqual(outputs[1]["tool_version"], "0.2.0")
                self.assertEqual(outputs[1]["bundle_schema_version"], BUNDLE_SCHEMA_VERSION)
                self.assertTrue(outputs[3]["valid"])
                self.assertEqual(
                    bundle.read_bytes(),
                    canonical_json_bytes(json.loads(bundle.read_text())) + b"\n",
                )

    def test_bundle_tamper_matrix(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_generic_demo(Path(directory) / "run")
            original = build_bundle(GenericManifestAdapter().load(root))
            mutations = (
                lambda bundle: bundle["outcome"].__setitem__("reward", 0.125),
                lambda bundle: bundle["inputs"][0].__setitem__("sha256", "0" * 64),
                lambda bundle: bundle["instrument_manifest"]["fields"]["model_id"].__setitem__(
                    "status", "derived"
                ),
                lambda bundle: bundle.__setitem__("schema_version", "eval-evidence.bundle/v9.9"),
            )
            for mutate in mutations:
                with self.subTest(mutate=mutate):
                    tampered = copy.deepcopy(original)
                    mutate(tampered)
                    errors = verify_bundle(tampered, schema_path=BUNDLE_SCHEMA)
                    self.assertTrue(
                        any("Bundle digest mismatch" in error for error in errors), errors
                    )

    def test_redigested_bundle_is_internally_valid_not_authentic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_generic_demo(Path(directory) / "run")
            bundle = build_bundle(GenericManifestAdapter().load(root))
            bundle["outcome"]["reward"] = 0.125
            payload = dict(bundle)
            payload.pop("bundle_digest")
            bundle["bundle_digest"]["value"] = sha256_bytes(canonical_json_bytes(payload))
            self.assertEqual(verify_bundle(bundle, schema_path=BUNDLE_SCHEMA), [])

    def test_unknown_harbor_trajectory_version_warns_without_failing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_harbor_demo(Path(directory) / "run")
            trajectory_path = root / "agent/trajectory.json"
            trajectory = json.loads(trajectory_path.read_text())
            trajectory["schema_version"] = "ATIF-v9.9"
            trajectory_path.write_text(json.dumps(trajectory), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "eval_evidence", "check", str(root)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["valid"])
            self.assertEqual(report["summary"]["compat_warnings"], 1)
            self.assertIn("ATIF-v9.9", report["runs"][0]["compat_warnings"][0])

    def test_inspect_explain_and_minimum_coverage_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_harbor_demo(Path(directory) / "run")
            inspect_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "eval_evidence",
                    "inspect",
                    str(root),
                    "--explain",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(inspect_result.returncode, 0, inspect_result.stderr)
            sources = json.loads(inspect_result.stdout)["runs"][0]["field_sources"]
            self.assertIn("max_wall_time_s", sources)
            self.assertIn("config.json:agent", sources["max_wall_time_s"])

            check_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "eval_evidence",
                    "check",
                    str(root),
                    "--min-coverage",
                    "1",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(check_result.returncode, 1, check_result.stderr)
            report = json.loads(check_result.stdout)
            self.assertTrue(report["valid"])
            self.assertFalse(report["policy_passed"])
            self.assertEqual(report["summary"]["failed"], 0)
            self.assertEqual(report["summary"]["policy_failed"], 1)
            self.assertEqual(report["runs"][0]["errors"], [])
            self.assertIn("below --min-coverage", report["runs"][0]["policy_errors"][0])

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

    def test_bundle_refuses_to_overwrite_a_source_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_generic_demo(Path(directory) / "run")
            source = root / "outputs/scores.json"
            before = source.read_bytes()
            result = subprocess.run(
                [sys.executable, "-m", "eval_evidence", "bundle", str(root), "-o", str(source)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("Refusing to overwrite referenced source file", result.stderr)
            self.assertEqual(source.read_bytes(), before)

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

    def test_trusted_publishing_is_oidc_only_and_checksum_gated(self):
        workflow = (ROOT / ".github/workflows/publish-pypi.yml").read_text()
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("environment: pypi", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("shasum -a 256 -c", workflow)
        self.assertIn(
            "pypa/gh-action-pypi-publish@ba38be9e461d3875417946c167d0b5f3d385a247",
            workflow,
        )
        self.assertNotIn("PYPI_TOKEN", workflow)
        self.assertNotIn("password:", workflow)

    def test_composite_action_rejects_escape_patterns_before_cli(self):
        action = (ROOT / "action.yml").read_text()
        self.assertIn("supplied.is_absolute()", action)
        self.assertIn('".." in supplied.parts', action)
        self.assertIn("candidate.relative_to(root)", action)
        self.assertNotIn('$GITHUB_WORKSPACE/$EVAL_', action)


if __name__ == "__main__":
    unittest.main()
