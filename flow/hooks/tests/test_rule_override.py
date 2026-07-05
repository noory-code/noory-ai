"""Rule sync — propagated-rule model regression (stdlib unittest).

Propagated rules (copies of the flow canonical source) = generated artifacts: unconditional override + `.gitignore` registration + orphan deletion.
Consumer's own rules (outside `.gitignore`) = preserved (untouched). No conflict concept (a hand-edited propagated rule is still overwritten).

Target: _flow_state.{gitignored_rule_files, register_rule_override, unregister_rule_override,
       detect_rule_drift_all, apply_rule_upgrade}
Run: cd flow/hooks && python3 -m unittest tests.test_rule_override
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from unittest import mock

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import _flow_state as w  # noqa: E402


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


class TestGitignoredRuleFiles(unittest.TestCase):
    """.gitignore per-file parsing (recognize propagated-rule marking — the function behavior is model-independent)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = self.tmp.name
        self.gi = os.path.join(self.ws, ".gitignore")

    def tearDown(self):
        self.tmp.cleanup()

    def _write_gi(self, content):
        with open(self.gi, "w", encoding="utf-8") as f:
            f.write(content)

    def test_empty_when_no_gitignore(self):
        self.assertEqual(w.gitignored_rule_files(self.ws), {"rules": set(), "details": set()})

    def test_detects_file_level_rule(self):
        self._write_gi(".claude/rules/foo.md\n")
        self.assertEqual(w.gitignored_rule_files(self.ws), {"rules": {"foo.md"}, "details": set()})

    def test_detects_file_level_detail(self):
        self._write_gi(".claude/rule-details/bar.md\n")
        self.assertEqual(w.gitignored_rule_files(self.ws), {"rules": set(), "details": {"bar.md"}})

    def test_folder_pattern_NOT_treated_as_mark(self):
        """A whole-folder pattern is not recognized as propagated-rule marking (protect the user's own rules — the core requirement)."""
        self._write_gi(".claude/rules/\n.claude/rule-details/\n.flow/workspace/\n")
        self.assertEqual(w.gitignored_rule_files(self.ws), {"rules": set(), "details": set()})

    def test_ignores_unrelated_and_comments(self):
        self._write_gi("# comment\n.env\nnode_modules/\n.claude/rules/keep.md\n")
        self.assertEqual(w.gitignored_rule_files(self.ws), {"rules": {"keep.md"}, "details": set()})


class TestRegisterUnregister(unittest.TestCase):
    """Register/unregister propagated rules in .gitignore (register / unregister)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = self.tmp.name
        self.gi = os.path.join(self.ws, ".gitignore")

    def tearDown(self):
        self.tmp.cleanup()

    def test_register_appends_file_path_not_folder(self):
        self.assertTrue(w.register_rule_override(self.ws, "foo.md"))
        body = _read(self.gi)
        self.assertIn(".claude/rules/foo.md", body)
        self.assertNotIn(".claude/rules/\n", body)  # not the whole folder

    def test_register_idempotent(self):
        self.assertTrue(w.register_rule_override(self.ws, "foo.md"))
        self.assertFalse(w.register_rule_override(self.ws, "foo.md"))
        self.assertEqual(_read(self.gi).count(".claude/rules/foo.md"), 1)

    def test_unregister_removes_line(self):
        w.register_rule_override(self.ws, "foo.md")
        self.assertTrue(w.unregister_rule_override(self.ws, "foo.md"))
        self.assertNotIn(".claude/rules/foo.md", _read(self.gi))

    def test_unregister_idempotent_when_absent(self):
        self.assertFalse(w.unregister_rule_override(self.ws, "nope.md"))

    def test_roundtrip(self):
        w.register_rule_override(self.ws, "foo.md")
        w.register_rule_override(self.ws, "bar.md", is_detail=True)
        self.assertEqual(w.gitignored_rule_files(self.ws), {"rules": {"foo.md"}, "details": {"bar.md"}})
        w.unregister_rule_override(self.ws, "foo.md")
        self.assertEqual(w.gitignored_rule_files(self.ws), {"rules": set(), "details": {"bar.md"}})

    def test_marker_comment_matches_behavior(self):
        """The .gitignore marker comment must describe reality: these lines mark
        *propagated* artifacts that apply force-overwrites/removes — not consumer
        overrides excluded from sync (the old, opposite wording)."""
        w.register_rule_override(self.ws, "foo.md")
        body = _read(self.gi)
        self.assertIn(w._OVERRIDE_MARKER, body)
        self.assertIn("propagated", w._OVERRIDE_MARKER)
        self.assertNotIn("excluded from flow-upgrade sync", w._OVERRIDE_MARKER,
                         "marker must not claim these files are excluded from sync")

    def test_legacy_marker_recognized_no_second_marker(self):
        """Backward compat: a consumer .gitignore written before the reword contains the
        OLD marker line — registering a new rule must not append a second marker."""
        legacy = "# Consumer override rules (excluded from flow-upgrade sync — per file)"
        self.assertEqual(w._OVERRIDE_MARKER_LEGACY, legacy)  # recognition pin
        _write(self.gi, f"{legacy}\n.claude/rules/old.md\n")
        self.assertTrue(w.register_rule_override(self.ws, "foo.md"))
        body = _read(self.gi)
        self.assertIn(".claude/rules/foo.md", body)
        self.assertEqual(body.count(legacy), 1)
        self.assertNotIn(w._OVERRIDE_MARKER, body,
                         "new marker must not be appended when the legacy marker is present")

    def test_new_marker_written_once(self):
        w.register_rule_override(self.ws, "foo.md")
        w.register_rule_override(self.ws, "bar.md")
        self.assertEqual(_read(self.gi).count(w._OVERRIDE_MARKER), 1)


class _SyncEnv(unittest.TestCase):
    """Common setup mocking the canonical (plugin) / copy (project) directories."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = self.tmp.name
        self.p_rules = os.path.join(self.ws, "p_rules")
        self.p_details = os.path.join(self.ws, "p_details")
        self.c_rules = os.path.join(self.ws, ".claude", "rules")
        self.c_details = os.path.join(self.ws, ".claude", "rule-details")
        for d in (self.p_rules, self.p_details, self.c_rules, self.c_details):
            os.makedirs(d)
        self._patches = [
            mock.patch.object(w, "plugin_rules_dir", return_value=self.p_rules),
            mock.patch.object(w, "plugin_rule_details_dir", return_value=self.p_details),
            mock.patch.object(w, "project_rules_dir", return_value=self.c_rules),
            mock.patch.object(w, "project_rule_details_dir", return_value=self.c_details),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()
        self.tmp.cleanup()


class TestDetectAllPropagationModel(_SyncEnv):
    """detect_rule_drift_all — propagated-rule model (override / orphan / preserve own / conflict removed)."""

    def test_stale_override_regardless_of_gitignore(self):
        # Propagated-rule canonical changed → stale (regardless of gitignore registration — a sync target, not skipped)
        _write(os.path.join(self.p_rules, "a.md"), "# A v2\n")
        _write(os.path.join(self.c_rules, "a.md"), "# A old\n")
        w.register_rule_override(self.ws, "a.md")  # not skipped even if registered
        d = w.detect_rule_drift_all(self.ws)
        self.assertIn("a.md", d["stale"])
        self.assertEqual(d["conflict"], [])  # conflict concept removed

    def test_handedit_still_stale_no_conflict(self):
        # Copy hand-edited + canonical changed → stale, not conflict (overwritten unconditionally)
        _write(os.path.join(self.p_rules, "a.md"), "# A v2\n")
        _write(os.path.join(self.c_rules, "a.md"), "# A hand-edited\n")
        d = w.detect_rule_drift_all(self.ws)
        self.assertIn("a.md", d["stale"])
        self.assertEqual(d["conflict"], [])

    def test_orphan_when_gitignored_and_absent_in_plugin(self):
        # Absent in canonical + registered in gitignore = orphan (propagated, then deleted from canonical)
        _write(os.path.join(self.c_rules, "gone.md"), "# gone\n")
        w.register_rule_override(self.ws, "gone.md")
        d = w.detect_rule_drift_all(self.ws)
        self.assertIn("gone.md", d["orphan"])
        self.assertNotIn("gone.md", d["protected"])

    def test_protected_when_not_gitignored(self):
        # Absent in canonical + outside gitignore = own rule (protected, preserved)
        _write(os.path.join(self.c_rules, "mine.md"), "# my own rule\n")
        d = w.detect_rule_drift_all(self.ws)
        self.assertIn("mine.md", d["protected"])
        self.assertNotIn("mine.md", d["orphan"])

    def test_missing_new_propagated(self):
        # Present in canonical + absent in copy = missing_new (new propagated rule)
        _write(os.path.join(self.p_rules, "new.md"), "# new\n")
        d = w.detect_rule_drift_all(self.ws)
        self.assertIn("new.md", d["missing_new"])

    def test_detail_orphan_prefixed(self):
        _write(os.path.join(self.c_details, "d.md"), "# d\n")
        w.register_rule_override(self.ws, "d.md", is_detail=True)
        d = w.detect_rule_drift_all(self.ws)
        self.assertIn(w.DETAIL_PREFIX + "d.md", d["orphan"])


class TestApplyPropagation(_SyncEnv):
    """apply_rule_upgrade — auto-sync propagated rules + orphan deletion + gitignore registration."""

    def test_apply_overrides_and_registers(self):
        _write(os.path.join(self.p_rules, "a.md"), "# A v2\n")
        _write(os.path.join(self.c_rules, "a.md"), "# A old\n")
        res = w.apply_rule_upgrade(self.ws)
        self.assertIn("# A v2", _read(os.path.join(self.c_rules, "a.md")))  # override
        self.assertIn("a.md", res["applied"])
        self.assertIn("a.md", w.gitignored_rule_files(self.ws)["rules"])  # register the generated artifact

    def test_apply_deletes_orphan_keeps_protected(self):
        _write(os.path.join(self.c_rules, "gone.md"), "# gone\n")
        w.register_rule_override(self.ws, "gone.md")               # propagation marking → orphan
        _write(os.path.join(self.c_rules, "mine.md"), "# mine\n")  # own rule (outside gitignore)
        res = w.apply_rule_upgrade(self.ws)
        self.assertFalse(os.path.isfile(os.path.join(self.c_rules, "gone.md")))  # orphan deleted
        self.assertTrue(os.path.isfile(os.path.join(self.c_rules, "mine.md")))   # own rule preserved
        self.assertIn("gone.md", res["deleted"])
        self.assertIn("mine.md", res["protected"])
        self.assertNotIn("gone.md", w.gitignored_rule_files(self.ws)["rules"])  # line removed

    def test_apply_adds_missing_new(self):
        _write(os.path.join(self.p_rules, "new.md"), "# new rule\n")
        res = w.apply_rule_upgrade(self.ws)
        self.assertTrue(os.path.isfile(os.path.join(self.c_rules, "new.md")))
        self.assertIn("new.md", res["applied"])

    def test_apply_registers_in_sync_for_migration(self):
        # Migration: even in_sync (unchanged) propagated rules are registered in .gitignore (tracked→ignored transition). The file is unchanged.
        _write(os.path.join(self.p_rules, "a.md"), "# A\n")
        _write(os.path.join(self.c_rules, "a.md"), w.wrap_with_marker("# A\n"))  # in_sync
        w.apply_rule_upgrade(self.ws)
        self.assertIn("a.md", w.gitignored_rule_files(self.ws)["rules"])  # registered
        self.assertEqual(_read(os.path.join(self.c_rules, "a.md")), w.wrap_with_marker("# A\n"))


if __name__ == "__main__":
    unittest.main()
