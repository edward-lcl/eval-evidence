"""Contract tests for the human and machine-readable project handoff."""
from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HandoffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.handoff = json.loads((ROOT / "PROJECT_HANDOFF.json").read_text(encoding="utf-8"))

    def test_entrypoints_and_work_starts_exist(self) -> None:
        paths = list(self.handoff["entrypoints"].values())
        paths.extend(item["start_at"] for item in self.handoff["next_work"])
        for relative in paths:
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_gate_ids_and_statuses_are_unambiguous(self) -> None:
        gates = self.handoff["gates"]
        self.assertEqual([item["id"] for item in gates], ["G1", "G2", "G3", "G4"])
        self.assertEqual({item["status"] for item in gates}, {"met", "unmet"})
        g2 = next(item for item in gates if item["id"] == "G2")
        self.assertEqual(g2["status"], "unmet")
        self.assertTrue(g2.get("blocked_by"))

    def test_next_work_is_ordered_and_blockers_are_named(self) -> None:
        work = self.handoff["next_work"]
        self.assertEqual([item["priority"] for item in work], list(range(1, len(work) + 1)))
        allowed = {"ready", "ready-for-review", "blocked-owner-input", "blocked-by-sequence"}
        for item in work:
            self.assertIn(item["status"], allowed)
            self.assertTrue(item["owner"])
            self.assertTrue(item["acceptance"])
            if item["status"] == "blocked-by-sequence":
                self.assertTrue(item.get("blocked_by"))

    def test_human_router_names_machine_readable_authority(self) -> None:
        router = (ROOT / "docs" / "START_HERE.md").read_text(encoding="utf-8")
        self.assertIn("PROJECT_HANDOFF.json", router)
        self.assertIn("Handoff does not mean every gate is met", router)

    def test_distribution_audit_cannot_self_authorize_release(self) -> None:
        source = (ROOT / "scripts" / "audit_distribution.py").read_text(encoding="utf-8")
        self.assertIn('"authorized_for_distribution": False', source)
        self.assertIn('"owner_authorization_required": True', source)


if __name__ == "__main__":
    unittest.main()
