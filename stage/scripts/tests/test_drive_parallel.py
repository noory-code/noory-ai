from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "drive_parallel.py"
HOOKS = SCRIPT.parent.parent / "hooks"


def load_module():
    spec = importlib.util.spec_from_file_location("stage_drive_parallel", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def git(root: Path, *args: str) -> str:
    environment = os.environ.copy()
    environment.pop("GIT_INDEX_FILE", None)
    return subprocess.run(
        ["git", *args],
        cwd=str(root),
        check=True,
        capture_output=True,
        env=environment,
        text=True,
    ).stdout.strip()


class DriveParallelTest(unittest.TestCase):
    def make_repository(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "project"
        root.mkdir()
        git(root, "init", "-q")
        git(root, "config", "user.email", "t@example.com")
        git(root, "config", "user.name", "Tester")
        (root / "seed.txt").write_text("seed", encoding="utf-8")
        git(root, "add", "seed.txt")
        git(root, "commit", "-q", "-m", "seed")
        return tmp, root

    def make_fake_driver(self, directory: Path, expected_count: int) -> Path:
        driver = directory / "fake_drive.py"
        driver.write_text(
            textwrap.dedent(
                f"""\
                import argparse
                import subprocess
                import time
                from pathlib import Path

                parser = argparse.ArgumentParser()
                parser.add_argument("--project-root", required=True)
                parser.add_argument("--execute", action="store_true")
                parser.add_argument("target")
                args = parser.parse_args()
                root = Path(args.project_root).resolve()
                assert Path.cwd().resolve() == root
                assert args.execute
                gate = root.parent / "started"
                gate.mkdir(exist_ok=True)
                (gate / args.target).write_text(str(root), encoding="utf-8")
                deadline = time.monotonic() + 5
                while len(list(gate.iterdir())) < {expected_count}:
                    if time.monotonic() >= deadline:
                        raise SystemExit("drivers did not overlap")
                    time.sleep(0.01)
                branch = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=root,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                print(f"{{args.target}} ran in {{root}} on {{branch}}")
                """
            ),
            encoding="utf-8",
        )
        return driver

    def add_current_cards(
        self,
        root: Path,
        targets: list[str],
        *,
        scopes: dict[str, str] | None = None,
    ) -> None:
        for target in targets:
            card_dir = root / ".stage/work/current" / target
            card_dir.mkdir(parents=True, exist_ok=True)
            (card_dir / "_story.md").write_text(
                (
                    "---\n"
                    f"id: {target}\n"
                    f"scope: {(scopes or {}).get(target, '')}\n"
                    "---\n\n"
                    f"# {target} test card\n"
                ),
                encoding="utf-8",
            )
        git(root, "add", ".stage")
        git(root, "commit", "-q", "-m", "add current cards")

    def add_current_story_with_action(
        self,
        root: Path,
        story_id: str,
        action_id: str,
        *,
        story_scope: str,
        action_scope: str,
    ) -> None:
        story_dir = root / ".stage/work/current" / story_id
        story_dir.mkdir(parents=True, exist_ok=True)
        (story_dir / "_story.md").write_text(
            (
                "---\n"
                f"id: {story_id}\n"
                f"scope: {story_scope}\n"
                "---\n\n"
                f"# {story_id} test story\n"
            ),
            encoding="utf-8",
        )
        (story_dir / f"{action_id}.md").write_text(
            (
                "---\n"
                f"id: {action_id}\n"
                f"scope: {action_scope}\n"
                "---\n\n"
                f"# {action_id} test action\n"
            ),
            encoding="utf-8",
        )

    def add_stage_probe(self, root: Path, targets: list[str]) -> None:
        shutil.copytree(HOOKS, root / "stage/hooks")
        settings = {
            "schema_version": 5,
            "governance": {"exclude_paths": [], "exclude_extensions": []},
            "extra_write_tools": [],
            "executors": {"codex": "python3 -B executor.py"},
            "reapers": {"codex": None, "claude": None},
            "review": {
                "reviewers": {
                    "codex": "python3 reviewer.py",
                    "claude": "python3 reviewer.py",
                }
            },
            "venue_routing": {"development": "codex"},
            "language": "en",
        }
        stage_root = root / ".stage"
        stage_root.mkdir()
        (stage_root / "settings.json").write_text(
            json.dumps(settings),
            encoding="utf-8",
        )
        for target in targets:
            card_dir = stage_root / "work/current" / target
            card_dir.mkdir(parents=True)
            (card_dir / "_story.md").write_text(
                (
                    "---\n"
                    f"id: {target}\n"
                    f"title: Probe {target}\n"
                    "kind: development\n"
                    "venue: codex\n"
                    "milestone:\n"
                    "priority: 1\n"
                    "autonomous: false\n"
                    "acceptance:\n"
                    f'  - "python3 accept.py {target}"\n'
                    "status: active\n"
                    "verification: pending\n"
                    "retrospective: pending\n"
                    "retrospective_ref:\n"
                    "promotion: pending\n"
                    "review: not_required\n"
                    f"scope: observed-{target}.json\n"
                    "promotes:\n"
                    "decision_refs:\n"
                    "---\n\n"
                    f"# {target} worktree probe\n\n"
                    "## Purpose\n\nVerify one real supervised driver round in a worktree.\n\n"
                    "## Success criteria\n\n"
                    "- Every observed root is this card worktree.\n"
                ),
                encoding="utf-8",
            )
        (root / ".gitignore").write_text(".stage/.runtime/\n", encoding="utf-8")
        (root / "executor.py").write_text(
            textwrap.dedent(
                """\
                import json
                import os
                import subprocess
                import sys
                from pathlib import Path

                target = os.environ["STAGE_WORK_ITEM"]
                root = Path(os.environ["STAGE_PROJECT_ROOT"]).resolve()
                assert Path(os.environ["CLAUDE_PROJECT_DIR"]).resolve() == root
                assert Path(os.environ["PROJECT_ROOT"]).resolve() == root
                observed_path = root / f"observed-{target}.json"
                payload = {
                    "tool_name": "Write",
                    "cwd": str(root),
                    "tool_input": {
                        "file_path": observed_path.name,
                        "content": "probe",
                    },
                }
                environment = os.environ.copy()
                hook = subprocess.run(
                    [sys.executable, "-B", "stage/hooks/stage_guard.py", "pre-tool-use"],
                    cwd=root,
                    input=json.dumps(payload),
                    capture_output=True,
                    text=True,
                    env=environment,
                )
                out_of_scope_payload = {
                    "tool_name": "Write",
                    "cwd": str(root),
                    "tool_input": {
                        "file_path": f"outside-{target}.txt",
                        "content": "must be denied",
                    },
                }
                denied_hook = subprocess.run(
                    [sys.executable, "-B", "stage/hooks/stage_guard.py", "pre-tool-use"],
                    cwd=root,
                    input=json.dumps(out_of_scope_payload),
                    capture_output=True,
                    text=True,
                    env=environment,
                )
                denied_output = json.loads(denied_hook.stdout)
                denied_decision = denied_output["hookSpecificOutput"]["permissionDecision"]
                git_root = subprocess.run(
                    ["git", "rev-parse", "--show-toplevel"],
                    cwd=root,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                observation = {
                    "cwd": str(Path.cwd().resolve()),
                    "project_root": str(root),
                    "claude_project_dir": os.environ["CLAUDE_PROJECT_DIR"],
                    "legacy_project_root": os.environ["PROJECT_ROOT"],
                    "work_item_path": os.environ["STAGE_WORK_ITEM_PATH"],
                    "hook_payload_root": payload["cwd"],
                    "hook_allowed": hook.returncode == 0 and not hook.stdout.strip(),
                    "hook_stdout": hook.stdout.strip(),
                    "hook_denied_out_of_scope": (
                        denied_hook.returncode == 0 and denied_decision == "deny"
                    ),
                    "hook_denial_stdout": denied_hook.stdout.strip(),
                    "git_root": git_root,
                }
                observed_path.write_text(
                    json.dumps(observation, sort_keys=True) + "\\n",
                    encoding="utf-8",
                )
                log = Path(os.environ["STAGE_WORK_LOG_PATH"])
                report = (
                    "\\n### Executor report\\n"
                    f"What changed: observed cwd={root}; project_root={root}; "
                    f"git_root={git_root}; work_item_path="
                    f"{os.environ['STAGE_WORK_ITEM_PATH']}; in-scope hook decision allow; "
                    f"out-of-scope hook decision {denied_decision}\\n"
                    "Why: prove the driver and Stage hook use the isolated worktree\\n"
                    "Changed paths (JSON):\\n"
                    + json.dumps([observed_path.name])
                    + "\\nReview request: verify every recorded root is this worktree\\n"
                )
                log.write_text(
                    log.read_text(encoding="utf-8") + report,
                    encoding="utf-8",
                )
                """
            ),
            encoding="utf-8",
        )
        (root / "accept.py").write_text(
            textwrap.dedent(
                """\
                import json
                import sys
                from pathlib import Path

                target = sys.argv[1]
                root = Path.cwd().resolve()
                observed = json.loads(
                    (root / f"observed-{target}.json").read_text(encoding="utf-8")
                )
                assert observed["cwd"] == str(root)
                assert observed["project_root"] == str(root)
                assert observed["claude_project_dir"] == str(root)
                assert observed["legacy_project_root"] == str(root)
                assert observed["hook_payload_root"] == str(root)
                assert observed["git_root"] == str(root)
                assert observed["hook_allowed"]
                assert observed["hook_denied_out_of_scope"]
                assert Path(observed["work_item_path"]).is_relative_to(root)
                print(f"acceptance observed isolated root {root}")
                """
            ),
            encoding="utf-8",
        )
        (root / "reviewer.py").write_text(
            textwrap.dedent(
                """\
                import json
                import os
                from pathlib import Path

                root = Path.cwd().resolve()
                changed = json.loads(
                    Path(os.environ["STAGE_CHANGED_PATHS_FILE"]).read_text(encoding="utf-8")
                )
                assert len(changed) == 1
                observed = json.loads((root / changed[0]).read_text(encoding="utf-8"))
                assert observed["project_root"] == str(root)
                assert observed["hook_allowed"]
                assert observed["hook_denied_out_of_scope"]
                report = (
                    "CRITERIA VERDICT:\\n"
                    f"- isolated worktree root: PASS - reviewer opened {changed[0]} in {root}\\n"
                    "APPROVED\\n"
                    "OUT-OF-CRITERIA OBSERVATIONS:\\n"
                    "- None."
                )
                log = Path(os.environ["STAGE_WORK_LOG_PATH"])
                log.write_text(
                    log.read_text(encoding="utf-8")
                    + "\\n### Reviewer report\\n"
                    + report
                    + "\\n",
                    encoding="utf-8",
                )
                Path(os.environ["STAGE_REVIEW_VERDICT_FILE"]).write_text(
                    json.dumps(
                        {
                            "criteria": [
                                {
                                    "criterion": "isolated worktree root",
                                    "verdict": "PASS",
                                    "reason": (
                                        f"reviewer opened {changed[0]} in {root}"
                                    ),
                                }
                            ],
                            "approved": True,
                        }
                    ),
                    encoding="utf-8",
                )
                print(report)
                """
            ),
            encoding="utf-8",
        )
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "stage probe fixture")

    def test_creates_card_named_worktrees_and_runs_drivers_concurrently(self) -> None:
        module = load_module()
        tmp, root = self.make_repository()
        temporary_root = Path(tmp.name)
        worktree_root = temporary_root / "worktrees"
        driver = self.make_fake_driver(temporary_root, expected_count=2)
        targets = ["W-00000001", "W-00000002"]
        self.add_current_cards(root, targets)

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = module.run_parallel(
                root,
                targets,
                worktree_root=worktree_root,
                driver_path=driver,
            )

        self.assertEqual(0, result)
        for target in targets:
            tree = worktree_root / target
            branch = f"stage/worktree/{target}"
            self.assertEqual(branch, git(tree, "branch", "--show-current"))
            self.assertIn(f"{target} ran in {tree.resolve()} on {branch}", output.getvalue())
            self.assertIn(f"Merge branch: {branch}", output.getvalue())

    def test_creation_failure_cleans_every_tree_and_branch_from_the_attempt(self) -> None:
        module = load_module()
        _, root = self.make_repository()
        worktree_root = root.parent / "worktrees"
        specs = module.worktree_specs(
            worktree_root,
            ["W-00000001", "W-00000002"],
        )

        with (
            mock.patch.object(module, "validate_specs", return_value=""),
            mock.patch.object(
                module,
                "create_worktree",
                side_effect=["", "simulated creation failure"],
            ),
            mock.patch.object(module, "cleanup_worktree") as cleanup,
            contextlib.redirect_stderr(io.StringIO()),
        ):
            result = module.run_parallel(
                root,
                [spec.target for spec in specs],
                worktree_root=worktree_root,
                driver_path=module.DRIVER,
            )

        self.assertEqual(1, result)
        self.assertEqual(
            [mock.call(root.resolve(), specs[1]), mock.call(root.resolve(), specs[0])],
            cleanup.call_args_list,
        )

    def test_real_driver_round_observes_each_worktree_root(self) -> None:
        module = load_module()
        tmp, root = self.make_repository()
        worktree_root = Path(tmp.name) / "probe-worktrees"
        targets = ["W-00000001", "W-00000002"]
        self.add_stage_probe(root, targets)

        output = io.StringIO()
        errors = io.StringIO()
        with (
            mock.patch.dict(
                os.environ,
                {
                    "CLAUDE_PROJECT_DIR": str(Path(tmp.name) / "wrong-claude-root"),
                    "PROJECT_ROOT": str(Path(tmp.name) / "wrong-legacy-root"),
                },
            ),
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(errors),
        ):
            result = module.run_parallel(
                root,
                targets,
                worktree_root=worktree_root,
                driver_path=module.DRIVER,
            )

        self.assertEqual(0, result, output.getvalue() + errors.getvalue())
        for target in targets:
            tree = (worktree_root / target).resolve()
            observed = json.loads(
                (tree / f"observed-{target}.json").read_text(encoding="utf-8")
            )
            self.assertEqual(str(tree), observed["cwd"])
            self.assertEqual(str(tree), observed["project_root"])
            self.assertEqual(str(tree), observed["claude_project_dir"])
            self.assertEqual(str(tree), observed["legacy_project_root"])
            self.assertEqual(str(tree), observed["hook_payload_root"])
            self.assertEqual(str(tree), observed["git_root"])
            self.assertTrue(observed["hook_allowed"], observed["hook_stdout"])
            self.assertTrue(
                observed["hook_denied_out_of_scope"],
                observed["hook_denial_stdout"],
            )
            self.assertTrue(Path(observed["work_item_path"]).is_relative_to(tree))
            log = tree / f".stage/.runtime/driver/logs/{target}.md"
            log_text = log.read_text(encoding="utf-8")
            self.assertIn("### Executor report", log_text)
            self.assertIn(f"observed cwd={tree}", log_text)
            self.assertIn("in-scope hook decision allow", log_text)
            self.assertIn("out-of-scope hook decision deny", log_text)
            self.assertIn("### Reviewer report", log_text)
            self.assertIn(f"Merge branch: stage/worktree/{target}", output.getvalue())

    def test_duplicate_target_is_rejected_before_creating_a_worktree(self) -> None:
        module = load_module()
        _, root = self.make_repository()

        with (
            mock.patch.object(module, "create_worktree") as create,
            contextlib.redirect_stderr(io.StringIO()),
        ):
            result = module.run_parallel(
                root,
                ["W-00000001", "W-00000001"],
                worktree_root=root.parent / "worktrees",
                driver_path=module.DRIVER,
            )

        self.assertEqual(2, result)
        create.assert_not_called()

    def test_overlapping_scopes_are_rejected_before_creating_any_worktree(self) -> None:
        module = load_module()
        _, root = self.make_repository()
        targets = ["W-00000001", "W-00000002"]
        shared_path = "stage/scripts/drive_parallel.py"
        self.add_current_cards(
            root,
            targets,
            scopes={target: shared_path for target in targets},
        )
        worktree_root = root.parent / "worktrees"
        errors = io.StringIO()

        with (
            mock.patch.object(module, "create_worktree") as create,
            contextlib.redirect_stderr(errors),
        ):
            result = module.run_parallel(
                root,
                targets,
                worktree_root=worktree_root,
                driver_path=module.DRIVER,
            )

        self.assertEqual(1, result)
        create.assert_not_called()
        self.assertFalse(worktree_root.exists())
        self.assertIn("scope overlap", errors.getvalue())
        self.assertIn(
            f"{targets[0]} <-> {targets[1]}: {shared_path}",
            errors.getvalue(),
        )

    def test_non_overlapping_scopes_run_without_an_override(self) -> None:
        module = load_module()
        _, root = self.make_repository()
        targets = ["W-00000001", "W-00000002"]
        self.add_current_cards(
            root,
            targets,
            scopes={
                targets[0]: "stage/scripts/drive_parallel.py",
                targets[1]: "plainly/tests/",
            },
        )
        worktree_root = root.parent / "worktrees"

        def successful_driver(spec, driver_path, *, timeout):
            return module.DriverResult(spec, 0, "", "")

        with (
            mock.patch.object(module, "create_worktree", return_value="") as create,
            mock.patch.object(module, "run_driver", side_effect=successful_driver),
        ):
            result = module.run_parallel(
                root,
                targets,
                worktree_root=worktree_root,
                driver_path=module.DRIVER,
            )

        self.assertEqual(0, result)
        self.assertEqual(2, create.call_count)

    def test_shared_changelog_scope_does_not_count_as_overlap(self) -> None:
        module = load_module()
        _, root = self.make_repository()
        targets = ["W-00000001", "W-00000002"]
        self.add_current_cards(
            root,
            targets,
            scopes={target: "stage/CHANGELOG.md" for target in targets},
        )
        worktree_root = root.parent / "worktrees"

        def successful_driver(spec, driver_path, *, timeout):
            return module.DriverResult(spec, 0, "", "")

        with (
            mock.patch.object(module, "create_worktree", return_value="") as create,
            mock.patch.object(module, "run_driver", side_effect=successful_driver),
        ):
            result = module.run_parallel(
                root,
                targets,
                worktree_root=worktree_root,
                driver_path=module.DRIVER,
            )

        self.assertEqual(0, result)
        self.assertEqual(2, create.call_count)

    def test_changelog_rewrite_counts_as_overlap(self) -> None:
        module = load_module()
        _, root = self.make_repository()
        targets = ["W-00000001", "W-00000002"]
        self.add_current_cards(
            root,
            targets,
            scopes={
                targets[0]: "stage/CHANGELOG.md",
                targets[1]: (
                    "stage/CHANGELOG.md, stage/scripts/release_plugin.py"
                ),
            },
        )
        worktree_root = root.parent / "worktrees"
        errors = io.StringIO()

        with (
            mock.patch.object(module, "create_worktree") as create,
            contextlib.redirect_stderr(errors),
        ):
            result = module.run_parallel(
                root,
                targets,
                worktree_root=worktree_root,
                driver_path=module.DRIVER,
            )

        self.assertEqual(1, result)
        create.assert_not_called()
        self.assertIn(
            f"{targets[0]} <-> {targets[1]}: stage/CHANGELOG.md",
            errors.getvalue(),
        )

    def test_descendant_scopes_count_as_parent_target_scopes(self) -> None:
        module = load_module()
        _, root = self.make_repository()
        targets = ["W-00000001", "W-00000002"]
        shared_path = "stage/scripts/shared.py"
        self.add_current_story_with_action(
            root,
            targets[0],
            "W-00000003",
            story_scope="stage/docs/first.md",
            action_scope=shared_path,
        )
        self.add_current_story_with_action(
            root,
            targets[1],
            "W-00000004",
            story_scope="stage/docs/second.md",
            action_scope=shared_path,
        )
        git(root, "add", ".stage")
        git(root, "commit", "-q", "-m", "add current hierarchies")
        worktree_root = root.parent / "worktrees"
        errors = io.StringIO()

        with (
            mock.patch.object(module, "create_worktree") as create,
            contextlib.redirect_stderr(errors),
        ):
            result = module.run_parallel(
                root,
                targets,
                worktree_root=worktree_root,
                driver_path=module.DRIVER,
            )

        self.assertEqual(1, result)
        create.assert_not_called()
        self.assertIn(
            f"{targets[0]} <-> {targets[1]}: {shared_path}",
            errors.getvalue(),
        )

    def test_allow_overlap_runs_and_reports_the_override(self) -> None:
        module = load_module()
        _, root = self.make_repository()
        targets = ["W-00000001", "W-00000002"]
        shared_path = "stage/scripts/drive_parallel.py"
        self.add_current_cards(
            root,
            targets,
            scopes={target: shared_path for target in targets},
        )
        worktree_root = root.parent / "worktrees"
        errors = io.StringIO()

        def successful_driver(spec, driver_path, *, timeout):
            return module.DriverResult(spec, 0, "", "")

        with (
            mock.patch.object(module, "create_worktree", return_value="") as create,
            mock.patch.object(module, "run_driver", side_effect=successful_driver),
            contextlib.redirect_stderr(errors),
        ):
            result = module.run_parallel(
                root,
                targets,
                worktree_root=worktree_root,
                driver_path=module.DRIVER,
                allow_overlap=True,
            )

        self.assertEqual(0, result)
        self.assertEqual(2, create.call_count)
        self.assertIn("--allow-overlap", errors.getvalue())
        self.assertIn(
            f"{targets[0]} <-> {targets[1]}: {shared_path}",
            errors.getvalue(),
        )

    def test_allow_overlap_is_available_from_the_command_line(self) -> None:
        module = load_module()

        with mock.patch.object(
            sys,
            "argv",
            [
                str(SCRIPT),
                "--allow-overlap",
                "W-00000001",
                "W-00000002",
            ],
        ):
            args = module.parse_args()

        self.assertTrue(args.allow_overlap)

    def test_limits_concurrent_drivers_to_configured_worker_count(self) -> None:
        module = load_module()
        _, root = self.make_repository()
        targets = ["W-00000001", "W-00000002", "W-00000003"]
        lock = threading.Lock()
        first_pair_started = threading.Event()
        active = 0
        started = 0
        maximum_active = 0

        def bounded_driver(spec, driver_path, *, timeout):
            nonlocal active, started, maximum_active
            with lock:
                active += 1
                started += 1
                current_start = started
                maximum_active = max(maximum_active, active)
                if started == 2:
                    first_pair_started.set()
            if current_start <= 2:
                self.assertTrue(first_pair_started.wait(timeout=1))
                time.sleep(0.05)
            with lock:
                active -= 1
            return module.DriverResult(spec, 0, "", "")

        with (
            mock.patch.object(module, "validate_specs", return_value=""),
            mock.patch.object(module, "create_worktree", return_value=""),
            mock.patch.object(module, "run_driver", side_effect=bounded_driver),
        ):
            result = module.run_parallel(
                root,
                targets,
                worktree_root=root.parent / "worktrees",
                driver_path=module.DRIVER,
                max_workers=2,
                driver_timeout=9,
            )

        self.assertEqual(0, result)
        self.assertEqual(2, maximum_active)

    def test_run_driver_reports_timeout(self) -> None:
        module = load_module()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tree = Path(tmp.name) / "worktree"
        card_dir = tree / ".stage/work/current/W-00000001"
        card_dir.mkdir(parents=True)
        (card_dir / "_story.md").write_text(
            "---\nid: W-00000001\nvenue: codex\n---\n",
            encoding="utf-8",
        )
        (tree / ".stage/settings.json").write_text(
            json.dumps({"reapers": {"codex": "reap-command"}}),
            encoding="utf-8",
        )
        spec = module.WorktreeSpec(
            "W-00000001",
            tree,
            "stage/worktree/W-00000001",
        )

        with mock.patch.object(
            module.subprocess,
            "run",
            side_effect=[
                subprocess.TimeoutExpired(["driver"], 7),
                subprocess.CompletedProcess("reap-command", 0, "", ""),
            ],
        ) as run:
            result = module.run_driver(spec, module.DRIVER, timeout=7)

        self.assertEqual(124, result.returncode)
        self.assertIn("timed out after 7 seconds", result.stderr)
        self.assertIn("may still be running and writing to this worktree", result.stderr)
        self.assertIn("Do not run --cleanup", result.stderr)
        self.assertIn("reapers.codex completed", result.stderr)
        self.assertEqual(7, run.call_args_list[0].kwargs["timeout"])
        self.assertEqual("reap-command", run.call_args_list[1].args[0])
        self.assertEqual(
            str((card_dir / "_story.md").resolve()),
            run.call_args_list[1].kwargs["env"]["STAGE_WORK_ITEM_PATH"],
        )
        self.assertEqual("executor", run.call_args_list[1].kwargs["env"]["STAGE_TURN_ROLE"])

    def test_run_driver_timeout_reaps_reviewer_venue(self) -> None:
        module = load_module()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tree = Path(tmp.name) / "worktree"
        card_dir = tree / ".stage/work/current/W-00000001"
        card_dir.mkdir(parents=True)
        (card_dir / "_story.md").write_text(
            "---\nid: W-00000001\nvenue: codex\n---\n",
            encoding="utf-8",
        )
        (tree / ".stage/settings.json").write_text(
            json.dumps(
                {
                    "reapers": {
                        "codex": "reap-executor",
                        "claude": "reap-reviewer",
                    },
                    "review": {
                        "reviewers": {
                            "codex": "own-venue",
                            "claude": "review-command",
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        log_dir = tree / ".stage/.runtime/driver/logs"
        log_dir.mkdir(parents=True)
        (log_dir / "W-00000001.md").write_text(
            "\n### Executor report\nWhat changed: ready for review\n",
            encoding="utf-8",
        )
        spec = module.WorktreeSpec(
            "W-00000001",
            tree,
            "stage/worktree/W-00000001",
        )

        with mock.patch.object(
            module.subprocess,
            "run",
            side_effect=[
                subprocess.TimeoutExpired(["driver"], 7),
                subprocess.CompletedProcess("reap-reviewer", 0, "", ""),
            ],
        ) as run:
            result = module.run_driver(spec, module.DRIVER, timeout=7)

        self.assertEqual(124, result.returncode)
        self.assertIn("reapers.claude completed", result.stderr)
        self.assertEqual("reap-reviewer", run.call_args_list[1].args[0])
        self.assertEqual("reviewer", run.call_args_list[1].kwargs["env"]["STAGE_TURN_ROLE"])

    def test_run_driver_timeout_explains_unresolved_reviewer_venue(self) -> None:
        module = load_module()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tree = Path(tmp.name) / "worktree"
        card_dir = tree / ".stage/work/current/W-00000001"
        card_dir.mkdir(parents=True)
        (card_dir / "_story.md").write_text(
            "---\nid: W-00000001\nvenue: codex\n---\n",
            encoding="utf-8",
        )
        (tree / ".stage/settings.json").write_text(
            json.dumps(
                {
                    "reapers": {"codex": "reap-executor"},
                    "review": {"reviewers": {"codex": "own-venue"}},
                }
            ),
            encoding="utf-8",
        )
        log_dir = tree / ".stage/.runtime/driver/logs"
        log_dir.mkdir(parents=True)
        (log_dir / "W-00000001.md").write_text(
            "\n### Executor report\nWhat changed: ready for review\n",
            encoding="utf-8",
        )
        spec = module.WorktreeSpec(
            "W-00000001",
            tree,
            "stage/worktree/W-00000001",
        )

        with mock.patch.object(
            module.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["driver"], 7),
        ):
            result = module.run_driver(spec, module.DRIVER, timeout=7)

        self.assertEqual(124, result.returncode)
        self.assertIn("cannot resolve independent reviewer venue", result.stderr)

    def test_run_driver_timeout_explains_when_no_reaper_is_configured(self) -> None:
        module = load_module()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tree = Path(tmp.name) / "worktree"
        card_dir = tree / ".stage/work/current/W-00000001"
        card_dir.mkdir(parents=True)
        (card_dir / "_story.md").write_text(
            "---\nid: W-00000001\nvenue: codex\n---\n",
            encoding="utf-8",
        )
        (tree / ".stage/settings.json").write_text("{}\n", encoding="utf-8")
        spec = module.WorktreeSpec(
            "W-00000001",
            tree,
            "stage/worktree/W-00000001",
        )

        with mock.patch.object(
            module.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["driver"], 7),
        ):
            result = module.run_driver(spec, module.DRIVER, timeout=7)

        self.assertEqual(124, result.returncode)
        self.assertIn("reapers.codex is not configured", result.stderr)
        self.assertIn("Do not run --cleanup", result.stderr)

    def test_dirty_project_is_rejected_before_creating_a_worktree(self) -> None:
        module = load_module()
        _, root = self.make_repository()
        target = "W-00000001"
        self.add_current_cards(root, [target])
        (root / "dirty.txt").write_text("not committed\n", encoding="utf-8")
        errors = io.StringIO()

        with (
            mock.patch.object(module, "create_worktree") as create,
            contextlib.redirect_stderr(errors),
        ):
            result = module.run_parallel(
                root,
                [target],
                worktree_root=root.parent / "worktrees",
                driver_path=module.DRIVER,
            )

        self.assertEqual(1, result)
        self.assertIn("project worktree is dirty", errors.getvalue())
        create.assert_not_called()

    def test_missing_card_is_rejected_before_creating_a_worktree(self) -> None:
        module = load_module()
        _, root = self.make_repository()
        errors = io.StringIO()

        with (
            mock.patch.object(module, "create_worktree") as create,
            contextlib.redirect_stderr(errors),
        ):
            result = module.run_parallel(
                root,
                ["W-00000099"],
                worktree_root=root.parent / "worktrees",
                driver_path=module.DRIVER,
            )

        self.assertEqual(1, result)
        self.assertIn("current work item does not exist: W-00000099", errors.getvalue())
        create.assert_not_called()

    def test_cleanup_removes_real_worktree_and_branch(self) -> None:
        module = load_module()
        tmp, root = self.make_repository()
        target = "W-00000001"
        worktree_root = Path(tmp.name) / "worktrees"
        spec = module.worktree_specs(worktree_root, [target])[0]
        worktree_root.mkdir()
        self.assertEqual("", module.create_worktree(root, spec))
        self.assertTrue(spec.path.is_dir())
        self.assertEqual(spec.branch, git(spec.path, "branch", "--show-current"))

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--project-root",
                str(root),
                "--worktree-root",
                str(worktree_root),
                "--cleanup",
                target,
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertFalse(spec.path.exists())
        self.assertNotIn(spec.branch, git(root, "branch", "--format=%(refname:short)"))
        self.assertIn(f"Removed worktree and branch for {target}", result.stdout)

    def test_cleanup_rejects_unregistered_path_without_deleting_it(self) -> None:
        module = load_module()
        tmp, root = self.make_repository()
        target = "W-00000001"
        worktree_root = Path(tmp.name) / "worktrees"
        unregistered = worktree_root / target
        unregistered.mkdir(parents=True)
        witness = unregistered / "keep.txt"
        witness.write_text("not created by drive_parallel\n", encoding="utf-8")
        errors = io.StringIO()

        with contextlib.redirect_stderr(errors):
            result = module.cleanup_targets(
                root,
                [target],
                worktree_root=worktree_root,
            )

        self.assertEqual(1, result)
        self.assertTrue(witness.is_file())
        self.assertIn("is not a registered Git worktree", errors.getvalue())

    def test_cleanup_rejects_registered_worktree_on_an_unexpected_branch(self) -> None:
        module = load_module()
        tmp, root = self.make_repository()
        target = "W-00000001"
        worktree_root = Path(tmp.name) / "worktrees"
        unexpected_tree = worktree_root / target
        worktree_root.mkdir()
        git(root, "worktree", "add", "-q", "-b", "user/keep", str(unexpected_tree), "HEAD")
        witness = unexpected_tree / "keep.txt"
        witness.write_text("registered, but not created by drive_parallel\n", encoding="utf-8")
        errors = io.StringIO()

        with contextlib.redirect_stderr(errors):
            result = module.cleanup_targets(
                root,
                [target],
                worktree_root=worktree_root,
            )

        self.assertEqual(1, result)
        self.assertTrue(witness.is_file())
        self.assertIn("is registered on unexpected branch user/keep", errors.getvalue())

    def test_cleanup_preserves_branch_with_unmerged_commits(self) -> None:
        module = load_module()
        tmp, root = self.make_repository()
        target = "W-00000001"
        worktree_root = Path(tmp.name) / "worktrees"
        spec = module.worktree_specs(worktree_root, [target])[0]
        worktree_root.mkdir()
        self.assertEqual("", module.create_worktree(root, spec))
        (spec.path / "committed.txt").write_text("must survive\n", encoding="utf-8")
        git(spec.path, "add", "committed.txt")
        git(spec.path, "commit", "-q", "-m", "unmerged work")
        errors = io.StringIO()

        with contextlib.redirect_stderr(errors):
            result = module.cleanup_targets(
                root,
                [target],
                worktree_root=worktree_root,
            )

        self.assertEqual(1, result)
        self.assertTrue((spec.path / "committed.txt").is_file())
        self.assertIn(spec.branch, git(root, "branch", "--format=%(refname:short)"))
        self.assertIn("contains commits not merged into HEAD", errors.getvalue())

    def test_cleanup_preserves_uncommitted_worktree_changes(self) -> None:
        module = load_module()
        tmp, root = self.make_repository()
        target = "W-00000001"
        worktree_root = Path(tmp.name) / "worktrees"
        spec = module.worktree_specs(worktree_root, [target])[0]
        worktree_root.mkdir()
        self.assertEqual("", module.create_worktree(root, spec))
        witness = spec.path / "uncommitted.txt"
        witness.write_text("must survive\n", encoding="utf-8")
        errors = io.StringIO()

        with contextlib.redirect_stderr(errors):
            result = module.cleanup_targets(
                root,
                [target],
                worktree_root=worktree_root,
            )

        self.assertEqual(1, result)
        self.assertTrue(witness.is_file())
        self.assertIn(spec.branch, git(root, "branch", "--format=%(refname:short)"))
        self.assertIn("contains uncommitted changes", errors.getvalue())
        self.assertIn("--force-cleanup", errors.getvalue())

    def test_force_cleanup_discards_uncommitted_worktree_changes(self) -> None:
        module = load_module()
        tmp, root = self.make_repository()
        target = "W-00000001"
        worktree_root = Path(tmp.name) / "worktrees"
        spec = module.worktree_specs(worktree_root, [target])[0]
        worktree_root.mkdir()
        self.assertEqual("", module.create_worktree(root, spec))
        (spec.path / "uncommitted.txt").write_text("discard me\n", encoding="utf-8")

        result = module.cleanup_targets(
            root,
            [target],
            worktree_root=worktree_root,
            force=True,
        )

        self.assertEqual(0, result)
        self.assertFalse(spec.path.exists())
        self.assertNotIn(spec.branch, git(root, "branch", "--format=%(refname:short)"))

    def test_cleanup_removes_retained_branch_when_worktree_is_absent(self) -> None:
        module = load_module()
        tmp, root = self.make_repository()
        target = "W-00000001"
        worktree_root = Path(tmp.name) / "worktrees"
        spec = module.worktree_specs(worktree_root, [target])[0]
        git(root, "branch", spec.branch, "HEAD")
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = module.cleanup_targets(
                root,
                [target],
                worktree_root=worktree_root,
            )

        self.assertEqual(0, result)
        self.assertNotIn(spec.branch, git(root, "branch", "--format=%(refname:short)"))
        self.assertIn(f"Removed retained branch {spec.branch}", output.getvalue())
        self.assertNotIn(str(spec.path), output.getvalue())

    def test_force_cleanup_is_available_from_the_command_line(self) -> None:
        module = load_module()

        with mock.patch.object(
            sys,
            "argv",
            [
                str(SCRIPT),
                "--cleanup",
                "--force-cleanup",
                "W-00000001",
            ],
        ):
            args = module.parse_args()

        self.assertTrue(args.force_cleanup)

    def test_cleanup_reports_absent_target_without_claiming_removal(self) -> None:
        module = load_module()
        tmp, root = self.make_repository()
        target = "W-00000001"
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = module.cleanup_targets(
                root,
                [target],
                worktree_root=Path(tmp.name) / "worktrees",
            )

        self.assertEqual(0, result)
        self.assertIn(f"No retained worktree or branch for {target}", output.getvalue())
        self.assertNotIn("Removed worktree and branch", output.getvalue())

    def test_cleanup_rmtree_fallback_runs_for_registered_worktree(self) -> None:
        module = load_module()
        tmp, root = self.make_repository()
        target = "W-00000001"
        worktree_root = Path(tmp.name) / "worktrees"
        spec = module.worktree_specs(worktree_root, [target])[0]
        worktree_root.mkdir()
        self.assertEqual("", module.create_worktree(root, spec))
        real_run_git = module.run_git

        def fail_git_worktree_remove(project_root, args):
            if args[:3] == ["worktree", "remove", "--force"]:
                return 1, "simulated worktree remove failure"
            return real_run_git(project_root, args)

        with (
            mock.patch.object(module, "run_git", side_effect=fail_git_worktree_remove),
            mock.patch.object(
                module.shutil,
                "rmtree",
                wraps=module.shutil.rmtree,
            ) as rmtree,
        ):
            result = module.cleanup_targets(
                root,
                [target],
                worktree_root=worktree_root,
            )

        self.assertEqual(0, result)
        rmtree.assert_called_once_with(spec.path)
        self.assertFalse(spec.path.exists())
        self.assertNotIn(spec.branch, git(root, "branch", "--format=%(refname:short)"))


if __name__ == "__main__":
    unittest.main()
