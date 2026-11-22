"""`close_work.py --archive` closes a top-level item and archives it in one command."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from python_shell_command import python_command

CLI = Path(__file__).resolve().parents[2] / "skills" / "stage-retrospective" / "close_work.py"

ITEM = """---
id: {wid}
title: Sample
kind: chore
venue: codex
scope: src/
autonomous: false
acceptance: []
status: {status}
verification: {verification}
retrospective: completed
retrospective_ref: {ref}
promotion: not_applicable
review: not_required
decision_refs:
---

# {wid} Sample

## Purpose

Sample purpose

## Success criteria

- Sample result

## Progress

## Verification

"""
RETRO = "---\nid: {ref}\nwork_item: {wid}\n---\n\n# {ref} Sample retro\n"
INDEX = "# Work Archive\n\n| Work | Final status | Item |\n|---|---|---|\n"
PASSING_CHECK = python_command("print('ok')")
FAILING_CHECK = python_command("raise SystemExit(1)")


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def load_close_module():
    if str(CLI.parent) not in sys.path:
        sys.path.insert(0, str(CLI.parent))
    spec = importlib.util.spec_from_file_location("stage_close_work_archive", CLI)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CloseAndArchiveTest(unittest.TestCase):
    def make(self, status: str = "active") -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        stage = root / ".stage"
        card = stage / "work/current/W-00000001/_story.md"
        card.parent.mkdir(parents=True)
        (stage / "work/retrospectives").mkdir(parents=True)
        (stage / "official/work/archive/items").mkdir(parents=True)
        (stage / "official/work/archive/retrospectives").mkdir(parents=True)
        verification = "passed" if status == "completed" else "pending"
        card.write_text(
            ITEM.format(
                wid="W-00000001", ref="R-00000001", status=status, verification=verification
            ),
            encoding="utf-8",
        )
        (stage / "work/retrospectives/R-00000001.md").write_text(
            RETRO.format(ref="R-00000001", wid="W-00000001"), encoding="utf-8"
        )
        (stage / "official/work/archive/index.md").write_text(INDEX, encoding="utf-8")
        (stage / "settings.json").write_text('{"schema_version": 5}\n', encoding="utf-8")
        return tmp, root

    def add_nested_action(self, root: Path) -> None:
        action = root / ".stage/work/current/W-00000001/W-00000002.md"
        action.write_text(
            ITEM.format(
                wid="W-00000002", ref="R-00000002", status="active", verification="pending"
            ),
            encoding="utf-8",
        )
        (root / ".stage/work/retrospectives/R-00000002.md").write_text(
            RETRO.format(ref="R-00000002", wid="W-00000002"), encoding="utf-8"
        )

    def assert_archived(self, root: Path) -> None:
        stage = root / ".stage"
        archived = stage / "official/work/archive/items/W-00000001/_story.md"
        self.assertTrue(archived.exists())
        self.assertIn("status: archived", archived.read_text(encoding="utf-8"))
        self.assertFalse((stage / "work/current/W-00000001").exists())
        self.assertTrue(
            (stage / "official/work/archive/retrospectives/R-00000001.md").exists()
        )
        self.assertFalse((stage / "work/retrospectives/R-00000001.md").exists())
        index = (stage / "official/work/archive/index.md").read_text(encoding="utf-8")
        self.assertIn("| W-00000001 | completed |", index)

    def test_archive_flag_closes_and_archives_in_one_command(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", PASSING_CHECK, "--archive")

            self.assertEqual(0, proc.returncode, proc.stderr + proc.stdout)
            self.assertIn("closed", proc.stdout)
            self.assertIn("archived", proc.stdout)
            self.assert_archived(root)
            archived = root / ".stage/official/work/archive/items/W-00000001/_story.md"
            self.assertIn("verification: passed", archived.read_text(encoding="utf-8"))

    def test_without_the_flag_the_item_waits_in_the_review_queue(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", PASSING_CHECK)

            self.assertEqual(0, proc.returncode, proc.stderr + proc.stdout)
            card = root / ".stage/work/current/W-00000001/_story.md"
            self.assertIn("status: completed", card.read_text(encoding="utf-8"))
            self.assertFalse(
                (root / ".stage/official/work/archive/items/W-00000001").exists()
            )

    def test_failing_check_archives_nothing(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", FAILING_CHECK, "--archive")

            self.assertEqual(1, proc.returncode)
            card = root / ".stage/work/current/W-00000001/_story.md"
            self.assertIn("status: active", card.read_text(encoding="utf-8"))
            self.assertFalse(
                (root / ".stage/official/work/archive/items/W-00000001").exists()
            )

    def test_archive_flag_is_refused_for_a_nested_item_before_any_check_runs(self):
        tmp, root = self.make()
        with tmp:
            self.add_nested_action(root)
            marker = root / "check-ran"
            check = python_command(
                f"from pathlib import Path; Path({str(marker)!r}).write_text('x')"
            )

            proc = run(root, "W-00000002", "--check", check, "--archive")

            self.assertEqual(1, proc.returncode)
            self.assertIn("--archive", proc.stderr)
            self.assertIn("W-00000001", proc.stderr)
            self.assertFalse(marker.exists())
            action = root / ".stage/work/current/W-00000001/W-00000002.md"
            self.assertIn("status: active", action.read_text(encoding="utf-8"))

    def test_rerun_with_the_flag_archives_an_already_completed_item(self):
        tmp, root = self.make(status="completed")
        with tmp:
            proc = run(root, "W-00000001", "--archive")

            self.assertEqual(0, proc.returncode, proc.stderr + proc.stdout)
            self.assert_archived(root)

    def test_archive_failure_after_close_exits_nonzero_and_names_the_next_command(self):
        tmp, root = self.make()
        with tmp:
            module = load_close_module()
            argv = [
                "close_work.py",
                "--project-root",
                str(root),
                "W-00000001",
                "--check",
                PASSING_CHECK,
                "--archive",
            ]
            stderr = io.StringIO()
            with mock.patch.object(
                module, "archive_closed_item", return_value="W-00000001: ERROR boom"
            ), mock.patch.object(sys, "argv", argv), contextlib.redirect_stderr(
                stderr
            ), contextlib.redirect_stdout(io.StringIO()):
                code = module.main()

            self.assertEqual(1, code)
            self.assertIn("ERROR boom", stderr.getvalue())
            self.assertIn("archive_work.py", stderr.getvalue())
            card = root / ".stage/work/current/W-00000001/_story.md"
            self.assertIn("status: completed", card.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
