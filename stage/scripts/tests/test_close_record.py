from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "close_record.py"
TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "templates" / "v4" / "project-stage"
AUDIT = Path(__file__).resolve().parents[1] / "audit_stage.py"


def run_cli(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
    )


class CloseRecordTest(unittest.TestCase):
    def make_stage(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        shutil.copytree(TEMPLATE_ROOT, root / ".stage")
        return tmp, root

    def write_observation(self, root: Path) -> tuple[Path, str]:
        stage = root / ".stage"
        record = stage / "state/observations/O-00000001.md"
        record.write_text(
            """---
id: O-00000001
title: Indexes can drift
work_items:
---

# O-00000001 Indexes can drift

## Observation

The files disagree.

## Evidence

The index is stale.

## Impact

Readers see the wrong state.

## Status

Open.

## Next action

Close it with one command.
""",
            encoding="utf-8",
        )
        entry = (
            "- [O-00000001](observations/O-00000001.md) — Indexes can drift\n"
            "  and this continuation must move with the entry.\n"
        )
        current = stage / "state/current.md"
        current.write_text(
            current.read_text(encoding="utf-8").replace("-\n", entry),
            encoding="utf-8",
        )
        return record, entry

    def write_question(self, root: Path) -> tuple[Path, str]:
        stage = root / ".stage"
        record = stage / "state/questions/Q-00000001.md"
        record.write_text(
            """---
id: Q-00000001
title: Why did the run fail?
work_items:
---

# Q-00000001 Why did the run fail?

## Question

Why?

## Decision needed

None.

## Blocked work

None.

## Answer owner

None.

## Status

Answered.
""",
            encoding="utf-8",
        )
        entry = (
            "| Q-00000001 | Find the cause | None | answered | "
            "[questions/Q-00000001.md](questions/Q-00000001.md) |\n"
        )
        index = stage / "state/questions.md"
        index.write_text(index.read_text(encoding="utf-8") + entry, encoding="utf-8")
        return record, entry

    def write_proposal(self, root: Path) -> tuple[Path, str]:
        stage = root / ".stage"
        record = stage / "proposals/P-00000001.md"
        record.write_text(
            """# P-00000001 Make record closing atomic

## Proposal

Move all owned surfaces together.

## Purpose

Keep indexes truthful.

## Alternatives

Edit them by hand.

## Cost

One command.

## Risks

A partial write.

## Decision criteria

All surfaces agree.

## Status

Pending.
""",
            encoding="utf-8",
        )
        entry = (
            "| P-00000001 | Make record closing atomic | pending | 2026-09-01 | "
            "[P-00000001](P-00000001.md) |\n"
        )
        index = stage / "proposals/index.md"
        index.write_text(index.read_text(encoding="utf-8") + entry, encoding="utf-8")
        return record, entry

    def test_closes_and_reopens_observation_with_exact_index_entry(self) -> None:
        tmp, root = self.make_stage()
        with tmp:
            source, entry = self.write_observation(root)
            original = source.read_bytes()

            closed = run_cli(root, "close", "O-00000001", "--reason", "The fix shipped.")

            archived = root / ".stage/official/state/archive/O-00000001.md"
            self.assertEqual(0, closed.returncode, closed.stdout + closed.stderr)
            self.assertFalse(source.exists())
            self.assertTrue(archived.exists())
            self.assertIn("Closed reason: The fix shipped.", archived.read_text(encoding="utf-8"))
            self.assertNotIn(
                "O-00000001",
                (root / ".stage/state/current.md").read_text(encoding="utf-8"),
            )
            archive_index = (
                root / ".stage/official/state/archive/index.md"
            ).read_text(encoding="utf-8")
            self.assertIn("| O-00000001 | observation | The fix shipped. |", archive_index)

            reopened = run_cli(root, "reopen", "O-00000001")

            self.assertEqual(0, reopened.returncode, reopened.stdout + reopened.stderr)
            self.assertEqual(original, source.read_bytes())
            self.assertFalse(archived.exists())
            self.assertIn(entry, (root / ".stage/state/current.md").read_text(encoding="utf-8"))
            self.assertNotIn(
                "O-00000001",
                (root / ".stage/official/state/archive/index.md").read_text(encoding="utf-8"),
            )

    def test_closes_question_and_removes_its_table_row(self) -> None:
        tmp, root = self.make_stage()
        with tmp:
            source, _entry = self.write_question(root)

            result = run_cli(root, "close", "Q-00000001", "--reason", "The cause is known.")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertFalse(source.exists())
            self.assertNotIn(
                "Q-00000001",
                (root / ".stage/state/questions.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "| Q-00000001 | question | The cause is known. |",
                (root / ".stage/official/state/archive/index.md").read_text(encoding="utf-8"),
            )

    def test_first_close_creates_a_missing_archive_index_from_the_locale(self) -> None:
        tmp, root = self.make_stage()
        with tmp:
            self.write_observation(root)
            shutil.rmtree(root / ".stage/official/state/archive")

            result = run_cli(root, "close", "O-00000001", "--reason", "The fix shipped.")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            archive = root / ".stage/official/state/archive"
            self.assertTrue((archive / "O-00000001.md").is_file())
            self.assertIn(
                "| O-00000001 | observation | The fix shipped. |",
                (archive / "index.md").read_text(encoding="utf-8"),
            )

    def test_proposal_requires_and_records_one_outcome(self) -> None:
        tmp, root = self.make_stage()
        with tmp:
            source, _entry = self.write_proposal(root)

            missing = run_cli(root, "close", "P-00000001", "--reason", "The choice was made.")
            self.assertNotEqual(0, missing.returncode)
            self.assertIn("--outcome", missing.stderr)
            self.assertTrue(source.exists())

            result = run_cli(
                root,
                "close",
                "P-00000001",
                "--reason",
                "The choice was made.",
                "--outcome",
                "partial",
            )

            archived = root / ".stage/official/proposals/archive/P-00000001.md"
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Outcome: partial", archived.read_text(encoding="utf-8"))
            self.assertNotIn(
                "P-00000001",
                (root / ".stage/proposals/index.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "| P-00000001 | partial | The choice was made. |",
                (root / ".stage/official/proposals/archive/index.md").read_text(encoding="utf-8"),
            )

    def test_reason_is_required_and_must_be_one_line(self) -> None:
        tmp, root = self.make_stage()
        with tmp:
            source, _entry = self.write_observation(root)

            missing = run_cli(root, "close", "O-00000001")
            multiline = run_cli(root, "close", "O-00000001", "--reason", "one\ntwo")

            self.assertNotEqual(0, missing.returncode)
            self.assertIn("--reason", missing.stderr)
            self.assertNotEqual(0, multiline.returncode)
            self.assertIn("one line", multiline.stderr)
            self.assertTrue(source.exists())

    def test_failed_write_restores_every_surface(self) -> None:
        spec = importlib.util.spec_from_file_location("close_record", SCRIPT)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        tmp, root = self.make_stage()
        with tmp:
            source, _entry = self.write_observation(root)
            watched = [
                source,
                root / ".stage/state/current.md",
                root / ".stage/official/state/archive/O-00000001.md",
                root / ".stage/official/state/archive/index.md",
            ]
            before = {path: path.read_bytes() if path.exists() else None for path in watched}
            real_replace = module._replace_staged_file
            calls = 0

            def fail_third(staged: Path, target: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 3:
                    raise OSError("injected write failure")
                real_replace(staged, target)

            with mock.patch.object(module, "_replace_staged_file", side_effect=fail_third):
                with self.assertRaisesRegex(module.CloseRecordError, "injected write failure"):
                    module.close_record(
                        root / ".stage",
                        "O-00000001",
                        "The fix shipped.",
                        None,
                    )

            after = {path: path.read_bytes() if path.exists() else None for path in watched}
            self.assertEqual(before, after)

    def test_each_closed_record_family_passes_stage_audit(self) -> None:
        cases = (
            ("observation", self.write_observation, ("O-00000001",)),
            ("question", self.write_question, ("Q-00000001",)),
            (
                "proposal",
                self.write_proposal,
                ("P-00000001", "--outcome", "accepted"),
            ),
        )
        for family, write_record, close_args in cases:
            with self.subTest(family=family):
                tmp, root = self.make_stage()
                with tmp:
                    write_record(root)
                    result = run_cli(
                        root,
                        "close",
                        *close_args,
                        "--reason",
                        "The record is settled.",
                    )
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)

                    audit = subprocess.run(
                        [sys.executable, str(AUDIT), "--project-root", str(root)],
                        capture_output=True,
                        text=True,
                    )

                    self.assertEqual(0, audit.returncode, audit.stdout + audit.stderr)
                    self.assertIn("Summary: errors=0", audit.stdout)


if __name__ == "__main__":
    unittest.main()
