#!/usr/bin/env python3
"""TS-001 A-002 aggregation CLI tests (stdlib unittest, 0 dependencies).

Essence: not trimming but simple + writing. Count exactly what is in the log (0 embellishment).
- aggregate: group by unit_id → Counter of blocked rules / skills / retries / tools (pure function)
- load_entries: read jsonl + skip malformed
Run: cd flow/hooks && python3 -m unittest tests.test_audit_report
"""
from __future__ import annotations

import io
import os
import sys
import tempfile
import unittest
from unittest import mock

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import audit_report as ar  # noqa: E402


# post = "success" key (executed) / pre-block = "blocked_rule" key (blocked)
ENTRIES = [
    {"tool": "Bash", "success": True, "unit_id": "e/TS-001/A-001"},
    {"tool": "Read", "success": True, "unit_id": "e/TS-001/A-001"},
    {"tool": "Read", "success": False, "unit_id": "e/TS-001/A-001"},  # retry 1
    {"tool": "Skill", "success": True, "unit_id": "e/TS-001/A-001", "skill": "flow:flow"},
    {"tool": "Write", "decision": "deny", "blocked_rule": "no-node-without-purpose", "unit_id": "e/TS-001/A-001"},
    {"tool": "AskUserQuestion", "decision": "ask", "blocked_rule": "decision-criteria-first", "unit_id": "e/TS-001/A-001"},
    {"tool": "Bash", "success": True, "unit_id": "e/TS-002/A-001"},  # a different work item
    {"tool": "Edit", "success": True},  # no unit_id → unattributed
]


class TestAggregate(unittest.TestCase):
    def setUp(self):
        self.agg = ar.aggregate(ENTRIES)

    def test_groups_by_unit(self):
        self.assertIn("e/TS-001/A-001", self.agg)
        self.assertIn("e/TS-002/A-001", self.agg)
        self.assertIn("unattributed", self.agg)

    def test_tools_counted(self):
        u = self.agg["e/TS-001/A-001"]
        self.assertEqual(u["tools"]["Read"], 2)
        self.assertEqual(u["tools"]["Bash"], 1)

    def test_retries_counted(self):
        # one success=false
        self.assertEqual(self.agg["e/TS-001/A-001"]["retries"], 1)
        self.assertEqual(self.agg["e/TS-002/A-001"]["retries"], 0)

    def test_skills_counted(self):
        self.assertEqual(self.agg["e/TS-001/A-001"]["skills"]["flow:flow"], 1)

    def test_denied_rules_counted(self):
        # deny goes to denied_rules (H3 — separated from ask)
        self.assertEqual(
            self.agg["e/TS-001/A-001"]["denied_rules"]["no-node-without-purpose"], 1
        )

    def test_asked_rules_separated_from_denied(self):
        # the ask gate (decision-criteria-first) goes to asked_rules — not mixed into the deny count
        u = self.agg["e/TS-001/A-001"]
        self.assertEqual(u["asked_rules"]["decision-criteria-first"], 1)
        self.assertNotIn("decision-criteria-first", u["denied_rules"])

    def test_blocked_record_not_counted_as_tool(self):
        # a blocked (not executed) record does not enter tools/retries (no success key)
        self.assertNotIn("Write", self.agg["e/TS-001/A-001"]["tools"])

    def test_unattributed_bucket(self):
        self.assertEqual(self.agg["unattributed"]["tools"]["Edit"], 1)


class TestLoadEntries(unittest.TestCase):
    def test_skips_malformed_lines(self):
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "audit.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.write('{"tool": "Bash", "success": true}\n')
            f.write("not json at all\n")  # malformed → skip
            f.write('{"tool": "Read", "success": true}\n')
        entries = ar.load_entries(path)
        self.assertEqual(len(entries), 2)

    def test_missing_file_returns_empty(self):
        self.assertEqual(ar.load_entries("/no/such/file.jsonl"), [])


class TestFormat(unittest.TestCase):
    def test_format_includes_counts(self):
        out = ar.format_report(ar.aggregate(ENTRIES))
        self.assertIn("e/TS-001/A-001", out)
        self.assertIn("no-node-without-purpose", out)
        self.assertIn("flow:flow", out)


class TestRender(unittest.TestCase):
    """H1: a filter on a non-existent unit → a message distinct from 'zero activity' (blocks retrospective misreading)."""

    def setUp(self):
        self.agg = ar.aggregate(ENTRIES)

    def test_existing_unit_shows_counts(self):
        out = ar.render(self.agg, unit="e/TS-001/A-001")
        self.assertIn("no-node-without-purpose", out)

    def test_nonexistent_unit_distinct_message(self):
        out = ar.render(self.agg, unit="e/TS-999/typo")
        self.assertIn("no records for unit", out)
        self.assertNotEqual(out, "(no measurement data)")  # must differ from 'zero activity'

    def test_json_mode(self):
        import json as _json
        out = ar.render(self.agg, unit="e/TS-001/A-001", as_json=True)
        parsed = _json.loads(out)
        self.assertEqual(parsed["e/TS-001/A-001"]["denied_rules"]["no-node-without-purpose"], 1)


class TestCaptureAggregateContract(unittest.TestCase):
    """H2: regression guard for record-key parity between capture (build_entry/build_block_entry) and aggregation.
    post has only success, pre-block only blocked_rule — no crossover (a premise of the aggregation classification)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_post_record_has_no_blocked_rule(self):
        import post_tool_validate as post
        e = post.build_entry({"tool_name": "Bash", "tool_response": {}}, self.tmp)
        self.assertIn("success", e)
        self.assertNotIn("blocked_rule", e)

    def test_block_record_has_no_success(self):
        import hook_pre_tool_validate as pre
        out = {"hookSpecificOutput": {
            "permissionDecision": "deny",
            "permissionDecisionReason": "violation (no-node-without-purpose): x",
        }}
        b = pre.build_block_entry({"tool_name": "Write"}, out, self.tmp)
        self.assertIn("blocked_rule", b)
        self.assertNotIn("success", b)


class TestMarkdownAndPost(unittest.TestCase):
    """A-003: markdown for a PR comment + fail-open when publishing via gh."""

    def test_format_markdown_reuses_report(self):
        md = ar.format_markdown(ar.aggregate(ENTRIES))
        self.assertIn("flow", md)
        self.assertIn("no-node-without-purpose", md)  # includes format_report content
        self.assertIn("```", md)  # preserves layout as a code block

    def test_post_pr_comment_fail_open_when_gh_missing(self):
        import audit_report as a
        orig = a.subprocess.run
        a.subprocess.run = lambda *args, **kw: (_ for _ in ()).throw(FileNotFoundError("gh"))
        try:
            ok = a.post_pr_comment("123", "body")  # fails if the exception propagates
        finally:
            a.subprocess.run = orig
        self.assertFalse(ok, "False when gh is not installed (fail-open) — does not block the PR flow")

    def test_post_pr_comment_success(self):
        import audit_report as a
        calls = {}
        def fake_run(args, **kw):
            calls["args"] = args
            calls["input"] = kw.get("input")
            class R:  # noqa
                pass
            return R()
        orig = a.subprocess.run
        a.subprocess.run = fake_run
        try:
            ok = a.post_pr_comment("123", "BODYTEXT")
        finally:
            a.subprocess.run = orig
        self.assertTrue(ok)
        self.assertIn("gh", calls["args"][0])
        self.assertIn("123", calls["args"])
        self.assertEqual(calls["input"], "BODYTEXT")  # body passed via stdin


class TestPrFlagInterplay(unittest.TestCase):
    """--pr must honor --unit (posts the unit-filtered markdown) and reject --json
    (parser.error) instead of silently ignoring both."""

    def _run_main(self, argv):
        """Run main() with mocked argv/load_entries/post_pr_comment.

        Returns (exit_code, stdout, posted) — posted stays {} when nothing was posted.
        """
        posted: dict = {}

        def fake_post(pr, body):
            posted["pr"] = pr
            posted["body"] = body
            return True

        code = 0
        with mock.patch.object(ar, "load_entries", return_value=ENTRIES), \
             mock.patch.object(ar, "post_pr_comment", side_effect=fake_post), \
             mock.patch.object(sys, "argv", ["audit_report.py"] + argv), \
             mock.patch.object(sys, "stdout", new_callable=io.StringIO) as out, \
             mock.patch.object(sys, "stderr", new_callable=io.StringIO):
            try:
                ar.main()
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
        return code, out.getvalue(), posted

    def test_pr_alone_posts_full_report(self):
        # regression: --pr without --unit still posts every unit
        code, _, posted = self._run_main(["--pr", "7"])
        self.assertEqual(code, 0)
        self.assertEqual(posted["pr"], "7")
        self.assertIn("e/TS-001/A-001", posted["body"])
        self.assertIn("e/TS-002/A-001", posted["body"])

    def test_pr_with_unit_posts_filtered_markdown(self):
        code, _, posted = self._run_main(["--pr", "7", "--unit", "e/TS-001/A-001"])
        self.assertEqual(code, 0)
        self.assertEqual(posted["pr"], "7")
        self.assertIn("e/TS-001/A-001", posted["body"])
        self.assertNotIn("e/TS-002/A-001", posted["body"], "--unit filter must apply to the PR body")
        self.assertIn("```", posted["body"])  # markdown path reused (format_markdown)

    def test_pr_with_nonexistent_unit_refuses(self):
        # documented choice: refuse (exit 2, nothing posted) — a typo'd unit id must not
        # land as a junk PR comment; the distinct render() message tells the caller why.
        code, out, posted = self._run_main(["--pr", "7", "--unit", "e/TS-999/typo"])
        self.assertEqual(code, 2)
        self.assertEqual(posted, {}, "no comment may be posted for a unit with no records")
        self.assertIn("no records for unit", out)

    def test_pr_with_json_is_parser_error(self):
        code, _, posted = self._run_main(["--pr", "7", "--json"])
        self.assertEqual(code, 2)  # argparse parser.error exit code
        self.assertEqual(posted, {}, "no comment may be posted when flags are rejected")


class TestChecksAggregation(unittest.TestCase):
    """TS-003 A-003 — aggregation of quality-gate verifier results (check records)."""

    CHECK_ENTRIES = [
        {"check": "test", "passed": True, "returncode": 0, "unit_id": "e/TS-003/A-001"},
        {"check": "test", "passed": False, "returncode": 1, "unit_id": "e/TS-003/A-001"},
        {"check": "lint", "passed": True, "returncode": 0, "unit_id": "e/TS-003/A-001"},
        {"tool": "Bash", "success": True, "unit_id": "e/TS-003/A-001"},  # mixed in — no effect
    ]

    def test_checks_pass_fail_counted(self):
        agg = ar.aggregate(self.CHECK_ENTRIES)
        checks = agg["e/TS-003/A-001"]["checks"]
        self.assertEqual(checks["test"], {"pass": 1, "fail": 1})
        self.assertEqual(checks["lint"], {"pass": 1, "fail": 0})

    def test_checks_absent_failsafe(self):
        # existing logs with no check record → checks {} (0 regression)
        agg = ar.aggregate(ENTRIES)
        self.assertEqual(agg["e/TS-001/A-001"]["checks"], {})

    def test_checks_in_json_output(self):
        out = ar.render(ar.aggregate(self.CHECK_ENTRIES), as_json=True)
        import json as _j
        parsed = _j.loads(out)
        self.assertEqual(parsed["e/TS-003/A-001"]["checks"]["test"], {"pass": 1, "fail": 1})

    def test_checks_in_text_report(self):
        rep = ar.format_report(ar.aggregate(self.CHECK_ENTRIES))
        self.assertIn("verify(quality-gate)", rep)
        self.assertIn("test=1p/1f", rep)

    def test_check_record_not_counted_as_tool(self):
        # a check record does not enter tool aggregation (no success/blocked key)
        agg = ar.aggregate(self.CHECK_ENTRIES)
        self.assertEqual(agg["e/TS-003/A-001"]["tools"]["Bash"], 1)  # only 1 Bash


if __name__ == "__main__":
    unittest.main()
