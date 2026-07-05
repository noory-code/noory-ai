#!/usr/bin/env python3
"""Retrospective rigor-label regression — `flow-retrospective` Part 4 §4-8 hook mapping.

Targets:
- `_flow_state.read_retrospective_settings` (SSOT shared by 4 hooks — fail-safe + §4-4 guard)
- `hook_pre_tool_validate.check_retro_not_empty` (Rule 2 label branch — A-001 scope)

Rule 11 branch + additional scenarios to be reinforced in A-002.

Run: cd flow/hooks && python3 -m unittest tests.test_retro_rigor
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stderr
from pathlib import Path

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import _flow_state as ws  # noqa: E402
import hook_pre_tool_validate as pre  # noqa: E402


# ----- fixture helpers -----

def _action_md(status="🔄", retro_body=None):
    body = f"# A-001\n\n**Status**: {status}\n**Ultimate purpose**: test purpose\n\n## Goal\ntest action.\n"
    if retro_body is not None:
        body += "\n## Retrospective\n" + retro_body
    return body


def _epic_md():
    return (
        "# Epic X\n\n**Status**: 🔄\n**Ultimate purpose**: test\n"
        "**playbook**: feature\n\n## Goal\ntest epic.\n"
    )


def _story_md():
    return (
        "# US-X\n\n**Status**: 🔄\n**Ultimate purpose**: test\n\n## Goal\ntest story.\n"
    )


class _Workspace:
    """`.flow/workspace` tree fixture in a tmp directory (parity with the test_disk_state_rules.py pattern)."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.ws = self.root / ".flow" / "workspace"
        self.ws.mkdir(parents=True)

    def write_settings(self, payload):
        settings_dir = self.root / ".flow"
        settings_dir.mkdir(exist_ok=True)
        (settings_dir / "settings.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )

    def write_raw_settings(self, raw: str):
        settings_dir = self.root / ".flow"
        settings_dir.mkdir(exist_ok=True)
        (settings_dir / "settings.json").write_text(raw, encoding="utf-8")

    def action(self, retro_body=None, status="🔄", name="A-001.md"):
        epic_dir = self.ws / "epic-test"
        story_dir = epic_dir / "TS-001-test"
        story_dir.mkdir(parents=True, exist_ok=True)
        (epic_dir / "_epic.md").write_text(_epic_md(), encoding="utf-8")
        (story_dir / "_story.md").write_text(_story_md(), encoding="utf-8")
        (story_dir / name).write_text(_action_md(status=status, retro_body=retro_body), encoding="utf-8")
        return story_dir

    def cleanup(self):
        self._tmp.cleanup()


# ===== A. read_retrospective_settings — fail-safe + §4-4 guard =====

class ReaderFailSafeTests(unittest.TestCase):
    """4 fail-safe cases + initiative guard. Zero exceptions thrown in any case."""

    def setUp(self):
        self.w = _Workspace()

    def tearDown(self):
        self.w.cleanup()

    def test_file_absent_returns_default(self):
        """① File absent → return §4-5 default."""
        result = ws.read_retrospective_settings(str(self.w.root))
        self.assertEqual(result, ws.RIGOR_DEFAULT)

    def test_json_parse_error_returns_default(self):
        """② JSON parse failure → return default (no exception)."""
        self.w.write_raw_settings("{invalid json")
        result = ws.read_retrospective_settings(str(self.w.root))
        self.assertEqual(result, ws.RIGOR_DEFAULT)

    def test_retrospective_key_absent_returns_default(self):
        """③ retrospective key absent → default."""
        self.w.write_settings({"playbooks": ["feature"]})
        result = ws.read_retrospective_settings(str(self.w.root))
        self.assertEqual(result, ws.RIGOR_DEFAULT)

    def test_invalid_rigor_value_keeps_default(self):
        """④ Invalid label value → keep the default mapping (other levels apply normally)."""
        self.w.write_settings({
            "retrospective": {
                "levels": {
                    "action": {"rigor": "bogus"},        # invalid → keep default
                    "story":  {"rigor": "minimal"},       # valid → applied
                }
            }
        })
        result = ws.read_retrospective_settings(str(self.w.root))
        self.assertEqual(result["action"], "template")   # default kept
        self.assertEqual(result["story"], "minimal")     # valid value applied

    def test_initiative_none_guard_forces_template_rt(self):
        """§4-4 guard — even with initiative.rigor=none pinned, force template+rt + stderr warning."""
        self.w.write_settings({
            "retrospective": {
                "levels": {"initiative": {"rigor": "none"}}
            }
        })
        buf = io.StringIO()
        with redirect_stderr(buf):
            result = ws.read_retrospective_settings(str(self.w.root))
        self.assertEqual(result["initiative"], "template+rt")
        self.assertIn("WARNING", buf.getvalue())
        self.assertIn("initiative.rigor", buf.getvalue())


# ===== B. check_retro_not_empty — Rule 2 label branch (§4-8 mapping) =====

class Rule2RigorBranchTests(unittest.TestCase):
    """4 labels × retrospective scenarios. §4-1 judgment criteria + §4-8 hook-mapping parity."""

    def setUp(self):
        self.w = _Workspace()

    def tearDown(self):
        self.w.cleanup()

    def _set_action_rigor(self, label):
        self.w.write_settings({
            "retrospective": {"levels": {"action": {"rigor": label}}}
        })

    def test_none_label_passes_even_empty_retro(self):
        """`none` → passes even with an empty retrospective (full exemption)."""
        self._set_action_rigor("none")
        self.w.action(retro_body="")  # retrospective is empty
        self.assertTrue(pre.check_retro_not_empty(str(self.w.root)))

    def test_minimal_label_passes_with_one_line_body(self):
        """`minimal` → passes with no placeholder + body ≥ 1 line."""
        self._set_action_rigor("minimal")
        self.w.action(retro_body="This Action proceeded per the procedure.\n")
        self.assertTrue(pre.check_retro_not_empty(str(self.w.root)))

    def test_minimal_label_rejects_only_placeholder(self):
        """`minimal` → blocked if only a placeholder is present."""
        self._set_action_rigor("minimal")
        self.w.action(retro_body="TODO\n")
        self.assertFalse(pre.check_retro_not_empty(str(self.w.root)))

    def test_template_label_passes_with_kpt(self):
        """`template` → passes with 1+ KPT marker + 5 chars (current behavior — body-line KPT marker)."""
        self._set_action_rigor("template")
        # KPT_MARKER_RE = `^[\s\-*]*(Keep|...)` — matches only when a body line starts with a KPT marker.
        # A `### Keep` header is excluded by the content_lines filter (`l.strip().startswith("#")`).
        self.w.action(retro_body="- Keep: followed the procedure well, proceeded with zero guessing.\n")
        self.assertTrue(pre.check_retro_not_empty(str(self.w.root)))

    def test_template_label_rejects_short_no_kpt(self):
        """`template` → blocked when there's no KPT and the body is short."""
        self._set_action_rigor("template")
        self.w.action(retro_body="Short.\n")
        self.assertFalse(pre.check_retro_not_empty(str(self.w.root)))

    def test_template_rt_label_rejects_missing_r3(self):
        """`template+rt` → blocked when the R3 self-attack result section is absent even with KPT present."""
        self._set_action_rigor("template+rt")
        self.w.action(retro_body="- Keep: followed the procedure well, proceeded with zero guessing.\n")
        self.assertFalse(pre.check_retro_not_empty(str(self.w.root)))

    def test_template_rt_label_passes_with_r3(self):
        """`template+rt` → passes when KPT + the R3 self-attack result section are stated."""
        self._set_action_rigor("template+rt")
        retro = (
            "- Keep: followed the procedure well, proceeded with zero guessing.\n\n"
            "### R3 self-attack result\n- Surface-level Keep 0\n"
        )
        self.w.action(retro_body=retro)
        self.assertTrue(pre.check_retro_not_empty(str(self.w.root)))

    def test_default_settings_absent_acts_as_template(self):
        """settings absent default = template — equivalent to current hook behavior (§4-5 compatibility)."""
        # settings.json not created
        self.w.action(retro_body="- Keep: followed the procedure well, proceeded with zero guessing.\n")
        self.assertTrue(pre.check_retro_not_empty(str(self.w.root)))


# ===== C. detect_level_from_name — Rule 11 §4-8 level branch =====

class DetectLevelTests(unittest.TestCase):
    """Extract the level from the unit directory-name prefix — Rule 11 branch input."""

    def test_initiative_prefix(self):
        self.assertEqual(pre.detect_level_from_name("initiative-foo"), "initiative")

    def test_epic_prefix(self):
        self.assertEqual(pre.detect_level_from_name("epic-bar"), "epic")

    def test_story_default(self):
        """story-* / other prefixes → story default."""
        self.assertEqual(pre.detect_level_from_name("story-baz"), "story")
        self.assertEqual(pre.detect_level_from_name("US-001-foo"), "story")  # standalone story
        self.assertEqual(pre.detect_level_from_name("TS-001-bar"), "story")


# ===== D. Rule 11 — per-level branch of the archive check (§4-8) =====

def _top_node_completed(name, top_fn="_epic.md"):
    """Content of a unit directory's top SSOT node (completed ✅)."""
    return f"# {name}\n\n**Status**: ✅\n**Ultimate purpose**: test\n"


class Rule11ArchiveBranchTests(unittest.TestCase):
    """Per-unit-prefix level branch + initiative reader-guard parity."""

    def setUp(self):
        self.w = _Workspace()

    def tearDown(self):
        self.w.cleanup()

    def _make_completed_unit(self, name, top_fn="_epic.md"):
        """Completed unit directory + top SSOT node (archive not created)."""
        d = self.w.ws / name
        d.mkdir(parents=True, exist_ok=True)
        (d / top_fn).write_text(_top_node_completed(name, top_fn), encoding="utf-8")

    def _validate_pr_create(self):
        """validate() call — gh pr create scenario."""
        input_data = {
            "tool_name": "Bash",
            "tool_input": {"command": "gh pr create --title test --body test"},
            "cwd": str(self.w.root),
        }
        with mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(self.w.root)}):
            return pre.validate(input_data)

    def test_story_rigor_none_exempts(self):
        """story unit + story.rigor=none → archive check exempt (not denied)."""
        self.w.write_settings({"retrospective": {"levels": {"story": {"rigor": "none"}}}})
        self._make_completed_unit("story-baz", top_fn="_story.md")
        result = self._validate_pr_create()
        # When exempt, Rule 11 deny does not fire (assuming other rules pass)
        decision = result.get("hookSpecificOutput", {}).get("permissionDecision")
        reason = result.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
        # exempt — the Rule 11 message must not be in reason
        self.assertNotIn("no-finish-without-archive", reason)

    def test_epic_rigor_template_blocks(self):
        """epic unit + epic.rigor=template (default) + archive absent → block (current behavior kept)."""
        # settings absent = default applied (epic=template+rt)
        self._make_completed_unit("epic-bar", top_fn="_epic.md")
        result = self._validate_pr_create()
        reason = result.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
        decision = result.get("hookSpecificOutput", {}).get("permissionDecision")
        self.assertEqual(decision, "deny")
        self.assertIn("no-finish-without-archive", reason)
        self.assertIn("epic-bar", reason)

    def test_initiative_rigor_none_settings_blocked_by_guard(self):
        """initiative unit + even with initiative.rigor=none pinned in settings, the reader guard → archive check blocks."""
        self.w.write_settings({"retrospective": {"levels": {"initiative": {"rigor": "none"}}}})
        self._make_completed_unit("initiative-foo", top_fn="_initiative.md")
        buf = io.StringIO()
        with redirect_stderr(buf):
            result = self._validate_pr_create()
        reason = result.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
        decision = result.get("hookSpecificOutput", {}).get("permissionDecision")
        # guard parity: initiative is not exempt → archive check applies → deny because absent
        self.assertEqual(decision, "deny")
        self.assertIn("no-finish-without-archive", reason)
        self.assertIn("initiative-foo", reason)
        # stderr warning is also emitted (reader guard)
        self.assertIn("WARNING", buf.getvalue())

    def test_mixed_only_blocking_in_deny_message(self):
        """mixed — epic.rigor=none exempt + story.rigor=template block → deny message shows only the blocked unit."""
        self.w.write_settings({"retrospective": {"levels": {
            "epic":  {"rigor": "none"},     # exempt
            "story": {"rigor": "template"}, # block (same as default)
        }}})
        self._make_completed_unit("epic-exempt", top_fn="_epic.md")
        self._make_completed_unit("story-block", top_fn="_story.md")
        result = self._validate_pr_create()
        reason = result.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
        decision = result.get("hookSpecificOutput", {}).get("permissionDecision")
        self.assertEqual(decision, "deny")
        # only the blocking one in the message — the exempt epic-exempt must not appear
        self.assertIn("story-block", reason)
        self.assertNotIn("epic-exempt", reason)


if __name__ == "__main__":
    unittest.main()
