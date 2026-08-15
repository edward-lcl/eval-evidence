import copy
import json
import tempfile
import unittest
from pathlib import Path

from eval_evidence.adapters import GenericManifestAdapter, HarborAdapter
from eval_evidence.core import (
    IntegrityError,
    build_bundle,
    canonical_json_bytes,
    sha256_bytes,
    verify_bundle,
)
from eval_evidence.demo import materialize_generic_demo, materialize_harbor_demo


class AdversarialSemanticTests(unittest.TestCase):
    def test_partial_provenance_never_upgrades_a_value_to_observed(self):
        partial_declarations = (
            {"note": "copied from another system"},
            {"source": "another-system.json:model"},
            {"status": "observed"},
            {"status": "observed", "source": None},
        )
        for declaration in partial_declarations:
            with self.subTest(declaration=declaration), tempfile.TemporaryDirectory() as directory:
                root = materialize_generic_demo(Path(directory) / "run")
                manifest_path = root / "eval-run.json"
                document = json.loads(manifest_path.read_text())
                document["provenance"]["model_id"] = declaration
                manifest_path.write_text(json.dumps(document), encoding="utf-8")

                with self.assertRaisesRegex(
                    IntegrityError, "Generic manifest schema error.*provenance"
                ):
                    GenericManifestAdapter().load(root)

    def test_absent_and_complete_provenance_have_distinct_conservative_semantics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_generic_demo(Path(directory) / "run")
            manifest_path = root / "eval-run.json"
            document = json.loads(manifest_path.read_text())
            document["provenance"].pop("model_id")
            document["provenance"]["model_provider"] = {
                "status": "provider_asserted",
                "source": "provider response metadata",
            }
            manifest_path.write_text(json.dumps(document), encoding="utf-8")

            bundle = build_bundle(GenericManifestAdapter().load(root))
            fields = bundle["instrument_manifest"]["fields"]
            self.assertEqual(fields["model_id"]["status"], "operator_asserted")
            self.assertEqual(fields["model_provider"]["status"], "provider_asserted")

    def test_contradictory_provenance_value_pairs_fail_closed(self):
        cases = (
            ("unavailable", "synthetic-model"),
            ("observed", None),
        )
        for status, value in cases:
            with self.subTest(status=status, value=value), tempfile.TemporaryDirectory() as directory:
                root = materialize_generic_demo(Path(directory) / "run")
                manifest_path = root / "eval-run.json"
                document = json.loads(manifest_path.read_text())
                document["instrument"]["model_id"] = value
                document["provenance"]["model_id"] = {
                    "status": status,
                    "source": "adversarial fixture",
                }
                manifest_path.write_text(json.dumps(document), encoding="utf-8")

                with self.assertRaisesRegex(IntegrityError, "Contradictory provenance"):
                    GenericManifestAdapter().load(root)

    def test_harbor_disagreement_is_preserved_not_reduced_by_precedence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_harbor_demo(Path(directory) / "run")

            config_path = root / "config.json"
            config = json.loads(config_path.read_text())
            config["agent"]["model_name"] = "other/different-model"
            config["task"]["path"] = "tasks/different-task"
            config_path.write_text(json.dumps(config), encoding="utf-8")

            trajectory_path = root / "agent/trajectory.json"
            trajectory = json.loads(trajectory_path.read_text())
            trajectory["agent"]["name"] = "different-agent"
            trajectory["final_metrics"]["total_prompt_tokens"] = 999
            trajectory_path.write_text(json.dumps(trajectory), encoding="utf-8")

            bundle = build_bundle(HarborAdapter().load(root))
            fields = bundle["instrument_manifest"]["fields"]
            conflicts = bundle["extensions"]["harbor"]["source_conflicts"]

            self.assertEqual(fields["model_id"]["status"], "unavailable")
            self.assertEqual(fields["agent_name"]["status"], "unavailable")
            self.assertIsNone(bundle["execution"]["metrics"]["input_tokens"])
            self.assertEqual(conflicts["instrument.model_id"]["resolution"], "unavailable")
            self.assertEqual(conflicts["instrument.agent_name"]["resolution"], "unavailable")
            self.assertEqual(
                conflicts["execution.metrics.input_tokens"]["resolution"],
                "unavailable",
            )
            self.assertEqual(
                conflicts["source.task_identity"]["resolution"],
                "primary_retained_for_bundle_addressing",
            )
            self.assertGreaterEqual(
                len(conflicts["instrument.model_id"]["candidates"]), 2
            )

    def test_absent_harbor_list_configuration_is_not_invented_as_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_harbor_demo(Path(directory) / "run")
            config_path = root / "config.json"
            config = json.loads(config_path.read_text())
            config["agent"].pop("skills")
            config["agent"].pop("mcp_servers")
            config["agent"].pop("extra_allowed_hosts", None)
            config["environment"].pop("extra_allowed_hosts")
            config_path.write_text(json.dumps(config), encoding="utf-8")

            bundle = build_bundle(HarborAdapter().load(root))
            fields = bundle["instrument_manifest"]["fields"]
            self.assertEqual(fields["tools"]["status"], "unavailable")
            self.assertEqual(fields["network_policy"]["status"], "unavailable")

    def test_explicit_empty_harbor_list_configuration_remains_derived(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_harbor_demo(Path(directory) / "run")
            config_path = root / "config.json"
            config = json.loads(config_path.read_text())
            config["agent"]["extra_allowed_hosts"] = []
            config_path.write_text(json.dumps(config), encoding="utf-8")

            bundle = build_bundle(HarborAdapter().load(root))
            fields = bundle["instrument_manifest"]["fields"]
            self.assertEqual(fields["tools"]["status"], "derived")
            self.assertEqual(fields["tools"]["value"]["skill_count"], 0)
            self.assertEqual(fields["network_policy"]["status"], "derived")
            self.assertEqual(
                fields["network_policy"]["value"]["extra_allowed_hosts"], []
            )

    def test_coverage_is_recomputed_even_after_valid_redigest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = materialize_generic_demo(Path(directory) / "run")
            original = build_bundle(GenericManifestAdapter().load(root))
            mutations = (
                ("field_count", 999),
                ("available_fraction", 1.0),
                ("available_fraction", True),
                ("status_counts", {"observed": 20}),
            )
            for key, value in mutations:
                with self.subTest(key=key, value=value):
                    bundle = copy.deepcopy(original)
                    bundle["instrument_manifest"]["coverage"][key] = value
                    bundle.pop("bundle_digest")
                    bundle["bundle_digest"] = {
                        "algorithm": "sha256",
                        "value": sha256_bytes(canonical_json_bytes(bundle)),
                    }

                    errors = verify_bundle(bundle)
                    self.assertTrue(
                        any("coverage" in error.lower() for error in errors), errors
                    )


if __name__ == "__main__":
    unittest.main()
