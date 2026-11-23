"""Session start states the inline-interpreter rule before a command meets the gate."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path


STAGE_ROOT = Path(__file__).resolve().parents[2]
HOOK_ROOT = STAGE_ROOT / "hooks"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))

import stage_context  # noqa: E402
import stage_shell  # noqa: E402


V4_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "v4" / "project-stage"


class InlineInterpreterRuleContextTest(unittest.TestCase):
    def rule_line(self, context: str) -> str:
        """The single context line that states the rule; fails when it is absent or repeated."""
        lines = [line for line in context.splitlines() if "inline interpreter code" in line]
        self.assertEqual(len(lines), 1, context)
        return lines[0]

    def test_current_topology_states_the_rule_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(V4_TEMPLATE_ROOT, root / ".stage")

            context = stage_context.session_context(root)

        # The milestone table exists only on the current topology branch.
        self.assertIn("### Active milestones (decision-derived)", context)
        self.rule_line(context)

    def test_legacy_topology_states_the_same_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            current_root = Path(tmp) / "current"
            shutil.copytree(V4_TEMPLATE_ROOT, current_root / ".stage")
            legacy_root = Path(tmp) / "legacy"
            (legacy_root / ".stage").mkdir(parents=True)

            current = stage_context.session_context(current_root)
            legacy = stage_context.session_context(legacy_root)

        self.assertNotIn("### Active milestones (decision-derived)", legacy)
        self.assertEqual(self.rule_line(legacy), self.rule_line(current))

    def test_rule_names_what_is_refused_and_what_to_use_instead(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(V4_TEMPLATE_ROOT, root / ".stage")

            line = self.rule_line(stage_context.session_context(root))

        self.assertTrue(line.startswith("- "), line)
        for expected in (
            "`python -c`",
            "`node -e`",
            "`bash -c`",
            "heredoc",
            "`.stage`",
            "refused",
            "Write/Edit",
            "script file",
        ):
            self.assertIn(expected, line)

    def test_rule_matches_what_the_gate_refuses_and_allows(self):
        """The line must describe the gate as it behaves, so the examples are run through it."""
        refused = (
            "python3 -c \"open('.stage/work/active.md').read()\"",
            "python3 - <<'EOF'\nprint(open('.stage/settings.json').read())\nEOF",
            "node -e \"require('fs').readFileSync('.stage/settings.json')\"",
            "bash -c 'cat .stage/work/active.md'",
        )
        allowed = (
            "python3 scripts/report.py .stage/work/active.md",
            "python3 -c \"print('no stage path here')\"",
        )
        for command in refused:
            with self.subTest(command=command):
                self.assertTrue(stage_shell.interpreter_inline_stage_write(command))
        for command in allowed:
            with self.subTest(command=command):
                self.assertFalse(stage_shell.interpreter_inline_stage_write(command))

    def test_project_without_stage_does_not_get_the_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            context = stage_context.session_context(Path(tmp))

        self.assertNotIn("inline interpreter code", context)


if __name__ == "__main__":
    unittest.main()
