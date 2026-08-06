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
            planned_index = stage / "work/planned/index.md"
            planned_index.write_text(
                planned_index.read_text(encoding="utf-8")
                + f"| {item_id} | rejected | [Reject planned work]"
                f"({item_id}/_story.md) |\n",
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
            )

            archived_item = (
                stage / f"official/work/archive/items/{item_id}/_story.md"
            )
            archived_text = archived_item.read_text(encoding="utf-8")
            archive_index = (
                stage / "official/work/archive/index.md"
            ).read_text(encoding="utf-8")
            planned_index_text = planned_index.read_text(encoding="utf-8")
            planned_unit_exists = planned_unit.exists()

        self.assertFalse(planned_unit_exists)
        self.assertIn("status: archived", archived_text)
        self.assertIn("terminal_disposition: rejected", archived_text)
        self.assertIn("Rejected because the premise no longer holds.", archived_text)
        self.assertIn(f"| {item_id} | rejected |", archive_index)
        self.assertNotIn(item_id, planned_index_text)
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
            review_path = stage / "work/review.md"
            review_path.write_text(
                review_path.read_text(encoding="utf-8")
                + f"| {action_id} | passed | completed | not_applicable | "
                f"[current/{story_id}/{action_id}.md]"
                f"(current/{story_id}/{action_id}.md) |\n"
                + f"| {story_id} | passed | completed | not_applicable | "
                f"[current/{story_id}/_story.md](current/{story_id}/_story.md) |\n",
                encoding="utf-8",
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
            review_path = stage / "work/review.md"
            review_path.write_text(
                review_path.read_text(encoding="utf-8")
                + "".join(
                    f"| {item_id} | passed | completed | not_applicable | "
                    f"[{path.relative_to(stage / 'work').as_posix()}]"
                    f"({path.relative_to(stage / 'work').as_posix()}) |\n"
                    for path, item_id, _retro_id in records
                ),
                encoding="utf-8",
            )
            active_path = stage / "work/active.md"
            active_path.write_text(
                active_path.read_text(encoding="utf-8")
                + "".join(
                    f"| {item_id} | development | codex | x | completed | codex | "
                    f"[{path.relative_to(stage / 'work').as_posix()}]"
                    f"({path.relative_to(stage / 'work').as_posix()}) |\n"
                    for path, item_id, _retro_id in records
                ),
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
            active_text = (stage / "work/active.md").read_text(encoding="utf-8")
            review_text = (stage / "work/review.md").read_text(encoding="utf-8")
            archive_index = (
                stage / "official/work/archive/index.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertFalse(current.exists())
        self.assertTrue(all("status: archived" in text for text in archived_texts))
        self.assertTrue(
            all("terminal_disposition: accepted" in text for text in archived_texts)
        )
        self.assertNotIn("W-00000001", active_text)
        self.assertNotIn("W-00000002", active_text)
        self.assertNotIn("W-00000003", review_text)
        self.assertEqual(1, archive_index.count("| W-00000001 | completed |"))
        self.assertNotIn("| W-00000002 |", archive_index)
        self.assertNotIn("| W-00000003 |", archive_index)
        self.assertEqual(1, len(proc.stdout.strip().splitlines()), proc.stdout)
        self.assertNotIn("W-00000002", proc.stdout)
        self.assertNotIn("W-00000003", proc.stdout)
        self.assertEqual(0, audit_proc.returncode, audit_proc.stdout + audit_proc.stderr)
        self.assertIn("Summary: errors=0", audit_proc.stdout)

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
