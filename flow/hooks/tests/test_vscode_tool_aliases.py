#!/usr/bin/env python3
"""VS Code Copilot tool-alias regression test.

Verifies that the flow hook does not fail-open when, in the VS Code/Copilot environment, a file edit comes in
under a tool_name different from Claude Code's, such as `apply_patch`.
"""
from __future__ import annotations

import os
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import hook_pre_tool_validate as pre  # noqa: E402

PURPOSE = "**Ultimate purpose**: test purpose"


def _epic_md(status="🔄", playbook=True):
    body = f"# Epic\n\n**Status**: {status}\n{PURPOSE}\n"
    if playbook:
        body += "**playbook**: docs\n"
    return body


def _story_md(status="🔄"):
    return f"# Story\n\n**Status**: {status}\n{PURPOSE}\n"


def _action_md(status="🔄"):
    return f"# Action\n\n**Status**: {status}\n{PURPOSE}\n\n## Retrospective\n### Keep\n- test retro content is sufficient.\n"


class _Workspace:
    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.ws = self.root / ".flow" / "workspace"
        self.ws.mkdir(parents=True)

    def close(self):
        self._tmp.cleanup()

    def epic(self, name="epic-test", **kw):
        d = self.ws / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "_epic.md").write_text(_epic_md(**kw), encoding="utf-8")
        return d

    def story(self, epic_dir, name="TS-001-test", **kw):
        d = epic_dir / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "_story.md").write_text(_story_md(**kw), encoding="utf-8")
        return d

    def action(self, story_dir, name="A-001.md", **kw):
        (story_dir / name).write_text(_action_md(**kw), encoding="utf-8")

    def src(self, rel: str) -> str:
        return str(self.root / rel)


def _validate(ws: _Workspace, tool_name: str, tool_input: dict):
    data = {"tool_name": tool_name, "tool_input": tool_input, "cwd": str(ws.root)}
    env = dict(os.environ)
    env.pop("CLAUDE_PROJECT_DIR", None)
    with mock.patch.dict(os.environ, env, clear=True):
        return pre.validate(data)


def _decision(result):
    return result["hookSpecificOutput"]["permissionDecision"]


def _apply_patch_input(*blocks: str) -> dict:
    return {"input": "\n".join(["*** Begin Patch", *blocks, "*** End Patch"])}


class TestApplyPatchAlias(unittest.TestCase):
    def setUp(self):
        self.ws = _Workspace()
        self.addCleanup(self.ws.close)

    def test_apply_patch_update_plugins_without_action_doc_denies(self):
        e = self.ws.epic()
        self.ws.story(e, status="✅")
        patch = _apply_patch_input(
            f"*** Update File: {self.ws.src('plugins/x/foo.py')}",
            "-old",
            "+new",
        )
        r = _validate(self.ws, "apply_patch", patch)
        self.assertEqual(_decision(r), "deny")

    def test_apply_patch_update_src_missing_action_doc_denies(self):
        e = self.ws.epic()
        self.ws.story(e, status="🔄")  # 0 actions
        patch = _apply_patch_input(
            f"*** Update File: {self.ws.src('src/foo.py')}",
            "-old",
            "+new",
        )
        r = _validate(self.ws, "apply_patch", patch)
        self.assertEqual(_decision(r), "deny")

    def test_apply_patch_update_without_playbook_denies(self):
        e = self.ws.epic(playbook=False)
        s = self.ws.story(e, status="🔄")
        self.ws.action(s, status="🔄")
        patch = _apply_patch_input(
            f"*** Update File: {self.ws.src('plugins/x/foo.py')}",
            "-old",
            "+new",
        )
        r = _validate(self.ws, "apply_patch", patch)
        self.assertEqual(_decision(r), "deny")

    def test_apply_patch_add_action_without_purpose_denies(self):
        path = self.ws.src(".flow/workspace/epic-x/TS-001-test/A-001.md")
        patch = _apply_patch_input(
            f"*** Add File: {path}",
            "+**Action**: A-001",
            "+**Status**: ⬜",
        )
        r = _validate(self.ws, "apply_patch", patch)
        self.assertEqual(_decision(r), "deny")

    def test_apply_patch_add_action_with_purpose_allows(self):
        # A-NNN.md must pass both Rule 9 (purpose) and Rule 12 (depends_on) to allow.
        # 0.12.0 RT-FIX (PR #24): added the Rule 12 apply_patch branch — depends_on must accompany it.
        path = self.ws.src(".flow/workspace/epic-x/TS-001-test/A-001.md")
        patch = _apply_patch_input(
            f"*** Add File: {path}",
            f"+{PURPOSE}",
            "+**Action**: A-001",
            "+**depends_on**: []",
            "+**Status**: ⬜",
        )
        r = _validate(self.ws, "apply_patch", patch)
        self.assertEqual(_decision(r), "allow")

    def test_extract_patch_files_multiple_blocks(self):
        patch = _apply_patch_input(
            "*** Update File: /tmp/a.md",
            "-a",
            "+b",
            "*** Add File: /tmp/b.md",
            "+hello",
        )
        self.assertEqual(pre.extract_tool_file_paths("apply_patch", patch), ["/tmp/a.md", "/tmp/b.md"])


class TestEditFilesAlias(unittest.TestCase):
    def setUp(self):
        self.ws = _Workspace()
        self.addCleanup(self.ws.close)

    def test_edit_files_alias_extracts_files_array(self):
        e = self.ws.epic()
        self.ws.story(e, status="✅")
        r = _validate(self.ws, "editFiles", {"files": [self.ws.src("plugins/x/foo.py")]})
        self.assertEqual(_decision(r), "deny")


if __name__ == "__main__":
    unittest.main()
