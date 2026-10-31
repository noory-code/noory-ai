from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
    def test_allows_only_the_verdict_file_and_unittest_with_the_prompt_last(self):
        with tempfile.TemporaryDirectory() as tmp:
            verdict = Path(tmp) / "verdict.json"
            command = claude_review_companion.claude_command(
                ["task", "--model", "gpt-6-astra", "--write", "Review the card."],
                {
                    "STAGE_CHANGED_PATHS_FILE": str(Path(tmp) / "review-x/changed-paths.json"),
                    "STAGE_REVIEW_VERDICT_FILE": str(verdict),
                },
                "claude",
            )
            rule = "/" + verdict.resolve().as_posix()

        self.assertEqual(
            [
                "claude",
                "-p",
                "--add-dir",
                str(Path(tmp) / "review-x"),
                "--model",
                "opus[1m]",
                "--allowedTools",
                f"Write({rule})",
                f"Edit({rule})",
                "Bash(python3 -m unittest:*)",
                "--",
                "Review the card.",
            ],
            command,
        )
        self.assertNotIn("acceptEdits", command)
        self.assertNotIn("--permission-mode", command)

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
                env=env,
            )

        self.assertEqual(4, proc.returncode, proc.stderr)
        self.assertEqual(["task", "Review."], json.loads(proc.stdout))


if __name__ == "__main__":
    unittest.main()
