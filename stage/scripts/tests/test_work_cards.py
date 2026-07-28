"""Unified work-card lifecycle (DE-00000007): capture in future/backlog,
start_work moves the card to present, migration v3 retires the B family."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
V3_TEMPLATE_ROOT = SCRIPT_ROOT.parent / "templates" / "project-stage"
REGISTER = SCRIPT_ROOT.parents[0] / "skills" / "stage-work" / "register_work.py"
START = SCRIPT_ROOT / "start_work.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


audit_stage = load_module("audit_stage_cards", SCRIPT_ROOT / "audit_stage.py")
init_stage = load_module("init_stage_cards", SCRIPT_ROOT / "init_stage.py")
migrate_stage = load_module("migrate_stage_cards", SCRIPT_ROOT / "migrate_stage.py")


def run_cli(cli: Path, root: Path, *args: str) -> subprocess.CompletedProcess:
    if cli == REGISTER and "--scale" not in args:
        args = ("--scale", "story", *args)
    return subprocess.run(
        [sys.executable, str(cli), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
    )


class WorkCardFlowTest(unittest.TestCase):
    def make(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        init_stage.copy_templates(root, False)
        return tmp, root

    def declare_routing(self, root: Path, routing) -> None:
        settings_path, data, error = audit_stage.read_settings(root / ".stage")
        if error is not None:
            raise error
        if not isinstance(data, dict):
            raise AssertionError("test project settings must be an object")
        data["venue_routing"] = routing
        settings_path.write_text(json.dumps(data), encoding="utf-8")

    def write_exception_decision(self, root: Path, decision_id: str = "DE-0001") -> None:
        decisions = root / ".stage/decisions/pending"
        decisions.mkdir(parents=True, exist_ok=True)
        (decisions / f"{decision_id}.md").write_text(
            (
                f"---\nid: {decision_id}\nwork_item: W-00000001\nstatus: decided\n"
                "authorizes: venue_exception\n---\n"
                f"# {decision_id} Exception\n\n## Principles applied\n\n- SSOT — one owner.\n"
            ),
            encoding="utf-8",
        )

    def test_backlog_capture_creates_planned_card(self):
        tmp, root = self.make()
        with tmp:
            result = run_cli(
                REGISTER, root, "--backlog", "--title", "Future thing", "--kind", "feature",
                "--scope", "", "--priority", "high",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            card = root / ".stage/work/planned/W-00000001/_story.md"
            body = card.read_text(encoding="utf-8")
            index = (root / ".stage/work/planned/index.md").read_text(encoding="utf-8")
            active = (root / ".stage/work/active.md").read_text(encoding="utf-8")
            findings = audit_stage.Audit(root).run()

        self.assertIn("status: captured", body)
        self.assertIn("priority: high", body)
        self.assertIn("(W-00000001/_story.md)", index)
        self.assertNotIn("W-00000001", active)
        self.assertEqual([], [f.code for f in findings if f.severity == "error"])

    def test_capture_allows_split_kind_without_decision(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root, {"feature": "split"})
            result = run_cli(
                REGISTER, root, "--backlog", "--title", "Mixed", "--kind", "feature",
                "--scope", "",
            )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_start_moves_card_and_upgrades_fields(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root, {"design": "claude"})
            run_cli(REGISTER, root, "--backlog", "--title", "Plan it", "--kind", "design", "--scope", "")
            result = run_cli(START, root, "W-00000001", "--scope", "src")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("design -> claude", result.stdout)
            moved = root / ".stage/work/current/W-00000001/_story.md"
            body = moved.read_text(encoding="utf-8")
            gone = (root / ".stage/work/planned/W-00000001").exists()
            index = (root / ".stage/work/planned/index.md").read_text(encoding="utf-8")
            active = (root / ".stage/work/active.md").read_text(encoding="utf-8")
            findings = audit_stage.Audit(root).run()

        self.assertFalse(gone)
        self.assertIn("status: active", body)
        self.assertIn("venue: claude", body)
        self.assertIn("scope: src", body)
        self.assertIn("verification: pending", body)
        self.assertIn("## Promotion decision", body)
        self.assertNotIn("(W-00000001/_story.md)", index)
        self.assertIn("(current/W-00000001/_story.md)", active)
        self.assertEqual([], [f.code for f in findings if f.severity == "error"])

    def test_start_moves_the_whole_top_level_hierarchy(self):
        tmp, root = self.make()
        with tmp:
            epic = run_cli(
                REGISTER,
                root,
                "--backlog",
                "--scale",
                "epic",
                "--title",
                "Reliable driver",
                "--kind",
                "development",
                "--scope",
                "",
                "--id",
                "W-00000001",
            )
            story = run_cli(
                REGISTER,
                root,
                "--backlog",
                "--scale",
                "story",
                "--parent",
                "W-00000001",
                "--title",
                "Review evidence",
                "--kind",
                "development",
                "--scope",
                "",
                "--id",
                "W-00000002",
            )
            action = run_cli(
                REGISTER,
                root,
                "--backlog",
                "--scale",
                "action",
                "--parent",
                "W-00000002",
                "--title",
                "Driver side",
                "--kind",
                "development",
                "--scope",
                "",
                "--id",
                "W-00000003",
            )
            result = run_cli(START, root, "W-00000001", "--scope", "stage/x")
            current = root / ".stage/work/current/W-00000001"
            planned_exists = (root / ".stage/work/planned/W-00000001").exists()
            epic_exists = (current / "_epic.md").is_file()
            story_exists = (current / "W-00000002/_story.md").is_file()
            action_exists = (
                current / "W-00000002/W-00000003.md"
            ).is_file()
            bodies = [
                record.read_text(encoding="utf-8")
                for record in current.rglob("*.md")
            ]
            findings = audit_stage.Audit(root).run()

        self.assertEqual(0, epic.returncode, epic.stderr)
        self.assertEqual(0, story.returncode, story.stderr)
        self.assertEqual(0, action.returncode, action.stderr)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(planned_exists)
        self.assertTrue(epic_exists)
        self.assertTrue(story_exists)
        self.assertTrue(action_exists)
        for body in bodies:
            self.assertNotIn("\nparent:", body)
            self.assertIn("\nstatus: active\n", body)
            self.assertIn("\nverification: pending\n", body)
            self.assertIn("\nscope: stage/x\n", body)
        self.assertEqual([], [f.code for f in findings if f.severity == "error"])

    def test_start_does_not_reactivate_rejected_hierarchy_descendant(self):
        tmp, root = self.make()
        with tmp:
            epic = run_cli(
                REGISTER,
                root,
                "--backlog",
                "--scale",
                "epic",
                "--title",
                "Reliable driver",
                "--kind",
                "development",
                "--scope",
                "",
                "--id",
                "W-00000001",
            )
            story = run_cli(
                REGISTER,
                root,
                "--backlog",
                "--scale",
                "story",
                "--parent",
                "W-00000001",
                "--title",
                "Review evidence",
                "--kind",
                "development",
                "--scope",
                "",
                "--id",
                "W-00000002",
            )
            action = run_cli(
                REGISTER,
                root,
                "--backlog",
                "--scale",
                "action",
                "--parent",
                "W-00000002",
                "--title",
                "Discarded path",
                "--kind",
                "development",
                "--scope",
                "",
                "--id",
                "W-00000003",
            )
            action_path = (
                root
                / ".stage/work/planned/W-00000001/W-00000002/W-00000003.md"
            )
            action_path.write_text(
                action_path.read_text(encoding="utf-8").replace(
                    "status: captured", "status: rejected"
                ),
                encoding="utf-8",
            )
            result = run_cli(START, root, "W-00000001", "--scope", "stage/x")
            moved_action = (
                root
                / ".stage/work/current/W-00000001/W-00000002/W-00000003.md"
            ).read_text(encoding="utf-8")
            review = (root / ".stage/work/review.md").read_text(encoding="utf-8")
            findings = audit_stage.Audit(root).run()

        self.assertEqual(0, epic.returncode, epic.stderr)
        self.assertEqual(0, story.returncode, story.stderr)
        self.assertEqual(0, action.returncode, action.stderr)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("\nstatus: rejected\n", moved_action)
        self.assertIn(
            "(current/W-00000001/W-00000002/W-00000003.md)",
            review,
        )
        self.assertEqual([], [f.code for f in findings if f.severity == "error"])

    def test_start_carries_autonomous_acceptance_from_planned_card(self):
        tmp, root = self.make()
        with tmp:
            result = run_cli(
                REGISTER,
                root,
                "--backlog",
                "--title",
                "Run itself",
                "--kind",
                "chore",
                "--scope",
                "",
                "--autonomous",
                "--acceptance",
                'python3 -c "print(1)"',
            )
            self.assertEqual(0, result.returncode, result.stderr)
            result = run_cli(START, root, "W-00000001", "--scope", "src")
            body = (root / ".stage/work/current/W-00000001/_story.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("autonomous: true", body)
        self.assertIn('  - "python3 -c \\"print(1)\\""', body)

    def test_start_refuses_autonomous_without_acceptance(self):
        tmp, root = self.make()
        with tmp:
            run_cli(
                REGISTER,
                root,
                "--backlog",
                "--title",
                "Needs check",
                "--kind",
                "chore",
                "--scope",
                "",
            )
            result = run_cli(
                START,
                root,
                "W-00000001",
                "--scope",
                "src",
                "--autonomous",
            )
            still_planned = (root / ".stage/work/planned/W-00000001").exists()

        self.assertEqual(1, result.returncode)
        self.assertIn("autonomous", result.stderr)
        self.assertIn("acceptance", result.stderr)
        self.assertTrue(still_planned)

    def test_start_cli_can_supply_autonomous_acceptance(self):
        tmp, root = self.make()
        with tmp:
            run_cli(
                REGISTER,
                root,
                "--backlog",
                "--title",
                "Needs check",
                "--kind",
                "chore",
                "--scope",
                "",
            )
            result = run_cli(
                START,
                root,
                "W-00000001",
                "--scope",
                "src",
                "--autonomous",
                "--acceptance",
                "python3 -m unittest -q",
            )
            body = (root / ".stage/work/current/W-00000001/_story.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("autonomous: true", body)
        self.assertIn('  - "python3 -m unittest -q"', body)

    def test_start_refuses_split_kind_without_decision(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root, {"feature": "split"})
            run_cli(REGISTER, root, "--backlog", "--title", "Mixed", "--kind", "feature", "--scope", "")
            result = run_cli(START, root, "W-00000001", "--scope", "src")
            still_planned = (root / ".stage/work/planned/W-00000001").exists()

        self.assertEqual(1, result.returncode)
        self.assertIn("split", result.stderr)
        self.assertTrue(still_planned)

    def test_start_accepts_validated_exception(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root, {"feature": "split"})
            self.write_exception_decision(root)
            run_cli(REGISTER, root, "--backlog", "--title", "Mixed", "--kind", "feature", "--scope", "")
            result = run_cli(
                START, root, "W-00000001", "--scope", "src", "--venue", "claude",
                "--decision", "DE-0001",
            )
            body = (
                root / ".stage/work/current/W-00000001/_story.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("decision_refs: DE-0001", body)

    def test_start_refuses_missing_card_and_empty_scope(self):
        tmp, root = self.make()
        with tmp:
            result = run_cli(START, root, "W-00000009", "--scope", "src")
            self.assertEqual(1, result.returncode)
            run_cli(REGISTER, root, "--backlog", "--title", "X", "--kind", "chore", "--scope", "")
            result = run_cli(START, root, "W-00000001", "--scope", ".")
            self.assertEqual(1, result.returncode)

    def test_ids_are_unique_across_columns(self):
        tmp, root = self.make()
        with tmp:
            run_cli(REGISTER, root, "--backlog", "--title", "Planned", "--kind", "chore", "--scope", "")
            result = run_cli(REGISTER, root, "--title", "Direct", "--kind", "chore", "--scope", "src")
            self.assertEqual(0, result.returncode, result.stderr)
            present = sorted(p.name for p in (root / ".stage/work/current").glob("W-*"))

        self.assertEqual(["W-00000002"], present)


class BacklogMigrationTest(unittest.TestCase):
    def make_v2_project_with_b_items(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        shutil.copytree(V3_TEMPLATE_ROOT, root / ".stage")
        stage_root = root / ".stage"
        settings_path = stage_root / "settings.json"
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        settings["schema_version"] = 2
        settings_path.write_text(json.dumps(settings), encoding="utf-8")
        items = stage_root / "future" / "backlog" / "items"
        (items / "B-00000001-realized.md").write_text(
            "---\nid: B-00000001\ntitle: Done already\nkind: feature\nparent:\n"
            "status: selected\npriority:\nrealized_by: W-00000009\n---\n"
            "# B-00000001 Done already\n\n## Purpose\n\nRealized.\n",
            encoding="utf-8",
        )
        (items / "B-00000002-open.md").write_text(
            "---\nid: B-00000002\ntitle: Still wanted\nkind: chore\nparent:\n"
            "status: triaged\npriority: low\n---\n"
            "# B-00000002 Still wanted\n\n## Purpose\n\nKeep me.\n",
            encoding="utf-8",
        )
        (items / "B-00000003-child.md").write_text(
            "---\nid: B-00000003\ntitle: Child idea\nkind: chore\nparent: B-00000002\n"
            "status: captured\npriority:\n---\n"
            "# B-00000003 Child idea\n\n## Purpose\n\nChild.\n",
            encoding="utf-8",
        )
        index = stage_root / "future" / "backlog" / "index.md"
        index.write_text(
            index.read_text(encoding="utf-8")
            + "| B-00000001 | Done already | feature | selected |  |  | [items/B-00000001-realized.md](items/B-00000001-realized.md) |\n"
            + "| B-00000002 | Still wanted | chore | triaged | low |  | [items/B-00000002-open.md](items/B-00000002-open.md) |\n"
            + "| B-00000003 | Child idea | chore | captured |  | B-00000002 | [items/B-00000003-child.md](items/B-00000003-child.md) |\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "stage-test@example.com"],
            cwd=root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Stage Test"], cwd=root, check=True
        )
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "v2 fixture"], cwd=root, check=True)
        return tmp, root

    def test_v3_migration_converts_and_removes(self):
        tmp, root = self.make_v2_project_with_b_items()
        with tmp:
            code = migrate_stage.migrate(root, False)
            stage_root = root / ".stage"
            names = sorted(
                p.name
                for p in (stage_root / "work" / "planned").glob("*.md")
                if p.name not in ("README.md", "_template.md", "index.md")
            )
            converted = {
                p.name: p.read_text(encoding="utf-8")
                for p in (stage_root / "work" / "planned").glob("W-*.md")
            }
            index = (stage_root / "work" / "planned" / "index.md").read_text(encoding="utf-8")
            settings = json.loads(
                (stage_root / "settings.json").read_text(encoding="utf-8")
            )
            findings = audit_stage.Audit(root).run()

        self.assertEqual(0, code)
        self.assertEqual(
            ["W-00000001.md", "W-00000002.md", "_epic.md", "_story.md"],
            names,
        )
        bodies = "\n".join(converted.values())
        self.assertIn("Keep me.", bodies)
        self.assertIn("Child.", bodies)
        self.assertNotIn("realized_by", bodies)
        self.assertIn("parent: W-00000001", converted["W-00000002.md"])
        self.assertNotIn("B-00000001", index)
        self.assertIn("| W-00000001 |", index)
        self.assertEqual(migrate_stage.STAGE_SCHEMA_VERSION, settings["schema_version"])
        self.assertEqual([], [f for f in findings if f.severity == "error"])

    def test_backlog_migration_is_idempotent(self):
        tmp, root = self.make_v2_project_with_b_items()
        with tmp:
            migrate_stage.migrate(root, False)
            stage_root = root / ".stage"
            before = {
                p.name: p.read_bytes()
                for p in (stage_root / "work" / "planned").glob("*.md")
            }
            code = migrate_stage.migrate(root, False)
            after = {
                p.name: p.read_bytes()
                for p in (stage_root / "work" / "planned").glob("*.md")
            }

        self.assertEqual(0, code)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
