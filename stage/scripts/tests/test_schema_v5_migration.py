import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


STAGE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = STAGE_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import stage_schema_v5_migration as migration  # noqa: E402
import audit_stage  # noqa: E402
import migrate_stage  # noqa: E402


def write_card(
    path: Path,
    item_id: str,
    *,
    status: str,
    parent: str = "",
    retrospective_ref: str = "",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"id: {item_id}\n"
        f"title: {item_id} title\n"
        "kind: development\n"
        "venue: codex\n"
        f"parent: {parent}\n"
        f"status: {status}\n"
        + ("terminal_disposition: accepted\n" if status == "archived" else "")
        + "verification: passed\n"
        "retrospective: completed\n"
        f"retrospective_ref: {retrospective_ref}\n"
        "promotion: not_applicable\n"
        "review: not_required\n"
        "scope: stage/\n"
        "promotes:\n"
        "decision_refs:\n"
        "---\n\n"
        f"# {item_id} title\n\n"
        "## Purpose\n\nFixture.\n",
        encoding="utf-8",
    )


class SchemaV5MigrationTest(unittest.TestCase):
    def make_project(self) -> tuple[tempfile.TemporaryDirectory[str], Path, Path]:
        temporary = tempfile.TemporaryDirectory()
        project_root = Path(temporary.name)
        stage_root = project_root / ".stage"
        for relative in (
            "work/current",
            "work/planned",
            "work/retrospectives",
            "official/work/archive/items",
            "official/work/archive/retrospectives",
        ):
            (stage_root / relative).mkdir(parents=True)
        (stage_root / "settings.json").write_text(
            json.dumps({"schema_version": 4, "language": "en"}) + "\n",
            encoding="utf-8",
        )
        (stage_root / "work/active.md").write_text(
            "# Active\n\n"
            "| Work | Item |\n"
            "|---|---|\n"
            "| W-00000003 | [item](current/W-00000003.md) |\n",
            encoding="utf-8",
        )
        (stage_root / "work/review.md").write_text(
            "# Review\n\n| Work | Item |\n|---|---|\n",
            encoding="utf-8",
        )
        (stage_root / "work/planned/index.md").write_text(
            "# Planned\n\n| Work | Item |\n|---|---|\n",
            encoding="utf-8",
        )
        (stage_root / "official/work/archive/index.md").write_text(
            "# Archive\n\n"
            "| Work | Status | Item |\n"
            "|---|---|---|\n"
            "| W-00000001 | completed | [item](items/W-00000001.md) |\n"
            "| W-00000002 | completed | [item](items/W-00000002.md) |\n",
            encoding="utf-8",
        )
        return temporary, project_root, stage_root

    def test_flat_cards_become_one_shape_and_cross_lifecycle_children_rejoin_parent(self):
        temporary, project_root, stage_root = self.make_project()
        with temporary:
            write_card(
                stage_root / "official/work/archive/items/W-00000001.md",
                "W-00000001",
                status="archived",
                retrospective_ref="R-00000001",
            )
            write_card(
                stage_root / "official/work/archive/items/W-00000002.md",
                "W-00000002",
                status="archived",
                parent="W-00000003",
                retrospective_ref="R-00000002",
            )
            write_card(
                stage_root / "work/current/W-00000003.md",
                "W-00000003",
                status="active",
                retrospective_ref="R-00000003",
            )
            archived_retro = (
                stage_root
                / "official/work/archive/retrospectives/R-00000002.md"
            )
            archived_retro.write_text(
                "---\nid: R-00000002\nwork_item: W-00000002\n---\n",
                encoding="utf-8",
            )

            result = migration.migrate(project_root, dry_run=False)

            self.assertEqual(0, result)
            independent = (
                stage_root
                / "official/work/archive/items/W-00000001/_story.md"
            )
            epic = stage_root / "work/current/W-00000003/_epic.md"
            child = stage_root / "work/current/W-00000003/W-00000002/_story.md"
            self.assertTrue(independent.is_file())
            self.assertTrue(epic.is_file())
            self.assertTrue(child.is_file())
            self.assertNotIn("\nparent:", independent.read_text(encoding="utf-8"))
            self.assertNotIn("\nparent:", epic.read_text(encoding="utf-8"))
            child_text = child.read_text(encoding="utf-8")
            self.assertNotIn("\nparent:", child_text)
            self.assertIn("\nstatus: completed\n", child_text)
            self.assertTrue(
                (stage_root / "work/retrospectives/R-00000002.md").is_file()
            )
            self.assertFalse(archived_retro.exists())
            self.assertIn(
                "current/W-00000003/_epic.md",
                (stage_root / "work/active.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "current/W-00000003/W-00000002/_story.md",
                (stage_root / "work/review.md").read_text(encoding="utf-8"),
            )
            archive_index = (
                stage_root / "official/work/archive/index.md"
            ).read_text(encoding="utf-8")
            self.assertIn("items/W-00000001/_story.md", archive_index)
            self.assertNotIn("W-00000002", archive_index)
            settings = json.loads(
                (stage_root / "settings.json").read_text(encoding="utf-8")
            )
            self.assertEqual(5, settings["schema_version"])
            self.assertFalse(
                (stage_root / migration.JOURNAL_RELATIVE).exists()
            )

    def test_preexisting_audit_warning_is_reported_but_does_not_block_migration(self):
        temporary, project_root, stage_root = self.make_project()
        with temporary:
            write_card(
                stage_root / "work/current/W-00000003.md",
                "W-00000003",
                status="active",
            )
            warning = audit_stage.Finding(
                "warning",
                "KIND001",
                "Work kind `legacy` has no `passed` criterion.",
                ".stage/work/current/W-00000003.md",
            )
            stale = stage_root / migrate_stage.v4_migration.JOURNAL_RELATIVE
            stale.parent.mkdir(parents=True, exist_ok=True)
            stale.write_text(
                json.dumps(
                    {
                        "migration": "schema-v3-to-v4",
                        "status": "complete",
                        "original_head": "historical-transaction",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            output = io.StringIO()

            with patch.object(
                migrate_stage,
                "strict_audit_findings",
                side_effect=([warning], [warning]),
            ), redirect_stdout(output):
                result = migrate_stage.migrate(project_root, dry_run=False)

            self.assertEqual(0, result, output.getvalue())
            self.assertIn("Pre-existing audit findings carried forward", output.getvalue())
            self.assertIn("WARNING KIND001", output.getvalue())
            self.assertFalse(stale.exists())

    def test_abort_restores_the_exact_pre_migration_tree_after_interruption(self):
        temporary, project_root, stage_root = self.make_project()
        with temporary:
            card = stage_root / "work/current/W-00000001.md"
            write_card(
                card,
                "W-00000001",
                status="active",
                retrospective_ref="R-00000001",
            )
            before = migration.snapshot_tree(stage_root)
            checked = migration.preflight(project_root, stage_root)
            journal = migration.begin(stage_root, checked)
            migration.relocate_work_records(stage_root, checked, journal)

            self.assertFalse(card.exists())
            self.assertTrue(
                (stage_root / migration.MAINTENANCE_MARKER_RELATIVE).is_file()
            )
            self.assertEqual(0, migration.abort(project_root, stage_root))
            self.assertEqual(before, migration.snapshot_tree(stage_root))
            self.assertFalse(
                (stage_root / migration.MAINTENANCE_MARKER_RELATIVE).exists()
            )

    def test_pending_promotion_machinery_blocks_before_mutation(self):
        temporary, project_root, stage_root = self.make_project()
        with temporary:
            card = stage_root / "work/current/W-00000001.md"
            write_card(card, "W-00000001", status="active")
            intent = stage_root / ".runtime/intents/W-00000001.json"
            intent.parent.mkdir(parents=True)
            intent.write_text("{}\n", encoding="utf-8")
            before = migration.snapshot_tree(stage_root)

            result = migration.migrate(project_root, dry_run=False)

            self.assertEqual(1, result)
            self.assertEqual(before, migration.snapshot_tree(stage_root))
            self.assertFalse(
                (stage_root / migration.MAINTENANCE_MARKER_RELATIVE).exists()
            )

    def test_abort_skips_an_unrelated_completed_v4_journal(self):
        temporary, project_root, stage_root = self.make_project()
        with temporary:
            card = stage_root / "work/current/W-00000001.md"
            write_card(card, "W-00000001", status="active")
            before = migration.snapshot_tree(stage_root)
            checked = migration.preflight(project_root, stage_root)
            journal = migration.begin(stage_root, checked)
            journal["original_head"] = "current-transaction"
            migration.save_journal(stage_root, journal)
            stale = stage_root / migrate_stage.v4_migration.JOURNAL_RELATIVE
            stale.write_text(
                json.dumps(
                    {
                        "status": "complete",
                        "original_head": "historical-transaction",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = migrate_stage.abort(project_root)

            self.assertEqual(0, result)
            self.assertEqual(before, migration.snapshot_tree(stage_root))
            self.assertTrue(stale.is_file())

    def test_abort_ignores_a_stale_v4_journal_without_a_v5_transaction(self):
        temporary, project_root, stage_root = self.make_project()
        with temporary:
            card = stage_root / "work/current/W-00000001.md"
            write_card(card, "W-00000001", status="active")
            before = migration.snapshot_tree(stage_root)
            stale = stage_root / migrate_stage.v4_migration.JOURNAL_RELATIVE
            stale.parent.mkdir(parents=True, exist_ok=True)
            stale.write_text(
                json.dumps(
                    {
                        "migration": "schema-v3-to-v4",
                        "status": "complete",
                        "original_head": "historical-transaction",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            output = io.StringIO()

            with patch.object(
                migrate_stage.v4_migration,
                "abort",
                side_effect=AssertionError("stale journal must not own this abort"),
            ), redirect_stdout(output):
                result = migrate_stage.abort(project_root)

            self.assertEqual(0, result, output.getvalue())
            self.assertEqual(before, migration.snapshot_tree(stage_root))
            self.assertTrue(stale.is_file())
            self.assertIn(
                "Ignoring unrelated schema-v4 migration journal",
                output.getvalue(),
            )


if __name__ == "__main__":
    unittest.main()
