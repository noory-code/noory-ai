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
        "Why: exercise the driver contract\\n"
        "Changed paths (JSON):\\n' + "
        f"json.dumps({changed_paths!r}) + "
        "'\\nReview request: review every success criterion\\n', encoding='utf-8')"
    )
    return python_command(f"{code}; {report}")


def stale_log_rewrite_command(code: str, changed_paths: list[str]) -> str:
    return python_command(
        "import json, os\n"
        "from pathlib import Path\n"
        f"{code}\n"
        "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
        "current = log.read_text(encoding='utf-8')\n"
        "durable = current.rsplit('\\n### Driver commands\\n', 1)[0]\n"
        "report = ('\\n### Executor report\\n"
        "What changed: rewrote the log from an intact prior snapshot\\n"
        "Why: exercise recovery of the current driver command record\\n"
        "Decisions made: kept every prior work-log byte intact\\n"
        "Work not done: None\\n"
        "Changed paths (JSON):\\n' + "
        f"json.dumps({changed_paths!r}) + "
        "'\\nReview request: review the recovered append-only log\\n')\n"
        "log.write_text(durable + report, encoding='utf-8')\n"
    )


def cumulative_retry_executor_command(marker: Path) -> str:
    return python_command(
        "import json, os\n"
        "from pathlib import Path\n"
        f"marker = Path({str(marker)!r})\n"
        "round_number = int(marker.read_text() if marker.exists() else '0') + 1\n"
        "marker.write_text(str(round_number), encoding='utf-8')\n"
        "if round_number == 1:\n"
        "    Path('first-round.txt').write_text('first', encoding='utf-8')\n"
        "    changed_paths = ['first-round.txt']\n"
        "else:\n"
        "    Path('second-round.txt').write_text('second', encoding='utf-8')\n"
        "    changed_paths = ['first-round.txt', 'second-round.txt']\n"
        "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
        "report = ('\\n### Executor report\\n"
        "What changed: completed round ' + str(round_number) + '\\n"
        "Why: exercise cumulative card reporting\\n"
        "Changed paths (JSON):\\n' + json.dumps(changed_paths) + '\\n"
        "Review request: review the cumulative card output\\n')\n"
        "log.write_text(log.read_text(encoding='utf-8') + report, encoding='utf-8')\n"
    )


def retry_reviewer_command(marker: Path) -> str:
    return python_command(
        "import json, os\n"
        "from pathlib import Path\n"
        f"marker = Path({str(marker)!r})\n"
        "if marker.read_text(encoding='utf-8') == '1':\n"
        "    raise SystemExit(1)\n"
        "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
        "report = ('\\n### Reviewer report\\n"
        "CRITERIA VERDICT:\\n"
        "- cumulative paths: PASS - both rounds were reviewed\\n"
        "APPROVED\\n"
        "OUT-OF-CRITERIA OBSERVATIONS:\\n- None\\n')\n"
        "log.write_text(log.read_text(encoding='utf-8') + report, encoding='utf-8')\n"
        "Path(os.environ['STAGE_REVIEW_VERDICT_FILE']).write_text(\n"
        "    json.dumps({'criteria': [{'criterion': 'cumulative paths', "
        "'verdict': 'PASS', 'reason': 'both rounds were reviewed'}], "
        "'approved': True}), encoding='utf-8')\n"
        "print('APPROVED')\n"
    )


def narrowing_executor_command(marker: Path) -> str:
    return python_command(
        "import json, os\n"
        "from pathlib import Path\n"
        f"marker = Path({str(marker)!r})\n"
        "round_number = int(marker.read_text() if marker.exists() else '0') + 1\n"
        "marker.write_text(str(round_number), encoding='utf-8')\n"
        "changed = Path(f'round-{round_number}.txt')\n"
        "changed.write_text(str(round_number), encoding='utf-8')\n"
        "changed_paths = [f'round-{number}.txt' for number in range(1, round_number + 1)]\n"
        "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
        "report = ('\\n### Executor report\\n"
        "What changed: completed review round ' + str(round_number) + '\\n"
        "Why: exercise narrowed re-review inputs\\n"
        "Changed paths (JSON):\\n' + json.dumps(changed_paths) + '\\n')\n"
        "if round_number > 1:\n"
        "    report += ('Review dispositions (JSON):\\n' + json.dumps([{\n"
        "        'finding': 'failing criterion',\n"
        "        'disposition': 'accept',\n"
        "        'reason': 'the second round fixes this criterion',\n"
        "    }]) + '\\n')\n"
        "report += 'Review request: review this round according to the driver inputs\\n'\n"
        "log.write_text(log.read_text(encoding='utf-8') + report, encoding='utf-8')\n"
    )


def narrowing_reviewer_command(marker: Path, capture: Path) -> str:
    return python_command(
        "import json, os\n"
        "from pathlib import Path\n"
        f"marker = Path({str(marker)!r})\n"
        f"capture = Path({str(capture)!r})\n"
        "round_number = int(marker.read_text(encoding='utf-8'))\n"
        "verdict_path = Path(os.environ['STAGE_REVIEW_VERDICT_FILE'])\n"
        "if round_number == 1:\n"
        "    assert os.environ['STAGE_REVIEW_MODE'] == 'full'\n"
        "    assert 'STAGE_PREVIOUS_REVIEW_VERDICT_FILE' not in os.environ\n"
        "    assert 'STAGE_REVIEW_FAILED_CRITERIA_FILE' not in os.environ\n"
        "    verdict = {\n"
        "        'criteria': [\n"
        "            {'criterion': 'passing criterion', 'verdict': 'PASS', "
        "'reason': 'the first review passed it'},\n"
        "            {'criterion': 'failing criterion', 'verdict': 'FAIL', "
        "'reason': 'the first review found a defect'},\n"
        "        ],\n"
        "        'approved': False,\n"
        "    }\n"
        "else:\n"
        "    assert os.environ['STAGE_REVIEW_MODE'] == 'narrow'\n"
        "    previous = json.loads(Path(\n"
        "        os.environ['STAGE_PREVIOUS_REVIEW_VERDICT_FILE']\n"
        "    ).read_text(encoding='utf-8'))\n"
        "    failed = json.loads(Path(\n"
        "        os.environ['STAGE_REVIEW_FAILED_CRITERIA_FILE']\n"
        "    ).read_text(encoding='utf-8'))\n"
        "    changed = json.loads(Path(\n"
        "        os.environ['STAGE_CHANGED_PATHS_FILE']\n"
        "    ).read_text(encoding='utf-8'))\n"
        "    capture.write_text(json.dumps({\n"
        "        'previous': previous,\n"
        "        'failed': failed,\n"
        "        'changed': changed,\n"
        "    }), encoding='utf-8')\n"
        "    assert failed == ['failing criterion']\n"
        "    assert changed == ['round-2.txt']\n"
        "    verdict = {\n"
        "        'criteria': [{\n"
        "            'criterion': 'failing criterion',\n"
        "            'verdict': 'PASS',\n"
        "            'reason': 'the second review confirmed the fix',\n"
        "        }],\n"
        "        'approved': True,\n"
        "    }\n"
        "verdict_path.write_text(json.dumps(verdict), encoding='utf-8')\n"
        "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
        "with log.open('a', encoding='utf-8') as handle:\n"
        "    handle.write('\\n### Reviewer report\\nreviewed round ' + "
        "str(round_number) + '\\n')\n"
    )


def missing_verdict_then_full_reviewer_command(marker: Path, capture: Path) -> str:
    return python_command(
        "import json, os\n"
        "from pathlib import Path\n"
        f"marker = Path({str(marker)!r})\n"
        f"capture = Path({str(capture)!r})\n"
        "round_number = int(marker.read_text(encoding='utf-8'))\n"
        "if round_number == 1:\n"
        "    raise SystemExit(9)\n"
        "capture.write_text(json.dumps({\n"
        "    'mode': os.environ['STAGE_REVIEW_MODE'],\n"
        "    'has_previous': 'STAGE_PREVIOUS_REVIEW_VERDICT_FILE' in os.environ,\n"
        "    'has_failed': 'STAGE_REVIEW_FAILED_CRITERIA_FILE' in os.environ,\n"
        "    'changed': json.loads(Path(os.environ['STAGE_CHANGED_PATHS_FILE']).read_text(\n"
        "        encoding='utf-8'\n"
        "    )),\n"
        "}), encoding='utf-8')\n"
        "Path(os.environ['STAGE_REVIEW_VERDICT_FILE']).write_text(json.dumps({\n"
        "    'criteria': [{\n"
        "        'criterion': 'full criterion',\n"
        "        'verdict': 'PASS',\n"
        "        'reason': 'the fallback reviewed the complete card',\n"
        "    }],\n"
        "    'approved': True,\n"
        "}), encoding='utf-8')\n"
    )


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
        + "import json, os\n"
        "from pathlib import Path\n"
        "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
        "report = ('\\n### Reviewer report\\n"
        "CRITERIA VERDICT:\\n"
        "- criterion: PASS - test reviewer inspected the inputs\\n"
        "APPROVED\\n"
        "OUT-OF-CRITERIA OBSERVATIONS:\\n- None\\n')\n"
        "log.write_text(log.read_text(encoding='utf-8') + report, encoding='utf-8')\n"
        "Path(os.environ['STAGE_REVIEW_VERDICT_FILE']).write_text(\n"
        "    json.dumps({'criteria': [{'criterion': 'criterion', "
        "'verdict': 'PASS', 'reason': 'test reviewer inspected the inputs'}], "
        "'approved': True}), encoding='utf-8')\n"
        "print('APPROVED')"
    )


def rejecting_reviewer_command(code: str = "") -> str:
    return python_command(
        "import json, os\n"
        "from pathlib import Path\n"
        + (f"exec({code!r})\n" if code else "")
        + "Path(os.environ['STAGE_REVIEW_VERDICT_FILE']).write_text(\n"
        "    json.dumps({'criteria': [{'criterion': 'criterion', "
        "'verdict': 'FAIL', 'reason': 'reviewer found a blocker'}], "
        "'approved': False}), encoding='utf-8')\n"
        "print('prose says APPROVED and CRITERIA VERDICT: PASS')"
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
    promotion: str = "pending",
    autonomous: bool = False,
    acceptance: tuple[str, ...] = (),
    scope: tuple[str, ...] = (),
    success_criteria: tuple[str, ...] = (),
) -> None:
    current_root = stage_root / "work/current"
    if not parent:
        path = current_root / item_id / "_story.md"
    else:
        parent_path = card_path(stage_root, parent)
        if parent_path.name == "_story.md" and parent_path.parent.parent == current_root:
            epic_path = parent_path.with_name("_epic.md")
            parent_path.replace(epic_path)
            parent_path = epic_path
        if parent_path.name == "_epic.md":
            path = parent_path.parent / item_id / "_story.md"
        elif parent_path.name == "_story.md":
            path = parent_path.parent / f"{item_id}.md"
        else:
            raise AssertionError(f"action cannot parent another fixture: {parent_path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered_acceptance = "[]"
    if acceptance:
        rendered_acceptance = "\n" + "\n".join(
            f"  - {json.dumps(command)}" for command in acceptance
        )
    rendered_criteria = "".join(
        f"- {criterion}\n" for criterion in success_criteria
    )
    path.write_text(
        (
            "---\n"
            f"id: {item_id}\n"
            f"venue: {venue}\n"
            f"status: {status}\n"
            f"promotion: {promotion}\n"
            f"autonomous: {'true' if autonomous else 'false'}\n"
            f"acceptance: {rendered_acceptance}\n"
            f"scope: {', '.join(scope)}\n"
            "---\n\n"
            "## Success criteria\n\n"
            f"{rendered_criteria}"
        ),
        encoding="utf-8",
    )


def card_path(stage_root: Path, item_id: str) -> Path:
    current_root = stage_root / "work/current"
    for path in current_root.rglob("*.md"):
        if path.name == f"{item_id}.md":
            return path
        text = path.read_text(encoding="utf-8")
        if f"id: {item_id}\n" in text:
            return path
    return current_root / item_id / "_story.md"


class DriveTest(unittest.TestCase):
    def make_project(
        self,
        *,
        executor: str | None = PASS_COMMAND,
        reviewer: str = APPROVING_REVIEWER,
        limits: object = None,
        reapers: object = None,
        preflights: object = None,
    ) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        stage_root = root / ".stage"
        stage_root.mkdir()
        settings: dict[str, object] = {
            "schema_version": 5,
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
        if preflights is not None:
            settings["preflights"] = preflights
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

    def test_close_uses_the_promotion_choice_stored_on_the_card(self):
        tmp, root = self.make_project()
        self.addCleanup(tmp.cleanup)
        stage_root = root / ".stage"
        write_card(
            stage_root,
            "W-00000001",
            promotion="deferred",
        )
        drive = self.load_module()
        completed = subprocess.CompletedProcess([], 0, "closed\n", "")

        with mock.patch.object(drive.subprocess, "run", return_value=completed) as run:
            closed, output = drive.close_via_close_work(
                root,
                "W-00000001",
                [],
                30,
                promotion_default="not_applicable",
            )

        self.assertTrue(closed, output)
        command = run.call_args.args[0]
        promotion_index = command.index("--promotion") + 1
        self.assertEqual("deferred", command[promotion_index])

    def test_close_uses_the_default_only_while_the_card_is_pending(self):
        tmp, root = self.make_project()
        self.addCleanup(tmp.cleanup)
        write_card(root / ".stage", "W-00000001", promotion="pending")
        drive = self.load_module()
        completed = subprocess.CompletedProcess([], 0, "closed\n", "")

        with mock.patch.object(drive.subprocess, "run", return_value=completed) as run:
            closed, output = drive.close_via_close_work(
                root,
                "W-00000001",
                [],
                30,
                promotion_default="not_applicable",
            )

        self.assertTrue(closed, output)
        command = run.call_args.args[0]
        promotion_index = command.index("--promotion") + 1
        self.assertEqual("not_applicable", command[promotion_index])

    def test_driver_retrospective_ids_follow_work_items_across_isolated_projects(self):
        drive = self.load_module()
        results: list[tuple[str, str, Path]] = []

        for item_id in ("W-00000227", "W-00000228"):
            tmp, root = self.make_project()
            self.addCleanup(tmp.cleanup)
            stage_root = root / ".stage"
            write_card(stage_root, item_id)
            item = next(
                item
                for item in drive.load_all_work_items(stage_root)
                if item.item_id == item_id
            )

            retro_id, error = drive.write_driver_retrospective(stage_root, item)
            results.append((retro_id, error, stage_root))

        self.assertEqual(
            ["R-00000227", "R-00000228"],
            [retro_id for retro_id, _, _ in results],
        )
        for retro_id, error, stage_root in results:
            self.assertEqual("", error)
            retrospective = stage_root / "work" / "retrospectives" / f"{retro_id}.md"
            self.assertTrue(retrospective.is_file())

    def test_driver_retrospective_refuses_id_owned_by_another_work_item(self):
        tmp, root = self.make_project()
        self.addCleanup(tmp.cleanup)
        stage_root = root / ".stage"
        write_card(stage_root, "W-00000041")
        retrospective_root = stage_root / "work" / "retrospectives"
        retrospective_root.mkdir(parents=True)
        (retrospective_root / "R-00000041.md").write_text(
            "---\nid: R-00000041\nwork_item: W-00000099\n---\n",
            encoding="utf-8",
        )
        drive = self.load_module()
        item = next(
            item
            for item in drive.load_all_work_items(stage_root)
            if item.item_id == "W-00000041"
        )

        retro_id, error = drive.write_driver_retrospective(stage_root, item)

        self.assertEqual("", retro_id)
        self.assertIn("R-00000041", error)
        self.assertIn("W-00000099", error)
        self.assertIn("W-00000041", error)
        self.assertFalse((retrospective_root / "R-00000042.md").exists())

    def test_item_commit_always_includes_the_work_card(self):
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000001",
                scope=("executor-output.txt",),
            )
            initialize_git(root)
            git(root, "checkout", "-q", "-b", "stage/driver/W-00000001-test")
            base_head = git(root, "rev-parse", "HEAD").stdout.strip()
            item_path = card_path(stage_root, "W-00000001")
            item_path.write_text(
                item_path.read_text(encoding="utf-8").replace(
                    "promotion: pending", "promotion: not_applicable"
                ),
                encoding="utf-8",
            )
            (root / "executor-output.txt").write_text("done\n", encoding="utf-8")
            drive = self.load_module()
            item = next(
                item
                for item in drive.load_all_work_items(stage_root)
                if item.item_id == "W-00000001"
            )

            committed, error = drive.commit_item(root, item, base_head)
            committed_paths = set(
                git(root, "show", "--pretty=format:", "--name-only", "HEAD")
                .stdout.strip()
                .splitlines()
            )

        self.assertTrue(committed, error)
        self.assertEqual(
            {
                ".stage/work/current/W-00000001/_story.md",
                "executor-output.txt",
            },
            committed_paths,
        )

    def test_supervised_card_only_change_is_a_rejection_without_spending_attempt(self):
        card_relative = ".stage/work/current/W-00000001/_story.md"
        change_card = (
            "import os; from pathlib import Path; "
            "card = Path(os.environ['STAGE_WORK_ITEM_PATH']); "
            "card.write_text(card.read_text(encoding='utf-8').replace("
            "'promotion: pending', 'promotion: not_applicable'), encoding='utf-8')"
        )
        tmp, root = self.make_project(
            executor=reporting_python_command(change_card, [card_relative]),
        )
        with tmp:
            acceptance_marker = root / "acceptance-ran"
            write_card(
                root / ".stage",
                "W-00000001",
                acceptance=(
                    python_command(
                        "from pathlib import Path; "
                        f"Path({str(acceptance_marker)!r}).touch(); raise SystemExit(9)"
                    ),
                ),
            )
            initialize_git(root)
            base_head = git(root, "rev-parse", "HEAD").stdout.strip()

            result = self.run_cli(root, "--execute")
            state = json.loads(
                (root / ".stage/.runtime/driver/W-00000001.json").read_text(
                    encoding="utf-8"
                )
            )
            log = (
                root / ".stage/.runtime/driver/logs/W-00000001.md"
            ).read_text(encoding="utf-8")
            final_head = git(root, "rev-parse", "HEAD").stdout.strip()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("executor rejected the work item", result.stdout)
        self.assertIn("Reason: executor rejected the work item", log)
        self.assertFalse(acceptance_marker.exists())
        self.assertEqual(0, state["items"]["W-00000001"]["attempt_count"])
        self.assertEqual(base_head, final_head)

    def test_unattended_card_only_change_is_committed_as_a_rejection(self):
        card_relative = ".stage/work/current/W-00000001/_story.md"
        change_card = (
            "import os; from pathlib import Path; "
            "card = Path(os.environ['STAGE_WORK_ITEM_PATH']); "
            "card.write_text(card.read_text(encoding='utf-8').replace("
            "'promotion: pending', 'promotion: not_applicable'), encoding='utf-8')"
        )
        tmp, root = self.make_project(
            executor=reporting_python_command(change_card, [card_relative]),
            limits={
                "max_attempts_per_item": 1,
                "max_iterations": 1,
                "max_wall_clock_seconds": 3600,
            },
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000001",
                autonomous=True,
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)
            drive = self.load_module()
            args = mock.Mock(
                target="W-00000001",
                timeout=30,
                limit_action_seconds=30,
                skip_preflight=True,
            )

            with redirect_stdout(io.StringIO()) as output:
                result = drive.run_unattended(
                    args,
                    root,
                    root / ".stage",
                    drive.time.time(),
                )
            state = json.loads(
                (root / ".stage/.runtime/driver/W-00000001.json").read_text(
                    encoding="utf-8"
                )
            )
            log = (
                root / ".stage/.runtime/driver/logs/W-00000001.md"
            ).read_text(encoding="utf-8")
            committed_paths = set(
                git(root, "show", "--pretty=format:", "--name-only", "HEAD")
                .stdout.strip()
                .splitlines()
            )

        self.assertEqual(0, result, output.getvalue())
        self.assertIn("executor rejected the work item", output.getvalue())
        self.assertIn("Reason: executor rejected the work item", log)
        self.assertEqual(0, state["items"]["W-00000001"]["attempt_count"])
        self.assertEqual({card_relative}, committed_paths)

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
                stage_root / ".runtime/driver/verdicts/W-00000003.json",
                items=items,
            )
            expected_ancestors = [
                str(card_path(stage_root, "W-00000001").resolve()),
                str(card_path(stage_root, "W-00000002").resolve()),
            ]

        self.assertEqual(
            expected_ancestors,
            json.loads(environment["STAGE_WORK_ITEM_ANCESTOR_PATHS"]),
        )
        self.assertEqual(
            str(
                (
                    stage_root
                    / ".runtime/driver/verdicts/W-00000003.json"
                ).resolve()
            ),
            environment["STAGE_REVIEW_VERDICT_FILE"],
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

    def test_reset_attempts_requires_reason(self):
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            drive = self.load_module()
            state_path = stage_root / ".runtime/driver/W-00000001.json"
            state = drive.new_run_state("W-00000001", 1.0)
            state["items"]["W-00000002"] = {
                "attempt_count": 3,
                "last_fingerprint": "old-fingerprint",
                "base_head": "base-head",
                "executor_changed_paths": ["changed.txt"],
                "running_role": None,
            }
            drive.write_run_state(state_path, state)
            before = state_path.read_text(encoding="utf-8")

            result = self.run_cli(root, "--reset-attempts")

            self.assertEqual(before, state_path.read_text(encoding="utf-8"))
            self.assertFalse(
                (stage_root / ".runtime/driver/logs/W-00000002.md").exists()
            )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("--reason is required with --reset-attempts", result.stdout)

    def test_supervised_idle_time_does_not_spend_the_execution_budget(self):
        limits = {
            "max_attempts_per_item": 3,
            "max_iterations": 10,
            "max_wall_clock_seconds": 3600,
        }
        tmp, root = self.make_project(
            executor=reporting_python_command(
                "from pathlib import Path; "
                "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                ["executor-work.txt"],
            ),
            limits=limits,
        )
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)
            state_path = stage_root / ".runtime/driver/W-00000001.json"
            state_path.parent.mkdir(parents=True)
            state = {
                "target": "W-00000001",
                "started_at_unix": 1.0,
                "execution_seconds": 0.0,
                "iteration_count": 0,
                "items": {},
            }
            state_path.write_text(json.dumps(state), encoding="utf-8")

            result = self.run_cli(root, "--execute")
            updated = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Execution time:", result.stdout)
        self.assertGreater(updated["execution_seconds"], 0.0)
        self.assertLess(updated["execution_seconds"], 3600)

    def test_supervised_execution_time_limit_still_blocks_long_execution(self):
        drive = self.load_module()
        limits = {
            "max_attempts_per_item": 3,
            "max_iterations": 10,
            "max_wall_clock_seconds": 3600,
        }

        blocker = drive.limit_blocker(
            limits,
            attempt=1,
            iteration=1,
            execution_seconds=3600.0,
        )

        self.assertEqual(
            "global execution-time limit exceeded before execution",
            blocker,
        )

    def test_supervised_execution_time_limit_blocks_before_next_cli_execution(self):
        limits = {
            "max_attempts_per_item": 3,
            "max_iterations": 10,
            "max_wall_clock_seconds": 3600,
        }
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "executor-ran"
            tmp, root = self.make_project(
                executor=reporting_python_command(
                    "from pathlib import Path; "
                    f"Path({str(marker)!r}).touch(); "
                    "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                    ["executor-work.txt"],
                ),
                limits=limits,
            )
            with tmp:
                stage_root = root / ".stage"
                write_card(
                    stage_root,
                    "W-00000002",
                    parent="W-00000001",
                    acceptance=(PASS_COMMAND,),
                )
                initialize_git(root)
                state_path = stage_root / ".runtime/driver/W-00000001.json"
                state_path.parent.mkdir(parents=True)
                state = {
                    "target": "W-00000001",
                    "started_at_unix": 1.0,
                    "execution_seconds": 3600.0,
                    "iteration_count": 0,
                    "items": {},
                }
                state_path.write_text(json.dumps(state), encoding="utf-8")

                result = self.run_cli(root, "--execute")

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "global execution-time limit exceeded before execution",
            result.stdout,
        )
        self.assertFalse(marker.exists())

    def test_legacy_supervised_state_starts_with_no_execution_time(self):
        tmp, root = self.make_project()
        with tmp:
            drive = self.load_module()
            state_path = root / ".stage/.runtime/driver/W-00000001.json"
            state_path.parent.mkdir(parents=True)
            state_path.write_text(
                json.dumps(
                    {
                        "target": "W-00000001",
                        "started_at_unix": 1.0,
                        "iteration_count": 2,
                        "items": {},
                    }
                ),
                encoding="utf-8",
            )

            state, error = drive.load_run_state(
                state_path,
                "W-00000001",
                now=999999.0,
            )

        self.assertEqual("", error)
        self.assertIsNotNone(state)
        self.assertEqual(0.0, state["execution_seconds"])

    def test_supervised_execution_time_state_must_be_non_negative(self):
        tmp, root = self.make_project()
        with tmp:
            drive = self.load_module()
            state_path = root / ".stage/.runtime/driver/W-00000001.json"
            state_path.parent.mkdir(parents=True)
            for invalid in (-1, True, "1"):
                with self.subTest(invalid=invalid):
                    state_path.write_text(
                        json.dumps(
                            {
                                "target": "W-00000001",
                                "started_at_unix": 1.0,
                                "execution_seconds": invalid,
                                "iteration_count": 0,
                                "items": {},
                            }
                        ),
                        encoding="utf-8",
                    )

                    state, error = drive.load_run_state(
                        state_path,
                        "W-00000001",
                        now=2.0,
                    )

                    self.assertIsNone(state)
                    self.assertIn(
                        "execution_seconds must be a non-negative number",
                        error,
                    )

    def test_reset_attempts_clears_an_interrupted_target_role(self):
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            drive = self.load_module()
            state_path = stage_root / ".runtime/driver/W-00000001.json"
            state = drive.new_run_state("W-00000001", 1.0)
            state["items"]["W-00000002"] = {
                "attempt_count": 3,
                "last_fingerprint": "old-fingerprint",
                "base_head": "base-head",
                "executor_changed_paths": ["changed.txt"],
                "running_role": "executor",
            }
            drive.write_run_state(state_path, state)
            before = state_path.read_text(encoding="utf-8")

            result = self.run_cli(
                root,
                "--reset-attempts",
                "--reason",
                "The card was corrected.",
            )
            updated = json.loads(state_path.read_text(encoding="utf-8"))
            after = state_path.read_text(encoding="utf-8")
            item_state = updated["items"]["W-00000002"]
            log_path = stage_root / ".runtime/driver/logs/W-00000002.md"
            log = log_path.read_text(encoding="utf-8") if log_path.exists() else ""

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotEqual(before, after)
        self.assertEqual(0, item_state["attempt_count"])
        self.assertEqual("", item_state["last_fingerprint"])
        self.assertIsNone(item_state["running_role"])
        self.assertIn("### Attempt limit reset", log)

    def test_reset_attempts_refuses_a_running_sibling_item(self):
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
            drive = self.load_module()
            state_path = stage_root / ".runtime/driver/W-00000001.json"
            state = drive.new_run_state("W-00000001", 1.0)
            state["items"]["W-00000002"] = {
                "attempt_count": 3,
                "last_fingerprint": "old-fingerprint",
                "base_head": "base-head",
                "executor_changed_paths": ["changed.txt"],
                "running_role": "reviewer",
            }
            state["items"]["W-00000003"] = {
                "attempt_count": 1,
                "last_fingerprint": "",
                "base_head": "base-head",
                "executor_changed_paths": [],
                "running_role": "executor",
            }
            drive.write_run_state(state_path, state)
            before = state_path.read_text(encoding="utf-8")

            result = self.run_cli(
                root,
                "--reset-attempts",
                "--reason",
                "The card was corrected.",
            )
            after = state_path.read_text(encoding="utf-8")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            "driver run state has multiple interrupted roles: "
            "W-00000002, W-00000003",
            result.stdout,
        )
        self.assertEqual(before, after)

    def test_reset_attempts_targets_the_item_with_the_interrupted_role(self):
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
            drive = self.load_module()
            state_path = stage_root / ".runtime/driver/W-00000001.json"
            state = drive.new_run_state("W-00000001", 1.0)
            state["items"]["W-00000002"] = {
                "attempt_count": 1,
                "last_fingerprint": "next-ready-fingerprint",
                "base_head": "base-head",
                "executor_changed_paths": ["next-ready.txt"],
                "running_role": None,
            }
            state["items"]["W-00000003"] = {
                "attempt_count": 3,
                "last_fingerprint": "interrupted-fingerprint",
                "base_head": "base-head",
                "executor_changed_paths": ["interrupted.txt"],
                "running_role": "executor",
            }
            drive.write_run_state(state_path, state)

            result = self.run_cli(
                root,
                "--reset-attempts",
                "--reason",
                "The interrupted card was corrected.",
            )
            updated = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Reset attempts for W-00000003", result.stdout)
        self.assertEqual(
            "next-ready-fingerprint",
            updated["items"]["W-00000002"]["last_fingerprint"],
        )
        self.assertEqual(0, updated["items"]["W-00000003"]["attempt_count"])
        self.assertEqual("", updated["items"]["W-00000003"]["last_fingerprint"])
        self.assertIsNone(updated["items"]["W-00000003"]["running_role"])

    def test_reset_attempts_resets_limit_state_and_logs_reason(self):
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            drive = self.load_module()
            state_path = stage_root / ".runtime/driver/W-00000001.json"
            state = drive.new_run_state("W-00000001", 1.0)
            state["iteration_count"] = 2
            state["execution_seconds"] = 123.0
            state["items"]["W-00000002"] = {
                "attempt_count": 3,
                "last_fingerprint": "old-fingerprint",
                "base_head": "base-head",
                "executor_changed_paths": ["changed.txt"],
                "running_role": None,
            }
            drive.write_run_state(state_path, state)

            result = self.run_cli(
                root,
                "--reset-attempts",
                "--reason",
                "The card was corrected.",
            )
            updated = json.loads(state_path.read_text(encoding="utf-8"))
            item_state = updated["items"]["W-00000002"]
            log = (
                stage_root / ".runtime/driver/logs/W-00000002.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Reset attempts for W-00000002", result.stdout)
        self.assertEqual(0, item_state["attempt_count"])
        self.assertEqual("", item_state["last_fingerprint"])
        self.assertEqual("base-head", item_state["base_head"])
        self.assertEqual(["changed.txt"], item_state["executor_changed_paths"])
        self.assertIsNone(item_state["running_role"])
        self.assertGreater(updated["started_at_unix"], 1.0)
        self.assertEqual(0.0, updated["execution_seconds"])
        self.assertEqual(2, updated["iteration_count"])
        self.assertIn("### Attempt limit reset", log)
        self.assertIn("Reason: The card was corrected.", log)

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

    def test_execute_records_the_exact_executor_and_reviewer_commands_in_the_work_log(self):
        executor = reporting_python_command(
            "from pathlib import Path; "
            "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
            ["executor-work.txt"],
        )
        reviewer = approving_reviewer_command()
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
        self.assertIn("### Driver commands", log)
        self.assertIn(f"Executor command: {json.dumps(executor)}", log)
        self.assertIn(f"Reviewer command: {json.dumps(reviewer)}", log)

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
                expected_path = str(
                    card_path(root / ".stage", "W-00000002").resolve()
                )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
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

    def test_execute_unchanged_repository_runs_acceptance_before_review(self):
        completed_path = "already-complete.txt"
        acceptance_marker = "acceptance-ran.txt"
        reviewer = python_command(
            "import json, os\n"
            "from pathlib import Path\n"
            "changed = json.loads(Path(os.environ["
            "'STAGE_CHANGED_PATHS_FILE']).read_text(encoding='utf-8'))\n"
            f"assert changed == [{completed_path!r}]\n"
            "Path(os.environ['STAGE_REVIEW_VERDICT_FILE']).write_text(\n"
            "    json.dumps({'criteria': [{'criterion': 'criterion', "
            "'verdict': 'PASS', 'reason': 'the completed work passed review'}], "
            "'approved': True}), encoding='utf-8')\n"
        )
        tmp, root = self.make_project(
            executor=reporting_python_command("pass", [completed_path]),
            reviewer=reviewer,
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(
                    python_command(
                        "from pathlib import Path; "
                        f"Path({acceptance_marker!r}).write_text("
                        "'ran', encoding='utf-8')"
                    ),
                ),
            )
            initialize_git(root)
            (root / completed_path).write_text("done\n", encoding="utf-8")
            drive = self.load_module()
            state_path = root / ".stage/.runtime/driver/W-00000001.json"
            state_path.parent.mkdir(parents=True)
            state = drive.new_run_state("W-00000001", 1.0)
            state["items"]["W-00000002"] = {
                "attempt_count": 1,
                "last_fingerprint": "",
                "last_no_change_fingerprint": "",
                "base_head": git(root, "rev-parse", "HEAD").stdout.strip(),
                "executor_changed_paths": [completed_path],
                "running_role": None,
            }
            drive.write_run_state(state_path, state)

            result = self.run_cli(root, "--execute")
            state = json.loads(
                (
                    root / ".stage/.runtime/driver/W-00000001.json"
                ).read_text(encoding="utf-8")
            )
            acceptance_result = (root / acceptance_marker).read_text(
                encoding="utf-8"
            )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Acceptance result:", result.stdout)
        self.assertIn("Independent reviewer result:", result.stdout)
        self.assertIn(
            "executor, acceptance, and independent reviewer passed",
            result.stdout,
        )
        self.assertEqual("ran", acceptance_result)
        self.assertEqual(2, state["items"]["W-00000002"]["attempt_count"])

    def test_command_timeout_uses_declared_size_and_unfinished_children(self):
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000001",
                scope=("one", "two", "three", "four"),
                success_criteria=("first", "second"),
            )
            drive = self.load_module()
            scope_items = drive.load_all_work_items(stage_root)

            self.assertEqual(
                4 * drive.MIN_COMMAND_TIMEOUT_SECONDS,
                drive.subtree_command_timeout(
                    "W-00000001", scope_items, requested=None
                ),
            )

            write_card(
                stage_root,
                "W-00000001",
                scope=("one",),
                success_criteria=("first",),
            )
            for suffix in range(2, 5):
                write_card(
                    stage_root,
                    f"W-0000000{suffix}",
                    parent="W-00000001",
                    acceptance=(PASS_COMMAND,),
                )
            child_items = drive.load_all_work_items(stage_root)

            self.assertEqual(
                3 * drive.MIN_COMMAND_TIMEOUT_SECONDS,
                drive.subtree_command_timeout(
                    "W-00000001", child_items, requested=None
                ),
            )
            self.assertEqual(
                17,
                drive.subtree_command_timeout(
                    "W-00000001", child_items, requested=17
                ),
            )

    def test_execute_unchanged_repository_stops_when_acceptance_fails(self):
        completed_path = "already-complete.txt"
        reviewer_marker = "reviewer-ran.txt"
        tmp, root = self.make_project(
            executor=reporting_python_command("pass", [completed_path]),
            reviewer=python_command(
                "from pathlib import Path; "
                f"Path({reviewer_marker!r}).write_text('ran', encoding='utf-8')"
            ),
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(python_command("raise SystemExit(9)"),),
            )
            initialize_git(root)
            (root / completed_path).write_text("done\n", encoding="utf-8")
            drive = self.load_module()
            state_path = root / ".stage/.runtime/driver/W-00000001.json"
            state_path.parent.mkdir(parents=True)
            state = drive.new_run_state("W-00000001", 1.0)
            state["items"]["W-00000002"] = {
                "attempt_count": 1,
                "last_fingerprint": "",
                "last_no_change_fingerprint": "",
                "base_head": git(root, "rev-parse", "HEAD").stdout.strip(),
                "executor_changed_paths": [completed_path],
                "running_role": None,
            }
            drive.write_run_state(state_path, state)

            result = self.run_cli(root, "--execute")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("Acceptance result:", result.stdout)
        self.assertIn("acceptance check failed", result.stdout)
        self.assertNotIn("Independent reviewer result:", result.stdout)
        self.assertFalse((root / reviewer_marker).exists())

    def test_execute_unchanged_repository_without_report_still_fails(self):
        tmp, root = self.make_project(executor=PASS_COMMAND)
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)

            result = self.run_cli(root, "--execute")
            state = json.loads(
                (
                    root / ".stage/.runtime/driver/W-00000001.json"
                ).read_text(encoding="utf-8")
            )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("executor did not append a work log report", result.stdout)
        self.assertEqual(1, state["items"]["W-00000002"]["attempt_count"])

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
                    str(card_path(stage_root, "W-00000002").resolve()),
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

    def test_child_commands_split_project_environment_contract(self):
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "child-environments.jsonl"

            def record_environment(role: str) -> str:
                return (
                    "import json, os; from pathlib import Path; "
                    f"Path({str(marker)!r}).open('a', encoding='utf-8').write("
                    f"json.dumps({{'role': {role!r}, "
                    "'CLAUDE_PROJECT_DIR': os.environ.get('CLAUDE_PROJECT_DIR'), "
                    "'PROJECT_ROOT': os.environ.get('PROJECT_ROOT')}) + '\\n')"
                )

            executor = reporting_python_command(
                record_environment("executor")
                + "; Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                ["executor-work.txt"],
            )
            reviewer = approving_reviewer_command(record_environment("reviewer"))
            preflight = python_command(record_environment("preflight"))
            acceptance = python_command(record_environment("acceptance"))
            tmp, root = self.make_project(
                executor=executor,
                reviewer=reviewer,
                preflights={"codex": preflight},
            )
            with tmp:
                stage_root = root / ".stage"
                write_card(
                    stage_root,
                    "W-00000002",
                    parent="W-00000001",
                    acceptance=(acceptance,),
                )
                initialize_git(root)

                with mock.patch.dict(
                    os.environ,
                    {
                        "CLAUDE_PROJECT_DIR": "/wrong/main-checkout",
                        "PROJECT_ROOT": "/wrong/main-checkout",
                    },
                ):
                    result = self.run_cli(root, "--execute")

                self.assertEqual(
                    0, result.returncode, result.stdout + result.stderr
                )
                environments = [
                    json.loads(line)
                    for line in marker.read_text(encoding="utf-8").splitlines()
                ]
                self.assertEqual(
                    ["preflight", "executor", "acceptance", "reviewer"],
                    [environment["role"] for environment in environments],
                )
                session_environments = [
                    environment
                    for environment in environments
                    if environment["role"] != "acceptance"
                ]
                for environment in session_environments:
                    self.assertEqual(
                        str(root.resolve()),
                        environment["CLAUDE_PROJECT_DIR"],
                    )
                    self.assertEqual(
                        str(root.resolve()),
                        environment["PROJECT_ROOT"],
                    )
                acceptance_environment = environments[2]
                self.assertIsNone(
                    acceptance_environment["CLAUDE_PROJECT_DIR"]
                )
                self.assertIsNone(acceptance_environment["PROJECT_ROOT"])

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
                    str(card_path(stage_root, "W-00000002").resolve()),
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

    def test_second_review_only_rechecks_failures_and_changed_segment(self):
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "round"
            capture = Path(marker_tmp) / "reviewer-input.json"
            tmp, root = self.make_project(
                executor=narrowing_executor_command(marker),
                reviewer=narrowing_reviewer_command(marker, capture),
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
                verdict = json.loads(
                    (
                        root
                        / ".stage/.runtime/driver/verdicts/W-00000002.json"
                    ).read_text(encoding="utf-8")
                )

            self.assertNotEqual(0, first.returncode)
            self.assertEqual(
                0, second.returncode, second.stdout + second.stderr
            )
            reviewer_input = json.loads(capture.read_text(encoding="utf-8"))
            self.assertEqual(["failing criterion"], reviewer_input["failed"])
            self.assertEqual(["round-2.txt"], reviewer_input["changed"])
            self.assertEqual(
                [
                    {
                        "criterion": "passing criterion",
                        "verdict": "PASS",
                        "reason": "the first review passed it",
                        "reviewed_in_round": 1,
                    },
                    {
                        "criterion": "failing criterion",
                        "verdict": "PASS",
                        "reason": "the second review confirmed the fix",
                        "reviewed_in_round": 2,
                    },
                ],
                verdict["criteria"],
            )
            self.assertTrue(verdict["approved"])

    def test_missing_previous_verdict_falls_back_to_full_review(self):
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "round"
            capture = Path(marker_tmp) / "reviewer-input.json"
            tmp, root = self.make_project(
                executor=narrowing_executor_command(marker),
                reviewer=missing_verdict_then_full_reviewer_command(
                    marker, capture
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

                first = self.run_cli(root, "--execute")
                second = self.run_cli(root, "--execute")

            self.assertNotEqual(0, first.returncode)
            self.assertEqual(
                0, second.returncode, second.stdout + second.stderr
            )
            reviewer_input = json.loads(capture.read_text(encoding="utf-8"))
            self.assertEqual("full", reviewer_input["mode"])
            self.assertFalse(reviewer_input["has_previous"])
            self.assertFalse(reviewer_input["has_failed"])
            self.assertEqual(
                ["round-1.txt", "round-2.txt"],
                reviewer_input["changed"],
            )

    def test_supervised_comparison_ignores_driver_owned_work_log_path(self):
        work_log_path = ".stage/.runtime/driver/logs/W-00000002.md"
        executor = reporting_python_command(
            "from pathlib import Path; "
            "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
            [work_log_path, "executor-work.txt"],
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

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_supervised_retry_keeps_executor_paths_and_excludes_intervening_human_commit(
        self,
    ):
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "round"
            tmp, root = self.make_project(
                executor=cumulative_retry_executor_command(marker),
                reviewer=retry_reviewer_command(marker),
                limits={
                    "max_attempts_per_item": 3,
                    "max_iterations": 10,
                    "max_wall_clock_seconds": 300,
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

                first = self.run_cli(root, "--execute")
                (root / "human-between-attempts.txt").write_text(
                    "human\n",
                    encoding="utf-8",
                )
                git(root, "add", "human-between-attempts.txt")
                git(root, "commit", "-q", "-m", "human between attempts")
                second = self.run_cli(root, "--execute")
                first_round = (root / "first-round.txt").read_text(encoding="utf-8")
                second_round = (root / "second-round.txt").read_text(encoding="utf-8")

        self.assertNotEqual(0, first.returncode)
        self.assertEqual(0, second.returncode, second.stdout + second.stderr)
        self.assertEqual("first", first_round)
        self.assertEqual("second", second_round)

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
            state = json.loads(
                (
                    root / ".stage/.runtime/driver/W-00000001.json"
                ).read_text(encoding="utf-8")
            )

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
            self.assertEqual(
                ["failed-artifact.txt"],
                state["items"]["W-00000002"]["executor_changed_paths"],
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
            state = json.loads(
                (
                    root / ".stage/.runtime/driver/W-00000001.json"
                ).read_text(encoding="utf-8")
            )
            item_state = state["items"]["W-00000002"]

        self.assertEqual(1, state["iteration_count"])
        self.assertGreater(state["execution_seconds"], 0.0)
        self.assertEqual(1, item_state["attempt_count"])
        self.assertIsNone(item_state["running_role"])

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
                '{"schema_version": 5}\n', encoding="utf-8"
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
                '{"schema_version": 5}\n', encoding="utf-8"
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

    def test_executor_intact_stale_log_rewrite_restores_driver_commands(self):
        executor = stale_log_rewrite_command(
            "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
            ["executor-work.txt"],
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
            log = (
                root / ".stage/.runtime/driver/logs/W-00000002.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(1, log.splitlines().count("### Driver commands"))
        self.assertEqual(1, log.splitlines().count("### Executor report"))
        self.assertLess(
            log.index("### Driver commands"),
            log.index("### Executor report"),
        )

    def test_executor_log_rewrite_still_fails_when_prior_content_is_lost(self):
        executor = python_command(
            "import json, os\n"
            "from pathlib import Path\n"
            "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')\n"
            "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
            "report = ('### Executor report\\n"
            "What changed: replaced the prior work log\\n"
            "Why: exercise the data-loss boundary\\n"
            "Decisions made: None\\n"
            "Work not done: None\\n"
            "Changed paths (JSON):\\n' + json.dumps(['executor-work.txt']) + '\\n"
            "Review request: reject the lost prior record\\n')\n"
            "log.write_text(report, encoding='utf-8')\n"
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
            log = (
                root / ".stage/.runtime/driver/logs/W-00000002.md"
            ).read_text(encoding="utf-8")

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "executor rewrote existing work log content instead of appending",
            result.stdout,
        )
        self.assertNotIn("Acceptance result:", result.stdout)
        self.assertIn("## 책임 경계", log)
        self.assertIn("### Driver commands", log)
        self.assertEqual(0, log.splitlines().count("### Executor report"))
        self.assertIn("### Driver failure", log)

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

    def test_supervised_reasoned_decline_allows_empty_changed_paths(self):
        finding = "unsupported fictional host"
        executor = python_command(
            "import json, os\n"
            "from pathlib import Path\n"
            "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
            "report = ('\\n### Executor report\\n"
            "What changed: declined the pending fictional-host finding\\n"
            "Why: that host cannot run this project\\n"
            "Changed paths (JSON):\\n[]\\n"
            "Review dispositions (JSON):\\n' + "
            f"json.dumps([{{'finding': {finding!r}, 'disposition': 'decline', "
            "'reason': 'that host cannot run this project'}]) + '\\n"
            "Review request: recheck the reasoned disposition\\n')\n"
            "log.write_text(log.read_text(encoding='utf-8') + report, "
            "encoding='utf-8')\n"
        )
        tmp, root = self.make_project(
            executor=executor,
            reviewer=python_command(
                "import json, os\n"
                "from pathlib import Path\n"
                "Path(os.environ['STAGE_REVIEW_VERDICT_FILE']).write_text(\n"
                "    json.dumps({'criteria': [{"
                f"'criterion': {finding!r}, "
                "'verdict': 'PASS', "
                "'reason': 'the disposition resolves this criterion'}], "
                "'approved': True}), encoding='utf-8')\n"
            ),
        )
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)
            verdict_file = (
                stage_root
                / ".runtime/driver/verdicts/W-00000002.json"
            )
            verdict_file.parent.mkdir(parents=True, exist_ok=True)
            verdict_file.write_text(
                json.dumps(
                    {
                        "criteria": [
                            {
                                "criterion": finding,
                                "verdict": "FAIL",
                                "reason": "reviewer requested a fictional host",
                            }
                        ],
                        "approved": False,
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_cli(root, "--execute")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("executor, acceptance, and independent reviewer passed", result.stdout)

    def test_reviewer_prose_labels_do_not_override_approved_json(self):
        misleading_prose = (
            "import os\n"
            "from pathlib import Path\n"
            "log = Path(os.environ['STAGE_WORK_LOG_PATH'])\n"
            "with log.open('a', encoding='utf-8') as handle:\n"
            "    handle.write('\\n### Reviewer report\\n"
            "CRITERIA VERDICT: FAIL APPROVED `### Reviewer report`\\n')"
        )
        executor = reporting_python_command(
            "from pathlib import Path; "
            "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
            ["executor-work.txt"],
        )
        tmp, root = self.make_project(
            executor=executor,
            reviewer=approving_reviewer_command(misleading_prose),
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

    def test_reviewer_must_write_verdict_file(self):
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
            "review verdict file is missing",
            result.stdout,
        )

    def test_failed_json_review_verdict_recommends_escalation(self):
        with tempfile.TemporaryDirectory() as marker_tmp:
            reviewer_reaped = Path(marker_tmp) / "reviewer-reaped"
            tmp, root = self.make_project(
                executor=reporting_python_command(
                    "from pathlib import Path; "
                    "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                    ["executor-work.txt"],
                ),
                reviewer=rejecting_reviewer_command(),
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
            self.assertIn("review verdict did not approve", result.stdout)
            self.assertIn("→ escalate_work", result.stdout)
            self.assertTrue(reviewer_reaped.exists())

    def test_reviewer_command_failure_output_is_appended_to_shared_work_log(self):
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
        self.assertIn("Reason: review verdict file is missing", log)
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

    def test_preflight_failure_stops_before_executor_and_attempt_state(self):
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker = Path(marker_tmp) / "executor-ran"
            tmp, root = self.make_project(
                executor=python_command(
                    "from pathlib import Path; "
                    f"Path({str(marker)!r}).write_text('ran', encoding='utf-8')"
                ),
                preflights={"codex": python_command("raise SystemExit(7)")},
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
            self.assertIn("preflights.codex failed before attempt", result.stdout)
            self.assertIn("[exit 7]", result.stdout)
            self.assertNotIn("escalate_work", result.stdout)
            self.assertFalse(marker.exists())
            self.assertFalse(
                (root / ".stage/.runtime/driver/W-00000001.json").exists()
            )

    def test_preflight_timeout_stops_without_attempt_state(self):
        tmp, root = self.make_project(
            preflights={
                "codex": python_command("import time; time.sleep(5)")
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

            result = self.run_cli(root, "--execute", "--timeout", "1")

            self.assertNotEqual(0, result.returncode)
            self.assertIn("preflights.codex failed before attempt", result.stdout)
            self.assertIn("[TIMED OUT after 1s]", result.stdout)
            self.assertNotIn("escalate_work", result.stdout)
            self.assertFalse(
                (root / ".stage/.runtime/driver/W-00000001.json").exists()
            )

    def test_missing_preflight_warns_but_explicit_null_is_silent(self):
        drive = self.load_module()
        tmp, root = self.make_project()
        with tmp:
            item = drive.load_all_work_items(root / ".stage")[0]
            missing_output = io.StringIO()
            with (
                mock.patch.object(
                    drive,
                    "load_preflights_config",
                    return_value=None,
                ),
                redirect_stdout(missing_output),
            ):
                missing_ok = drive.run_preflight(
                    stage_root=root / ".stage",
                    project_root=root,
                    item=item,
                    items=[item],
                    timeout=1,
                    skip=False,
                )

            declared_output = io.StringIO()
            with (
                mock.patch.object(
                    drive,
                    "load_preflights_config",
                    return_value={"codex": None},
                ),
                redirect_stdout(declared_output),
            ):
                declared_ok = drive.run_preflight(
                    stage_root=root / ".stage",
                    project_root=root,
                    item=item,
                    items=[item],
                    timeout=1,
                    skip=False,
                )

            with mock.patch.object(
                drive,
                "load_preflights_config",
                return_value={"codex": PASS_COMMAND},
            ):
                passed_ok = drive.run_preflight(
                    stage_root=root / ".stage",
                    project_root=root,
                    item=item,
                    items=[item],
                    timeout=1,
                    skip=False,
                )

            work_log_exists = (
                root / ".stage/.runtime/driver/logs/W-00000001.md"
            ).exists()

        self.assertEqual(
            (None, False, ""),
            drive.resolve_preflight_command(None, "codex"),
        )
        self.assertEqual(
            (None, True, ""),
            drive.resolve_preflight_command({"codex": None}, "codex"),
        )
        self.assertTrue(missing_ok)
        self.assertIn(
            "WARNING: preflights.codex is not configured",
            missing_output.getvalue(),
        )
        self.assertTrue(declared_ok)
        self.assertEqual("", declared_output.getvalue())
        self.assertTrue(passed_ok)
        self.assertFalse(work_log_exists)

    def test_skip_preflight_runs_executor_for_human_recovery(self):
        tmp, root = self.make_project(
            executor=reporting_python_command(
                "from pathlib import Path; "
                "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                ["executor-work.txt"],
            ),
            preflights={"codex": python_command("raise SystemExit(7)")},
        )
        with tmp:
            write_card(
                root / ".stage",
                "W-00000002",
                parent="W-00000001",
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)

            result = self.run_cli(root, "--execute", "--skip-preflight")
            work_log = (
                root / ".stage/.runtime/driver/logs/W-00000002.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("WARNING: preflight skipped by operator", result.stdout)
        self.assertIn(
            "WARNING: preflight skipped by operator for recovery; "
            "preflights.codex was not run",
            work_log,
        )

    def test_run_state_records_the_role_before_each_external_turn(self):
        target = "W-00000001"
        selected = "W-00000002"
        state_path = f".stage/.runtime/driver/{target}.json"
        executor = reporting_python_command(
            "import json; from pathlib import Path; "
            f"state = json.loads(Path({state_path!r}).read_text(encoding='utf-8')); "
            f"assert state['items'][{selected!r}]['running_role'] == 'executor'; "
            f"assert state['items'][{selected!r}]['attempt_count'] == 1; "
            "assert state['iteration_count'] == 1; "
            "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
            ["executor-work.txt"],
        )
        reviewer = approving_reviewer_command(
            "import json; from pathlib import Path; "
            f"state = json.loads(Path({state_path!r}).read_text(encoding='utf-8')); "
            f"assert state['items'][{selected!r}]['running_role'] == 'reviewer'; "
            f"assert state['items'][{selected!r}]['attempt_count'] == 1; "
            "assert state['iteration_count'] == 1"
        )
        tmp, root = self.make_project(executor=executor, reviewer=reviewer)
        with tmp:
            write_card(
                root / ".stage",
                selected,
                parent=target,
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)

            result = self.run_cli(root, "--execute")
            state = json.loads(
                (root / state_path).read_text(encoding="utf-8")
            )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIsNone(state["items"][selected]["running_role"])

    def test_started_round_survives_termination_during_executor_call(self):
        target = "W-00000001"
        selected = "W-00000002"
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                selected,
                parent=target,
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)
            drive = self.load_module()
            state_path = stage_root / f".runtime/driver/{target}.json"
            argv = [
                str(SCRIPT),
                "--project-root",
                str(root),
                "--execute",
                target,
            ]

            def terminate_during_executor(*_args, **_kwargs):
                running_state = json.loads(state_path.read_text(encoding="utf-8"))
                running_item = running_state["items"][selected]
                self.assertEqual(1, running_state["iteration_count"])
                self.assertEqual(1, running_item["attempt_count"])
                self.assertEqual("executor", running_item["running_role"])
                raise SystemExit("simulated termination during executor call")

            with (
                mock.patch.object(sys, "argv", argv),
                mock.patch.object(
                    drive,
                    "timed_run_check",
                    side_effect=terminate_during_executor,
                ),
                self.assertRaisesRegex(
                    SystemExit,
                    "simulated termination during executor call",
                ),
            ):
                drive.main()

            state = json.loads(state_path.read_text(encoding="utf-8"))
            item_state = state["items"][selected]
            resumed = self.run_cli(root, "--resume")

        self.assertEqual(1, state["iteration_count"])
        self.assertEqual(1, item_state["attempt_count"])
        self.assertEqual("executor", item_state["running_role"])
        self.assertNotEqual(0, resumed.returncode)
        self.assertIn(
            "interrupted driver state has no completed-stage checkpoint",
            resumed.stdout,
        )

    def test_completed_executor_time_survives_termination_during_reaping(self):
        target = "W-00000001"
        selected = "W-00000002"
        tmp, root = self.make_project(
            executor=reporting_python_command(
                "from pathlib import Path; "
                "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                ["executor-work.txt"],
            )
        )
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                selected,
                parent=target,
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)
            drive = self.load_module()
            argv = [
                str(SCRIPT),
                "--project-root",
                str(root),
                "--execute",
                target,
            ]

            with (
                mock.patch.object(sys, "argv", argv),
                mock.patch.object(
                    drive,
                    "reap_turn",
                    side_effect=SystemExit("simulated driver termination"),
                ),
                self.assertRaisesRegex(
                    SystemExit,
                    "simulated driver termination",
                ),
            ):
                drive.main()

            state = json.loads(
                (
                    stage_root / f".runtime/driver/{target}.json"
                ).read_text(encoding="utf-8")
            )
            item_state = state["items"][selected]

            resumed = self.run_cli(root, "--resume")
            resumed_state = json.loads(
                (
                    stage_root / f".runtime/driver/{target}.json"
                ).read_text(encoding="utf-8")
            )
            log = (
                stage_root / f".runtime/driver/logs/{selected}.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(1, state["iteration_count"])
        self.assertGreater(state["execution_seconds"], 0.0)
        self.assertEqual(1, item_state["attempt_count"])
        self.assertEqual("executor", item_state["running_role"])
        self.assertTrue(item_state["resume_repository_fingerprint"])
        self.assertEqual(0, resumed.returncode, resumed.stdout + resumed.stderr)
        self.assertIn("Resuming after completed executor", resumed.stdout)
        self.assertNotIn("Executor result:", resumed.stdout)
        self.assertIn("Acceptance result:", resumed.stdout)
        self.assertIn("Independent reviewer result:", resumed.stdout)
        self.assertEqual(
            1,
            sum(line == "### Executor report" for line in log.splitlines()),
        )
        self.assertIsNone(resumed_state["items"][selected]["running_role"])

    def test_resume_refuses_to_skip_executor_after_repository_changes(self):
        target = "W-00000001"
        selected = "W-00000002"
        tmp, root = self.make_project()
        with tmp:
            stage_root = root / ".stage"
            write_card(
                stage_root,
                selected,
                parent=target,
                acceptance=(PASS_COMMAND,),
            )
            initialize_git(root)
            drive = self.load_module()
            state_path = stage_root / f".runtime/driver/{target}.json"
            state = drive.new_run_state(target, 1.0)
            state["iteration_count"] = 1
            state["items"][selected] = {
                "attempt_count": 1,
                "last_fingerprint": "",
                "last_no_change_fingerprint": "",
                "base_head": git(root, "rev-parse", "HEAD").stdout.strip(),
                "executor_changed_paths": ["executor-work.txt"],
                "running_role": "executor",
                "resume_repository_fingerprint": drive.repository_fingerprint(root),
                "resume_review_changed_paths": ["executor-work.txt"],
                "resume_acceptance_output": [],
                "resume_previous_verdict": None,
            }
            drive.write_run_state(state_path, state)
            (root / "changed-after-driver-death.txt").write_text(
                "changed\n", encoding="utf-8"
            )

            result = self.run_cli(root, "--resume")
            unchanged_state = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "repository changed after the interrupted driver checkpoint",
            result.stdout,
        )
        self.assertEqual("executor", unchanged_state["items"][selected]["running_role"])

    def test_resume_from_reviewer_skips_executor_and_acceptance(self):
        target = "W-00000001"
        selected = "W-00000002"
        with tempfile.TemporaryDirectory() as marker_tmp:
            marker_root = Path(marker_tmp)
            executor_marker = marker_root / "executor-count"
            acceptance_marker = marker_root / "acceptance-count"
            reviewer_marker = marker_root / "reviewer-count"

            def increment(path: Path) -> str:
                return (
                    f"path = Path({str(path)!r}); "
                    "path.write_text(str(int(path.read_text(encoding='utf-8')) + 1) "
                    "if path.exists() else '1', encoding='utf-8')"
                )

            executor = reporting_python_command(
                "from pathlib import Path; "
                + increment(executor_marker)
                + "; Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                ["executor-work.txt"],
            )
            acceptance = python_command(
                "from pathlib import Path; " + increment(acceptance_marker)
            )
            reviewer = approving_reviewer_command(
                "from pathlib import Path; " + increment(reviewer_marker)
            )
            tmp, root = self.make_project(executor=executor, reviewer=reviewer)
            with tmp:
                stage_root = root / ".stage"
                write_card(
                    stage_root,
                    selected,
                    parent=target,
                    acceptance=(acceptance,),
                )
                initialize_git(root)
                drive = self.load_module()
                state_path = stage_root / f".runtime/driver/{target}.json"
                argv = [
                    str(SCRIPT),
                    "--project-root",
                    str(root),
                    "--execute",
                    target,
                ]

                def terminate_after_review(*_args, **kwargs):
                    if kwargs["role"] == "reviewer":
                        raise SystemExit("simulated termination after reviewer")
                    return True

                with (
                    mock.patch.object(sys, "argv", argv),
                    mock.patch.object(
                        drive,
                        "reap_turn",
                        side_effect=terminate_after_review,
                    ),
                    self.assertRaisesRegex(
                        SystemExit,
                        "simulated termination after reviewer",
                    ),
                ):
                    drive.main()

                interrupted = json.loads(state_path.read_text(encoding="utf-8"))
                resumed = self.run_cli(root, "--resume")
                completed = json.loads(state_path.read_text(encoding="utf-8"))
                executor_count = executor_marker.read_text(encoding="utf-8")
                acceptance_count = acceptance_marker.read_text(encoding="utf-8")
                reviewer_count = reviewer_marker.read_text(encoding="utf-8")

        self.assertEqual(
            "reviewer",
            interrupted["items"][selected]["running_role"],
        )
        self.assertEqual(0, resumed.returncode, resumed.stdout + resumed.stderr)
        self.assertIn("Resuming after completed reviewer", resumed.stdout)
        self.assertNotIn("Executor result:", resumed.stdout)
        self.assertNotIn("Acceptance result:", resumed.stdout)
        self.assertIn("Independent reviewer result:", resumed.stdout)
        self.assertEqual("1", executor_count)
        self.assertEqual("1", acceptance_count)
        self.assertEqual("2", reviewer_count)
        self.assertIsNone(completed["items"][selected]["running_role"])

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

    def test_infrastructure_failure_recognizes_existing_markers(self):
        drive = self.load_module()

        for marker in (
            "timed out",
            "command not found",
            "[exit 126]",
            "[exit 127]",
            "terminated by signal",
            "killed by signal",
        ):
            with self.subTest(marker=marker):
                self.assertTrue(drive.infrastructure_failure(marker))

        self.assertFalse(drive.infrastructure_failure("[exit 2]\nsubstantive failure"))

    def test_supervised_infrastructure_failures_do_not_spend_attempt(self):
        cases = (
            {
                "name": "executor",
                "executor": python_command(
                    "print('command not found'); raise SystemExit(2)"
                ),
                "acceptance": PASS_COMMAND,
                "reviewer": APPROVING_REVIEWER,
            },
            {
                "name": "acceptance",
                "executor": reporting_python_command(
                    "from pathlib import Path; "
                    "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                    ["executor-work.txt"],
                ),
                "acceptance": python_command(
                    "print('terminated by signal'); raise SystemExit(2)"
                ),
                "reviewer": APPROVING_REVIEWER,
            },
            {
                "name": "reviewer",
                "executor": reporting_python_command(
                    "from pathlib import Path; "
                    "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                    ["executor-work.txt"],
                ),
                "acceptance": PASS_COMMAND,
                "reviewer": python_command(
                    "print('killed by signal'); raise SystemExit(2)"
                ),
            },
        )

        for case in cases:
            with self.subTest(role=case["name"]):
                tmp, root = self.make_project(
                    executor=case["executor"],
                    reviewer=case["reviewer"],
                    limits={
                        "max_attempts_per_item": 1,
                        "max_iterations": 10,
                        "max_wall_clock_seconds": 3600,
                    },
                )
                with tmp:
                    write_card(
                        root / ".stage",
                        "W-00000001",
                        acceptance=(case["acceptance"],),
                    )
                    initialize_git(root)

                    result = self.run_cli(root, "--execute")
                    state = json.loads(
                        (
                            root / ".stage/.runtime/driver/W-00000001.json"
                        ).read_text(encoding="utf-8")
                    )

                self.assertNotEqual(0, result.returncode)
                self.assertNotIn("per-item attempt cap reached", result.stdout)
                self.assertEqual(
                    0,
                    state["items"]["W-00000001"]["attempt_count"],
                    result.stdout + result.stderr,
                )

    def test_supervised_substantive_failures_spend_attempt(self):
        cases = (
            {
                "name": "executor",
                "executor": python_command("raise SystemExit(2)"),
                "acceptance": PASS_COMMAND,
                "reviewer": APPROVING_REVIEWER,
            },
            {
                "name": "acceptance",
                "executor": reporting_python_command(
                    "from pathlib import Path; "
                    "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                    ["executor-work.txt"],
                ),
                "acceptance": python_command("raise SystemExit(2)"),
                "reviewer": APPROVING_REVIEWER,
            },
            {
                "name": "reviewer",
                "executor": reporting_python_command(
                    "from pathlib import Path; "
                    "Path('executor-work.txt').write_text('done\\n', encoding='utf-8')",
                    ["executor-work.txt"],
                ),
                "acceptance": PASS_COMMAND,
                "reviewer": rejecting_reviewer_command(),
            },
        )

        for case in cases:
            with self.subTest(role=case["name"]):
                tmp, root = self.make_project(
                    executor=case["executor"],
                    reviewer=case["reviewer"],
                )
                with tmp:
                    write_card(
                        root / ".stage",
                        "W-00000001",
                        acceptance=(case["acceptance"],),
                    )
                    initialize_git(root)

                    result = self.run_cli(root, "--execute")
                    state = json.loads(
                        (
                            root / ".stage/.runtime/driver/W-00000001.json"
                        ).read_text(encoding="utf-8")
                    )

                self.assertNotEqual(0, result.returncode)
                self.assertEqual(
                    1,
                    state["items"]["W-00000001"]["attempt_count"],
                    result.stdout + result.stderr,
                )

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
