"""Plugin staleness detection (detect_plugin_staleness) regression — environment branching + version comparison (stdlib unittest).

Targets: _flow_state.{detect_plugin_staleness, _cli_latest_version}
- env detection: CLAUDE_PLUGIN_ROOT path (.claude/plugins/cache=cli / .vscode/agent-plugins=vscode)
- compare against current local state (zero network) — installed != latest → stale. fail-safe.

Run: cd flow/hooks && python3 -m unittest tests.test_plugin_staleness
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from unittest import mock

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import _flow_state as w  # noqa: E402


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


class TestDetectPluginStaleness(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cli_root = os.path.join(
            self.tmp.name, ".claude", "plugins", "cache", "mp", "plug", "0.16.0"
        )
        _write(os.path.join(self.cli_root, ".claude-plugin", "plugin.json"), '{"version": "0.16.0"}')

    def tearDown(self):
        self.tmp.cleanup()

    def test_env_cli_stale(self):
        with mock.patch.object(w, "_cli_latest_version", return_value="0.17.0"):
            d = w.detect_plugin_staleness(self.cli_root)
        self.assertEqual(d["env"], "cli")
        self.assertEqual(d["installed"], "0.16.0")
        self.assertEqual(d["latest"], "0.17.0")
        self.assertTrue(d["stale"])

    def test_in_sync_not_stale(self):
        with mock.patch.object(w, "_cli_latest_version", return_value="0.16.0"):
            self.assertFalse(w.detect_plugin_staleness(self.cli_root)["stale"])

    def test_failsafe_no_latest(self):
        # cannot determine latest (clone missing, etc.) → stale=False (silent — avoid false positives)
        with mock.patch.object(w, "_cli_latest_version", return_value=""):
            self.assertFalse(w.detect_plugin_staleness(self.cli_root)["stale"])

    def test_env_vscode_stale(self):
        root = os.path.join(
            self.tmp.name, ".vscode", "agent-plugins", "github.com", "o", "r", "plugins", "plug"
        )
        _write(os.path.join(root, ".claude-plugin", "plugin.json"), '{"version": "0.16.0"}')
        with mock.patch.object(w, "_vscode_latest_version", return_value="0.17.0"):
            d = w.detect_plugin_staleness(root)
        self.assertEqual(d["env"], "vscode")
        self.assertTrue(d["stale"])

    def test_cli_latest_extracts_clone_path(self):
        # cache/<mp>/<plugin>/<ver> → marketplaces/<mp>/plugins/<plugin> path extraction accuracy
        with tempfile.TemporaryDirectory() as home:
            clone = os.path.join(
                home, ".claude", "plugins", "marketplaces", "mp", "plugins", "plug", ".claude-plugin"
            )
            _write(os.path.join(clone, "plugin.json"), '{"version": "9.9.9"}')
            with mock.patch.object(w.os.path, "expanduser", return_value=home):
                v = w._cli_latest_version("x/.claude/plugins/cache/mp/plug/0.16.0")
        self.assertEqual(v, "9.9.9")


if __name__ == "__main__":
    unittest.main()
