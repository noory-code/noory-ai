#!/usr/bin/env python3
"""fan-out-attempt-mandatory (Rule 13) regression test.

With AT on, when an in-progress Story has a 'parallelizable first wave' but there is no
spawn trace, deny. AT off / silent fallback (a trace remains) / serial Story pass.

Run: cd flow/hooks && python3 -m unittest tests.test_fan_out_attempt
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
    "**Ultimate purpose**: Test purpose\n"
    "**Status**: 🔄\n"
    "\n# Story\n"
)


def _action(num: int, depends_on: str = "[]") -> str:
    return (
        f"**Story**: TS-001\n"
        f"**Action**: A-{num:03d}\n"
        f"**Ultimate purpose**: Test purpose\n"
        f"**depends_on**: {depends_on}\n"
        f"**Status**: ⬜\n"
        f"\n## Goal\nTest\n"
    )


class TestFanOutAttempt(unittest.TestCase):
    """Rule 13 firing matrix — AT on/off × spawn trace present/absent × parallelizable/not."""

    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="rule13_")
        self._saved_project = os.environ.pop("CLAUDE_PROJECT_DIR", None)
        self._saved_at = os.environ.pop(pre.AGENT_TEAMS_ENV, None)
        os.environ["CLAUDE_PROJECT_DIR"] = self._tmp

    def tearDown(self):
        os.environ.pop("CLAUDE_PROJECT_DIR", None)
        if self._saved_project is not None:
            os.environ["CLAUDE_PROJECT_DIR"] = self._saved_project
        os.environ.pop(pre.AGENT_TEAMS_ENV, None)
        if self._saved_at is not None:
            os.environ[pre.AGENT_TEAMS_ENV] = self._saved_at
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _make_parallel_ready_story(self, n_empty_dep: int = 2, n_total: int = 2, in_progress_idx=None):
        """Create a Story directory with a parallelizable first wave.

        in_progress_idx: a 1-based index set/list — sets those Actions' self-status to 🔄.
        The rest are ⬜.
        """
        in_progress_set = set(in_progress_idx or [])
        story_dir = os.path.join(
            self._tmp, ".flow", "workspace", "epic-x", "TS-001"
        )
        os.makedirs(story_dir, exist_ok=True)
        with open(os.path.join(story_dir, "_story.md"), "w", encoding="utf-8") as f:
            f.write(STORY_RUNNING)
        for i in range(1, n_total + 1):
            dep = "[]" if i <= n_empty_dep else f"[A-{i-1:03d}]"
            status = "🔄" if i in in_progress_set else "⬜"
            content = _action(i, dep).replace("**Status**: ⬜", f"**Status**: {status}")
            with open(os.path.join(story_dir, f"A-{i:03d}.md"), "w", encoding="utf-8") as f:
                f.write(content)
        return story_dir

    def _make_transcript(self, with_fan_out: bool) -> str:
        """Fake transcript JSONL — with/without an assistant tool_use trace."""
        path = os.path.join(self._tmp, "transcript.jsonl")
        entries = [
            {"type": "user", "message": {"content": "start"}},
        ]
        if with_fan_out:
            entries.append({
                "type": "assistant",
                "message": {
                    "content": [
                        {"type": "tool_use", "name": "Flow", "input": {}},
                    ],
                },
            })
        else:
            entries.append({
                "type": "assistant",
                "message": {
                    "content": [
                        {"type": "tool_use", "name": "Read", "input": {}},
                    ],
                },
            })
        with open(path, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        return path

    def _decide(self, file_path: str, transcript_path: str = "", agent_id: str = "") -> str:
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": file_path, "content": "code"},
            "cwd": self._tmp,
            "transcript_path": transcript_path,
        }
        if agent_id:
            input_data["agent_id"] = agent_id
        out = pre.validate(input_data)
        return out["hookSpecificOutput"]["permissionDecision"]

    # ----- matrix, 4 cases -----

    def test_at_on_no_fan_out_deny(self):
        """AT on + parallelizable Story + no spawn trace → deny."""
        os.environ[pre.AGENT_TEAMS_ENV] = "1"
        self._make_parallel_ready_story(n_empty_dep=2, n_total=2)
        tp = self._make_transcript(with_fan_out=False)
        code_file = os.path.join(self._tmp, "plugins", "demo", "src", "main.py")
        self.assertEqual(self._decide(code_file, tp), "deny")

    def test_at_on_with_fan_out_allow(self):
        """AT on + parallelizable Story + spawn trace present (normal or silent fallback) → allow."""
        os.environ[pre.AGENT_TEAMS_ENV] = "1"
        self._make_parallel_ready_story(n_empty_dep=2, n_total=2)
        tp = self._make_transcript(with_fan_out=True)
        code_file = os.path.join(self._tmp, "plugins", "demo", "src", "main.py")
        # Note: Rule 1 (no-action-without-doc) could block, but an A-NNN.md exists so it passes.
        # Verifies Rule 13 only: it is hard to use a path outside cwd to avoid Rule 1's influence, but since the active
        # Story has an A-NNN.md, Rule 1's has_action_doc returns True → passes.
        self.assertEqual(self._decide(code_file, tp), "allow")

    def test_at_off_no_fan_out_allow(self):
        """AT off + parallelizable Story + no spawn trace → allow (consistent with D4 — intentionally disabled)."""
        # AGENT_TEAMS_ENV unset = off
        self._make_parallel_ready_story(n_empty_dep=2, n_total=2)
        tp = self._make_transcript(with_fan_out=False)
        code_file = os.path.join(self._tmp, "plugins", "demo", "src", "main.py")
        self.assertEqual(self._decide(code_file, tp), "allow")

    def test_at_on_serial_story_allow(self):
        """AT on + serial Story (only 1 depends_on: []) → allow (parallelism is meaningless)."""
        os.environ[pre.AGENT_TEAMS_ENV] = "1"
        # A-001 (depends: []) + A-002 (depends: [A-001]) — serial, not parallelizable
        self._make_parallel_ready_story(n_empty_dep=1, n_total=2)
        tp = self._make_transcript(with_fan_out=False)
        code_file = os.path.join(self._tmp, "plugins", "demo", "src", "main.py")
        self.assertEqual(self._decide(code_file, tp), "allow")

    # ----- H2 recovery: block the status-transition bypass (0.12.0 RT-FIX — PR #24) -----

    def test_at_on_action_in_progress_no_fan_out_still_deny(self):
        """AT on + parallelizable Story + 1 Action 🔄 (normal procedure right before editing code) + no spawn trace → deny.

        The old implementation fired only on all_pending (all ⬜) → could be bypassed just by flipping to 🔄.
        0.12.0 RT-FIX (PR #24): changed to the '2+ independent Actions that are not ✅' condition — blocks the normal status-transition bypass.
        """
        os.environ[pre.AGENT_TEAMS_ENV] = "1"
        # A-001 🔄 (right before editing code), A-002 ⬜ — both depends_on: []
        self._make_parallel_ready_story(n_empty_dep=2, n_total=2, in_progress_idx=[1])
        tp = self._make_transcript(with_fan_out=False)
        code_file = os.path.join(self._tmp, "plugins", "demo", "src", "main.py")
        self.assertEqual(self._decide(code_file, tp), "deny")

    # ----- teammate (subagent) session exemption (fan-out is the main session's responsibility) -----

    def test_at_on_teammate_session_no_fan_out_allow(self):
        """AT on + parallelizable Story + no spawn trace, yet a teammate session (agent_id present) is allow.

        Same conditions as test_at_on_no_fan_out_deny but with agent_id added → since fan-out is the main
        session's responsibility, a code edit inside a teammate is exempt from Rule 13 (subagent-deployment-timing).
        """
        os.environ[pre.AGENT_TEAMS_ENV] = "1"
        self._make_parallel_ready_story(n_empty_dep=2, n_total=2)
        tp = self._make_transcript(with_fan_out=False)
        code_file = os.path.join(self._tmp, "plugins", "demo", "src", "main.py")
        self.assertEqual(self._decide(code_file, tp, agent_id="agent-abc123"), "allow")

    def test_is_subagent_session_signal(self):
        """agent_id present = non-main / absent or empty = main."""
        self.assertTrue(pre.is_subagent_session({"agent_id": "x"}))
        self.assertFalse(pre.is_subagent_session({"agent_id": ""}))
        self.assertFalse(pre.is_subagent_session({}))

    # ----- the AT env branch itself -----

    def test_at_env_off_values(self):
        """AT env = '', '0', 'false', 'no', 'off' are all off."""
        for val in ["", "0", "false", "False", "no", "OFF"]:
            os.environ[pre.AGENT_TEAMS_ENV] = val
            self.assertFalse(pre.is_agent_teams_on(), f"val={val!r} should be off")

    def test_at_env_on_values(self):
        """AT env = '1', 'true', 'yes', etc. (truthy) are on."""
        for val in ["1", "true", "yes", "on"]:
            os.environ[pre.AGENT_TEAMS_ENV] = val
            self.assertTrue(pre.is_agent_teams_on(), f"val={val!r} should be on")


if __name__ == "__main__":
    unittest.main()
