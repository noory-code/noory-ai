"""CLI plugin auto-upgrade command resolution regression (stdlib unittest, 0 dependencies).

Target: _flow_state.resolve_plugin_upgrade_commands
- Build concrete argv (marketplace/plugin) only when CLI + stale; non-CLI/up-to-date yields empty commands.
- scope is always fixed to ``project`` (this marketplace uses a per-project install/manage model).

Run: cd flow/hooks && python3 -m unittest tests.test_plugin_upgrade
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


_STALE_CLI = {"env": "cli", "installed": "0.18.0", "latest": "0.19.0", "stale": True}


class TestResolvePluginUpgradeCommands(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # cache/<mp>/<plugin>/<ver> shape — source for extracting marketplace/plugin names
        self.cli_root = os.path.join(
            self.tmp.name, ".claude", "plugins", "cache",
            "noory-ai", "flow", "0.18.0",
        )
        _write(os.path.join(self.cli_root, ".claude-plugin", "plugin.json"),
               '{"version": "0.18.0"}')
        # The CLI path actually calls `claude plugin marketplace update` right before judging,
        # so mock subprocess.run to keep the unit test off the real shell.
        self.subp = mock.patch.object(w.subprocess, "run").start()
        self.subp.return_value = mock.Mock(returncode=0, stdout="", stderr="")
        self.addCleanup(mock.patch.stopall)

    def tearDown(self):
        self.tmp.cleanup()

    def test_cli_stale_builds_commands_with_scope_project(self):
        """CLI + stale → concrete commands. scope does not follow the install value; it is always fixed to project."""
        with mock.patch.object(w, "detect_plugin_staleness", return_value=_STALE_CLI):
            r = w.resolve_plugin_upgrade_commands(self.cli_root)
        self.assertTrue(r["stale"])
        self.assertEqual(r["env"], "cli")
        self.assertEqual(r["commands"], [
            "claude plugin marketplace update noory-ai",
            "claude plugin update flow@noory-ai --scope project",
        ])

    def test_not_stale_empty(self):
        info = {"env": "cli", "installed": "0.18.0", "latest": "0.18.0", "stale": False}
        with mock.patch.object(w, "detect_plugin_staleness", return_value=info):
            self.assertEqual(w.resolve_plugin_upgrade_commands(self.cli_root)["commands"], [])

    def test_vscode_stale_empty(self):
        info = {"env": "vscode", "installed": "0.18.0", "latest": "0.19.0", "stale": True}
        with mock.patch.object(w, "detect_plugin_staleness", return_value=info):
            self.assertEqual(w.resolve_plugin_upgrade_commands(self.cli_root)["commands"], [])

    def test_unknown_env_empty(self):
        info = {"env": "unknown", "installed": "", "latest": "", "stale": False}
        with mock.patch.object(w, "detect_plugin_staleness", return_value=info):
            self.assertEqual(w.resolve_plugin_upgrade_commands(self.cli_root)["commands"], [])

    def test_unparseable_root_failsafe_empty(self):
        # If it is not a cache-path pattern, empty commands even when stale (fail-safe)
        with mock.patch.object(w, "detect_plugin_staleness", return_value=_STALE_CLI):
            r = w.resolve_plugin_upgrade_commands("/not/a/cache/path")
        self.assertEqual(r["commands"], [])

    def test_cli_refreshes_marketplace_before_judging(self):
        """Chicken-and-egg regression: with a stale marketplace clone the first judgment is
        not-stale, but running `marketplace update` beforehand catches stale on the refreshed
        clone and fills commands.

        The pre-fix behavior (judge only, clone not refreshed) yields not-stale → fails with empty commands.
        """
        calls = {"refreshed": False}

        def fake_refresh(argv, *a, **k):
            if argv[:4] == ["claude", "plugin", "marketplace", "update"]:
                calls["refreshed"] = True
            return mock.Mock(returncode=0, stdout="", stderr="")

        def fake_detect(_root=None):
            # before refresh = stale clone (install==clone, not stale) / after refresh = stale
            if calls["refreshed"]:
                return {"env": "cli", "installed": "0.18.0",
                        "latest": "0.19.0", "stale": True}
            return {"env": "cli", "installed": "0.18.0",
                    "latest": "0.18.0", "stale": False}

        self.subp.side_effect = fake_refresh
        with mock.patch.object(w, "detect_plugin_staleness", side_effect=fake_detect):
            r = w.resolve_plugin_upgrade_commands(self.cli_root)
        self.assertTrue(calls["refreshed"], "marketplace update must run before judging")
        self.assertTrue(r["stale"], "re-judged after refresh, so it must catch stale")
        self.assertEqual(r["commands"], [
            "claude plugin marketplace update noory-ai",
            "claude plugin update flow@noory-ai --scope project",
        ])

    def test_cli_marketplace_update_failure_failsafe(self):
        """Even if `marketplace update` fails with an exception, fail-safe — without propagating
        the exception it continues judging with the existing clone (emits commands if stale)."""
        self.subp.side_effect = OSError("claude not found")
        with mock.patch.object(w, "detect_plugin_staleness", return_value=_STALE_CLI):
            r = w.resolve_plugin_upgrade_commands(self.cli_root)
        self.assertTrue(r["stale"])
        self.assertEqual(r["commands"], [
            "claude plugin marketplace update noory-ai",
            "claude plugin update flow@noory-ai --scope project",
        ])


if __name__ == "__main__":
    unittest.main()
