# resolve_review_command turns per-stage review config into the command to run,
# and fails CLOSED (a non-empty error the caller must honor) on a typo'd strength
# or a strength with no bound command — never a silent skip.
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

_P = Path(__file__).resolve().parents[1] / "stage_paths.py"
_spec = importlib.util.spec_from_file_location("stage_paths", _P)
stage_paths = importlib.util.module_from_spec(_spec)
sys.modules["stage_paths"] = stage_paths
assert _spec.loader is not None
_spec.loader.exec_module(stage_paths)


class ResolveReviewCommandTest(unittest.TestCase):
    def test_off_or_unset_requires_nothing(self):
        self.assertEqual(stage_paths.resolve_review_command({}, "implementation"), (None, ""))
        self.assertEqual(
            stage_paths.resolve_review_command({"stages": {"implementation": "off"}}, "implementation"),
            (None, ""),
        )

    def test_valid_strength_resolves_command(self):
        review = {"stages": {"implementation": "standard"}, "strengths": {"standard": "run-review"}}
        self.assertEqual(stage_paths.resolve_review_command(review, "implementation"), ("run-review", ""))

    def test_typo_strength_fails_closed(self):
        cmd, err = stage_paths.resolve_review_command({"stages": {"design": "redteam"}}, "design")
        self.assertIsNone(cmd)
        self.assertIn("not one of", err)

    def test_strength_without_command_fails_closed(self):
        cmd, err = stage_paths.resolve_review_command({"stages": {"promotion": "deep"}}, "promotion")
        self.assertIsNone(cmd)
        self.assertIn("no command", err)

    def test_non_string_stage_value_fails_closed(self):
        # A number/null/list is malformed, not "off" — must not silently skip.
        for bad in (5, None, ["standard"], True):
            cmd, err = stage_paths.resolve_review_command({"stages": {"implementation": bad}}, "implementation")
            self.assertIsNone(cmd)
            self.assertTrue(err, f"{bad!r} should fail closed")

    def test_non_dict_stages_fails_closed(self):
        cmd, err = stage_paths.resolve_review_command({"stages": "implementation"}, "implementation")
        self.assertIsNone(cmd)
        self.assertTrue(err)

    def test_absent_stage_is_off(self):
        self.assertEqual(stage_paths.resolve_review_command({"stages": {"design": "off"}}, "implementation"), (None, ""))


if __name__ == "__main__":
    unittest.main()
