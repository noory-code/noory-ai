# The hook must run wherever `python3` points on a host machine (3.9+), so the
# test module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


HOOK_PATH = Path(__file__).resolve().parents[1] / "stage_guard.py"
SPEC = importlib.util.spec_from_file_location("stage_guard", HOOK_PATH)
stage_guard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["stage_guard"] = stage_guard
SPEC.loader.exec_module(stage_guard)


def decision(result: dict) -> str:
    # Allow is empty output (cross-host contract: Codex rejects an explicit
    # permissionDecision:allow without updatedInput as unsupported).
    if not result:
        return "allow"
    return result["hookSpecificOutput"]["permissionDecision"]


class InterpreterInlineGuardTest(unittest.TestCase):
    def create_stage(self, root: Path) -> None:
        stage_root = root / ".stage"
        stage_root.mkdir()
        (stage_root / "settings.json").write_text(
            '{"schema_version": 5}\n',
            encoding="utf-8",
        )
        work_item = stage_root / "work" / "current" / "W-0001.md"
        work_item.parent.mkdir(parents=True)
        work_item.write_text(
            (
                "---\n"
                "id: W-0001\n"
                "title: Test work\n"
                "status: active\n"
                "verification: pending\n"
                "retrospective: pending\n"
                "retrospective_ref:\n"
                "promotion: pending\n"
                "scope: '*'\n"
                "promotes:\n"
                "---\n"
                "# W-0001 Test work\n"
            ),
            encoding="utf-8",
        )

    def payload(self, root: Path, command: str) -> dict:
        return {
            "tool_name": "Bash",
            "cwd": str(root),
            "tool_input": {"command": command},
        }

    def test_denies_opaque_inline_interpreters_that_reference_stage(self) -> None:
        commands = (
            (
                "python3 - <<'EOF'\n"
                "import shutil\n"
                "shutil.copyfile('source.md', '.stage/official/x.md')\n"
                "EOF"
            ),
            """python3 -c "open('.stage/official/x.md', 'w').write('x')\"""",
            """/usr/bin/python3.11 -W ignore -c "print('.stage')\"""",
            """node -e "fs.writeFileSync('.stage/official/x.md', 'x')\"""",
            """perl -e 'open my $fh, ">", ".stage/official/x.md"'""",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_stage(root)

            for command in commands:
                with self.subTest(command=command):
                    self.assertTrue(stage_guard.interpreter_inline_stage_write(command))

                    result = stage_guard.validate_pre_tool(self.payload(root, command))

                    self.assertNotEqual(decision(result), "allow")

    def test_allows_non_opaque_or_non_stage_shell_commands(self) -> None:
        commands = (
            "python3 stage/scripts/promote_intent.py --path .stage/official/x.md",
            "python3 -m unittest discover -s stage/hooks/tests -q",
            'python3 -c "print(1+1)"',
            "cp a b",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_stage(root)

            for command in commands:
                with self.subTest(command=command):
                    self.assertFalse(stage_guard.interpreter_inline_stage_write(command))

                    result = stage_guard.validate_pre_tool(self.payload(root, command))

                    self.assertEqual(decision(result), "allow")

    def test_allows_named_script_after_unrelated_heredoc(self) -> None:
        commands = (
            (
                "cat > note.md <<'X'\n"
                "hello .stage/official/x.md\n"
                "X\n"
                "python3 stage/scripts/audit_stage.py --project-root ."
            ),
            (
                "cat <<'X'\n"
                ".stage/official/x.md\n"
                "X\n"
                "python3 stage/scripts/audit_stage.py --project-root ."
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_stage(root)

            for command in commands:
                with self.subTest(command=command):
                    self.assertFalse(stage_guard.interpreter_inline_stage_write(command))

                    result = stage_guard.validate_pre_tool(self.payload(root, command))

                    self.assertEqual(decision(result), "allow")


if __name__ == "__main__":
    unittest.main()
