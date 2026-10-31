from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
CLI = SCRIPTS / "import_executor_report.py"
sys.path.insert(0, str(SCRIPTS.parent / "skills" / "stage-retrospective"))
import close_work  # noqa: E402

LOG = Path(".stage/.runtime/driver/logs/W-00000001.md")

WRAPPED_MESSAGE = """fix(app): change the app

Summary paragraph that is not part of the report.

### Executor report

What changed: rewrote the app entry point so that it reads its settings
from the project root instead of the current directory.

Why: W-00000001 - the app must start from any working
directory.

Decisions made: kept the old flag as an alias; documented it in the
changelog.

Work not done: None.

Changed paths (JSON): ["src/app.py",
"src/settings.py"]

Review request: Judge both success criteria of
W-00000001.

Tests pass.

Co-Authored-By: Someone <someone@example.invalid>
"""


class ImportExecutorReportTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.commits = 0
        self.git("init", "-q")
        (self.root / ".stage").mkdir()
        (self.root / "README.md").write_text("base\n", encoding="utf-8")
        self.commit("chore: base")

    def git(self, *args: str) -> None:
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Stage Test",
                "-c",
                "user.email=stage@example.invalid",
                *args,
            ],
            cwd=self.root,
            check=True,
            capture_output=True,
        )

    def commit(self, message: str, *paths: str) -> None:
        self.commits += 1
        for path in paths:
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"{path} {self.commits}\n", encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(CLI), "--project-root", str(self.root), "W-00000001", *args],
            capture_output=True,
            text=True,
        )

    def test_joins_wrapped_fields_onto_one_line_each(self):
        self.commit(WRAPPED_MESSAGE, "src/app.py", "src/settings.py")

        proc = self.run_cli()
        log = (self.root / LOG).read_text(encoding="utf-8")

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertTrue(log.startswith(close_work.WORK_LOG_PREAMBLE.format(item_id="W-00000001")))
        self.assertIn(
            "\n### Executor report\n"
            "What changed: rewrote the app entry point so that it reads its settings "
            "from the project root instead of the current directory.\n"
            "Why: W-00000001 - the app must start from any working directory.\n"
            "Decisions made: kept the old flag as an alias; documented it in the changelog.\n"
            "Work not done: None.\n"
            "Changed paths (JSON):\n"
            '["src/app.py", "src/settings.py"]\n'
            "Review request: Judge both success criteria of W-00000001.\n",
            log,
        )
        self.assertNotIn("Tests pass.", log)
        self.assertNotIn("Co-Authored-By", log)
        self.assertEqual(
            [
                "What changed: rewrote the app entry point so that it reads its settings "
                "from the project root instead of the current directory.",
                "Why: W-00000001 - the app must start from any working directory.",
                "Decisions made: kept the old flag as an alias; documented it in the changelog.",
                "Work not done: None.",
            ],
            close_work.latest_executor_report_lines(log),
        )

    def test_appends_after_an_existing_work_log(self):
        log_path = self.root / LOG
        log_path.parent.mkdir(parents=True)
        log_path.write_text("# existing log\n\nearlier attempt\n", encoding="utf-8")
        self.commit(WRAPPED_MESSAGE, "src/app.py", "src/settings.py")

        proc = self.run_cli("--commit", "HEAD")
        log = log_path.read_text(encoding="utf-8")

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertTrue(log.startswith("# existing log\n\nearlier attempt\n\n### Executor report\n"))

    def head(self) -> str:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def test_multi_attempt_report_is_checked_against_every_listed_commit(self):
        cumulative = (
            "fix(app): second attempt\n\n### Executor report\n"
            "What changed: second attempt fixed b\n"
            "Why: W-00000001 - finish the card\n"
            "Decisions made: kept attempt one's change to a\n"
            "Work not done: None\n"
            'Changed paths (JSON): ["src/a.py", "src/b.py"]\n'
            "Review request: judge both attempts\n"
        )
        self.commit("fix(app): first attempt", "src/a.py")
        first = self.head()
        self.commit("chore(other): another card's commit in between", "other/card.txt")
        self.commit(cumulative, "src/b.py")
        second = self.head()

        last_only = self.run_cli("--commit", second)
        both = self.run_cli("--commit", first, "--commit", second)
        log = (self.root / LOG).read_text(encoding="utf-8")

        self.assertEqual(1, last_only.returncode, last_only.stdout)
        self.assertIn("do not match", last_only.stderr)
        self.assertEqual(0, both.returncode, both.stderr)
        self.assertIn(f"from {first}, {second}", both.stdout)
        self.assertIn('Changed paths (JSON):\n["src/a.py", "src/b.py"]\n', log)
        self.assertEqual(1, log.count("### Executor report"))

    def test_refuses_reports_that_fail_the_contract_and_leaves_the_log_alone(self):
        cases = {
            "missing judgment field": (
                WRAPPED_MESSAGE.replace("Decisions made: kept the old flag as an alias; "
                                        "documented it in the\nchangelog.\n\n", ""),
                ("src/app.py", "src/settings.py"),
                "missing non-empty `Decisions made:`",
            ),
            "claimed paths differ from the commit": (
                WRAPPED_MESSAGE,
                ("src/app.py",),
                "src/settings.py",
            ),
            "no report in the commit": (
                "fix(app): change the app\n\nNo report here.\n",
                ("src/app.py",),
                "has no `### Executor report` section",
            ),
            "repeated field": (
                WRAPPED_MESSAGE.replace("Work not done: None.\n", "Work not done: None.\nWhy: again\n"),
                ("src/app.py", "src/settings.py"),
                "repeats `Why:`",
            ),
        }
        for label, (message, paths, expected) in cases.items():
            with self.subTest(case=label):
                self.commit(message, *paths)
                log_path = self.root / LOG
                before = log_path.read_text(encoding="utf-8") if log_path.exists() else None

                proc = self.run_cli()
                after = log_path.read_text(encoding="utf-8") if log_path.exists() else None

                self.assertEqual(1, proc.returncode, proc.stdout)
                self.assertIn("work log unchanged", proc.stderr)
                self.assertIn(expected, proc.stderr)
                self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
