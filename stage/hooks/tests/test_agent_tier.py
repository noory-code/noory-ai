# The hook must run wherever `python3` points on a host machine (3.9+), so the
# test module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import importlib.util
import json
import os
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

TIERS = {
    "scout": {"claude": {"model": "haiku", "effort": "low"}},
    "standard": {"claude": {"model": "sonnet", "effort": "medium"}},
    "strong": {"claude": {"model": "opus[1m]", "effort": "high"}},
    "lead": {"claude": {"model": "fable", "effort": "high"}},
}
BASE_INPUT = {
    "description": "find the config loader",
    "prompt": "Find where settings are read.",
    "subagent_type": "general-purpose",
    "run_in_background": False,
}


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def card(root: Path, item_id: str, tier: str = "", status: str = "active") -> Path:
    tier_line = f"tier: {tier}\n" if tier else ""
    return write(
        root / ".stage/work/current" / item_id / "_story.md",
        f"---\nid: {item_id}\ntitle: T\nkind: development\nvenue: claude\n{tier_line}"
        f"status: {status}\nverification: pending\nretrospective: pending\n"
        "promotion: pending\nscope: src/\n---\n\n## Purpose\n\nP\n",
    )


def project(root: Path, *, tiers: dict | None = TIERS) -> Path:
    settings: dict[str, object] = {"schema_version": 5}
    if tiers is not None:
        settings["model_tiers"] = tiers
    write(root / ".stage/settings.json", json.dumps(settings))
    write(root / ".stage/work/active.md", "# Active\n")
    return root


def pre(root: Path, tool_input: dict, **env: str) -> dict:
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Agent",
        "tool_input": tool_input,
        "session_id": "session-1",
        "tool_use_id": "toolu_1",
        "cwd": str(root),
    }
    with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(root), **env}):
        return stage_guard.handle_event("pre-tool-use", payload)


def post(root: Path, tool_input: dict, tool_response: dict, transcript: Path) -> dict:
    payload = {
        "hook_event_name": "PostToolUse",
        "tool_name": "Agent",
        "tool_input": tool_input,
        "tool_response": tool_response,
        "session_id": "session-1",
        "tool_use_id": "toolu_1",
        "transcript_path": str(transcript),
        "cwd": str(root),
    }
    with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(root)}):
        return stage_guard.handle_event("post-tool-use", payload)


def usage_records(root: Path) -> list[dict]:
    folder = root / ".stage/.runtime/model-usage"
    records: list[dict] = []
    for path in sorted(folder.glob("*.jsonl")) if folder.is_dir() else []:
        records.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines())
    return records


def decision(result: dict) -> str:
    return result.get("hookSpecificOutput", {}).get("permissionDecision", "allow")


def updated(result: dict) -> dict | None:
    return result.get("hookSpecificOutput", {}).get("updatedInput")


class AgentFillTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = project(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_model_and_effort_are_filled_from_the_card_tier(self):
        card(self.root, "W-00000001", "standard")
        result = pre(self.root, dict(BASE_INPUT))

        self.assertEqual("allow", decision(result))
        self.assertEqual({**BASE_INPUT, "model": "sonnet", "effort": "medium"}, updated(result))
        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("standard", context)
        self.assertIn("sonnet", context)

    def test_only_the_missing_key_is_filled(self):
        card(self.root, "W-00000001", "standard")
        result = pre(self.root, {**BASE_INPUT, "model": "haiku"})

        self.assertEqual({**BASE_INPUT, "model": "haiku", "effort": "medium"}, updated(result))

    def test_a_complete_call_within_the_tier_passes_untouched(self):
        card(self.root, "W-00000001", "standard")
        for model in ("haiku", "sonnet"):
            with self.subTest(model=model):
                result = pre(self.root, {**BASE_INPUT, "model": model, "effort": "high"})
                self.assertEqual({}, result)

    def test_driver_selected_card_wins_over_other_open_cards(self):
        card(self.root, "W-00000001", "scout")
        selected = card(self.root, "W-00000002", "strong")
        result = pre(self.root, dict(BASE_INPUT), STAGE_WORK_ITEM_PATH=str(selected))

        self.assertEqual("opus[1m]", updated(result)["model"])
        self.assertEqual("high", updated(result)["effort"])

    def test_open_cards_with_different_tiers_cannot_fill(self):
        card(self.root, "W-00000001", "scout")
        card(self.root, "W-00000002", "strong")
        result = pre(self.root, dict(BASE_INPUT))

        self.assertEqual("deny", decision(result))
        reason = result["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("scout", reason)
        self.assertIn("strong", reason)
        self.assertIn("model", reason)

    def test_open_cards_with_different_tiers_allow_an_explicit_call_under_the_highest(self):
        card(self.root, "W-00000001", "scout")
        card(self.root, "W-00000002", "strong")
        result = pre(self.root, {**BASE_INPUT, "model": "opus", "effort": "high"})

        self.assertEqual({}, result)


class AgentCeilingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = project(Path(self.tmp.name))
        card(self.root, "W-00000001", "standard")

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_model_above_the_card_tier_is_denied(self):
        for model in ("opus", "fable", "mystery-model"):
            with self.subTest(model=model):
                result = pre(self.root, {**BASE_INPUT, "model": model, "effort": "low"})
                self.assertEqual("deny", decision(result))
                reason = result["hookSpecificOutput"]["permissionDecisionReason"]
                self.assertIn("standard", reason)
                self.assertIn("[over-tier:", reason)

    def test_a_stated_reason_lets_a_costlier_model_run_and_is_recorded(self):
        description = "audit the migration [over-tier: cross-file invariants need deep reasoning]"
        result = pre(
            self.root,
            {**BASE_INPUT, "description": description, "model": "opus"},
        )

        self.assertEqual("allow", decision(result))
        self.assertEqual("medium", updated(result)["effort"])
        records = usage_records(self.root)
        self.assertEqual(1, len(records))
        self.assertEqual("over_tier_allowed", records[0]["event"])
        self.assertEqual("cross-file invariants need deep reasoning", records[0]["reason"])
        self.assertEqual("opus", records[0]["model"])
        self.assertEqual(["W-00000001"], records[0]["cards"])

    def test_an_empty_reason_does_not_count(self):
        result = pre(
            self.root,
            {**BASE_INPUT, "description": "x [over-tier: ]", "model": "opus", "effort": "low"},
        )

        self.assertEqual("deny", decision(result))


class AgentInertTest(unittest.TestCase):
    def test_without_model_tiers_the_hook_does_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(Path(tmp), tiers=None)
            card(root, "W-00000001", "standard")
            result = pre(root, dict(BASE_INPUT))
            expensive = pre(root, {**BASE_INPUT, "model": "fable"})

        self.assertEqual({}, result)
        self.assertEqual({}, expensive)

    def test_without_a_card_tier_the_hook_does_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(Path(tmp))
            card(root, "W-00000001")
            result = pre(root, {**BASE_INPUT, "model": "fable"})

        self.assertEqual({}, result)

    def test_malformed_input_or_settings_never_break_the_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(Path(tmp))
            card(root, "W-00000001", "standard")
            odd_input = pre(root, {**BASE_INPUT, "model": 3})
            write(root / ".stage/settings.json", "{not json")
            broken_settings = pre(root, dict(BASE_INPUT))

        self.assertIn(decision(odd_input), {"allow", "deny"})
        self.assertEqual({}, broken_settings)

    def test_other_tools_are_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(Path(tmp))
            card(root, "W-00000001", "standard")
            payload = {"tool_name": "Read", "tool_input": {"file_path": "x"}, "cwd": str(root)}
            with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(root)}):
                result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual({}, result)


def subagent_stop(root: Path, agent_id: str, agent_transcript: Path | None, effort: str | None) -> dict:
    payload: dict = {
        "hook_event_name": "SubagentStop",
        "session_id": "session-1",
        "agent_id": agent_id,
        "agent_type": "general-purpose",
        "cwd": str(root),
    }
    if agent_transcript is not None:
        payload["agent_transcript_path"] = str(agent_transcript)
    if effort is not None:
        payload["effort"] = {"level": effort}
    with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(root)}):
        return stage_guard.handle_event("subagent-stop", payload)


class AgentUsageRecordTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = project(self.base / "project")
        card(self.root, "W-00000001", "scout")
        self.transcript = write(self.base / "sessions" / "session-1.jsonl", "")

    def tearDown(self):
        self.tmp.cleanup()

    def agent_transcript(self, model: str, effort: str) -> Path:
        lines = [
            {"type": "user", "message": {"content": "go"}},
            {"type": "assistant", "effort": effort, "message": {"model": model}},
        ]
        return write(
            self.base / "sessions" / "session-1" / "subagents" / "agent-abc.jsonl",
            "\n".join(json.dumps(line) for line in lines) + "\n",
        )

    def test_a_stopping_subagent_records_the_model_and_effort_it_ran_with(self):
        transcript = self.agent_transcript("claude-sonnet-5-5", "high")
        result = subagent_stop(self.root, "abc", transcript, "low")
        records = usage_records(self.root)

        self.assertEqual({}, result)
        self.assertEqual(1, len(records))
        record = records[0]
        self.assertEqual("agent_finished", record["event"])
        self.assertEqual("abc", record["agent_id"])
        self.assertEqual("scout", record["tier"])
        self.assertEqual(["W-00000001"], record["cards"])
        self.assertEqual("claude-sonnet-5-5", record["model"])
        self.assertEqual("low", record["effort"])
        self.assertEqual("session-1", record["session_id"])

    def test_a_transcript_without_the_final_reply_still_yields_the_request_model(self):
        lines = [
            {"type": "user", "message": {"content": "go"}},
            {
                "type": "api-request",
                "params": {"model": "claude-haiku-5-5", "output_config": {"effort": "low"}},
            },
        ]
        transcript = write(
            self.base / "sessions" / "session-1" / "subagents" / "agent-abc.jsonl",
            "\n".join(json.dumps(line) for line in lines) + "\n",
        )
        subagent_stop(self.root, "abc", transcript, None)
        record = usage_records(self.root)[0]

        self.assertEqual("claude-haiku-5-5", record["model"])
        self.assertEqual("low", record["effort"])

    def test_effort_falls_back_to_the_transcript(self):
        transcript = self.agent_transcript("claude-haiku-5-5", "medium")
        subagent_stop(self.root, "abc", transcript, None)

        self.assertEqual("medium", usage_records(self.root)[0]["effort"])

    def test_missing_transcript_leaves_the_model_empty(self):
        subagent_stop(self.root, "abc", self.base / "missing.jsonl", "low")
        record = usage_records(self.root)[0]

        self.assertEqual("", record["model"])
        self.assertEqual("low", record["effort"])

    def test_every_launch_records_its_request_and_reason(self):
        for status, agent_id in (("completed", "fg"), ("async_launched", "bg")):
            with self.subTest(status=status):
                result = post(
                    self.root,
                    {
                        **BASE_INPUT,
                        "description": "x [over-tier: needs a careful read]",
                        "model": "opus",
                        "effort": "low",
                        "run_in_background": status != "completed",
                    },
                    {"status": status, "agentId": agent_id},
                    self.transcript,
                )
                self.assertEqual({}, result)
        records = usage_records(self.root)

        self.assertEqual(["fg", "bg"], [record["agent_id"] for record in records])
        for record in records:
            self.assertEqual("agent_requested", record["event"])
            self.assertEqual("opus", record["requested_model"])
            self.assertEqual("low", record["requested_effort"])
            self.assertEqual("needs a careful read", record["over_tier_reason"])
            self.assertEqual("scout", record["tier"])

    def test_without_model_tiers_or_a_tiered_card_nothing_is_recorded(self):
        transcript = self.agent_transcript("claude-sonnet-5-5", "high")
        write(self.root / ".stage/settings.json", json.dumps({"schema_version": 5}))
        subagent_stop(self.root, "abc", transcript, "high")
        post(self.root, dict(BASE_INPUT), {"status": "completed", "agentId": "abc"}, self.transcript)
        no_tiers = usage_records(self.root)

        self.assertEqual([], no_tiers)

    def test_a_malformed_stop_payload_never_breaks(self):
        with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(self.root)}):
            result = stage_guard.handle_event(
                "subagent-stop", {"cwd": str(self.root), "agent_id": 7, "effort": "high"}
            )

        self.assertEqual({}, result)


if __name__ == "__main__":
    unittest.main()
