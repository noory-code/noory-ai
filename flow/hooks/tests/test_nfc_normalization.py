#!/usr/bin/env python3
"""Hangul NFC/NFD normalization regression test (stdlib unittest, 0 dependencies).

Gates with embedded Hangul literals (no-node-without-purpose etc.) and status parsers (STATUS_RE/
PURPOSE_RE) have NFC (composed) source, so they only match NFC content. If the content is NFD (decomposed)
(macOS APFS/HFS+ filename normalization, some editors, model emission, drift-sync Windows↔macOS
round-trip), the same Hangul has different code points and fails to match → false-deny + silent status misjudgment.
This regression-guards that normalizing the haystack to NFC (`nfc()`) right before matching blocks that.

Run: cd flow/hooks && python3 -m unittest tests.test_nfc_normalization
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unicodedata
import unittest

# Add the hooks directory to the import path (parent of tests/)
HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import _flow_state as ws  # noqa: E402
import hook_pre_tool_validate as pre  # noqa: E402


def nfd(s: str) -> str:
    """Make the test input decomposed (NFD) — reproduces real macOS/round-trip content."""
    return unicodedata.normalize("NFD", s)


CWD = "/ws"  # no disk — Rule 9 checks content only (no file I/O)


def _decide(tool_name: str, rel_path: str, content=None, **extra) -> str:
    ti = {"file_path": CWD + rel_path}
    if content is not None:
        ti["content"] = content
    ti.update(extra)
    out = pre.validate({"tool_name": tool_name, "tool_input": ti, "cwd": CWD})
    return out["hookSpecificOutput"]["permissionDecision"]


class TestNfcHelper(unittest.TestCase):
    def test_nfc_idempotent_and_unifies(self):
        s = "**Ultimate purpose**"
        # NFD input is also unified to NFC
        self.assertEqual(ws.nfc(nfd(s)), unicodedata.normalize("NFC", s))
        # idempotent — no effect on NFC input
        self.assertEqual(ws.nfc(ws.nfc(s)), ws.nfc(s))


class TestNfcStateParsing(unittest.TestCase):
    """_flow_state's status/purpose parsers parse NFD content correctly too."""

    def test_self_status_parses_nfd_status_label(self):
        # Even if '**Status**' is NFD, the status must parse (otherwise the completed/in-progress verdict is misjudged).
        content = nfd("# Epic\n**Status**: ✅\n")
        self.assertEqual(ws.self_status(content), "✅")
        self.assertTrue(ws.is_completed(content))

    def test_self_status_none_when_absent(self):
        # Normalization must not break the conservative 'no status → None' verdict.
        self.assertIsNone(ws.self_status(nfd("# Epic\n## Goal\n")))

    def test_extract_purpose_from_nfd(self):
        content = nfd("# Epic\n**Ultimate purpose**: Keep the broadcast uninterrupted\n")
        self.assertEqual(
            ws.extract_purpose(content),
            unicodedata.normalize("NFC", "Keep the broadcast uninterrupted"),
        )


class TestNfcNodeGate(unittest.TestCase):
    """no-node-without-purpose (Rule 9) passes an NFD purpose too — false-deny regression guard."""

    # validate() uses resolve_workspace_root (CLAUDE_PROJECT_DIR takes priority), so isolate it.
    def setUp(self):
        self._saved = os.environ.pop("CLAUDE_PROJECT_DIR", None)

    def tearDown(self):
        if self._saved is not None:
            os.environ["CLAUDE_PROJECT_DIR"] = self._saved

    def test_story_nfd_purpose_allow(self):
        content = nfd("# Story\n**Ultimate purpose**: restate the parent purpose")
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/US-001/_story.md", content),
            "allow",
        )

    def test_action_nfd_purpose_allow(self):
        # A-NNN.md must pass both Rule 9 (purpose) and Rule 12 (depends_on) to allow.
        content = nfd("**Ultimate purpose**: purpose\n**depends_on**: []\n**Action**: A-001")
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/US-001/A-001.md", content),
            "allow",
        )

    def test_nfd_missing_purpose_still_deny(self):
        # Normalization must not weaken a proper deny (purpose truly missing → keep deny).
        self.assertEqual(
            _decide("Write", "/.flow/workspace/epic-x/US-001/_story.md", nfd("# Story\n## Goal")),
            "deny",
        )


class TestNfcFileReadPaths(unittest.TestCase):
    """Verify the file-read normalization path with a **real NFD disk file** (not an in-memory simulation).

    An OS-independent proxy for the situation where NFD content authored on macOS is on disk —
    it exercises the `nfc(f.read())` path of check_retro_not_empty(:512) / check_review_eval_recorded(:572)
    through real file I/O. Without the fix, the 'block' cases fall through to status-not-parsed→skip→pass
    (a silent bug), so this becomes a regression guard that distinguishes fixed from unfixed.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._saved = os.environ.get("CLAUDE_PROJECT_DIR")
        os.environ["CLAUDE_PROJECT_DIR"] = self.tmp

    def tearDown(self):
        if self._saved is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = self._saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_nfd(self, rel_parts, text):
        path = os.path.join(self.tmp, *rel_parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(unicodedata.normalize("NFD", text))  # write NFD bytes to disk

    def test_retro_gate_blocks_nfd_status_empty_retro(self):
        # 🔄 Action (NFD status) + empty retro → block (False). Without the fix, status-not-parsed→skip→True (pass).
        self._write_nfd(
            (".flow", "workspace", "epic-x", "US-001", "A-001.md"),
            "# A-001\n**Status**: 🔄\n\n## Retrospective\n",
        )
        self.assertFalse(pre.check_retro_not_empty(self.tmp))

    def test_retro_gate_passes_nfd_status_valid_retro(self):
        # 🔄 Action (NFD) + sufficient NFD retro body → pass (True).
        self._write_nfd(
            (".flow", "workspace", "epic-x", "US-001", "A-001.md"),
            "# A-001\n**Status**: 🔄\n\n## Retrospective\nA record sentence, long enough, of what this change confirmed and what to watch for more carefully next time.\n",
        )
        self.assertTrue(pre.check_retro_not_empty(self.tmp))

    def test_review_gate_blocks_nfd_missing_review(self):
        # 🔄 Story + all Actions ✅ (NFD) but no review marker → block (False).
        self._write_nfd(
            (".flow", "workspace", "epic-x", "US-001", "_story.md"),
            "# Story\n**Status**: 🔄\n",
        )
        self._write_nfd(
            (".flow", "workspace", "epic-x", "US-001", "A-001.md"),
            "# A-001\n**Status**: ✅\n",
        )
        self.assertFalse(pre.check_review_eval_recorded(self.tmp))

    def test_review_gate_passes_nfd_valid_review(self):
        # 🔄 Story (NFD) + all Actions ✅ + sufficient NFD review body → pass (True).
        self._write_nfd(
            (".flow", "workspace", "epic-x", "US-001", "_story.md"),
            "# Story\n**Status**: 🔄\n\n## Review\nA record sentence that reviews and evaluates the deliverable at sufficient length, really long enough.\n",
        )
        self._write_nfd(
            (".flow", "workspace", "epic-x", "US-001", "A-001.md"),
            "# A-001\n**Status**: ✅\n",
        )
        self.assertTrue(pre.check_review_eval_recorded(self.tmp))


if __name__ == "__main__":
    unittest.main()
