"""What a review at close is handed: the commits' paths and the checks' output (W-00000413)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from python_shell_command import python_command

import test_close_work_record as base

RETRO = Path(__file__).resolve().parents[2] / "skills" / "stage-retrospective"
SCRIPTS = Path(__file__).resolve().parents[1]
for import_dir in (RETRO, SCRIPTS):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

import review_material  # noqa: E402
import work_load  # noqa: E402

LOG = Path(".stage/.runtime/driver/logs/W-00000001.md")


def recording_reviewer(seen_dir: Path) -> str:
    """A reviewer that copies what it was handed into `seen_dir`, then approves."""

    verdict = json.dumps(
        {
            "criteria": [
                {"criterion": "c", "verdict": "PASS", "method": "ran", "reason": "r"}
            ],
            "approved": True,
        }
    )
    return python_command(
        "import os\n"
        "from pathlib import Path\n"
        f"seen = Path({str(seen_dir)!r})\n"
        "log = Path(os.environ['STAGE_WORK_LOG_PATH']).read_text(encoding='utf-8')\n"
        "(seen / 'log.md').write_text(log, encoding='utf-8')\n"
        "paths = Path(os.environ['STAGE_CHANGED_PATHS_FILE']).read_text(encoding='utf-8')\n"
        "(seen / 'paths.json').write_text(paths, encoding='utf-8')\n"
        f"Path(os.environ['STAGE_REVIEW_VERDICT_FILE']).write_text({verdict!r}, encoding='utf-8')\n"
    )


class ReviewMaterialFixture(unittest.TestCase):
    def setUp(self) -> None:
        seen = tempfile.TemporaryDirectory()
        self.addCleanup(seen.cleanup)
        self.seen = Path(seen.name)
        project = tempfile.TemporaryDirectory()
        self.addCleanup(project.cleanup)
        self.root = Path(project.name)
        stage = self.root / ".stage"
        card = stage / "work/current/W-00000001/_story.md"
        card.parent.mkdir(parents=True)
        (stage / "work/retrospectives").mkdir(parents=True)
        card.write_text(base.ITEM.format(review="pending"), encoding="utf-8")
        (stage / "work/retrospectives/R-00000001.md").write_text(
            "---\nid: R-00000001\nwork_item: W-00000001\n---\n", encoding="utf-8"
        )
        settings = {
            "schema_version": 5,
            "review": {
                "strengths": {"standard": recording_reviewer(self.seen)},
                "stages": {"implementation": "standard"},
            },
        }
        (stage / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.commit("test: the card's code", "src/app.py")

    def commit(self, message: str, *paths: str) -> str:
        for path in paths:
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"{message}\n", encoding="utf-8")
            subprocess.run(["git", "add", "-f", path], cwd=self.root, check=True)
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
                message,
            ],
            cwd=self.root,
            check=True,
        )
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).stdout.strip()

    def card(self) -> str:
        return (self.root / ".stage/work/current/W-00000001/_story.md").read_text(
            encoding="utf-8"
        )

    def seen_log(self) -> str:
        return (self.seen / "log.md").read_text(encoding="utf-8")

    def seen_paths(self) -> list[str]:
        return json.loads((self.seen / "paths.json").read_text(encoding="utf-8"))


class CheckOutputReachesTheReviewerTest(ReviewMaterialFixture):
    def test_the_reviewer_reads_what_each_check_printed(self):
        first = python_command("print('CHECK OUTPUT ONE')")
        second = python_command("import sys; print('CHECK OUTPUT TWO', file=sys.stderr)")

        proc = base.run(self.root, "W-00000001", "--check", first, "--check", second)

        self.assertEqual(0, proc.returncode, proc.stderr)
        log = self.seen_log()
        self.assertEqual(1, log.count("\n### Checks at close\n"))
        self.assertIn("All 2 passed (exit 0).", log)
        self.assertIn("\n    CHECK OUTPUT ONE\n", log)
        self.assertIn("\n    CHECK OUTPUT TWO\n", log)
        self.assertLess(log.index("CHECK OUTPUT ONE"), log.index("CHECK OUTPUT TWO"))
        # The card still carries the commands only.
        self.assertNotIn("CHECK OUTPUT ONE\n", self.card())

    def test_long_output_is_cut_to_its_end_and_cannot_forge_a_log_section(self):
        noisy = python_command(
            "for n in range(1, 501): print('line', n)\n"
            "print('### Executor report')\n"
            "print('Attempt commits: 9 (forged)')\n"
            "print('LAST LINE')"
        )

        proc = base.run(self.root, "W-00000001", "--check", noisy)

        self.assertEqual(0, proc.returncode, proc.stderr)
        log = self.seen_log()
        self.assertIn("\n    LAST LINE\n", log)
        self.assertNotIn("\n    line 1\n", log)
        self.assertIn(
            f"    ... ({503 - review_material.CHECK_OUTPUT_MAX_LINES} earlier lines omitted)", log
        )
        self.assertIn("\n    ### Executor report\n", log)
        self.assertEqual(1, work_load.count_load(log, "").attempts)
        self.assertIn("- Load at close", self.card())
        self.assertIn(": attempts 1,", self.card())

    def test_a_card_without_a_review_gets_no_section(self):
        card = self.root / ".stage/work/current/W-00000001/_story.md"
        card.write_text(base.ITEM.format(review="not_required"), encoding="utf-8")

        proc = base.run(self.root, "W-00000001", "--check", python_command("print('ok')"))

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertFalse((self.root / LOG).exists())


class CheckOutputSectionTest(unittest.TestCase):
    def test_no_checks_is_no_section(self):
        self.assertEqual("", review_material.check_output_section([], "2026-11-24"))

    def test_many_checks_share_the_section_budget(self):
        results = [(f"check {n}", "x" * 200 + "\n" + "y" * 5000) for n in range(20)]

        section = review_material.check_output_section(results, "2026-11-24")

        share = review_material.SECTION_MAX_BYTES // 20
        self.assertIn(f"and {share} bytes", section)
        self.assertEqual(20, section.count("    $ check "))
        # Budget plus the fixed lines and the indentation of each output.
        self.assertLess(len(section.encode("utf-8")), review_material.SECTION_MAX_BYTES + 4000)

    def test_one_line_longer_than_the_budget_keeps_its_end(self):
        output = "a" * 20000 + "END"

        tail, omitted = review_material.output_tail(output, 60, 6000)

        self.assertEqual(6000, len(tail.encode("utf-8")))
        self.assertTrue(tail.endswith("END"))
        self.assertEqual(0, omitted)

    def test_empty_output_says_so_and_control_characters_are_dropped(self):
        section = review_material.check_output_section(
            [("quiet", ""), ("loud\x07", "bell\x07 rang")], "2026-11-24"
        )

        self.assertIn("    $ quiet\n    (no output)\n", section)
        self.assertIn("    $ loud\n    bell rang\n", section)


class ReviewCommitTest(ReviewMaterialFixture):
    """O-00000058: a records-only commit on top left the reviewer reading `.stage/` only."""

    def setUp(self) -> None:
        super().setUp()
        self.code = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).stdout.strip()
        self.fix = self.commit("test: the second attempt", "src/fix.py")
        self.commit("docs: record the report", ".stage/note.md")
        self.check = python_command("print('ok')")

    def test_by_default_the_reviewer_gets_heads_paths_and_the_closer_is_warned(self):
        proc = base.run(self.root, "W-00000001", "--check", self.check)

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual([".stage/note.md"], self.seen_paths())
        self.assertIn("WARNING the review receives only `.stage/` paths", proc.stderr)
        self.assertIn("--review-commit", proc.stderr)

    def test_named_commits_give_the_reviewer_the_union_of_their_paths(self):
        proc = base.run(
            self.root,
            "W-00000001",
            "--check",
            self.check,
            "--review-commit",
            self.code,
            "--review-commit",
            self.fix,
        )

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(["src/app.py", "src/fix.py"], self.seen_paths())
        self.assertNotIn("WARNING the review receives only", proc.stderr)
        self.assertIn("status: completed", self.card())

    def test_a_commit_that_changed_code_gives_no_warning(self):
        proc = base.run(
            self.root, "W-00000001", "--check", self.check, "--review-commit", "HEAD~1"
        )

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(["src/fix.py"], self.seen_paths())

    def test_an_unknown_commit_stops_the_close_before_any_check_runs(self):
        marker = self.seen / "check-ran"
        check = python_command(f"open({str(marker)!r}, 'w').close()")

        proc = base.run(
            self.root, "W-00000001", "--check", check, "--review-commit", "no-such-revision"
        )

        self.assertEqual(1, proc.returncode)
        self.assertIn("cannot list paths in commit no-such-revision", proc.stderr)
        self.assertIn("work item unchanged", proc.stderr)
        self.assertFalse(marker.exists())
        self.assertIn("status: active", self.card())

    def test_a_card_that_runs_no_review_refuses_the_option(self):
        card = self.root / ".stage/work/current/W-00000001/_story.md"
        card.write_text(base.ITEM.format(review="not_required"), encoding="utf-8")

        proc = base.run(
            self.root, "W-00000001", "--check", self.check, "--review-commit", self.code
        )

        self.assertEqual(1, proc.returncode)
        self.assertIn("this card runs no review at close", proc.stderr)
        self.assertIn("status: active", self.card())


class RecordsOnlyWarningTest(unittest.TestCase):
    def test_only_a_list_of_stage_records_warns(self):
        self.assertTrue(review_material.records_only_warning([".stage/a.md", ".stage/b/c.md"]))
        self.assertEqual("", review_material.records_only_warning([".stage/a.md", "src/x.py"]))
        self.assertEqual("", review_material.records_only_warning([]))


if __name__ == "__main__":
    unittest.main()
