from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


STAGE_ROOT = Path(__file__).resolve().parents[2]
HOOK_ROOT = STAGE_ROOT / "hooks"
SCRIPT_ROOT = STAGE_ROOT / "scripts"
V4_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "v4" / "project-stage"
for import_root in (HOOK_ROOT, SCRIPT_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


init_stage = load_module("schema_dispatch_init_stage", SCRIPT_ROOT / "init_stage.py")
stage_guard = load_module("stage_guard", HOOK_ROOT / "stage_guard.py")
stage_context = load_module("stage_context", HOOK_ROOT / "stage_context.py")
stage_paths = load_module("stage_paths", HOOK_ROOT / "stage_paths.py")
stage_records = load_module("stage_records", SCRIPT_ROOT / "stage_records.py")
audit_stage = load_module("schema_dispatch_audit_stage", SCRIPT_ROOT / "audit_stage.py")


def permission_decision(result: dict) -> str:
    if not result:
        return "allow"
    return result.get("hookSpecificOutput", {}).get("permissionDecision", "allow")


def active_card(item_id: str, *, decision_refs: str = "") -> str:
    return (
        "---\n"
        f"id: {item_id}\n"
        "title: Schema dispatch fixture\n"
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
        "scope: src/\n"
        "promotes:\n"
        f"decision_refs: {decision_refs}\n"
        "---\n\n"
        f"# {item_id} Schema dispatch fixture\n"
    )


class SchemaV4ConsumerDispatchTest(unittest.TestCase):
    def assert_guard_allows_registered_write(self, root: Path) -> None:
        result = stage_guard.validate_pre_tool(
            {
                "cwd": str(root),
                "tool_name": "Write",
                "tool_input": {
                    "file_path": str(root / "src" / "app.py"),
                    "content": "print('ok')\n",
                },
            }
        )
        self.assertEqual("allow", permission_decision(result))
        self.assertEqual("", stage_guard.commit_blocker(root, ["src/app.py"]))

    def assert_guard_blocks_unapproved_official_write(
        self, root: Path, target: str
    ) -> None:
        result = stage_guard.validate_pre_tool(
            {
                "cwd": str(root),
                "tool_name": "Write",
                "tool_input": {"file_path": target, "content": "replacement\n"},
            }
        )
        self.assertEqual("deny", permission_decision(result))

    def test_v3_fixture_keeps_existing_consumer_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False)
            stage_root = root / ".stage"
            item_id = "W-00000091"
            item_path = stage_root / "present" / "work" / "items" / f"{item_id}.md"
            item_path.write_text(active_card(item_id), encoding="utf-8")
            with (stage_root / "present" / "work" / "active.md").open(
                "a", encoding="utf-8"
            ) as handle:
                handle.write(
                    f"| {item_id} | development | codex | Fixture | active | test | "
                    f"[items/{item_id}.md](items/{item_id}.md) |\n"
                )

            self.assertEqual("v3", stage_paths.active_topology(stage_root))
            self.assert_guard_allows_registered_write(root)
            self.assert_guard_blocks_unapproved_official_write(
                root, ".stage/past/canon/principles.md"
            )
            graph = stage_records.RecordGraph(stage_root)
            self.assertEqual([item_path], [entry.item.path for entry in graph.work])
            self.assertEqual([], audit_stage.Audit(root).run())
            context = stage_context.session_context(root)

        self.assertIn("`past` is official, `present` is in progress, `future` is planned", context)
        self.assertIn("`.stage/present/work/items/`", context)
        self.assertIn("`future/backlog/items`", context)
        self.assertNotIn("`.stage/work/current/`", context)

    def test_v4_fixture_routes_every_rewired_consumer_through_registry_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = root / ".stage"
            shutil.copytree(V4_TEMPLATE_ROOT, stage_root)

            current_id = "W-00000092"
            current_path = stage_root / "work" / "current" / f"{current_id}.md"
            current_path.write_text(
                active_card(current_id, decision_refs="DE-00000092"), encoding="utf-8"
            )
            with (stage_root / "work" / "active.md").open("a", encoding="utf-8") as handle:
                handle.write(
                    f"| {current_id} | development | codex | Fixture | active | test | "
                    f"[current/{current_id}.md](current/{current_id}.md) |\n"
                )

            planned_id = "W-00000093"
            planned_path = stage_root / "work" / "planned" / f"{planned_id}.md"
            planned_path.write_text(
                (
                    f"---\nid: {planned_id}\ntitle: Planned fixture\nkind: development\n"
                    "venue: codex\nparent:\nstatus: selected\npriority: high\n---\n"
                    f"# {planned_id} Planned fixture\n"
                ),
                encoding="utf-8",
            )
            with (stage_root / "work" / "planned" / "index.md").open(
                "a", encoding="utf-8"
            ) as handle:
                handle.write(
                    f"| {planned_id} | Planned fixture | development | selected | high | | "
                    f"[{planned_id}.md]({planned_id}.md) |\n"
                )

            decision_path = stage_root / "decisions" / "pending" / "DE-00000092.md"
            decision_path.write_text(
                (
                    "---\nid: DE-00000092\n"
                    f"work_item: {current_id}\nstatus: decided\n---\n"
                    "# DE-00000092 Fixture decision\n\n"
                    "## Principles applied\n\nSSOT\n"
                ),
                encoding="utf-8",
            )

            question_path = stage_root / "state" / "questions" / "Q-00000092.md"
            question_path.write_text(
                (
                    "---\nid: Q-00000092\ntitle: Fixture question\n"
                    f"work_items: {current_id}\n---\n# Q-00000092 Fixture question\n"
                ),
                encoding="utf-8",
            )

            milestone_path = stage_root / "roadmap" / "milestones" / "M-00000092.md"
            milestone_path.write_text("# M-00000092 Fixture milestone\n", encoding="utf-8")
            with (stage_root / "roadmap" / "index.md").open("a", encoding="utf-8") as handle:
                handle.write("| M-00000092 | Fixture milestone |\n")

            self.assertEqual("v4", stage_paths.active_topology(stage_root))
            self.assert_guard_allows_registered_write(root)
            self.assert_guard_blocks_unapproved_official_write(
                root, ".stage/official/canon/principles.md"
            )
            graph = stage_records.RecordGraph(stage_root)
            self.assertIn(current_path, [entry.item.path for entry in graph.work])
            self.assertIn(planned_path, [node.path for node in graph.backlog])
            self.assertIn(decision_path, [node.path for node in graph.decisions])
            self.assertIn(question_path, [node.path for node in graph.state])
            self.assertIn(milestone_path, [node.path for node in graph.milestones])
            self.assertEqual([], audit_stage.Audit(root).run())
            context = stage_context.session_context(root)

        self.assertIn("`.stage/work/current/`", context)
        self.assertIn("`official/canon/principles.md`", context)
        self.assertIn("`decisions/pending`", context)
        self.assertIn("`state/questions`", context)
        self.assertIn("`work/planned`", context)
        self.assertIn("`roadmap/", context)
        self.assertNotIn("`.stage/present/work/items/`", context)

    def test_v4_guard_authorizes_official_write_with_matching_intent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = root / ".stage"
            shutil.copytree(V4_TEMPLATE_ROOT, stage_root)
            item_id = "W-00000094"
            target = ".stage/official/canon/principles.md"
            item_path = stage_root / "work" / "current" / f"{item_id}.md"
            item_path.write_text(
                active_card(item_id)
                .replace("status: active", "status: completed")
                .replace("verification: pending", "verification: passed")
                .replace("retrospective: pending", "retrospective: completed")
                .replace("promotion: pending", "promotion: approved")
                .replace("promotes:\n", f"promotes: {target}\n"),
                encoding="utf-8",
            )
            intent_path = stage_guard.write_intent_file(
                stage_root, {"work_item": item_id}, target
            )
            self.assertIsNotNone(intent_path)

            result = stage_guard.validate_pre_tool(
                {
                    "cwd": str(root),
                    "tool_name": "Write",
                    "tool_input": {"file_path": target, "content": "replacement\n"},
                }
            )

        self.assertEqual("allow", permission_decision(result))


class ActiveTopologyTest(unittest.TestCase):
    def test_missing_or_non_v4_schema_version_uses_v3(self):
        with tempfile.TemporaryDirectory() as tmp:
            stage_root = Path(tmp) / ".stage"
            stage_root.mkdir()
            self.assertEqual("v3", stage_paths.active_topology(stage_root))
            (stage_root / "settings.json").write_text(
                json.dumps({"schema_version": 3}), encoding="utf-8"
            )
            self.assertEqual("v3", stage_paths.active_topology(stage_root))

    def test_exact_v4_schema_version_uses_v4(self):
        with tempfile.TemporaryDirectory() as tmp:
            stage_root = Path(tmp) / ".stage"
            stage_root.mkdir()
            (stage_root / "settings.json").write_text(
                json.dumps({"schema_version": 4}), encoding="utf-8"
            )
            self.assertEqual("v4", stage_paths.active_topology(stage_root))


if __name__ == "__main__":
    unittest.main()
