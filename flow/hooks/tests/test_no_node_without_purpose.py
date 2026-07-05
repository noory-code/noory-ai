#!/usr/bin/env python3
"""no-node-without-purpose (Rule 9) regression test (stdlib unittest, 0 dependencies).

Enforce purpose-anchoring chain propagation — on new creation (Write/full-replace) of a workspace node SSOT
(_initiative/_epic/_story/A-NNN.md), deny if the **Ultimate purpose** restatement is missing.
Edit (partial edit) / non-node files / outside the workspace pass.

origin: enforce that the purpose is not broken from parent (Epic) → child (Story/Action)
(a precondition for runtime purpose-anchoring derivation).

Run: cd flow/hooks && python3 -m unittest tests.test_no_node_without_purpose
"""
from __future__ import annotations

import os
import sys
import unittest

# Add the hooks directory to the import path (parent of tests/)
HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import hook_pre_tool_validate as pre  # noqa: E402

PURPOSE = "**Ultimate purpose**: improve AI escalation quality"
CWD = "/ws"  # no disk — Rule 9 checks content only (no file I/O)


def _decide(tool_name: str, rel_path: str, content=None, **extra) -> str:
    ti = {"file_path": CWD + rel_path}
    if content is not None:
        ti["content"] = content
    ti.update(extra)
    out = pre.validate({"tool_name": tool_name, "tool_input": ti, "cwd": CWD})
    return out["hookSpecificOutput"]["permissionDecision"]


class TestNoNodeWithoutPurpose(unittest.TestCase):
    # validate() uses resolve_workspace_root (CLAUDE_PROJECT_DIR takes priority),
    # so the test isolates the ambient environment variable so the input cwd (/ws) is respected.
    def setUp(self):
        self._saved = os.environ.pop("CLAUDE_PROJECT_DIR", None)

    def tearDown(self):
        if self._saved is not None:
            os.environ["CLAUDE_PROJECT_DIR"] = self._saved

    # ----- deny: new node-SSOT creation + missing ultimate purpose -----
    def test_story_missing_purpose_deny(self):
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/US-001/_story.md", "# Story\n## Goal"),
            "deny",
        )

    def test_action_missing_purpose_deny(self):
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/US-001/A-001.md", "**Action**: A-001"),
            "deny",
        )

    def test_epic_missing_purpose_deny(self):
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/_epic.md", "# Epic"),
            "deny",
        )

    def test_initiative_missing_purpose_deny(self):
        self.assertEqual(
            _decide("Write", "/.flow/workspace/initiative-x/_initiative.md", "# Initiative"),
            "deny",
        )

    # ----- allow: purpose included -----
    def test_story_with_purpose_allow(self):
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/US-001/_story.md", "# Story\n" + PURPOSE),
            "allow",
        )

    def test_action_with_purpose_allow(self):
        # A-NNN.md must pass both Rule 9 (purpose) and Rule 12 (depends_on) to allow.
        content = PURPOSE + "\n**depends_on**: []\n**Action**: A-001"
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/US-001/A-001.md", content),
            "allow",
        )

    # ----- allow: non-node file / outside the workspace / Edit (partial edit) -----
    def test_non_node_file_allow(self):
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/US-001/notes.md", "no purpose"),
            "allow",
        )

    def test_outside_workspace_allow(self):
        self.assertEqual(
            _decide("Write", "/.claude/rules/foo.md", "no purpose here"),
            "allow",
        )

    def test_edit_partial_allow(self):
        self.assertEqual(
            _decide("Edit", "/.flow/workspace/epic-x/US-001/A-001.md", old_string="a", new_string="b"),
            "allow",
        )

    def test_lookalike_basename_allow(self):
        # Block false positives from node-like basenames (DATA-001.md = A-001 substring / foo_story.md) — basename anchor
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/US-001/DATA-001.md", "no purpose"),
            "allow",
        )
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/US-001/foo_story.md", "no purpose"),
            "allow",
        )


if __name__ == "__main__":
    unittest.main()
