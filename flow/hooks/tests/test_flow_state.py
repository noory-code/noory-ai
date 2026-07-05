#!/usr/bin/env python3
"""Reproduction + regression test for the completion-judgment defect (stdlib unittest, zero dependencies).

Defect: completion judgment used ``"**Status**: ✅" in content`` (a *whole-document*
substring), so it was polluted by a child Step/Story's ``**Status**: ✅`` marker and
misjudged an *in-progress* epic/initiative as complete. The correct judgment must look
only at the document's *own* status (the header-area ``**Status**:`` field).

Core of the reproduction fixture:
  _epic.md header ``**Status**: 🔄`` (the epic itself = in progress)
        +  Step ``**Status**: ✅`` (a child Story = complete)
  → current code: ✅ substring present → misjudged complete
  → fixed code: header self-status (🔄) → correctly recognized as active

Run: ``cd flow/hooks && python3 -m unittest tests.test_flow_state``
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

# add the hooks directory to the import path (tests/'s parent)
HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import _flow_state as ws  # noqa: E402
import hook_pre_tool_validate as pre  # noqa: E402


def _write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# in-progress epic: header 🔄 (the epic itself) + Step ✅ (child Story complete — pollution source)
EPIC_INPROGRESS = """# Epic: Test in progress

**Status**: 🔄
**Branch**: `epic/test`

## Step 2: US-001-foo
**Status**: ✅
**Title**: First completed Story

## Step 3: US-002-bar
**Status**: ⬜
**Title**: Remaining Story
"""

# completed epic: header ✅
EPIC_COMPLETED = """# Epic: Test complete

**Status**: ✅
**Branch**: `epic/test`

## Step 2: US-001-foo
**Status**: ✅
"""

STORY_INPROGRESS = """# Story: Foo

**Story**: US-001-foo
**Status**: 🔄

## Acceptance Criteria
| AC-1 | ... | ✅ pass | A-001 |
"""

INITIATIVE_INPROGRESS = """# Initiative: Test

**Status**: 🔄

## Progress
- Epic 1: ✅ complete
"""


class TestEpicCompletionMarker(unittest.TestCase):
    """epic-level completion judgment must not be polluted by a child Step's ✅."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ws_root = self.tmp
        self.epic_dir = os.path.join(self.tmp, ".flow", "workspace", "epic-test")

    def _make_inprogress(self):
        _write(os.path.join(self.epic_dir, "_epic.md"), EPIC_INPROGRESS)
        _write(
            os.path.join(self.epic_dir, "US-001-foo", "_story.md"),
            STORY_INPROGRESS,
        )

    def _make_completed(self):
        _write(os.path.join(self.epic_dir, "_epic.md"), EPIC_COMPLETED)

    # AC-1: an in-progress epic must be recognized as active (fails before the fix = Red)
    def test_has_active_epic_inprogress_is_true(self):
        self._make_inprogress()
        self.assertTrue(
            pre.has_active_epic(self.ws_root),
            "an in-progress epic (header 🔄 + Step ✅) must be recognized as active",
        )

    def test_parse_epic_inprogress_not_none(self):
        self._make_inprogress()
        result = ws.parse_epic(self.epic_dir, "epic-test")
        self.assertIsNotNone(
            result, "for an in-progress epic, parse_epic must not be None"
        )

    def test_find_active_epics_includes_inprogress(self):
        self._make_inprogress()
        names = [e["name"] for e in ws.find_active_epics(self.ws_root)]
        self.assertIn("epic-test", names)

    # AC-2: a completed epic must still be excluded (regression — completion judgment preserved)
    def test_has_active_epic_completed_is_false(self):
        self._make_completed()
        self.assertFalse(
            pre.has_active_epic(self.ws_root),
            "a completed epic (header ✅) must not be active",
        )

    def test_parse_epic_completed_is_none(self):
        self._make_completed()
        self.assertIsNone(ws.parse_epic(self.epic_dir, "epic-test"))


class TestTechnicalStoryScan(unittest.TestCase):
    """A-005: parse_epic must also scan TS- (Technical Story).

    Defect: line 150 ``startswith("US-")`` misses TS- Stories → context injection and
    summarize_inprogress cannot see TS Story status. Both US-/TS- must be scanned.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.epic_dir = os.path.join(self.tmp, ".flow", "workspace", "epic-t")

    def _make_ts_inprogress(self):
        _write(os.path.join(self.epic_dir, "_epic.md"), EPIC_INPROGRESS)
        _write(os.path.join(self.epic_dir, "TS-001-m", "_story.md"), STORY_INPROGRESS)
        _write(
            os.path.join(self.epic_dir, "TS-001-m", "A-002.md"),
            "# Action: A\n\n**Action**: A-002\n**Status**: 🔄\n",
        )

    # before Red: parse_epic misses TS- Stories → stories empty (fail)
    def test_parse_epic_includes_ts_story(self):
        self._make_ts_inprogress()
        result = ws.parse_epic(self.epic_dir, "epic-t")
        self.assertIsNotNone(result)
        names = [s["name"] for s in result["stories"]]
        self.assertIn("TS-001-m", names, "parse_epic must include TS- Stories")

    # summarize_inprogress must report a TS- Story's 🔄 Action
    def test_summarize_reports_ts_inprogress_action(self):
        self._make_ts_inprogress()
        summary = ws.summarize_inprogress(self.tmp)
        self.assertIn("TS-001-m", summary)
        self.assertIn("A-002", summary)

    # US- regression — preserves existing behavior
    def test_us_story_still_scanned(self):
        _write(os.path.join(self.epic_dir, "_epic.md"), EPIC_INPROGRESS)
        _write(os.path.join(self.epic_dir, "US-001-f", "_story.md"), STORY_INPROGRESS)
        result = ws.parse_epic(self.epic_dir, "epic-t")
        names = [s["name"] for s in result["stories"]]
        self.assertIn("US-001-f", names)


class TestInitiativeCompletionMarker(unittest.TestCase):
    """initiative-level follows the same pattern — must not be polluted by a child epic's ✅."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.init_dir = os.path.join(
            self.tmp, ".flow", "workspace", "initiative-test"
        )

    def test_inprogress_initiative_is_active(self):
        # header 🔄 + "Epic 1: ✅ complete" in the Progress section (pollution source)
        _write(os.path.join(self.init_dir, "_initiative.md"), INITIATIVE_INPROGRESS)
        inits = ws.find_active_initiatives(self.tmp)
        names = [i["name"] for i in inits]
        self.assertIn(
            "initiative-test", names,
            "an in-progress initiative (header 🔄 + a child Epic ✅ mention) must be recognized as active",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
