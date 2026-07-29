from __future__ import annotations

import importlib.util
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


STAGE_ROOT = Path(__file__).resolve().parents[2]
HOOK_ROOT = STAGE_ROOT / "hooks"
REGISTER = STAGE_ROOT / "skills" / "stage-work" / "register_work.py"
START = STAGE_ROOT / "scripts" / "start_work.py"
CLOSE = STAGE_ROOT / "skills" / "stage-retrospective" / "close_work.py"
ARCHIVE = STAGE_ROOT / "skills" / "stage-archive" / "archive_work.py"
AUDIT = STAGE_ROOT / "scripts" / "audit_stage.py"
V3_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "project-stage"
V4_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "v4" / "project-stage"

if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))
import stage_paths  # noqa: E402


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


register_work = load_module("schema_v4_register_work", REGISTER)


def run_cli(cli: Path, root: Path, *args: str) -> subprocess.CompletedProcess:
    if cli == REGISTER and "--scale" not in args and "--count-open-milestones" not in args:
        args = ("--scale", "story", *args)
    return subprocess.run(
        [sys.executable, str(cli), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
    )


def set_frontmatter_field(text: str, name: str, value: str) -> str:
    updated, count = re.subn(
        rf"^({re.escape(name)}:)[ \t]*.*$",
        rf"\g<1> {value}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise AssertionError(f"missing frontmatter field: {name}")
    return updated


class SchemaLifecycleDispatchTest(unittest.TestCase):
    def make_fixture(self, template_root: Path) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        shutil.copytree(template_root, root / ".stage")
        return tmp, root

    def assert_audit_clean(self, root: Path) -> None:
        result = run_cli(AUDIT, root)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("OK: no findings", result.stdout)
        self.assertIn("Summary: errors=0, warnings=0", result.stdout)

    def assert_audit_errors(
        self,
        root: Path,
        expected: list[tuple[str, str]],
    ) -> None:
        result = run_cli(AUDIT, root, "--format", "json")
        payload = json.loads(result.stdout)
        actual = [
            (finding["code"], finding["path"])
            for finding in payload["findings"]
            if finding["severity"] == "error"
        ]
        self.assertEqual(expected, actual, result.stdout + result.stderr)

    def test_v3_registration_fails_closed_and_names_stage_migrate(self):
        tmp, root = self.make_fixture(V3_TEMPLATE_ROOT)
        with tmp:
            without_milestone = run_cli(
                REGISTER,
                root,
                "--title",
                "Legacy unchanged",
                "--kind",
                "development",
                "--scope",
                "src",
            )
            with_milestone = run_cli(
                REGISTER,
                root,
                "--title",
                "Legacy attributed",
                "--kind",
                "development",
                "--scope",
                "docs",
                "--milestone",
                "M-00000007",
            )

            self.assertEqual(2, without_milestone.returncode)
            self.assertEqual(2, with_milestone.returncode)
            self.assertIn("plugin requires v5", without_milestone.stderr)
            self.assertIn("stage-migrate", without_milestone.stderr)
            self.assertIn("stage-migrate", with_milestone.stderr)
            first = root / ".stage/present/work/items/W-00000001.md"
            second = root / ".stage/present/work/items/W-00000002.md"
            active = (root / ".stage/present/work/active.md").read_text(encoding="utf-8")

            self.assertFalse(first.exists())
            self.assertFalse(second.exists())
            self.assertNotIn("W-00000001", active)
            self.assertFalse((root / ".stage/work/current").exists())
            self.assertEqual(5, stage_paths.STAGE_SCHEMA_VERSION)
            audited = run_cli(AUDIT, root)
            self.assertEqual(0, audited.returncode)
            self.assertIn("SCHEMA001", audited.stdout)
            self.assertIn("stage-migrate", audited.stdout)

    def test_v4_direct_registration_uses_registry_current_paths(self):
        tmp, root = self.make_fixture(V4_TEMPLATE_ROOT)
        with tmp:
            result = run_cli(
                REGISTER,
                root,
                "--title",
                "Direct current work",
                "--kind",
                "development",
                "--scope",
                "src",
                "--venue",
                "codex",
                "--milestone",
                "M-00000008",
            )

            self.assertEqual(0, result.returncode, result.stderr)
            card = root / ".stage/work/current/W-00000001/_story.md"
            active = (root / ".stage/work/active.md").read_text(encoding="utf-8")
            self.assertTrue(card.is_file())
            self.assertIn("milestone: M-00000008", card.read_text(encoding="utf-8"))
            self.assertIn("(current/W-00000001/_story.md)", active)
            self.assertFalse((root / ".stage/present/work/items").exists())
            self.assert_audit_clean(root)

    def test_milestone_argument_enforces_zero_or_one_valid_id(self):
        tmp, root = self.make_fixture(V4_TEMPLATE_ROOT)
        with tmp:
            repeated = run_cli(
                REGISTER,
                root,
                "--title",
                "Too many milestones",
                "--kind",
                "development",
                "--scope",
                "src",
                "--milestone",
                "M-00000001",
                "--milestone",
                "M-00000002",
            )
            malformed = run_cli(
                REGISTER,
                root,
                "--title",
                "Malformed milestone",
                "--kind",
                "development",
                "--scope",
                "src",
                "--milestone",
                "M-1",
            )

            self.assertEqual(2, repeated.returncode)
            self.assertIn("at most one", repeated.stderr)
            self.assertEqual(2, malformed.returncode)
            self.assertIn("M-00000001", malformed.stderr)
            self.assertEqual(
                [],
                list((root / ".stage/work/current").glob("W-*.md")),
            )

    def test_v4_direct_registration_refuses_a_planned_id(self):
        tmp, root = self.make_fixture(V4_TEMPLATE_ROOT)
        with tmp:
            captured = run_cli(
                REGISTER,
                root,
                "--backlog",
                "--title",
                "Planned identity owner",
                "--kind",
                "development",
                "--scope",
                "",
            )
            duplicate = run_cli(
                REGISTER,
                root,
                "--id",
                "W-00000001",
                "--title",
                "Duplicate current identity",
                "--kind",
                "development",
                "--scope",
                "src",
                "--venue",
                "codex",
            )

            self.assertEqual(0, captured.returncode, captured.stderr)
            self.assertEqual(1, duplicate.returncode)
            self.assertIn("planned card", duplicate.stderr)
            self.assertTrue(
                (root / ".stage/work/planned/W-00000001/_story.md").is_file()
            )
            self.assertFalse(
                (root / ".stage/work/current/W-00000001").exists()
            )
            self.assert_audit_clean(root)

    def test_open_milestone_detection_is_conservative_until_c6(self):
        tmp, root = self.make_fixture(V4_TEMPLATE_ROOT)
        with tmp:
            milestone = root / ".stage/roadmap/milestones/M-00000001.md"
            milestone.write_text(
                "---\nid: M-00000001\ntheme:\ndecision_refs: DE-00000001\n---\n"
                "# M-00000001 Future semantics\n",
                encoding="utf-8",
            )
            default_count = register_work.count_open_milestones(root / ".stage")
            original = register_work.milestone_decision_chain_is_open
            register_work.milestone_decision_chain_is_open = (
                lambda stage_root, milestone_path: milestone_path == milestone
            )
            try:
                classified_count = register_work.count_open_milestones(root / ".stage")
            finally:
                register_work.milestone_decision_chain_is_open = original
            cli_count = run_cli(REGISTER, root, "--count-open-milestones")

        self.assertEqual(0, default_count)
        self.assertEqual(1, classified_count)
        self.assertEqual(0, cli_count.returncode, cli_count.stderr)
        self.assertEqual("0", cli_count.stdout.strip())

    def test_real_v4_lifecycle_stays_audit_clean_after_every_cli_step(self):
        tmp, root = self.make_fixture(V4_TEMPLATE_ROOT)
        with tmp:
            item_id = "W-00000001"
            retro_id = "R-00000001"
            stage_root = root / ".stage"

            captured = run_cli(
                REGISTER,
                root,
                "--backlog",
                "--title",
                "End-to-end lifecycle",
                "--kind",
                "development",
                "--scope",
                "",
                "--priority",
                "high",
                "--milestone",
                "M-00000009",
            )
            self.assertEqual(0, captured.returncode, captured.stderr)
            planned = stage_root / "work/planned" / item_id / "_story.md"
            current = stage_root / "work/current" / item_id / "_story.md"
            self.assertTrue(planned.is_file())
            self.assertFalse(current.exists())
            self.assertIn(
                f"({item_id}/_story.md)",
                (stage_root / "work/planned/index.md").read_text(encoding="utf-8"),
            )
            self.assertNotIn(
                item_id, (stage_root / "work/active.md").read_text(encoding="utf-8")
            )
            self.assert_audit_clean(root)

            started = run_cli(
                START,
                root,
                item_id,
                "--scope",
                "src",
                "--venue",
                "codex",
                "--owner",
                "Codex",
            )
            self.assertEqual(0, started.returncode, started.stderr)
            self.assertFalse(planned.exists())
            self.assertTrue(current.is_file())
            current_text = current.read_text(encoding="utf-8")
            self.assertEqual(1, current_text.count("milestone: M-00000009"))
            self.assertNotIn(
                item_id,
                (stage_root / "work/planned/index.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                f"(current/{item_id}/_story.md)",
                (stage_root / "work/active.md").read_text(encoding="utf-8"),
            )
            self.assert_audit_clean(root)

            current_text = set_frontmatter_field(
                current_text, "retrospective", "completed"
            )
            current_text = set_frontmatter_field(
                current_text, "retrospective_ref", retro_id
            )
            current.write_text(current_text, encoding="utf-8")
            current_retro = stage_root / "work/retrospectives" / f"{retro_id}.md"
            current_retro.write_text(
                f"---\nid: {retro_id}\nwork_item: {item_id}\n---\n\n"
                f"# {retro_id} End-to-end retrospective\n\n"
                "## Principles applied\n\n- SSOT — registry paths owned the dispatch.\n",
                encoding="utf-8",
            )
            check_command = (
                subprocess.list2cmdline(
                    [sys.executable, "-c", "print('v4 lifecycle check passed')"]
                )
                if sys.platform == "win32"
                else shlex.join(
                    [sys.executable, "-c", "print('v4 lifecycle check passed')"]
                )
            )
            closed = run_cli(
                CLOSE,
                root,
                item_id,
                "--promotion",
                "not_applicable",
                "--check",
                check_command,
            )
            self.assertEqual(0, closed.returncode, closed.stderr)
            closed_text = current.read_text(encoding="utf-8")
            self.assertIn("status: completed", closed_text)
            self.assertIn("verification: passed", closed_text)
            self.assertIn("v4 lifecycle check passed", closed_text)
            self.assertNotIn(
                item_id,
                (stage_root / "work/active.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                f"(current/{item_id}/_story.md)",
                (stage_root / "work/review.md").read_text(encoding="utf-8"),
            )
            self.assert_audit_clean(root)

            archived = run_cli(ARCHIVE, root, item_id)
            self.assertEqual(0, archived.returncode, archived.stdout + archived.stderr)
            archived_item = (
                stage_root
                / "official/work/archive/items"
                / item_id
                / "_story.md"
            )
            archived_retro = (
                stage_root / "official/work/archive/retrospectives" / f"{retro_id}.md"
            )
            self.assertTrue(archived_item.is_file())
            self.assertTrue(archived_retro.is_file())
            self.assertFalse(current.exists())
            self.assertFalse(current_retro.exists())
            self.assertNotIn(
                item_id, (stage_root / "work/review.md").read_text(encoding="utf-8")
            )
            self.assertIn(
                f"| {item_id} | completed | [items/{item_id}/_story.md]",
                (stage_root / "official/work/archive/index.md").read_text(
                    encoding="utf-8"
                ),
            )
            self.assert_audit_clean(root)


if __name__ == "__main__":
    unittest.main()
