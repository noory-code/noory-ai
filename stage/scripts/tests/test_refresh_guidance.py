from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
CLI = SCRIPT_ROOT / "refresh_guidance.py"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import init_stage
import guidance_docs


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
    )


def insert_first_table_row(text: str, row: str) -> str:
    lines = text.splitlines()
    separator = next(
        index
        for index, line in enumerate(lines)
        if line.startswith("|---") or line.startswith("| ---")
    )
    lines.insert(separator + 1, row)
    return "\n".join(lines) + "\n"


class RefreshGuidanceTest(unittest.TestCase):
    def test_help_describes_both_default_skip_conditions(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run(Path(tmp), "--help")

        self.assertEqual(0, result.returncode, result.stderr)
        help_text = " ".join(result.stdout.split())
        self.assertIn("no-table templates have unexplained project lines", help_text)
        self.assertIn("templates have populated tables", help_text)

    def test_default_skips_no_table_document_with_unexplained_project_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False, language="ko")
            relative = Path("state/current.md")
            target = root / ".stage" / relative
            project = target.read_text(encoding="utf-8").replace(
                "-\n",
                "- [O-00000001](observations/O-00000001.md) — 프로젝트 관측\n",
            )
            target.write_text(project, encoding="utf-8")

            result = run(root)

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(project, target.read_text(encoding="utf-8"))
            self.assertIn("skipped state/current.md", result.stdout)
            self.assertIn("1 line not present in the template", result.stdout)

    def test_dry_run_reports_plan_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False, language="ko")
            target = root / ".stage" / "state" / "current.md"
            stale = b"# stale\n"
            target.write_bytes(stale)

            result = run(root, "--dry-run", "state/current.md")

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(stale, target.read_bytes())
            self.assertIn("would refresh state/current.md", result.stdout)

    def test_selected_no_table_document_with_project_lines_is_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False, language="ko")
            relative = Path("state/current.md")
            target = root / ".stage" / relative
            target.write_text(
                "# 현재 상태\n\n- [O-00000001](observations/O-00000001.md)\n",
                encoding="utf-8",
            )

            result = run(root, relative.as_posix())

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(
                init_stage.template_source(relative, "ko").read_bytes(),
                target.read_bytes(),
            )
            self.assertIn("refreshed state/current.md", result.stdout)

    def test_default_keeps_fresh_no_table_document_refreshable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False, language="ko")
            relative = Path("state/current.md")
            target = root / ".stage" / relative
            template = init_stage.template_source(relative, "ko").read_bytes()

            result = run(root)

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(template, target.read_bytes())
            self.assertIn("unchanged state/current.md", result.stdout)
            self.assertNotIn("skipped state/current.md", result.stdout)

    def test_empty_table_keeps_project_rows_and_replaces_other_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False, language="ko")
            relative = Path("work/active.md")
            target = root / ".stage" / relative
            row = (
                "| W-00000001 | development | codex | Test | active | owner | "
                "[item](current/W-00000001.md) |"
            )
            template = init_stage.template_source(relative, "ko").read_text(encoding="utf-8")
            project = insert_first_table_row(template.replace("# 진행 중 작업", "# stale"), row)
            target.write_text(project, encoding="utf-8")

            result = run(root, relative.as_posix())
            refreshed = target.read_text(encoding="utf-8")

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("# 진행 중 작업", refreshed)
            self.assertNotIn("# stale", refreshed)
            self.assertIn(row, refreshed)

    def test_empty_table_merge_preserves_template_prose_exactly(self):
        template = (
            "# Work Archive\r\n"
            "\r\n"
            "First body line.\r\n"
            "Second body line.\r\n"
            "\r\n"
            "| Work | Item |\r\n"
            "|---|---|\r\n"
            "\r\n"
            "Closing body line one.\r\n"
            "Closing body line two.\r\n"
        )
        row = "| W-00000001 | [item](items/W-00000001/_story.md) |"
        project = (
            "# stale\n\n"
            "| Work | Item |\n"
            "|---|---|\n"
            f"{row}\n"
        )

        plan = guidance_docs.plan_refresh(template, project, selected=False)

        self.assertEqual("refresh", plan.action)
        self.assertEqual(
            template.replace("|---|---|\r\n", f"|---|---|\r\n{row}\r\n"),
            plan.content,
        )

    def test_unexplained_line_count_ignores_blank_and_table_separator_lines(self):
        template = "# Current\n\n-\n| Name |\n|---|\n"
        project = "# Current\n \n-\n| Name |\n|:---:|\n- observation\n"

        self.assertEqual(
            1,
            guidance_docs.unexplained_line_count(template, project),
        )

    def test_populated_template_table_is_skipped_by_default_and_replaced_when_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_stage.copy_templates(root, False, language="ko")
            relative = Path("index.md")
            target = root / ".stage" / relative
            stale = "# stale\n"
            target.write_text(stale, encoding="utf-8")

            default_result = run(root)

            self.assertEqual(0, default_result.returncode, default_result.stderr)
            self.assertEqual(stale, target.read_text(encoding="utf-8"))
            self.assertIn("skipped index.md", default_result.stdout)

            selected_result = run(root, relative.as_posix())

            self.assertEqual(0, selected_result.returncode, selected_result.stderr)
            self.assertEqual(
                init_stage.template_source(relative, "ko").read_bytes(),
                target.read_bytes(),
            )

    def test_two_empty_template_tables_are_refused(self):
        import refresh_guidance

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stage_root = root / ".stage"
            stage_root.mkdir()
            (stage_root / "settings.json").write_text(
                json.dumps({"schema_version": 5, "language": "en"}),
                encoding="utf-8",
            )
            target = stage_root / "double.md"
            original = (
                "# Project\n\n"
                "| A |\n"
                "|---|\n"
                "| project row |\n\n"
                "| B |\n"
                "|---|\n"
            )
            target.write_text(original, encoding="utf-8")

            template_root = root / "templates"
            template_root.mkdir()
            (template_root / "double.md").write_text(
                "# Template\n\n| A |\n|---|\n\n| B |\n|---|\n",
                encoding="utf-8",
            )
            locale_root = root / "locales"
            output = io.StringIO()
            with (
                mock.patch.object(
                    refresh_guidance.guidance_docs.init_stage,
                    "TEMPLATE_ROOT",
                    template_root,
                ),
                mock.patch.object(
                    refresh_guidance.guidance_docs.init_stage,
                    "LOCALE_ROOT",
                    locale_root,
                ),
                contextlib.redirect_stdout(output),
            ):
                return_code = refresh_guidance.main(
                    ["--project-root", str(root), "double.md"]
                )

            self.assertEqual(1, return_code)
            self.assertEqual(original, target.read_text(encoding="utf-8"))
            self.assertIn("refused double.md", output.getvalue())
            self.assertIn("multiple empty tables", output.getvalue())


if __name__ == "__main__":
    unittest.main()
