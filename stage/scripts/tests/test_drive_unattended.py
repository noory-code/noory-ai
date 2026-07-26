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


SCRIPT = Path(__file__).resolve().parents[1] / "drive.py"


def python_command(code: str) -> str:
    args = [sys.executable, "-c", code]
    return subprocess.list2cmdline(args) if os.name == "nt" else shlex.join(args)


EXECUTOR_WRITE = python_command("open('driver-work.txt', 'a', encoding='utf-8').write('x')")
EXECUTOR_FAIL = python_command("raise SystemExit(1)")


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=str(root), check=True, capture_output=True, text=True)


def git_out(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=str(root), check=True, capture_output=True, text=True
    ).stdout.strip()


def load_module():
    spec = importlib.util.spec_from_file_location("stage_drive_unattended", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class UnattendedTest(unittest.TestCase):
    def make(self, *, limits: object, executor: str = EXECUTOR_WRITE):
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
            "schema_version": 4,
            "review": {"reviewers": {"codex": "echo SELF", "claude": "echo APPROVED"}},
            "executors": {"codex": executor},
        }
        if limits is not None:
            settings["limits"] = limits
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
        acceptance: tuple[str, ...] = ("echo ok",),
        scope: str = "driver-work.txt",
    ) -> None:
        path = stage_root / "work" / "current" / f"{item_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        rendered = "[]"
        if acceptance:
            rendered = "\n" + "\n".join(f"  - {json.dumps(c)}" for c in acceptance)
        path.write_text(
            "---\n"
            f"id: {item_id}\n"
            "kind: development\n"
            "venue: codex\n"
            f"parent: {parent}\n"
            f"status: {status}\n"
            "verification: pending\n"
            "retrospective: pending\n"
            "retrospective_ref:\n"
            "promotion: pending\n"
            f"autonomous: {'true' if autonomous else 'false'}\n"
            f"acceptance: {rendered}\n"
            f"scope: {scope}\n"
            "promotes:\n"
            "decision_refs:\n"
            "---\n\n## Progress\n",
            encoding="utf-8",
        )

    def args(self, root: Path, target: str) -> argparse.Namespace:
        return argparse.Namespace(
            project_root=str(root), target=target, timeout=30, unattended=True, execute=False
        )

    def install_stubs(self, drive, calls: list):
        def set_status(root: str, item_id: str, status: str) -> None:
            path = Path(root) / ".stage" / "work" / "current" / f"{item_id}.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(
                drive.set_frontmatter_field(text, "status", status), encoding="utf-8"
            )

        def stub_close(project_root, item_id, extra_checks, timeout):
            calls.append(("close", item_id))
            set_status(str(project_root), item_id, "completed")
            return True, ""

        def stub_escalate(project_root, item_id, reason, timeout=120):
            calls.append(("escalate", item_id))
            set_status(str(project_root), item_id, "blocked")
            return True, ""

        drive.close_via_close_work = stub_close
        drive.escalate_via_escalate_work = stub_escalate

    def fail_lifecycle_commit(self, drive, fragment: str, calls: list[str]) -> None:
        def stub_commit_lifecycle(project_root, message):
            calls.append(message)
            if fragment in message:
                return False, "simulated lifecycle commit failure"
            return True, ""

        drive.commit_lifecycle = stub_commit_lifecycle

    def commit_all(self, root: Path) -> None:
        git(root, "add", "-A")
        subprocess.run(["git", "commit", "-q", "-m", "fixture"],
                       cwd=str(root), capture_output=True, text=True)

    # --- tests -------------------------------------------------------------

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

    def test_executor_receives_selected_work_item_environment(self):
        limits = {"max_attempts_per_item": 3, "max_iterations": 50, "max_wall_clock_seconds": 300}
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "executor-environment.json"
            variable_names = (
                "STAGE_WORK_ITEM",
                "STAGE_WORK_ITEM_PATH",
                "STAGE_PROJECT_ROOT",
                "GIT_INDEX_FILE",
            )
            executor = python_command(
                "import json, os; "
                "from pathlib import Path; "
                f"names = {variable_names!r}; "
                "Path('driver-work.txt').write_text('x', encoding='utf-8'); "
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
                str((stage_root / "work/current/W-00000002.md").resolve()),
                environment["STAGE_WORK_ITEM_PATH"],
            )
            self.assertEqual(str(root.resolve()), environment["STAGE_PROJECT_ROOT"])
            self.assertEqual(
                "executor-index",
                Path(environment["GIT_INDEX_FILE"]).name,
            )
            self.assertNotEqual(
                str((root / ".git/index").resolve()),
                environment["GIT_INDEX_FILE"],
            )

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
            settings["executors"]["codex"] = python_command(
                "import subprocess; "
                "from pathlib import Path; "
                "Path('driver-work.txt').write_text('x', encoding='utf-8'); "
                "subprocess.run(['git', 'add', 'driver-work.txt'], check=True); "
                f"Path({str(marker)!r}).write_bytes(Path({str(index_path)!r}).read_bytes())"
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

    def test_successful_executor_without_repository_changes_escalates_not_closes(self):
        limits = {"max_attempts_per_item": 1, "max_iterations": 50, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits, executor=python_command("raise SystemExit(0)"))
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)
        escalation_reasons: list[str] = []

        def stub_escalate_and_commit(project_root, item_id, reason, timeout):
            escalation_reasons.append(reason)
            calls.append(("escalate", item_id))
            path = stage_root / "work/current" / f"{item_id}.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(
                drive.set_frontmatter_field(text, "status", "blocked"),
                encoding="utf-8",
            )
            return True

        drive.escalate_and_commit = stub_escalate_and_commit

        self.commit_all(root)
        rc = drive.run_unattended(
            self.args(root, "W-00000001"), root, stage_root, time.time()
        )

        self.assertEqual(0, rc)
        self.assertIn(("escalate", "W-00000002"), calls)
        self.assertNotIn(("close", "W-00000002"), calls)
        self.assertIn("executor left repository state unchanged", escalation_reasons[0])
        self.assertIn("close_work.py", escalation_reasons[0])

    def test_iteration_cap_stops_run(self):
        limits = {"max_attempts_per_item": 3, "max_iterations": 1, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        self.card(stage_root, "W-00000003", parent="W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)

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
            "schema_version": 4,
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
        committed = git_out(root, "show", f"{branch}:.stage/work/current/W-00000002.md")
        self.assertIn("status: completed", committed)

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

    def test_pre_close_lifecycle_commit_failure_stops_before_retry(self):
        limits = {"max_attempts_per_item": 3, "max_iterations": 50, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        close_calls: list[str] = []
        lifecycle_calls: list[str] = []

        def stub_close(project_root, item_id, extra_checks, timeout):
            close_calls.append(item_id)
            return False, "simulated close failure"

        drive.close_via_close_work = stub_close
        self.fail_lifecycle_commit(drive, "pre-close lifecycle (retry)", lifecycle_calls)

        self.commit_all(root)
        rc = drive.run_unattended(self.args(root, "W-00000001"), root, stage_root, time.time())

        self.assertEqual(1, rc)
        self.assertEqual(["W-00000002"], close_calls)
        self.assertEqual(
            ["driver: W-00000002 pre-close lifecycle (retry)"],
            lifecycle_calls,
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
        item_path = stage_root / "work/current/W-00000001.md"
        item_path.write_text(
            item_path.read_text(encoding="utf-8").replace(
                "## Progress\n",
                "## Progress\n\n## Verification\n\n## Retrospective\n\n## Promotion decision\n",
            ),
            encoding="utf-8",
        )
        drive = load_module()

        drive.audit_check = lambda project_root: audit_command

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

    def test_parent_and_ancestor_lifecycle_failures_are_both_reported(self):
        limits = {"max_attempts_per_item": 3, "max_iterations": 50, "max_wall_clock_seconds": 300}
        root, stage_root = self.make(limits=limits)
        self.card(stage_root, "W-00000001")
        self.card(stage_root, "W-00000002", parent="W-00000001")
        drive = load_module()
        calls: list = []
        self.install_stubs(drive, calls)

        original_close = drive.close_via_close_work

        def fail_parent_close(project_root, item_id, extra_checks, timeout):
            if item_id == "W-00000001":
                return False, "simulated parent close failure"
            return original_close(project_root, item_id, extra_checks, timeout)

        drive.close_via_close_work = fail_parent_close
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
            p = Path(r) / ".stage" / "work" / "current" / f"{iid}.md"
            p.write_text(
                drive.set_frontmatter_field(p.read_text(encoding="utf-8"), "status", st),
                encoding="utf-8",
            )

        def stub_close(project_root, item_id, extra_checks, timeout):
            calls.append(("close", item_id))
            if item_id == "W-00000001":  # the parent close fails
                return False, "boom"
            set_status(str(project_root), item_id, "completed")
            return True, ""

        def stub_escalate(project_root, item_id, reason, timeout=120):
            calls.append(("escalate", item_id))
            set_status(str(project_root), item_id, "blocked")
            return True, ""

        drive.close_via_close_work = stub_close
        drive.escalate_via_escalate_work = stub_escalate

        self.commit_all(root)
        rc = drive.run_unattended(self.args(root, "W-00000001"), root, stage_root, time.time())

        self.assertEqual(1, rc)  # parent close failure stops the run
        self.assertIn(("close", "W-00000001"), calls)  # the parent close was attempted


if __name__ == "__main__":
    unittest.main()
