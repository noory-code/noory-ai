#!/usr/bin/env python3
"""Regression tests for the 5 disk-state-dependent PreToolUse rules (stdlib unittest, zero dependencies).

Unlike the pure-function rules (test_pre_tool_rules.py), these 5 judge by reading the
`.flow/workspace/` tree + header status markers → a fake workspace fixture is
required. T1 safety net: if a later hook refactor / rule change silently breaks the
deny/allow behavior, it is caught here.

Targets (validate() end-to-end):
- Rule 1 no-action-without-doc
- Rule 3 no-push-workspace (ask)
- Rule 6 no-story-without-action-doc
- Rule 7 no-merge-without-review
- Rule 8 no-work-without-playbook
+ self-status pollution regression (header status is not polluted by a child node's ✅)

Run: cd flow/hooks && python3 -m unittest tests.test_disk_state_rules
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import hook_pre_tool_validate as pre  # noqa: E402


# ----- fixture helpers -----

def _epic_md(status="🔄", playbook=True):
    body = f"# Epic X\n\n**Status**: {status}\n**Ultimate purpose**: Test purpose\n"
    if playbook:
        body += "**playbook**: feature\n"
    body += "\n## Objective\nTest epic.\n"
    return body


def _story_md(status="🔄", review=False):
    body = f"# US-X\n\n**Status**: {status}\n**Ultimate purpose**: Test purpose\n\n## Objective\nTest story.\n"
    if review:
        body += "\n## Review & evaluation\nAC-1 pass confirmed, deliverables reviewed — review result recorded.\n"
    return body


def _action_md(status="🔄", retro=False):
    body = f"# A-001\n\n**Status**: {status}\n**Ultimate purpose**: Test purpose\n\n## Objective\nTest action.\n"
    if retro:
        body += "\n## Retrospective\n### Keep\n- Followed the procedure well; proceeded with zero guessing.\n"
    return body


class _Workspace:
    """Context helper that builds a fake .flow/workspace tree in a tmp directory."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.ws = self.root / ".flow" / "workspace"
        self.ws.mkdir(parents=True)

    def epic(self, name="epic-test", **kw):
        d = self.ws / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "_epic.md").write_text(_epic_md(**kw), encoding="utf-8")
        return d

    def story(self, epic_dir, name="US-001-test", **kw):
        d = epic_dir / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "_story.md").write_text(_story_md(**kw), encoding="utf-8")
        return d

    def top_story(self, name="story-test", **kw):
        d = self.ws / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "_story.md").write_text(_story_md(**kw), encoding="utf-8")
        return d

    def action(self, story_dir, name="A-001.md", **kw):
        (story_dir / name).write_text(_action_md(**kw), encoding="utf-8")

    def archive(self, name="epic-test"):
        """Marks that a completed unit's retrospective has been extracted/consolidated into .flow/archives/retro-<name>.md.

        flow-archive v2.0.0: the existence of a flat retro-{unit name}.md file (no folder) determines archival.
        """
        arch = self.root / ".flow" / "archives"
        arch.mkdir(parents=True, exist_ok=True)
        f = arch / f"retro-{name}.md"
        f.write_text("# retro: epic-test\n", encoding="utf-8")
        return f

    def close(self):
        self._tmp.cleanup()


def _validate(ws, tool_name, tool_input, command=None, extra=None):
    """Call validate() with CLAUDE_PROJECT_DIR cleared and workspace_root injected via cwd."""
    if command is not None:
        tool_input = dict(tool_input, command=command)
    data = {"tool_name": tool_name, "tool_input": tool_input, "cwd": str(ws.root)}
    if extra:
        data.update(extra)
    env = dict(os.environ)
    env.pop("CLAUDE_PROJECT_DIR", None)
    with mock.patch.dict(os.environ, env, clear=True):
        return pre.validate(data)


def _decision(result):
    return result["hookSpecificOutput"]["permissionDecision"]


class _WSBase(unittest.TestCase):
    def setUp(self):
        self.ws = _Workspace()
        self.addCleanup(self.ws.close)

    def src(self, rel):
        """Build a protected (absolute) path relative to workspace_root."""
        return str(self.ws.root / rel)


class TestNoActionWithoutDoc(_WSBase):
    """Rule 1 — an active Epic + protected source edits require an in-progress A-NNN.md."""

    def test_no_action_doc_denies(self):
        e = self.ws.epic()  # 🔄, playbook
        self.ws.story(e, status="✅")  # story complete → no in-progress action
        r = _validate(self.ws, "Write", {"file_path": self.src("plugins/x/foo.py"), "content": "x"})
        self.assertEqual(_decision(r), "deny")

    def test_with_action_doc_allows(self):
        e = self.ws.epic()  # 🔄, has playbook (avoids Rule 8)
        s = self.ws.story(e)
        self.ws.action(s, status="🔄")  # in-progress action exists
        r = _validate(self.ws, "Write", {"file_path": self.src("plugins/x/foo.py"), "content": "x"})
        self.assertEqual(_decision(r), "allow")

    def test_src_without_action_doc_denies(self):
        e = self.ws.epic()  # 🔄, playbook
        self.ws.story(e, status="✅")  # story complete → no in-progress action
        r = _validate(self.ws, "Write", {"file_path": self.src("src/foo.py"), "content": "x"})
        self.assertEqual(_decision(r), "deny")


class TestNoPushWorkspace(_WSBase):
    """Rule 3 — check for workspace contamination on git push (ask)."""

    def test_push_asks(self):
        self.ws.epic()  # active epic required
        r = _validate(self.ws, "Bash", {}, command="git push origin feature-x")
        self.assertEqual(_decision(r), "ask")

    def test_push_denies_on_codex_payload(self):
        self.ws.epic()  # active epic required
        r = _validate(
            self.ws,
            "Bash",
            {},
            command="git push origin feature-x",
            extra={"turn_id": "t-1", "permission_mode": "default"},
        )
        self.assertEqual(_decision(r), "deny")

    def test_push_still_asks_on_claude_payload_with_permission_mode(self):
        # permission_mode is a Claude Code COMMON hook field (present in every real
        # payload) — it must NOT flip the ask gate to deny. Only turn_id marks Codex.
        self.ws.epic()
        r = _validate(
            self.ws,
            "Bash",
            {},
            command="git push origin feature-x",
            extra={"permission_mode": "default", "session_id": "s", "hook_event_name": "PreToolUse"},
        )
        self.assertEqual(_decision(r), "ask")

    def test_non_push_allows(self):
        self.ws.epic()
        r = _validate(self.ws, "Bash", {}, command="git status")
        self.assertEqual(_decision(r), "allow")


class TestNoStoryWithoutActionDoc(_WSBase):
    """Rule 6 — if an active 🔄 Story has 0 A-*.md files, block edits to non-SSOT files."""

    def test_missing_action_doc_denies(self):
        e = self.ws.epic()
        self.ws.story(e, status="🔄")  # 🔄 story, 0 actions
        # Rule 1 and Rule 6 both protect /src/; the important contract is deny.
        r = _validate(self.ws, "Write", {"file_path": self.src("src/foo.py"), "content": "x"})
        self.assertEqual(_decision(r), "deny")

    def test_with_action_doc_allows(self):
        e = self.ws.epic()
        s = self.ws.story(e, status="🔄")
        self.ws.action(s, status="🔄")  # action exists → passes Rule 6
        r = _validate(self.ws, "Write", {"file_path": self.src("src/foo.py"), "content": "x"})
        self.assertEqual(_decision(r), "allow")


class TestNoMergeWithoutReview(_WSBase):
    """Rule 7 — if a Story's Actions are all ✅ but _story.md has no review/evaluation, block commit."""

    def test_finish_without_review_denies(self):
        e = self.ws.epic()
        s = self.ws.story(e, status="🔄", review=False)  # no review
        self.ws.action(s, status="✅", retro=True)  # all actions ✅ + retrospective filled
        r = _validate(self.ws, "Bash", {}, command="git commit -m x")
        self.assertEqual(_decision(r), "deny")

    def test_finish_with_review_allows(self):
        e = self.ws.epic()
        s = self.ws.story(e, status="🔄", review=True)  # review/evaluation recorded
        self.ws.action(s, status="✅", retro=True)
        r = _validate(self.ws, "Bash", {}, command="git commit -m x")
        self.assertEqual(_decision(r), "allow")


class TestNoWorkWithoutPlaybook(_WSBase):
    """Rule 8 — in the execution stage (in-progress Action), block if the playbook field is absent."""

    def test_no_playbook_denies(self):
        e = self.ws.epic(playbook=False)  # no playbook field
        s = self.ws.story(e)
        self.ws.action(s, status="🔄")  # has_action_doc True → execution stage
        r = _validate(self.ws, "Write", {"file_path": self.src("plugins/x/foo.py"), "content": "x"})
        self.assertEqual(_decision(r), "deny")

    def test_with_playbook_allows(self):
        e = self.ws.epic(playbook=True)
        s = self.ws.story(e)
        self.ws.action(s, status="🔄")
        r = _validate(self.ws, "Write", {"file_path": self.src("plugins/x/foo.py"), "content": "x"})
        self.assertEqual(_decision(r), "allow")


class TestTechnicalStoryRecognized(_WSBase):
    """Epic 3 US-003 — whether the hook's [UT]S-* glob recognizes a TS-NNN (Technical Story)
    directory the same as US (regression for the added TS type)."""

    def test_ts_story_missing_action_doc_denies(self):
        # TS-001 story 🔄 + 0 actions → no-story-without-action-doc fires (TS recognized)
        e = self.ws.epic()
        self.ws.story(e, name="TS-001-test", status="🔄")
        r = _validate(self.ws, "Write", {"file_path": self.src("src/foo.py"), "content": "x"})
        self.assertEqual(_decision(r), "deny")

    def test_ts_story_action_doc_found(self):
        # TS-001's A-001 🔄 → has_action_doc True (detects A-* inside a TS directory)
        e = self.ws.epic()
        s = self.ws.story(e, name="TS-001-test", status="🔄")
        self.ws.action(s, status="🔄")
        self.assertTrue(pre.has_action_doc(str(self.ws.root)))


class TestNoShellNodeWrite(_WSBase):
    """Rule 10 — block creating a workspace node via shell redirection (>/>>/tee) (best-effort)."""

    def test_redirect_to_node_denies(self):
        for cmd in [
            "cat x > .flow/workspace/epic-a/US-1/_story.md",
            "echo y >> .flow/workspace/epic-a/_epic.md",
            "tee .flow/workspace/epic-a/US-1/A-001.md",
        ]:
            with self.subTest(cmd=cmd):
                r = _validate(self.ws, "Bash", {}, command=cmd)
                self.assertEqual(_decision(r), "deny")

    def test_pure_function_detects(self):
        self.assertTrue(pre.shell_writes_workspace_node(
            "echo x > .flow/workspace/epic-a/US-1/_story.md"))

    def test_non_node_redirect_allows(self):
        for cmd in [
            "echo x > /tmp/foo.txt",                 # not a node path
            "cat .flow/workspace/epic-a/_epic.md",  # no redirect (read)
            "grep foo bar.py > out.txt",
            # false-positive regression: an unrelated redirect (2>&1) + a node path elsewhere must pass
            "pytest 2>&1 | tail; grep x .flow/workspace/epic-a/_initiative.md",
            "cmd 2>&1 | grep .flow/workspace/epic-a/US-1/_story.md",
        ]:
            with self.subTest(cmd=cmd):
                self.assertFalse(pre.shell_writes_workspace_node(cmd), cmd)


class TestSelfStatusPollution(_WSBase):
    """self-status pollution regression — header status is not polluted by a child node's ✅."""

    def test_completed_epic_header_not_active(self):
        # epic header ✅ + child story 🔄 → the epic should be seen as complete (inactive)
        e = self.ws.epic(status="✅")
        self.ws.story(e, status="🔄")
        self.assertFalse(pre.has_active_epic(str(self.ws.root)))

    def test_inprogress_epic_with_done_children_active(self):
        # epic header 🔄 + child story/action ✅ → the epic is still active
        e = self.ws.epic(status="🔄")
        s = self.ws.story(e, status="✅")
        self.ws.action(s, status="✅")
        self.assertTrue(pre.has_active_epic(str(self.ws.root)))


class TestNoFinishWithoutArchive(_WSBase):
    """Rule 11 — if a completed (✅) work item is unarchived, block PR creation / shared-branch merge."""

    def _reason(self, r):
        return r["hookSpecificOutput"]["permissionDecisionReason"]

    def test_pr_with_unarchived_complete_denies(self):
        self.ws.epic(status="✅")  # epic-test complete, no archives
        r = _validate(self.ws, "Bash", {}, command="gh pr create --base main --title x")
        self.assertEqual(_decision(r), "deny")
        # prove Rule 11 blocked it (no other rule masks it — gh pr is not a Rule 5 target)
        self.assertIn("no-finish-without-archive", self._reason(r))

    def test_copilot_terminal_pr_with_unarchived_complete_denies(self):
        self.ws.epic(status="✅")  # epic-test complete, no archives
        r = _validate(self.ws, "run_in_terminal", {}, command="gh pr create --base main --title x")
        self.assertEqual(_decision(r), "deny")
        self.assertIn("no-finish-without-archive", self._reason(r))

    def test_shared_merge_after_user_request_hits_rule11(self):
        # A shared-branch merge is checked by Rule 5 first → after passing Rule 5 via an explicit
        # user request (transcript), verify Rule 11 (unarchived) fires on its own. (Prevents Rule 5 masking it.)
        self.ws.epic(status="✅")
        tpath = self.ws.root / "transcript.jsonl"
        tpath.write_text(
            '{"type":"user","message":{"content":"please merge into main"}}\n', encoding="utf-8")
        env = dict(os.environ); env.pop("CLAUDE_PROJECT_DIR", None)
        data = {"tool_name": "Bash",
                "tool_input": {"command": "git push origin main"},
                "cwd": str(self.ws.root), "transcript_path": str(tpath)}
        with mock.patch.dict(os.environ, env, clear=True):
            r = pre.validate(data)
        self.assertEqual(_decision(r), "deny")
        self.assertIn("no-finish-without-archive", self._reason(r))

    def test_pr_after_archive_allows(self):
        self.ws.epic(status="✅")
        self.ws.archive("epic-test")  # retrospective retro.md extracted
        r = _validate(self.ws, "Bash", {}, command="gh pr create --base main --title x")
        self.assertEqual(_decision(r), "allow")

    def test_copilot_terminal_pr_after_archive_allows(self):
        self.ws.epic(status="✅")
        self.ws.archive("epic-test")  # retrospective retro.md extracted
        r = _validate(self.ws, "run_in_terminal", {}, command="gh pr create --base main --title x")
        self.assertEqual(_decision(r), "allow")

    def test_other_retro_without_own_denies(self):
        # Flat model: even if another item's retro-*.md is in archives/, if this unit's retro-{name}.md is absent, deny.
        # (prevents parallel collisions — each item has a unique retro-{name}.md)
        self.ws.epic(status="✅")
        arch = self.ws.root / ".flow" / "archives"
        arch.mkdir(parents=True, exist_ok=True)
        (arch / "retro-other-epic.md").write_text("# other\n", encoding="utf-8")  # another item's retrospective
        # retro-epic-test.md not created
        r = _validate(self.ws, "Bash", {}, command="gh pr create --base main --title x")
        self.assertEqual(_decision(r), "deny")
        self.assertIn("no-finish-without-archive", self._reason(r))

    def test_story_archive_must_keep_workspace_prefix(self):
        # <name> in completed_unarchived is the workspace directory basename verbatim.
        # story-agent-teams-model → only retro-story-agent-teams-model.md passes;
        # retro-agent-teams-model.md (with a guessed prefix stripped) must not pass.
        self.ws.top_story(name="story-agent-teams-model", status="✅")
        self.ws.archive("agent-teams-model")
        r = _validate(self.ws, "run_in_terminal", {}, command="gh pr create --base main --title x")
        self.assertEqual(_decision(r), "deny")
        self.assertIn("no-finish-without-archive", self._reason(r))

        self.ws.archive("story-agent-teams-model")
        r = _validate(self.ws, "run_in_terminal", {}, command="gh pr create --base main --title x")
        self.assertEqual(_decision(r), "allow")

    def test_non_pr_command_not_blocked_by_archive(self):
        self.ws.epic(status="✅")  # unarchived, but
        r = _validate(self.ws, "Bash", {}, command="git status")  # not a PR/merge
        self.assertEqual(_decision(r), "allow")

    def test_inprogress_epic_no_archive_gate(self):
        self.ws.epic(status="🔄")  # in progress = not complete → archive gate irrelevant
        r = _validate(self.ws, "Bash", {}, command="gh pr create --base main --title x")
        self.assertEqual(_decision(r), "allow")

    def test_pure_helper_lists_unarchived(self):
        self.ws.epic(status="✅")
        self.assertIn("epic-test", pre.completed_unarchived(str(self.ws.root)))
        self.ws.archive("epic-test")
        self.assertNotIn("epic-test", pre.completed_unarchived(str(self.ws.root)))

    def test_creates_pr_detection(self):
        # detect PR-creation triggers (best-effort): gh pr create / gh api ...pulls
        self.assertTrue(pre.creates_pr("gh pr create -B main -t x"))
        self.assertTrue(pre.creates_pr("gh api repos/o/r/pulls -f title=x"))
        self.assertFalse(pre.creates_pr("gh issue list"))
        self.assertFalse(pre.creates_pr("git status"))


if __name__ == "__main__":
    unittest.main()
