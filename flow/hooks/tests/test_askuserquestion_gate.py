#!/usr/bin/env python3
"""AskUserQuestion question-gate regression test (stdlib unittest, 0 dependencies).

The hook does not judge whether a question is "bad" (it cannot judge meaning). It **stops AskUserQuestion once** (deny),
shows the four-way brief, and passes it (allow) on the re-call after re-examination (1 cycle). On pass, the marker is deleted →
**once per question** (not once per session). It does not fire for general work (no active Epic). The AI decides whether to judge/ask.

origin: unifies the stop+recall gate + 1-cycle pass (infinite-loop prevention).

Run: cd flow/hooks && python3 -m unittest tests.test_askuserquestion_gate
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import hook_pre_tool_validate as pre  # noqa: E402
from _flow_state import FOUR_WAY_BRIEF  # noqa: E402

EPIC_ACTIVE = "# Epic: Test\n**Ultimate purpose**: Test purpose\n**Status**: 🔄\n"


def _mk_epic(root: str) -> None:
    d = os.path.join(root, ".flow", "workspace", "epic-x")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "_epic.md"), "w", encoding="utf-8") as f:
        f.write(EPIC_ACTIVE)


def _decide(cwd: str, tool: str = "AskUserQuestion") -> dict:
    out = pre.validate({"tool_name": tool, "tool_input": {}, "cwd": cwd})
    return out["hookSpecificOutput"]


class TestAskUserQuestionGate(unittest.TestCase):
    # validate() uses resolve_workspace_root (CLAUDE_PROJECT_DIR takes priority), so isolate the ambient
    # environment variable so the input cwd (temp dir) is respected. Without isolation, running inside a
    # session scans the real repo (misjudges the active Epic + the marker leaks into the real .runtime).
    def setUp(self):
        self._saved = os.environ.pop("CLAUDE_PROJECT_DIR", None)

    def tearDown(self):
        if self._saved is not None:
            os.environ["CLAUDE_PROJECT_DIR"] = self._saved

    def test_first_call_stops_with_brief(self):
        """First question attempt → stop once (deny) + recall the four-way brief."""
        with tempfile.TemporaryDirectory() as d:
            _mk_epic(d)
            out = _decide(d)
            self.assertEqual(out["permissionDecision"], "deny")
            self.assertIn("Pre-question four-way decision", out["permissionDecisionReason"])
            self.assertIn(FOUR_WAY_BRIEF, out["permissionDecisionReason"])

    def test_recall_passes(self):
        """Re-call after re-examination → pass (allow)."""
        with tempfile.TemporaryDirectory() as d:
            _mk_epic(d)
            self.assertEqual(_decide(d)["permissionDecision"], "deny")   # first stop
            self.assertEqual(_decide(d)["permissionDecision"], "allow")  # re-call passes

    def test_pass_clears_marker_next_stops(self):
        """Once per question — after a pass, the next question stops again (not once per session)."""
        with tempfile.TemporaryDirectory() as d:
            _mk_epic(d)
            _decide(d)                                                   # question A stops + marker
            self.assertEqual(_decide(d)["permissionDecision"], "allow")  # question A re-call passes + marker deleted
            self.assertEqual(_decide(d)["permissionDecision"], "deny")   # question B stops again

    def test_no_epic_passes(self):
        """General work (no active Epic) → does not fire (pass)."""
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(_decide(d)["permissionDecision"], "allow")

    def test_non_askquestion_unaffected(self):
        """Non-AskUserQuestion (Read) → unrelated to the gate."""
        with tempfile.TemporaryDirectory() as d:
            _mk_epic(d)
            out = _decide(d, tool="Read")
            self.assertEqual(out["permissionDecision"], "allow")
            self.assertNotIn("permissionDecisionReason", out)

    def test_brief_is_compact(self):
        """Injected content ≤3 lines (AC-2 compaction)."""
        self.assertLessEqual(FOUR_WAY_BRIEF.count("\n") + 1, 3)


if __name__ == "__main__":
    unittest.main()
