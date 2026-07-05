#!/usr/bin/env python3
"""no-action-without-depends-on (Rule 12) regression test.

On new creation (Write/full-replace) of A-NNN.md, block a missing **depends_on** field.
The dependency graph = a fan-out attempt (D3) precondition — always enforced regardless of AT.

Run: cd flow/hooks && python3 -m unittest tests.test_no_depends_on
"""
from __future__ import annotations

import os
import sys
import unittest

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import hook_pre_tool_validate as pre  # noqa: E402

CWD = "/ws"


def _decide(tool_name: str, rel_path: str, content=None, **extra) -> str:
    ti = {"file_path": CWD + rel_path}
    if content is not None:
        ti["content"] = content
    ti.update(extra)
    out = pre.validate({"tool_name": tool_name, "tool_input": ti, "cwd": CWD})
    return out["hookSpecificOutput"]["permissionDecision"]


class TestNoActionWithoutDependsOn(unittest.TestCase):
    def setUp(self):
        self._saved = os.environ.pop("CLAUDE_PROJECT_DIR", None)

    def tearDown(self):
        if self._saved is not None:
            os.environ["CLAUDE_PROJECT_DIR"] = self._saved

    def test_missing_depends_on_deny(self):
        """Write: on A-NNN.md creation, depends_on missing → deny"""
        content = (
            "**Story**: TS-001\n"
            "**Action**: A-001\n"
            "**Ultimate purpose**: restated test purpose\n"
            "**Status**: ⬜\n"
            "\n## Goal\nTest action"
        )
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/TS-001/A-001.md", content),
            "deny",
        )

    def test_empty_array_allow(self):
        """depends_on: [] (no dependency) → allow"""
        content = (
            "**Story**: TS-001\n"
            "**Action**: A-001\n"
            "**Ultimate purpose**: restated test purpose\n"
            "**depends_on**: []\n"
            "**Status**: ⬜\n"
        )
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/TS-001/A-001.md", content),
            "allow",
        )

    def test_with_values_allow(self):
        """depends_on: [A-001] (a preceding Action specified) → allow"""
        content = (
            "**Story**: TS-001\n"
            "**Action**: A-002\n"
            "**Ultimate purpose**: restated test purpose\n"
            "**depends_on**: [A-001]\n"
            "**Status**: ⬜\n"
        )
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/TS-001/A-002.md", content),
            "allow",
        )

    def test_non_action_file_allow(self):
        """_story.md / _epic.md are not Rule 12 targets → allow (depends_on irrelevant)"""
        content = (
            "**Story**: TS-001\n"
            "**Ultimate purpose**: test purpose\n"
            "**Status**: 🔄\n"
            "\n# Story body — OK without depends_on (Rule 12 is A-NNN.md only)"
        )
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/TS-001/_story.md", content),
            "allow",
        )

    # ----- apply_patch (VS Code Copilot compatibility — H1/X1 recovery) -----

    def test_apply_patch_add_missing_depends_on_deny(self):
        """apply_patch Add File: on A-NNN.md creation, depends_on missing → deny.

        VS Code Copilot's core write path. Rule 9 (no-node-without-purpose) has an
        apply_patch branch, but only Rule 12 was missing it — this recovers that fail-open.
        """
        patch_input = "*** Begin Patch\n*** Add File: " + CWD + "/.flow/workspace/epic-x/TS-001/A-001.md\n+**Story**: TS-001\n+**Action**: A-001\n+**Ultimate purpose**: test\n+**Status**: ⬜\n*** End Patch\n"
        out = pre.validate({
            "tool_name": "apply_patch",
            "tool_input": {"input": patch_input},
            "cwd": CWD,
        })
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_apply_patch_add_with_depends_on_allow(self):
        """apply_patch Add File: on A-NNN.md creation, depends_on present → allow."""
        patch_input = "*** Begin Patch\n*** Add File: " + CWD + "/.flow/workspace/epic-x/TS-001/A-001.md\n+**Story**: TS-001\n+**Action**: A-001\n+**Ultimate purpose**: test\n+**depends_on**: []\n+**Status**: ⬜\n*** End Patch\n"
        out = pre.validate({
            "tool_name": "apply_patch",
            "tool_input": {"input": patch_input},
            "cwd": CWD,
        })
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "allow")


if __name__ == "__main__":
    unittest.main()
