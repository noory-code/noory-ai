"""Rule sync (plugin rules/ → .claude/rules/) drift detection, apply, and hook-notice regression (stdlib unittest, 0 deps).

Targets:
- _flow_state: strip/wrap, detect_rule_drift (propagated-copy model — always override, no conflict), apply_rule_upgrade, state IO, build_sync_state
- inject_flow_context.format_rule_drift / main (SessionStart notice, read-only, blast-radius)

Run: cd flow/hooks && python3 -m unittest tests.test_rule_drift
"""
from __future__ import annotations

import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import _flow_state as w  # noqa: E402


def _write(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


class TestMarker(unittest.TestCase):
    def test_roundtrip(self):
        body = "# Title\n\nbody line\n"
        self.assertEqual(w.strip_marker_prefix(w.wrap_with_marker(body)), body)

    def test_strip_no_blank_variant(self):
        # marker + immediate body (no blank line) variant: strip only the marker line
        self.assertEqual(w.strip_marker_prefix(w.MARKER_LINE + "\n# X\n"), "# X\n")

    def test_strip_non_marker_untouched(self):
        self.assertEqual(w.strip_marker_prefix("# no marker\n"), "# no marker\n")

    def test_marker_line_is_measured_value(self):
        # current ground-truth marker line (em-dash included) — changing it affects compat with existing installs
        self.assertTrue(w.MARKER_LINE.startswith(w.MARKER_PREFIX))
        self.assertIn("generated from flow plugin rules/", w.MARKER_LINE)


class TestDetect(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.plugin = os.path.join(self.tmp.name, "rules")
        self.project = os.path.join(self.tmp.name, ".claude", "rules")
        os.makedirs(self.plugin)
        os.makedirs(self.project)

    def tearDown(self):
        self.tmp.cleanup()

    def _detect(self, state=None):
        return w.detect_rule_drift(self.plugin, self.project, state)

    def test_in_sync(self):
        _write(os.path.join(self.plugin, "a.md"), "# A\n")
        _write(os.path.join(self.project, "a.md"), w.wrap_with_marker("# A\n"))
        d = self._detect()
        self.assertEqual(d["in_sync"], ["a.md"])
        self.assertEqual(d["stale"], [])

    def test_stateless_diff_is_stale(self):
        _write(os.path.join(self.plugin, "a.md"), "# NEW\n")
        _write(os.path.join(self.project, "a.md"), w.wrap_with_marker("# OLD\n"))
        self.assertEqual(self._detect(None)["stale"], ["a.md"])

    def test_upstream_stale_with_state(self):
        _write(os.path.join(self.plugin, "a.md"), "# NEW\n")
        _write(os.path.join(self.project, "a.md"), w.wrap_with_marker("# OLD\n"))
        state = {"rule_hashes": {"a.md": w._hash_body("# OLD\n")}, "synced_files": ["a.md"]}
        d = self._detect(state)
        self.assertEqual(d["stale"], ["a.md"])
        self.assertEqual(d["conflict"], [])

    def test_handedit_is_stale_not_conflict(self):
        # propagated rule hand-edited + canonical source changed → stale, not conflict (always override — generated artifact)
        _write(os.path.join(self.plugin, "a.md"), "# NEW\n")
        _write(os.path.join(self.project, "a.md"), w.wrap_with_marker("# HAND EDIT\n"))
        d = self._detect()
        self.assertEqual(d["stale"], ["a.md"])
        self.assertEqual(d["conflict"], [])

    def test_missing_new(self):
        _write(os.path.join(self.plugin, "a.md"), "# A\n")
        self.assertEqual(self._detect()["missing_new"], ["a.md"])

    def test_readme_excluded(self):
        _write(os.path.join(self.plugin, "README.md"), "# readme\n")
        _write(os.path.join(self.plugin, "a.md"), "# A\n")
        self.assertEqual(w.synced_rule_files(self.plugin), ["a.md"])
        self.assertNotIn("README.md", self._detect()["missing_new"])


class TestApply(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = self.tmp.name
        self.plugin = os.path.join(self.ws, "rules")
        self.project = os.path.join(self.ws, ".claude", "rules")
        os.makedirs(self.plugin)
        os.makedirs(self.project)
        self.patcher = mock.patch.object(w, "plugin_rules_dir", return_value=self.plugin)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.tmp.cleanup()

    def test_stale_applied_bytematch_and_backup(self):
        _write(os.path.join(self.plugin, "a.md"), "# NEW\n")
        _write(os.path.join(self.project, "a.md"), w.wrap_with_marker("# OLD\n"))
        res = w.apply_rule_upgrade(self.ws)
        self.assertIn("a.md", res["applied"])
        self.assertEqual(_read(os.path.join(self.project, "a.md")), w.wrap_with_marker("# NEW\n"))
        self.assertTrue(res["backups"])  # one backup copy
        d = w.detect_rule_drift(self.plugin, self.project, w.load_sync_state(self.ws))
        self.assertIn("a.md", d["in_sync"])  # in_sync after apply

    def test_handedit_overwritten_no_conflict(self):
        # a propagated rule is always overwritten by the canonical source even if hand-edited (no conflict/approval concept — generated artifact)
        _write(os.path.join(self.plugin, "a.md"), "# NEW\n")
        _write(os.path.join(self.project, "a.md"), w.wrap_with_marker("# HAND\n"))
        res = w.apply_rule_upgrade(self.ws)
        self.assertIn("a.md", res["applied"])
        self.assertEqual(_read(os.path.join(self.project, "a.md")), w.wrap_with_marker("# NEW\n"))

    def test_missing_new_auto_applied(self):
        # a new propagated rule (missing_new) is added automatically (no include needed — propagated rules auto-sync)
        _write(os.path.join(self.plugin, "a.md"), "# A\n")  # no copy = missing_new
        res = w.apply_rule_upgrade(self.ws)
        self.assertTrue(os.path.isfile(os.path.join(self.project, "a.md")))
        self.assertIn("a.md", res["applied"])


class TestStateIO(unittest.TestCase):
    def test_write_load_atomic_corrupt_absent(self):
        with tempfile.TemporaryDirectory() as d:
            st = {"applied_version": "1", "rule_hashes": {"a": "b"}, "synced_files": ["a"]}
            w.write_sync_state(d, st)
            self.assertEqual(w.load_sync_state(d), st)
            self.assertFalse(os.path.isfile(w.rules_sync_state_path(d) + ".tmp"))  # atomic
            _write(w.rules_sync_state_path(d), "{broken")
            self.assertIsNone(w.load_sync_state(d))  # corrupt → None
            os.remove(w.rules_sync_state_path(d))
            self.assertIsNone(w.load_sync_state(d))  # absent → None

    def test_build_skip_preserves_prev_s(self):
        with tempfile.TemporaryDirectory() as d:
            plugin = os.path.join(d, "rules")
            project = os.path.join(d, ".claude", "rules")
            os.makedirs(plugin)
            os.makedirs(project)
            _write(os.path.join(plugin, "a.md"), "# NEW\n")
            _write(os.path.join(project, "a.md"), w.wrap_with_marker("# HAND\n"))
            prev = {"rule_hashes": {"a.md": "OLD_S"}, "synced_files": ["a.md"]}
            st = w.build_sync_state(prev, plugin, project, "1", skip={"a.md"})
            self.assertEqual(st["rule_hashes"].get("a.md"), "OLD_S")  # previous S preserved
            self.assertNotIn("a.md", st["synced_files"])


class TestInjectHook(unittest.TestCase):
    """SessionStart two-axis notice (plugin stale first → rule drift). read-only, blast-radius."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = self.tmp.name
        self.plugin = os.path.join(self.ws, "rules")
        self.project = os.path.join(self.ws, ".claude", "rules")
        os.makedirs(self.plugin)
        os.makedirs(self.project)
        import inject_flow_context as inj
        self.inj = inj
        # pass format_rule_drift's isdir check + plugin detection default = up-to-date (individual tests override)
        self._patches = [
            mock.patch.object(inj, "plugin_rules_dir", return_value=self.plugin),
            mock.patch.object(inj, "project_rules_dir", return_value=self.project),
            mock.patch.object(inj, "detect_plugin_staleness",
                              return_value={"env": "cli", "installed": "1", "latest": "1", "stale": False}),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()
        self.tmp.cleanup()

    def _drift(self, **kw):
        base = {"stale": [], "missing_new": [], "orphan": [], "protected": [], "plugin_version": "1"}
        base.update(kw)
        return mock.patch.object(self.inj, "detect_rule_drift_all", return_value=base)

    def _stale_plugin(self):
        return mock.patch.object(
            self.inj, "detect_plugin_staleness",
            return_value={"env": "cli", "installed": "0.16.0", "latest": "0.17.0", "stale": True},
        )

    def test_rule_block_when_stale(self):
        with self._drift(stale=["a.md"]):
            block = self.inj.format_rule_drift(self.ws)
        self.assertIn("rule sync required", block)
        self.assertIn("a.md", block)

    def test_rule_block_orphan(self):
        with self._drift(orphan=["gone.md"]):
            block = self.inj.format_rule_drift(self.ws)
        self.assertIn("To delete", block)
        self.assertIn("gone.md", block)

    def test_rule_block_preflight_phrases(self):
        with self._drift(stale=["a.md"]):
            block = self.inj.format_rule_drift(self.ws)
        for phrase in ("before starting the user-requested work", "/flow-upgrade",
                       "do the work first", "later", "skip", "once per session"):
            self.assertIn(phrase, block)

    def test_silent_when_in_sync(self):
        with self._drift():  # all empty (silent even if only protected present)
            self.assertEqual(self.inj.format_rule_drift(self.ws), "")

    def test_fail_safe_when_project_rules_absent(self):
        with mock.patch.object(self.inj, "project_rules_dir",
                               return_value=os.path.join(self.ws, "nonexist")):
            self.assertEqual(self.inj.format_rule_drift(self.ws), "")  # isdir absent → silent

    def test_plugin_block_when_stale(self):
        with self._stale_plugin():
            block = self.inj.format_plugin_staleness()
        self.assertIn("Plugin upgrade required", block)
        self.assertIn("0.16.0", block)
        self.assertIn("claude plugin update", block)  # cli-environment means

    def test_main_plugin_priority_over_rule(self):
        # if the plugin is stale, the plugin notice takes priority and the rule block is omitted (rule sync after restart)
        with self._stale_plugin(), self._drift(stale=["a.md"]), \
             mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": self.ws}), \
             mock.patch.object(sys, "stdin", io.StringIO("{}")), \
             mock.patch.object(sys, "stdout", io.StringIO()) as out:
            self.inj.main()
        ctx = json.loads(out.getvalue())["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Plugin upgrade required", ctx)
        self.assertNotIn("rule sync required", ctx)

    def test_blast_radius_main_survives_failure(self):
        with mock.patch.object(self.inj, "detect_plugin_staleness", side_effect=RuntimeError("boom")), \
             mock.patch.object(self.inj, "format_rule_drift", side_effect=RuntimeError("boom2")), \
             mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": self.ws}), \
             mock.patch.object(sys, "stdin", io.StringIO("{}")), \
             mock.patch.object(sys, "stdout", io.StringIO()) as out:
            self.inj.main()
        parsed = json.loads(out.getvalue())  # valid JSON
        self.assertEqual(parsed["hookSpecificOutput"]["hookEventName"], "SessionStart")
        ctx = parsed["hookSpecificOutput"]["additionalContext"]
        self.assertNotIn("upgrade required", ctx)
        self.assertIn("Flow state", ctx)  # flow-state injection is retained


class TestRuleDetailsSync(unittest.TestCase):
    """rule-details domain integrated sync (detect_rule_drift_all / apply routing / same-name non-collision)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = self.tmp.name
        self.plugin_rules = os.path.join(self.ws, "rules")
        self.plugin_details = os.path.join(self.ws, "rule-details")
        self.proj_rules = os.path.join(self.ws, ".claude", "rules")
        self.proj_details = os.path.join(self.ws, ".claude", "rule-details")
        for d in (self.plugin_rules, self.plugin_details, self.proj_rules, self.proj_details):
            os.makedirs(d)
        self.p1 = mock.patch.object(w, "plugin_rules_dir", return_value=self.plugin_rules)
        self.p2 = mock.patch.object(w, "plugin_rule_details_dir", return_value=self.plugin_details)
        self.p1.start()
        self.p2.start()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()
        self.tmp.cleanup()

    def test_detail_missing_new_prefixed(self):
        _write(os.path.join(self.plugin_details, "x.md"), "# X detail\n")
        d = w.detect_rule_drift_all(self.ws, None)
        self.assertIn("rule-details/x.md", d["missing_new"])
        self.assertNotIn("x.md", d["missing_new"])  # only with prefix

    def test_same_name_no_collision_across_domains(self):
        # flow-rules.md exists in both rules/ and rule-details/ — tracked separately without collision
        _write(os.path.join(self.plugin_rules, "flow-rules.md"), "# core\n")
        _write(os.path.join(self.proj_rules, "flow-rules.md"), w.wrap_with_marker("# core\n"))
        _write(os.path.join(self.plugin_details, "flow-rules.md"), "# detail\n")
        _write(os.path.join(self.proj_details, "flow-rules.md"), w.wrap_with_marker("# detail\n"))
        d = w.detect_rule_drift_all(self.ws, None)
        self.assertIn("flow-rules.md", d["in_sync"])
        self.assertIn("rule-details/flow-rules.md", d["in_sync"])

    def test_apply_routes_detail_to_details_dir(self):
        _write(os.path.join(self.plugin_details, "x.md"), "# X detail\n")
        res = w.apply_rule_upgrade(self.ws)
        self.assertIn("rule-details/x.md", res["applied"])
        # written to rule-details/, not rules/
        self.assertTrue(os.path.isfile(os.path.join(self.proj_details, "x.md")))
        self.assertFalse(os.path.isfile(os.path.join(self.proj_rules, "x.md")))
        self.assertEqual(
            _read(os.path.join(self.proj_details, "x.md")), w.wrap_with_marker("# X detail\n")
        )

    def test_detail_missing_dir_created_on_apply(self):
        shutil.rmtree(self.proj_details)  # .claude/rule-details absent on first sync
        _write(os.path.join(self.plugin_details, "x.md"), "# X\n")
        res = w.apply_rule_upgrade(self.ws)
        self.assertIn("rule-details/x.md", res["applied"])
        self.assertTrue(os.path.isfile(os.path.join(self.proj_details, "x.md")))

    def test_state_records_detail_hashes(self):
        _write(os.path.join(self.plugin_details, "x.md"), "# X\n")
        w.apply_rule_upgrade(self.ws)
        state = w.load_sync_state(self.ws)
        self.assertIn("rule_details_hashes", state)
        self.assertIn("x.md", state["rule_details_hashes"])  # bare name inside the domain
        self.assertIn("x.md", state["synced_detail_files"])

    def test_detail_stale_applied(self):
        _write(os.path.join(self.plugin_details, "x.md"), "# NEW\n")
        _write(os.path.join(self.proj_details, "x.md"), w.wrap_with_marker("# OLD\n"))
        res = w.apply_rule_upgrade(self.ws)  # stale is always applied (no approval needed)
        self.assertIn("rule-details/x.md", res["applied"])
        self.assertEqual(
            _read(os.path.join(self.proj_details, "x.md")), w.wrap_with_marker("# NEW\n")
        )

    def test_rules_only_state_backward_compat(self):
        # even with rule-details empty, rules sync works as before (regression)
        _write(os.path.join(self.plugin_rules, "a.md"), "# A\n")
        res = w.apply_rule_upgrade(self.ws)
        self.assertIn("a.md", res["applied"])
        self.assertTrue(os.path.isfile(os.path.join(self.proj_rules, "a.md")))

    def test_same_name_backup_no_collision(self):
        # H-2: same-name rules/wf.md and rule-details/wf.md don't overwrite each other when backed up in the same apply.
        # both stale (existing copy != canonical source) → backup triggered.
        _write(os.path.join(self.plugin_rules, "wf.md"), "# CORE NEW\n")
        _write(os.path.join(self.proj_rules, "wf.md"), w.wrap_with_marker("# CORE OLD\n"))
        _write(os.path.join(self.plugin_details, "wf.md"), "# DETAIL NEW\n")
        _write(os.path.join(self.proj_details, "wf.md"), w.wrap_with_marker("# DETAIL OLD\n"))
        w.apply_rule_upgrade(self.ws)
        bdir = os.path.join(w.runtime_dir(self.ws), "rules-backup")
        core_bak = os.path.join(bdir, "rules", "wf.md.bak")
        detail_bak = os.path.join(bdir, "rule-details", "wf.md.bak")
        self.assertTrue(os.path.isfile(core_bak), "rules backup exists")
        self.assertTrue(os.path.isfile(detail_bak), "rule-details backup exists (no collision)")
        # each backup preserves its own domain's old content (no mutual overwrite)
        self.assertIn("CORE OLD", _read(core_bak))
        self.assertIn("DETAIL OLD", _read(detail_bak))


if __name__ == "__main__":
    unittest.main()
