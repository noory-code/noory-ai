from __future__ import annotations

import os
import importlib.util
import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

CLI = Path(__file__).resolve().parents[2] / "skills" / "stage-retrospective" / "close_work.py"

ITEM = """---
id: W-00000001
kind: chore
venue: {venue}
scope: src/
autonomous: {autonomous}
acceptance: {acceptance}
status: active
verification: pending
retrospective: {retro}
retrospective_ref: {ref}
promotion: {promotion}
review: {review}
---

# W-00000001 Sample

## Verification


## Retrospective

See R.

## Promotion decision
"""

ACTIVE = (
    "# Active Work\n\n| Work | Kind | Venue | Purpose | Status | Owner | Item |\n|---|---|---|---|---|---|---|\n"
    "| W-00000001 | chore | claude | x | active | Claude | [current/W-00000001.md](current/W-00000001.md) |\n"
)
REVIEW = "# Review Candidates\n\n| Artifact | Verification | Retrospective | Promotion | Item |\n|---|---|---|---|---|\n"


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), "--project-root", str(root), *args], capture_output=True, text=True
    )


def python_command(code: str) -> str:
    args = [sys.executable, "-c", code]
    return subprocess.list2cmdline(args) if os.name == "nt" else shlex.join(args)


def approving_reviewer_command(command: str) -> str:
    return python_command(
        "import os, subprocess, sys\n"
        "from pathlib import Path\n"
        f"proc = subprocess.run({command!r}, shell=True, capture_output=True, text=True)\n"
        "sys.stdout.write(proc.stdout)\n"
        "sys.stderr.write(proc.stderr)\n"
        "if proc.returncode:\n"
        "    raise SystemExit(proc.returncode)\n"
        "verdict = ('CRITERIA VERDICT:\\n"
        "- criterion: PASS - test reviewer inspected the inputs\\n"
        "APPROVED\\n"
        "OUT-OF-CRITERIA OBSERVATIONS:\\n- None')\n"
        "report = proc.stdout + proc.stderr + verdict + '\\n'\n"
        "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
        "with log.open('a', encoding='utf-8') as handle:\n"
        "    handle.write('\\n### Reviewer report\\n' + report)\n"
        "print(verdict)"
    )


def load_close_module():
    if str(CLI.parent) not in sys.path:
        sys.path.insert(0, str(CLI.parent))
    spec = importlib.util.spec_from_file_location("stage_close_work", CLI)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CloseWorkTest(unittest.TestCase):
    def make(
        self,
        retro="completed",
        ref="R-00000001",
        promotion="not_applicable",
        with_ref_file=True,
        review="not_required",
        acceptance="[]",
        autonomous="false",
        venue="codex",
    ):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / ".stage/work/current").mkdir(parents=True)
        (root / ".stage/work/retrospectives").mkdir(parents=True)
        (root / ".stage/work/current/W-00000001.md").write_text(
            ITEM.format(
                retro=retro,
                ref=ref,
                promotion=promotion,
                review=review,
                acceptance=acceptance,
                autonomous=autonomous,
                venue=venue,
            ),
            encoding="utf-8",
        )
        if with_ref_file and ref:
            (root / ".stage/work/retrospectives" / f"{ref}.md").write_text("---\nid: R\n---\n", encoding="utf-8")
        (root / ".stage/work/active.md").write_text(ACTIVE, encoding="utf-8")
        (root / ".stage/work/review.md").write_text(REVIEW, encoding="utf-8")
        (root / ".stage/settings.json").write_text('{"schema_version": 4}\n', encoding="utf-8")
        return tmp, root

    def init_git(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q", str(root)], check=True)

    def write_child(self, root: Path, item_id: str, status: str, zone: str) -> None:
        path = root / ".stage" / zone / f"{item_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nid: {item_id}\nparent: W-00000001\nstatus: {status}\n---\n",
            encoding="utf-8",
        )

    def test_refuses_parent_with_active_child(self):
        tmp, root = self.make()
        with tmp:
            self.write_child(root, "W-00000002", "active", "work/current")

            proc = run(
                root,
                "W-00000001",
                "--check",
                python_command("print('check should not run')"),
            )
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(1, proc.returncode)
        self.assertIn("W-00000002", proc.stderr)
        self.assertIn("active", proc.stderr)
        self.assertIn("status: active", item)

    def test_refuses_parent_with_planned_child(self):
        tmp, root = self.make()
        with tmp:
            self.write_child(root, "W-00000002", "captured", "work/planned")

            proc = run(
                root,
                "W-00000001",
                "--check",
                python_command("print('check should not run')"),
            )
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(1, proc.returncode)
        self.assertIn("W-00000002", proc.stderr)
        self.assertIn("captured", proc.stderr)
        self.assertIn("status: active", item)

    def test_parent_closes_with_archived_and_rejected_children(self):
        tmp, root = self.make()
        with tmp:
            self.write_child(
                root,
                "W-00000002",
                "archived",
                "official/work/archive/items",
            )
            self.write_child(root, "W-00000003", "rejected", "work/current")

            proc = run(
                root,
                "W-00000001",
                "--check",
                python_command("print('children terminal')"),
            )
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("status: completed", item)

    def test_refuses_staged_dirty_path_inside_scope(self):
        tmp, root = self.make()
        with tmp:
            self.init_git(root)
            source = root / "src/app.py"
            source.parent.mkdir(parents=True)
            source.write_text("print('dirty')\n", encoding="utf-8")
            subprocess.run(["git", "add", "src/app.py"], cwd=root, check=True)
            marker = root / "check-ran"

            proc = run(
                root,
                "W-00000001",
                "--check",
                f"{sys.executable} -c \"from pathlib import Path; Path(r'{marker}').touch()\"",
            )

            self.assertEqual(proc.returncode, 1)
            self.assertIn("src/app.py", proc.stderr)
            self.assertIn("commit source changes first, then close, then archive", proc.stderr)
            self.assertFalse(marker.exists())

    def test_allows_dirty_path_outside_scope(self):
        tmp, root = self.make()
        with tmp:
            self.init_git(root)
            outside = root / "docs/note.md"
            outside.parent.mkdir(parents=True)
            outside.write_text("dirty\n", encoding="utf-8")

            proc = run(root, "W-00000001", "--check", "true")

            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_allows_stage_only_changes(self):
        tmp, root = self.make()
        with tmp:
            self.init_git(root)

            proc = run(root, "W-00000001", "--check", "true")

            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_allows_non_git_tree(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", "true")

            self.assertEqual(proc.returncode, 0, proc.stderr)

    def write_decision(self, root: Path, *, status: str) -> None:
        decisions = root / ".stage/decisions/pending"
        decisions.mkdir(parents=True, exist_ok=True)
        (decisions / "DE-00000001.md").write_text(
            f"---\nid: DE-00000001\nwork_item: W-00000001\nstatus: {status}\n---\n# DE-00000001\n",
            encoding="utf-8",
        )

    def link_decision(self, root: Path) -> None:
        item = root / ".stage/work/current/W-00000001.md"
        text = item.read_text(encoding="utf-8").replace(
            "kind: chore\n", "kind: chore\ndecision_refs: DE-00000001\n", 1
        )
        item.write_text(text, encoding="utf-8")

    def test_refuses_while_linked_decision_is_open(self):
        tmp, root = self.make()
        with tmp:
            self.write_decision(root, status="open")
            self.link_decision(root)
            proc = run(root, "W-00000001", "--check", f"{sys.executable} -c 'print(1)'")
            body = (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8")

        self.assertEqual(1, proc.returncode)
        self.assertIn("DE-00000001", proc.stderr)
        self.assertIn("status: active", body)

    def test_closes_when_linked_decision_is_decided(self):
        tmp, root = self.make()
        with tmp:
            self.write_decision(root, status="decided")
            self.link_decision(root)
            proc = run(root, "W-00000001", "--check", f"{sys.executable} -c 'print(1)'")
            body = (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8")

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("status: completed", body)

    def test_passing_check_closes_and_moves(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", "python3 -c \"print('ok')\"")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8")
            self.assertIn("status: completed", item)
            self.assertIn("verification: passed", item)
            self.assertIn("print('ok')", item)  # evidence embedded
            self.assertNotIn("W-00000001", (root / ".stage/work/active.md").read_text(encoding="utf-8"))
            self.assertIn("[current/W-00000001.md]", (root / ".stage/work/review.md").read_text(encoding="utf-8"))

    def test_missing_lifecycle_field_fails_without_closing(self):
        tmp, root = self.make()
        with tmp:
            item_path = root / ".stage/work/current/W-00000001.md"
            original = item_path.read_text(encoding="utf-8").replace(
                "verification: pending\n",
                "",
                1,
            )
            item_path.write_text(original, encoding="utf-8")

            proc = run(root, "W-00000001", "--check", "python3 -c \"print('ok')\"")
            item = item_path.read_text(encoding="utf-8")

        self.assertEqual(1, proc.returncode)
        self.assertIn("missing lifecycle field `verification`", proc.stderr)
        self.assertEqual(original, item)

    def test_passing_check_preserves_existing_verification_and_appends_evidence(self):
        tmp, root = self.make()
        with tmp:
            item_path = root / ".stage/work/current/W-00000001.md"
            item_path.write_text(
                item_path.read_text(encoding="utf-8").replace(
                    "## Verification\n\n",
                    "## Verification\n\nBrowser verification: checkout completed successfully.\n\n",
                    1,
                ),
                encoding="utf-8",
            )

            proc = run(root, "W-00000001", "--check", "python3 -c \"print('check ok')\"")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = item_path.read_text(encoding="utf-8")

        self.assertIn("Browser verification: checkout completed successfully.", item)
        self.assertIn(f"### Executed at close — {date.today().isoformat()}", item)
        self.assertIn("print('check ok')", item)
        self.assertIn("check ok", item)
        self.assertLess(item.index("Browser verification"), item.index("### Executed at close"))

    def test_failing_check_changes_nothing(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", "python3 -c \"import sys; sys.exit(1)\"")
            self.assertEqual(proc.returncode, 1)
            item = (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8")
            self.assertIn("status: active", item)
            self.assertIn("verification: pending", item)

    def test_refuses_without_completed_retrospective(self):
        tmp, root = self.make(retro="pending")
        with tmp:
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("retrospective", proc.stderr)

    def test_refuses_missing_retro_file(self):
        tmp, root = self.make(with_ref_file=False)
        with tmp:
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)

    def test_refuses_retrospective_id_archived_for_different_work_item(self):
        tmp, root = self.make()
        with tmp:
            archive_retro = (
                root / ".stage/official/work/archive/retrospectives/R-00000001.md"
            )
            archive_retro.parent.mkdir(parents=True)
            archive_retro.write_text(
                "---\nid: R-00000001\nwork_item: W-00000099\n---\n",
                encoding="utf-8",
            )
            marker = root / "check-ran"

            proc = run(
                root,
                "W-00000001",
                "--check",
                f"{sys.executable} -c \"from pathlib import Path; Path(r'{marker}').touch()\"",
            )
            body = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("R-00000001", proc.stderr)
        self.assertIn("W-00000001", proc.stderr)
        self.assertIn("W-00000099", proc.stderr)
        self.assertFalse(marker.exists())
        self.assertIn("status: active", body)

    def test_refuses_non_final_promotion(self):
        tmp, root = self.make(promotion="pending")
        with tmp:
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("promotion", proc.stderr)

    def test_refuses_no_check(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("no --check", proc.stderr)

    def test_item_acceptance_closes_without_check_argument(self):
        tmp, root = self.make(acceptance='\n  - "python3 -c \\"print(123)\\""')
        with tmp:
            proc = run(root, "W-00000001")
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("status: completed", item)
        self.assertIn("print(123)", item)
        self.assertIn("verification passed on 1 check(s)", proc.stdout)

    def test_item_acceptance_and_cli_checks_are_merged(self):
        tmp, root = self.make(acceptance='\n  - "python3 -c \\"print(123)\\""')
        with tmp:
            proc = run(
                root,
                "W-00000001",
                "--check",
                'python3 -c "print(456)"',
            )
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("print(123)", item)
        self.assertIn("print(456)", item)

    def test_failing_item_acceptance_changes_nothing(self):
        tmp, root = self.make(
            acceptance='\n  - "python3 -c \\"import sys; sys.exit(1)\\""'
        )
        with tmp:
            proc = run(root, "W-00000001")
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(1, proc.returncode)
        self.assertIn("status: active", item)
        self.assertIn("verification: pending", item)

    def test_check_output_with_backslashes_does_not_crash(self):
        # Regression: check output is spliced into the Verification section; it must
        # not be read as regex-replacement escapes (\1, \U...) — that once crashed
        # set_section and left the item permanently un-closable.
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", r"""python3 -c "print(r'C:\Users\x back \1 \d+')" """)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8")
            self.assertIn("status: completed", item)
            self.assertIn(r"C:\Users\x", item)

    def test_refuses_item_without_verification_section(self):
        tmp, root = self.make()
        with tmp:
            p = root / ".stage/work/current/W-00000001.md"
            p.write_text(p.read_text(encoding="utf-8").replace("## Verification\n", "## Notes\n"), encoding="utf-8")
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("Verification", proc.stderr)

    def _write_review(self, root, review, *, add_verdict=True):
        import json

        self.init_git(root)
        source = root / "src/app.py"
        source.parent.mkdir(parents=True)
        source.write_text("print('committed review material')\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/app.py"], cwd=root, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Stage Test",
                "-c",
                "user.email=stage-test@example.com",
                "commit",
                "-q",
                "-m",
                "test: add review material",
            ],
            cwd=root,
            check=True,
        )
        rendered_review = review
        if add_verdict:
            rendered_review = {
                key: (
                    {
                        name: (
                            approving_reviewer_command(command)
                            if command
                            else command
                        )
                        for name, command in value.items()
                    }
                    if key in {"reviewers", "strengths"}
                    else value
                )
                for key, value in review.items()
            }
        (root / ".stage/settings.json").write_text(
            json.dumps({"schema_version": 4, "review": rendered_review}),
            encoding="utf-8",
        )

    def test_configured_review_runs_and_records(self):
        tmp, root = self.make(review="pending")
        with tmp:
            self._write_review(
                root,
                {
                    "strengths": {
                        "standard": python_command(
                            "print(''.join(['configured ', 'verdict retained']))"
                        )
                    },
                    "stages": {"implementation": "standard"},
                },
            )
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )
            self.assertIn(
                f"### Review at close — {date.today().isoformat()}",
                item,
            )
            self.assertIn(".stage/.runtime/driver/logs/W-00000001.md", item)
            self.assertIn(
                "configured verdict retained",
                (
                    root / ".stage/.runtime/driver/logs/W-00000001.md"
                ).read_text(encoding="utf-8"),
            )

    def test_review_commands_receive_absolute_work_item_path(self):
        cases = (
            (
                "staged review",
                {"review": "pending"},
                {
                    "strengths": {
                        "standard": python_command(
                            "import os; print(os.environ['STAGE_WORK_ITEM_PATH'])"
                        )
                    },
                    "stages": {"implementation": "standard"},
                },
            ),
            (
                "independent review",
                {"autonomous": "true"},
                {
                    "reviewers": {
                        "claude": python_command(
                            "import os; print(os.environ['STAGE_WORK_ITEM_PATH'])"
                        )
                    }
                },
            ),
        )
        for label, item_fields, review_config in cases:
            with self.subTest(label=label):
                tmp, root = self.make(**item_fields)
                with tmp:
                    self._write_review(root, review_config)
                    proc = run(
                        root,
                        "W-00000001",
                        "--check",
                        python_command("print(1)"),
                    )
                    item_path = (
                        root / ".stage/work/current/W-00000001.md"
                    ).resolve()
                    log = (
                        root / ".stage/.runtime/driver/logs/W-00000001.md"
                    ).read_text(encoding="utf-8")

                self.assertEqual(0, proc.returncode, proc.stderr)
                self.assertIn(str(item_path), log)

    def test_review_receives_log_path_and_appends_criterion_verdict(self):
        tmp, root = self.make(review="pending")
        with tmp:
            command = python_command(
                "import os; from pathlib import Path; "
                "log = Path(os.environ['STAGE_WORK_LOG_PATH']); "
                "assert '## 책임 경계' in log.read_text(encoding='utf-8'); "
                "print('CRITERIA VERDICT:\\n"
                "- criterion: PASS - direct inspection\\n"
                "APPROVED\\n"
                "OUT-OF-CRITERIA OBSERVATIONS:\\n- None')"
            )
            self._write_review(
                root,
                {
                    "strengths": {"standard": command},
                    "stages": {"implementation": "standard"},
                },
            )

            proc = run(root, "W-00000001", "--check", "true")
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )
            log = (
                root / ".stage/.runtime/driver/logs/W-00000001.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("### Reviewer report", log)
        self.assertIn("CRITERIA VERDICT:", log)
        self.assertIn("APPROVED", log)
        self.assertNotIn("CRITERIA VERDICT:", item)
        self.assertIn(".stage/.runtime/driver/logs/W-00000001.md", item)

    def test_review_without_criterion_verdict_blocks_even_on_zero_exit(self):
        tmp, root = self.make(review="pending")
        with tmp:
            self._write_review(
                root,
                {
                    "strengths": {
                        "standard": python_command(
                            "import os\n"
                            "from pathlib import Path\n"
                            "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
                            "with log.open('a', encoding='utf-8') as handle:\n"
                            "    handle.write('\\n### Reviewer report\\nlooks fine\\n')"
                        )
                    },
                    "stages": {"implementation": "standard"},
                },
                add_verdict=False,
            )

            proc = run(root, "W-00000001", "--check", "true")
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )
            log = (
                root / ".stage/.runtime/driver/logs/W-00000001.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(1, proc.returncode)
        self.assertIn("reviewer did not append criterion verdicts", proc.stderr)
        self.assertIn("status: active", item)
        self.assertIn("looks fine", log)

    def test_out_of_criteria_fail_text_does_not_block_logged_approval(self):
        tmp, root = self.make(review="pending")
        with tmp:
            reviewer = python_command(
                "import os; from pathlib import Path; "
                "log = Path(os.environ['STAGE_WORK_LOG_PATH']); "
                "report = ('\\n### Reviewer report\\n"
                "CRITERIA VERDICT:\\n"
                "- criterion: PASS - success criterion is satisfied\\n"
                "APPROVED\\n"
                "OUT-OF-CRITERIA OBSERVATIONS:\\n"
                "- FAIL text here is non-blocking\\n'); "
                "log.write_text(log.read_text(encoding='utf-8') + report, "
                "encoding='utf-8'); "
                "print('APPROVED')"
            )
            self._write_review(
                root,
                {
                    "strengths": {"standard": reviewer},
                    "stages": {"implementation": "standard"},
                },
                add_verdict=False,
            )

            proc = run(root, "W-00000001", "--check", "true")

        self.assertEqual(0, proc.returncode, proc.stderr)

    def test_latest_review_failures_exclude_out_of_criteria_observations(self):
        close_work = load_close_module()
        log = (
            "### Reviewer report\n"
            "CRITERIA VERDICT:\n"
            "- criterion one: PASS - complete\n"
            "- criterion two: FAIL [P1] - missing regression\n"
            "OUT-OF-CRITERIA OBSERVATIONS:\n"
            "- FAIL text outside the card does not enter the round trip\n"
        )

        self.assertEqual(
            ["- criterion two: FAIL [P1] - missing regression"],
            close_work.latest_review_failures(log),
        )

    def test_executor_report_rejects_reasonless_review_disposition(self):
        close_work = load_close_module()
        finding = "- criterion two: FAIL [P1] - missing regression"
        previous = (
            "### Reviewer report\n"
            "CRITERIA VERDICT:\n"
            f"{finding}\n"
            "OUT-OF-CRITERIA OBSERVATIONS:\n- None\n"
        )
        current = (
            previous
            + "\n### Executor report\n"
            "What changed: declined the finding\n"
            "Why: the reported situation does not occur\n"
            "Changed paths (JSON):\n[]\n"
            "Review dispositions (JSON):\n"
            + json.dumps(
                [
                    {
                        "finding": finding,
                        "disposition": "decline",
                        "reason": "",
                    }
                ]
            )
            + "\n"
            "Review request: verify the disposition\n"
        )

        _dispositions, error = close_work.executor_review_dispositions(
            previous,
            current,
            [finding],
        )

        self.assertIn("requires a non-empty one-line reason", error)

    def review_committed_paths_command(self) -> str:
        return python_command(
            "import json, os; from pathlib import Path; "
            "paths = json.loads(Path(os.environ['STAGE_CHANGED_PATHS_FILE'])"
            ".read_text(encoding='utf-8')); "
            "assert paths == ['src/app.py'], paths; "
            "print(Path(paths[0]).read_text(encoding='utf-8'), end='')"
        )

    def test_staged_review_receives_close_owned_committed_path_list(self):
        tmp, root = self.make(review="pending")
        with tmp:
            self._write_review(
                root,
                {
                    "strengths": {"standard": self.review_committed_paths_command()},
                    "stages": {"implementation": "standard"},
                },
            )

            proc = run(root, "W-00000001", "--check", "true")
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )
            log = (
                root / ".stage/.runtime/driver/logs/W-00000001.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn(".stage/.runtime/driver/logs/W-00000001.md", item)
        self.assertIn("committed review material", log)

    def test_autonomous_review_receives_close_owned_committed_path_list(self):
        tmp, root = self.make(autonomous="true")
        with tmp:
            self._write_review(
                root,
                {"reviewers": {"claude": self.review_committed_paths_command()}},
            )

            proc = run(
                root,
                "W-00000001",
                "--check",
                python_command("print(1)"),
            )
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )
            log = (
                root / ".stage/.runtime/driver/logs/W-00000001.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn(".stage/.runtime/driver/logs/W-00000001.md", item)
        self.assertIn("committed review material", log)

    def test_review_block_verdict_refuses(self):
        tmp, root = self.make(review="pending")
        with tmp:
            self._write_review(root, {"strengths": {"red-team": "python3 -c \"print('BLOCK: found a bug')\""}, "stages": {"implementation": "red-team"}})
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("status: active", (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8"))

    def test_not_required_bypasses_review_even_if_configured(self):
        # Field-driven: an item that does not declare review: pending completes
        # without running the configured review command.
        tmp, root = self.make(review="not_required")
        with tmp:
            self._write_review(root, {"strengths": {"standard": "python3 -c \"print('BLOCK: should not run')\""}, "stages": {"implementation": "standard"}})
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8")
            self.assertIn("status: completed", item)
            self.assertNotIn("should not run", item)

    def test_pending_review_becomes_passed(self):
        tmp, root = self.make(review="pending")
        with tmp:
            self._write_review(root, {"strengths": {"standard": "python3 -c \"print('review ok')\""}, "stages": {"implementation": "standard"}})
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("review: passed", (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8"))

    def test_pending_review_without_command_fails_closed(self):
        # review: pending but the stage has no configured command -> cannot honestly pass.
        tmp, root = self.make(review="pending")
        with tmp:
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("review is pending", proc.stderr)

    def test_review_block_survives_long_output(self):
        # Verdict first, then >40 lines, exit 0 — BLOCK: must still be detected on
        # the raw output, not the clipped evidence.
        tmp, root = self.make(review="pending")
        with tmp:
            cmd = "python3 -c \"print('BLOCK: nope'); [print(i) for i in range(60)]\""
            self._write_review(root, {"strengths": {"red-team": cmd}, "stages": {"implementation": "red-team"}})
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("status: active", (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8"))

    def test_review_strength_typo_fails_closed(self):
        tmp, root = self.make(review="pending")
        with tmp:
            self._write_review(root, {"stages": {"implementation": "redteam"}})  # not a valid strength
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("review config", proc.stderr)

    def test_review_strength_without_command_fails_closed(self):
        tmp, root = self.make(review="pending")
        with tmp:
            self._write_review(root, {"stages": {"implementation": "standard"}})  # no strengths.standard command
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)

    def test_autonomous_item_runs_opposite_venue_reviewer_and_blocks_on_verdict(self):
        tmp, root = self.make(autonomous="true")
        with tmp:
            self._write_review(
                root,
                {
                    "reviewers": {
                        "codex": python_command("print('same venue should not run')"),
                        "claude": python_command("print('BLOCK: independent rejection')"),
                    }
                },
            )

            proc = run(root, "W-00000001", "--check", python_command("print(1)"))
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )
            log = (
                root / ".stage/.runtime/driver/logs/W-00000001.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(1, proc.returncode)
        self.assertIn("independent review did not pass", proc.stderr)
        self.assertIn("status: active", item)

    def test_autonomous_item_without_opposite_venue_reviewer_fails_closed(self):
        tmp, root = self.make(autonomous="true")
        with tmp:
            self._write_review(
                root,
                {"reviewers": {"codex": python_command("print(1)")}},
            )

            proc = run(root, "W-00000001", "--check", python_command("print(1)"))
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(1, proc.returncode)
        self.assertIn("independent review config unusable", proc.stderr)
        self.assertIn("different from item venue `codex`", proc.stderr)
        self.assertIn("status: active", item)

    def test_autonomous_item_closes_when_opposite_venue_reviewer_approves(self):
        tmp, root = self.make(autonomous="true")
        with tmp:
            self._write_review(
                root,
                {
                    "reviewers": {
                        "codex": python_command("print('same venue should not run')"),
                        "claude": python_command(
                            "print(''.join(['independent ', 'verdict retained']))"
                        ),
                    }
                },
            )

            proc = run(root, "W-00000001", "--check", python_command("print(1)"))
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )
            log = (
                root / ".stage/.runtime/driver/logs/W-00000001.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("status: completed", item)
        self.assertIn("review: passed", item)
        self.assertIn(
            f"### Independent review at close — {date.today().isoformat()}",
            item,
        )
        self.assertIn(".stage/.runtime/driver/logs/W-00000001.md", item)
        self.assertIn("independent verdict retained", log)
        self.assertNotIn("same venue should not run", item)

    def test_autonomous_item_blocks_on_nonzero_reviewer_exit(self):
        tmp, root = self.make(autonomous="true")
        with tmp:
            self._write_review(
                root,
                {
                    "reviewers": {
                        "claude": python_command(
                            "import sys; print('review failed'); sys.exit(7)"
                        )
                    }
                },
            )

            proc = run(root, "W-00000001", "--check", python_command("print(1)"))
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(1, proc.returncode)
        self.assertIn("independent review did not pass", proc.stderr)
        self.assertIn("[exit 7]", proc.stderr)
        self.assertIn("status: active", item)

    def test_non_autonomous_item_ignores_independent_reviewers(self):
        tmp, root = self.make()
        with tmp:
            self._write_review(
                root,
                {
                    "reviewers": {
                        "claude": python_command("print('BLOCK: should not run')")
                    }
                },
            )

            proc = run(root, "W-00000001", "--check", python_command("print(1)"))
            item = (root / ".stage/work/current/W-00000001.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("status: completed", item)
        self.assertNotIn("should not run", item)

    def test_promotion_arg_sets_final(self):
        tmp, root = self.make(promotion="pending")
        with tmp:
            proc = run(root, "W-00000001", "--promotion", "not_applicable", "--check", "true")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("promotion: not_applicable", (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
