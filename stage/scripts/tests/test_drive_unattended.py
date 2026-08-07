"""Tests for drive.py --unattended: the loop, isolated branch, and safety.

The reviewed subprocess helpers close_work.py / escalate_work.py have their own
tests; here they are stubbed (recording + simulating the item state change) so
these tests focus on the loop control, real git branch isolation, required
limits, escalation routing, and the no-touch-default-branch invariant.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from driver_test_environment import sanitize_current_driver_test_environment


SCRIPT = Path(__file__).resolve().parents[1] / "drive.py"

sanitize_current_driver_test_environment()


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
        "Why: exercise the unattended driver contract\\n"
        "Changed paths (JSON):\\n' + "
        f"json.dumps({changed_paths!r}) + "
        "'\\nReview request: review every success criterion\\n', encoding='utf-8')"
    )
    return python_command(f"{code}; {report}")


EXECUTOR_WRITE = reporting_python_command(
    "open('driver-work.txt', 'a', encoding='utf-8').write('x')",
    ["driver-work.txt"],
)
EXECUTOR_FAIL = python_command("raise SystemExit(1)")


def round_trip_executor_command(
    marker: Path,
    finding: str,
    *,
    disposition: str = "accept",
    reason: str = "the reported case occurs in this project",
) -> str:
    second_change = (
        "Path('driver-work.txt').write_text('second', encoding='utf-8')"
        if disposition == "accept"
        else "None"
    )
    second_paths = ["driver-work.txt"] if disposition == "accept" else []
    return python_command(
        "import json, os\n"
        "from pathlib import Path\n"
        f"marker = Path({str(marker)!r})\n"
        "round_number = int(marker.read_text() if marker.exists() else '0') + 1\n"
        "marker.write_text(str(round_number), encoding='utf-8')\n"
        "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
        "existing = log.read_text(encoding='utf-8')\n"
        "if round_number == 1:\n"
        "    Path('driver-work.txt').write_text('first', encoding='utf-8')\n"
        "    changed_paths = ['driver-work.txt']\n"
        "    disposition_block = ''\n"
        "else:\n"
        f"    assert {finding!r} in existing\n"
        f"    {second_change}\n"
        f"    changed_paths = {second_paths!r}\n"
        "    disposition_block = ('Review dispositions (JSON):\\n' + "
        f"json.dumps([{{'finding': {finding!r}, 'disposition': {disposition!r}, "
        f"'reason': {reason!r}}}]) + '\\n')\n"
        "report = ('\\n### Executor report\\n"
        "What changed: completed round ' + str(round_number) + '\\n"
        "Why: satisfy the pending card criteria\\n"
        "Changed paths (JSON):\\n' + json.dumps(changed_paths) + '\\n' + "
        "disposition_block + "
        "'Review request: review every success criterion\\n')\n"
        "log.write_text(existing + report, encoding='utf-8')\n"
    )


def cumulative_round_trip_executor_command(marker: Path, finding: str) -> str:
    return python_command(
        "import json, os\n"
        "from pathlib import Path\n"
        f"marker = Path({str(marker)!r})\n"
        "round_number = int(marker.read_text() if marker.exists() else '0') + 1\n"
        "marker.write_text(str(round_number), encoding='utf-8')\n"
        "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
        "existing = log.read_text(encoding='utf-8')\n"
        "Path('rounds').mkdir(exist_ok=True)\n"
        "if round_number == 1:\n"
        "    Path('rounds/first.txt').write_text('first', encoding='utf-8')\n"
        "    changed_paths = ['rounds/first.txt']\n"
        "    disposition_block = ''\n"
        "else:\n"
        "    Path('rounds/second.txt').write_text('second', encoding='utf-8')\n"
        "    changed_paths = ['rounds/first.txt', 'rounds/second.txt']\n"
        "    disposition_block = ('Review dispositions (JSON):\\n' + "
        f"json.dumps([{{'finding': {finding!r}, 'disposition': 'accept', "
        "'reason': 'the cumulative retry must retain the first-round path'}]) + '\\n')\n"
        "report = ('\\n### Executor report\\n"
        "What changed: completed cumulative round ' + str(round_number) + '\\n"
        "Why: retain the complete card output across attempts\\n"
        "Changed paths (JSON):\\n' + json.dumps(changed_paths) + '\\n' + "
        "disposition_block + "
        "'Review request: review the cumulative card output\\n')\n"
        "log.write_text(existing + report, encoding='utf-8')\n"
    )


def timeout_then_success_executor_command(marker: Path) -> str:
    return python_command(
        "import json, os, time\n"
        "from pathlib import Path\n"
        f"marker = Path({str(marker)!r})\n"
        "round_number = int(marker.read_text() if marker.exists() else '0') + 1\n"
        "marker.write_text(str(round_number), encoding='utf-8')\n"
        "if round_number == 1:\n"
        "    time.sleep(5)\n"
        "Path('driver-work.txt').write_text('recovered', encoding='utf-8')\n"
        "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
        "report = ('\\n### Executor report\\n"
        "What changed: recovered after the unavailable tool\\n"
        "Why: finish the card without spending the failed transport attempt\\n"
        "Changed paths (JSON):\\n[\"driver-work.txt\"]\\n"
        "Review request: review every success criterion\\n')\n"
        "log.write_text(log.read_text(encoding='utf-8') + report, encoding='utf-8')\n"
    )


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=str(root), check=True, capture_output=True, text=True)


def git_out(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=str(root), check=True, capture_output=True, text=True
    ).stdout.strip()


def write_review_verdict(
    stage_root: Path,
    item_id: str,
    criterion: str,
    *,
    passed: bool,
) -> None:
    path = (
        stage_root
        / ".runtime"
        / "driver"
        / "verdicts"
        / f"{item_id}.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "criteria": [
                    {
                        "criterion": criterion,
                        "verdict": "PASS" if passed else "FAIL",
                        "reason": (
                            "criterion passed"
                            if passed
                            else "criterion needs another executor round"
                        ),
                    }
                ],
                "approved": passed,
            }
        ),
        encoding="utf-8",
    )


def load_module():
    # Each test stubs collaborators on the modules that own them, so those
    # modules have to be rebuilt per test the way the driver itself is.
    for name in [n for n in sys.modules if n.startswith("driver_")]:
        del sys.modules[name]
    spec = importlib.util.spec_from_file_location("stage_drive_unattended", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    # The unattended loop resolves its collaborators in its own namespace, so a
    # stub has to replace the name there rather than the one drive re-exports.
    module.unattended = sys.modules["driver_unattended"]
    module.lifecycle = sys.modules["driver_lifecycle"]
    return module


class UnattendedTest(unittest.TestCase):
    def make(
        self,
        *,
        limits: object,
        executor: str = EXECUTOR_WRITE,
        reapers: object = None,
    ):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        git(root, "init", "-q")
        git(root, "config", "user.email", "t@example.com")
        git(root, "config", "user.name", "Tester")
        (root / "seed.txt").write_text("seed", encoding="utf-8")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "seed")
        stage_root = root / ".stage"
        stage_root.mkdir()
        settings: dict[str, object] = {
            "schema_version": 5,
            "review": {"reviewers": {"codex": "echo SELF", "claude": "echo APPROVED"}},
            "executors": {"codex": executor},
        }
        if limits is not None:
            settings["limits"] = limits
        if reapers is not None:
            settings["reapers"] = reapers
        (stage_root / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
        return root, stage_root

    def card(
        self,
        stage_root: Path,
        item_id: str,
        *,
        parent: str = "",
        status: str = "active",
        autonomous: bool = True,
        promotion: str = "pending",
        promotes: str = "",
        decision_refs: str = "",
        acceptance: tuple[str, ...] = ("echo ok",),
        scope: str = "driver-work.txt",
    ) -> None:
        current_root = stage_root / "work/current"
        if not parent:
            path = current_root / item_id / "_story.md"
        else:
            parent_path = self.card_path(stage_root, parent)
            if (
                parent_path.name == "_story.md"
                and parent_path.parent.parent == current_root
            ):
                epic_path = parent_path.with_name("_epic.md")
                parent_path.replace(epic_path)
                parent_path = epic_path
            if parent_path.name == "_epic.md":
                path = parent_path.parent / item_id / "_story.md"
            elif parent_path.name == "_story.md":
                path = parent_path.parent / f"{item_id}.md"
            else:
                raise AssertionError(
                    f"action cannot parent another fixture: {parent_path}"
                )
        path.parent.mkdir(parents=True, exist_ok=True)
        rendered = "[]"
        if acceptance:
            rendered = "\n" + "\n".join(f"  - {json.dumps(c)}" for c in acceptance)
        path.write_text(
            "---\n"
            f"id: {item_id}\n"
            "kind: development\n"
            "venue: codex\n"
            f"status: {status}\n"
            "verification: pending\n"
            "retrospective: pending\n"
            "retrospective_ref:\n"
            f"promotion: {promotion}\n"
            f"autonomous: {'true' if autonomous else 'false'}\n"
            f"acceptance: {rendered}\n"
            f"scope: {scope}\n"
            f"promotes: {promotes}\n"
            f"decision_refs: {decision_refs}\n"
            "---\n\n## Progress\n",
            encoding="utf-8",
        )

    def card_path(self, stage_root: Path, item_id: str) -> Path:
        current_root = stage_root / "work/current"
        for path in current_root.rglob("*.md"):
            if path.name == f"{item_id}.md":
                return path
            if f"id: {item_id}\n" in path.read_text(encoding="utf-8"):
                return path
        return current_root / item_id / "_story.md"

    def args(self, root: Path, target: str) -> argparse.Namespace:
        return argparse.Namespace(
            project_root=str(root), target=target, timeout=30, unattended=True, execute=False
        )

    def install_stubs(self, drive, calls: list):
        def set_status(root: str, item_id: str, status: str) -> None:
            path = self.card_path(Path(root) / ".stage", item_id)
            text = path.read_text(encoding="utf-8")
            path.write_text(
                drive.set_frontmatter_field(text, "status", status), encoding="utf-8"
            )

        def stub_close(
            project_root, item_id, extra_checks, timeout, promotion_default=None
        ):
            calls.append(("close", item_id))
            set_status(str(project_root), item_id, "completed")
            return True, ""

        def stub_escalate(project_root, item_id, reason, timeout=120):
            calls.append(("escalate", item_id))
            set_status(str(project_root), item_id, "blocked")
            return True, ""

        drive.unattended.close_via_close_work = stub_close
        drive.unattended.escalate_via_escalate_work = stub_escalate

    def fail_lifecycle_commit(self, drive, fragment: str, calls: list[str]) -> None:
        def stub_commit_lifecycle(project_root, message):
            calls.append(message)
            if fragment in message:
                return False, "simulated lifecycle commit failure"
            return True, ""

        drive.unattended.commit_lifecycle = stub_commit_lifecycle

    def commit_all(self, root: Path) -> None:
        git(root, "add", "-A")
        subprocess.run(["git", "commit", "-q", "-m", "fixture"],
                       cwd=str(root), capture_output=True, text=True)

    # --- tests -------------------------------------------------------------

    def test_selects_target_when_it_is_an_autonomous_runnable_leaf(self):
        root, stage_root = self.make(limits=None)
        self.card(stage_root, "W-00000001")
        drive = load_module()

        selected = drive.select_next_unattended_leaf(
            "W-00000001", drive.load_all_work_items(stage_root)
        )

        self.assertIsNotNone(selected)
        self.assertEqual("W-00000001", selected.item_id)

    def test_close_work_overrides_project_environment_for_spawned_hook(self):
        root, _stage_root = self.make(limits=None)
        marker = root / "spawned-hook-environment.json"
        close_work = root / "fake_close_work.py"
        hook_probe = (
            "import json, os; from pathlib import Path; "
            f"Path({str(marker)!r}).write_text("
            "json.dumps({"
            "'CLAUDE_PROJECT_DIR': os.environ['CLAUDE_PROJECT_DIR'], "
            "'PROJECT_ROOT': os.environ['PROJECT_ROOT']}), encoding='utf-8')"
        )
        close_work.write_text(
            "import subprocess, sys\n"
            f"subprocess.run([sys.executable, '-c', {hook_probe!r}], check=True)\n",
            encoding="utf-8",
        )
        drive = load_module()
        drive.lifecycle.CLOSE_WORK = close_work

        with mock.patch.dict(
            os.environ,
            {
                "CLAUDE_PROJECT_DIR": "/wrong/main-checkout",
                "PROJECT_ROOT": "/wrong/main-checkout",
            },
        ):
            closed, output = drive.close_via_close_work(
                root,
                "W-00000001",
                [],
                30,
            )

        self.assertTrue(closed, output)
        environment = json.loads(marker.read_text(encoding="utf-8"))
        self.assertEqual(str(root.resolve()), environment["CLAUDE_PROJECT_DIR"])
        self.assertEqual(str(root.resolve()), environment["PROJECT_ROOT"])

    def test_unfinished_child_prevents_selecting_unattended_target_directly(self):
        root, stage_root = self.make(limits=None)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()

        selected = drive.select_next_unattended_leaf(
            "W-00000001", drive.load_all_work_items(stage_root)
        )

        self.assertIsNotNone(selected)
        self.assertEqual("W-00000002", selected.item_id)

    def test_unrunnable_unfinished_child_still_hides_unattended_target(self):
        root, stage_root = self.make(limits=None)
        self.card(stage_root, "W-00000001")
        self.card(
            stage_root,
            "W-00000002",
            parent="W-00000001",
            acceptance=(),
        )
        drive = load_module()

        selected = drive.select_next_unattended_leaf(
            "W-00000001", drive.load_all_work_items(stage_root)
        )

        self.assertIsNone(selected)

    def test_blocked_story_hides_its_remaining_actions_but_not_other_stories(self):
        root, stage_root = self.make(limits=None)
        self.card(stage_root, "W-00000001")
        self.card(
            stage_root,
            "W-00000002",
            parent="W-00000001",
            status="blocked",
        )
        self.card(stage_root, "W-00000003", parent="W-00000002")
        self.card(stage_root, "W-00000004", parent="W-00000001")
        self.card(stage_root, "W-00000005", parent="W-00000004")
        drive = load_module()

        selected = drive.select_next_unattended_leaf(
            "W-00000001", drive.load_all_work_items(stage_root)
        )

        self.assertIsNotNone(selected)
        self.assertEqual("W-00000005", selected.item_id)

    def test_subtree_limits_grow_with_action_count(self):
        root, stage_root = self.make(limits=None)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        self.card(stage_root, "W-00000003", parent="W-00000002")
        self.card(stage_root, "W-00000004", parent="W-00000002")
        drive = load_module()
        configured = {
            "max_attempts_per_item": 3,
            "max_iterations": 2,
            "max_wall_clock_seconds": 10,
        }

        effective = drive.subtree_limits(
            configured,
            "W-00000001",
            drive.load_all_work_items(stage_root),
            per_action_seconds=30,
        )

        self.assertEqual(3, effective["max_attempts_per_item"])
        self.assertEqual(6, effective["max_iterations"])
        self.assertEqual(60, effective["max_wall_clock_seconds"])

    def test_default_command_timeout_grows_with_subtree_and_keeps_900_second_floor(
        self,
    ):
        root, stage_root = self.make(limits=None)
        self.card(stage_root, "W-00000001")
        drive = load_module()

        one_leaf = drive.subtree_command_timeout(
            "W-00000001",
            drive.load_all_work_items(stage_root),
            requested=None,
        )
        self.card(stage_root, "W-00000002", parent="W-00000001")
        self.card(stage_root, "W-00000003", parent="W-00000001")
        two_leaves = drive.subtree_command_timeout(
            "W-00000001",
            drive.load_all_work_items(stage_root),
            requested=None,
        )

        self.assertEqual(900, one_leaf)
        self.assertEqual(1800, two_leaves)
        self.assertEqual(
            37,
            drive.subtree_command_timeout(
                "W-00000001",
                drive.load_all_work_items(stage_root),
                requested=37,
            ),
        )

    def test_pass_runs_target_leaf_without_wrapper_parent(self):
        limits = {
            "max_attempts_per_item": 3,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.commit_all(root)
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)

        rc = drive.run_unattended(
            self.args(root, "W-00000001"), root, stage_root, time.time()
        )

        self.assertEqual(0, rc)
        self.assertEqual(
            [("close", "W-00000001")],
            [call for call in calls if call[0] == "close"],
        )
        self.assertEqual([], [call for call in calls if call[0] == "escalate"])

    def test_unattended_records_the_exact_executor_and_reviewer_commands(self):
        limits = {
            "max_attempts_per_item": 3,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.commit_all(root)
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)

        rc = drive.run_unattended(
            self.args(root, "W-00000001"), root, stage_root, time.time()
        )
        log = (
            stage_root / ".runtime/driver/logs/W-00000001.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(0, rc)
        self.assertIn("### Driver commands", log)
        self.assertIn(f"Executor command: {json.dumps(EXECUTOR_WRITE)}", log)
        self.assertIn(
            f"Reviewer command: {json.dumps('echo APPROVED')}",
            log,
        )

    def test_refuses_without_limits(self):
        root, stage_root = self.make(limits=None)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)
        base_before = git_out(root, "rev-parse", "--abbrev-ref", "HEAD")

        self.commit_all(root)
        rc = drive.run_unattended(self.args(root, "W-00000001"), root, stage_root, time.time())

        self.assertEqual(1, rc)
        self.assertEqual([], calls)  # nothing ran
        # No isolated branch was created; still on the base branch.
        self.assertEqual(base_before, git_out(root, "rev-parse", "--abbrev-ref", "HEAD"))

    def test_pass_commits_to_isolated_branch_not_base(self):
        limits = {"max_attempts_per_item": 3, "max_iterations": 50, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        self.card(stage_root, "W-00000003", parent="W-00000001")
        self.commit_all(root)
        base = git_out(root, "rev-parse", "--abbrev-ref", "HEAD")
        base_count_before = int(git_out(root, "rev-list", "--count", base))
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)

        self.commit_all(root)
        rc = drive.run_unattended(self.args(root, "W-00000001"), root, stage_root, time.time())

        self.assertEqual(0, rc)
        closed = [c[1] for c in calls if c[0] == "close"]
        # Both leaves and the parent were closed.
        self.assertIn("W-00000002", closed)
        self.assertIn("W-00000003", closed)
        self.assertIn("W-00000001", closed)
        self.assertEqual([], [c for c in calls if c[0] == "escalate"])
        # The base branch was NOT modified.
        self.assertEqual(base_count_before, int(git_out(root, "rev-list", "--count", base)))
        # Work landed on an isolated stage/driver branch with new commits.
        current = git_out(root, "rev-parse", "--abbrev-ref", "HEAD")
        self.assertTrue(current.startswith("stage/driver/W-00000001-"), current)
        self.assertGreater(int(git_out(root, "rev-list", "--count", current)), base_count_before)

    def test_unattended_worktree_keeps_human_changes_out_of_executor_commit(self):
        limits = {
            "max_attempts_per_item": 3,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        root, stage_root = self.make(limits=limits)
        human_path = root / "human-during-run.txt"
        marker = root.parent / f"{root.name}-unattended-round"
        self.addCleanup(marker.unlink, missing_ok=True)
        settings_path = stage_root / "settings.json"
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        settings["executors"]["codex"] = python_command(
            "import os\n"
            "from pathlib import Path\n"
            f"marker = Path({str(marker)!r})\n"
            "round_number = int(marker.read_text() if marker.exists() else '0') + 1\n"
            "marker.write_text(str(round_number), encoding='utf-8')\n"
            f"Path({str(human_path)!r}).write_text('human', encoding='utf-8')\n"
            "if round_number == 1:\n"
            "    Path('failed-attempt.txt').write_text('discard me', encoding='utf-8')\n"
            "    raise SystemExit(1)\n"
            "Path('driver-work.txt').write_text('executor', encoding='utf-8')\n"
            "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
            "report = ('\\n### Executor report\\n"
            "What changed: wrote the successful executor output\\n"
            "Why: exercise isolated failure recovery\\n"
            "Decisions made: None\\n"
            "Work not done: None\\n"
            "Changed paths (JSON):\\n[\"driver-work.txt\"]\\n"
            "Review request: review every success criterion\\n')\n"
            "log.write_text(log.read_text(encoding='utf-8') + report, encoding='utf-8')"
        )
        settings_path.write_text(json.dumps(settings), encoding="utf-8")
        self.card(stage_root, "W-00000001")
        self.commit_all(root)
        exclude_path = root / ".git/info/exclude"
        with exclude_path.open("a", encoding="utf-8") as handle:
            handle.write("\n.stage/.runtime/\n")
        prior_log = stage_root / ".runtime/driver/logs/W-00000001.md"
        prior_log.parent.mkdir(parents=True)
        prior_log.write_text("# Prior unattended evidence\n", encoding="utf-8")
        base_branch = git_out(root, "rev-parse", "--abbrev-ref", "HEAD")
        base_head = git_out(root, "rev-parse", "HEAD")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)
        now = time.time()
        stamp = int(now)

        with tempfile.TemporaryDirectory() as temporary:
            worktree_root = Path(temporary) / "unattended"
            rc = drive.run_unattended_in_worktree(
                self.args(root, "W-00000001"),
                root,
                stage_root,
                now,
                worktree_root=worktree_root,
            )

            self.assertFalse((worktree_root / f"W-00000001-{stamp}").exists())

        branch = f"stage/driver/W-00000001-{stamp}"
        self.assertEqual(0, rc)
        self.assertEqual("human", human_path.read_text(encoding="utf-8"))
        self.assertEqual(base_branch, git_out(root, "rev-parse", "--abbrev-ref", "HEAD"))
        self.assertEqual(base_head, git_out(root, "rev-parse", "HEAD"))
        self.assertEqual("executor", git_out(root, "show", f"{branch}:driver-work.txt"))
        self.assertIn(
            "# Prior unattended evidence",
            prior_log.read_text(encoding="utf-8"),
        )
        failed_attempt = subprocess.run(
            ["git", "show", f"{branch}:failed-attempt.txt"],
            cwd=str(root),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, failed_attempt.returncode)
        human_in_branch = subprocess.run(
            ["git", "show", f"{branch}:human-during-run.txt"],
            cwd=str(root),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, human_in_branch.returncode)

    def test_unattended_cleanup_failure_retains_recoverable_worktree(self):
        limits = {
            "max_attempts_per_item": 3,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        root, stage_root = self.make(
            limits=limits,
            executor=reporting_python_command(
                "from pathlib import Path; "
                "Path('driver-work.txt').write_text('executor', encoding='utf-8'); "
                "Path('recovery.txt').write_text('recover me', encoding='utf-8')",
                ["driver-work.txt", "recovery.txt"],
            ),
        )
        self.card(stage_root, "W-00000001")
        self.commit_all(root)
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)
        now = time.time()
        stamp = int(now)

        with tempfile.TemporaryDirectory() as temporary:
            worktree_root = Path(temporary) / "unattended"
            worktree_path = worktree_root / f"W-00000001-{stamp}"
            output = io.StringIO()
            try:
                with contextlib.redirect_stdout(output):
                    rc = drive.run_unattended_in_worktree(
                        self.args(root, "W-00000001"),
                        root,
                        stage_root,
                        now,
                        worktree_root=worktree_root,
                    )

                self.assertEqual(1, rc)
                self.assertEqual(
                    "recover me",
                    (worktree_path / "recovery.txt").read_text(encoding="utf-8"),
                )
                self.assertIn(str(worktree_path), output.getvalue())
                self.assertIn("git worktree remove", output.getvalue())
            finally:
                if worktree_path.exists():
                    git(root, "worktree", "remove", "--force", str(worktree_path))
                subprocess.run(
                    ["git", "branch", "-D", f"stage/driver/W-00000001-{stamp}"],
                    cwd=str(root),
                    capture_output=True,
                    text=True,
                )

    def test_executor_receives_selected_work_item_environment(self):
        limits = {"max_attempts_per_item": 3, "max_iterations": 50, "max_wall_clock_seconds": 300}
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "executor-environment.json"
            variable_names = (
                "STAGE_WORK_ITEM",
                "STAGE_WORK_ITEM_PATH",
                "STAGE_PROJECT_ROOT",
                "STAGE_WORK_LOG_PATH",
                "GIT_INDEX_FILE",
            )
            executor = python_command(
                "import json, os; "
                "from pathlib import Path; "
                f"names = {variable_names!r}; "
                "Path('driver-work.txt').write_text('x', encoding='utf-8'); "
                "log = Path(os.environ['STAGE_WORK_LOG_PATH']); "
                "log.write_text(log.read_text(encoding='utf-8') + "
                "'\\n### Executor report\\n"
                "What changed: wrote driver-work.txt\\n"
                "Why: satisfy the card\\n"
                "Changed paths (JSON):\\n[\"driver-work.txt\"]\\n"
                "Review request: review every success criterion\\n', encoding='utf-8'); "
                f"Path({str(marker)!r}).write_text("
                "json.dumps({name: os.environ[name] for name in names}), "
                "encoding='utf-8')"
            )
            root, stage_root = self.make(limits=limits, executor=executor)
            self.card(stage_root, "W-00000001")
            self.card(stage_root, "W-00000002", parent="W-00000001")
            drive = load_module()
            calls: list = []
            self.install_stubs(drive, calls)

            self.commit_all(root)
            rc = drive.run_unattended(
                self.args(root, "W-00000001"), root, stage_root, time.time()
            )

            self.assertEqual(0, rc)
            environment = json.loads(marker.read_text(encoding="utf-8"))
            self.assertEqual("W-00000002", environment["STAGE_WORK_ITEM"])
            self.assertEqual(
                str(self.card_path(stage_root, "W-00000002").resolve()),
                environment["STAGE_WORK_ITEM_PATH"],
            )
            self.assertEqual(str(root.resolve()), environment["STAGE_PROJECT_ROOT"])
            self.assertEqual(
                str(
                    (
                        stage_root / ".runtime/driver/logs/W-00000002.md"
                    ).resolve()
                ),
                environment["STAGE_WORK_LOG_PATH"],
            )
            self.assertEqual(
                "executor-index",
                Path(environment["GIT_INDEX_FILE"]).name,
            )
            self.assertNotEqual(
                str((root / ".git/index").resolve()),
                environment["GIT_INDEX_FILE"],
            )

    def test_failed_review_flows_to_next_executor_and_success_squashes_rounds(self):
        limits = {
            "max_attempts_per_item": 2,
            "max_iterations": 10,
            "max_wall_clock_seconds": 300,
        }
        finding = "- regression coverage: FAIL [P1] - missing boundary case"
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "round"
            root, stage_root = self.make(
                limits=limits,
                executor=round_trip_executor_command(marker, finding),
            )
            self.card(stage_root, "W-00000001")
            self.commit_all(root)
            drive = load_module()
            close_calls: list[str] = []

            def stub_close(
                project_root, item_id, extra_checks, timeout, promotion_default=None
            ):
                close_calls.append(item_id)
                log = (
                    stage_root / ".runtime/driver/logs" / f"{item_id}.md"
                )
                if len(close_calls) == 1:
                    write_review_verdict(
                        stage_root,
                        item_id,
                        finding,
                        passed=False,
                    )
                    with log.open("a", encoding="utf-8") as handle:
                        handle.write(
                            "\n### Reviewer report\n"
                            "CRITERIA VERDICT:\n"
                            f"{finding}\n"
                            "OUT-OF-CRITERIA OBSERVATIONS:\n- None\n"
                        )
                    return False, "independent review did not pass"
                path = self.card_path(stage_root, item_id)
                path.write_text(
                    drive.set_frontmatter_field(
                        path.read_text(encoding="utf-8"),
                        "status",
                        "completed",
                    ),
                    encoding="utf-8",
                )
                return True, ""

            drive.unattended.close_via_close_work = stub_close

            rc = drive.run_unattended(
                self.args(root, "W-00000001"),
                root,
                stage_root,
                time.time(),
            )
            log = (
                stage_root / ".runtime/driver/logs/W-00000001.md"
            ).read_text(encoding="utf-8")
            subjects = git_out(root, "log", "--format=%s").splitlines()
            marker_value = marker.read_text(encoding="utf-8")

        self.assertEqual(0, rc)
        self.assertEqual(2, len(close_calls))
        self.assertEqual("2", marker_value)
        self.assertIn(f'"finding": "{finding}"', log)
        self.assertIn('"disposition": "accept"', log)
        self.assertEqual(
            1,
            subjects.count("driver: W-00000001 executor output"),
        )
        self.assertEqual("second", git_out(root, "show", "HEAD~1:driver-work.txt"))

    def test_unattended_comparison_ignores_driver_owned_work_log_path(self):
        limits = {
            "max_attempts_per_item": 2,
            "max_iterations": 10,
            "max_wall_clock_seconds": 300,
        }
        work_log_path = ".stage/.runtime/driver/logs/W-00000001.md"
        root, stage_root = self.make(
            limits=limits,
            executor=reporting_python_command(
                "from pathlib import Path; "
                "Path('driver-work.txt').write_text('done', encoding='utf-8')",
                [work_log_path, "driver-work.txt"],
            ),
        )
        self.card(stage_root, "W-00000001")
        self.commit_all(root)
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)

        rc = drive.run_unattended(
            self.args(root, "W-00000001"),
            root,
            stage_root,
            time.time(),
        )

        self.assertEqual(0, rc)
        self.assertIn(("close", "W-00000001"), calls)

    def test_unattended_retry_keeps_executor_paths_and_excludes_intervening_human_commit(
        self,
    ):
        limits = {
            "max_attempts_per_item": 2,
            "max_iterations": 10,
            "max_wall_clock_seconds": 300,
        }
        finding = "- cumulative paths: FAIL [P1] - first-round output was omitted"
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "round"
            root, stage_root = self.make(
                limits=limits,
                executor=cumulative_round_trip_executor_command(marker, finding),
            )
            self.card(
                stage_root,
                "W-00000001",
                scope="rounds",
            )
            self.commit_all(root)
            drive = load_module()
            close_calls = 0

            def stub_close(
                project_root, item_id, extra_checks, timeout, promotion_default=None
            ):
                nonlocal close_calls
                close_calls += 1
                log = stage_root / ".runtime/driver/logs" / f"{item_id}.md"
                if close_calls == 1:
                    write_review_verdict(
                        stage_root,
                        item_id,
                        finding,
                        passed=False,
                    )
                    with log.open("a", encoding="utf-8") as handle:
                        handle.write(
                            "\n### Reviewer report\n"
                            "CRITERIA VERDICT:\n"
                            f"{finding}\n"
                            "OUT-OF-CRITERIA OBSERVATIONS:\n- None\n"
                        )
                    (project_root / "human-between-attempts.txt").write_text(
                        "human",
                        encoding="utf-8",
                    )
                    git(project_root, "add", "human-between-attempts.txt")
                    git(
                        project_root,
                        "commit",
                        "-q",
                        "-m",
                        "human between attempts",
                    )
                    return False, "independent review did not pass"
                path = self.card_path(stage_root, item_id)
                path.write_text(
                    drive.set_frontmatter_field(
                        path.read_text(encoding="utf-8"),
                        "status",
                        "completed",
                    ),
                    encoding="utf-8",
                )
                return True, ""

            drive.unattended.close_via_close_work = stub_close

            rc = drive.run_unattended(
                self.args(root, "W-00000001"),
                root,
                stage_root,
                time.time(),
            )
            log = (
                stage_root / ".runtime/driver/logs/W-00000001.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, rc, log)
        self.assertEqual(2, close_calls)
        self.assertEqual("first", git_out(root, "show", "HEAD~1:rounds/first.txt"))
        self.assertEqual("second", git_out(root, "show", "HEAD~1:rounds/second.txt"))

    def test_attempt_cap_restores_executor_output_as_uncommitted_handoff(self):
        limits = {
            "max_attempts_per_item": 1,
            "max_iterations": 10,
            "max_wall_clock_seconds": 300,
        }
        finding = "- regression coverage: FAIL [P1] - still missing"
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.commit_all(root)
        drive = load_module()
        escalation_reasons: list[str] = []

        def stub_close(
            project_root, item_id, extra_checks, timeout, promotion_default=None
        ):
            log = stage_root / ".runtime/driver/logs" / f"{item_id}.md"
            write_review_verdict(
                stage_root,
                item_id,
                finding,
                passed=False,
            )
            with log.open("a", encoding="utf-8") as handle:
                handle.write(
                    "\n### Reviewer report\n"
                    "CRITERIA VERDICT:\n"
                    f"{finding}\n"
                    "OUT-OF-CRITERIA OBSERVATIONS:\n- None\n"
                )
            return False, "independent review did not pass"

        def stub_escalate(project_root, item_id, reason, timeout):
            escalation_reasons.append(reason)
            path = self.card_path(stage_root, item_id)
            path.write_text(
                drive.set_frontmatter_field(
                    path.read_text(encoding="utf-8"),
                    "status",
                    "blocked",
                ),
                encoding="utf-8",
            )
            return True

        drive.unattended.close_via_close_work = stub_close
        drive.unattended.escalate_and_commit = stub_escalate

        rc = drive.run_unattended(
            self.args(root, "W-00000001"),
            root,
            stage_root,
            time.time(),
        )
        subjects = git_out(root, "log", "--format=%s").splitlines()

        self.assertEqual(0, rc)
        self.assertEqual(1, len(escalation_reasons))
        self.assertNotIn("driver: W-00000001 executor output", subjects)
        self.assertEqual("x", (root / "driver-work.txt").read_text(encoding="utf-8"))
        self.assertIn("driver-work.txt", git_out(root, "status", "--short"))

    def test_reasoned_decline_can_complete_without_a_second_repository_change(self):
        limits = {
            "max_attempts_per_item": 2,
            "max_iterations": 10,
            "max_wall_clock_seconds": 300,
        }
        finding = "- unsupported platform: FAIL [P1] - add a fictional host"
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "round"
            root, stage_root = self.make(
                limits=limits,
                executor=round_trip_executor_command(
                    marker,
                    finding,
                    disposition="decline",
                    reason="that host cannot run this project",
                ),
            )
            self.card(stage_root, "W-00000001")
            self.commit_all(root)
            drive = load_module()
            close_calls = 0

            def stub_close(
                project_root, item_id, extra_checks, timeout, promotion_default=None
            ):
                nonlocal close_calls
                close_calls += 1
                log = (
                    stage_root / ".runtime/driver/logs" / f"{item_id}.md"
                )
                if close_calls == 1:
                    write_review_verdict(
                        stage_root,
                        item_id,
                        finding,
                        passed=False,
                    )
                    with log.open("a", encoding="utf-8") as handle:
                        handle.write(
                            "\n### Reviewer report\n"
                            "CRITERIA VERDICT:\n"
                            f"{finding}\n"
                            "OUT-OF-CRITERIA OBSERVATIONS:\n- None\n"
                        )
                    return False, "independent review did not pass"
                path = self.card_path(stage_root, item_id)
                path.write_text(
                    drive.set_frontmatter_field(
                        path.read_text(encoding="utf-8"),
                        "status",
                        "completed",
                    ),
                    encoding="utf-8",
                )
                return True, ""

            drive.unattended.close_via_close_work = stub_close

            rc = drive.run_unattended(
                self.args(root, "W-00000001"),
                root,
                stage_root,
                time.time(),
            )
            log = (
                stage_root / ".runtime/driver/logs/W-00000001.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, rc)
        self.assertEqual(2, close_calls)
        self.assertIn('"disposition": "decline"', log)
        self.assertEqual("first", git_out(root, "show", "HEAD~1:driver-work.txt"))

    def test_reviewer_timeout_retries_without_rerunning_executor_or_spending_attempt(self):
        limits = {
            "max_attempts_per_item": 1,
            "max_iterations": 10,
            "max_wall_clock_seconds": 300,
        }
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.commit_all(root)
        drive = load_module()
        close_calls: list[str] = []

        def stub_close(
            project_root, item_id, extra_checks, timeout, promotion_default=None
        ):
            close_calls.append(item_id)
            if len(close_calls) == 1:
                return False, "close_work timed out after 31s"
            path = self.card_path(stage_root, item_id)
            path.write_text(
                drive.set_frontmatter_field(
                    path.read_text(encoding="utf-8"),
                    "status",
                    "completed",
                ),
                encoding="utf-8",
            )
            return True, ""

        drive.unattended.close_via_close_work = stub_close

        rc = drive.run_unattended(
            self.args(root, "W-00000001"),
            root,
            stage_root,
            time.time(),
        )
        state = json.loads(
            (stage_root / ".runtime/driver/W-00000001.json").read_text(
                encoding="utf-8"
            )
        )
        log = (
            stage_root / ".runtime/driver/logs/W-00000001.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(0, rc)
        self.assertEqual(2, len(close_calls))
        self.assertEqual(1, log.splitlines().count("### Executor report"))
        self.assertEqual(1, state["items"]["W-00000001"]["attempt_count"])

    def test_review_failure_with_timeout_text_is_not_an_infrastructure_retry(self):
        drive = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            verdict_path = Path(tmp) / "review-verdict.json"
            verdict_path.write_text("{broken", encoding="utf-8")

            self.assertFalse(
                drive.retryable_review_infrastructure_failure(
                    close_ok=False,
                    close_output="close_work timed out after 31s",
                    verdict_file=verdict_path,
                )
            )
            verdict_path.write_text(
                json.dumps(
                    {
                        "criteria": [
                            {
                                "criterion": "criterion failed",
                                "verdict": "FAIL",
                                "reason": "the implementation is incomplete",
                            }
                        ],
                        "approved": False,
                    }
                ),
                encoding="utf-8",
            )
            self.assertFalse(
                drive.retryable_review_infrastructure_failure(
                    close_ok=False,
                    close_output="close_work timed out after 31s",
                    verdict_file=verdict_path,
                )
            )
            verdict_path.unlink()
            self.assertTrue(
                drive.retryable_review_infrastructure_failure(
                    close_ok=False,
                    close_output="close_work timed out after 31s",
                    verdict_file=verdict_path,
                )
            )

    def test_executor_timeout_does_not_spend_the_only_attempt(self):
        limits = {
            "max_attempts_per_item": 1,
            "max_iterations": 10,
            "max_wall_clock_seconds": 30,
        }
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "executor-round"
            root, stage_root = self.make(
                limits=limits,
                executor=timeout_then_success_executor_command(marker),
            )
            self.card(stage_root, "W-00000001")
            self.commit_all(root)
            drive = load_module()
            calls: list = []
            self.install_stubs(drive, calls)
            args = self.args(root, "W-00000001")
            args.timeout = 1

            rc = drive.run_unattended(
                args,
                root,
                stage_root,
                time.time(),
            )
            state = json.loads(
                (stage_root / ".runtime/driver/W-00000001.json").read_text(
                    encoding="utf-8"
                )
            )
            marker_value = marker.read_text(encoding="utf-8")

        self.assertEqual(0, rc)
        self.assertEqual("2", marker_value)
        self.assertEqual(1, state["items"]["W-00000001"]["attempt_count"])
        self.assertIn(("close", "W-00000001"), calls)

    def test_executor_staging_is_isolated_before_unattended_commit(self):
        limits = {
            "max_attempts_per_item": 3,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "index-during-executor"
            root, stage_root = self.make(limits=limits)
            self.card(stage_root, "W-00000001")
            self.card(stage_root, "W-00000002", parent="W-00000001")
            self.commit_all(root)
            index_path = root / git_out(root, "rev-parse", "--git-path", "index")
            settings_path = stage_root / "settings.json"
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            settings["executors"]["codex"] = reporting_python_command(
                "import subprocess; "
                "from pathlib import Path; "
                "Path('driver-work.txt').write_text('x', encoding='utf-8'); "
                "subprocess.run(['git', 'add', 'driver-work.txt'], check=True); "
                f"Path({str(marker)!r}).write_bytes(Path({str(index_path)!r}).read_bytes())",
                ["driver-work.txt"],
            )
            settings_path.write_text(json.dumps(settings), encoding="utf-8")
            self.commit_all(root)
            index_before = index_path.read_bytes()
            drive = load_module()
            calls: list = []
            self.install_stubs(drive, calls)

            rc = drive.run_unattended(
                self.args(root, "W-00000001"),
                root,
                stage_root,
                time.time(),
            )

            self.assertEqual(0, rc)
            self.assertEqual(index_before, marker.read_bytes())
            self.assertEqual("x", git_out(root, "show", "HEAD:driver-work.txt"))

    def test_executor_failure_escalates_not_closes(self):
        limits = {"max_attempts_per_item": 1, "max_iterations": 50, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits, executor=EXECUTOR_FAIL)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)

        self.commit_all(root)
        rc = drive.run_unattended(self.args(root, "W-00000001"), root, stage_root, time.time())

        self.assertEqual(0, rc)  # run finishes (nothing left ready)
        self.assertIn(("escalate", "W-00000002"), calls)
        self.assertNotIn("close", [c[0] for c in calls if c[1] == "W-00000002"])

    def test_unattended_reaps_executor_after_success_and_failure(self):
        limits = {
            "max_attempts_per_item": 1,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker_root = Path(marker_tmp)
            success_reaped = marker_root / "success-reaped"
            failure_reaped = marker_root / "failure-reaped"

            success_root, success_stage_root = self.make(
                limits=limits,
                reapers={
                    "codex": python_command(
                        "from pathlib import Path; "
                        f"Path({str(success_reaped)!r}).touch()"
                    )
                },
            )
            self.card(success_stage_root, "W-00000001")
            success_drive = load_module()
            success_calls: list = []
            self.install_stubs(success_drive, success_calls)
            self.commit_all(success_root)

            success_rc = success_drive.run_unattended(
                self.args(success_root, "W-00000001"),
                success_root,
                success_stage_root,
                time.time(),
            )

            failure_root, failure_stage_root = self.make(
                limits=limits,
                executor=EXECUTOR_FAIL,
                reapers={
                    "codex": python_command(
                        "from pathlib import Path; "
                        f"Path({str(failure_reaped)!r}).touch()"
                    )
                },
            )
            self.card(failure_stage_root, "W-00000001")
            failure_drive = load_module()
            failure_calls: list = []
            self.install_stubs(failure_drive, failure_calls)
            self.commit_all(failure_root)

            failure_rc = failure_drive.run_unattended(
                self.args(failure_root, "W-00000001"),
                failure_root,
                failure_stage_root,
                time.time(),
            )
            success_reaped_exists = success_reaped.exists()
            failure_reaped_exists = failure_reaped.exists()

        self.assertEqual(0, success_rc)
        self.assertEqual(0, failure_rc)
        self.assertTrue(success_reaped_exists)
        self.assertTrue(failure_reaped_exists)

    def test_unattended_missing_reaper_warns_in_output_and_work_log(self):
        limits = {
            "max_attempts_per_item": 1,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        root, stage_root = self.make(limits=limits, executor=EXECUTOR_FAIL)
        self.card(stage_root, "W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)
        self.commit_all(root)
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            rc = drive.run_unattended(
                self.args(root, "W-00000001"), root, stage_root, time.time()
            )
        log = (
            stage_root / ".runtime/driver/logs/W-00000001.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(0, rc)
        self.assertIn(
            "WARNING: reapers.codex is not configured after executor turn; "
            "jobs may remain",
            output.getvalue(),
        )
        self.assertIn("reapers.codex is not configured", log)

    def test_unattended_declared_nothing_to_reap_is_silent(self):
        limits = {
            "max_attempts_per_item": 1,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        root, stage_root = self.make(
            limits=limits,
            executor=EXECUTOR_FAIL,
            reapers={"codex": None},
        )
        self.card(stage_root, "W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)
        self.commit_all(root)
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            rc = drive.run_unattended(
                self.args(root, "W-00000001"), root, stage_root, time.time()
            )
        log = (
            stage_root / ".runtime/driver/logs/W-00000001.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(0, rc)
        self.assertNotIn("WARNING: reapers.", output.getvalue())
        self.assertNotIn("Driver warning", log)

    def test_unattended_failed_reaper_stops_before_retry(self):
        limits = {
            "max_attempts_per_item": 3,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        root, stage_root = self.make(
            limits=limits,
            executor=EXECUTOR_FAIL,
            reapers={
                "codex": python_command(
                    "print('reap stop sentinel'); raise SystemExit(4)"
                )
            },
        )
        self.card(stage_root, "W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)
        self.commit_all(root)
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            rc = drive.run_unattended(
                self.args(root, "W-00000001"), root, stage_root, time.time()
            )
        state = json.loads(
            (
                stage_root / ".runtime/driver/W-00000001.json"
            ).read_text(encoding="utf-8")
        )
        log = (
            stage_root / ".runtime/driver/logs/W-00000001.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(1, rc)
        self.assertEqual(1, state["items"]["W-00000001"]["attempt_count"])
        self.assertEqual([], calls)
        self.assertIn(
            "executor reap command failed for W-00000001; "
            "stopping before another turn",
            output.getvalue(),
        )
        self.assertIn("reap stop sentinel", log)

    def test_executor_failure_output_is_appended_to_shared_work_log(self):
        limits = {
            "max_attempts_per_item": 1,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        executor = python_command(
            "print('executor failure sentinel'); raise SystemExit(7)"
        )
        root, stage_root = self.make(limits=limits, executor=executor)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)

        self.commit_all(root)
        rc = drive.run_unattended(
            self.args(root, "W-00000001"), root, stage_root, time.time()
        )
        log = (
            stage_root / ".runtime/driver/logs/W-00000002.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(0, rc)
        self.assertIn("### Driver failure", log)
        self.assertIn("Role: executor", log)
        self.assertIn("Reason: executor failed", log)
        self.assertIn("executor failure sentinel", log)
        self.assertIn("[exit 7]", log)

    def test_successful_executor_without_repository_changes_notifies_then_escalates_repeat(self):
        limits = {"max_attempts_per_item": 1, "max_iterations": 50, "max_wall_clock_seconds": 300}
        marker_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(marker_tmp.cleanup)
        round_marker = Path(marker_tmp.name) / "no-change-round"
        executor = reporting_python_command(
            "from pathlib import Path; "
            f"marker = Path({str(round_marker)!r}); "
            "marker.parent.mkdir(parents=True, exist_ok=True); "
            "round_number = int(marker.read_text(encoding='utf-8')) + 1 "
            "if marker.exists() else 1; "
            "marker.write_text(str(round_number), encoding='utf-8'); "
            "print(round_number)",
            [],
        )
        root, stage_root = self.make(
            limits=limits,
            executor=executor,
        )
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)
        escalation_reasons: list[str] = []

        def stub_escalate_and_commit(project_root, item_id, reason, timeout):
            escalation_reasons.append(reason)
            calls.append(("escalate", item_id))
            path = self.card_path(stage_root, item_id)
            text = path.read_text(encoding="utf-8")
            path.write_text(
                drive.set_frontmatter_field(text, "status", "blocked"),
                encoding="utf-8",
            )
            return True

        drive.unattended.escalate_and_commit = stub_escalate_and_commit

        self.commit_all(root)
        exclude_path = root / git_out(root, "rev-parse", "--git-path", "info/exclude")
        exclude_path.write_text(
            exclude_path.read_text(encoding="utf-8") + ".stage/.runtime/\n",
            encoding="utf-8",
        )
        started_at = time.time()
        first_output = io.StringIO()
        with contextlib.redirect_stdout(first_output):
            first_rc = drive.run_unattended(
                self.args(root, "W-00000001"), root, stage_root, started_at
            )
        first_state = json.loads(
            (stage_root / ".runtime/driver/W-00000001.json").read_text(
                encoding="utf-8"
            )
        )
        first_log = (
            stage_root / ".runtime/driver/logs/W-00000002.md"
        ).read_text(encoding="utf-8")
        second_output = io.StringIO()
        with contextlib.redirect_stdout(second_output):
            second_rc = drive.run_unattended(
                self.args(root, "W-00000001"), root, stage_root, started_at + 2
            )

        self.assertEqual(0, first_rc)
        self.assertIn("work appears complete", first_output.getvalue())
        self.assertIn("### Driver notice", first_log)
        self.assertIn("work appears complete", first_log)
        self.assertIn("close_work.py", first_log)
        self.assertEqual(
            0,
            first_state["items"]["W-00000002"]["attempt_count"],
        )
        self.assertEqual(0, second_rc, second_output.getvalue())
        self.assertIn(("escalate", "W-00000002"), calls)
        self.assertNotIn(("close", "W-00000002"), calls)
        self.assertIn("NO-PROGRESS", escalation_reasons[0])

    def test_iteration_cap_stops_run(self):
        limits = {"max_attempts_per_item": 3, "max_iterations": 1, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        self.card(stage_root, "W-00000003", parent="W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)
        drive.unattended.subtree_limits = (
            lambda configured, target_id, items, *, per_action_seconds: configured
        )

        self.commit_all(root)
        rc = drive.run_unattended(self.args(root, "W-00000001"), root, stage_root, time.time())

        self.assertEqual(1, rc)  # stopped at the global iteration cap
        # Exactly one leaf was processed before the cap stopped the run.
        self.assertEqual(1, len([c for c in calls if c[0] == "close" and c[1] != "W-00000001"]))

    def test_missing_executor_escalates(self):
        limits = {"max_attempts_per_item": 2, "max_iterations": 50, "max_wall_clock_seconds": 300}
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        git(root, "init", "-q")
        git(root, "config", "user.email", "t@example.com")
        git(root, "config", "user.name", "Tester")
        (root / "seed.txt").write_text("seed", encoding="utf-8")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "seed")
        stage_root = root / ".stage"
        stage_root.mkdir()
        # No `executors` section at all -> resolve fails closed.
        settings = {
            "schema_version": 5,
            "review": {"reviewers": {"codex": "echo SELF", "claude": "echo APPROVED"}},
            "limits": limits,
        }
        (stage_root / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)

        self.commit_all(root)
        rc = drive.run_unattended(self.args(root, "W-00000001"), root, stage_root, time.time())

        self.assertEqual(0, rc)
        self.assertIn(("escalate", "W-00000002"), calls)


    def test_executor_failure_with_tracked_scope_still_escalates(self):
        # Regression (Codex P1): a failed executor must not be masked by
        # "nothing to commit" when the scope file already exists (tracked).
        limits = {"max_attempts_per_item": 1, "max_iterations": 50, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits, executor=EXECUTOR_FAIL)
        (root / "driver-work.txt").write_text("pre", encoding="utf-8")  # tracked scope
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)

        self.commit_all(root)
        rc = drive.run_unattended(self.args(root, "W-00000001"), root, stage_root, time.time())

        self.assertEqual(0, rc)
        self.assertIn(("escalate", "W-00000002"), calls)
        self.assertNotIn(("close", "W-00000002"), calls)

    def test_lifecycle_committed_to_run_branch(self):
        # Regression (Codex P1): the .stage lifecycle change (card -> completed) must
        # be committed to the run branch, not left only in the working tree.
        limits = {"max_attempts_per_item": 3, "max_iterations": 50, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)

        self.commit_all(root)
        rc = drive.run_unattended(self.args(root, "W-00000001"), root, stage_root, time.time())

        self.assertEqual(0, rc)
        branch = git_out(root, "rev-parse", "--abbrev-ref", "HEAD")
        card_relative = self.card_path(stage_root, "W-00000002").relative_to(root)
        committed = git_out(root, "show", f"{branch}:{card_relative.as_posix()}")
        self.assertIn("status: completed", committed)

    def test_lifecycle_commit_excludes_ignored_runtime_directory(self):
        root, stage_root = self.make(limits=None)
        self.card(stage_root, "W-00000001")
        (root / ".gitignore").write_text(".stage/.runtime/\n", encoding="utf-8")
        self.commit_all(root)
        git(root, "checkout", "-q", "-b", "stage/driver/test-runtime-exclusion")
        runtime_file = stage_root / ".runtime/driver/state.json"
        runtime_file.parent.mkdir(parents=True)
        runtime_file.write_text("{}\n", encoding="utf-8")
        card_path = self.card_path(stage_root, "W-00000001")
        card_path.write_text(
            card_path.read_text(encoding="utf-8").replace(
                "status: active", "status: blocked"
            ),
            encoding="utf-8",
        )
        drive = load_module()

        ok, error = drive.commit_lifecycle(root, "driver: test lifecycle")

        self.assertTrue(ok, error)
        committed_paths = git_out(
            root, "show", "--format=", "--name-only", "HEAD"
        ).splitlines()
        self.assertIn(
            ".stage/work/current/W-00000001/_story.md", committed_paths
        )
        self.assertNotIn(".stage/.runtime/driver/state.json", committed_paths)
        self.assertTrue(runtime_file.exists())

    def test_escalation_lifecycle_commit_failure_stops_run(self):
        limits = {"max_attempts_per_item": 1, "max_iterations": 50, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits, executor=EXECUTOR_FAIL)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        calls: list = []
        lifecycle_calls: list[str] = []
        self.install_stubs(drive, calls)
        self.fail_lifecycle_commit(drive, "escalated (lifecycle)", lifecycle_calls)

        self.commit_all(root)
        rc = drive.run_unattended(self.args(root, "W-00000001"), root, stage_root, time.time())

        self.assertEqual(1, rc)
        self.assertIn(("escalate", "W-00000002"), calls)
        self.assertEqual(
            ["driver: W-00000002 escalated (lifecycle)"],
            lifecycle_calls,
        )

    def test_close_failure_retries_without_pre_close_lifecycle_commit(self):
        limits = {"max_attempts_per_item": 2, "max_iterations": 50, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        close_calls: list[str] = []
        lifecycle_calls: list[str] = []

        def stub_close(
            project_root, item_id, extra_checks, timeout, promotion_default=None
        ):
            close_calls.append(item_id)
            return False, "simulated close failure"

        def stub_escalate(project_root, item_id, reason, timeout):
            path = self.card_path(stage_root, item_id)
            path.write_text(
                drive.set_frontmatter_field(
                    path.read_text(encoding="utf-8"),
                    "status",
                    "blocked",
                ),
                encoding="utf-8",
            )
            return True

        drive.unattended.close_via_close_work = stub_close
        drive.unattended.escalate_and_commit = stub_escalate
        self.fail_lifecycle_commit(drive, "pre-close lifecycle (retry)", lifecycle_calls)

        self.commit_all(root)
        rc = drive.run_unattended(self.args(root, "W-00000001"), root, stage_root, time.time())

        self.assertEqual(0, rc)
        self.assertEqual(["W-00000002", "W-00000002"], close_calls)
        self.assertEqual([], lifecycle_calls)

    def test_review_block_output_is_preserved_on_escalation_after_retry(self):
        limits = {
            "max_attempts_per_item": 2,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        latest_close_output = "\n".join(
            [f"review detail {number}" for number in range(44)]
            + ["x" * 5000, "CRITERIA VERDICT: FAIL [P1] review sentinel ```"]
        )
        close_outputs = ["obsolete first review output", latest_close_output]
        escalation_reasons: list[str] = []

        def stub_close(
            project_root, item_id, extra_checks, timeout, promotion_default=None
        ):
            return False, close_outputs.pop(0)

        def stub_escalate_and_commit(project_root, item_id, reason, timeout):
            escalation_reasons.append(reason)
            path = self.card_path(stage_root, item_id)
            text = path.read_text(encoding="utf-8")
            path.write_text(
                drive.set_frontmatter_field(text, "status", "blocked"),
                encoding="utf-8",
            )
            return True

        drive.unattended.close_via_close_work = stub_close
        drive.unattended.escalate_and_commit = stub_escalate_and_commit

        self.commit_all(root)
        rc = drive.run_unattended(
            self.args(root, "W-00000001"), root, stage_root, time.time()
        )

        self.assertEqual(0, rc)
        self.assertEqual(1, len(escalation_reasons))
        reason = escalation_reasons[0]
        self.assertIn("earlier lines omitted", reason)
        self.assertIn("CRITERIA VERDICT: FAIL [P1] review sentinel ``\u200b`", reason)
        self.assertNotIn("obsolete first review output", reason)
        preserved_output = drive.clip(latest_close_output)
        self.assertIn(f"close_work output:\n{preserved_output}", reason)
        self.assertLessEqual(
            len(preserved_output.split("\n", 1)[1].encode("utf-8")),
            4000,
        )

    def test_acceptance_failure_output_is_preserved_on_escalation(self):
        limits = {
            "max_attempts_per_item": 1,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        escalation_reasons: list[str] = []

        drive.unattended.close_via_close_work = (
            lambda project_root, item_id, extra_checks, timeout: (
                False,
                "$ python acceptance.py\n[exit 1]\nacceptance failure sentinel",
            )
        )

        def stub_escalate_and_commit(project_root, item_id, reason, timeout):
            escalation_reasons.append(reason)
            path = self.card_path(stage_root, item_id)
            text = path.read_text(encoding="utf-8")
            path.write_text(
                drive.set_frontmatter_field(text, "status", "blocked"),
                encoding="utf-8",
            )
            return True

        drive.unattended.escalate_and_commit = stub_escalate_and_commit

        self.commit_all(root)
        rc = drive.run_unattended(
            self.args(root, "W-00000001"), root, stage_root, time.time()
        )

        self.assertEqual(0, rc)
        self.assertEqual(1, len(escalation_reasons))
        self.assertIn(
            "$ python acceptance.py\n[exit 1]\nacceptance failure sentinel",
            escalation_reasons[0],
        )

    def test_ancestor_lifecycle_commit_failure_stops_run(self):
        limits = {"max_attempts_per_item": 3, "max_iterations": 50, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        calls: list = []
        lifecycle_calls: list[str] = []
        self.install_stubs(drive, calls)
        self.fail_lifecycle_commit(drive, "ancestor aggregation (lifecycle)", lifecycle_calls)

        self.commit_all(root)
        rc = drive.run_unattended(self.args(root, "W-00000001"), root, stage_root, time.time())

        self.assertEqual(1, rc)
        self.assertIn(("close", "W-00000001"), calls)
        self.assertEqual(
            [
                "driver: W-00000002 closed (lifecycle)",
                "driver: W-00000002 ancestor aggregation (lifecycle)",
            ],
            lifecycle_calls,
        )

    def test_parent_with_acceptance_runs_audit_and_declared_acceptance(self):
        limits = {"max_attempts_per_item": 3, "max_iterations": 50, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits)
        marker = root / "parent-checks.txt"
        audit_command = python_command(
            f"open({str(marker)!r}, 'a', encoding='utf-8').write('audit\\n')"
        )
        acceptance_command = python_command(
            f"open({str(marker)!r}, 'a', encoding='utf-8').write('acceptance\\n')"
        )
        self.card(
            stage_root,
            "W-00000001",
            autonomous=False,
            acceptance=(acceptance_command,),
            scope="parent-checks.txt",
        )
        item_path = self.card_path(stage_root, "W-00000001")
        item_path.write_text(
            item_path.read_text(encoding="utf-8").replace(
                "## Progress\n",
                "## Progress\n\n## Verification\n\n## Retrospective\n\n## Promotion decision\n",
            ),
            encoding="utf-8",
        )
        drive = load_module()

        drive.unattended.audit_check = lambda project_root: audit_command

        closed, error = drive.close_ready_ancestors(
            root,
            stage_root,
            "W-00000001",
            "W-00000001",
            30,
        )

        self.assertEqual("", error)
        self.assertEqual(["W-00000001"], closed)
        self.assertEqual(
            ["acceptance", "audit"],
            marker.read_text(encoding="utf-8").splitlines(),
        )

    def test_parent_with_a_decision_requires_a_stored_promotion_choice(self):
        limits = {
            "max_attempts_per_item": 3,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        root, stage_root = self.make(limits=limits)
        self.card(
            stage_root,
            "W-00000001",
            autonomous=False,
            decision_refs="DE-00000001",
        )
        item_path = self.card_path(stage_root, "W-00000001")
        item_path.write_text(
            item_path.read_text(encoding="utf-8").replace(
                "## Progress\n",
                "## Progress\n\n## Verification\n\n## Retrospective\n\n## Promotion decision\n",
            ),
            encoding="utf-8",
        )
        drive = load_module()
        drive.unattended.audit_check = lambda project_root: python_command("pass")

        closed, error = drive.close_ready_ancestors(
            root,
            stage_root,
            "W-00000001",
            "W-00000001",
            30,
        )

        self.assertEqual([], closed)
        self.assertIn("promotion `pending` is not final", error)

    def test_parent_with_promotion_paths_requires_a_stored_promotion_choice(self):
        limits = {
            "max_attempts_per_item": 3,
            "max_iterations": 50,
            "max_wall_clock_seconds": 300,
        }
        root, stage_root = self.make(limits=limits)
        self.card(
            stage_root,
            "W-00000001",
            autonomous=False,
            promotes=".stage/official/decisions/records/DE-00000001.md",
        )
        item_path = self.card_path(stage_root, "W-00000001")
        item_path.write_text(
            item_path.read_text(encoding="utf-8").replace(
                "## Progress\n",
                "## Progress\n\n## Verification\n\n## Retrospective\n\n## Promotion decision\n",
            ),
            encoding="utf-8",
        )
        drive = load_module()
        drive.unattended.audit_check = lambda project_root: python_command("pass")

        closed, error = drive.close_ready_ancestors(
            root,
            stage_root,
            "W-00000001",
            "W-00000001",
            30,
        )

        self.assertEqual([], closed)
        self.assertIn("promotion `pending` is not final", error)

    def test_parent_and_ancestor_lifecycle_failures_are_both_reported(self):
        limits = {"max_attempts_per_item": 3, "max_iterations": 50, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)

        original_close = drive.unattended.close_via_close_work

        def fail_parent_close(
            project_root, item_id, extra_checks, timeout, promotion_default=None
        ):
            if item_id == "W-00000001":
                return False, "simulated parent close failure"
            return original_close(project_root, item_id, extra_checks, timeout)

        drive.unattended.close_via_close_work = fail_parent_close
        self.fail_lifecycle_commit(drive, "ancestor aggregation (lifecycle)", [])

        self.commit_all(root)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = drive.run_unattended(
                self.args(root, "W-00000001"), root, stage_root, time.time()
            )

        self.assertEqual(1, rc)
        self.assertIn("parent aggregation-close failed", output.getvalue())
        self.assertIn("simulated parent close failure", output.getvalue())
        self.assertIn("cannot commit ancestor lifecycle", output.getvalue())

    def test_parent_close_failure_stops_run(self):
        # Regression (re-review): a failed parent aggregation-close must stop the run
        # with a non-zero exit, not be silently ignored.
        limits = {"max_attempts_per_item": 3, "max_iterations": 50, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        calls: list = []

        def set_status(r: str, iid: str, st: str) -> None:
            p = self.card_path(Path(r) / ".stage", iid)
            p.write_text(
                drive.set_frontmatter_field(p.read_text(encoding="utf-8"), "status", st),
                encoding="utf-8",
            )

        def stub_close(
            project_root, item_id, extra_checks, timeout, promotion_default=None
        ):
            calls.append(("close", item_id))
            if item_id == "W-00000001":  # the parent close fails
                return False, "boom"
            set_status(str(project_root), item_id, "completed")
            return True, ""

        def stub_escalate(project_root, item_id, reason, timeout=120):
            calls.append(("escalate", item_id))
            set_status(str(project_root), item_id, "blocked")
            return True, ""

        drive.unattended.close_via_close_work = stub_close
        drive.unattended.escalate_via_escalate_work = stub_escalate

        self.commit_all(root)
        rc = drive.run_unattended(self.args(root, "W-00000001"), root, stage_root, time.time())

        self.assertEqual(1, rc)  # parent close failure stops the run
        self.assertIn(("close", "W-00000001"), calls)  # the parent close was attempted


if __name__ == "__main__":
    unittest.main()
