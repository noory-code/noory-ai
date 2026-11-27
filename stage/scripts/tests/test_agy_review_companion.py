"""Tests for `agy_review_companion.py` command building and stream-json relay."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

STAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(STAGE / "scripts"))
sys.path.insert(0, str(STAGE / "skills" / "stage-retrospective"))

import agy_review_companion  # noqa: E402
import review_containment  # noqa: E402


class AgyCommandTest(unittest.TestCase):
    def test_requires_prompt_and_verdict_file(self) -> None:
        with self.assertRaises(ValueError):
            agy_review_companion.agy_command([], {"STAGE_REVIEW_VERDICT_FILE": "/tmp/v.json"}, "agy")
        with self.assertRaises(ValueError):
            agy_review_companion.agy_command(["Review."], {}, "agy")

    def test_builds_attached_print_command_with_dirs_model_and_effort(self) -> None:
        command = agy_review_companion.agy_command(
            ["ignored-flag", "Review the card."],
            {
                "STAGE_REVIEW_VERDICT_FILE": "/tmp/run/verdict.json",
                "STAGE_CHANGED_PATHS_FILE": "/tmp/changed/paths.json",
                "STAGE_AGY_REVIEW_MODEL": "gemini-4-neon-high",
                "STAGE_EFFORT": "high",
            },
            "/usr/local/bin/agy",
        )

        self.assertEqual("/usr/local/bin/agy", command[0])
        self.assertIn("--output-format", command)
        self.assertEqual("stream-json", command[command.index("--output-format") + 1])
        self.assertIn("--sandbox", command)
        self.assertIn("--disable-slash-commands", command)
        self.assertEqual(["/tmp/run", "/tmp/changed"], [
            command[i + 1] for i, token in enumerate(command) if token == "--add-dir"
        ])
        self.assertEqual("gemini-4-neon-high", command[command.index("--model") + 1])
        self.assertEqual("high", command[command.index("--effort") + 1])
        self.assertTrue(command[-1].startswith("--print=Review the card.\n\nRules of this review"))
        for phrase in ("Do not restore it", "~/.claude", "~/.gemini/antigravity", "api.github.com"):
            self.assertIn(phrase, command[-1])

    def test_deduplicates_add_dir_and_falls_back_to_stage_model(self) -> None:
        command = agy_review_companion.agy_command(
            ["Review."],
            {
                "STAGE_REVIEW_VERDICT_FILE": "/tmp/same/verdict.json",
                "STAGE_CHANGED_PATHS_FILE": "/tmp/same/changed.json",
                "STAGE_MODEL": "gemini-4-carbon-high",
            },
            "agy",
        )
        self.assertEqual(
            ["/tmp/same"],
            [command[i + 1] for i, token in enumerate(command) if token == "--add-dir"],
        )
        self.assertEqual("gemini-4-carbon-high", command[command.index("--model") + 1])


class AgyRelayStreamTest(unittest.TestCase):
    STREAM = [
        {"event": "init", "conversation_id": "c1", "init": {"cwd": "/repo"}},
        {"event": "step_update", "step_update": {"step_index": 0, "state": "DONE", "step_type": "user_input"}},
        {
            "event": "step_update",
            "step_update": {
                "step_index": 2,
                "state": "ACTIVE",
                "step_type": "tool",
                "tool_name": "run_command",
                "tool_info": {"name": "run_command", "parameters": {"CommandLine": "ls"}},
            },
        },
        {
            "event": "step_update",
            "step_update": {
                "step_index": 2,
                "state": "DONE",
                "step_type": "tool",
                "tool_name": "run_command",
                "tool_info": {"name": "run_command", "parameters": {"CommandLine": "ls"}, "output": "ok"},
            },
        },
        {
            "event": "step_update",
            "step_update": {
                "step_index": 3,
                "state": "ERROR",
                "step_type": "tool",
                "tool_name": "read_file",
                "tool_info": {
                    "name": "read_file",
                    "parameters": {"Path": "/home/me/.gemini/antigravity/secret"},
                    "error": {
                        "type": "TOOL_ERROR",
                        "message": "tool call denied by pre-tool hook: blocked",
                    },
                },
            },
        },
        {
            "event": "result",
            "result": {"conversation_id": "c1", "status": "SUCCESS", "response": "Verdict written.\n"},
        },
    ]

    def relay(self, lines: list[str]) -> tuple[str, list[dict[str, object]]]:
        record, out = io.StringIO(), io.StringIO()
        agy_review_companion.relay_stream(lines, record, out)
        return out.getvalue(), [json.loads(line) for line in record.getvalue().splitlines()]

    def test_relays_tool_calls_marks_denials_and_prints_response(self) -> None:
        out, record = self.relay([json.dumps(event) + "\n" for event in self.STREAM])

        self.assertEqual("Verdict written.\n", out)
        self.assertEqual(
            [
                {"id": "step-2", "tool": "run_command", "input": {"CommandLine": "ls"}},
                {
                    "id": "step-3",
                    "tool": "read_file",
                    "input": {"Path": "/home/me/.gemini/antigravity/secret"},
                },
                {"complete": True, "denied": ["step-3"]},
            ],
            record,
        )

    def test_record_is_readable_by_review_containment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "calls.jsonl"
            with path.open("w", encoding="utf-8") as handle:
                agy_review_companion.relay_stream(
                    [json.dumps(event) for event in self.STREAM], handle, io.StringIO()
                )
            # step-3 was denied, so only step-2 ("ls") remains.
            self.assertEqual((["ls"], True), review_containment.read_tool_calls(path))
        self.assertEqual(review_containment.TOOL_CALLS_ENV, agy_review_companion.TOOL_CALLS_ENV)

    def test_missing_result_event_emits_diagnostic_and_preserves_plain_lines(self) -> None:
        out, record = self.relay(["Auth error\n", json.dumps(self.STREAM[2]) + "\n"])
        self.assertEqual(
            "Auth error\nagy_review_companion: the reviewer ended without a result event\n",
            out,
        )
        self.assertEqual(["step-2"], [entry.get("id") for entry in record])


if __name__ == "__main__":
    unittest.main()
