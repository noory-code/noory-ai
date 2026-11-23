from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath, PureWindowsPath

STAGE = Path(__file__).resolve().parents[2]
REGISTER = STAGE / "skills" / "stage-work" / "register_work.py"
START = STAGE / "scripts" / "start_work.py"
AUDIT = STAGE / "scripts" / "audit_stage.py"
CODEX_COMPANION = STAGE / "scripts" / "codex_companion.py"
TEMPLATE_ROOT = STAGE / "templates" / "v4" / "project-stage"
sys.path.insert(0, str(STAGE / "scripts"))
import claude_review_companion  # noqa: E402

SETTINGS = {
    "schema_version": 5,
    "venue_routing": {"fix": "codex", "design": "claude"},
    "environment_venues": {"cloud": "claude"},
}
CARD_ARGS = (
    "--title",
    "Fix the thing",
    "--kind",
    "fix",
    "--scale",
    "story",
    "--scope",
    "src/",
    "--purpose",
    "Deliver the requested outcome.",
    "--success-criterion",
    "The user can observe the requested outcome",
)


def run(script: Path, root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class EnvironmentVenuePolicyTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.stage = self.root / ".stage"
        shutil.copytree(TEMPLATE_ROOT, self.stage)
        (self.stage / "settings.jsonc").unlink()
        (self.stage / "settings.json").write_text(json.dumps(SETTINGS), encoding="utf-8")

    def card(self, item_id: str = "W-00000001") -> Path:
        return self.stage / "work/current" / item_id / "_story.md"

    def audit_codes(self) -> str:
        return run(AUDIT, self.root).stdout

    def test_register_permits_the_environment_venue_without_an_exception(self):
        proc = run(REGISTER, self.root, *CARD_ARGS, "--environment", "cloud", "--review")
        text = self.card().read_text(encoding="utf-8")
        audit = self.audit_codes()

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("permitted by environment `cloud`", proc.stdout)
        self.assertIn("venue: claude\nenvironment: cloud\n", text)
        self.assertIn("review: pending", text)
        self.assertIn("decision_refs:\n", text)
        self.assertNotIn("VENUE003", audit)
        self.assertNotIn("VENUE006", audit)

    def test_register_refuses_cards_that_break_the_environment_policy(self):
        cases = {
            "undeclared environment": (
                ("--environment", "mars", "--review"),
                "environment `mars` is not declared in environment_venues",
            ),
            "venue differs from the environment": (
                ("--environment", "cloud", "--venue", "codex", "--review"),
                "environment `cloud` runs venue `claude`, but the card names venue `codex`",
            ),
            "no independent close review": (
                ("--environment", "cloud"),
                "environment `cloud` requires an independent close review",
            ),
            "planned card": (
                ("--environment", "cloud", "--review", "--backlog"),
                "a planned card takes no --environment",
            ),
        }
        for label, (extra, expected) in cases.items():
            with self.subTest(case=label):
                proc = run(REGISTER, self.root, *CARD_ARGS, *extra)

                self.assertEqual(1, proc.returncode, proc.stdout)
                self.assertIn(expected, proc.stderr)
                self.assertFalse(self.card().exists())
                self.assertFalse((self.stage / "work/planned/W-00000001").exists())

    def test_start_applies_the_same_policy_to_a_planned_card(self):
        captured = run(REGISTER, self.root, *CARD_ARGS, "--backlog")
        self.assertEqual(0, captured.returncode, captured.stderr)

        refused = run(START, self.root, "W-00000001", "--scope", "src/", "--environment", "cloud")
        started = run(
            START, self.root, "W-00000001", "--scope", "src/", "--environment", "cloud", "--review"
        )
        text = self.card().read_text(encoding="utf-8")
        audit = self.audit_codes()

        self.assertEqual(1, refused.returncode, refused.stdout)
        self.assertIn("requires an independent close review", refused.stderr)
        self.assertEqual(0, started.returncode, started.stderr)
        self.assertIn("venue: claude\nenvironment: cloud\n", text)
        self.assertIn("review: pending", text)
        self.assertNotIn("VENUE003", audit)
        self.assertNotIn("VENUE006", audit)

    def test_audit_reports_an_environment_card_that_breaks_the_policy(self):
        proc = run(REGISTER, self.root, *CARD_ARGS, "--environment", "cloud", "--review")
        self.assertEqual(0, proc.returncode, proc.stderr)
        card = self.card()
        allowed = card.read_text(encoding="utf-8")
        cases = {
            "review dropped": (
                allowed.replace("review: pending", "review: not_required"),
                "VENUE006",
            ),
            "environment removed": (allowed.replace("environment: cloud\n", ""), "VENUE003"),
        }
        for label, (text, code) in cases.items():
            with self.subTest(case=label):
                card.write_text(text, encoding="utf-8")

                audit = self.audit_codes()

                self.assertIn(code, audit)
        card.write_text(allowed, encoding="utf-8")
        self.assertNotIn("VENUE00", self.audit_codes())


class ClaudeReviewCompanionTest(unittest.TestCase):
    def test_allows_verdict_edits_and_any_shell_command_with_the_prompt_last(self):
        with tempfile.TemporaryDirectory() as tmp:
            verdict = Path(tmp) / "verdict.json"
            command = claude_review_companion.claude_command(
                ["task", "--model", "gpt-6-astra", "--write", "Review the card."],
                {
                    "STAGE_CHANGED_PATHS_FILE": str(Path(tmp) / "review-x/changed-paths.json"),
                    "STAGE_REVIEW_VERDICT_FILE": str(verdict),
                },
                "claude",
                "linux",
            )
            rule = claude_review_companion.absolute_rule_path(verdict.resolve())

        self.assertEqual(
            [
                "claude",
                "-p",
                "--output-format",
                "stream-json",
                "--verbose",
                "--add-dir",
                str(Path(tmp) / "review-x"),
                "--model",
                "opus[1m]",
                "--allowedTools",
                f"Edit({rule})",
                "Bash",
                "--disallowedTools",
                "Bash(git push)",
                "Bash(git push:*)",
                "Bash(git commit)",
                "Bash(git commit:*)",
                "--",
                "Review the card." + claude_review_companion.REVIEWER_RULES,
            ],
            command,
        )
        self.assertNotIn("acceptEdits", command)
        self.assertNotIn("--permission-mode", command)
        self.assertFalse(any(part.startswith("Write(") for part in command))
        # Only the verdict file is open to the file-edit tools.
        self.assertEqual(1, sum(part.startswith("Edit(") for part in command))

    def test_windows_also_allows_and_denies_through_the_powershell_tool(self):
        def rules(platform: str) -> tuple[list[str], list[str]]:
            command = claude_review_companion.claude_command(
                ["Review."], {"STAGE_REVIEW_VERDICT_FILE": "/v.json"}, "claude", platform
            )
            allow, deny = command.index("--allowedTools"), command.index("--disallowedTools")
            return command[allow + 1 : deny], command[deny + 1 : command.index("--")]

        # A Bash rule does not cover the PowerShell tool Claude Code offers on Windows.
        allowed, denied = rules("win32")
        self.assertTrue(allowed[0].startswith("Edit("))
        self.assertEqual(["Bash", "PowerShell"], allowed[1:])
        for command in claude_review_companion.DENIED_COMMANDS:
            for tool in ("Bash", "PowerShell"):
                self.assertIn(f"{tool}({command})", denied)
                self.assertIn(f"{tool}({command}:*)", denied)
        for platform in ("linux", "darwin"):
            allowed, denied = rules(platform)
            self.assertEqual(["Bash"], allowed[1:])
            self.assertFalse(any(rule.startswith("PowerShell") for rule in denied))

    def test_the_reviewer_may_not_publish_or_record_a_change(self):
        self.assertIn("git push", claude_review_companion.DENIED_COMMANDS)
        self.assertIn("git commit", claude_review_companion.DENIED_COMMANDS)

    def test_the_verdict_rule_is_absolute_on_posix_and_on_a_windows_drive(self):
        rule = claude_review_companion.absolute_rule_path

        self.assertEqual("//work/.stage/v.json", rule(PurePosixPath("/work/.stage/v.json")))
        # Claude Code matches no rule that keeps the drive colon.
        self.assertEqual(
            "//c/work/.stage/v.json", rule(PureWindowsPath("C:\\work\\.stage\\v.json"))
        )

    def test_model_override_and_missing_inputs(self):
        command = claude_review_companion.claude_command(
            ["Review."],
            {"STAGE_CLAUDE_REVIEW_MODEL": "sonnet", "STAGE_REVIEW_VERDICT_FILE": "/v.json"},
            "claude",
        )

        self.assertEqual("sonnet", command[command.index("--model") + 1])
        self.assertNotIn("--add-dir", command)
        with self.assertRaisesRegex(ValueError, "STAGE_REVIEW_VERDICT_FILE"):
            claude_review_companion.claude_command(["Review."], {}, "claude")

    def test_codex_companion_runs_a_python_stand_in_without_node(self):
        with tempfile.TemporaryDirectory() as tmp:
            stand_in = Path(tmp) / "stand_in.py"
            stand_in.write_text(
                "import json, sys\nprint(json.dumps(sys.argv[1:]))\nraise SystemExit(4)\n",
                encoding="utf-8",
            )
            env = {**os.environ, "STAGE_CODEX_COMPANION": str(stand_in), "PATH": ""}

            proc = subprocess.run(
                [sys.executable, str(CODEX_COMPANION), "task", "Review."],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )

        self.assertEqual(4, proc.returncode, proc.stderr)
        self.assertEqual(["task", "Review."], json.loads(proc.stdout))


if __name__ == "__main__":
    unittest.main()
