"""A review at close cannot hide what it did by putting the tree back (W-00000416).

`test_claude_review_guard.py` covers a review that leaves a repository file changed.
These tests cover what that comparison let through: a file changed and restored, a
write to a file Git ignores, and a reviewer that reads records outside the repository.
The reviewers here are plain Python commands, so no model runs.
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path, PureWindowsPath

from python_shell_command import python_command
from test_claude_review_guard import (
    APPROVED,
    CARD_RELATIVE,
    ITEM_ID,
    VERDICT_RELATIVE,
    git,
    make_repository,
    probe_module,
)

STAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(STAGE / "scripts"))
sys.path.insert(0, str(STAGE / "skills" / "stage-retrospective"))
import claude_review_companion  # noqa: E402
import close_work  # noqa: E402
import review_containment  # noqa: E402

WRITE_VERDICT = (
    "open(os.environ['STAGE_REVIEW_VERDICT_FILE'], 'w', encoding='utf-8').write("
    f"json.dumps({APPROVED!r}))\n"
)
PREAMBLE = "import json, os, subprocess\nfrom pathlib import Path\n"


def reviewer(steps: str) -> str:
    """A reviewer that runs `steps` in the project root and then approves."""

    return python_command(PREAMBLE + steps + WRITE_VERDICT)


def recording_reviewer(calls: list[dict[str, object]], complete: bool = True) -> str:
    """A reviewer whose command records `calls` the way the Claude stand-in does."""

    lines = [json.dumps(call) for call in calls]
    if complete:
        lines.append(json.dumps({"complete": True, "denied": ["refused"]}))
    return reviewer(
        f"Path(os.environ[{review_containment.TOOL_CALLS_ENV!r}]).write_text("
        f"{chr(10).join(lines) + chr(10)!r}, encoding='utf-8')\n"
    )


def shell_call(command: str, call_id: str = "ran") -> dict[str, object]:
    return {"id": call_id, "tool": "Bash", "input": {"command": command}}


class CloseReviewContainmentTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "project"
        self.root.mkdir()
        self.card = make_repository(self.root, probe_module())
        (self.root / ".gitignore").write_text(
            ".stage/.runtime/\n__pycache__/\n*.local\n", encoding="utf-8"
        )
        git(self.root, "commit", "-q", "-am", "ignore local files")

    def review(self, command: str) -> tuple[bool, str, review_containment.ReviewTraces, str]:
        traces: list[review_containment.ReviewTraces] = []
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            passed, detail = close_work.run_close_review(
                self.root, self.card, ITEM_ID, command, 120, 1800, traces=traces
            )
        return passed, detail, traces[0], stderr.getvalue()

    def test_a_tracked_file_changed_and_restored_fails_the_review(self):
        for restore in (["checkout", "--", "tracked.txt"], ["restore", "tracked.txt"]):
            with self.subTest(restore=restore[0]):
                passed, detail, _, _ = self.review(
                    reviewer(
                        "Path('tracked.txt').write_text('changed', encoding='utf-8')\n"
                        f"subprocess.run(['git', *{restore!r}], check=True)\n"
                    )
                )

                self.assertFalse(passed)
                self.assertFalse((self.root / VERDICT_RELATIVE).exists())
                self.assertIn("left their earlier content in place", detail)
                self.assertIn("): tracked.txt; verdict removed", detail)
                # The tree is clean, which is what let this review pass before.
                self.assertEqual("", git(self.root, "status", "--porcelain"))

    def test_a_file_restored_by_writing_the_same_bytes_back_fails_the_review(self):
        passed, detail, _, _ = self.review(
            reviewer(
                "Path('tracked.txt').write_text('changed', encoding='utf-8')\n"
                "Path('tracked.txt').write_text('original', encoding='utf-8')\n"
            )
        )

        self.assertFalse(passed)
        self.assertIn("tracked.txt; verdict removed", detail)

    def test_a_restored_file_and_a_changed_file_are_both_named(self):
        passed, detail, _, _ = self.review(
            reviewer(
                "Path('tracked.txt').write_text('changed', encoding='utf-8')\n"
                "subprocess.run(['git', 'checkout', '--', 'tracked.txt'], check=True)\n"
                "Path('left-behind.txt').write_text('x', encoding='utf-8')\n"
            )
        )

        self.assertFalse(passed)
        self.assertIn("other than its verdict file: left-behind.txt;", detail)
        self.assertIn("): tracked.txt; verdict removed", detail)

    def test_a_review_that_only_reads_and_runs_passes_without_a_trace(self):
        passed, detail, traces, stderr = self.review(
            reviewer(
                "Path('tracked.txt').read_text(encoding='utf-8')\n"
                "subprocess.run(['git', 'status'], check=True, capture_output=True)\n"
                "subprocess.run(['git', 'diff', 'HEAD'], check=True, capture_output=True)\n"
            )
        )

        self.assertTrue(passed, detail)
        self.assertEqual([], traces.warnings())
        self.assertEqual("", traces.record_line("2026-11-23"))
        self.assertNotIn("WARNING", stderr)

    def test_a_write_to_an_ignored_file_is_told_and_does_not_fail_the_review(self):
        (self.root / "kept.local").write_text("before", encoding="utf-8")
        (self.root / "removed.local").write_text("before", encoding="utf-8")

        passed, detail, traces, stderr = self.review(
            reviewer(
                "Path('new.local').write_text('x', encoding='utf-8')\n"
                "Path('kept.local').write_text('after the review', encoding='utf-8')\n"
                "Path('removed.local').unlink()\n"
            )
        )

        self.assertTrue(passed, detail)
        self.assertEqual(["kept.local", "new.local", "removed.local"], traces.ignored)
        self.assertIn(
            f"{ITEM_ID}: WARNING the review's commands wrote files Git ignores: "
            "kept.local, new.local, removed.local",
            stderr,
        )
        self.assertEqual(
            "- Reviewer traces at close 2026-11-23: ignored files written 3 "
            "(kept.local, new.local, removed.local)",
            traces.record_line("2026-11-23"),
        )

    def test_the_runtime_folder_and_untouched_ignored_files_are_not_told(self):
        (self.root / "kept.local").write_text("before", encoding="utf-8")

        passed, detail, traces, _ = self.review(
            reviewer(
                "Path('.stage/.runtime/driver/note.txt').write_text('x', encoding='utf-8')\n"
                "Path('kept.local').read_text(encoding='utf-8')\n"
            )
        )

        self.assertTrue(passed, detail)
        self.assertEqual([], traces.ignored)

    def test_commands_that_name_outside_records_are_told(self):
        passed, detail, traces, stderr = self.review(
            recording_reviewer(
                [
                    shell_call("ls ~/.claude/projects/ | head"),
                    shell_call("gh pr view 102 --json headRefOid"),
                    shell_call("curl -s https://api.github.com/repos/o/r/pulls/102"),
                    shell_call("cat ~/.claude/projects/x/a.jsonl", call_id="refused"),
                    shell_call("cat .claude/settings.json; git log -1"),
                ]
            )
        )

        self.assertTrue(passed, detail)
        self.assertEqual(
            {
                review_containment.SESSION_RECORDS: ["ls ~/.claude/projects/ | head"],
                review_containment.GITHUB: [
                    "gh pr view 102 --json headRefOid",
                    "curl -s https://api.github.com/repos/o/r/pulls/102",
                ],
            },
            traces.reach,
        )
        self.assertIn("1 reviewer command(s) name the session record folder (~/.claude)", stderr)
        self.assertIn("  ls ~/.claude/projects/ | head", stderr)
        self.assertIn("2 reviewer command(s) name GitHub", stderr)
        self.assertEqual(
            "- Reviewer traces at close 2026-11-23: commands naming the session record "
            "folder (~/.claude) 1; commands naming GitHub 2",
            traces.record_line("2026-11-23"),
        )

    def test_a_record_cut_short_is_told_and_a_missing_one_is_not(self):
        _, _, cut, stderr = self.review(recording_reviewer([shell_call("ls")], complete=False))
        _, _, missing, _ = self.review(reviewer(""))

        self.assertIs(False, cut.record_complete)
        self.assertIn("tool-call record is incomplete", stderr)
        self.assertIn("tool-call record incomplete", cut.record_line("2026-11-23"))
        self.assertIsNone(missing.record_complete)
        self.assertEqual("", missing.record_line("2026-11-23"))

    def test_a_rejected_review_leaves_its_traces_line_on_the_card(self):
        card = self.root / CARD_RELATIVE
        card.write_text(card.read_text(encoding="utf-8") + "\n## Verification\n", encoding="utf-8")
        verdict = self.root / VERDICT_RELATIVE
        verdict.parent.mkdir(parents=True, exist_ok=True)
        rejected = {
            "criteria": [
                {"criterion": "probe", "verdict": "FAIL", "method": "ran", "reason": "probe"}
            ],
            "approved": False,
        }
        verdict.write_text(json.dumps(rejected), encoding="utf-8")
        traces = review_containment.ReviewTraces(ignored=["new.local"])

        recorded = close_work.record_rejected_review(
            card, verdict, "reviewer", close_work.traces_record_line([traces])
        )

        self.assertTrue(recorded)
        lines = card.read_text(encoding="utf-8").splitlines()
        review_line = next(i for i, line in enumerate(lines) if "rejected (1 FAIL ran)" in line)
        self.assertRegex(
            lines[review_line + 1],
            r"^- Reviewer traces at close \d{4}-\d\d-\d\d: ignored files written 1 \(new.local\)$",
        )


class OutsideReachTest(unittest.TestCase):
    def reach(self, command: str, home: str = "/home/me", environ=None) -> list[str]:
        home_path = PureWindowsPath(home) if ":" in home else Path(home)
        return sorted(review_containment.outside_reach([command], home_path, environ or {}))

    def test_every_spelling_of_the_session_record_folder(self):
        for command in (
            "ls ~/.claude",
            "cat $HOME/.claude/projects/x.jsonl",
            'grep -r x "${HOME}/.claude/"',
            "ls /home/me/.claude/projects",
            "cat ~/.claude.json",
            "Get-ChildItem $env:USERPROFILE\\.claude\\projects",
            "dir %USERPROFILE%\\.claude",
        ):
            with self.subTest(command=command):
                self.assertEqual([review_containment.SESSION_RECORDS], self.reach(command))

    def test_a_windows_home_in_native_and_git_bash_spelling(self):
        for command in ("type C:\\Users\\me\\.claude\\x", "cat /c/Users/me/.claude/x"):
            with self.subTest(command=command):
                self.assertEqual(
                    [review_containment.SESSION_RECORDS], self.reach(command, "C:\\Users\\me")
                )

    def test_a_configured_session_folder(self):
        self.assertEqual(
            [review_containment.SESSION_RECORDS],
            self.reach(
                "ls /data/claude-config/projects",
                environ={"CLAUDE_CONFIG_DIR": "/data/claude-config"},
            ),
        )

    def test_github_commands(self):
        for command in (
            "gh api repos/o/r/pulls/1",
            "cd repo; gh pr list --state all",
            "curl -s https://api.github.com/repos/o/r",
            "gh.exe run list",
        ):
            with self.subTest(command=command):
                self.assertEqual([review_containment.GITHUB], self.reach(command))

    def test_commands_inside_the_project_are_not_named(self):
        for command in (
            "cat .claude/settings.json",
            "ls /home/me/project/.claude",
            "ls ~/.claude-backup",
            "python3 -m unittest discover -s stage/scripts/tests -q",
            "git log --oneline | head; ./bin/gh-like status",
            "echo high api",
        ):
            with self.subTest(command=command):
                self.assertEqual([], self.reach(command))

    def test_a_file_tool_call_is_read_by_the_path_it_carries(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = Path(tmp) / "calls.jsonl"
            record.write_text(
                json.dumps(
                    {"id": "a", "tool": "Read", "input": {"file_path": "/home/me/.claude/x"}}
                )
                + "\nnot json\n"
                + json.dumps({"complete": True, "denied": []})
                + "\n",
                encoding="utf-8",
            )

            calls, complete = review_containment.read_tool_calls(record)

        self.assertTrue(complete)
        self.assertEqual(["/home/me/.claude/x"], calls)
        self.assertIsNone(review_containment.read_tool_calls(Path(tmp) / "absent.jsonl"))


class CompanionToolCallRecordTest(unittest.TestCase):
    STREAM = [
        {"type": "system", "subtype": "init"},
        {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "text", "text": "Running."},
                    {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "ls"}},
                ]
            },
        },
        {"type": "stream_event"},
        {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "tool_use", "id": "t2", "name": "Read", "input": {"file_path": "/x"}}
                ]
            },
        },
        {
            "type": "result",
            "subtype": "success",
            "result": "Verdict written.\n",
            "permission_denials": [{"tool_name": "Read", "tool_use_id": "t2"}],
        },
    ]

    def relay(self, lines: list[str]) -> tuple[str, list[dict[str, object]]]:
        record, out = io.StringIO(), io.StringIO()
        claude_review_companion.relay_stream(lines, record, out)
        return out.getvalue(), [json.loads(line) for line in record.getvalue().splitlines()]

    def test_the_answer_is_printed_and_each_tool_call_recorded(self):
        out, record = self.relay([json.dumps(event) + "\n" for event in self.STREAM])

        self.assertEqual("Verdict written.\n", out)
        self.assertEqual(
            [
                {"id": "t1", "tool": "Bash", "input": {"command": "ls"}},
                {"id": "t2", "tool": "Read", "input": {"file_path": "/x"}},
                {"complete": True, "denied": ["t2"]},
            ],
            record,
        )

    def test_the_record_matches_what_the_close_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "calls.jsonl"
            with path.open("w", encoding="utf-8") as handle:
                claude_review_companion.relay_stream(
                    [json.dumps(event) for event in self.STREAM], handle, io.StringIO()
                )

            # The refused Read is left out: it read nothing.
            self.assertEqual((["ls"], True), review_containment.read_tool_calls(path))
        self.assertEqual(review_containment.TOOL_CALLS_ENV, claude_review_companion.TOOL_CALLS_ENV)

    def test_a_run_without_a_result_says_so_and_keeps_plain_lines(self):
        out, record = self.relay(["Error: not logged in\n", json.dumps(self.STREAM[1]) + "\n"])

        self.assertEqual(
            "Error: not logged in\n"
            "claude_review_companion: the reviewer ended without a result event\n",
            out,
        )
        self.assertEqual(["t1"], [entry.get("id") for entry in record])

    def test_every_prompt_carries_the_rules_the_close_checks(self):
        command = claude_review_companion.claude_command(
            ["Review."], {"STAGE_REVIEW_VERDICT_FILE": "/v.json"}, "claude"
        )

        self.assertTrue(command[-1].startswith("Review.\n\nRules of this review"))
        for phrase in ("Do not restore it", "~/.claude", "api.github.com", "`unable`"):
            self.assertIn(phrase, command[-1])


if __name__ == "__main__":
    unittest.main()
