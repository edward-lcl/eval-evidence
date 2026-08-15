import json
import os
import unittest
from pathlib import Path

from eval_evidence.adapters import discover_runs
from eval_evidence.core import build_bundle, verify_bundle, verify_referenced_files

ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "docs/READINESS.md"
BUNDLE_SCHEMA = ROOT / "eval_evidence/schemas/eval-evidence-bundle-v0.1.schema.json"
SANITIZED_HARBOR_FIXTURE = ROOT / "tests/fixtures/harbor-job-sanitized"


class ReadinessTests(unittest.TestCase):
    def test_every_gate_names_an_existing_test(self):
        rows = [line for line in READINESS.read_text(encoding="utf-8").splitlines() if line.startswith("| G")]
        self.assertEqual(len(rows), 4)
        for row in rows:
            columns = [column.strip() for column in row.strip("|").split("|")]
            self.assertEqual(len(columns), 4, row)
            test_name = columns[2].strip("`")
            error_count = len(unittest.defaultTestLoader.errors)
            suite = unittest.defaultTestLoader.loadTestsFromName(test_name)
            new_errors = unittest.defaultTestLoader.errors[error_count:]
            self.assertFalse(new_errors, f"{test_name}: {new_errors}")
            self.assertGreater(suite.countTestCases(), 0, test_name)
            status = columns[3]
            self.assertIn(status, {"met", "unmet"})
            if status == "met":
                result = unittest.TestResult()
                suite.run(result)
                self.assertTrue(
                    result.wasSuccessful(),
                    f"met gate {test_name} failed: "
                    f"failures={result.failures}, errors={result.errors}",
                )
                self.assertEqual(result.skipped, [], f"met gate {test_name} skipped")

    def test_sanitized_harbor_structural_fixture(self):
        matches = discover_runs(SANITIZED_HARBOR_FIXTURE, "harbor")
        self.assertEqual(len(matches), 2)
        bundles = {
            match.root.parent.name: build_bundle(match.adapter.load(match.root))
            for match in matches
        }
        for name, bundle in bundles.items():
            errors = verify_bundle(bundle, schema_path=BUNDLE_SCHEMA)
            match = next(
                match for match in matches if match.root.parent.name == name
            )
            errors += verify_referenced_files(bundle, match.root)
            self.assertEqual(errors, [], f"{name}: {errors}")

        completed = bundles["completed"]
        self.assertEqual(
            completed["extensions"]["harbor"]["trajectory_schema_version"],
            "ATIF-v1.5",
        )
        self.assertEqual(
            completed["instrument_manifest"]["fields"]["tools"]["status"],
            "unavailable",
        )
        self.assertTrue(
            any(
                not item["required"] and not item["present"]
                for item in completed["inputs"]
            )
        )

        conflicted = bundles["conflict-error"]
        self.assertEqual(conflicted["outcome"]["termination_reason"], "SyntheticError")
        conflicts = conflicted["extensions"]["harbor"]["source_conflicts"]
        self.assertIn("instrument.model_id", conflicts)
        self.assertIn("instrument.agent_name", conflicts)
        self.assertIn("execution.metrics.input_tokens", conflicts)

    @unittest.skipUnless(
        os.environ.get("EVAL_EVIDENCE_REAL_HARBOR_ROOT"),
        "set EVAL_EVIDENCE_REAL_HARBOR_ROOT to a redacted genuine Harbor job archive",
    )
    def test_real_harbor_archive_when_supplied(self):
        archive = Path(os.environ["EVAL_EVIDENCE_REAL_HARBOR_ROOT"])
        matches = discover_runs(archive, "harbor")
        self.assertGreaterEqual(len(matches), 2, "readiness requires a multi-trial job")
        optional_absence_seen = False
        transcript = []
        for match in matches:
            run = match.adapter.load(match.root)
            bundle = build_bundle(run)
            errors = verify_bundle(bundle, schema_path=BUNDLE_SCHEMA)
            errors += verify_referenced_files(bundle, match.root)
            self.assertEqual(errors, [], f"{match.root}: {errors}")
            optional_absence_seen |= any(
                not item["required"] and not item["present"] for item in bundle["inputs"]
            )
            transcript.append(
                {
                    "root": str(match.root),
                    "run_id": run.run_id,
                    "coverage": bundle["instrument_manifest"]["coverage"],
                    "compat": bundle["extensions"]["harbor"]["adapter_compat"],
                }
            )
        self.assertTrue(optional_absence_seen, "need a trial with a missing optional file")
        transcript_path = os.environ.get("EVAL_EVIDENCE_REAL_HARBOR_TRANSCRIPT")
        if transcript_path:
            Path(transcript_path).write_text(
                json.dumps({"runs": transcript}, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )


if __name__ == "__main__":
    unittest.main()
