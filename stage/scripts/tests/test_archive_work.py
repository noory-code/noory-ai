# The CLI must run wherever `python3` points on a host machine (3.9+), so the
# test module keeps the same annotation-laziness contract as the scripts.
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# archive_work.py is owned by (and lives inside) the stage-archive skill; the
# test stays in the central suite so one `unittest discover` covers everything.
CLI_PATH = Path(__file__).resolve().parents[2] / "skills" / "stage-archive" / "archive_work.py"
AUDIT_CLI_PATH = Path(__file__).resolve().parents[1] / "audit_stage.py"
TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "templates" / "v4" / "project-stage"


def run_cli(project_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI_PATH), "--project-root", str(project_root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
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

V5_ITEM = """---
id: {wid}
title: Sample
kind: development
venue: codex
status: completed
verification: passed
retrospective: completed
retrospective_ref: {ref}
promotion: not_applicable
review: not_required
scope: src/
decision_refs:
---

# {wid} Sample
"""

INDEX = (
    "# Work Archive\n\n"
    "| Work | Final status | Item |\n"
    "|---|---|---|\n"
)


sys.path.insert(0, str(CLI_PATH.parent))
import archive_work  # noqa: E402


class ArchiveIndexRowTest(unittest.TestCase):
    def test_a_new_row_ends_with_the_title_and_an_old_header_gains_the_column(self):
        text = archive_work.append_index_row(
            INDEX + "| W-00000001 | completed | [a](a) |\n",
            "W-00000002",
            "rejected",
            "items/W-00000002/_story.md",
            "Give the index | a title",
        )

        self.assertEqual(
            "# Work Archive\n\n"
            "| Work | Final status | Item | Title |\n"
            "|---|---|---|---|\n"
            "| W-00000001 | completed | [a](a) |\n"
            "| W-00000002 | rejected | [items/W-00000002/_story.md](items/W-00000002/_story.md) "
            "| Give the index \\| a title |\n",
            text,
        )
        # A header that already has the column is not widened again.
        again = archive_work.append_index_row(text, "W-00000003", "completed", "c", "")
        self.assertIn("| Work | Final status | Item | Title |\n|---|---|---|---|\n", again)
        self.assertTrue(again.endswith("| W-00000003 | completed | [c](c) | — |\n"))

    def test_a_korean_header_gains_a_korean_title_cell(self):
        text = archive_work.append_index_row(
            "| 작업 | Final status | 항목 |\n|---|---|---|\n", "W-00000001", "completed", "a", "제목"
        )

        self.assertTrue(text.startswith("| 작업 | Final status | 항목 | 제목 |\n|---|---|---|---|\n"))


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

    def test_archiving_removes_only_the_archived_items_pending_intents(self):
        tmp, root = self.make_stage()
        with tmp:
            intents = root / ".stage/.runtime/intents"
            intents.mkdir(parents=True)
            archived_intents = [
                intents / "W-00000001--index.md-1111111111.json",
                intents / "W-00000001--principles.md-2222222222.json",
            ]
            other_intent = intents / "W-00000002--index.md-3333333333.json"
            for path in [*archived_intents, other_intent]:
                path.write_text("{}\n", encoding="utf-8")

            proc = run_cli(root, "W-00000001")

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertFalse(any(path.exists() for path in archived_intents))
            self.assertTrue(other_intent.exists())

    def test_v3_parent_field_is_inert_history(self):
        tmp, root = self.make_stage()
        with tmp:
            planned = root / ".stage/future/backlog/items/W-00000002.md"
            planned.parent.mkdir(parents=True)
            planned.write_text(
                "---\nid: W-00000002\nparent: W-00000001\nstatus: captured\n---\n",
                encoding="utf-8",
            )

            proc = run_cli(root, "W-00000001")

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertTrue(
                (root / ".stage/past/work/archive/items/W-00000001.md").exists()
            )

    def test_all_completed_flag(self):
        tmp, root = self.make_stage()
        with tmp:
            proc = run_cli(root, "--all-completed")
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertTrue((root / ".stage/past/work/archive/items/W-00000001.md").exists())

    def test_refuses_non_terminal_status(self):
        tmp, root = self.make_stage(status="active")
        with tmp:
            proc = run_cli(root, "W-00000001")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("ERROR", proc.stdout)
            # Nothing moved.
            self.assertTrue((root / ".stage/present/work/items/W-00000001.md").exists())
            self.assertFalse((root / ".stage/past/work/archive/items/W-00000001.md").exists())

    def test_refuses_current_rejected_item_without_retrospective(self):
        tmp, root = self.make_stage(status="rejected", retro="pending")
        with tmp:
            proc = run_cli(root, "W-00000001")

            self.assertEqual(proc.returncode, 1, proc.stderr + proc.stdout)
            self.assertIn("retrospective is not completed", proc.stdout)
            self.assertTrue((root / ".stage/present/work/items/W-00000001.md").exists())
            self.assertFalse((root / ".stage/past/work/archive/items/W-00000001.md").exists())

    def test_v5_refuses_current_rejected_story_without_retrospective(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage = root / ".stage"
            shutil.copytree(TEMPLATE_ROOT, stage)
            item_id = "W-00000001"
            current_unit = stage / f"work/current/{item_id}"
            current_unit.mkdir(parents=True)
            current_item = current_unit / "_story.md"
            current_item.write_text(
                (
                    "---\n"
                    f"id: {item_id}\n"
                    "title: Reject current work\n"
                    "kind: fix\n"
                    "venue: codex\n"
                    "status: rejected\n"
                    "verification: pending\n"
                    "retrospective: pending\n"
                    "retrospective_ref:\n"
                    "promotion: rejected\n"
                    "review: not_required\n"
                    "scope: src/\n"
                    "---\n\n"
                    f"# {item_id} Reject current work\n"
                ),
                encoding="utf-8",
            )

            proc = run_cli(root, item_id)

            self.assertEqual(1, proc.returncode, proc.stdout + proc.stderr)
            self.assertIn("retrospective is not completed", proc.stdout)
            self.assertTrue(current_item.exists())
            self.assertFalse(
                (stage / f"official/work/archive/items/{item_id}").exists()
            )

    def test_v5_archives_planned_rejected_story_without_retrospective(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage = root / ".stage"
            shutil.copytree(TEMPLATE_ROOT, stage)
            item_id = "W-00000001"
            planned_unit = stage / f"work/planned/{item_id}"
            planned_unit.mkdir(parents=True)
            planned_item = planned_unit / "_story.md"
            planned_item.write_text(
                (
                    "---\n"
                    f"id: {item_id}\n"
                    "title: Reject planned work\n"
                    "kind: fix\n"
                    "venue: codex\n"
                    "status: rejected\n"
                    "scope: src/\n"
                    "---\n\n"
                    f"# {item_id} Reject planned work\n\n"
                    "Rejected because the premise no longer holds.\n"
                ),
                encoding="utf-8",
            )

            proc = run_cli(root, item_id)
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            audit_proc = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_CLI_PATH),
                    "--project-root",
                    str(root),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            archived_item = (
                stage / f"official/work/archive/items/{item_id}/_story.md"
            )
            archived_text = archived_item.read_text(encoding="utf-8")
            archive_index = (
                stage / "official/work/archive/index.md"
            ).read_text(encoding="utf-8")
            planned_unit_exists = planned_unit.exists()

        self.assertFalse(planned_unit_exists)
        self.assertIn("status: archived", archived_text)
        self.assertIn("terminal_disposition: rejected", archived_text)
        self.assertIn("Rejected because the premise no longer holds.", archived_text)
        self.assertIn(f"| {item_id} | rejected |", archive_index)
        self.assertEqual(0, audit_proc.returncode, audit_proc.stdout + audit_proc.stderr)
        self.assertIn("Summary: errors=0", audit_proc.stdout)

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

    def test_v4_all_completed_archives_independent_story_with_action_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage = root / ".stage"
            shutil.copytree(TEMPLATE_ROOT, stage)
            story_id = "W-00000001"
            action_id = "W-00000002"
            story_retro_id = "R-00000001"
            action_retro_id = "R-00000002"
            current = stage / f"work/current/{story_id}"
            current.mkdir(parents=True)
            (current / "_story.md").write_text(
                V5_ITEM.format(wid=story_id, ref=story_retro_id),
                encoding="utf-8",
            )
            (current / f"{action_id}.md").write_text(
                V5_ITEM.format(wid=action_id, ref=action_retro_id), encoding="utf-8"
            )
            for item_id, retro_id in (
                (story_id, story_retro_id),
                (action_id, action_retro_id),
            ):
                (stage / "work/retrospectives" / f"{retro_id}.md").write_text(
                    RETRO.format(ref=retro_id, wid=item_id), encoding="utf-8"
                )
            proc = run_cli(root, "--all-completed")

            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertTrue(
                (stage / f"official/work/archive/items/{story_id}/_story.md").is_file()
            )
            self.assertTrue(
                (
                    stage
                    / f"official/work/archive/items/{story_id}/{action_id}.md"
                ).is_file()
            )
            self.assertEqual(1, len(proc.stdout.strip().splitlines()), proc.stdout)
            self.assertIn(story_id, proc.stdout)
            self.assertNotIn(action_id, proc.stdout)

    def test_all_completed_reads_card_status_not_a_list_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage = root / ".stage"
            shutil.copytree(TEMPLATE_ROOT, stage)
            for item_id, retro_id, status in (
                ("W-00000001", "R-00000001", "completed"),
                ("W-00000002", "R-00000002", "active"),
            ):
                unit = stage / f"work/current/{item_id}"
                unit.mkdir(parents=True)
                (unit / "_story.md").write_text(
                    V5_ITEM.format(wid=item_id, ref=retro_id).replace(
                        "status: completed", f"status: {status}"
                    ),
                    encoding="utf-8",
                )
                (stage / "work/retrospectives" / f"{retro_id}.md").write_text(
                    RETRO.format(ref=retro_id, wid=item_id), encoding="utf-8"
                )
            listed = (stage / "work/review.md").exists()

            proc = run_cli(root, "--all-completed")
            archived = (stage / "official/work/archive/items/W-00000001/_story.md").is_file()
            still_current = (stage / "work/current/W-00000002/_story.md").is_file()

        self.assertFalse(listed)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertTrue(archived)
        self.assertTrue(still_current)
        self.assertNotIn("W-00000002", proc.stdout)

    def test_v4_all_completed_archives_one_top_level_hierarchy_as_one_move_unit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage = root / ".stage"
            shutil.copytree(TEMPLATE_ROOT, stage)
            current = stage / "work/current/W-00000001"
            story = current / "W-00000002"
            story.mkdir(parents=True)
            records = (
                (current / "_epic.md", "W-00000001", "R-00000001"),
                (story / "_story.md", "W-00000002", "R-00000002"),
                (story / "W-00000003.md", "W-00000003", "R-00000003"),
            )
            for path, item_id, retro_id in records:
                path.write_text(
                    V5_ITEM.format(
                        wid=item_id,
                        ref=retro_id,
                    ),
                    encoding="utf-8",
                )
                (stage / "work/retrospectives" / f"{retro_id}.md").write_text(
                    RETRO.format(ref=retro_id, wid=item_id),
                    encoding="utf-8",
                )
            proc = run_cli(root, "--all-completed")
            audit_proc = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_CLI_PATH),
                    "--project-root",
                    str(root),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            archive_unit = stage / "official/work/archive/items/W-00000001"
            archived_texts = [
                (archive_unit / "_epic.md").read_text(encoding="utf-8"),
                (
                    archive_unit / "W-00000002/_story.md"
                ).read_text(encoding="utf-8"),
                (
                    archive_unit / "W-00000002/W-00000003.md"
                ).read_text(encoding="utf-8"),
            ]
            archive_index = (
                stage / "official/work/archive/index.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertFalse(current.exists())
        self.assertTrue(all("status: archived" in text for text in archived_texts))
        self.assertTrue(
            all("terminal_disposition: accepted" in text for text in archived_texts)
        )
        self.assertEqual(1, archive_index.count("| W-00000001 | completed |"))
        self.assertNotIn("| W-00000002 |", archive_index)
        self.assertNotIn("| W-00000003 |", archive_index)
        self.assertEqual(1, len(proc.stdout.strip().splitlines()), proc.stdout)
        self.assertNotIn("W-00000002", proc.stdout)
        self.assertNotIn("W-00000003", proc.stdout)
        self.assertEqual(0, audit_proc.returncode, audit_proc.stdout + audit_proc.stderr)
        self.assertIn("Summary: errors=0", audit_proc.stdout)

    def make_v5_unit(self, root: Path, nested: bool = False) -> tuple[Path, Path]:
        stage = root / ".stage"
        shutil.copytree(TEMPLATE_ROOT, stage)
        unit = stage / "work/current/W-00000001"
        if nested:
            records = (
                (unit / "_epic.md", "W-00000001", "R-00000001"),
                (unit / "W-00000002/_story.md", "W-00000002", "R-00000002"),
                (unit / "W-00000002/W-00000003.md", "W-00000003", "R-00000003"),
            )
        else:
            records = ((unit / "_story.md", "W-00000001", "R-00000001"),)
        for path, item_id, retro_id in records:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(V5_ITEM.format(wid=item_id, ref=retro_id), encoding="utf-8")
            (stage / "work/retrospectives" / f"{retro_id}.md").write_text(
                RETRO.format(ref=retro_id, wid=item_id), encoding="utf-8"
            )
        return stage, unit

    def write_attachments(self, unit: Path, relatives: list[str]) -> dict[str, bytes]:
        contents = {}
        for index, relative in enumerate(relatives):
            data = b"\x89PNG\r\n\x1a\n\x00\xff" + bytes([index]) + b"\r\nraw\n"
            path = unit / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            contents[relative] = data
        return contents

    def test_v5_archive_carries_non_markdown_files_beside_the_story_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage, unit = self.make_v5_unit(root)
            contents = self.write_attachments(unit, ["evidence.json", "screen.png"])

            proc = run_cli(root, "W-00000001")

            archive_unit = stage / "official/work/archive/items/W-00000001"
            archived = {
                relative: (archive_unit / relative).read_bytes()
                for relative in contents
            }
            story_text = (archive_unit / "_story.md").read_text(encoding="utf-8")
            unit_exists = unit.exists()

        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertEqual(contents, archived)
        self.assertIn("status: archived", story_text)
        self.assertIn("2 attachment(s)", proc.stdout)
        self.assertFalse(unit_exists)

    def test_v5_archive_carries_files_beside_nested_records_at_any_depth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage, unit = self.make_v5_unit(root, nested=True)
            (unit / "W-00000002/empty").mkdir()
            contents = self.write_attachments(
                unit,
                [
                    "W-00000002/run.log",
                    "W-00000002/evidence/screens/before.png",
                    "data/deep/er/result.csv",
                ],
            )

            proc = run_cli(root, "W-00000001")

            archive_unit = stage / "official/work/archive/items/W-00000001"
            archived = {
                relative: (archive_unit / relative).read_bytes()
                for relative in contents
            }
            action_text = (archive_unit / "W-00000002/W-00000003.md").read_text(
                encoding="utf-8"
            )
            unit_exists = unit.exists()

        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertEqual(contents, archived)
        self.assertIn("status: archived", action_text)
        self.assertFalse(unit_exists)

    def test_v5_refuses_existing_archive_unit_before_moving_any_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage, unit = self.make_v5_unit(root)
            contents = self.write_attachments(unit, ["evidence.json"])
            archive_unit = stage / "official/work/archive/items/W-00000001"
            archive_unit.mkdir(parents=True)
            (archive_unit / "evidence.json").write_bytes(b"older\n")

            proc = run_cli(root, "W-00000001")

            source_evidence = (unit / "evidence.json").read_bytes()
            archived_evidence = (archive_unit / "evidence.json").read_bytes()
            archived_names = sorted(path.name for path in archive_unit.rglob("*"))
            story_exists = (unit / "_story.md").is_file()
            retro_exists = (stage / "work/retrospectives/R-00000001.md").is_file()

        self.assertEqual(1, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("archive move unit already exists", proc.stdout)
        self.assertEqual(contents["evidence.json"], source_evidence)
        self.assertEqual(b"older\n", archived_evidence)
        self.assertEqual(["evidence.json"], archived_names)
        self.assertTrue(story_exists)
        self.assertTrue(retro_exists)

    def test_single_file_card_archive_leaves_sibling_files_alone(self):
        tmp, root = self.make_stage()
        with tmp:
            items = root / ".stage/present/work/items"
            sibling = items / "evidence.json"
            sibling.write_bytes(b"{}\n")

            proc = run_cli(root, "W-00000001")

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertNotIn("attachment", proc.stdout)
            self.assertEqual(b"{}\n", sibling.read_bytes())
            self.assertFalse(
                (root / ".stage/past/work/archive/items/evidence.json").exists()
            )
            self.assertTrue(
                (root / ".stage/past/work/archive/items/W-00000001.md").is_file()
            )

    def test_v5_archives_the_work_items_consumed_venue_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage = root / ".stage"
            shutil.copytree(TEMPLATE_ROOT, stage)
            item_id = "W-00000001"
            retro_id = "R-00000001"
            decision_id = "DE-00000001"
            current = stage / f"work/current/{item_id}"
            current.mkdir(parents=True)
            item = current / "_story.md"
            item.write_text(
                V5_ITEM.format(wid=item_id, ref=retro_id).replace(
                    "decision_refs:\n", f"decision_refs: {decision_id}\n"
                ),
                encoding="utf-8",
            )
            (stage / f"work/retrospectives/{retro_id}.md").write_text(
                RETRO.format(ref=retro_id, wid=item_id), encoding="utf-8"
            )
            decision = stage / f"decisions/pending/{decision_id}.md"
            decision.write_text(
                (
                    "---\n"
                    f"id: {decision_id}\n"
                    f"work_item: {item_id}\n"
                    "status: decided\n"
                    "authorizes: venue_exception\n"
                    "---\n\n"
                    f"# {decision_id} One-time venue exception\n\n"
                    "## Question\n\nMay this item use another venue?\n\n"
                    "## Principles applied\n\n- **SSOT** — one owner.\n\n"
                    "## Chosen direction\n\nYes, once.\n"
                ),
                encoding="utf-8",
            )

            proc = run_cli(root, item_id)
            audit_proc = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_CLI_PATH),
                    "--project-root",
                    str(root),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            archived_decision = stage / f"official/decisions/archive/{decision_id}.md"
            archived_decision_exists = archived_decision.is_file()
            pending_decision_exists = decision.exists()
            archive_index = (
                stage / "official/decisions/archive/index.md"
            ).read_text(encoding="utf-8")
            pending_index = (stage / "decisions/index.md").read_text(encoding="utf-8")

        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertTrue(archived_decision_exists)
        self.assertFalse(pending_decision_exists)
        self.assertIn(f"| {decision_id} | consumed |", archive_index)
        self.assertNotIn(decision_id, pending_index)
        self.assertEqual(
            0, audit_proc.returncode, audit_proc.stdout + audit_proc.stderr
        )

    def test_v5_archive_points_the_pending_index_at_the_archived_owner(self):
        for with_exception in (False, True):
            with self.subTest(with_exception=with_exception), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                stage = root / ".stage"
                shutil.copytree(TEMPLATE_ROOT, stage)
                refs = "DE-00000001, DE-00000002" if with_exception else "DE-00000001"
                current = stage / "work/current/W-00000001"
                current.mkdir(parents=True)
                (current / "_story.md").write_text(
                    V5_ITEM.format(wid="W-00000001", ref="R-00000001")
                    .replace("decision_refs:\n", f"decision_refs: {refs}\n")
                    .replace("promotion: not_applicable", "promotion: deferred"),
                    encoding="utf-8",
                )
                (stage / "work/retrospectives/R-00000001.md").write_text(
                    RETRO.format(ref="R-00000001", wid="W-00000001"), encoding="utf-8"
                )
                decisions = [("DE-00000001", "")]
                if with_exception:
                    decisions.append(("DE-00000002", "authorizes: venue_exception\n"))
                for decision_id, authorizes in decisions:
                    (stage / f"decisions/pending/{decision_id}.md").write_text(
                        "---\n"
                        f"id: {decision_id}\nwork_item: W-00000001\nstatus: decided\n{authorizes}"
                        "---\n\n"
                        f"# {decision_id} Decision\n\n## Question\n\nQ?\n\n"
                        "## Principles applied\n\n- **SSOT** — one owner.\n\n"
                        "## Chosen direction\n\nYes.\n",
                        encoding="utf-8",
                    )
                subprocess.run(
                    [sys.executable, str(AUDIT_CLI_PATH.parent / "refresh_decision_index.py"),
                     "--project-root", str(root)],
                    check=True,
                    capture_output=True,
                )

                proc = run_cli(root, "W-00000001")
                pending_index = (stage / "decisions/index.md").read_text(encoding="utf-8")
                audit = subprocess.run(
                    [sys.executable, str(AUDIT_CLI_PATH), "--project-root", str(root)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )

                self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
                row = next(line for line in pending_index.splitlines() if "DE-00000001" in line)
                self.assertIn("official/work/archive/items/W-00000001/_story.md", row)
                self.assertIn("| archived |", row)
                self.assertNotIn("DE-00000002", pending_index)
                self.assertNotIn("DECISION004", audit.stdout)
                self.assertIn("Summary: errors=0", audit.stdout)

    def test_v5_can_archive_consumed_decisions_for_already_archived_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage = root / ".stage"
            shutil.copytree(TEMPLATE_ROOT, stage)
            item_id = "W-00000001"
            decision_id = "DE-00000001"
            archived = stage / f"official/work/archive/items/{item_id}"
            archived.mkdir(parents=True)
            (archived / "_story.md").write_text(
                (
                    "---\n"
                    f"id: {item_id}\n"
                    "title: Archived\n"
                    "kind: development\n"
                    "venue: codex\n"
                    "status: archived\n"
                    "terminal_disposition: accepted\n"
                    "verification: passed\n"
                    "retrospective: completed\n"
                    "retrospective_ref: R-00000001\n"
                    "promotion: not_applicable\n"
                    "review: not_required\n"
                    "scope: src/\n"
                    f"decision_refs: {decision_id}\n"
                    "---\n"
                ),
                encoding="utf-8",
            )
            decision = stage / f"decisions/pending/{decision_id}.md"
            decision.write_text(
                (
                    "---\n"
                    f"id: {decision_id}\n"
                    f"work_item: {item_id}\n"
                    "status: decided\n"
                    "authorizes: venue_exception\n"
                    "---\n"
                ),
                encoding="utf-8",
            )

            proc = run_cli(root, "--archive-consumed-decisions")

            archived_decision = stage / f"official/decisions/archive/{decision_id}.md"
            archived_decision_exists = archived_decision.is_file()
            pending_decision_exists = decision.exists()

        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertTrue(archived_decision_exists)
        self.assertFalse(pending_decision_exists)
        self.assertIn("archived 1 consumed decision", proc.stdout)


if __name__ == "__main__":
    unittest.main()
