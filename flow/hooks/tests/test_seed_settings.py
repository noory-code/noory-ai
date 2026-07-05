#!/usr/bin/env python3
"""Regression for seeding plugin-internal defaults such as upstream_board (TS-001 A-006).

Target: `_flow_state.seed_settings_defaults` — called by `/flow-upgrade` stage 0.5.
Idempotent and non-destructive: fill when empty, preserve when present, do not create when settings are absent.

Run: cd flow/hooks && python3 -m unittest tests.test_seed_settings
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

import _flow_state as ws  # noqa: E402


def _write_settings(root: str, data: dict) -> str:
    wf = os.path.join(root, ".flow")
    os.makedirs(wf, exist_ok=True)
    path = os.path.join(wf, "settings.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def _read_settings(root: str) -> dict:
    with open(os.path.join(root, ".flow", "settings.json"), "r", encoding="utf-8") as f:
        return json.load(f)


class SeedSettingsTest(unittest.TestCase):
    def test_seeds_board_when_absent(self):
        """When upstream_board is absent, fill it with the internal default."""
        with tempfile.TemporaryDirectory() as root:
            _write_settings(root, {"playbooks": ["feature"]})
            result = ws.seed_settings_defaults(root)
            self.assertIn("upstream_board", result["seeded"])
            self.assertFalse(result["settings_missing"])
            after = _read_settings(root)
            self.assertIn("upstream_board", after)
            # existing keys unchanged
            self.assertEqual(after["playbooks"], ["feature"])

    def test_preserves_existing_custom_board(self):
        """When a board already exists, do not overwrite it (preserve team customization — non-destructive)."""
        with tempfile.TemporaryDirectory() as root:
            custom = {"type": "github-project", "owner": "acme", "number": 7}
            _write_settings(root, {"playbooks": ["bug"], "upstream_board": custom})
            result = ws.seed_settings_defaults(root)
            self.assertIn("upstream_board", result["preserved"])
            self.assertNotIn("upstream_board", result["seeded"])
            after = _read_settings(root)
            self.assertEqual(after["upstream_board"], custom)

    def test_idempotent(self):
        """Calling twice yields the same result (idempotent) — the second call is preserved."""
        with tempfile.TemporaryDirectory() as root:
            _write_settings(root, {"playbooks": ["feature"]})
            ws.seed_settings_defaults(root)
            first = _read_settings(root)
            result2 = ws.seed_settings_defaults(root)
            self.assertIn("upstream_board", result2["preserved"])
            self.assertEqual(_read_settings(root), first)

    def test_settings_missing_does_not_create(self):
        """When settings.json is absent, do not create it and set settings_missing=True (configuration is the config command's responsibility)."""
        with tempfile.TemporaryDirectory() as root:
            result = ws.seed_settings_defaults(root)
            self.assertTrue(result["settings_missing"])
            self.assertEqual(result["seeded"], [])
            self.assertFalse(os.path.exists(os.path.join(root, ".flow", "settings.json")))

    def test_broken_settings_not_clobbered(self):
        """Broken JSON is not seeded (file protection)."""
        with tempfile.TemporaryDirectory() as root:
            wf = os.path.join(root, ".flow")
            os.makedirs(wf, exist_ok=True)
            path = os.path.join(wf, "settings.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{ not valid json ")
            result = ws.seed_settings_defaults(root)
            self.assertEqual(result["seeded"], [])
            # original preserved
            with open(path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "{ not valid json ")


if __name__ == "__main__":
    unittest.main()
