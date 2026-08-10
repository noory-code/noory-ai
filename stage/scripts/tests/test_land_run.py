from __future__ import annotations

import importlib.util
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "land_run.py"


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


def load_module():
    spec = importlib.util.spec_from_file_location("stage_land_run", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LandRunTest(unittest.TestCase):
    target = "W-00000001"

    def make_repository(
        self,
        *,
        branch: str | None = None,
    ) -> tuple[Path, Path]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        main = Path(temporary.name) / "project"
        run = Path(temporary.name) / "run"
        main.mkdir()
        git(main, "init", "-q")
        git(main, "config", "user.email", "test@example.com")
        git(main, "config", "user.name", "Tester")
        (main / ".gitignore").write_text(".stage/.runtime/\n", encoding="utf-8")
        (main / ".stage/work/current" / self.target).mkdir(parents=True)
        (main / ".stage/work/retrospectives").mkdir(parents=True)
        (main / ".stage/work/active.md").write_text("active\n", encoding="utf-8")
        (main / ".stage/work/review.md").write_text("review\n", encoding="utf-8")
        (main / ".stage/settings.json").write_text(
            '{"schema_version": 5, "governance": {"exclude_paths": []}}\n',
            encoding="utf-8",
        )
        (main / "src.txt").write_text("before\n", encoding="utf-8")
        self.write_card(main, status="active")
        git(main, "add", ".")
        git(main, "commit", "-q", "-m", "seed")
        git(
            main,
            "worktree",
            "add",
            "-q",
            "-b",
            branch or f"stage/worktree/{self.target}",
            str(run),
            "HEAD",
        )
        return main, run

    def card_path(self, root: Path, target: str | None = None) -> Path:
        target = target or self.target
        return root / ".stage/work/current" / target / "_story.md"

    def write_card(
        self,
        root: Path,
        *,
        target: str | None = None,
        status: str,
        verification: str = "passed",
        retrospective: str = "completed",
        retrospective_ref: str = "R-00000001",
        scope: str = "src.txt",
        parent: str = "",
    ) -> None:
        target = target or self.target
        path = self.card_path(root, target)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            textwrap.dedent(
                f"""\
                ---
                id: {target}
                kind: development
                venue: codex
                autonomous: false
                status: {status}
                verification: {verification}
                retrospective: {retrospective}
                retrospective_ref: {retrospective_ref}
                promotion: not_applicable
                review: not_required
                scope: {scope}
                parent: {parent}
                promotes:
                decision_refs:
                ---

                # {target} Test
                """
            ),
            encoding="utf-8",
        )

    def write_retrospective(
        self,
        root: Path,
        *,
        target: str | None = None,
        ref: str = "R-00000001",
    ) -> None:
        target = target or self.target
        retrospective_root = root / ".stage/work/retrospectives"
        retrospective_root.mkdir(parents=True, exist_ok=True)
        (retrospective_root / f"{ref}.md").write_text(
            f"---\nid: {ref}\nwork_item: {target}\n---\n\n# {ref}\n",
            encoding="utf-8",
        )

    def finish_run(self, run: Path, *, indexes: bool = True) -> None:
        self.write_card(run, status="completed")
        self.write_retrospective(run)
        (run / "src.txt").write_text("after\n", encoding="utf-8")
        if indexes:
            (run / ".stage/work/active.md").write_text("closed\n", encoding="utf-8")
            (run / ".stage/work/review.md").write_text("candidate\n", encoding="utf-8")
        log = run / ".stage/.runtime/driver/logs" / f"{self.target}.md"
        log.parent.mkdir(parents=True)
        log.write_text("run evidence\n", encoding="utf-8")

    def run_main(self, main: Path, run: Path) -> tuple[int, str, str]:
        module = load_module()
        stdout: list[str] = []
        stderr: list[str] = []
        with mock.patch("builtins.print") as printed:
            status = module.main(
                [
                    "--project-root",
                    str(main),
                    "--worktree",
                    str(run),
                    self.target,
                ]
            )
        for call in printed.call_args_list:
            rendered = " ".join(str(value) for value in call.args)
            if call.kwargs.get("file") is module.sys.stderr:
                stderr.append(rendered)
            else:
                stdout.append(rendered)
        return status, "\n".join(stdout), "\n".join(stderr)

    def assert_main_unchanged(self, main: Path, before: str) -> None:
        self.assertEqual(git(main, "rev-parse", "HEAD"), before)

    def test_lands_run_and_records_both_commits_before_cleanup(self):
        main, run = self.make_repository()
        branch = git(run, "branch", "--show-current")
        self.finish_run(run)

        status, stdout, stderr = self.run_main(main, run)

        self.assertEqual((status, stderr), (0, ""))
        self.assertIn(f"Landed {self.target}", stdout)
        self.assertEqual((main / "src.txt").read_text(encoding="utf-8"), "after\n")
        self.assertEqual(
            (main / ".stage/.runtime/driver/logs" / f"{self.target}.md").read_text(
                encoding="utf-8"
            ),
            "run evidence\n",
        )
        messages = [
            git(main, "show", "-s", "--format=%B", "HEAD"),
            git(main, "show", "-s", "--format=%B", "HEAD^2"),
        ]
        for message in messages:
            self.assertIn(f"Work-Item: {self.target}", message)
            self.assertIn(f"Source-Branch: {branch}", message)
        parents = git(main, "rev-list", "--parents", "-n", "1", "HEAD").split()
        self.assertEqual(len(parents), 3)
        self.assertFalse(run.exists())
        self.assertNotIn(branch, git(main, "branch", "--format=%(refname:short)").splitlines())

    def test_reports_changed_project_operations_files(self):
        main, run = self.make_repository()
        self.finish_run(run)
        self.write_card(
            run,
            status="completed",
            scope="src.txt, .stage/operations/",
        )
        instruction = run / ".stage/operations/claude-venue.md"
        instruction.parent.mkdir(parents=True)
        instruction.write_text("updated instruction\n", encoding="utf-8")

        status, stdout, stderr = self.run_main(main, run)

        self.assertEqual((status, stderr), (0, ""))
        self.assertIn("Project rules under .stage/operations/ changed; read them again:", stdout)
        self.assertIn("- .stage/operations/claude-venue.md", stdout)

    def test_does_not_report_project_operations_when_none_changed(self):
        main, run = self.make_repository()
        self.finish_run(run)

        status, stdout, stderr = self.run_main(main, run)

        self.assertEqual((status, stderr), (0, ""))
        self.assertNotIn("Project rules under .stage/operations/ changed; read them again:", stdout)

    def test_accepts_terminal_run_without_index_changes(self):
        main, run = self.make_repository()
        self.finish_run(run, indexes=False)

        status, _, stderr = self.run_main(main, run)

        self.assertEqual((status, stderr), (0, ""))

    def test_accepts_rejected_run_with_retrospective(self):
        main, run = self.make_repository()
        self.finish_run(run)
        self.write_card(run, status="rejected", verification="pending")

        status, _, stderr = self.run_main(main, run)

        self.assertEqual((status, stderr), (0, ""))

    def test_accepts_declared_teammate_branch_prefix(self):
        main, run = self.make_repository(
            branch=f"stage/teammate/{self.target}-implementer"
        )
        self.finish_run(run)

        status, _, stderr = self.run_main(main, run)

        self.assertEqual((status, stderr), (0, ""))

    def test_restores_retained_unattended_branch_before_landing(self):
        branch = f"stage/driver/{self.target}-123"
        main, run = self.make_repository(branch=branch)
        self.finish_run(run)
        git(run, "add", ".stage", "src.txt")
        git(run, "commit", "-q", "-m", "driver closed run")
        source_log = run / ".stage/.runtime/driver/logs" / f"{self.target}.md"
        destination_log = main / ".stage/.runtime/driver/logs" / f"{self.target}.md"
        destination_log.parent.mkdir(parents=True)
        destination_log.write_text(source_log.read_text(encoding="utf-8"), encoding="utf-8")
        source_log.unlink()
        git(main, "worktree", "remove", str(run))
        self.assertFalse(run.exists())

        status, _, stderr = self.run_main(main, run)

        self.assertEqual((status, stderr), (0, ""))
        self.assertFalse(run.exists())
        self.assertNotIn(branch, git(main, "branch", "--format=%(refname:short)").splitlines())

    def test_accepts_closed_target_and_closed_ancestor_records(self):
        parent = "W-00000002"
        main, run = self.make_repository()
        main_branch = git(main, "branch", "--show-current")
        parent_dir = main / ".stage/work/current" / parent
        target_dir = parent_dir
        target_dir.mkdir(parents=True)
        self.card_path(main).replace(target_dir / f"{self.target}.md")
        self.write_card(main, target=parent, status="active", scope="parent.txt")
        (main / "parent.txt").write_text("parent\n", encoding="utf-8")
        git(main, "add", ".stage", "parent.txt")
        git(main, "commit", "-q", "-m", "add hierarchy")
        git(run, "merge", "--ff-only", main_branch)

        parent_dir = run / ".stage/work/current" / parent
        target_dir = parent_dir
        self.write_card(
            run,
            target=parent,
            status="completed",
            retrospective_ref="R-00000002",
            scope="parent.txt",
        )
        self.write_retrospective(run, target=parent, ref="R-00000002")
        (run / "parent.txt").write_text("parent\n", encoding="utf-8")
        target_path = target_dir / f"{self.target}.md"
        text = target_path.read_text(encoding="utf-8")
        target_path.write_text(
            text.replace("status: active", "status: completed")
            .replace("retrospective: completed", "retrospective: completed")
            .replace("parent: ", f"parent: {parent}"),
            encoding="utf-8",
        )
        self.write_retrospective(run)
        (run / "src.txt").write_text("after\n", encoding="utf-8")
        (run / ".stage/work/active.md").write_text("closed\n", encoding="utf-8")
        (run / ".stage/work/review.md").write_text("candidate\n", encoding="utf-8")
        log = run / ".stage/.runtime/driver/logs" / f"{self.target}.md"
        log.parent.mkdir(parents=True)
        log.write_text("run evidence\n", encoding="utf-8")

        status, _, stderr = self.run_main(main, run)

        self.assertEqual((status, stderr), (0, ""))
        self.assertTrue(main.joinpath(target_path.relative_to(run)).is_file())
        self.assertTrue(main.joinpath(parent_dir.relative_to(run), "_story.md").is_file())
        self.assertTrue(main.joinpath(".stage/work/retrospectives/R-00000002.md").is_file())

    def test_uses_registry_derived_index_paths(self):
        main, run = self.make_repository()
        self.finish_run(run, indexes=False)
        custom_active = run / ".stage/work/custom-active.md"
        custom_review = run / ".stage/work/custom-review.md"
        custom_active.write_text("closed\n", encoding="utf-8")
        custom_review.write_text("candidate\n", encoding="utf-8")
        module = load_module()
        actual = module.v4_lifecycle_paths()
        derived = type(actual)(
            **{
                **actual.__dict__,
                "active_index": "work/custom-active.md",
                "review_index": "work/custom-review.md",
            }
        )

        with mock.patch.object(module, "v4_lifecycle_paths", return_value=derived):
            status = module.main(
                ["--project-root", str(main), "--worktree", str(run), self.target]
            )

        self.assertEqual(status, 0)
        self.assertTrue(main.joinpath(".stage/work/custom-active.md").is_file())
        self.assertTrue(main.joinpath(".stage/work/custom-review.md").is_file())

    def test_rejects_stage_official_change_before_main_branch_changes(self):
        main, run = self.make_repository()
        self.finish_run(run)
        self.write_card(run, status="completed", scope="*")
        official = run / ".stage/official/canon"
        official.mkdir(parents=True)
        (official / "truth.md").write_text("not allowed\n", encoding="utf-8")
        before = git(main, "rev-parse", "HEAD")

        status, _, stderr = self.run_main(main, run)

        self.assertEqual(status, 1)
        self.assertIn("outside the landing allowance", stderr)
        self.assertIn(".stage/official/canon/truth.md", stderr)
        self.assert_main_unchanged(main, before)

    def test_rejects_sibling_lifecycle_even_with_wildcard_scope(self):
        main, run = self.make_repository()
        self.finish_run(run)
        self.write_card(run, status="completed", scope="*")
        sibling = run / ".stage/work/current/W-00000009/_story.md"
        sibling.parent.mkdir(parents=True)
        sibling.write_text("---\nid: W-00000009\nstatus: active\n---\n", encoding="utf-8")
        before = git(main, "rev-parse", "HEAD")

        status, _, stderr = self.run_main(main, run)

        self.assertEqual(status, 1)
        self.assertIn(".stage/work/current/W-00000009/_story.md", stderr)
        self.assert_main_unchanged(main, before)

    def test_rejects_out_of_scope_decision_record_before_main_branch_changes(self):
        main, run = self.make_repository()
        self.finish_run(run)
        decision = run / ".stage/decisions/pending/DE-00000001.md"
        decision.parent.mkdir(parents=True)
        decision.write_text("decision\n", encoding="utf-8")
        git(run, "add", str(decision.relative_to(run)))
        before = git(main, "rev-parse", "HEAD")

        status, _, stderr = self.run_main(main, run)

        self.assertEqual(status, 1)
        self.assertIn("already staged outside the landing allowance", stderr)
        self.assertIn(".stage/decisions/pending/DE-00000001.md", stderr)
        self.assert_main_unchanged(main, before)

    def test_rejects_branch_that_does_not_name_target(self):
        main, run = self.make_repository(branch="stage/worktree/W-00000999")
        self.finish_run(run)
        before = git(main, "rev-parse", "HEAD")

        status, _, stderr = self.run_main(main, run)

        self.assertEqual(status, 1)
        self.assertIn("does not name W-00000001", stderr)
        self.assert_main_unchanged(main, before)

    def test_rejects_non_terminal_target(self):
        main, run = self.make_repository()
        self.finish_run(run)
        self.write_card(run, status="active")
        before = git(main, "rev-parse", "HEAD")

        status, _, stderr = self.run_main(main, run)

        self.assertEqual(status, 1)
        self.assertIn("status `active` is not final", stderr)
        self.assert_main_unchanged(main, before)

    def test_rejects_completed_target_with_completion_blocker(self):
        main, run = self.make_repository()
        self.finish_run(run)
        self.write_card(run, status="completed", verification="pending")
        before = git(main, "rev-parse", "HEAD")

        status, _, stderr = self.run_main(main, run)

        self.assertEqual(status, 1)
        self.assertIn("verification `pending`", stderr)
        self.assert_main_unchanged(main, before)

    def test_rejects_missing_retrospective_file(self):
        main, run = self.make_repository()
        self.finish_run(run)
        (run / ".stage/work/retrospectives/R-00000001.md").unlink()
        before = git(main, "rev-parse", "HEAD")

        status, _, stderr = self.run_main(main, run)

        self.assertEqual(status, 1)
        self.assertIn("retrospective file does not exist", stderr)
        self.assert_main_unchanged(main, before)

    def test_rejects_incomplete_or_unreferenced_retrospective(self):
        cases = (
            ({"retrospective": "pending"}, "retrospective `pending`"),
            ({"retrospective_ref": ""}, "retrospective_ref is empty"),
        )
        for fields, expected in cases:
            with self.subTest(expected=expected):
                main, run = self.make_repository()
                self.finish_run(run)
                self.write_card(run, status="completed", **fields)
                before = git(main, "rev-parse", "HEAD")

                status, _, stderr = self.run_main(main, run)

                self.assertEqual(status, 1)
                self.assertIn(expected, stderr)
                self.assert_main_unchanged(main, before)

    def test_rejects_dirty_main_checkout(self):
        main, run = self.make_repository()
        self.finish_run(run)
        (main / "src.txt").write_text("dirty main\n", encoding="utf-8")
        before = git(main, "rev-parse", "HEAD")

        status, _, stderr = self.run_main(main, run)

        self.assertEqual(status, 1)
        self.assertIn("project checkout is dirty", stderr)
        self.assert_main_unchanged(main, before)

    def test_aborts_conflicting_merge_without_a_main_commit(self):
        main, run = self.make_repository()
        self.finish_run(run)
        (main / "src.txt").write_text("main change\n", encoding="utf-8")
        git(main, "add", "src.txt")
        git(main, "commit", "-q", "-m", "main change")
        before = git(main, "rev-parse", "HEAD")

        status, _, stderr = self.run_main(main, run)

        self.assertEqual(status, 1)
        self.assertIn("merge conflict", stderr)
        self.assert_main_unchanged(main, before)
        self.assertFalse((main / ".git/MERGE_HEAD").exists())
        self.assertTrue(run.exists())

    def test_ignores_main_only_paths_when_checking_run_allowance(self):
        main, run = self.make_repository()
        self.finish_run(run)
        (main / "unrelated.txt").write_text("main only\n", encoding="utf-8")
        git(main, "add", "unrelated.txt")
        git(main, "commit", "-q", "-m", "unrelated main work")

        status, _, stderr = self.run_main(main, run)

        self.assertEqual((status, stderr), (0, ""))
        self.assertEqual(
            (main / "unrelated.txt").read_text(encoding="utf-8"),
            "main only\n",
        )


if __name__ == "__main__":
    unittest.main()
