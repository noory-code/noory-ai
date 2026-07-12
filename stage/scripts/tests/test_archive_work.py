# The CLI must run wherever `python3` points on a host machine (3.9+), so the
# test module keeps the same annotation-laziness contract as the scripts.
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# archive_work.py is owned by (and lives inside) the stage-archive skill; the
# test stays in the central suite so one `unittest discover` covers everything.
CLI_PATH = Path(__file__).resolve().parents[2] / "skills" / "stage-archive" / "archive_work.py"


def run_cli(project_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI_PATH), "--project-root", str(project_root), *args],
        capture_output=True,
        text=True,
    )


ITEM = """---
id: {wid}
scope: src/
status: {status}
retrospective: {retro}
retrospective_ref: {ref}
promotion: not_applicable
---

# {wid} Sample
"""

RETRO = "---\nid: {ref}\nwork_item: {wid}\n---\n\n# {ref} Sample retro\n"

REVIEW = (
    "# Review Candidates\n\n"
    "| Artifact | Verification | Retrospective | Promotion | Item |\n"
    "|---|---|---|---|---|\n"
    "| {wid} | passed | completed | not_applicable | [items/{wid}.md](items/{wid}.md) |\n"
)

HAND_WRITTEN_REVIEW = (
    "# Review Candidates\n\n"
    "| Artifact | Verification | Retrospective | Promotion | Item |\n"
    "|---|---|---|---|---|\n"
    "| Fix archive cleanup | passed | completed | not_applicable | "
    "[items/{wid}.md](items/{wid}.md) |\n"
)

INDEX = (
    "# Work Archive\n\n"
    "| Work | Final status | Item |\n"
    "|---|---|---|\n"
)


class ArchiveWorkCliTest(unittest.TestCase):
    def make_stage(self, status: str = "completed", retro: str = "completed") -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        stage = root / ".stage"
        (stage / "present/work/items").mkdir(parents=True)
        (stage / "present/work/retrospectives").mkdir(parents=True)
        (stage / "past/work/archive/items").mkdir(parents=True)
        (stage / "past/work/archive/retrospectives").mkdir(parents=True)
        wid, ref = "W-00000001", "R-00000001"
        (stage / "present/work/items" / f"{wid}.md").write_text(
            ITEM.format(wid=wid, status=status, retro=retro, ref=ref), encoding="utf-8"
        )
        (stage / "present/work/retrospectives" / f"{ref}.md").write_text(
            RETRO.format(ref=ref, wid=wid), encoding="utf-8"
        )
        (stage / "present/work/review.md").write_text(REVIEW.format(wid=wid), encoding="utf-8")
        (stage / "past/work/archive/index.md").write_text(INDEX, encoding="utf-8")
        return tmp, root

    def init_git(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q", str(root)], check=True)

    def test_refuses_unstaged_dirty_path_inside_scope(self):
        tmp, root = self.make_stage()
        with tmp:
            self.init_git(root)
            source = root / "src/app.py"
            source.parent.mkdir(parents=True)
            source.write_text("print('clean')\n", encoding="utf-8")
            subprocess.run(["git", "add", "src/app.py"], cwd=root, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Stage Test",
                    "-c",
                    "user.email=stage@example.invalid",
                    "commit",
                    "-qm",
                    "test baseline",
                ],
                cwd=root,
                check=True,
            )
            source.write_text("print('dirty')\n", encoding="utf-8")

            proc = run_cli(root, "W-00000001")

            self.assertEqual(proc.returncode, 1, proc.stderr + proc.stdout)
            self.assertIn("src/app.py", proc.stdout)
            self.assertIn(
                "commit source changes first, then close, then archive", proc.stdout
            )
            self.assertTrue((root / ".stage/present/work/items/W-00000001.md").exists())

    def test_allows_dirty_path_outside_scope(self):
        tmp, root = self.make_stage()
        with tmp:
            self.init_git(root)
            outside = root / "docs/note.md"
            outside.parent.mkdir(parents=True)
            outside.write_text("dirty\n", encoding="utf-8")

            proc = run_cli(root, "W-00000001")

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_allows_stage_only_changes(self):
        tmp, root = self.make_stage()
        with tmp:
            self.init_git(root)

            proc = run_cli(root, "W-00000001")

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_allows_non_git_tree(self):
        tmp, root = self.make_stage()
        with tmp:
            proc = run_cli(root, "W-00000001")

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_archives_completed_item(self):
        tmp, root = self.make_stage()
        with tmp:
            proc = run_cli(root, "W-00000001")
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            stage = root / ".stage"

            archived = stage / "past/work/archive/items/W-00000001.md"
            self.assertTrue(archived.exists())
            self.assertIn("status: archived", archived.read_text(encoding="utf-8"))
            self.assertTrue((stage / "past/work/archive/retrospectives/R-00000001.md").exists())

            index = (stage / "past/work/archive/index.md").read_text(encoding="utf-8")
            self.assertIn("| W-00000001 | completed |", index)

            self.assertFalse((stage / "present/work/items/W-00000001.md").exists())
            self.assertFalse((stage / "present/work/retrospectives/R-00000001.md").exists())
            self.assertNotIn("W-00000001", (stage / "present/work/review.md").read_text(encoding="utf-8"))

    def test_all_completed_flag(self):
        tmp, root = self.make_stage()
        with tmp:
            proc = run_cli(root, "--all-completed")
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertTrue((root / ".stage/past/work/archive/items/W-00000001.md").exists())

    def test_archives_item_with_hand_written_review_artifact(self):
        tmp, root = self.make_stage()
        with tmp:
            review = root / ".stage/present/work/review.md"
            review.write_text(HAND_WRITTEN_REVIEW.format(wid="W-00000001"), encoding="utf-8")

            proc = run_cli(root, "W-00000001")

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertNotIn("items/W-00000001.md", review.read_text(encoding="utf-8"))

    def test_refuses_non_terminal_status(self):
        tmp, root = self.make_stage(status="active")
        with tmp:
            proc = run_cli(root, "W-00000001")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("ERROR", proc.stdout)
            # Nothing moved.
            self.assertTrue((root / ".stage/present/work/items/W-00000001.md").exists())
            self.assertFalse((root / ".stage/past/work/archive/items/W-00000001.md").exists())

    def test_refuses_retrospective_id_collision_with_different_work_item(self):
        tmp, root = self.make_stage()
        with tmp:
            stage = root / ".stage"
            archive_retro = stage / "past/work/archive/retrospectives/R-00000001.md"
            existing = RETRO.format(ref="R-00000001", wid="W-00000099")
            archive_retro.write_text(existing, encoding="utf-8")

            proc = run_cli(root, "W-00000001")

            self.assertEqual(proc.returncode, 1, proc.stderr + proc.stdout)
            self.assertIn("ERROR", proc.stdout)
            self.assertIn("R-00000001", proc.stdout)
            self.assertIn("W-00000001", proc.stdout)
            self.assertIn("W-00000099", proc.stdout)
            self.assertEqual(archive_retro.read_text(encoding="utf-8"), existing)
            self.assertTrue((stage / "present/work/items/W-00000001.md").exists())
            self.assertTrue(
                (stage / "present/work/retrospectives/R-00000001.md").exists()
            )
            self.assertFalse((stage / "past/work/archive/items/W-00000001.md").exists())
            self.assertNotIn(
                "W-00000001", (stage / "past/work/archive/index.md").read_text(encoding="utf-8")
            )

    def test_allows_existing_retrospective_for_same_work_item(self):
        tmp, root = self.make_stage()
        with tmp:
            stage = root / ".stage"
            archive_retro = stage / "past/work/archive/retrospectives/R-00000001.md"
            archive_retro.write_text(
                RETRO.format(ref="R-00000001", wid="W-00000001"), encoding="utf-8"
            )

            proc = run_cli(root, "W-00000001")

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertTrue((stage / "past/work/archive/items/W-00000001.md").exists())
            self.assertFalse((stage / "present/work/items/W-00000001.md").exists())

    def test_idempotent_rerun(self):
        tmp, root = self.make_stage()
        with tmp:
            run_cli(root, "W-00000001")
            proc = run_cli(root, "W-00000001")
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertIn("already archived", proc.stdout)


if __name__ == "__main__":
    unittest.main()
