"""Synthetic checker tests; these are not real AI handoff evidence."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from check_host_result import check_case


class HostResultCheckerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        (self.project / "app").mkdir(parents=True)
        (self.project / "app/port.py").write_text("def parse_port(value): return int(value)\n")
        (self.project / "app/host.py").write_text("def parse_host(value):\n    return value if '.' in value else None\n")
        (self.project / "progress.md").write_text("Applied criteria: distill:CR-aaaaaaaaaaaa@2\nStale judgment: distill:CR-aaaaaaaaaaaa@1 superseded\n")
        self.frozen = {"project_dir": "project", "card": "progress.md", "condition": "C2",
                       "sender_port_sha256": hashlib.sha256((self.project / "app/port.py").read_bytes()).hexdigest(),
                       "expected_applied_ref": "distill:CR-aaaaaaaaaaaa@2",
                       "stale_ref": "distill:CR-aaaaaaaaaaaa@1"}

    def tearDown(self):
        self.temp.cleanup()

    def test_correct_files_and_records_pass(self):
        self.assertTrue(check_case(self.root, self.frozen)["passed"])

    def test_claimed_completion_does_not_hide_wrong_behavior(self):
        (self.project / "app/host.py").write_text("class ConfigError(Exception): pass\ndef parse_host(value):\n    if '.' not in value: raise ConfigError()\n    return value\n")
        self.assertFalse(check_case(self.root, self.frozen)["passed"])
        self.frozen["condition"] = "C1"
        self.assertTrue(check_case(self.root, self.frozen)["passed"])

    def test_repeating_prior_work_fails_the_unchanged_check(self):
        (self.project / "app/port.py").write_text("# Receiver rewrote the prior result.\n")
        self.assertFalse(check_case(self.root, self.frozen)["port_unchanged"])

    def test_missing_reference_or_stale_report_fails(self):
        (self.project / "progress.md").write_text("Everything passed.\n")
        result = check_case(self.root, self.frozen)
        self.assertFalse(result["applied_ref_recorded"])
        self.assertFalse(result["stale_judgment_recorded"])
        self.assertFalse(result["passed"])

    def test_stage_supported_bullets_and_dates_keep_applied_refs(self):
        for prefix in ("- ", "- 2026-10-07: "):
            (self.project / "progress.md").write_text(prefix + "Applied criteria: distill:CR-aaaaaaaaaaaa@2\n"
                                                      + prefix + "Stale judgment: distill:CR-aaaaaaaaaaaa@1 superseded\n")
            with self.subTest(prefix=prefix):
                self.assertTrue(check_case(self.root, self.frozen)["passed"])

    def test_control_condition_observes_instead_of_assuming_a_contract(self):
        self.frozen.update({"condition": "C0", "expected_applied_ref": "none", "stale_ref": None})
        (self.project / "progress.md").write_text("Applied criteria: none\n")
        result = check_case(self.root, self.frozen)
        self.assertTrue(result["passed"])
        self.assertEqual(result["observed"]["invalid"], {"returned": None})

    def test_sender_applied_record_cannot_stand_in_for_receiver_record(self):
        before = "Applied criteria: distill:CR-aaaaaaaaaaaa@2\n"
        self.frozen["sender_card_text"] = before
        result = check_case(self.root, self.frozen)
        self.assertFalse(result["applied_ref_recorded"])
        with (self.project / "progress.md").open("a") as card:
            card.write(before)
        self.assertTrue(check_case(self.root, self.frozen)["applied_ref_recorded"])

    def test_absent_store_does_not_prove_superseded(self):
        self.frozen.update({"condition": "C0", "expected_applied_ref": "none", "stale_ref": None})
        (self.project / "progress.md").write_text(
            "Applied criteria: none\nStale judgment: distill:CR-aaaaaaaaaaaa@1 superseded\n")
        self.assertFalse(check_case(self.root, self.frozen)["passed"])

    def test_unfinished_next_action_is_not_a_complete_handoff(self):
        self.frozen["require_next_action_update"] = True
        with (self.project / "progress.md").open("a") as card:
            card.write("## Next action\nImplement parse_host.\n")
        self.assertFalse(check_case(self.root, self.frozen)["passed"])


if __name__ == "__main__":
    unittest.main()
