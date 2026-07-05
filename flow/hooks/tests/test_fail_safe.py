"""A-001 fail-safe regression test — the hook does not silently pass (fail-open) on a validate() exception.

Target: hook_pre_tool_validate
- fail_safe_output(tool_name, exc): high-stakes (write/shell/patch) tools deny, others allow, warn on stderr.
- main(): even if validate() throws, it outputs a decision to stdout (blocks the fail-open where dying with no output → allow).

Run: cd flow/hooks && python3 -m unittest tests.test_fail_safe
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import hook_pre_tool_validate as pre  # noqa: E402


class TestFailSafeOutput(unittest.TestCase):
    """Per-tool conservative decision on exception."""

    def test_high_stakes_denied(self):
        exc = RuntimeError("boom")
        for tool in ["Bash", "run_in_terminal", "Write", "Edit", "MultiEdit",
                     "NotebookEdit", "create_file", "apply_patch"]:
            out = pre.fail_safe_output(tool, exc)
            self.assertEqual(
                out["hookSpecificOutput"]["permissionDecision"], "deny",
                f"{tool}: high-stakes tools must deny on exception",
            )

    def test_read_allowed(self):
        exc = RuntimeError("boom")
        for tool in ["Read", "Grep", "Glob", "TodoWrite", ""]:
            out = pre.fail_safe_output(tool, exc)
            self.assertEqual(
                out["hookSpecificOutput"]["permissionDecision"], "allow",
                f"{tool}: read-type tools allow on exception (prevents a hook bug from halting all work)",
            )

    def test_deny_reason_present(self):
        out = pre.fail_safe_output("Bash", RuntimeError("boom"))
        self.assertIn("permissionDecisionReason", out["hookSpecificOutput"])


class TestFailSafeMain(unittest.TestCase):
    """main() outputs a decision even on a validate() exception (blocks fail-open)."""

    def _run_main(self, tool_name):
        payload = json.dumps({"tool_name": tool_name, "tool_input": {}})
        # Isolate the audit side-write: main() appends .flow/.runtime/hook_audit.jsonl
        # under CLAUDE_PROJECT_DIR (cwd fallback) — without this, running the test from
        # the repo drops a stray .flow/ into the tests dir.
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": tmp}), \
             mock.patch.object(pre, "validate", side_effect=RuntimeError("boom")), \
             mock.patch.object(sys, "stdin", io.StringIO(payload)), \
             mock.patch.object(sys, "stdout", new_callable=io.StringIO) as out, \
             mock.patch.object(sys, "stderr", new_callable=io.StringIO):
            pre.main()
            return out.getvalue()

    def test_main_emits_decision_on_exception(self):
        out = self._run_main("Bash")
        self.assertTrue(out.strip(), "fail-open: on a validate exception, main outputs nothing to stdout → treated as allow")

    def test_main_denies_write_on_exception(self):
        dec = json.loads(self._run_main("Write"))["hookSpecificOutput"]["permissionDecision"]
        self.assertEqual(dec, "deny")

    def test_main_allows_read_on_exception(self):
        dec = json.loads(self._run_main("Read"))["hookSpecificOutput"]["permissionDecision"]
        self.assertEqual(dec, "allow")


if __name__ == "__main__":
    unittest.main()
