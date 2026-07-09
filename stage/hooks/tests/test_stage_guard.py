# The hook must run wherever `python3` points on a host machine (3.9+), so the
# test module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HOOK_PATH = Path(__file__).resolve().parents[1] / "stage_guard.py"
SPEC = importlib.util.spec_from_file_location("stage_guard", HOOK_PATH)
stage_guard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["stage_guard"] = stage_guard
SPEC.loader.exec_module(stage_guard)


def decision(result):
    # Allow is empty output (cross-host contract: Codex rejects an explicit
    # permissionDecision:allow without updatedInput as unsupported).
    if not result:
        return "allow"
    return result["hookSpecificOutput"]["permissionDecision"]


def reason(result):
    return result["hookSpecificOutput"].get("permissionDecisionReason", "")


class StageGuardTest(unittest.TestCase):
    def write_stage_file(self, root: Path, relative: str, content: str) -> Path:
        path = root / ".stage" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_work_item(
        self,
        root: Path,
        *,
        item_id: str = "W-0001",
        status: str = "active",
        verification: str = "pending",
        retrospective: str = "pending",
        promotion: str = "pending",
        scope: str = "",
        promotes: str = "",
        retrospective_ref: str = "",
    ) -> Path:
        return self.write_stage_file(
            root,
            f"present/work/items/{item_id}.md",
            (
                "---\n"
                f"id: {item_id}\n"
                f"title: Test work\n"
                f"status: {status}\n"
                f"verification: {verification}\n"
                f"retrospective: {retrospective}\n"
                f"retrospective_ref: {retrospective_ref}\n"
                f"promotion: {promotion}\n"
                f"scope: {scope}\n"
                f"promotes: {promotes}\n"
                "---\n"
                f"# {item_id} Test work\n"
            ),
        )

    def write_promotion_intent(
        self,
        root: Path,
        *,
        work_item: str = "W-0001",
        paths: list[str] | None = None,
        intent_type: str | None = None,
    ) -> None:
        target_paths = paths or [".stage/past/canon/principles.md"]
        payload = {"work_item": work_item, "paths": target_paths}
        if intent_type is not None:
            payload["type"] = intent_type
        self.write_stage_file(
            root,
            ".runtime/promote-intent.json",
            json.dumps(payload, ensure_ascii=False),
        )

    def test_session_start_injects_stage_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")

            result = stage_guard.handle_event("session-start", {"cwd": str(root)})

        output = result["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "SessionStart")
        self.assertIn("Global time axis", output["additionalContext"])

    def test_blocks_stage_root_deletion(self):
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf .stage"},
        }

        result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting `.stage`", reason(result))

    def test_blocks_past_write_without_promotion_intent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="completed", verification="passed", retrospective="completed", promotion="approved")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/past/canon/principles.md",
                    "content": "# Principles\n\nDo not promote an abstraction early.\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("promotion intent", reason(result))

    def test_allows_work_item_write_that_declares_promotes_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/present/work/items/W-0001.md",
                    "content": (
                        "---\n"
                        "id: W-0001\n"
                        "title: Test work\n"
                        "status: active\n"
                        "verification: pending\n"
                        "retrospective: pending\n"
                        "promotion: pending\n"
                        "scope:\n"
                        "promotes: .stage/past/canon/principles.md\n"
                        "---\n"
                        "# W-0001 Test work\n"
                    ),
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_allows_document_write_that_mentions_past_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.write_work_item(root, status="active", scope="*")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": "NOTES.md",
                    "content": "The canonical truth lives at .stage/past/canon/principles.md.\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_allows_past_write_with_completed_item_and_promotion_intent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(
                root,
                status="completed",
                verification="passed",
                retrospective="completed",
                promotion="approved",
                promotes=".stage/past/canon/principles.md",
            )
            self.write_promotion_intent(root)
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/past/canon/principles.md",
                    "content": "# Principles\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)
            intent = root / ".stage" / ".runtime" / "promote-intent.json"

        self.assertEqual(decision(result), "allow")
        self.assertFalse(intent.exists())

    def test_promotion_intent_consumes_only_written_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(
                root,
                status="completed",
                verification="passed",
                retrospective="completed",
                promotion="approved",
                promotes=".stage/past/canon/principles.md, .stage/past/canon/vocabulary.md",
            )
            self.write_promotion_intent(
                root,
                paths=[
                    ".stage/past/canon/principles.md",
                    ".stage/past/canon/vocabulary.md",
                ],
            )
            first = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": ".stage/past/canon/principles.md", "content": "# Principles\n"},
            }
            second = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": ".stage/past/canon/vocabulary.md", "content": "# Vocabulary\n"},
            }

            first_result = stage_guard.handle_event("pre-tool-use", first)
            intent = root / ".stage" / ".runtime" / "promote-intent.json"
            remaining = json.loads(intent.read_text(encoding="utf-8"))
            second_result = stage_guard.handle_event("pre-tool-use", second)

        self.assertEqual(decision(first_result), "allow")
        self.assertEqual(remaining["paths"], [".stage/past/canon/vocabulary.md"])
        self.assertEqual(decision(second_result), "allow")
        self.assertFalse(intent.exists())

    def test_blocks_promotion_when_work_item_does_not_promote_target_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(
                root,
                item_id="W-0001",
                status="completed",
                verification="passed",
                retrospective="completed",
                promotion="approved",
                promotes=".stage/past/canon/vocabulary.md",
            )
            self.write_promotion_intent(root, work_item="W-0001", paths=[".stage/past/canon/principles.md"])
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/past/canon/principles.md",
                    "content": "# Principles\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("promotes", reason(result))

    def test_blocks_past_write_when_intent_work_item_is_not_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", promotes=".stage/past/canon/principles.md")
            self.write_promotion_intent(root)
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/past/canon/principles.md",
                    "content": "# Principles\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("not in a completed state", reason(result))

    def test_blocks_source_write_without_registered_work_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": "src/app.py",
                    "content": "print('x')\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration gate", reason(result))

    def test_blocks_shell_redirect_source_write_without_registered_work_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "echo 'code' > src/app.py"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration gate", reason(result))

    def test_blocks_shell_append_redirect_source_write_without_registered_work_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "printf 'code' >> src/app.py"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration gate", reason(result))

    def test_allows_source_write_with_matching_active_work_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", scope="src")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": "src/app.py",
                    "content": "print('x')\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_blank_scope_does_not_match_source_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", scope="")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "src/app.py", "content": "print('x')\n"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration gate", reason(result))

    def test_dot_scope_does_not_match_source_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", scope=".")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "src/app.py", "content": "print('x')\n"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration gate", reason(result))

    def test_allows_intermediate_commit_with_open_work_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "git commit -m work"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_blocks_git_add_and_commit_without_registered_work_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "git add src/app.py && git commit -m x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("commit gate", reason(result))

    def test_blocks_completed_item_commit_when_retrospective_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="completed", verification="passed", retrospective="pending", promotion="approved", scope="src")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "git add src/app.py && git commit -m x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("retrospective", reason(result))

    def test_blocks_git_commit_all_without_registered_work_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            source = root / "src" / "app.py"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("print('before')\n", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "add", "src/app.py"], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(
                ["git", "-c", "user.name=Stage Test", "-c", "user.email=stage@example.test", "commit", "-m", "init"],
                cwd=root,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            source.write_text("print('after')\n", encoding="utf-8")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "git commit -a -m x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("commit gate", reason(result))

    def test_git_log_with_commit_word_is_not_a_completion_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "git log --grep commit"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_allows_read_only_shell_commands_for_past_paths_without_promotion_intent(self):
        commands = [
            "cat .stage/past/canon/principles.md",
            "grep foo .stage/past/canon/principles.md",
            "ls .stage/past/",
            "git log -- .stage/past/canon/principles.md",
            "git diff -- .stage/past/canon/principles.md",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "past/canon/principles.md", "# Principles\n")
            results = [
                stage_guard.handle_event(
                    "pre-tool-use",
                    {
                        "tool_name": "Bash",
                        "cwd": str(root),
                        "tool_input": {"command": command},
                    },
                )
                for command in commands
            ]

        self.assertTrue(all(decision(result) == "allow" for result in results))

    def test_allows_git_add_commit_for_consumed_past_promotion_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="completed", verification="passed", retrospective="completed", promotion="approved")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "git add .stage/past/canon/principles.md && git commit -m promote"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_allows_archive_intent_for_rejected_work_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="rejected", verification="pending", retrospective="pending", promotion="rejected")
            self.write_promotion_intent(
                root,
                paths=[".stage/past/work/archive/items/W-0001.md"],
                intent_type="archive",
            )
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/past/work/archive/items/W-0001.md",
                    "content": "# W-0001\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_blocks_archive_intent_when_target_file_does_not_match_work_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, item_id="W-0001", status="rejected", verification="pending", retrospective="pending", promotion="rejected")
            self.write_promotion_intent(
                root,
                work_item="W-0001",
                paths=[".stage/past/work/archive/items/W-0002.md"],
                intent_type="archive",
            )
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/past/work/archive/items/W-0002.md",
                    "content": "# W-0002\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("work_item", reason(result))

    def test_allows_non_stage_directory_named_stage_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", scope="deploy")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": "deploy/stage/run.sh",
                    "content": "#!/bin/sh\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_blocks_cp_into_past_without_promotion_intent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cp draft.md .stage/past/canon/principles.md"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("promotion intent", reason(result))

    def test_blocks_os_specific_script_under_dot_stage_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/hooks/run.sh",
                    "content": "#!/bin/sh\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("portability", reason(result))

    def test_stop_writes_summary_and_allows_handoff_with_open_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active")

            result = stage_guard.handle_event("stop", {"cwd": str(root)})
            summary = root / ".stage" / ".runtime" / "session-summary.md"

            # Stop output carries only systemMessage: Codex accepts `decision`
            # only as the literal "block", so approve/continue keys are omitted.
            self.assertEqual(set(result), {"systemMessage"})
            self.assertIn("session summary saved", result["systemMessage"])
            self.assertTrue(summary.exists())
            self.assertIn("Stage Session Summary", summary.read_text(encoding="utf-8"))

    def test_main_result_is_json_serializable(self):
        result = stage_guard.handle_event(
            "pre-tool-use",
            {"tool_name": "Bash", "tool_input": {"command": "true"}},
        )
        json.dumps(result, ensure_ascii=False)

    def test_governed_path_from_settings_requires_registration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(
                root,
                "settings.json",
                json.dumps({"governance": {"paths": ["designs"]}}),
            )
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "designs/home-mock.fig", "content": "binary"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration gate", reason(result))

    def test_governed_path_allows_registered_non_code_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(
                root,
                "settings.json",
                json.dumps({"governance": {"paths": ["designs"]}}),
            )
            self.write_work_item(root, status="active", scope="designs")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "designs/home-mock.fig", "content": "binary"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_governed_extensions_override_covers_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(
                root,
                "settings.json",
                json.dumps({"governance": {"extensions": [".md"]}}),
            )
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "docs/product-plan.md", "content": "# plan"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration gate", reason(result))

    def test_archive_intent_moves_retrospective_with_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(
                root,
                status="completed",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0001",
                promotion="approved",
            )
            self.write_promotion_intent(
                root,
                intent_type="archive",
                paths=[
                    ".stage/past/work/archive/items/W-0001.md",
                    ".stage/past/work/archive/retrospectives/R-0001.md",
                ],
            )

            item_result = stage_guard.handle_event(
                "pre-tool-use",
                {
                    "tool_name": "Write",
                    "cwd": str(root),
                    "tool_input": {
                        "file_path": ".stage/past/work/archive/items/W-0001.md",
                        "content": "---\nid: W-0001\nstatus: archived\n---\n",
                    },
                },
            )
            retro_result = stage_guard.handle_event(
                "pre-tool-use",
                {
                    "tool_name": "Write",
                    "cwd": str(root),
                    "tool_input": {
                        "file_path": ".stage/past/work/archive/retrospectives/R-0001.md",
                        "content": "---\nid: R-0001\nwork_item: W-0001\n---\n",
                    },
                },
            )

        self.assertEqual(decision(item_result), "allow")
        self.assertEqual(decision(retro_result), "allow")

    def test_broad_default_governs_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "docs/product-plan.md", "content": "# plan"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration gate", reason(result))

    def test_broad_default_allows_registered_document_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", scope="docs")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "docs/product-plan.md", "content": "# plan"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_exclude_paths_opt_out_of_governance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(
                root,
                "settings.json",
                json.dumps({"governance": {"exclude_paths": ["notes"]}}),
            )
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "notes/scratch.md", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_absolute_path_outside_workspace_is_not_governed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "/tmp/elsewhere/scratch.py", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_hierarchy_gate_blocks_unknown_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/present/work/items/W-0002.md",
                    "content": "---\nid: W-0002\nparent: W-9999\nstatus: active\n---\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("hierarchy gate", reason(result))

    def test_hierarchy_gate_blocks_open_child_under_finalized_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(
                root,
                item_id="W-0001",
                status="completed",
                verification="passed",
                retrospective="completed",
                promotion="approved",
            )
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/present/work/items/W-0002.md",
                    "content": "---\nid: W-0002\nparent: W-0001\nstatus: active\n---\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("finalized parent", reason(result))

    def test_hierarchy_gate_allows_child_under_open_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, item_id="W-0001", status="active")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/present/work/items/W-0002.md",
                    "content": "---\nid: W-0002\nparent: W-0001\nstatus: active\n---\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_hierarchy_gate_blocks_multiedit_with_unknown_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "MultiEdit",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/present/work/items/W-00000002.md",
                    "edits": [
                        {
                            "old_string": "",
                            "new_string": "---\nid: W-00000002\nparent: W-99999999\nstatus: active\n---\n",
                        }
                    ],
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("parent work item not found", reason(result))

    def test_hierarchy_gate_blocks_apply_patch_with_unknown_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "apply_patch",
                "cwd": str(root),
                "tool_input": {
                    "input": (
                        "*** Begin Patch\n"
                        "*** Add File: .stage/present/work/items/W-00000002.md\n"
                        "+---\n"
                        "+id: W-00000002\n"
                        "+parent: W-99999999\n"
                        "+status: active\n"
                        "+---\n"
                        "*** End Patch\n"
                    ),
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("parent work item not found", reason(result))

    def test_hierarchy_gate_blocks_apply_patch_move_with_unknown_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "draft.md").write_text("---\nid: W-00000002\nstatus: active\n---\n", encoding="utf-8")
            payload = {
                "tool_name": "apply_patch",
                "cwd": str(root),
                "tool_input": {
                    "input": (
                        "*** Begin Patch\n"
                        "*** Update File: draft.md\n"
                        "*** Move to: .stage/present/work/items/W-00000002.md\n"
                        "+parent: W-99999999\n"
                        "*** End Patch\n"
                    ),
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("parent work item not found", reason(result))

    def test_hierarchy_gate_applies_multiedit_fragments_sequentially(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, item_id="W-00000001", status="active")
            payload = {
                "tool_name": "MultiEdit",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/present/work/items/W-00000002.md",
                    "edits": [
                        {
                            "old_string": "",
                            "new_string": "---\nid: W-00000002\nparent: W-99999999\nstatus: active\n---\n",
                        },
                        {
                            "old_string": "parent: W-99999999",
                            "new_string": "parent: W-00000001",
                        },
                    ],
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_hierarchy_gate_allows_partial_edit_of_completed_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(
                root,
                item_id="W-00000001",
                status="completed",
                verification="passed",
                retrospective="completed",
                promotion="approved",
            )
            self.write_stage_file(
                root,
                "present/work/items/W-00000002.md",
                (
                    "---\n"
                    "id: W-00000002\n"
                    "parent:\n"
                    "status: completed\n"
                    "verification: passed\n"
                    "retrospective: completed\n"
                    "promotion: approved\n"
                    "scope:\n"
                    "promotes:\n"
                    "---\n"
                ),
            )
            payload = {
                "tool_name": "Edit",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/present/work/items/W-00000002.md",
                    "old_string": "parent:",
                    "new_string": "parent: W-00000001",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_question_gate_reminds_once_then_allows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {"tool_name": "AskUserQuestion", "cwd": str(root), "tool_input": {}}

            first = stage_guard.handle_event("pre-tool-use", payload)
            second = stage_guard.handle_event("pre-tool-use", payload)
            third = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(first), "deny")
        self.assertIn("question gate", reason(first))
        self.assertEqual(decision(second), "allow")
        self.assertEqual(decision(third), "deny")

    def test_question_gate_ignores_projects_without_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = {"tool_name": "AskUserQuestion", "cwd": tmp, "tool_input": {}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_question_gate_covers_codex_request_user_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {"tool_name": "request_user_input", "cwd": str(root), "tool_input": {}}

            first = stage_guard.handle_event("pre-tool-use", payload)
            second = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(first), "deny")
        self.assertIn("question gate", reason(first))
        self.assertEqual(decision(second), "allow")

    def test_pre_tool_allow_is_empty_output(self):
        # Codex marks permissionDecision:allow (without updatedInput) as a
        # failed hook run; allow must therefore be empty output on both hosts.
        result = stage_guard.handle_event(
            "pre-tool-use",
            {"tool_name": "Read", "tool_input": {"file_path": "README.md"}},
        )

        self.assertEqual(result, {})

    def test_stop_skip_marker_yields_empty_output(self):
        result = stage_guard.handle_event("stop", {"stop_hook_active": True})

        self.assertEqual(result, {})

    def test_empty_parent_line_is_not_read_as_next_line(self):
        # Regression (Codex e2e, 2026-07-10): \s* crossed the newline after an
        # empty `parent:` line and captured `source:` as the parent value,
        # producing a false hierarchy deny on work-item creation.
        text = "---\nid: W-00000002\nparent:\nsource:\nstatus: active\n---\n"
        self.assertEqual(stage_guard.frontmatter_field_from_text(text, "parent"), "")
        self.assertEqual(stage_guard.frontmatter_field_from_text(text, "id"), "W-00000002")

    def test_hierarchy_gate_allows_item_with_empty_parent_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/present/work/items/W-00000002-hello.md",
                    "content": (
                        "---\n"
                        "id: W-00000002\n"
                        "title: Hello\n"
                        "status: active\n"
                        "parent:\n"
                        "source:\n"
                        "scope: src\n"
                        "---\n"
                        "# W-00000002 Hello\n"
                    ),
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_content_mentions_of_governed_paths_do_not_trip_gates(self):
        # Regression (Codex e2e, 2026-07-10): payload content was scanned for
        # path-like strings, so a .stage-internal write whose BODY mentioned
        # governed paths / markdown links was falsely denied. Only explicit
        # write targets go through the gates.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/present/work/active.md",
                    "content": (
                        "| W-00000001 | task | Create src/app.py | active | "
                        "[W-00000001-create-app.md](items/W-00000001-create-app.md) |\n"
                    ),
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_apply_patch_body_is_not_parsed_as_shell_command(self):
        # Regression (Codex e2e, 2026-07-10): Codex sends the patch body under
        # tool_input.command; shell semantics (delete gate, shell write-target
        # extraction) must not run on patch content.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            patch = (
                "*** Begin Patch\n"
                "*** Add File: .stage/present/state/notes.md\n"
                "+Never run rm -rf .stage on this project.\n"
                "*** End Patch\n"
            )
            payload = {
                "tool_name": "apply_patch",
                "cwd": str(root),
                "tool_input": {"command": patch},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_codex_apply_patch_command_payload_hits_registration_gate(self):
        # Codex serializes apply_patch hook input as {"command": "<patch>"}.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            patch = (
                "*** Begin Patch\n"
                "*** Add File: src/app.py\n"
                "+print('hello')\n"
                "*** End Patch\n"
            )
            payload = {
                "tool_name": "apply_patch",
                "cwd": str(root),
                "tool_input": {"command": patch},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration", reason(result).lower())

    def test_broken_settings_fails_closed_for_governed_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "settings.json", '{"governance":{"paths":["designs"]')
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "designs/home-mock.fig", "content": "binary"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("settings.json", reason(result))

    def test_broken_settings_still_allows_repairing_settings_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "settings.json", '{"governance":{')
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/settings.json",
                    "content": '{"governance": {"paths": []}}',
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_apply_patch_source_target_requires_registration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "apply_patch",
                "cwd": str(root),
                "tool_input": {
                    "input": "*** Begin Patch\n*** Update File: src/app.py\n@@\n-x\n+y\n*** End Patch\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration gate", reason(result))

    def test_apply_patch_past_target_requires_promotion_intent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "apply_patch",
                "cwd": str(root),
                "tool_input": {
                    "input": "*** Begin Patch\n*** Update File: .stage/past/canon/principles.md\n@@\n-x\n+y\n*** End Patch\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("promotion intent", reason(result))

    def test_archive_intent_rejects_mismatched_retrospective_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(
                root,
                status="completed",
                verification="passed",
                retrospective="completed",
                retrospective_ref="R-0001",
                promotion="approved",
            )
            self.write_promotion_intent(
                root,
                intent_type="archive",
                paths=[".stage/past/work/archive/retrospectives/R-0002.md"],
            )

            result = stage_guard.handle_event(
                "pre-tool-use",
                {
                    "tool_name": "Write",
                    "cwd": str(root),
                    "tool_input": {
                        "file_path": ".stage/past/work/archive/retrospectives/R-0002.md",
                        "content": "---\nid: R-0002\n---\n",
                    },
                },
            )

        self.assertEqual(decision(result), "deny")
        self.assertIn("retrospective_ref", reason(result))


if __name__ == "__main__":
    unittest.main()
