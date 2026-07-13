import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


audit_stage = load_module("audit_stage", SCRIPT_ROOT / "audit_stage.py")
init_stage = load_module("init_stage", SCRIPT_ROOT / "init_stage.py")
migrate_stage = load_module("migrate_stage", SCRIPT_ROOT / "migrate_stage.py")


LEGACY_VERIFICATION = """# Verification

This document owns the verification rules.

## Rules

- Both external-perspective and internal-perspective completion are required.
- Tests or equivalent verification must match the change.
- If the project declares a linter or formatter (a config file or a documented command exists), it must pass; if none is declared, this criterion is skipped.
- New behavior needs a verification path.
- `verification: passed` records evidence produced in the session that sets it — the stated checks actually run, with their output observed, not the checks that were merely supposed to run.
- Work without a retrospective is not complete.

## What `passed` means per kind

`verification: passed` on a work item is valid only against the criterion declared for its `kind`. Projects extend this table; the audit warns when a work item uses a kind that has no row here.

| Kind | `passed` means |
|---|---|
| planning | The user (or decision owner) confirmed the plan; open questions routed to `present/state/questions/`. |
| design | The design was reviewed and approved by its owner; decisions recorded in `present/work/decisions/`. |
| feature | Tests pass; a declared linter passes. |
"""


class MigrateStageTest(unittest.TestCase):
    def make_v1_project(self, root: Path) -> Path:
        """A v2 init downgraded to the v1 layout: full common-doc copies,
        legacy verification.md, legacy index routing rows, schema_version 1."""
        shutil.copytree(migrate_stage.TEMPLATE_ROOT, root / ".stage")
        stage_root = root / ".stage"
        operations = stage_root / "operations"
        for name, path in migrate_stage.plugin_common_docs().items():
            (operations / name).write_bytes(path.read_bytes())
        (operations / "verification.md").write_text(LEGACY_VERIFICATION, encoding="utf-8")
        index_path = stage_root / "index.md"
        rows = "\n".join(
            f"| {name} rules | `operations/{name}` |"
            for name in migrate_stage.plugin_common_docs()
        )
        index_path.write_text(
            index_path.read_text(encoding="utf-8") + rows + "\n", encoding="utf-8"
        )
        settings_path = stage_root / "settings.json"
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        settings["schema_version"] = 1
        settings.pop("operations_overrides", None)
        settings_path.write_text(json.dumps(settings), encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "stage-test@example.com"],
            cwd=root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Stage Test"], cwd=root, check=True
        )
        self.commit(root, "v1 fixture")
        return stage_root

    def commit(self, root: Path, message: str) -> None:
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", message], cwd=root, check=True)

    def run_migrate(self, root: Path, dry_run: bool = False) -> tuple[int, str]:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = migrate_stage.migrate(root, dry_run)
        return code, buffer.getvalue()

    def test_full_v1_layout_migrates_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v1_project(root)

            code, _output = self.run_migrate(root)
            names = sorted(p.name for p in (stage_root / "operations").glob("*.md"))
            verification = (stage_root / "operations" / "verification.md").read_text(
                encoding="utf-8"
            )
            settings = json.loads(
                (stage_root / "settings.json").read_text(encoding="utf-8")
            )
            index_text = (stage_root / "index.md").read_text(encoding="utf-8")
            findings = audit_stage.Audit(root).run()

        self.assertEqual(0, code)
        self.assertEqual(["verification.md"], names)
        # Project-authored kind rows survive; legacy common prose does not.
        self.assertIn("| feature | Tests pass; a declared linter passes. |", verification)
        self.assertIn("| planning |", verification)
        self.assertNotIn("This document owns the verification rules.", verification)
        self.assertEqual(migrate_stage.STAGE_SCHEMA_VERSION, settings["schema_version"])
        self.assertEqual([], settings["operations_overrides"])
        self.assertNotIn("`operations/during.md`", index_text)
        self.assertIn("`operations/verification.md`", index_text)
        self.assertEqual([], [f for f in findings if f.severity == "error"])
        self.assertEqual(set(), {f.code for f in findings} & {"OPS001", "OPS002", "SCHEMA001"})

    def test_migration_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v1_project(root)

            self.run_migrate(root)
            first = {
                p.name: p.read_bytes() for p in (stage_root / "operations").glob("*.md")
            }
            code, _output = self.run_migrate(root)
            second = {
                p.name: p.read_bytes() for p in (stage_root / "operations").glob("*.md")
            }

        self.assertEqual(0, code)
        self.assertEqual(first, second)

    def test_differing_doc_is_kept_and_blocks_stamping(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v1_project(root)
            edited = stage_root / "operations" / "during.md"
            edited.write_text("# During\n\nProject-edited rule.\n", encoding="utf-8")
            self.commit(root, "customize during")

            code, output = self.run_migrate(root)
            kept = edited.exists()
            settings = json.loads(
                (stage_root / "settings.json").read_text(encoding="utf-8")
            )

        self.assertEqual(1, code)
        self.assertIn("during.md", output)
        self.assertTrue(kept)
        self.assertEqual(1, settings["schema_version"])

    def test_declared_override_is_kept_and_stamps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v1_project(root)
            edited = stage_root / "operations" / "during.md"
            edited.write_text("# During\n\nProject-edited rule.\n", encoding="utf-8")
            settings_path = stage_root / "settings.json"
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            settings["operations_overrides"] = ["during.md"]
            settings_path.write_text(json.dumps(settings), encoding="utf-8")
            self.commit(root, "declare override")

            code, _output = self.run_migrate(root)
            kept = edited.exists()
            settings = json.loads(settings_path.read_text(encoding="utf-8"))

        self.assertEqual(0, code)
        self.assertTrue(kept)
        self.assertEqual(migrate_stage.STAGE_SCHEMA_VERSION, settings["schema_version"])

    def test_project_authored_verification_prose_is_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v1_project(root)
            verification = stage_root / "operations" / "verification.md"
            custom = LEGACY_VERIFICATION + "\nProject-specific verification note.\n"
            verification.write_text(custom, encoding="utf-8")
            self.commit(root, "customize verification")

            code, output = self.run_migrate(root)
            after = verification.read_text(encoding="utf-8")

        self.assertEqual(0, code)
        self.assertEqual(custom, after)
        self.assertIn("review manually", output)

    def test_dry_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = self.make_v1_project(root)
            before = {
                p.relative_to(stage_root).as_posix(): p.read_bytes()
                for p in stage_root.rglob("*")
                if p.is_file()
            }

            code, output = self.run_migrate(root, dry_run=True)
            after = {
                p.relative_to(stage_root).as_posix(): p.read_bytes()
                for p in stage_root.rglob("*")
                if p.is_file()
            }

        self.assertEqual(0, code)
        self.assertIn("dry run", output)
        self.assertEqual(before, after)

    def test_fresh_v4_init_is_a_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False)
            stage_root = root / ".stage"
            before = {
                p.relative_to(stage_root).as_posix(): p.read_bytes()
                for p in stage_root.rglob("*")
                if p.is_file()
            }

            code, _output = self.run_migrate(root)
            after = {
                p.relative_to(stage_root).as_posix(): p.read_bytes()
                for p in stage_root.rglob("*")
                if p.is_file()
            }

        self.assertEqual(0, code)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
