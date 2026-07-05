"""Skill usage stats — on/off switch + hook registration regression (Epic usage-data-collection).

Validates append-log.py's on/off (settings `skill_usage.enabled`)·non-Skill ignore and the hooks.json
registration. Default on (records when the setting/key is absent), only `false` skips — a regression guard for the default-on / only-`false`-skips behavior.

The monthly GitHub ticket aggregation (report-usage.py·team-usage-report.py) depends on a real gh server, so instead of
automating it we validate it with a throwaway practice-ticket e2e (manual). Here we only verify hook registration.

Run: cd flow/hooks && python3 -m unittest tests.test_skill_usage
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_ROOT = os.path.dirname(HOOKS_DIR)
APPEND_LOG = os.path.join(PLUGIN_ROOT, "scripts", "append-log.py")
HOOKS_JSON = os.path.join(HOOKS_DIR, "hooks.json")

_HAVE = True  # pure-Python script — no external (bash/jq) dependency


@unittest.skipUnless(_HAVE, "python3 required")
class TestOnOffSwitch(unittest.TestCase):
    def _record_count(self, enabled, tool="Skill", extra=None, log_home=".claude"):
        home = tempfile.mkdtemp()
        proj = tempfile.mkdtemp()
        try:
            if enabled is not None:
                os.makedirs(os.path.join(proj, ".flow"))
                with open(os.path.join(proj, ".flow", "settings.json"), "w", encoding="utf-8") as f:
                    json.dump({"skill_usage": {"enabled": enabled}}, f)
            payload = json.dumps({
                "tool_name": tool,
                "tool_input": {"skill": "t", "args": ""},
                "cwd": "x", "session_id": "s",
                **(extra or {}),
            })
            env = dict(os.environ, HOME=home, CLAUDE_PROJECT_DIR=proj)
            subprocess.run([sys.executable, APPEND_LOG], input=payload, text=True, env=env,
                           capture_output=True, timeout=15)
            log = os.path.join(home, log_home, "skill-usage.jsonl")
            if not os.path.exists(log):
                return 0
            with open(log, encoding="utf-8") as fh:
                return sum(1 for _ in fh)
        finally:
            shutil.rmtree(home, ignore_errors=True)
            shutil.rmtree(proj, ignore_errors=True)

    def test_off_skips(self):
        self.assertEqual(self._record_count(False), 0, "enabled=false but recorded")

    def test_on_records(self):
        self.assertEqual(self._record_count(True), 1)

    def test_default_on_when_no_settings(self):
        self.assertEqual(self._record_count(None), 1, "should default to on when the setting is absent")

    def test_non_skill_ignored(self):
        self.assertEqual(self._record_count(None, tool="Bash"), 0, "non-Skill tools are not recorded")

    def test_codex_payload_records_under_codex_home(self):
        self.assertEqual(
            self._record_count(None, extra={"turn_id": "t-1", "permission_mode": "default"}, log_home=".codex"),
            1,
        )

    def test_claude_payload_with_permission_mode_stays_in_claude_home(self):
        # permission_mode is a Claude Code COMMON hook field — a real Claude payload
        # always carries it. It must NOT reroute the capture into ~/.codex
        # (otherwise /skill-stats, which reads ~/.claude, silently reports empty).
        self.assertEqual(
            self._record_count(
                None,
                extra={"permission_mode": "default", "session_id": "s2", "hook_event_name": "PreToolUse"},
                log_home=".claude",
            ),
            1,
        )


class TestHooksRegistered(unittest.TestCase):
    def _cfg(self):
        with open(HOOKS_JSON, encoding="utf-8") as f:
            return json.load(f)

    def test_skill_capture_registered(self):
        pre = self._cfg()["hooks"]["PreToolUse"]
        ok = any(e.get("matcher") == "Skill"
                 and any("append-log" in h["command"] for h in e["hooks"]) for e in pre)
        self.assertTrue(ok, "Skill capture (append-log) PreToolUse hook not registered")

    def test_report_usage_registered(self):
        post = self._cfg()["hooks"]["PostToolUse"]
        ok = any(any("report-usage" in h["command"] for h in e["hooks"]) for e in post)
        self.assertTrue(ok, "report-usage PostToolUse hook not registered")


class TestConfigDefaultVisibility(unittest.TestCase):
    """Discoverability: the switch must be in config-defaults so the initial config·seed is explicitly exposed in settings."""

    def test_skill_usage_in_config_defaults(self):
        with open(os.path.join(PLUGIN_ROOT, "config-defaults.json"), encoding="utf-8") as f:
            cd = json.load(f)
        self.assertIn("skill_usage", cd, "skill_usage absent from config-defaults → not visible in settings, cannot be turned off")
        self.assertEqual(cd["skill_usage"].get("enabled"), True, "default is on")


if __name__ == "__main__":
    unittest.main()
