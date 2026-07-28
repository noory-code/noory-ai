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


def reporting_python_command(code: str, changed_paths: list[str]) -> str:
    report = (
        "import json, os; from pathlib import Path; "
        "log = Path(os.environ['STAGE_WORK_LOG_PATH']); "
        "log.write_text(log.read_text(encoding='utf-8') + "
        "'\\n### Executor report\\n"
        "What changed: test executor changed its declared paths\\n"
        "Why: exercise the driver contract\\n"
        "Changed paths (JSON):\\n' + "
        f"json.dumps({changed_paths!r}) + "
        "'\\nReview request: review every success criterion\\n', encoding='utf-8')"
    )
    return python_command(f"{code}; {report}")


def approving_reviewer_command(code: str = "") -> str:
    setup = ""
    if code:
        setup = (
            "try:\n"
            f"    exec({code!r})\n"
            "except SystemExit as exc:\n"
            "    if exc.code not in (None, 0):\n"
            "        raise\n"
        )
    return python_command(
        setup
        + "import os\n"
        "from pathlib import Path\n"
        "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
        "report = ('\\n### Reviewer report\\n"
        "CRITERIA VERDICT:\\n"
        "- criterion: PASS - test reviewer inspected the inputs\\n"
        "APPROVED\\n"
        "OUT-OF-CRITERIA OBSERVATIONS:\\n- None\\n')\n"
        "log.write_text(log.read_text(encoding='utf-8') + report, encoding='utf-8')\n"
        "print('APPROVED')"
    )


PASS_COMMAND = python_command("raise SystemExit(0)")
APPROVING_REVIEWER = approving_reviewer_command()


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
        reviewer: str = APPROVING_REVIEWER,
        limits: object = None,
        reapers: object = None,
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
        if reapers is not None:
            settings["reapers"] = reapers
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

    def test_shell_command_joins_for_posix(self):
        # A POSIX shell strips single quotes, so shlex is the joiner there and the
        # string must split back into exactly the arguments that went in.
        drive = self.load_module()
        args = ["/usr/bin/python3", "/a b/audit.py", "--project-root", "/a b/repo"]

        joined = drive.shell_command(args, os_name="posix")

        self.assertIn("'/a b/repo'", joined)
        self.assertEqual(args, shlex.split(joined))

    def test_shell_command_joins_for_windows(self):
        # cmd.exe does NOT strip single quotes, so quoting the POSIX way would hand
        # it a program name that literally starts with a quote. This branch runs on
        # every platform on purpose — there is no Windows runner to catch it.
        drive = self.load_module()
        args = [
            r"C:\Python\python.exe",
            r"C:\p\audit.py",
            "--project-root",
            r"C:\a b\repo",
        ]

        joined = drive.shell_command(args, os_name="nt")

        self.assertNotIn("'", joined)
        # Only the argument containing a space is quoted; the rest stay bare.
        self.assertIn(r'"C:\a b\repo"', joined)
        self.assertTrue(joined.startswith(r"C:\Python\python.exe "))

    def test_windows_audit_quotes_cmd_metacharacters_in_project_path(self):
        drive = self.load_module()
        project_root = Path(r"C:\repo&one^two|three<four>five")

        with mock.patch.object(drive.os, "name", "nt"):
            command = drive.audit_check(project_root)

        self.assertNotIn("'", command)
        self.assertIn(
            f'--project-root "{project_root}"',
            command,
        )

    def test_windows_shell_command_doubles_trailing_backslashes_when_forcing_quotes(self):
        drive = self.load_module()

        command = drive.shell_command(
            ["audit.exe", "C:\\repo&trailing\\"],
            os_name="nt",
        )

        self.assertEqual('audit.exe "C:\\repo&trailing\\\\"', command)

    def test_audit_check_survives_a_project_path_with_a_space(self):
        # The assertion compares against `str(project_root)`, not a POSIX literal:
        # on Windows the same Path renders with backslashes, and hard-coding the
        # slash form would fail there for a reason that has nothing to do with the
        # quoting this guards.
        drive = self.load_module()
        project_root = Path("/tmp/a b/repo")

        command = drive.audit_check(project_root, os_name="posix")

        parsed = shlex.split(command)
        self.assertEqual(4, len(parsed))
        self.assertEqual("--project-root", parsed[2])
        self.assertEqual(str(project_root), parsed[3])

    def test_supervised_selection_descends_from_epic_to_action(self):
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000002",
                parent="W-00000001",
            )
            write_card(
                stage_root,
                "W-00000003",
                parent="W-00000002",
                acceptance=(PASS_COMMAND,),
            )
            drive = self.load_module()

            selected = drive.select_next_ready_leaf(
                "W-00000001", drive.load_all_work_items(stage_root)
            )

        self.assertIsNotNone(selected)
        self.assertEqual("W-00000003", selected.item_id)

    def test_executor_environment_lists_ancestor_cards_in_root_first_order(self):
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(stage_root, "W-00000002", parent="W-00000001")
            write_card(stage_root, "W-00000003", parent="W-00000002")
            drive = self.load_module()
            items = drive.load_all_work_items(stage_root)
            action = next(item for item in items if item.item_id == "W-00000003")

            environment = drive.executor_environment(
                action,
                root,
                stage_root / ".runtime/driver/logs/W-00000003.md",
                items=items,
            )

        self.assertEqual(
            [
                str((stage_root / "work/current/W-00000001.md").resolve()),
                str((stage_root / "work/current/W-00000002.md").resolve()),
            ],
            json.loads(environment["STAGE_WORK_ITEM_ANCESTOR_PATHS"]),
        )

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

    def test_selects_target_when_it_is_a_runnable_leaf(self):
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            drive = self.load_module()

            selected = drive.select_next_ready_leaf(
                "W-00000001", drive.load_all_work_items(stage_root)
            )

        self.assertIsNotNone(selected)
        self.assertEqual("W-00000001", selected.item_id)

    def test_unfinished_child_prevents_selecting_target_directly(self):
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000001",
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

    def test_unrunnable_unfinished_child_still_hides_target(self):
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            write_card(
                stage_root,
                "W-00000002",
                parent="W-00000001",
            )
            drive = self.load_module()

            selected = drive.select_next_ready_leaf(
                "W-00000001", drive.load_all_work_items(stage_root)
            )

        self.assertIsNone(selected)

    def test_dry_run_accepts_runnable_target_without_wrapper_parent(self):
        tmp, root = self.make_project()
        with tmp:
            write_card(
                root / ".stage",
                "W-00000001",
                acceptance=(PASS_COMMAND,),
            )

            result = self.run_cli(root)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Mode: dry-run", result.stdout)
        self.assertIn("Selected item: W-00000001", result.stdout)

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
        self.assertIn(f"Independent reviewer: {APPROVING_REVIEWER}", result.stdout)
        self.assertEqual(before, after)
        self.assertFalse(marker.exists())

    def test_execute_runs_fakes_and_reports_pass(self):
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "executor-ran"
            tmp, root = self.make_project(
                executor=reporting_python_command(
                    "from pathlib import Path; "
                    f"Path({str(marker)!r}).touch(); "
                    "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                    ["executor-work.txt"],
                )
            )
            with tmp:
                write_card(
                    root / ".stage",
                    "W-00000002",
                    parent="W-00000001",
                    acceptance=(PASS_COMMAND,),
                )
                initialize_git(root)

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

    def test_execute_reaps_executor_and_reviewer_turns_on_success(self):
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker_root = Path(marker_tmp)
            executor_reaped = marker_root / "executor-reaped"
            reviewer_reaped = marker_root / "reviewer-reaped"
            tmp, root = self.make_project(
                executor=reporting_python_command(
                    "from pathlib import Path; "
                    "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                    ["executor-work.txt"],
                ),
                reapers={
                    "codex": python_command(
                        "import os; from pathlib import Path; "
                        f"Path({str(executor_reaped)!r}).write_text("
                        "os.environ['STAGE_TURN_ROLE'] + '\\n' + "
                        "os.environ['STAGE_WORK_ITEM_PATH'], encoding='utf-8')"
                    ),
                    "claude": python_command(
                        "import os; from pathlib import Path; "
                        f"Path({str(reviewer_reaped)!r}).write_text("
                        "os.environ['STAGE_TURN_ROLE'] + '\\n' + "
                        "os.environ['STAGE_WORK_ITEM_PATH'], encoding='utf-8')"
                    ),
                },
            )
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
            expected_path = str(
                (root / ".stage/work/current/W-00000002.md").resolve()
            )
            self.assertEqual(
                f"executor\n{expected_path}",
                executor_reaped.read_text(encoding="utf-8"),
            )
            self.assertEqual(
                f"reviewer\n{expected_path}",
                reviewer_reaped.read_text(encoding="utf-8"),
            )

    def test_execute_warns_and_logs_when_executor_reaping_fails(self):
        tmp, root = self.make_project(
            executor=python_command("raise SystemExit(7)"),
            reapers={
                "codex": python_command(
                    "print('reap failure sentinel'); raise SystemExit(4)"
                ),
                "claude": PASS_COMMAND,
            },
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)

            result = self.run_cli(root, "--execute")
            log = (
                root / ".stage/.runtime/driver/logs/W-00000002.md"
            ).read_text(encoding="utf-8")

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "WARNING: reapers.codex failed after executor turn; jobs may remain",
            result.stdout,
        )
        self.assertIn(
            "WARNING: reapers.codex failed after executor turn; jobs may remain",
            log,
        )
        self.assertIn("reap failure sentinel", log)

    def test_execute_missing_reaper_warns_without_changing_success(self):
        tmp, root = self.make_project(
            executor=reporting_python_command(
                "from pathlib import Path; "
                "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                ["executor-work.txt"],
            ),
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)

            result = self.run_cli(root, "--execute")
            log = (
                root / ".stage/.runtime/driver/logs/W-00000002.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            "WARNING: reapers.codex is not configured after executor turn; "
            "jobs may remain",
            result.stdout,
        )
        self.assertIn(
            "WARNING: reapers.claude is not configured after reviewer turn; "
            "jobs may remain",
            result.stdout,
        )
        self.assertIn("reapers.codex is not configured", log)
        self.assertIn("reapers.claude is not configured", log)

    def test_execute_declared_nothing_to_reap_is_silent(self):
        tmp, root = self.make_project(
            executor=reporting_python_command(
                "from pathlib import Path; "
                "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                ["executor-work.txt"],
            ),
            reapers={"codex": None, "claude": None},
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)

            result = self.run_cli(root, "--execute")
            log = (
                root / ".stage/.runtime/driver/logs/W-00000002.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("WARNING: reapers.", result.stdout)
        self.assertNotIn("Driver warning", log)

    def test_execute_rejects_successful_executor_that_leaves_repository_unchanged(self):
        tmp, root = self.make_project(executor=PASS_COMMAND)
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )

            result = self.run_cli(root, "--execute")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("executor left repository state unchanged", result.stdout)
        self.assertIn("close_work.py", result.stdout)
        self.assertNotIn("Acceptance result:", result.stdout)
        self.assertNotIn("Independent reviewer result:", result.stdout)

    def test_execute_passes_in_unborn_repository_without_an_index(self):
        tmp, root = self.make_project(
            executor=reporting_python_command(
                "from pathlib import Path; "
                "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                ["executor-work.txt"],
            )
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            git(root, "init", "-q")
            index_path = (
                root
                / git(
                    root,
                    "rev-parse",
                    "--git-path",
                    "index",
                ).stdout.strip()
            )
            self.assertFalse(index_path.exists())

            result = self.run_cli(root, "--execute")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn(
                "verification+judge passed → ready to commit + close_work",
                result.stdout,
            )
            self.assertFalse(index_path.exists())

    def test_execute_passes_when_head_exists_but_index_is_missing(self):
        tmp, root = self.make_project(
            executor=reporting_python_command(
                "from pathlib import Path; "
                "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                ["executor-work.txt"],
            )
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)
            index_path = (
                root
                / git(
                    root,
                    "rev-parse",
                    "--git-path",
                    "index",
                ).stdout.strip()
            )
            index_path.unlink()
            self.assertTrue(git(root, "rev-parse", "--verify", "HEAD").stdout)
            self.assertFalse(index_path.exists())

            result = self.run_cli(root, "--execute")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn(
                "verification+judge passed → ready to commit + close_work",
                result.stdout,
            )
            self.assertFalse(index_path.exists())

    def test_execute_passes_selected_work_item_environment(self):
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "executor-environment.json"
            variable_names = (
                "STAGE_WORK_ITEM",
                "STAGE_WORK_ITEM_PATH",
                "STAGE_PROJECT_ROOT",
                "GIT_INDEX_FILE",
            )
            executor = reporting_python_command(
                "import json, os; "
                "from pathlib import Path; "
                f"names = {variable_names!r}; "
                f"Path({str(marker)!r}).write_text("
                "json.dumps({name: os.environ[name] for name in names}), "
                "encoding='utf-8'); "
                "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                ["executor-work.txt"],
            )
            tmp, root = self.make_project(executor=executor)
            with tmp:
                stage_root = root / ".stage"
                write_card(
                    stage_root,
                    "W-00000002",
                    parent="W-00000001",
                    acceptance=(
                        python_command(
                            "import os; "
                            "raise SystemExit("
                            "0 if 'GIT_INDEX_FILE' not in os.environ else 1)"
                        ),
                    ),
                )
                initialize_git(root)

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
                self.assertEqual(
                    "executor-index",
                    Path(environment["GIT_INDEX_FILE"]).name,
                )
                self.assertNotEqual(
                    str((root / ".git/index").resolve()),
                    environment["GIT_INDEX_FILE"],
                )

    def test_execute_passes_selected_work_item_path_to_reviewer(self):
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "reviewer-environment.json"
            reviewer = approving_reviewer_command(
                "import json, os; "
                "from pathlib import Path; "
                f"Path({str(marker)!r}).write_text("
                "json.dumps({'STAGE_WORK_ITEM_PATH': os.environ['STAGE_WORK_ITEM_PATH']}), "
                "encoding='utf-8')"
            )
            executor = reporting_python_command(
                "from pathlib import Path; "
                "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                ["executor-work.txt"],
            )
            tmp, root = self.make_project(executor=executor, reviewer=reviewer)
            with tmp:
                stage_root = root / ".stage"
                write_card(
                    stage_root,
                    "W-00000002",
                    parent="W-00000001",
                    acceptance=(PASS_COMMAND,),
                )
                initialize_git(root)

                result = self.run_cli(root, "--execute")

                self.assertEqual(
                    0, result.returncode, result.stdout + result.stderr
                )
                environment = json.loads(marker.read_text(encoding="utf-8"))
                self.assertEqual(
                    str(
                        (
                            stage_root
                            / "work/current/W-00000002.md"
                        ).resolve()
                    ),
                    environment["STAGE_WORK_ITEM_PATH"],
                )

    def test_reviewer_receives_driver_observed_paths_without_executor_index(self):
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "reviewer-input.json"
            reviewer = approving_reviewer_command(
                "import json, os; "
                "from pathlib import Path; "
                "changed_paths_file = Path(os.environ['STAGE_CHANGED_PATHS_FILE']); "
                f"Path({str(marker)!r}).write_text("
                "json.dumps({"
                "'changed_paths': json.loads(changed_paths_file.read_text(encoding='utf-8')), "
                "'git_index_file': os.environ.get('GIT_INDEX_FILE')"
                "}), encoding='utf-8')"
            )
            executor = reporting_python_command(
                "import subprocess; "
                "from pathlib import Path; "
                "subprocess.run(['git', 'read-tree', '--empty'], check=True); "
                "Path('tracked.txt').write_text('after\\n', encoding='utf-8'); "
                "Path('new.txt').write_text('new\\n', encoding='utf-8')",
                ["new.txt", "tracked.txt"],
            )
            tmp, root = self.make_project(executor=executor, reviewer=reviewer)
            with tmp:
                write_card(
                    root / ".stage",
                    "W-00000002",
                    parent="W-00000001",
                    acceptance=(PASS_COMMAND,),
                )
                (root / "tracked.txt").write_text("before\n", encoding="utf-8")
                initialize_git(root)

                result = self.run_cli(root, "--execute")

                self.assertEqual(
                    0, result.returncode, result.stdout + result.stderr
                )
                reviewer_input = json.loads(marker.read_text(encoding="utf-8"))
                self.assertEqual(
                    ["new.txt", "tracked.txt"],
                    reviewer_input["changed_paths"],
                )
                self.assertIsNone(reviewer_input["git_index_file"])

    def test_executor_staging_never_changes_the_real_index(self):
        tmp, root = self.make_project()
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)
            index_path = (
                root
                / git(
                    root,
                    "rev-parse",
                    "--git-path",
                    "index",
                ).stdout.strip()
            )
            index_before = index_path.read_bytes()
            executor = reporting_python_command(
                "import subprocess; "
                "from pathlib import Path; "
                "Path('executor-artifact.txt').write_text("
                "'executor artifact\\n', encoding='utf-8'); "
                "subprocess.run(['git', 'add', 'executor-artifact.txt'], check=True); "
                f"Path('index-during-executor').write_bytes(Path({str(index_path)!r}).read_bytes())",
                ["executor-artifact.txt", "index-during-executor"],
            )
            settings_path = root / ".stage/settings.json"
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            settings["executors"]["codex"] = executor
            settings_path.write_text(json.dumps(settings), encoding="utf-8")

            result = self.run_cli(root, "--execute")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual(
                index_before,
                (root / "index-during-executor").read_bytes(),
            )
            self.assertEqual(index_before, index_path.read_bytes())
            self.assertNotIn(
                "executor-artifact.txt",
                git(root, "diff", "--cached", "--name-only").stdout,
            )

    def test_human_index_update_during_executor_is_preserved(self):
        tmp, root = self.make_project()
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            (root / "human.txt").write_text("before\n", encoding="utf-8")
            initialize_git(root)
            index_path = (
                root
                / git(
                    root,
                    "rev-parse",
                    "--git-path",
                    "index",
                ).stdout.strip()
            )
            (root / "human.txt").write_text("human staged\n", encoding="utf-8")
            executor = reporting_python_command(
                "import os, subprocess; "
                "from pathlib import Path; "
                "human_env = os.environ.copy(); "
                f"human_env['GIT_INDEX_FILE'] = {str(index_path)!r}; "
                "subprocess.run(['git', 'add', 'human.txt'], check=True, env=human_env); "
                "Path('executor-artifact.txt').write_text("
                "'executor artifact\\n', encoding='utf-8'); "
                "subprocess.run(['git', 'add', 'executor-artifact.txt'], check=True)",
                ["executor-artifact.txt", "human.txt"],
            )
            settings_path = root / ".stage/settings.json"
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            settings["executors"]["codex"] = executor
            settings_path.write_text(json.dumps(settings), encoding="utf-8")

            result = self.run_cli(root, "--execute")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual(
                "human.txt\n",
                git(root, "diff", "--cached", "--name-only").stdout,
            )
            self.assertEqual(
                "human staged\n",
                git(root, "show", ":human.txt").stdout,
            )
            self.assertIn(
                "executor-artifact.txt",
                git(root, "ls-files", "--others", "--exclude-standard").stdout,
            )

    def test_reviewer_opens_executor_created_file_from_observed_path_list(self):
        artifact = "executor-artifact.txt"
        executor = reporting_python_command(
            "from pathlib import Path; "
            f"Path({artifact!r}).write_text('executor artifact\\n', encoding='utf-8')",
            [artifact],
        )
        reviewer = approving_reviewer_command(
            "import json, os; "
            "from pathlib import Path; "
            "paths = json.loads("
            "Path(os.environ['STAGE_CHANGED_PATHS_FILE']).read_text(encoding='utf-8')); "
            f"content = Path({artifact!r}).read_text(encoding='utf-8'); "
            "print(content); "
            "raise SystemExit("
            f"0 if paths == [{artifact!r}] and content == 'executor artifact\\n' else 1"
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

    def test_failed_executor_uses_disposable_index_and_does_not_commit(self):
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

    def test_executor_index_copy_failure_leaves_real_index_unchanged(self):
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

            def fail_executor_index_copy(source, destination):
                if Path(destination).name == "executor-index":
                    raise OSError("injected executor-index copy failure")
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
                    side_effect=fail_executor_index_copy,
                ),
                redirect_stdout(output),
            ):
                result = drive.main()

            self.assertNotEqual(0, result)
            self.assertIn(
                "cannot prepare disposable Git index for executor: "
                "injected executor-index copy failure",
                output.getvalue(),
            )
            self.assertEqual(
                index_before, git(root, "diff", "--cached", "--binary").stdout
            )
            self.assertNotIn(
                "executor-artifact.txt",
                git(root, "diff", "--cached", "--name-only").stdout,
            )
            self.assertFalse((root / "executor-artifact.txt").exists())

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

    def test_git_diff_fails_closed_when_git_cannot_start(self):
        drive = self.load_module()
        index_path = subprocess.CompletedProcess(
            args=["git", "rev-parse", "--git-path", "index"],
            returncode=0,
            stdout=".git/index\n",
            stderr="",
        )

        with (
            mock.patch.object(
                drive.subprocess,
                "run",
                side_effect=[
                    index_path,
                    OSError("injected git diff launch failure"),
                ],
            ),
            self.assertRaisesRegex(
                RuntimeError,
                "injected git diff launch failure",
            ),
        ):
            drive.git_diff(Path.cwd())

    def test_git_diff_fails_closed_when_unborn_diff_fails(self):
        drive = self.load_module()
        index_path = subprocess.CompletedProcess(
            args=["git", "rev-parse", "--git-path", "index"],
            returncode=0,
            stdout=".git/index\n",
            stderr="",
        )
        missing_head = subprocess.CompletedProcess(
            args=["git", "diff", "HEAD"],
            returncode=128,
            stdout="",
            stderr="fatal: bad revision 'HEAD'",
        )
        unborn_head = subprocess.CompletedProcess(
            args=["git", "rev-parse", "--verify", "--quiet", "HEAD"],
            returncode=1,
            stdout="",
            stderr="",
        )
        failed_unborn_diff = subprocess.CompletedProcess(
            args=["git", "diff", "--cached"],
            returncode=2,
            stdout="",
            stderr="injected unborn diff failure",
        )

        with (
            mock.patch.object(
                drive.subprocess,
                "run",
                side_effect=[
                    index_path,
                    missing_head,
                    unborn_head,
                    failed_unborn_diff,
                ],
            ),
            self.assertRaisesRegex(
                RuntimeError,
                "injected unborn diff failure",
            ),
        ):
            drive.git_diff(Path.cwd())

    def test_progress_fingerprint_fails_closed_on_untracked_enumeration_error(self):
        tmp, root = self.make_project(
            executor=python_command(
                "from pathlib import Path; "
                "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')"
            )
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)
            drive = self.load_module()
            output = io.StringIO()
            argv = [
                str(SCRIPT),
                "--project-root",
                str(root),
                "--execute",
                "W-00000001",
            ]
            enumerations = [
                (set(), ""),
                (set(), ""),
                ({"executor-work.txt"}, ""),
                ({"executor-work.txt"}, ""),
                (set(), "injected progress enumeration failure"),
            ]

            with (
                mock.patch.object(sys, "argv", argv),
                mock.patch.object(
                    drive,
                    "git_untracked_paths",
                    side_effect=enumerations,
                ),
                redirect_stdout(output),
            ):
                result = drive.main()

            self.assertNotEqual(0, result)
            self.assertIn(
                "cannot inspect changes for progress: "
                "injected progress enumeration failure",
                output.getvalue(),
            )
            self.assertFalse(
                (root / ".stage/.runtime/driver/W-00000001.json").exists()
            )

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
        executor = reporting_python_command(
            "from pathlib import Path; "
            f"Path({artifact!r}).write_text('progress\\n', encoding='utf-8')",
            [artifact],
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

    def test_acceptance_created_file_is_not_in_reviewer_path_list(self):
        executor_artifact = "executor-artifact.txt"
        acceptance_artifact = "acceptance-artifact.txt"
        executor = reporting_python_command(
            "from pathlib import Path; "
            f"Path({executor_artifact!r}).write_text("
            "'executor output\\n', encoding='utf-8')",
            [executor_artifact],
        )
        acceptance = python_command(
            "from pathlib import Path; "
            f"Path({acceptance_artifact!r}).write_text("
            "'acceptance output\\n', encoding='utf-8')"
        )
        reviewer = approving_reviewer_command(
            "import json, os; "
            "from pathlib import Path; "
            "paths = json.loads("
            "Path(os.environ['STAGE_CHANGED_PATHS_FILE']).read_text(encoding='utf-8')); "
            "print(paths); "
            "raise SystemExit("
            f"0 if {executor_artifact!r} in paths "
            f"and {acceptance_artifact!r} not in paths else 1)"
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

    def test_executor_must_append_a_work_log_report_before_acceptance(self):
        acceptance_marker = "acceptance-ran.txt"
        tmp, root = self.make_project(
            executor=python_command(
                "from pathlib import Path; "
                "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')"
            ),
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(
                    python_command(
                        "from pathlib import Path; "
                        f"Path({acceptance_marker!r}).write_text('ran', encoding='utf-8')"
                    ),
                ),
            )
            initialize_git(root)
            result = self.run_cli(root, "--execute")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("executor did not append a work log report", result.stdout)
        self.assertFalse((root / acceptance_marker).exists())
        self.assertNotIn("Independent reviewer result:", result.stdout)

    def test_executor_claim_must_match_driver_observed_paths_before_review(self):
        executor = reporting_python_command(
            "from pathlib import Path; "
            "Path('actual.txt').write_text('done\\n', encoding='utf-8')",
            ["claimed.txt"],
        )
        tmp, root = self.make_project(executor=executor)
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)
            result = self.run_cli(root, "--execute")

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "executor claimed changed paths do not match driver observation",
            result.stdout,
        )
        self.assertIn("actual.txt", result.stdout)
        self.assertIn("claimed.txt", result.stdout)
        self.assertNotIn("Acceptance result:", result.stdout)
        self.assertNotIn("Independent reviewer result:", result.stdout)

    def test_executor_and_reviewer_share_one_work_log(self):
        executor = reporting_python_command(
            "from pathlib import Path; "
            "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
            ["executor-work.txt"],
        )
        reviewer = approving_reviewer_command(
            "import os; from pathlib import Path; "
            "log = Path(os.environ['STAGE_WORK_LOG_PATH']); "
            "assert 'executor-work.txt' in log.read_text(encoding='utf-8')"
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
            log = (
                root / ".stage/.runtime/driver/logs/W-00000002.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("### Executor report", log)
        self.assertIn("### Reviewer report", log)
        self.assertIn("CRITERIA VERDICT:", log)
        self.assertIn("APPROVED", log)
        self.assertIn("## 책임 경계", log)
        self.assertIn("작업 카드는 지속되는 수명 주기 상태", log)

    def test_reviewer_must_append_criterion_verdicts_to_work_log(self):
        executor = reporting_python_command(
            "from pathlib import Path; "
            "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
            ["executor-work.txt"],
        )
        reviewer = python_command(
            "print('CRITERIA VERDICT:\\n"
            "- criterion: PASS - stdout is not the shared record\\n"
            "APPROVED\\n"
            "OUT-OF-CRITERIA OBSERVATIONS:\\n- None')"
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

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "reviewer did not append criterion verdicts to the work log",
            result.stdout,
        )

    def test_reviewer_block_recommends_escalation(self):
        with tempfile.TemporaryDirectory() as marker_tmp:
            reviewer_reaped = Path(marker_tmp) / "reviewer-reaped"
            tmp, root = self.make_project(
                executor=reporting_python_command(
                    "from pathlib import Path; "
                    "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                    ["executor-work.txt"],
                ),
                reviewer=python_command("print('BLOCK: no'); raise SystemExit(1)"),
                reapers={
                    "codex": PASS_COMMAND,
                    "claude": python_command(
                        "from pathlib import Path; "
                        f"Path({str(reviewer_reaped)!r}).touch()"
                    ),
                },
            )
            with tmp:
                write_card(
                    root / ".stage",
                    "W-00000002",
                    parent="W-00000001",
                    acceptance=(PASS_COMMAND,),
                )
                initialize_git(root)

                result = self.run_cli(root, "--execute")

            self.assertNotEqual(0, result.returncode)
            self.assertIn("independent reviewer BLOCK", result.stdout)
            self.assertIn("→ escalate_work", result.stdout)
            self.assertTrue(reviewer_reaped.exists())

    def test_reviewer_block_output_is_appended_to_shared_work_log(self):
        tmp, root = self.make_project(
            executor=reporting_python_command(
                "from pathlib import Path; "
                "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                ["executor-work.txt"],
            ),
            reviewer=python_command(
                "print('BLOCK: reviewer failure sentinel'); raise SystemExit(9)"
            ),
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)

            result = self.run_cli(root, "--execute")
            log = (
                root / ".stage/.runtime/driver/logs/W-00000002.md"
            ).read_text(encoding="utf-8")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("### Driver failure", log)
        self.assertIn("Role: reviewer", log)
        self.assertIn("Reason: independent reviewer BLOCK verdict", log)
        self.assertIn("reviewer failure sentinel", log)
        self.assertIn("[exit 9]", log)

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
        tmp, root = self.make_project(
            executor=reporting_python_command(
                "from pathlib import Path; "
                "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                ["executor-work.txt"],
            )
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)

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
        with tempfile.TemporaryDirectory() as marker_tmp:
            reap_count = Path(marker_tmp) / "reap-count"
            append_reap = python_command(
                "from pathlib import Path; "
                f"path = Path({str(reap_count)!r}); "
                "path.write_text(path.read_text(encoding='utf-8') + 'x' "
                "if path.exists() else 'x', encoding='utf-8')"
            )
            tmp, root = self.make_project(
                executor=reporting_python_command(
                    "from pathlib import Path; "
                    "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                    ["executor-work.txt"],
                ),
                limits=limits,
                reapers={"codex": append_reap, "claude": PASS_COMMAND},
            )
            with tmp:
                write_card(
                    root / ".stage",
                    "W-00000002",
                    parent="W-00000001",
                    acceptance=(PASS_COMMAND,),
                )
                initialize_git(root)

                first = self.run_cli(root, "--execute")
                second = self.run_cli(root, "--execute")
                state = json.loads(
                    (
                        root / ".stage/.runtime/driver/W-00000001.json"
                    ).read_text(encoding="utf-8")
                )

            self.assertEqual(0, first.returncode, first.stdout + first.stderr)
            self.assertNotEqual(0, second.returncode)
            self.assertIn("per-item attempt cap reached", second.stdout)
            self.assertIn("→ escalate_work", second.stdout)
            self.assertEqual("xx", reap_count.read_text(encoding="utf-8"))
            self.assertEqual(1, state["iteration_count"])
            self.assertEqual(
                1, state["items"]["W-00000002"]["attempt_count"]
            )


if __name__ == "__main__":
    unittest.main()
