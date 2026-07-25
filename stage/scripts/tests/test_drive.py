from __future__ import annotations

import io
import importlib.util
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "drive.py"


def python_command(code: str) -> str:
    args = [sys.executable, "-c", code]
    return subprocess.list2cmdline(args) if os.name == "nt" else shlex.join(args)


PASS_COMMAND = python_command("raise SystemExit(0)")


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )


def initialize_git(root: Path) -> None:
    (root / ".gitignore").write_text(".stage/.runtime/\n", encoding="utf-8")
    git(root, "init", "-q")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "Stage Test")
    git(root, "commit", "--allow-empty", "-q", "-m", "base")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "seed")


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

    def test_audit_check_quotes_for_the_platform_shell(self):
        # The audit string is handed to a shell, and the two shells disagree about
        # single quotes: a POSIX shell strips them, cmd.exe passes them through. A
        # command quoted for one is broken on the other.
        drive = self.load_module()
        spaced = drive.audit_check(Path("/tmp/a b/repo"))
        plain = drive.audit_check(Path("/tmp/plain/repo"))

        if os.name == "nt":
            self.assertIn('"', spaced)
            self.assertNotIn("'", spaced)
            self.assertNotIn("'", plain)
        else:
            self.assertIn("'/tmp/a b/repo'", spaced)
            self.assertIn("--project-root /tmp/plain/repo", plain)

        # Whatever the platform, the joined string must parse back into the four
        # arguments the audit expects — a path that survives quoting but splits on
        # the way out is the bug this guards.
        parsed = (
            drive.shlex.split(spaced) if os.name != "nt" else spaced.split('" "')
        )
        self.assertEqual(4, len(parsed))

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

    def test_execute_passes_selected_work_item_environment(self):
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "executor-environment.json"
            variable_names = (
                "STAGE_WORK_ITEM",
                "STAGE_WORK_ITEM_PATH",
                "STAGE_PROJECT_ROOT",
            )
            executor = python_command(
                "import json, os; "
                "from pathlib import Path; "
                f"names = {variable_names!r}; "
                f"Path({str(marker)!r}).write_text("
                "json.dumps({name: os.environ[name] for name in names}), "
                "encoding='utf-8')"
            )
            tmp, root = self.make_project(executor=executor)
            with tmp:
                stage_root = root / ".stage"
                write_card(
                    stage_root,
                    "W-00000002",
                    parent="W-00000001",
                    acceptance=(PASS_COMMAND,),
                )

                result = self.run_cli(root, "--execute")

                self.assertEqual(
                    0, result.returncode, result.stdout + result.stderr
                )
                environment = json.loads(marker.read_text(encoding="utf-8"))
                self.assertEqual("W-00000002", environment["STAGE_WORK_ITEM"])
                self.assertEqual(
                    str(
                        (
                            stage_root
                            / "work/current/W-00000002.md"
                        ).resolve()
                    ),
                    environment["STAGE_WORK_ITEM_PATH"],
                )
                self.assertEqual(
                    str(root.resolve()), environment["STAGE_PROJECT_ROOT"]
                )

    def test_reviewer_git_diff_sees_executor_created_file_content(self):
        artifact = "executor-artifact.txt"
        executor = python_command(
            "from pathlib import Path; "
            f"Path({artifact!r}).write_text('executor artifact\\n', encoding='utf-8')"
        )
        reviewer = python_command(
            "import subprocess; "
            f"result = subprocess.run(['git', 'diff', 'HEAD~1', '--', {artifact!r}], "
            "capture_output=True, text=True); "
            "print(result.stdout); "
            "raise SystemExit("
            "0 if result.returncode == 0 and 'executor artifact' in result.stdout else 1"
            ")"
        )
        tmp, root = self.make_project(executor=executor, reviewer=reviewer)
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)

            result = self.run_cli(root, "--execute")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("executor artifact", result.stdout)
            self.assertEqual("", git(root, "diff", "--cached", "--name-only").stdout)
            self.assertIn(
                artifact,
                git(root, "ls-files", "--others", "--exclude-standard").stdout,
            )

    def test_failed_executor_restores_index_and_does_not_commit(self):
        executor = python_command(
            "import subprocess; "
            "from pathlib import Path; "
            "Path('failed-artifact.txt').write_text('partial\\n', encoding='utf-8'); "
            "subprocess.run(['git', 'add', 'failed-artifact.txt'], check=True); "
            "raise SystemExit(1)"
        )
        tmp, root = self.make_project(executor=executor)
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            (root / "human.txt").write_text("before\n", encoding="utf-8")
            initialize_git(root)
            (root / "human.txt").write_text("human staged\n", encoding="utf-8")
            git(root, "add", "human.txt")
            head_before = git(root, "rev-parse", "HEAD").stdout
            index_before = git(root, "diff", "--cached", "--binary").stdout

            result = self.run_cli(root, "--execute")

            self.assertNotEqual(0, result.returncode)
            self.assertEqual(head_before, git(root, "rev-parse", "HEAD").stdout)
            self.assertEqual(
                index_before, git(root, "diff", "--cached", "--binary").stdout
            )
            self.assertNotIn(
                "failed-artifact.txt",
                git(root, "diff", "--cached", "--name-only").stdout,
            )
            self.assertIn(
                "failed-artifact.txt",
                git(root, "ls-files", "--others", "--exclude-standard").stdout,
            )

    def test_reviewer_index_snapshot_failure_restores_index(self):
        executor = python_command(
            "import subprocess; "
            "from pathlib import Path; "
            "Path('executor-artifact.txt').write_text('partial\\n', encoding='utf-8'); "
            "subprocess.run(['git', 'add', 'executor-artifact.txt'], check=True)"
        )
        tmp, root = self.make_project(executor=executor)
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            (root / "human.txt").write_text("before\n", encoding="utf-8")
            initialize_git(root)
            (root / "human.txt").write_text("human staged\n", encoding="utf-8")
            git(root, "add", "human.txt")
            index_before = git(root, "diff", "--cached", "--binary").stdout
            drive = self.load_module()
            real_copyfile = drive.shutil.copyfile

            def fail_reviewer_snapshot(source, destination):
                if Path(destination).name == "review-index":
                    raise OSError("injected reviewer-index snapshot failure")
                return real_copyfile(source, destination)

            output = io.StringIO()
            argv = [
                str(SCRIPT),
                "--project-root",
                str(root),
                "--execute",
                "W-00000001",
            ]
            with (
                mock.patch.object(sys, "argv", argv),
                mock.patch.object(
                    drive.shutil,
                    "copyfile",
                    side_effect=fail_reviewer_snapshot,
                ),
                redirect_stdout(output),
            ):
                result = drive.main()

            self.assertNotEqual(0, result)
            self.assertIn(
                "cannot snapshot executor Git index: "
                "injected reviewer-index snapshot failure",
                output.getvalue(),
            )
            self.assertEqual(
                index_before, git(root, "diff", "--cached", "--binary").stdout
            )
            self.assertNotIn(
                "executor-artifact.txt",
                git(root, "diff", "--cached", "--name-only").stdout,
            )
            self.assertIn(
                "executor-artifact.txt",
                git(root, "ls-files", "--others", "--exclude-standard").stdout,
            )

    def test_git_untracked_paths_reports_git_failure_without_stderr(self):
        drive = self.load_module()
        failed = subprocess.CompletedProcess(
            args=["git", "ls-files"],
            returncode=1,
            stdout=b"",
            stderr=b"",
        )

        with mock.patch.object(drive.subprocess, "run", return_value=failed):
            paths, error = drive.git_untracked_paths(Path.cwd())

        self.assertEqual(set(), paths)
        self.assertEqual("git ls-files failed with exit code 1", error)

    def test_fingerprint_counts_changes_with_unborn_head(self):
        tmp, root = self.make_project()
        with tmp:
            (root / ".gitignore").write_text(
                ".stage/.runtime/\n", encoding="utf-8"
            )
            git(root, "init", "-q")
            git(root, "add", "-A")
            drive = self.load_module()
            baseline = drive.fingerprint(root, ["same acceptance"])

            (root / ".stage/settings.json").write_text(
                '{"schema_version": 4}\n', encoding="utf-8"
            )
            git(root, "add", ".stage/settings.json")
            changed = drive.fingerprint(root, ["same acceptance"])

        self.assertNotEqual(baseline, changed)

    def test_fingerprint_counts_untracked_and_staged_changes(self):
        tmp, root = self.make_project()
        with tmp:
            initialize_git(root)
            drive = self.load_module()
            baseline = drive.fingerprint(root, ["same acceptance"])

            (root / "untracked.txt").write_text("new\n", encoding="utf-8")
            untracked = drive.fingerprint(root, ["same acceptance"])
            (root / "untracked.txt").unlink()

            (root / ".stage/settings.json").write_text(
                '{"schema_version": 4}\n', encoding="utf-8"
            )
            git(root, "add", ".stage/settings.json")
            staged = drive.fingerprint(root, ["same acceptance"])

        self.assertNotEqual(baseline, untracked)
        self.assertNotEqual(baseline, staged)

    def test_new_file_only_is_progress_with_identical_acceptance_output(self):
        artifact = "progress.txt"
        executor = python_command(
            "from pathlib import Path; "
            f"Path({artifact!r}).write_text('progress\\n', encoding='utf-8')"
        )
        tmp, root = self.make_project(executor=executor)
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)
            drive = self.load_module()
            state_path = stage_root / ".runtime/driver/W-00000001.json"
            state_path.parent.mkdir(parents=True)
            state = drive.new_run_state("W-00000001", 1.0)
            state["iteration_count"] = 1
            state["items"]["W-00000002"] = {
                "attempt_count": 1,
                "last_fingerprint": drive.fingerprint(root, [""]),
            }
            drive.write_run_state(state_path, state)

            result = self.run_cli(root, "--execute")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertNotIn("NO-PROGRESS", result.stdout)
            self.assertEqual("progress\n", (root / artifact).read_text(encoding="utf-8"))

    def test_acceptance_created_file_is_not_in_reviewer_diff(self):
        executor_artifact = "executor-artifact.txt"
        acceptance_artifact = "acceptance-artifact.txt"
        executor = python_command(
            "from pathlib import Path; "
            f"Path({executor_artifact!r}).write_text("
            "'executor output\\n', encoding='utf-8')"
        )
        acceptance = python_command(
            "from pathlib import Path; "
            f"Path({acceptance_artifact!r}).write_text("
            "'acceptance output\\n', encoding='utf-8')"
        )
        reviewer = python_command(
            "import subprocess; "
            "executor_result = subprocess.run("
            f"['git', 'diff', 'HEAD~1', '--', {executor_artifact!r}], "
            "capture_output=True, text=True); "
            "acceptance_result = subprocess.run("
            f"['git', 'diff', 'HEAD~1', '--', {acceptance_artifact!r}], "
            "capture_output=True, text=True); "
            "print(executor_result.stdout); "
            "raise SystemExit("
            f"0 if {executor_artifact!r} in executor_result.stdout "
            "and not acceptance_result.stdout else 1)"
        )
        tmp, root = self.make_project(executor=executor, reviewer=reviewer)
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(acceptance,),
            )
            initialize_git(root)

            result = self.run_cli(root, "--execute")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(executor_artifact, result.stdout)

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
