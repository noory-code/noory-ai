"""read_quality_commands fail-safe regression (quality-gate settings reader, stdlib unittest).

Target: _flow_state.read_quality_commands — absent / parse failure / key absent / normal /
validity / arbitrary check names / new `checks`+`required` shape with legacy
`commands`+`required_checks` compatibility.
Run: cd flow/hooks && python3 -m unittest tests.test_quality_commands
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import _flow_state as w  # noqa: E402


def _write_settings(ws: str, content: str) -> None:
    d = os.path.join(ws, ".flow")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "settings.json"), "w", encoding="utf-8") as f:
        f.write(content)


EMPTY = {"checks": {}, "required_checks": []}


class TestReadQualityChecksFailsafe(unittest.TestCase):
    def test_file_absent_failsafe(self):
        with tempfile.TemporaryDirectory() as ws:
            self.assertEqual(w.read_quality_commands(ws), EMPTY)

    def test_json_broken_failsafe(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, "{broken")
            self.assertEqual(w.read_quality_commands(ws), EMPTY)

    def test_field_absent_failsafe(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({"playbooks": ["feature"]}))
            self.assertEqual(w.read_quality_commands(ws), EMPTY)

    def test_field_not_dict_failsafe(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({"checks": ["test"]}))
            self.assertEqual(w.read_quality_commands(ws), EMPTY)

    def test_required_not_list_failsafe(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({"checks": {"test": "t", "required": "test"}}))
            self.assertEqual(w.read_quality_commands(ws)["required_checks"], [])


class TestReadQualityChecksShapes(unittest.TestCase):
    def test_new_shape_arbitrary_names(self):
        # The user-facing canonical shape: `checks` + `required`, names are free-form.
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({"checks": {
                "test-engine": ["uv", "run", "pytest", "-q"],
                "typecheck-viewer": "npm run typecheck",
                "required": ["test-engine", "typecheck-viewer"],
            }}))
            r = w.read_quality_commands(ws)
            self.assertEqual(r["checks"]["test-engine"], ["uv", "run", "pytest", "-q"])
            self.assertEqual(r["checks"]["typecheck-viewer"], "npm run typecheck")
            self.assertEqual(r["required_checks"], ["test-engine", "typecheck-viewer"])

    def test_legacy_shape_still_read(self):
        # Pre-rename settings (`commands` + `required_checks`) keep working.
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({"commands": {
                "test": "uv run pytest", "lint": "ruff check",
                "required_checks": ["test", "lint"],
            }}))
            r = w.read_quality_commands(ws)
            self.assertEqual(r["checks"]["test"], "uv run pytest")
            self.assertEqual(r["checks"]["lint"], "ruff check")
            self.assertEqual(r["required_checks"], ["test", "lint"])

    def test_new_shape_wins_over_legacy(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({
                "checks": {"new-check": "new", "required": ["new-check"]},
                "commands": {"old-check": "old", "required_checks": ["old-check"]},
            }))
            r = w.read_quality_commands(ws)
            self.assertIn("new-check", r["checks"])
            self.assertNotIn("old-check", r["checks"])
            self.assertEqual(r["required_checks"], ["new-check"])

    def test_empty_string_command_ignored(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({"checks": {"test": "  ", "lint": ""}}))
            self.assertEqual(w.read_quality_commands(ws)["checks"], {})

    def test_required_kept_verbatim_for_config_error(self):
        # A required name with no declared command is NOT silently dropped — the
        # adapter CLI must see it and fail loudly as a config error (Fail Fast;
        # silently dropping a typo would silently weaken the gate).
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({"checks": {
                "test": "t", "required": ["test", "bogus"],
            }}))
            self.assertEqual(w.read_quality_commands(ws)["required_checks"], ["test", "bogus"])


if __name__ == "__main__":
    unittest.main()
