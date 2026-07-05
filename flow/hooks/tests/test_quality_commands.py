"""read_quality_commands fail-safe regression (TS-003 A-001 — reading settings commands[], stdlib unittest).

Target: _flow_state.read_quality_commands — absent / parse failure / key absent / normal / validity.
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


EMPTY = {"test": None, "lint": None, "analyze": None, "required_checks": []}


class TestReadQualityCommands(unittest.TestCase):
    def test_file_absent_failsafe(self):
        with tempfile.TemporaryDirectory() as ws:
            self.assertEqual(w.read_quality_commands(ws), EMPTY)

    def test_json_broken_failsafe(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, "{broken")
            self.assertEqual(w.read_quality_commands(ws), EMPTY)

    def test_commands_key_absent_failsafe(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({"playbooks": ["feature"], "agents": []}))
            self.assertEqual(w.read_quality_commands(ws), EMPTY)

    def test_commands_not_dict_failsafe(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({"commands": ["test"]}))
            self.assertEqual(w.read_quality_commands(ws), EMPTY)

    def test_normal_read(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({"commands": {
                "test": "uv run pytest", "lint": "ruff check", "analyze": "mypy .",
                "required_checks": ["test", "lint"],
            }}))
            r = w.read_quality_commands(ws)
            self.assertEqual(r["test"], "uv run pytest")
            self.assertEqual(r["lint"], "ruff check")
            self.assertEqual(r["analyze"], "mypy .")
            self.assertEqual(r["required_checks"], ["test", "lint"])

    def test_empty_string_command_ignored(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({"commands": {"test": "  ", "lint": ""}}))
            r = w.read_quality_commands(ws)
            self.assertIsNone(r["test"])
            self.assertIsNone(r["lint"])

    def test_required_checks_filters_unknown_keys(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({"commands": {
                "test": "t", "required_checks": ["test", "bogus", "lint"],
            }}))
            # undefined / typo keys (bogus) are filtered out — declared keys only
            self.assertEqual(w.read_quality_commands(ws)["required_checks"], ["test", "lint"])

    def test_required_checks_not_list_failsafe(self):
        with tempfile.TemporaryDirectory() as ws:
            _write_settings(ws, json.dumps({"commands": {"test": "t", "required_checks": "test"}}))
            self.assertEqual(w.read_quality_commands(ws)["required_checks"], [])


if __name__ == "__main__":
    unittest.main()
