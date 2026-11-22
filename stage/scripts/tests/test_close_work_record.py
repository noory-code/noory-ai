"""What `close_work.py` leaves on the card: one line per check run and per review."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from python_shell_command import python_command

CLI = Path(__file__).resolve().parents[2] / "skills" / "stage-retrospective" / "close_work.py"
TODAY = date.today().isoformat()

ITEM = """---
id: W-00000001
kind: chore
venue: codex
scope: src/
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000001
promotion: not_applicable
review: {review}
---

# W-00000001 Sample

## Verification

Hand-written note.

## Retrospective

See R.
"""


def reviewer_command(verdicts: list[str]) -> str:
    """A reviewer that reports once and writes one criterion per given verdict."""

    criteria = [
        {"criterion": f"criterion {number}", "verdict": verdict, "reason": "LONG REASON TEXT"}
        for number, verdict in enumerate(verdicts, 1)
    ]
    payload = json.dumps(
        {"criteria": criteria, "approved": all(v == "PASS" for v in verdicts)}
    )
    script = python_command(
        "import os\n"
        "from pathlib import Path\n"
        "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
        "with log.open('a', encoding='utf-8') as handle:\n"
        "    handle.write('\\n### Reviewer report\\nreport body\\n')\n"
        f"Path(os.environ['STAGE_REVIEW_VERDICT_FILE']).write_text({payload!r}, encoding='utf-8')\n"
    )
    return script


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class CloseRecordTest(unittest.TestCase):
    def make(
        self, review: str = "not_required", review_command: str | None = None
    ) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        stage = root / ".stage"
        card = stage / "work/current/W-00000001/_story.md"
        card.parent.mkdir(parents=True)
        (stage / "work/retrospectives").mkdir(parents=True)
        card.write_text(ITEM.format(review=review), encoding="utf-8")
        (stage / "work/retrospectives/R-00000001.md").write_text(
            "---\nid: R-00000001\nwork_item: W-00000001\n---\n", encoding="utf-8"
        )
        settings: dict[str, object] = {"schema_version": 5}
        if review_command is not None:
            settings["review"] = {
                "strengths": {"standard": review_command},
                "stages": {"implementation": "standard"},
            }
        (stage / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
        if review_command is not None:
            self.commit_source(root)
        return tmp, root

    def commit_source(self, root: Path) -> None:
        """The close review judges the paths of the commit at HEAD."""

        source = root / "src/app.py"
        source.parent.mkdir(parents=True)
        source.write_text("print('reviewed')\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "add", "src/app.py"], cwd=root, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Stage Test",
                "-c",
                "user.email=stage-test@example.com",
                "commit",
                "-q",
                "-m",
                "test: add review material",
            ],
            cwd=root,
            check=True,
        )

    def card(self, root: Path) -> str:
        return (root / ".stage/work/current/W-00000001/_story.md").read_text(encoding="utf-8")

    def test_checks_leave_one_line_and_no_output(self):
        tmp, root = self.make()
        with tmp:
            first = python_command("print('CHECK OUTPUT ONE')")
            second = python_command("print('CHECK OUTPUT TWO')")

            proc = run(root, "W-00000001", "--check", first, "--check", second)
            card = self.card(root)

        self.assertEqual(0, proc.returncode, proc.stderr)
        lines = [line for line in card.splitlines() if line.startswith("- Checks at close")]
        self.assertEqual(1, len(lines), card)
        self.assertIn(f"- Checks at close {TODAY}: 2 passed", lines[0])
        self.assertIn(first, lines[0])
        self.assertIn(second, lines[0])
        self.assertNotIn("CHECK OUTPUT ONE\n", card)
        self.assertNotIn("### Executed at close", card)
        self.assertNotIn("```", card)
        self.assertLess(card.index("Hand-written note."), card.index("- Checks at close"))
        self.assertLess(card.index("- Checks at close"), card.index("## Retrospective"))

    def test_approved_review_leaves_one_verdict_line_without_reasons(self):
        tmp, root = self.make(review="pending", review_command=reviewer_command(["PASS", "PASS"]))
        with tmp:
            proc = run(root, "W-00000001", "--check", python_command("print('ok')"))
            card = self.card(root)

        self.assertEqual(0, proc.returncode, proc.stderr)
        lines = [line for line in card.splitlines() if line.startswith("- Review at close")]
        self.assertEqual(1, len(lines), card)
        self.assertIn(f"- Review at close {TODAY} by ", lines[0])
        self.assertIn(": approved (1 PASS, 2 PASS)", lines[0])
        self.assertNotIn("LONG REASON TEXT", card)
        self.assertNotIn("### Review at close", card)
        self.assertIn("review: passed", card)

    def test_rejected_review_leaves_a_line_and_keeps_the_item_open(self):
        tmp, root = self.make(review="pending", review_command=reviewer_command(["PASS", "FAIL"]))
        with tmp:
            proc = run(root, "W-00000001", "--check", python_command("print('ok')"))
            card = self.card(root)

        self.assertEqual(1, proc.returncode)
        lines = [line for line in card.splitlines() if line.startswith("- Review at close")]
        self.assertEqual(1, len(lines), card)
        self.assertIn(": rejected (1 PASS, 2 FAIL)", lines[0])
        self.assertIn("status: active", card)
        self.assertIn("verification: pending", card)
        self.assertIn("review: pending", card)
        self.assertNotIn("- Checks at close", card)
        self.assertNotIn("LONG REASON TEXT", card)

    def test_rejections_accumulate_so_the_repository_counts_them(self):
        tmp, root = self.make(review="pending", review_command=reviewer_command(["FAIL"]))
        with tmp:
            run(root, "W-00000001", "--check", python_command("print('ok')"))
            run(root, "W-00000001", "--check", python_command("print('ok')"))
            settings = root / ".stage/settings.json"
            config = json.loads(settings.read_text(encoding="utf-8"))
            config["review"]["strengths"]["standard"] = reviewer_command(["PASS"])
            settings.write_text(json.dumps(config), encoding="utf-8")

            proc = run(root, "W-00000001", "--check", python_command("print('ok')"))
            card = self.card(root)

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(2, card.count(": rejected (1 FAIL)"))
        self.assertEqual(1, card.count(": approved (1 PASS)"))

    def test_review_line_names_the_label_of_the_review_command(self):
        command = reviewer_command(["PASS"])
        labelled = command + " --label claude"
        tmp, root = self.make(review="pending", review_command=labelled)
        with tmp:
            proc = run(root, "W-00000001", "--check", python_command("print('ok')"))
            card = self.card(root)

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn(f"- Review at close {TODAY} by claude: approved", card)


if __name__ == "__main__":
    unittest.main()
