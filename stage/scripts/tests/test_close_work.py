from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

CLI = Path(__file__).resolve().parents[2] / "skills" / "stage-retrospective" / "close_work.py"

ITEM = """---
id: W-00000001
kind: chore
scope: src/
autonomous: false
acceptance: {acceptance}
status: active
verification: pending
retrospective: {retro}
retrospective_ref: {ref}
promotion: {promotion}
review: {review}
---

# W-00000001 Sample

## Verification


## Retrospective

See R.

## Promotion decision
"""

ACTIVE = (
    "# Active Work\n\n| Work | Kind | Venue | Purpose | Status | Owner | Item |\n|---|---|---|---|---|---|---|\n"
    "| W-00000001 | chore | claude | x | active | Claude | [current/W-00000001.md](current/W-00000001.md) |\n"
)
REVIEW = "# Review Candidates\n\n| Artifact | Verification | Retrospective | Promotion | Item |\n|---|---|---|---|---|\n"


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), "--project-root", str(root), *args], capture_output=True, text=True
    )


class CloseWorkTest(unittest.TestCase):
    def make(
        self,
        retro="completed",
        ref="R-00000001",
        promotion="not_applicable",
        with_ref_file=True,
        review="not_required",
        acceptance="[]",
    ):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / ".stage/work/current").mkdir(parents=True)
        (root / ".stage/work/retrospectives").mkdir(parents=True)
        (root / ".stage/work/current/W-00000001.md").write_text(
            ITEM.format(
                retro=retro,
                ref=ref,
                promotion=promotion,
                review=review,
                acceptance=acceptance,
            ),
            encoding="utf-8",
        )
        if with_ref_file and ref:
            (root / ".stage/work/retrospectives" / f"{ref}.md").write_text("---\nid: R\n---\n", encoding="utf-8")
        (root / ".stage/work/active.md").write_text(ACTIVE, encoding="utf-8")
        (root / ".stage/work/review.md").write_text(REVIEW, encoding="utf-8")
        (root / ".stage/settings.json").write_text('{"schema_version": 4}\n', encoding="utf-8")
        return tmp, root

    def init_git(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q", str(root)], check=True)

    def test_refuses_staged_dirty_path_inside_scope(self):
        tmp, root = self.make()
        with tmp:
            self.init_git(root)
            source = root / "src/app.py"
            source.parent.mkdir(parents=True)
            source.write_text("print('dirty')\n", encoding="utf-8")
            subprocess.run(["git", "add", "src/app.py"], cwd=root, check=True)
            marker = root / "check-ran"

            proc = run(
                root,
                "W-00000001",
                "--check",
                f"{sys.executable} -c \"from pathlib import Path; Path(r'{marker}').touch()\"",
            )

            self.assertEqual(proc.returncode, 1)
            self.assertIn("src/app.py", proc.stderr)
            self.assertIn("commit source changes first, then close, then archive", proc.stderr)
            self.assertFalse(marker.exists())

    def test_allows_dirty_path_outside_scope(self):
        tmp, root = self.make()
        with tmp:
            self.init_git(root)
            outside = root / "docs/note.md"
            outside.parent.mkdir(parents=True)
            outside.write_text("dirty\n", encoding="utf-8")

            proc = run(root, "W-00000001", "--check", "true")

            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_allows_stage_only_changes(self):
        tmp, root = self.make()
        with tmp:
            self.init_git(root)

            proc = run(root, "W-00000001", "--check", "true")

            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_allows_non_git_tree(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", "true")

            self.assertEqual(proc.returncode, 0, proc.stderr)

    def write_decision(self, root: Path, *, status: str) -> None:
        decisions = root / ".stage/decisions/pending"
        decisions.mkdir(parents=True, exist_ok=True)
        (decisions / "DE-00000001.md").write_text(
            f"---\nid: DE-00000001\nwork_item: W-00000001\nstatus: {status}\n---\n# DE-00000001\n",
            encoding="utf-8",
        )

    def link_decision(self, root: Path) -> None:
        item = root / ".stage/work/current/W-00000001.md"
        text = item.read_text(encoding="utf-8").replace(
            "kind: chore\n", "kind: chore\ndecision_refs: DE-00000001\n", 1
        )
        item.write_text(text, encoding="utf-8")

    def test_refuses_while_linked_decision_is_open(self):
        tmp, root = self.make()
        with tmp:
            self.write_decision(root, status="open")
            self.link_decision(root)
            proc = run(root, "W-00000001", "--check", f"{sys.executable} -c 'print(1)'")
            body = (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8")

        self.assertEqual(1, proc.returncode)
        self.assertIn("DE-00000001", proc.stderr)
        self.assertIn("status: active", body)

    def test_closes_when_linked_decision_is_decided(self):
        tmp, root = self.make()
        with tmp:
            self.write_decision(root, status="decided")
            self.link_decision(root)
            proc = run(root, "W-00000001", "--check", f"{sys.executable} -c 'print(1)'")
            body = (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8")

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("status: completed", body)

    def test_passing_check_closes_and_moves(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", "python3 -c \"print('ok')\"")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8")
            self.assertIn("status: completed", item)
            self.assertIn("verification: passed", item)
            self.assertIn("print('ok')", item)  # evidence embedded
            self.assertNotIn("W-00000001", (root / ".stage/work/active.md").read_text(encoding="utf-8"))
            self.assertIn("[current/W-00000001.md]", (root / ".stage/work/review.md").read_text(encoding="utf-8"))

    def test_passing_check_preserves_existing_verification_and_appends_evidence(self):
        tmp, root = self.make()
        with tmp:
            item_path = root / ".stage/work/current/W-00000001.md"
            item_path.write_text(
                item_path.read_text(encoding="utf-8").replace(
                    "## Verification\n\n",
                    "## Verification\n\nBrowser verification: checkout completed successfully.\n\n",
                    1,
                ),
                encoding="utf-8",
            )

            proc = run(root, "W-00000001", "--check", "python3 -c \"print('check ok')\"")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = item_path.read_text(encoding="utf-8")

        self.assertIn("Browser verification: checkout completed successfully.", item)
        self.assertIn(f"### Executed at close — {date.today().isoformat()}", item)
        self.assertIn("print('check ok')", item)
        self.assertIn("check ok", item)
        self.assertLess(item.index("Browser verification"), item.index("### Executed at close"))

    def test_failing_check_changes_nothing(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", "python3 -c \"import sys; sys.exit(1)\"")
            self.assertEqual(proc.returncode, 1)
            item = (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8")
            self.assertIn("status: active", item)
            self.assertIn("verification: pending", item)

    def test_refuses_without_completed_retrospective(self):
        tmp, root = self.make(retro="pending")
        with tmp:
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("retrospective", proc.stderr)

    def test_refuses_missing_retro_file(self):
        tmp, root = self.make(with_ref_file=False)
        with tmp:
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)

    def test_refuses_retrospective_id_archived_for_different_work_item(self):
        tmp, root = self.make()
        with tmp:
            archive_retro = (
                root / ".stage/official/work/archive/retrospectives/R-00000001.md"
            )
            archive_retro.parent.mkdir(parents=True)
            archive_retro.write_text(
                "---\nid: R-00000001\nwork_item: W-00000099\n---\n",
                encoding="utf-8",
            )
            marker = root / "check-ran"

            proc = run(
                root,
                "W-00000001",
                "--check",
                f"{sys.executable} -c \"from pathlib import Path; Path(r'{marker}').touch()\"",
            )
            body = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("R-00000001", proc.stderr)
        self.assertIn("W-00000001", proc.stderr)
        self.assertIn("W-00000099", proc.stderr)
        self.assertFalse(marker.exists())
        self.assertIn("status: active", body)

    def test_refuses_non_final_promotion(self):
        tmp, root = self.make(promotion="pending")
        with tmp:
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("promotion", proc.stderr)

    def test_refuses_no_check(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("no --check", proc.stderr)

    def test_item_acceptance_closes_without_check_argument(self):
        tmp, root = self.make(acceptance='\n  - "python3 -c \\"print(123)\\""')
        with tmp:
            proc = run(root, "W-00000001")
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("status: completed", item)
        self.assertIn("print(123)", item)

    def test_item_acceptance_and_cli_checks_are_merged(self):
        tmp, root = self.make(acceptance='\n  - "python3 -c \\"print(123)\\""')
        with tmp:
            proc = run(
                root,
                "W-00000001",
                "--check",
                'python3 -c "print(456)"',
            )
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("print(123)", item)
        self.assertIn("print(456)", item)

    def test_failing_item_acceptance_changes_nothing(self):
        tmp, root = self.make(
            acceptance='\n  - "python3 -c \\"import sys; sys.exit(1)\\""'
        )
        with tmp:
            proc = run(root, "W-00000001")
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(1, proc.returncode)
        self.assertIn("status: active", item)
        self.assertIn("verification: pending", item)

    def test_check_output_with_backslashes_does_not_crash(self):
        # Regression: check output is spliced into the Verification section; it must
        # not be read as regex-replacement escapes (\1, \U...) — that once crashed
        # set_section and left the item permanently un-closable.
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", r"""python3 -c "print(r'C:\Users\x back \1 \d+')" """)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8")
            self.assertIn("status: completed", item)
            self.assertIn(r"C:\Users\x", item)

    def test_refuses_item_without_verification_section(self):
        tmp, root = self.make()
        with tmp:
            p = root / ".stage/work/current/W-00000001.md"
            p.write_text(p.read_text(encoding="utf-8").replace("## Verification\n", "## Notes\n"), encoding="utf-8")
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("Verification", proc.stderr)

    def _write_review(self, root, review):
        import json
        (root / ".stage/settings.json").write_text(
            json.dumps({"schema_version": 4, "review": review}), encoding="utf-8"
        )

    def test_configured_review_runs_and_records(self):
        tmp, root = self.make(review="pending")
        with tmp:
            self._write_review(root, {"strengths": {"standard": "python3 -c \"print('review ok')\""}, "stages": {"implementation": "standard"}})
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("review ok", (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8"))

    def test_review_block_verdict_refuses(self):
        tmp, root = self.make(review="pending")
        with tmp:
            self._write_review(root, {"strengths": {"red-team": "python3 -c \"print('BLOCK: found a bug')\""}, "stages": {"implementation": "red-team"}})
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("status: active", (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8"))

    def test_not_required_bypasses_review_even_if_configured(self):
        # Field-driven: an item that does not declare review: pending completes
        # without running the configured review command.
        tmp, root = self.make(review="not_required")
        with tmp:
            self._write_review(root, {"strengths": {"standard": "python3 -c \"print('BLOCK: should not run')\""}, "stages": {"implementation": "standard"}})
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8")
            self.assertIn("status: completed", item)
            self.assertNotIn("should not run", item)

    def test_pending_review_becomes_passed(self):
        tmp, root = self.make(review="pending")
        with tmp:
            self._write_review(root, {"strengths": {"standard": "python3 -c \"print('review ok')\""}, "stages": {"implementation": "standard"}})
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("review: passed", (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8"))

    def test_pending_review_without_command_fails_closed(self):
        # review: pending but the stage has no configured command -> cannot honestly pass.
        tmp, root = self.make(review="pending")
        with tmp:
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("review is pending", proc.stderr)

    def test_review_block_survives_long_output(self):
        # Verdict first, then >40 lines, exit 0 — BLOCK: must still be detected on
        # the raw output, not the clipped evidence.
        tmp, root = self.make(review="pending")
        with tmp:
            cmd = "python3 -c \"print('BLOCK: nope'); [print(i) for i in range(60)]\""
            self._write_review(root, {"strengths": {"red-team": cmd}, "stages": {"implementation": "red-team"}})
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("status: active", (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8"))

    def test_review_strength_typo_fails_closed(self):
        tmp, root = self.make(review="pending")
        with tmp:
            self._write_review(root, {"stages": {"implementation": "redteam"}})  # not a valid strength
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("review config", proc.stderr)

    def test_review_strength_without_command_fails_closed(self):
        tmp, root = self.make(review="pending")
        with tmp:
            self._write_review(root, {"stages": {"implementation": "standard"}})  # no strengths.standard command
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)

    def test_promotion_arg_sets_final(self):
        tmp, root = self.make(promotion="pending")
        with tmp:
            proc = run(root, "W-00000001", "--promotion", "not_applicable", "--check", "true")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("promotion: not_applicable", (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
