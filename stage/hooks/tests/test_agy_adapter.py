"""Tests for Antigravity native hook adapter and plugin-root hooks.json."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK_TEST_ROOT = Path(__file__).resolve().parent
if str(HOOK_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_TEST_ROOT))

from hook_test_environment import sanitize_current_hook_environment  # noqa: E402

sanitize_current_hook_environment()

STAGE_ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = STAGE_ROOT / "hooks"
ADAPTER_PATH = HOOKS_DIR / "agy_adapter.py"
ROOT_HOOKS_JSON = STAGE_ROOT / "hooks.json"

SPEC = importlib.util.spec_from_file_location("agy_adapter", ADAPTER_PATH)
agy_adapter = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.path.insert(0, str(HOOKS_DIR))
SPEC.loader.exec_module(agy_adapter)

import stage_guard  # noqa: E402


def _init_minimal_stage(root: Path) -> None:
    stage = root / ".stage"
    (stage / "official" / "canon").mkdir(parents=True)
    (stage / "work" / "current").mkdir(parents=True)
    (stage / "work" / "planned").mkdir(parents=True)
    (stage / "state" / "observations").mkdir(parents=True)
    (stage / "state" / "questions").mkdir(parents=True)
    (stage / "operations").mkdir(parents=True)
    (stage / "settings.json").write_text(
        json.dumps({"schema_version": 5, "language": "en"}),
        encoding="utf-8",
    )
    (stage / "official" / "canon" / "principles.md").write_text(
        "# Principles\n\nKeep purpose strict.\n", encoding="utf-8"
    )
    (stage / "operations" / "verification.md").write_text(
        "# Verification\n", encoding="utf-8"
    )


def _write_active_card(root: Path, item_id: str = "W-00000001", scope: str = "src/") -> Path:
    card = root / ".stage" / "work" / "current" / f"{item_id}.md"
    card.write_text(
        f"---\nid: {item_id}\nkind: development\nstatus: active\nscope: {scope}\n"
        f"promotes: .stage/official/canon/principles.md\n---\n\n"
        "## Purpose\nKeep Antigravity hook enforcement exact.\n\n"
        "## Success criteria\n- Gates enforce registered work.\n",
        encoding="utf-8",
    )
    return card


class AgyHooksJsonTest(unittest.TestCase):
    def test_root_hooks_json_declares_stage_guard_events(self) -> None:
        config = json.loads(ROOT_HOOKS_JSON.read_text(encoding="utf-8"))
        self.assertIn("stage-guard", config)
        group = config["stage-guard"]
        expected = {
            "SessionStart": "session-start",
            "PreInvocation": "pre-invocation",
            "PreToolUse": "pre-tool-use",
            "PostToolUse": "post-tool-use",
            "Stop": "stop",
        }
        self.assertEqual(set(expected), set(group))
        for event_name, arg in expected.items():
            if event_name in {"PreToolUse", "PostToolUse"}:
                cmd = group[event_name][0]["hooks"][0]["command"]
            else:
                cmd = group[event_name][0]["command"]
            self.assertEqual(
                f"python3 ./hooks/agy_adapter.py {arg} || python ./hooks/agy_adapter.py {arg}",
                cmd,
            )


class AgyAdapterTest(unittest.TestCase):
    def test_session_start_injects_context_and_indexes_antigravity_rules(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _init_minimal_stage(root)
            (root / "GEMINI.md").write_text("# Project rules\n", encoding="utf-8")
            (root / ".agents" / "rules").mkdir(parents=True)
            (root / ".agents" / "rules" / "style.md").write_text("# Style\n", encoding="utf-8")

            result = agy_adapter.handle_agy_event(
                "session-start",
                {
                    "conversationId": "conv-1",
                    "workspacePaths": [str(root)],
                    "hookEventName": "SessionStart",
                },
            )

            injected = result["injectSteps"][0]["systemMessage"]["systemMessage"]
            self.assertIn("Stage", injected)
            self.assertIn("`GEMINI.md`", injected)
            self.assertIn("`.agents/rules/`", injected)

    def test_pre_invocation_injects_purpose_chain_only_when_work_is_active(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _init_minimal_stage(root)

            idle = agy_adapter.handle_agy_event(
                "pre-invocation",
                {"conversationId": "conv-2", "cwd": str(root), "hookEventName": "PreInvocation"},
            )
            self.assertEqual({}, idle)

            _write_active_card(root)
            active = agy_adapter.handle_agy_event(
                "pre-invocation",
                {"conversationId": "conv-2", "cwd": str(root), "hookEventName": "PreInvocation"},
            )
            text = active["injectSteps"][0]["systemMessage"]["systemMessage"]
            self.assertIn("W-00000001", text)
            self.assertIn("Keep Antigravity hook enforcement exact.", text)

    def test_pre_tool_use_enforces_registration_and_explicit_allow(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _init_minimal_stage(root)
            (root / "src").mkdir()
            target = str(root / "src" / "app.py")

            for tool_name, args in (
                ("write_to_file", {"TargetFile": target}),
                ("replace_file_content", {"TargetFile": target}),
                ("multi_replace_file_content", {"TargetFile": target}),
                ("edit_file", {"Path": target}),
                ("run_command", {"CommandLine": "echo hi > src/app.py"}),
            ):
                with self.subTest(tool=tool_name):
                    denied = agy_adapter.handle_agy_event(
                        "pre-tool-use",
                        {
                            "conversationId": "conv-3",
                            "cwd": str(root),
                            "hookEventName": "PreToolUse",
                            "toolCall": {"id": "c1", "name": tool_name, "args": args},
                        },
                    )
                    self.assertEqual("deny", denied["decision"])
                    self.assertIn("reason", denied)

            _write_active_card(root)
            allowed = agy_adapter.handle_agy_event(
                "pre-tool-use",
                {
                    "conversationId": "conv-3",
                    "cwd": str(root),
                    "hookEventName": "PreToolUse",
                    "toolCall": {"id": "c2", "name": "write_to_file", "args": {"TargetFile": target}},
                },
            )
            self.assertEqual({"decision": "allow"}, allowed)

            read_allowed = agy_adapter.handle_agy_event(
                "pre-tool-use",
                {
                    "conversationId": "conv-3",
                    "cwd": str(root),
                    "hookEventName": "PreToolUse",
                    "toolCall": {"id": "c3", "name": "read_file", "args": {"Path": target}},
                },
            )
            self.assertEqual({"decision": "allow"}, read_allowed)

    def test_pre_tool_use_blocks_stage_deletion_and_reminds_once_per_question(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _init_minimal_stage(root)
            _write_active_card(root)

            delete_denied = agy_adapter.handle_agy_event(
                "pre-tool-use",
                {
                    "conversationId": "conv-4",
                    "cwd": str(root),
                    "hookEventName": "PreToolUse",
                    "toolCall": {"id": "d1", "name": "run_command", "args": {"CommandLine": "rm -rf .stage"}},
                },
            )
            self.assertEqual("deny", delete_denied["decision"])

            first_q = agy_adapter.handle_agy_event(
                "pre-tool-use",
                {
                    "conversationId": "conv-4",
                    "cwd": str(root),
                    "hookEventName": "PreToolUse",
                    "toolCall": {"id": "q1", "name": "ask_question", "args": {"questions": []}},
                },
            )
            self.assertEqual("deny", first_q["decision"])
            self.assertIn("Stage question gate", first_q["reason"])

            second_q = agy_adapter.handle_agy_event(
                "pre-tool-use",
                {
                    "conversationId": "conv-4",
                    "cwd": str(root),
                    "hookEventName": "PreToolUse",
                    "toolCall": {"id": "q2", "name": "ask_question", "args": {"questions": []}},
                },
            )
            self.assertEqual({"decision": "allow"}, second_q)

    def test_promotion_intent_and_post_tool_use_complete_two_phase_claim(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _init_minimal_stage(root)
            card = _write_active_card(root)
            official_target = ".stage/official/canon/principles.md"

            blocked = agy_adapter.handle_agy_event(
                "pre-tool-use",
                {
                    "conversationId": "conv-5",
                    "cwd": str(root),
                    "hookEventName": "PreToolUse",
                    "toolCall": {
                        "id": "p1",
                        "name": "replace_file_content",
                        "args": {"TargetFile": str(root / official_target)},
                    },
                },
            )
            self.assertEqual("deny", blocked["decision"])

            card.write_text(
                "---\nid: W-00000001\nkind: development\nstatus: completed\n"
                "verification: passed\nretrospective: completed\npromotion: approved\n"
                "scope: src/\npromotes: .stage/official/canon/principles.md\n---\n\n"
                "## Purpose\nKeep Antigravity hook enforcement exact.\n\n"
                "## Success criteria\n- Gates enforce registered work.\n",
                encoding="utf-8",
            )

            # Plant pending intent matching the active item and target.
            intents_dir = root / ".stage" / ".runtime" / "intents"
            intents_dir.mkdir(parents=True, exist_ok=True)
            intent_path = intents_dir / "W-00000001--principles.md-0123456789.json"
            intent_path.write_text(
                json.dumps(
                    {
                        "type": "promotion",
                        "work_item": "W-00000001",
                        "paths": [official_target],
                        "allowed_paths": [official_target],
                    }
                ),
                encoding="utf-8",
            )

            pre_ok = agy_adapter.handle_agy_event(
                "pre-tool-use",
                {
                    "conversationId": "conv-5",
                    "cwd": str(root),
                    "hookEventName": "PreToolUse",
                    "toolCall": {
                        "id": "p2",
                        "name": "replace_file_content",
                        "args": {"TargetFile": str(root / official_target)},
                    },
                },
            )
            self.assertEqual({"decision": "allow"}, pre_ok)
            self.assertFalse(intent_path.exists())
            self.assertTrue(list(intents_dir.glob("*.claim-*")))

            post_ok = agy_adapter.handle_agy_event(
                "post-tool-use",
                {
                    "conversationId": "conv-5",
                    "cwd": str(root),
                    "hookEventName": "PostToolUse",
                    "toolCall": {
                        "id": "p2",
                        "name": "replace_file_content",
                        "args": {"TargetFile": str(root / official_target)},
                    },
                },
            )
            self.assertEqual({}, post_ok)
            self.assertEqual([], list(intents_dir.glob("*.claim-*")))

    def test_stop_writes_session_summary_per_conversation_id(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _init_minimal_stage(root)
            _write_active_card(root)

            stop_out = agy_adapter.handle_agy_event(
                "stop",
                {"conversationId": "conv-stop-9", "cwd": str(root), "hookEventName": "Stop"},
            )
            self.assertEqual({}, stop_out)
            summary = root / ".stage" / ".runtime" / "sessions" / "conv-stop-9.md"
            self.assertTrue(summary.is_file())
            self.assertIn("W-00000001", summary.read_text(encoding="utf-8"))

    def test_subprocess_cli_handles_pre_tool_use(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            _init_minimal_stage(root)
            payload = {
                "conversationId": "sub-1",
                "cwd": str(root),
                "hookEventName": "PreToolUse",
                "toolCall": {
                    "id": "s1",
                    "name": "write_to_file",
                    "args": {"TargetFile": str(root / "unregistered.py")},
                },
            }
            proc = subprocess.run(
                [sys.executable, str(ADAPTER_PATH), "pre-tool-use"],
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertEqual(0, proc.returncode, proc.stderr)
            response = json.loads(proc.stdout)
            self.assertEqual("deny", response["decision"])


if __name__ == "__main__":
    unittest.main()
