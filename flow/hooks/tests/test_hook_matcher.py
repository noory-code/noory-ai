"""A-002 — hooks.json PreToolUse matcher coverage regression.

If the matcher drops even one tool the hook actually checks (FILE_WRITE_TOOLS ∪ SHELL_TOOLS ∪ {AskUserQuestion}),
Claude Code does not fire the hook for that tool and the rule silently dies (silent gap).
This test enforces that coupling — it fails if you add to the tool set but forget to update the matcher.

Run: cd flow/hooks && python3 -m unittest tests.test_hook_matcher
"""
from __future__ import annotations

import json
import os
import sys
import unittest

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import hook_pre_tool_validate as pre  # noqa: E402

HOOKS_JSON = os.path.join(HOOKS_DIR, "hooks.json")


def _pre_tool_entry():
    with open(HOOKS_JSON, encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg["hooks"]["PreToolUse"][0]


class TestMatcherCoverage(unittest.TestCase):
    def test_matcher_covers_all_acted_tools(self):
        matcher = _pre_tool_entry()["matcher"]
        alts = set(matcher.split("|"))
        needed = set(pre.FILE_WRITE_TOOLS) | set(pre.SHELL_TOOLS) | {"AskUserQuestion"}
        missing = needed - alts
        self.assertEqual(
            missing, set(),
            f"hooks.json PreToolUse matcher does not cover these tools → rule silent gap: {sorted(missing)}",
        )

    def test_timeout_present(self):
        entry = _pre_tool_entry()
        self.assertIn("timeout", entry["hooks"][0], "PreToolUse hook has no timeout set (infinite-hang risk)")


if __name__ == "__main__":
    unittest.main()
