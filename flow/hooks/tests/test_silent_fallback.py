#!/usr/bin/env python3
"""Guarantee silent fallback + AT off pass normally (AC-5).

An explicit user concern — lock via regression that "silent fallback (attempted then failed) + AT off
(intentionally disabled) both pass normally" does not break. If the intent of Rule 13
(fan-out-attempt-mandatory) is distorted so it even denies the silent fallback, work stops flowing.

The 4 cases here differ in intent from the A-003 matrix (`test_fan_out_attempt.py`):
- A-003: the Rule 13 matrix alone (whether the rule fires/does not fire)
- This file: regression guarantee for the user-concern scenario (silent fallback **sequence** + AT off)

Run: cd flow/hooks && python3 -m unittest tests.test_silent_fallback
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

import hook_pre_tool_validate as pre  # noqa: E402


STORY_RUNNING = (
    "**Ultimate purpose**: silent fallback regression\n"
    "**Status**: 🔄\n"
)


def _action(num: int) -> str:
    return (
        f"**Story**: TS-001\n"
        f"**Action**: A-{num:03d}\n"
        f"**Ultimate purpose**: silent fallback regression\n"
        f"**depends_on**: []\n"
        f"**Status**: ⬜\n"
    )


class TestSilentFallbackAndATOff(unittest.TestCase):
    """AC-5: guarantee silent fallback + AT off pass normally."""

    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="ac5_")
        self._saved_project = os.environ.pop("CLAUDE_PROJECT_DIR", None)
        self._saved_at = os.environ.pop(pre.AGENT_TEAMS_ENV, None)
        os.environ["CLAUDE_PROJECT_DIR"] = self._tmp

        # Story directory with a parallelizable first wave
        self.story_dir = os.path.join(
            self._tmp, ".flow", "workspace", "epic-x", "TS-001"
        )
        os.makedirs(self.story_dir, exist_ok=True)
        with open(os.path.join(self.story_dir, "_story.md"), "w", encoding="utf-8") as f:
            f.write(STORY_RUNNING)
        for i in (1, 2):
            with open(os.path.join(self.story_dir, f"A-{i:03d}.md"), "w", encoding="utf-8") as f:
                f.write(_action(i))

    def tearDown(self):
        os.environ.pop("CLAUDE_PROJECT_DIR", None)
        if self._saved_project is not None:
            os.environ["CLAUDE_PROJECT_DIR"] = self._saved_project
        os.environ.pop(pre.AGENT_TEAMS_ENV, None)
        if self._saved_at is not None:
            os.environ[pre.AGENT_TEAMS_ENV] = self._saved_at
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _write_transcript(self, *tool_use_names) -> str:
        """transcript JSONL — simulate an assistant tool_use sequence."""
        path = os.path.join(self._tmp, "transcript.jsonl")
        entries = [{"type": "user", "message": {"content": "start"}}]
        for name in tool_use_names:
            entries.append({
                "type": "assistant",
                "message": {
                    "content": [{"type": "tool_use", "name": name, "input": {}}],
                },
            })
        with open(path, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        return path

    def _decide(self, transcript_path: str) -> str:
        code_file = os.path.join(self._tmp, "plugins", "demo", "src", "main.py")
        out = pre.validate({
            "tool_name": "Write",
            "tool_input": {"file_path": code_file, "content": "code"},
            "cwd": self._tmp,
            "transcript_path": transcript_path,
        })
        return out["hookSpecificOutput"]["permissionDecision"]

    # ----- AC-5 explicit 2 cases (consistent with the user concern) -----

    def test_silent_fallback_after_spawn_failure_allows(self):
        """(a) AT on + spawn attempt → fail → main directly (Write).

        A spawn-attempt (Flow) trace remains in the transcript, so Rule 13 passes.
        The hook does not know, and need not know, the failure itself — it checks only the 'attempt trace'.
        """
        os.environ[pre.AGENT_TEAMS_ENV] = "1"
        # sequence: Flow (spawn attempt) → Write (main handles it directly)
        tp = self._write_transcript("Flow", "Write")
        self.assertEqual(self._decide(tp), "allow")

    def test_at_off_main_direct_allows(self):
        """(b) AT off + main directly (no spawn trace).

        The AT env is intentionally disabled — Rule 13 itself does not fire (consistent with D4).
        """
        # AGENT_TEAMS_ENV unset = off
        tp = self._write_transcript("Read", "Write")  # 0 spawn traces
        self.assertEqual(self._decide(tp), "allow")

    # ----- paired cases (regression safety net) -----

    def test_at_on_no_spawn_at_all_denies(self):
        """(c) AT on + no spawn attempt at all → deny (block the silent-fallback bypass)."""
        os.environ[pre.AGENT_TEAMS_ENV] = "1"
        # a sequence with no spawn trace — did not even attempt
        tp = self._write_transcript("Read", "Grep")
        self.assertEqual(self._decide(tp), "deny")

    def test_at_on_normal_spawn_allows(self):
        """(d) AT on + normal spawn (Agent trace) → allow (attempt + success path)."""
        os.environ[pre.AGENT_TEAMS_ENV] = "1"
        tp = self._write_transcript("Agent")
        self.assertEqual(self._decide(tp), "allow")


if __name__ == "__main__":
    unittest.main()
