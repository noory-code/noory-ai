# The hook must run wherever `python3` points on a host machine (3.9+), so the
# test module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


HOOK_TEST_ROOT = Path(__file__).resolve().parent
if str(HOOK_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_TEST_ROOT))

from hook_test_environment import sanitize_current_hook_environment  # noqa: E402


sanitize_current_hook_environment()

HOOK_PATH = Path(__file__).resolve().parents[1] / "stage_guard.py"
SPEC = importlib.util.spec_from_file_location("stage_guard", HOOK_PATH)
stage_guard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["stage_guard"] = stage_guard
SPEC.loader.exec_module(stage_guard)


def git(*args: str, cwd: Path) -> None:
    subprocess.run(
        ["git", "-c", "user.email=stage@test", "-c", "user.name=Stage Test", *args],
        cwd=cwd,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def decision(result) -> str:
    if not result or "hookSpecificOutput" not in result:
        return "allow"
    return result["hookSpecificOutput"].get("permissionDecision", "allow")


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def make_repository(root: Path) -> Path:
    """A Stage project with one commit, so linked worktrees can branch from it."""

    root.mkdir(parents=True)
    git("init", "-q", cwd=root)
    write(root / ".stage" / "settings.json", json.dumps({"schema_version": 5}))
    write(root / "src" / "app.py", "print('app')\n")
    git("add", ".", cwd=root)
    git("commit", "-q", "-m", "init", cwd=root)
    return root.resolve()


def add_worktree(repository: Path, location: Path, branch: str) -> Path:
    git("worktree", "add", "-q", str(location), "-b", branch, cwd=repository)
    return location.resolve()


def open_work_item(root: Path) -> None:
    write(
        root / ".stage" / "work" / "current" / "W-0001.md",
        (
            "---\nid: W-0001\ntitle: Test work\nstatus: active\nverification: pending\n"
            "retrospective: pending\nretrospective_ref:\npromotion: pending\nscope: src\n"
            "promotes:\n---\n# W-0001 Test work\n"
        ),
    )


class WorktreeFixture(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name).resolve()
        self.main = make_repository(base / "main")
        self.worktree = add_worktree(
            self.main, self.main / ".claude" / "worktrees" / "job", "job"
        )
        self.sibling = add_worktree(
            self.main, self.main / ".claude" / "worktrees" / "sibling", "sibling"
        )
        self.other = make_repository(base / "other")
        self.other_worktree = add_worktree(self.other, base / "other-job", "other-job")
        self.outside = base / "outside"
        self.outside.mkdir()

    def root_for(self, cwd: Path, project_dir: Path | None) -> Path:
        """Claude Code's own binding: CLAUDE_PROJECT_DIR alone."""

        environment = {} if project_dir is None else {"CLAUDE_PROJECT_DIR": str(project_dir)}
        with patch.dict(os.environ, environment):
            return stage_guard.resolve_workspace_root({"cwd": str(cwd)})

    def pinned_root_for(self, cwd: Path, root: Path, *, executor: bool = False) -> Path:
        """The driver's binding: CLAUDE_PROJECT_DIR and PROJECT_ROOT on the target
        tree, plus STAGE_PROJECT_ROOT for executors and reviewers."""

        environment = {"CLAUDE_PROJECT_DIR": str(root), "PROJECT_ROOT": str(root)}
        if executor:
            environment["STAGE_PROJECT_ROOT"] = str(root)
        with patch.dict(os.environ, environment):
            return stage_guard.resolve_workspace_root({"cwd": str(cwd)})


class SessionEnteredWorktreeTest(WorktreeFixture):
    """Given a Claude session that started in the main checkout and entered a
    linked worktree of the same repository, the hook judges that worktree."""

    def test_root_is_the_entered_worktree(self) -> None:
        self.assertEqual(self.root_for(self.worktree, self.main), self.worktree)

    def test_root_is_the_worktree_from_a_subdirectory(self) -> None:
        subdirectory = self.worktree / "src"
        self.assertEqual(self.root_for(subdirectory, self.main), self.worktree)

    def test_worktree_stage_records_are_not_governed(self) -> None:
        payload = {
            "tool_name": "Write",
            "cwd": str(self.worktree),
            "tool_input": {
                "file_path": str(self.worktree / ".stage" / "work" / "planned" / "note.md"),
                "content": "# note\n",
            },
        }
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(self.main)}):
            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_open_work_is_read_from_the_worktree(self) -> None:
        open_work_item(self.worktree)
        payload = {
            "tool_name": "Write",
            "cwd": str(self.worktree),
            "tool_input": {
                "file_path": str(self.worktree / "src" / "app.py"),
                "content": "print('changed')\n",
            },
        }
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(self.main)}):
            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_worktree_without_open_work_still_hits_the_registration_gate(self) -> None:
        open_work_item(self.main)
        payload = {
            "tool_name": "Write",
            "cwd": str(self.worktree),
            "tool_input": {
                "file_path": str(self.worktree / "src" / "app.py"),
                "content": "print('changed')\n",
            },
        }
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(self.main)}):
            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")


class UnchangedRootTest(WorktreeFixture):
    """Every other binding keeps today's root."""

    def test_driver_pinned_worktree_stays_pinned(self) -> None:
        self.assertEqual(self.pinned_root_for(self.worktree, self.worktree), self.worktree)

    def test_driver_pinned_worktree_ignores_a_main_checkout_cwd(self) -> None:
        self.assertEqual(self.pinned_root_for(self.main, self.worktree), self.worktree)

    def test_driver_pinned_worktree_ignores_a_sibling_worktree_cwd(self) -> None:
        for cwd in (self.sibling, self.sibling / "src"):
            for executor in (False, True):
                with self.subTest(cwd=cwd, executor=executor):
                    self.assertEqual(
                        self.pinned_root_for(cwd, self.worktree, executor=executor),
                        self.worktree,
                    )

    def test_driver_pinned_main_checkout_ignores_a_worktree_cwd(self) -> None:
        for cwd in (self.worktree, self.worktree / "src"):
            for executor in (False, True):
                with self.subTest(cwd=cwd, executor=executor):
                    self.assertEqual(
                        self.pinned_root_for(cwd, self.main, executor=executor), self.main
                    )

    def test_session_started_in_a_worktree_keeps_it_for_a_sibling_cwd(self) -> None:
        self.assertEqual(self.root_for(self.sibling, self.worktree), self.worktree)

    def test_main_checkout_session_stays_on_the_main_checkout(self) -> None:
        self.assertEqual(self.root_for(self.main / "src", self.main), self.main)

    def test_codex_hook_without_project_variable_uses_cwd(self) -> None:
        self.assertEqual(self.root_for(self.worktree, None), self.worktree)
        self.assertEqual(self.root_for(self.main, None), self.main)

    def test_cwd_outside_any_worktree_keeps_the_project_root(self) -> None:
        self.assertEqual(self.root_for(self.outside, self.main), self.main)

    def test_worktree_of_another_repository_keeps_the_project_root(self) -> None:
        self.assertEqual(self.root_for(self.other_worktree, self.main), self.main)

    def test_main_checkout_of_another_repository_keeps_the_project_root(self) -> None:
        self.assertEqual(self.root_for(self.other, self.main), self.main)


if __name__ == "__main__":
    unittest.main()
