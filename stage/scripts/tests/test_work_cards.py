"""Unified work-card lifecycle (DE-00000007): capture in future/backlog,
start_work moves the card to present, migration v3 retires the B family."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
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
        settings_path = root / ".stage/settings.json"
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        data["venue_routing"] = routing
        settings_path.write_text(json.dumps(data), encoding="utf-8")

    def write_exception_decision(self, root: Path, decision_id: str = "DE-0001") -> None:
        decisions = root / ".stage/present/work/decisions"
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
            card = root / ".stage/future/backlog/items/W-00000001.md"
            body = card.read_text(encoding="utf-8")
            index = (root / ".stage/future/backlog/index.md").read_text(encoding="utf-8")
            active = (root / ".stage/present/work/active.md").read_text(encoding="utf-8")
            findings = audit_stage.Audit(root).run()

        self.assertIn("status: captured", body)
        self.assertIn("priority: high", body)
        self.assertIn("(items/W-00000001.md)", index)
        self.assertNotIn("W-00000001", active)
        self.assertEqual([], [f for f in findings if f.severity == "error"])

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
            moved = root / ".stage/present/work/items/W-00000001.md"
            body = moved.read_text(encoding="utf-8")
            gone = (root / ".stage/future/backlog/items/W-00000001.md").exists()
            index = (root / ".stage/future/backlog/index.md").read_text(encoding="utf-8")
            active = (root / ".stage/present/work/active.md").read_text(encoding="utf-8")
            findings = audit_stage.Audit(root).run()

        self.assertFalse(gone)
        self.assertIn("status: active", body)
        self.assertIn("venue: claude", body)
        self.assertIn("scope: src", body)
        self.assertIn("verification: pending", body)
        self.assertIn("## Promotion decision", body)
        self.assertNotIn("(items/W-00000001.md)", index)
        self.assertIn("(items/W-00000001.md)", active)
        self.assertEqual([], [f for f in findings if f.severity == "error"])

    def test_start_refuses_split_kind_without_decision(self):
        tmp, root = self.make()
        with tmp:
            self.declare_routing(root, {"feature": "split"})
            run_cli(REGISTER, root, "--backlog", "--title", "Mixed", "--kind", "feature", "--scope", "")
            result = run_cli(START, root, "W-00000001", "--scope", "src")
            still_planned = (root / ".stage/future/backlog/items/W-00000001.md").exists()

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
            body = (root / ".stage/present/work/items/W-00000001.md").read_text(encoding="utf-8")

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
            present = sorted(p.name for p in (root / ".stage/present/work/items").glob("W-*.md"))

        self.assertEqual(["W-00000002.md"], present)


class BacklogMigrationTest(unittest.TestCase):
    def make_v2_project_with_b_items(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        init_stage.copy_templates(root, False)
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
        return tmp, root

    def test_v3_migration_converts_and_removes(self):
        tmp, root = self.make_v2_project_with_b_items()
        with tmp:
            code = migrate_stage.migrate(root, False)
            stage_root = root / ".stage"
            names = sorted(
                p.name
                for p in (stage_root / "future" / "backlog" / "items").glob("*.md")
                if p.name not in ("README.md", "_template.md")
            )
            converted = {
                p.name: p.read_text(encoding="utf-8")
                for p in (stage_root / "future" / "backlog" / "items").glob("W-*.md")
            }
            index = (stage_root / "future" / "backlog" / "index.md").read_text(encoding="utf-8")
            settings = json.loads(
                (stage_root / "settings.json").read_text(encoding="utf-8")
            )
            findings = audit_stage.Audit(root).run()

        self.assertEqual(0, code)
        self.assertEqual(["W-00000001.md", "W-00000002.md"], names)
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
                for p in (stage_root / "future" / "backlog" / "items").glob("*.md")
            }
            code = migrate_stage.migrate(root, False)
            after = {
                p.name: p.read_bytes()
                for p in (stage_root / "future" / "backlog" / "items").glob("*.md")
            }

        self.assertEqual(0, code)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
