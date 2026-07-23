from __future__ import annotations

import importlib.util
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "drive.py"


def python_command(code: str) -> str:
    args = [sys.executable, "-c", code]
    return subprocess.list2cmdline(args) if os.name == "nt" else shlex.join(args)


PASS_COMMAND = python_command("raise SystemExit(0)")


def write_card(
    stage_root: Path,
    item_id: str,
    *,
    parent: str = "",
    status: str = "active",
    venue: str = "codex",
    acceptance: tuple[str, ...] = (),
) -> None:
    path = stage_root / "work/current" / f"{item_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered_acceptance = "[]"
    if acceptance:
        rendered_acceptance = "\n" + "\n".join(
            f"  - {json.dumps(command)}" for command in acceptance
        )
    path.write_text(
        (
            "---\n"
            f"id: {item_id}\n"
            f"venue: {venue}\n"
            f"parent: {parent}\n"
            f"status: {status}\n"
            f"acceptance: {rendered_acceptance}\n"
            "---\n"
        ),
        encoding="utf-8",
    )


class DriveTest(unittest.TestCase):
    def make_project(
        self,
        *,
        executor: str | None = PASS_COMMAND,
        reviewer: str = "echo APPROVED",
        limits: object = None,
    ) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        stage_root = root / ".stage"
        stage_root.mkdir()
        settings: dict[str, object] = {
            "schema_version": 4,
            "review": {
                "reviewers": {
                    "codex": "echo SELF",
                    "claude": reviewer,
                }
            },
        }
        if executor is not None:
            settings["executors"] = {"codex": executor}
        if limits is not None:
            settings["limits"] = limits
        (stage_root / "settings.json").write_text(
            json.dumps(settings), encoding="utf-8"
        )
        write_card(stage_root, "W-00000001")
        return tmp, root

    def run_cli(
        self, root: Path, *args: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--project-root",
                str(root),
                *args,
                "W-00000001",
            ],
            capture_output=True,
            text=True,
        )

    def load_module(self):
        spec = importlib.util.spec_from_file_location("stage_drive", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        sys.modules["stage_drive"] = module
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def test_selects_next_ready_leaf_by_id(self):
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000003",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            write_card(
                stage_root,
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            drive = self.load_module()

            selected = drive.select_next_ready_leaf(
                "W-00000001", drive.load_all_work_items(stage_root)
            )

        self.assertIsNotNone(selected)
        self.assertEqual("W-00000002", selected.item_id)

    def test_skips_direct_child_with_non_terminal_child(self):
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            write_card(
                stage_root,
                "W-00000003",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            write_card(
                stage_root,
                "W-00000004",
                parent="W-00000002",
                acceptance=(PASS_COMMAND,),
            )
            drive = self.load_module()

            selected = drive.select_next_ready_leaf(
                "W-00000001", drive.load_all_work_items(stage_root)
            )

        self.assertIsNotNone(selected)
        self.assertEqual("W-00000003", selected.item_id)

    def test_dry_run_prints_plan_without_changes(self):
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            marker = root / "executor-ran"
            write_card(
                stage_root,
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            settings = json.loads(
                (stage_root / "settings.json").read_text(encoding="utf-8")
            )
            settings["executors"]["codex"] = python_command(
                f"from pathlib import Path; Path({str(marker)!r}).touch()"
            )
            (stage_root / "settings.json").write_text(
                json.dumps(settings), encoding="utf-8"
            )
            before = {
                path.relative_to(root): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }

            result = self.run_cli(root)

            after = {
                path.relative_to(root): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Mode: dry-run", result.stdout)
        self.assertIn("Selected item: W-00000002", result.stdout)
        self.assertIn(f"Acceptance: {PASS_COMMAND}", result.stdout)
        self.assertIn("Independent reviewer: echo APPROVED", result.stdout)
        self.assertEqual(before, after)
        self.assertFalse(marker.exists())

    def test_execute_runs_fakes_and_reports_pass(self):
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "executor-ran"
            tmp, root = self.make_project(
                executor=python_command(
                    f"from pathlib import Path; Path({str(marker)!r}).touch()"
                )
            )
            with tmp:
                write_card(
                    root / ".stage",
                    "W-00000002",
                    parent="W-00000001",
                    acceptance=(PASS_COMMAND,),
                )

                result = self.run_cli(root, "--execute")
                state_path = (
                    root / ".stage/.runtime/driver/W-00000001.json"
                )
                state = json.loads(state_path.read_text(encoding="utf-8"))

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(marker.exists())
            self.assertIn(
                "verification+judge passed → ready to commit + close_work",
                result.stdout,
            )
            self.assertEqual(1, state["iteration_count"])
            self.assertEqual(1, state["items"]["W-00000002"]["attempt_count"])
            self.assertTrue(state["items"]["W-00000002"]["last_fingerprint"])

    def test_reviewer_block_recommends_escalation(self):
        tmp, root = self.make_project(
            reviewer=python_command("print('BLOCK: no'); raise SystemExit(1)")
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )

            result = self.run_cli(root, "--execute")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("independent reviewer BLOCK", result.stdout)
        self.assertIn("→ escalate_work", result.stdout)

    def test_missing_executor_recommends_escalation_without_state_write(self):
        tmp, root = self.make_project(executor=None)
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )

            result = self.run_cli(root, "--execute")

            self.assertNotEqual(0, result.returncode)
            self.assertIn("executors.codex", result.stdout)
            self.assertIn("→ escalate_work", result.stdout)
            self.assertFalse((root / ".stage/.runtime").exists())

    def test_identical_fingerprint_flags_no_progress(self):
        tmp, root = self.make_project()
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )

            first = self.run_cli(root, "--execute")
            second = self.run_cli(root, "--execute")

        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.assertNotEqual(0, second.returncode)
        self.assertIn("NO-PROGRESS", second.stdout)
        self.assertIn("→ escalate_work", second.stdout)

    def test_malformed_limits_fail_closed_without_state_write(self):
        tmp, root = self.make_project(
            limits={
                "max_attempts_per_item": 3,
                "max_iterations": "many",
                "max_wall_clock_seconds": 3600,
            }
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )

            result = self.run_cli(root, "--execute")

            self.assertNotEqual(0, result.returncode)
            self.assertIn(
                "limits.max_iterations must be a positive integer", result.stdout
            )
            self.assertIn("→ escalate_work", result.stdout)
            self.assertFalse((root / ".stage/.runtime").exists())

    def test_attempt_cap_stops_before_another_execution(self):
        limits = {
            "max_attempts_per_item": 1,
            "max_iterations": 10,
            "max_wall_clock_seconds": 3600,
        }
        tmp, root = self.make_project(limits=limits)
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )

            first = self.run_cli(root, "--execute")
            second = self.run_cli(root, "--execute")

            self.assertEqual(0, first.returncode, first.stdout + first.stderr)
            self.assertNotEqual(0, second.returncode)
            self.assertIn("per-item attempt cap reached", second.stdout)
            self.assertIn("→ escalate_work", second.stdout)
            state = json.loads(
                (
                    root / ".stage/.runtime/driver/W-00000001.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(1, state["iteration_count"])
            self.assertEqual(
                1, state["items"]["W-00000002"]["attempt_count"]
            )


if __name__ == "__main__":
    unittest.main()
