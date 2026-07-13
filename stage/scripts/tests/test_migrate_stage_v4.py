from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


STAGE_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_ROOT = STAGE_ROOT / "scripts"
V3_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "project-stage"
SKILL_CLI = STAGE_ROOT / "skills" / "stage-migrate" / "migrate_stage.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


audit_stage = load_module("audit_stage_migration_v4", SCRIPT_ROOT / "audit_stage.py")
migrate_stage = load_module("migrate_stage_v4", SCRIPT_ROOT / "migrate_stage.py")


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=True
    )


class V3ToV4MigrationTest(unittest.TestCase):
    def make_v3_project(self, root: Path) -> Path:
        shutil.copytree(V3_TEMPLATE_ROOT, root / ".stage")
        stage_root = root / ".stage"
        settings_path = stage_root / "settings.json"
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        settings["schema_version"] = 3
        settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")

        item = stage_root / "present/work/items/W-00000001.md"
        item.write_text(
            "---\n"
            "id: W-00000001\n"
            "title: Migration fixture\n"
            "kind: development\n"
            "venue: codex\n"
            "parent:\n"
            "source:\n"
            "status: active\n"
            "verification: pending\n"
            "retrospective: pending\n"
            "retrospective_ref:\n"
            "promotion: pending\n"
            "review: not_required\n"
            "scope: src\n"
            "promotes:\n"
            "decision_refs:\n"
            "---\n\n"
            "# W-00000001 Migration fixture\n\n"
            "## Purpose\n\nExercise migration.\n\n"
            "## Scope\n\n\n## Success criteria\n\n\n## Related truth\n\n"
            "## Progress\n\n\n## Verification\n\n\n## Retrospective\n\n"
            "## Promotion decision\n",
            encoding="utf-8",
        )
        active = stage_root / "present/work/active.md"
        active.write_text(
            active.read_text(encoding="utf-8")
            + "| W-00000001 | development | codex | Migration | active | codex | "
            "[item](items/W-00000001.md) |\n",
            encoding="utf-8",
        )
        path_fields = stage_root / "future/proposals/path-fields.md"
        path_fields.write_text(
            "---\n"
            'promotes: ".stage/past/canon/principles.md"\n'
            "decision_refs: .stage/present/work/decisions/DE-00000001.md\n"
            "retrospective_ref: .stage/present/work/retrospectives/R-00000001.md\n"
            "scope: src; .stage/future/proposals/\n"
            "---\n\n"
            "# Path fields\n\n"
            "See [principles](../../past/canon/principles.md) and "
            "`present/state/questions.md`.\n",
            encoding="utf-8",
        )
        (stage_root / "future/proposals/verbatim.txt").write_bytes(
            b"verbatim relocation payload\x00\xff"
        )

        git(root, "init", "-q")
        git(root, "config", "user.email", "stage-test@example.com")
        git(root, "config", "user.name", "Stage Test")
        git(root, "add", "-A")
        git(root, "commit", "-qm", "v3 fixture")
        return stage_root

    def run_migrate(
        self, root: Path, *, dry_run: bool = False, abort: bool = False
    ) -> tuple[int, str]:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            if abort:
                code = migrate_stage.abort(root)
            else:
                code = migrate_stage.migrate(root, dry_run)
        return code, buffer.getvalue()

    def assert_refusal(self, root: Path, expected: str) -> None:
        before = git(root, "rev-parse", "HEAD").stdout.strip()
        code, output = self.run_migrate(root)
        self.assertEqual(1, code)
        self.assertIn(expected, output.lower())
        self.assertEqual(before, git(root, "rev-parse", "HEAD").stdout.strip())
        self.assertTrue((root / ".stage/past").exists())
        self.assertFalse(
            (root / ".stage/.runtime/schema-v4-maintenance.json").exists()
        )

    def test_full_v3_project_migrates_to_strict_clean_v4(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v3_project(root)
            source_files = {
                path.relative_to(stage_root).as_posix()
                for path in stage_root.rglob("*")
                if path.is_file()
                and migrate_stage.v4_migration.stage_topology.is_legacy_path(
                    path.relative_to(stage_root).as_posix()
                )
            }
            expected_destinations = {
                migrate_stage.v4_migration.stage_topology.relocate_v3_path(path)
                for path in source_files
            }

            code, output = self.run_migrate(root)
            fields = (stage_root / "proposals/path-fields.md").read_text(
                encoding="utf-8"
            )
            settings = json.loads(
                (stage_root / "settings.json").read_text(encoding="utf-8")
            )
            findings = audit_stage.Audit(root).run()
            staged = git(root, "diff", "--cached", "--name-status").stdout
            result_files = {
                path.relative_to(stage_root).as_posix()
                for path in stage_root.rglob("*")
                if path.is_file()
            }

            self.assertEqual(0, code, output)
            self.assertTrue((stage_root / "official/canon/principles.md").is_file())
            self.assertTrue((stage_root / "work/current/W-00000001.md").is_file())
            self.assertTrue((stage_root / "work/planned/index.md").is_file())
            self.assertTrue((stage_root / "decisions/index.md").is_file())
            self.assertTrue((stage_root / "roadmap/themes/index.md").is_file())
            self.assertTrue((stage_root / "roadmap/milestones/index.md").is_file())
            self.assertFalse((stage_root / "past").exists())
            self.assertFalse((stage_root / "present").exists())
            self.assertFalse((stage_root / "future").exists())
            self.assertTrue(expected_destinations.issubset(result_files))
            self.assertEqual(
                b"verbatim relocation payload\x00\xff",
                (stage_root / "proposals/verbatim.txt").read_bytes(),
            )
            self.assertIn(
                'promotes: ".stage/official/canon/principles.md"', fields
            )
            self.assertIn("decision_refs: .stage/decisions/pending/DE-00000001.md", fields)
            self.assertIn("retrospective_ref: .stage/work/retrospectives/R-00000001.md", fields)
            self.assertIn("scope: src; .stage/proposals/", fields)
            self.assertIn("[principles](../official/canon/principles.md)", fields)
            self.assertIn("`state/questions.md`", fields)
            self.assertEqual(4, settings["schema_version"])
            self.assertEqual([], findings)
            self.assertIn("R100", staged)
            self.assertIn("does not commit", output.lower())
            self.assertIn("--abort", output)
            self.assertIn("git revert", output)

    def test_dirty_tree_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_v3_project(root)
            (root / "dirty.txt").write_text("dirty\n", encoding="utf-8")
            self.assert_refusal(root, "dirty")

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_symlinked_stage_root_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v3_project(root)
            data_root = root / "stage-data"
            stage_root.rename(data_root)
            (root / ".stage").symlink_to(data_root, target_is_directory=True)
            git(root, "add", "-A")
            git(root, "commit", "-qm", "symlink stage")
            self.assert_refusal(root, "symlink")

    def test_case_insensitive_destination_collision_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_v3_project(root)
            collision = root / ".stage/OFFICIAL"
            collision.mkdir()
            (collision / "custom.md").write_text("# Collision\n", encoding="utf-8")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "case collision")
            self.assert_refusal(root, "case-insensitive")

    def test_pending_intent_and_claim_are_refused(self):
        for name in ("W-00000001.json", "W-00000001.json.claim-deadbeef"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.make_v3_project(root)
                intent = root / ".stage/.runtime/intents" / name
                intent.parent.mkdir(parents=True, exist_ok=True)
                intent.write_text("{}\n", encoding="utf-8")
                self.assert_refusal(root, name.lower())

    def test_legacy_promotion_intent_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_v3_project(root)
            intent = root / ".stage/.runtime/promote-intent.json"
            intent.parent.mkdir(parents=True, exist_ok=True)
            intent.write_text("{}\n", encoding="utf-8")
            self.assert_refusal(root, "promote-intent.json")

    def test_mixed_populated_topology_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_v3_project(root)
            current = root / ".stage/work"
            current.mkdir(parents=True)
            (current / "custom.md").write_text("# Mixed\n", encoding="utf-8")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "mixed topology")
            self.assert_refusal(root, "mixed populated topology")

    def test_customized_root_index_emits_proposal_and_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v3_project(root)
            index_path = stage_root / "index.md"
            index_path.write_text(
                index_path.read_text(encoding="utf-8").replace(
                    "| Active work | `present/work/active.md` |",
                    "| Active work customized | `present/work/active.md` |",
                    1,
                ),
                encoding="utf-8",
            )
            git(root, "add", "-A")
            git(root, "commit", "-qm", "customize root index")

            self.assert_refusal(root, "proposed v4 index")
            proposal = stage_root / ".runtime/schema-v4-index.proposed.md"

            self.assertTrue(proposal.is_file())
            self.assertFalse((stage_root / ".runtime/schema-v4-maintenance.json").exists())

    def test_empty_legacy_roadmap_directory_uses_directory_rename(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v3_project(root)
            roadmap = stage_root / "future/roadmap"
            for path in sorted(roadmap.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
            git(root, "add", "-A")
            git(root, "commit", "-qm", "empty roadmap fixture")
            checked = migrate_stage.v4_migration.preflight(
                root,
                stage_root,
                migrate_stage.load_settings(stage_root),
                False,
            )
            journal = migrate_stage.v4_migration.begin(stage_root, checked, 3)

            migrate_stage.v4_migration.relocate(root, stage_root, checked, journal)

            roadmap_move = next(
                move
                for move in journal["moves"]
                if move["source"] == "future/roadmap"
            )
            self.assertEqual("directory-rename", roadmap_move["method"])
            self.assertTrue((stage_root / "roadmap").is_dir())
            self.assertFalse((stage_root / "future/roadmap").exists())

    def test_post_relocation_verification_blocks_schema_stamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v3_project(root)
            with patch.object(
                migrate_stage.v4_migration,
                "rewrite_moved_markdown",
                return_value=[],
            ):
                code, output = self.run_migrate(root)
            settings = json.loads(
                (stage_root / "settings.json").read_text(encoding="utf-8")
            )
            marker_exists = (
                stage_root / ".runtime/schema-v4-maintenance.json"
            ).is_file()
            rerun_code, rerun_output = self.run_migrate(root)

        self.assertEqual(1, code)
        self.assertIn("legacy reference", output.lower())
        self.assertEqual(3, settings["schema_version"])
        self.assertTrue(marker_exists)
        self.assertEqual(1, rerun_code)
        self.assertIn("abort", rerun_output.lower())

    def test_strict_audit_failure_restores_v3_schema_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v3_project(root)
            finding = audit_stage.Finding(
                "warning", "TEST001", "injected strict-audit failure"
            )
            with patch.object(
                migrate_stage,
                "strict_audit_findings",
                return_value=[finding],
            ):
                code, output = self.run_migrate(root)
            settings = json.loads(
                (stage_root / "settings.json").read_text(encoding="utf-8")
            )

        self.assertEqual(1, code)
        self.assertEqual(3, settings["schema_version"])
        self.assertIn("restored to the schema-v3 marker", output)

    def test_abort_restores_the_clean_v3_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v3_project(root)
            before = {
                path.relative_to(stage_root).as_posix(): path.read_bytes()
                for path in stage_root.rglob("*")
                if path.is_file() and ".runtime" not in path.parts
            }
            code, output = self.run_migrate(root)
            self.assertEqual(0, code, output)

            abort_code, abort_output = self.run_migrate(root, abort=True)
            after = {
                path.relative_to(stage_root).as_posix(): path.read_bytes()
                for path in stage_root.rglob("*")
                if path.is_file() and ".runtime" not in path.parts
            }
            status = git(root, "status", "--porcelain").stdout

        self.assertEqual(0, abort_code, abort_output)
        self.assertEqual(before, after)
        self.assertEqual("", status)
        self.assertIn("restored", abort_output.lower())

    def test_dry_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v3_project(root)
            before = {
                path.relative_to(stage_root).as_posix(): path.read_bytes()
                for path in stage_root.rglob("*")
                if path.is_file()
            }
            code, output = self.run_migrate(root, dry_run=True)
            after = {
                path.relative_to(stage_root).as_posix(): path.read_bytes()
                for path in stage_root.rglob("*")
                if path.is_file()
            }

        self.assertEqual(0, code, output)
        self.assertEqual(before, after)
        self.assertIn("dry run", output.lower())

    def test_stage_migrate_skill_facade_runs_the_canonical_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_v3_project(root)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_CLI),
                    "--project-root",
                    str(root),
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
            )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Migration plan complete", result.stdout)

    def test_v3_write_fails_closed_while_audit_and_migration_remain_callable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_v3_project(root)
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "src/app.py", "content": "x\n"},
            }

            gate = audit_stage.stage_guard.handle_event("pre-tool-use", payload)
            reason = gate["hookSpecificOutput"]["permissionDecisionReason"]
            schema_findings = [
                finding
                for finding in audit_stage.Audit(root).run()
                if finding.code == "SCHEMA001"
            ]
            migration_code, migration_output = self.run_migrate(root, dry_run=True)

        self.assertEqual(
            "deny", gate["hookSpecificOutput"]["permissionDecision"]
        )
        self.assertIn("schema v3", reason)
        self.assertIn("requires v4", reason)
        self.assertIn("stage-migrate", reason)
        self.assertEqual(1, len(schema_findings))
        self.assertIn("stage-migrate", schema_findings[0].message)
        self.assertEqual(0, migration_code, migration_output)

    def test_missing_schema_marker_is_behind_but_remains_migratable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v3_project(root)
            settings_path = stage_root / "settings.json"
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            settings.pop("schema_version")
            settings_path.write_text(
                json.dumps(settings, indent=2) + "\n", encoding="utf-8"
            )
            git(root, "add", "-A")
            git(root, "commit", "-qm", "remove schema marker")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "src/app.py", "content": "x\n"},
            }

            gate = audit_stage.stage_guard.handle_event("pre-tool-use", payload)
            reason = gate["hookSpecificOutput"]["permissionDecisionReason"]
            schema_findings = [
                finding
                for finding in audit_stage.Audit(root).run()
                if finding.code == "SCHEMA001"
            ]
            migration_code, migration_output = self.run_migrate(root, dry_run=True)

        self.assertEqual("deny", gate["hookSpecificOutput"]["permissionDecision"])
        self.assertIn("missing/invalid", reason)
        self.assertIn("stage-migrate", reason)
        self.assertEqual(1, len(schema_findings))
        self.assertEqual(0, migration_code, migration_output)


if __name__ == "__main__":
    unittest.main()
