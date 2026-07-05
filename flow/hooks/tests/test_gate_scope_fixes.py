"""Regression tests for the round-4 functional-review fixes.

Covers four confirmed findings:
1. Completed (✅) epics must not pollute Rule 1/2/7/13 scans — a leftover in-progress
   action inside a ✅ epic neither satisfies no-action-without-doc for the active epic
   nor blocks retro/review gates nor becomes a fan-out target.
2. user_requested_shared_merge must match keywords on word boundaries (no 'pushover'
   substring false-positives) and USER_MERGE_KEYWORDS must contain no duplicates.
3. REVIEW_MARKER_RE must be heading-anchored — prose or an HTML-comment mention of
   "Review & Evaluation" is not a review record.
4. _flow_state readers (parse_epic / find_active_initiatives) must skip unreadable /
   non-UTF-8 workspace files instead of crashing the SessionStart/Stop hooks.

Run: cd flow/hooks && python3 -m unittest tests.test_gate_scope_fixes
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import _flow_state as fs  # noqa: E402
import hook_pre_tool_validate as pre  # noqa: E402


def _epic_md(status="🔄"):
    return (
        f"# Epic X\n\n**Status**: {status}\n**Ultimate purpose**: Test purpose\n"
        "**playbook**: feature\n\n## Objective\nTest epic.\n"
    )


def _story_md(status="🔄", extra=""):
    return (
        f"# US-X\n\n**Status**: {status}\n**Ultimate purpose**: Test purpose\n\n"
        f"## Objective\nTest story.\n{extra}"
    )


def _action_md(status="🔄", depends_on=None, retro=""):
    dep = f"**depends_on**: {depends_on}\n" if depends_on is not None else ""
    return (
        f"# A-001\n\n**Status**: {status}\n{dep}**Ultimate purpose**: Test purpose\n\n"
        f"## Objective\nTest action.\n{retro}"
    )


class _WS(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.ws = self.root / ".flow" / "workspace"
        self.ws.mkdir(parents=True)
        self.addCleanup(self._tmp.cleanup)

    def epic(self, name="epic-a", status="🔄"):
        d = self.ws / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "_epic.md").write_text(_epic_md(status), encoding="utf-8")
        return d

    def story(self, epic_dir, name="US-001-t", status="🔄", extra=""):
        d = epic_dir / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "_story.md").write_text(_story_md(status, extra), encoding="utf-8")
        return d

    def action(self, story_dir, name="A-001.md", **kw):
        (story_dir / name).write_text(_action_md(**kw), encoding="utf-8")


class TestCompletedEpicScope(_WS):
    """Finding 1 — ✅ epics must be out of scope for the gate scans."""

    def test_leftover_action_in_completed_epic_does_not_satisfy_rule1(self):
        done = self.epic("epic-done", status="✅")
        s = self.story(done, status="🔄")
        self.action(s, status="🔄")  # leftover in-progress action inside a ✅ epic
        active = self.epic("epic-live", status="🔄")
        self.story(active, status="🔄")  # active story has NO action doc
        self.assertFalse(
            pre.has_action_doc(str(self.root)),
            "a leftover action inside a completed epic must not satisfy no-action-without-doc",
        )

    def test_placeholder_retro_in_completed_epic_does_not_block(self):
        done = self.epic("epic-done", status="✅")
        s = self.story(done, status="🔄")
        self.action(s, status="🔄")  # in-progress action with NO retrospective, in a ✅ epic
        self.assertTrue(
            pre.check_retro_not_empty(str(self.root)),
            "an empty retro inside a completed epic must not block commits",
        )

    def test_missing_review_in_completed_epic_does_not_block(self):
        done = self.epic("epic-done", status="✅")
        s = self.story(done, status="🔄")  # finish window: all actions done, no review section
        self.action(s, status="✅")
        self.assertTrue(
            pre.check_review_eval_recorded(str(self.root)),
            "a missing review inside a completed epic must not block",
        )

    def test_completed_epic_is_not_a_fan_out_target(self):
        done = self.epic("epic-done", status="✅")
        s = self.story(done, status="🔄")
        self.action(s, "A-001.md", status="⬜", depends_on="[]")
        self.action(s, "A-002.md", status="⬜", depends_on="[]")
        self.assertIsNone(
            pre.find_parallel_ready_story(str(self.root)),
            "a story inside a completed epic must not trigger Rule 13",
        )

    def test_active_epic_still_scanned(self):
        live = self.epic("epic-live", status="🔄")
        s = self.story(live, status="🔄")
        self.action(s, status="🔄")
        self.assertTrue(pre.has_action_doc(str(self.root)))


class TestMergeKeywordPrecision(unittest.TestCase):
    """Finding 2 — word-boundary matching + no duplicate keywords."""

    def _transcript(self, *user_texts):
        tmp = tempfile.NamedTemporaryFile(
            "w", suffix=".jsonl", delete=False, encoding="utf-8"
        )
        for t in user_texts:
            tmp.write(json.dumps({"type": "user", "message": {"content": t}}) + "\n")
        tmp.close()
        self.addCleanup(os.unlink, tmp.name)
        return tmp.name

    def test_no_duplicate_keywords(self):
        self.assertEqual(
            len(pre.USER_MERGE_KEYWORDS),
            len(set(pre.USER_MERGE_KEYWORDS)),
            "USER_MERGE_KEYWORDS contains exact duplicates",
        )

    def test_substring_inside_word_is_not_authorization(self):
        path = self._transcript("the pushover pattern is interesting to summarize")
        self.assertFalse(
            pre.user_requested_shared_merge(path),
            "'pushover' must not count as a 'push' instruction",
        )

    def test_real_instruction_still_detected(self):
        path = self._transcript("looks good — please push to main")
        self.assertTrue(pre.user_requested_shared_merge(path))


class TestReviewMarkerAnchored(_WS):
    """Finding 3 — the review marker must be a heading, not prose / an HTML comment."""

    def _finish_window_story(self, extra):
        live = self.epic("epic-live", status="🔄")
        s = self.story(live, status="🔄", extra=extra)
        self.action(s, status="✅")
        return s

    def test_prose_mention_is_not_a_review_record(self):
        self._finish_window_story(
            "\nLater we plan the Review & Evaluation session with the team and"
            " everyone joins to discuss the deliverable quality in detail.\n"
        )
        self.assertFalse(
            pre.check_review_eval_recorded(str(self.root)),
            "a prose mention of 'Review & Evaluation' is not a recorded review",
        )

    def test_marker_inside_html_comment_is_not_a_review_record(self):
        self._finish_window_story(
            "\n<!--\n## Review & evaluation\nfill this in before finishing the story\n-->\n"
        )
        self.assertFalse(
            pre.check_review_eval_recorded(str(self.root)),
            "a commented-out template marker is not a recorded review",
        )

    def test_real_heading_passes(self):
        self._finish_window_story(
            "\n## Review & evaluation\nAC-1 pass confirmed, deliverables reviewed"
            " thoroughly — review result recorded.\n"
        )
        self.assertTrue(pre.check_review_eval_recorded(str(self.root)))

    def test_slash_variant_heading_passes(self):
        self._finish_window_story(
            "\n## Review/Evaluation\nAC-1 pass confirmed, deliverables reviewed"
            " thoroughly — review result recorded.\n"
        )
        self.assertTrue(pre.check_review_eval_recorded(str(self.root)))


class TestUnreadableWorkspaceFiles(_WS):
    """Finding 4 (CRITICAL) — non-UTF-8 workspace files must be skipped, not crash."""

    BAD = b"\xff\xfe\x80 not utf-8 \x9c"

    def test_binary_epic_file_skipped(self):
        d = self.ws / "epic-bad"
        d.mkdir()
        (d / "_epic.md").write_bytes(self.BAD)
        self.assertIsNone(fs.parse_epic(str(d), "epic-bad"))  # must not raise

    def test_binary_story_file_skipped(self):
        d = self.epic("epic-live", status="🔄")
        sd = d / "US-001-t"
        sd.mkdir()
        (sd / "_story.md").write_bytes(self.BAD)
        epic = fs.parse_epic(str(d), "epic-live")  # must not raise
        self.assertIsNotNone(epic)
        self.assertEqual(epic["stories"], [])

    def test_binary_action_file_skipped(self):
        d = self.epic("epic-live", status="🔄")
        s = self.story(d, status="🔄")
        (s / "A-001.md").write_bytes(self.BAD)
        epic = fs.parse_epic(str(d), "epic-live")  # must not raise
        self.assertIsNotNone(epic)
        self.assertEqual(epic["stories"][0]["actions"], [])

    def test_binary_initiative_file_skipped(self):
        d = self.ws / "initiative-bad"
        d.mkdir()
        (d / "_initiative.md").write_bytes(self.BAD)
        self.assertEqual(fs.find_active_initiatives(str(self.root)), [])  # must not raise


if __name__ == "__main__":
    unittest.main()
