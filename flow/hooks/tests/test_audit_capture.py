#!/usr/bin/env python3
"""TS-001 A-001 capture extension — audit schema tests (stdlib unittest, 0 dependencies).

Under test:
- active_unit_id: single attribution to the deepest 🔄 node id (both US-/TS-, multi-🔄 tie-break rule, none)
- post record: unit_id + (for Skill) skill tagging
- pre (deny/ask) record: blocked_rule extraction + allow emits no record
- append_audit: one shared append line

Run: cd flow/hooks && python3 -m unittest tests.test_audit_capture
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

import _flow_state as ws  # noqa: E402
import post_tool_validate as post  # noqa: E402
import hook_pre_tool_validate as pre  # noqa: E402


def _write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


EPIC_INPROGRESS = "# Epic: T\n\n**Status**: 🔄\n**Branch**: `epic/t`\n"
STORY_INPROGRESS = "# Story: S\n\n**Story**: TS-001-m\n**Status**: 🔄\n"
STORY_DONE = "# Story: S\n\n**Story**: TS-001-m\n**Status**: ✅\n"
ACTION_INPROGRESS = "# Action: A\n\n**Action**: A-002\n**Status**: 🔄\n"
ACTION_DONE = "# Action: A\n\n**Action**: A-001\n**Status**: ✅\n"


class TestActiveUnitId(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.epic = os.path.join(self.tmp, ".flow", "workspace", "epic-t")

    # deepest 🔄 = action (a TS- story must be scanned too)
    def test_deepest_inprogress_action_ts_story(self):
        _write(os.path.join(self.epic, "_epic.md"), EPIC_INPROGRESS)
        _write(os.path.join(self.epic, "TS-001-m", "_story.md"), STORY_INPROGRESS)
        _write(os.path.join(self.epic, "TS-001-m", "A-001.md"), ACTION_DONE)
        _write(os.path.join(self.epic, "TS-001-m", "A-002.md"), ACTION_INPROGRESS)
        self.assertEqual(
            ws.active_unit_id(self.tmp), "epic-t/TS-001-m/A-002",
            "must attribute solely to the deepest 🔄 Action (TS- story)",
        )

    # a US- story is scanned the same way
    def test_us_story_scanned(self):
        _write(os.path.join(self.epic, "_epic.md"), EPIC_INPROGRESS)
        _write(os.path.join(self.epic, "US-001-f", "_story.md"), STORY_INPROGRESS)
        _write(os.path.join(self.epic, "US-001-f", "A-001.md"), ACTION_INPROGRESS)
        self.assertEqual(ws.active_unit_id(self.tmp), "epic-t/US-001-f/A-001")

    # no 🔄 action → attribute to the 🔄 story
    def test_story_when_no_inprogress_action(self):
        _write(os.path.join(self.epic, "_epic.md"), EPIC_INPROGRESS)
        _write(os.path.join(self.epic, "TS-001-m", "_story.md"), STORY_INPROGRESS)
        _write(os.path.join(self.epic, "TS-001-m", "A-001.md"), ACTION_DONE)
        self.assertEqual(ws.active_unit_id(self.tmp), "epic-t/TS-001-m")

    # no 🔄 story → attribute to the 🔄 epic
    def test_epic_when_no_inprogress_story(self):
        _write(os.path.join(self.epic, "_epic.md"), EPIC_INPROGRESS)
        _write(os.path.join(self.epic, "TS-001-m", "_story.md"), STORY_DONE)
        self.assertEqual(ws.active_unit_id(self.tmp), "epic-t")

    # no workspace → None
    def test_none_when_no_workspace(self):
        self.assertIsNone(ws.active_unit_id(self.tmp))


class TestAppendAudit(unittest.TestCase):
    def test_append_writes_line(self):
        tmp = tempfile.mkdtemp()
        ws.append_audit(tmp, {"tool": "Bash", "success": True})
        path = os.path.join(ws.runtime_dir(tmp), ws.AUDIT_FILE)
        with open(path, encoding="utf-8") as f:
            lines = f.read().strip().split("\n")
        self.assertEqual(json.loads(lines[-1])["tool"], "Bash")


class TestPostEntry(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        epic = os.path.join(self.tmp, ".flow", "workspace", "epic-t")
        _write(os.path.join(epic, "_epic.md"), EPIC_INPROGRESS)
        _write(os.path.join(epic, "TS-001-m", "_story.md"), STORY_INPROGRESS)
        _write(os.path.join(epic, "TS-001-m", "A-002.md"), ACTION_INPROGRESS)

    def test_post_entry_has_unit_id_and_base_fields(self):
        e = post.build_entry(
            {"tool_name": "Bash", "tool_response": {}}, self.tmp
        )
        self.assertEqual(e["tool"], "Bash")
        self.assertTrue(e["success"])
        self.assertEqual(e["unit_id"], "epic-t/TS-001-m/A-002")
        self.assertNotIn("skill", e)  # non-Skill tools have no skill key

    def test_post_entry_skill_tagged(self):
        e = post.build_entry(
            {"tool_name": "Skill", "tool_response": {},
             "tool_input": {"skill": "flow:flow"}},
            self.tmp,
        )
        self.assertEqual(e["skill"], "flow:flow")

    def test_post_entry_success_false_on_error(self):
        e = post.build_entry(
            {"tool_name": "Read", "tool_response": {"isError": True}}, self.tmp
        )
        self.assertFalse(e["success"])


class TestBlockEntry(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_deny_entry_extracts_blocked_rule(self):
        output = {"hookSpecificOutput": {
            "permissionDecision": "deny",
            "permissionDecisionReason": "flow rule violation (no-node-without-purpose): ...",
        }}
        e = pre.build_block_entry({"tool_name": "Write"}, output, self.tmp)
        self.assertEqual(e["blocked_rule"], "no-node-without-purpose")
        self.assertEqual(e["decision"], "deny")
        self.assertEqual(e["tool"], "Write")

    def test_allow_returns_none(self):
        output = {"hookSpecificOutput": {"permissionDecision": "allow"}}
        self.assertIsNone(pre.build_block_entry({"tool_name": "Read"}, output, self.tmp))

    def test_unknown_rule_when_no_match(self):
        output = {"hookSpecificOutput": {
            "permissionDecision": "ask",
            "permissionDecisionReason": "just a confirmation request (no rule id pattern)",
        }}
        e = pre.build_block_entry({"tool_name": "Bash"}, output, self.tmp)
        self.assertEqual(e["blocked_rule"], "unknown")
        self.assertEqual(e["decision"], "ask")


class TestBlockedRuleCoverage(unittest.TestCase):
    """H2 regression guard: every deny/ask permissionDecisionReason in the source
    must have its rule name caught by BLOCKED_RULE_RE (an un-tagged reason → prevents unknown pollution).
    Stronger than driving individual validate() calls — exhaustive over all current + future reasons."""

    def test_all_deny_reasons_carry_rule_id(self):
        src_path = os.path.join(HOOKS_DIR, "hook_pre_tool_validate.py")
        with open(src_path, encoding="utf-8") as f:
            src = f.read()
        import re
        misses = []
        for m in re.finditer(r'permissionDecisionReason"\s*:\s*\(', src):
            chunk = src[m.end():m.end() + 500]
            literals = re.findall(r'"((?:[^"\\]|\\.)*)"', chunk)
            joined = "".join(literals)
            if not pre.BLOCKED_RULE_RE.search(joined):
                misses.append(joined[:50])
        self.assertEqual(
            misses, [],
            f"{len(misses)} deny/ask reason(s) missing a rule name (unknown pollution): {misses}",
        )


class TestPostMainCrashSafe(unittest.TestCase):
    """H1 regression guard: even if the measurement scan (active_unit_id) raises, the post hook
    must always emit {} to stdout (hook non-blocking — an add-on cannot break the core function)."""

    def test_main_emits_empty_when_scan_raises(self):
        import io
        import post_tool_validate as p
        orig_scan = p.active_unit_id
        orig_stdin, orig_stdout = sys.stdin, sys.stdout
        p.active_unit_id = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
        sys.stdin = io.StringIO('{"tool_name":"Bash","tool_response":{}}')
        sys.stdout = io.StringIO()
        try:
            p.main()  # test fails if the exception propagates
            out = sys.stdout.getvalue().strip()
        finally:
            p.active_unit_id = orig_scan
            sys.stdin, sys.stdout = orig_stdin, orig_stdout
        self.assertEqual(out, "{}", "the post hook must emit {} even if the scan dies")


if __name__ == "__main__":
    unittest.main()
