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
    ) -> Path:
        target_paths = paths or [".stage/past/canon/principles.md"]
        payload = {"work_item": work_item, "paths": target_paths}
        if intent_type is not None:
            payload["type"] = intent_type
        return self.write_stage_file(
            root,
            f".runtime/intents/{work_item}.json",
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

    def test_dot_segment_reentry_hits_registration_gate(self):
        # F1: .stage/../src must not masquerade as .stage-internal (ungoverned).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": ".stage/../src/rogue.py", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration", reason(result).lower())

    def test_dot_segment_reentry_into_past_hits_promotion_gate(self):
        # F1: .stage/present/../past must be seen as past.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "printf x > .stage/present/../past/canon/principles.md"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("promotion", reason(result).lower())

    def test_multi_target_requires_every_path_registered(self):
        # F2: one covered target must not smuggle an uncovered one.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.write_work_item(root, status="active", scope="allowed")
            patch = (
                "*** Begin Patch\n"
                "*** Add File: allowed/ok.txt\n+x\n"
                "*** Add File: outside.txt\n+y\n"
                "*** End Patch\n"
            )
            payload = {
                "tool_name": "apply_patch",
                "cwd": str(root),
                "tool_input": {"command": patch},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("outside.txt", reason(result))

    def test_multi_target_allows_when_each_path_registered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.write_work_item(root, item_id="W-1", status="active", scope="a")
            self.write_work_item(root, item_id="W-2", status="active", scope="b")
            patch = (
                "*** Begin Patch\n"
                "*** Add File: a/one.txt\n+x\n"
                "*** Add File: b/two.txt\n+y\n"
                "*** End Patch\n"
            )
            payload = {
                "tool_name": "apply_patch",
                "cwd": str(root),
                "tool_input": {"command": patch},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_recursive_delete_variants_are_blocked(self):
        for command in (
            "rm -R .stage",
            "rm --recursive .stage",
            "rm -rf ./.stage",
            "rmdir /s .stage",
            "find .stage -delete",
            "find ./.stage -exec rm {} +",
        ):
            payload = {"tool_name": "Bash", "tool_input": {"command": command}}
            result = stage_guard.handle_event("pre-tool-use", payload)
            self.assertEqual(decision(result), "deny", command)

    def test_find_delete_outside_stage_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {"tool_name": "Bash", "cwd": str(root), "tool_input": {"command": "find build -delete"}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_non_recursive_rm_of_file_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {"tool_name": "Bash", "cwd": str(root), "tool_input": {"command": "rm notes.txt"}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_git_commit_pathspec_is_registration_checked(self):
        # F4: git commit -- <path> commits unstaged changes; it must be gated.
        self.assertEqual(
            stage_guard.git_commit_pathspec_files(
                'git commit -m "x" -- src/app.py docs/readme.md', Path("/ws")
            ),
            ["src/app.py", "docs/readme.md"],
        )
        self.assertEqual(
            stage_guard.git_commit_pathspec_files("git commit -am msg", Path("/ws")), []
        )

    def test_hierarchy_atomic_patch_uses_post_state_parent(self):
        # F5: a patch that rejects the parent AND opens a child under it must deny.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.write_work_item(root, item_id="W-1", status="active")
            patch = (
                "*** Begin Patch\n"
                "*** Update File: .stage/present/work/items/W-1.md\n"
                "@@\n"
                "-status: active\n"
                "+status: rejected\n"
                "*** Add File: .stage/present/work/items/W-2.md\n"
                "+---\n+id: W-2\n+title: t\n+status: active\n+parent: W-1\n+---\n+# W-2\n"
                "*** End Patch\n"
            )
            payload = {"tool_name": "apply_patch", "cwd": str(root), "tool_input": {"command": patch}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("finalized parent", reason(result))

    def test_legacy_summary_collision_keeps_both_handoffs(self):
        # F6: a taken legacy.md slot must not drop the incoming handoff.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.write_stage_file(root, ".runtime/sessions/legacy.md", "# OLD\n")
            self.write_stage_file(root, ".runtime/session-summary.md", "# NEW\n")

            stage_guard.migrate_legacy_runtime(root / ".stage")

            sessions = root / ".stage" / ".runtime" / "sessions"
            bodies = sorted(p.read_text(encoding="utf-8").strip() for p in sessions.glob("*.md"))
        self.assertIn("# OLD", bodies)
        self.assertIn("# NEW", bodies)
        self.assertFalse((root / ".stage" / ".runtime" / "session-summary.md").exists())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_symlink_then_dotdot_resolves_to_real_past(self):
        # P28-followup: `link/../past` with `link -> .stage/present` resolves to
        # .stage/past on the OS; lexical pre-collapse must not hide that.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", scope="*")
            (root / "link").symlink_to(root / ".stage" / "present", target_is_directory=True)
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "link/../past/canon/principles.md", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("promotion", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_symlinked_stage_root_still_classifies_past(self):
        # P28-followup: `.stage -> stage-data` must not let a global-scope write
        # to .stage/past dodge the promotion gate.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "stage-data" / "present" / "work" / "items").mkdir(parents=True)
            (root / "stage-data" / "past" / "canon").mkdir(parents=True)
            (root / ".stage").symlink_to(root / "stage-data", target_is_directory=True)
            (root / "stage-data" / "present" / "work" / "items" / "W-1.md").write_text(
                "---\nid: W-1\ntitle: t\nstatus: active\nverification: pending\n"
                "retrospective: pending\npromotion: pending\nscope: '*'\n---\n# W-1\n",
                encoding="utf-8",
            )
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": ".stage/past/canon/principles.md", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("promotion", reason(result).lower())

    def test_unc_prefix_is_preserved(self):
        self.assertEqual(
            stage_guard.clean_path_text(r"\\\\server\\share\\repo\\x.py"),
            "//server/share/repo/x.py",
        )

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_degenerate_stage_symlink_does_not_ungovern_sources(self):
        # `.stage -> .` must not remap ordinary sources into `.stage/...` and
        # exclude them from governance.
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".stage").mkdir()
            shutil.rmtree(root / ".stage")
            (root / ".stage").symlink_to(root, target_is_directory=True)
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "src/x.py", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")

    def test_redundant_separators_stay_governed(self):
        # canonicalization: `.//src` must classify as workspace-relative src,
        # not an absolute /src outside the workspace.
        self.assertEqual(stage_guard.clean_path_text(".//src/x.py"), "src/x.py")
        self.assertEqual(stage_guard.clean_path_text("a//b//c"), "a/b/c")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": ".//src/x.py", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_symlink_loop_does_not_crash_the_hook(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "loopa").symlink_to(root / "loopb")
            (root / "loopb").symlink_to(root / "loopa")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "loopa/x.py", "content": "x"},
            }

            # Must return a decision (not raise), taking the lexical fallback.
            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertIn(decision(result), {"allow", "deny"})

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_apply_patch_delete_of_past_symlink_hits_promotion_gate(self):
        # unlink-style op on a symlink whose leaf sits in .stage/past: resolve
        # would deref to the outside target, but the lexical form keeps it past.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", scope="*")
            (root / "outside.txt").write_text("x", encoding="utf-8")
            (root / ".stage" / "past" / "canon").mkdir(parents=True, exist_ok=True)
            (root / ".stage" / "past" / "canon" / "plink").symlink_to(root / "outside.txt")
            patch = "*** Begin Patch\n*** Delete File: .stage/past/canon/plink\n*** End Patch\n"
            payload = {"tool_name": "apply_patch", "cwd": str(root), "tool_input": {"command": patch}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("promotion", reason(result).lower())

    def test_home_and_outside_paths_stay_ungoverned(self):
        # canonicalization must not turn `~/x` into a governed workspace path.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.assertFalse(stage_guard.is_source_path("~/notes.py", root))

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_symlinked_scope_matches_resolved_write(self):
        # scope: link (link -> src) must accept a registered write to link/x.py.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "link").symlink_to(root / "src", target_is_directory=True)
            self.write_work_item(root, status="active", scope="link")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "link/x.py", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_terminal_dot_dereferences_symlink_and_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "alias").symlink_to(root / ".stage", target_is_directory=True)
            payload = {"tool_name": "Bash", "cwd": str(root), "tool_input": {"command": "find alias/. -delete"}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")

    def test_find_exec_on_unrelated_file_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "find .stage -exec rm /tmp/stale-lock ;"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_deleting_governed_symlink_entry_needs_registration(self):
        # src/link -> outside: apply_patch Delete unlinks the workspace entry;
        # it stays registration-gated even though it resolves outside.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "src").mkdir()
            (root / "outside.txt").write_text("x", encoding="utf-8")
            (root / "src" / "link").symlink_to(root / "outside.txt")
            patch = "*** Begin Patch\n*** Delete File: src/link\n*** End Patch\n"
            payload = {"tool_name": "apply_patch", "cwd": str(root), "tool_input": {"command": patch}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration", reason(result).lower())

    def test_tilde_filename_does_not_crash_and_is_governed(self):
        # `~draft.py` is an ordinary workspace file, not a home reference.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.assertTrue(stage_guard.is_source_path("~draft.py", root))
            self.assertFalse(stage_guard.is_source_path("~/notes.py", root))
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "~draft.py", "content": "x"},
            }
            result = stage_guard.handle_event("pre-tool-use", payload)
            self.assertIn(decision(result), {"allow", "deny"})

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_excluded_dir_through_symlink_is_not_governed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "real").mkdir()
            (root / "link").symlink_to(root / "real", target_is_directory=True)
            self.write_stage_file(root, "settings.json", '{"governance":{"exclude_paths":["real"]}}')
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "link/x.py", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_work_item_symlink_still_hits_hierarchy_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "outside_W.md").write_text("x", encoding="utf-8")
            items = root / ".stage" / "present" / "work" / "items"
            items.mkdir(parents=True, exist_ok=True)
            (items / "W-2.md").symlink_to(root / "outside_W.md")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/present/work/items/W-2.md",
                    "content": "---\nid: W-2\ntitle: t\nstatus: active\nparent: W-999\n---\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("parent", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_scope_authorizes_deleting_a_symlink_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "out.txt").write_text("x", encoding="utf-8")
            (root / "src" / "link").symlink_to(root / "out.txt")
            self.write_work_item(root, status="active", scope="src")
            patch = "*** Begin Patch\n*** Delete File: src/link\n*** End Patch\n"
            payload = {"tool_name": "apply_patch", "cwd": str(root), "tool_input": {"command": patch}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_home_path_stays_outside_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.assertFalse(stage_guard.is_source_path("~/notes.py", root))

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_trailing_slash_dereferences_symlink_and_is_blocked(self):
        # `rm -rf alias/` (trailing slash) derefs the symlink and deletes the
        # target dir — must be blocked even though `rm -rf alias` is allowed.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "alias").symlink_to(root / ".stage", target_is_directory=True)
            payload = {"tool_name": "Bash", "cwd": str(root), "tool_input": {"command": "rm -rf alias/"}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_removing_a_symlink_to_stage_is_not_a_stage_deletion(self):
        # POSIX `rm -rf alias` (alias -> .stage) unlinks the symlink only.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "alias").symlink_to(root / ".stage", target_is_directory=True)
            payload = {"tool_name": "Bash", "cwd": str(root), "tool_input": {"command": "rm -rf alias"}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_symlinked_governance_prefix_still_governs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "src").mkdir()
            (root / "link").symlink_to(root / "src", target_is_directory=True)
            self.write_stage_file(root, "settings.json", '{"governance":{"paths":["link"]}}')
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "link/x.py", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_find_through_symlink_then_dotdot_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "link").symlink_to(root / ".stage" / "present", target_is_directory=True)
            payload = {"tool_name": "Bash", "cwd": str(root), "tool_input": {"command": "find link/.. -delete"}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")

    def test_find_execdir_rm_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {"tool_name": "Bash", "cwd": str(root), "tool_input": {"command": "find .stage -execdir rm -rf {} +"}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")

    def test_find_delete_with_absolute_stage_path_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            for command in (f"find {root}/.stage -delete", f"rm -rf {root}/.stage"):
                payload = {"tool_name": "Bash", "cwd": str(root), "tool_input": {"command": command}}
                result = stage_guard.handle_event("pre-tool-use", payload)
                self.assertEqual(decision(result), "deny", command)

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_symlink_parent_into_past_hits_promotion_gate(self):
        # P28: a symlink whose target is .stage must not let a scoped work item
        # smuggle a `past` write past the promotion gate.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", scope="link")
            (root / "link").symlink_to(root / ".stage", target_is_directory=True)
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "link/past/canon/principles.md", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("promotion", reason(result).lower())

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
            intent = root / ".stage" / ".runtime" / "intents" / "W-0001.json"

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
            intents_dir = root / ".stage" / ".runtime" / "intents"
            # The multi-path intent is normalized into per-path slots; the
            # first write consumes only the principles slot (atomic unlink).
            remaining_after_first = sorted(path.name for path in intents_dir.glob("*.json"))
            second_result = stage_guard.handle_event("pre-tool-use", second)
            remaining_after_second = sorted(path.name for path in intents_dir.glob("*.json"))

        self.assertEqual(decision(first_result), "allow")
        self.assertEqual(len(remaining_after_first), 1)
        self.assertIn("vocabulary", remaining_after_first[0])
        self.assertEqual(decision(second_result), "allow")
        self.assertEqual(remaining_after_second, [])

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

    def test_allows_archive_intent_for_rejected_item_with_retrospective(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(
                root,
                status="rejected",
                verification="pending",
                retrospective="completed",
                retrospective_ref="R-0001",
                promotion="rejected",
            )
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

    def test_blocks_archive_intent_for_rejected_item_without_retrospective(self):
        # Rejection reasons are learning assets: rejected items record their
        # completed retrospective before archiving, like completed ones.
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

        self.assertEqual(decision(result), "deny")
        self.assertIn("retrospective", reason(result).lower())

    def test_blocks_archive_intent_for_present_item_marked_archived(self):
        # `archived` in present is a shortcut out of the completion gates, not
        # a terminal state an archive intent accepts.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="archived", verification="pending", retrospective="pending", promotion="pending")
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

        self.assertEqual(decision(result), "deny")
        self.assertIn("completed/rejected", reason(result))

    def test_allows_archive_intent_maintenance_for_archive_located_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(
                root,
                "past/work/archive/items/W-0001.md",
                (
                    "---\nid: W-0001\ntitle: Old work\nstatus: archived\nverification: passed\n"
                    "retrospective: completed\nretrospective_ref: R-0001\npromotion: promoted\n"
                    "scope:\npromotes:\n---\n# W-0001\n"
                ),
            )
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
                    "content": "# W-0001 corrected\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_allows_archive_intent_including_index_update(self):
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
                paths=[
                    ".stage/past/work/archive/items/W-0001.md",
                    ".stage/past/work/archive/index.md",
                ],
                intent_type="archive",
            )
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/past/work/archive/index.md",
                    "content": "| W-0001 | completed | [item](items/W-0001.md) |\n",
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

            result = stage_guard.handle_event("stop", {"cwd": str(root), "session_id": "sess-a"})
            summary = root / ".stage" / ".runtime" / "sessions" / "sess-a.md"

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

    def test_concurrent_intents_consume_only_the_matching_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(
                root,
                item_id="W-0001",
                status="completed",
                verification="passed",
                retrospective="completed",
                promotion="approved",
                promotes=".stage/past/canon/principles.md",
            )
            self.write_work_item(
                root,
                item_id="W-0002",
                status="completed",
                verification="passed",
                retrospective="completed",
                promotion="approved",
                promotes=".stage/past/canon/vocabulary.md",
            )
            self.write_promotion_intent(root, work_item="W-0001")
            other = self.write_promotion_intent(
                root, work_item="W-0002", paths=[".stage/past/canon/vocabulary.md"]
            )
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/past/canon/principles.md",
                    "content": "# Principles\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)
            consumed = root / ".stage" / ".runtime" / "intents" / "W-0001.json"

            self.assertEqual(decision(result), "allow")
            self.assertFalse(consumed.exists())
            self.assertTrue(other.exists())

    def test_question_gate_is_session_scoped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            ask_a = {"tool_name": "AskUserQuestion", "cwd": str(root), "session_id": "sess-a", "tool_input": {}}
            ask_b = {"tool_name": "AskUserQuestion", "cwd": str(root), "session_id": "sess-b", "tool_input": {}}

            first_a = stage_guard.handle_event("pre-tool-use", ask_a)
            first_b = stage_guard.handle_event("pre-tool-use", ask_b)
            second_a = stage_guard.handle_event("pre-tool-use", ask_a)
            second_b = stage_guard.handle_event("pre-tool-use", ask_b)

        # Each session gets its own reminder; another session's pending question
        # must not consume it.
        self.assertEqual(decision(first_a), "deny")
        self.assertEqual(decision(first_b), "deny")
        self.assertEqual(decision(second_a), "allow")
        self.assertEqual(decision(second_b), "allow")

    def test_stop_prunes_session_summaries_to_keep_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            sessions = root / ".stage" / ".runtime" / "sessions"
            sessions.mkdir(parents=True)
            for index in range(6):
                path = sessions / f"old-{index}.md"
                path.write_text(f"# old {index}\n", encoding="utf-8")
                stamp = 1_000_000 + index
                os.utime(path, (stamp, stamp))

            stage_guard.handle_event("stop", {"cwd": str(root), "session_id": "sess-new"})

            remaining = sorted(path.name for path in sessions.glob("*.md"))
            self.assertEqual(len(remaining), stage_guard.SESSION_SUMMARY_KEEP)
            self.assertIn("sess-new.md", remaining)
            self.assertNotIn("old-0.md", remaining)
            self.assertNotIn("old-1.md", remaining)

    def test_session_start_injects_most_recent_session_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            older = self.write_stage_file(root, ".runtime/sessions/sess-old.md", "# Old handoff\n")
            os.utime(older, (1_000_000, 1_000_000))
            self.write_stage_file(root, ".runtime/sessions/sess-new.md", "# New handoff\n")

            result = stage_guard.handle_event("session-start", {"cwd": str(root)})

        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("New handoff", context)
        self.assertNotIn("Old handoff", context)

    def test_session_start_injects_open_questions_and_selected_backlog(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            for index in range(1, 6):
                self.write_stage_file(
                    root,
                    f"present/state/questions/Q-0000000{index}.md",
                    (
                        "---\n"
                        f"id: Q-0000000{index}\n"
                        f"title: Question {index}\n"
                        "work_items: W-00000001\n"
                        "---\n"
                    ),
                )
            self.write_stage_file(
                root,
                "future/backlog/items/B-00000001.md",
                "---\nid: B-00000001\ntitle: Selected thing\nstatus: selected\npriority: high\n---\n",
            )
            self.write_stage_file(
                root,
                "future/backlog/items/B-00000002.md",
                "---\nid: B-00000002\ntitle: Captured thing\nstatus: captured\n---\n",
            )

            result = stage_guard.handle_event("session-start", {"cwd": str(root)})

        context = result["hookSpecificOutput"]["additionalContext"]
        # Newest 3 questions + overflow pointer; selected-only backlog.
        self.assertIn("Q-00000005 Question 5 (blocks: W-00000001)", context)
        self.assertIn("Q-00000003", context)
        self.assertNotIn("Q-00000001 Question 1", context)
        self.assertIn("…and 2 more in `present/state/questions/`", context)
        self.assertIn("B-00000001 Selected thing (priority: high)", context)
        self.assertNotIn("Captured thing", context)

    def test_question_recency_is_numeric_not_lexical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            for number in (998, 999, 1000, 1001):
                self.write_stage_file(
                    root,
                    f"present/state/questions/Q-{number}.md",
                    f"---\nid: Q-{number}\ntitle: Question {number}\nwork_items:\n---\n",
                )

            lines = stage_guard.open_question_lines(root / ".stage")

        joined = "\n".join(lines)
        self.assertIn("Q-1001", joined)
        self.assertIn("Q-1000", joined)
        self.assertIn("Q-999", joined)
        self.assertNotIn("Q-998 ", joined)

    def test_injected_record_lines_are_length_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.write_stage_file(
                root,
                "present/state/questions/Q-00000001.md",
                f"---\nid: Q-00000001\ntitle: {'t' * 500}\nwork_items:\n---\n",
            )

            lines = stage_guard.open_question_lines(root / ".stage")

        self.assertLessEqual(len(lines[0]), stage_guard.SESSION_CONTEXT_LINE_LIMIT)

    def test_session_start_injects_host_project_instructions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "CLAUDE.md").write_text("# Project rules\n", encoding="utf-8")
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)
            (rules / "style.md").write_text("- rule\n", encoding="utf-8")

            result = stage_guard.handle_event("session-start", {"cwd": str(root)})

        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Project instructions (host-defined)", context)
        self.assertIn("`CLAUDE.md`", context)
        self.assertIn("`.claude/rules/` (1 entries)", context)
        self.assertIn("register the conflict as an open", context)

    def test_nested_package_instructions_are_discovered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            pkg = root / "distill"
            pkg.mkdir()
            (pkg / "CLAUDE.md").write_text("# Package rules\n", encoding="utf-8")

            lines = stage_guard.consumer_context_lines(root)

        self.assertIn("- `distill/CLAUDE.md`", lines)

    def test_agents_override_takes_precedence_over_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "AGENTS.md").write_text("# base\n", encoding="utf-8")
            (root / "AGENTS.override.md").write_text("# override\n", encoding="utf-8")

            lines = stage_guard.consumer_context_lines(root)

        self.assertIn("- `AGENTS.override.md`", lines)
        self.assertNotIn("- `AGENTS.md`", lines)

    def test_consumer_context_inventory_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            for index in range(15):
                pkg = root / f"pkg{index:02d}"
                pkg.mkdir()
                (pkg / "CLAUDE.md").write_text("# rules\n", encoding="utf-8")

            lines = stage_guard.consumer_context_lines(root)

        self.assertEqual(len(lines), stage_guard.CONSUMER_CONTEXT_MAX_LINES + 1)
        self.assertIn("more instruction sources", lines[-1])

    def test_nested_package_skills_and_dotfiles_are_discovered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            pkg = root / "engine"
            (pkg / ".agents" / "skills").mkdir(parents=True)
            (pkg / ".agents" / "skills" / "review.md").write_text("s\n", encoding="utf-8")
            (pkg / ".claude" / "CLAUDE.md").parent.mkdir(parents=True, exist_ok=True)
            (pkg / ".claude" / "CLAUDE.md").write_text("# rules\n", encoding="utf-8")

            lines = stage_guard.consumer_context_lines(root)

        self.assertIn("- `engine/.agents/skills/` (1 entries)", lines)
        self.assertIn("- `engine/.claude/CLAUDE.md`", lines)

    def test_stage_init_session_still_sees_host_instructions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "CLAUDE.md").write_text("# Project rules\n", encoding="utf-8")

            result = stage_guard.handle_event("session-start", {"cwd": str(root)})

        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("stage-init", context)
        self.assertIn("Project instructions (host-defined)", context)
        self.assertIn("`CLAUDE.md`", context)

    def test_container_layout_packages_are_discovered_at_depth_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            web = root / "apps" / "web"
            web.mkdir(parents=True)
            (web / "CLAUDE.md").write_text("# web rules\n", encoding="utf-8")

            lines = stage_guard.consumer_context_lines(root)

        self.assertIn("- `apps/web/CLAUDE.md`", lines)

    def test_pre_init_directive_does_not_require_question_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "CLAUDE.md").write_text("# Project rules\n", encoding="utf-8")

            result = stage_guard.handle_event("session-start", {"cwd": str(root)})

        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("raise it with the user directly", context)
        self.assertNotIn("register the conflict as an open", context)

    def test_dependency_trees_cannot_inject_instructions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            dep = root / "node_modules" / "evil-pkg"
            dep.mkdir(parents=True)
            (dep / "AGENTS.md").write_text("# injected\n", encoding="utf-8")

            lines = stage_guard.consumer_context_lines(root)

        self.assertEqual([line for line in lines if "node_modules" in line], [])

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_symlink_escaping_workspace_is_not_discovered(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            external = Path(outside) / "elsewhere"
            external.mkdir()
            (external / "CLAUDE.md").write_text("# external\n", encoding="utf-8")
            (root / "linked").symlink_to(external, target_is_directory=True)

            lines = stage_guard.consumer_context_lines(root)

        self.assertEqual([line for line in lines if "linked" in line], [])

    def test_cap_preserves_packages_scoped_by_active_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.write_work_item(root, status="active", scope="zpkg/src")
            for index in range(14):
                pkg = root / f"pkg{index:02d}"
                pkg.mkdir()
                (pkg / "CLAUDE.md").write_text("# rules\n", encoding="utf-8")
            zpkg = root / "zpkg"
            zpkg.mkdir()
            (zpkg / "CLAUDE.md").write_text("# governing rules\n", encoding="utf-8")

            lines = stage_guard.consumer_context_lines(
                root, stage_root=root / ".stage"
            )

        # zpkg sorts last lexically but is scoped by active work — it must
        # survive the cap.
        self.assertIn("- `zpkg/CLAUDE.md`", lines[: stage_guard.CONSUMER_CONTEXT_MAX_LINES])

    def test_session_start_omits_host_instructions_section_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")

            result = stage_guard.handle_event("session-start", {"cwd": str(root)})

        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertNotIn("Project instructions (host-defined)", context)

    def test_session_start_omits_question_and_backlog_sections_when_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")

            result = stage_guard.handle_event("session-start", {"cwd": str(root)})

        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertNotIn("Open questions", context)
        self.assertNotIn("Selected backlog", context)

    def test_session_start_injects_all_tied_handoffs(self):
        # P30: two sessions can Stop in the same coarse-mtime tick; both
        # handoffs must be injected, not just one.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            a = self.write_stage_file(root, ".runtime/sessions/sess-a.md", "# Handoff A\n")
            b = self.write_stage_file(root, ".runtime/sessions/sess-b.md", "# Handoff B\n")
            import os as _os
            _os.utime(a, (1_000_000, 1_000_000))
            _os.utime(b, (1_000_000, 1_000_000))

            result = stage_guard.handle_event("session-start", {"cwd": str(root)})

        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Handoff A", context)
        self.assertIn("Handoff B", context)
        self.assertIn("concurrent", context)

    def test_session_start_prunes_stale_question_ack_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            stale = self.write_stage_file(root, ".runtime/question-ack/sess-dead", "t\n")
            os.utime(stale, (1_000_000, 1_000_000))
            fresh = self.write_stage_file(root, ".runtime/question-ack/sess-live", "t\n")

            stage_guard.handle_event("session-start", {"cwd": str(root)})

            self.assertFalse(stale.exists())
            self.assertTrue(fresh.exists())

    def test_overlapping_intents_covering_same_path_are_denied(self):
        # Fail closed on ambiguity: an arbitrary consume could let one work
        # item's write ride another item's authorization.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(
                root,
                item_id="W-0001",
                status="completed",
                verification="passed",
                retrospective="completed",
                promotion="approved",
                promotes=".stage/past/canon/principles.md",
            )
            self.write_work_item(root, item_id="W-0002", status="active")
            self.write_promotion_intent(root, work_item="W-0001")
            self.write_promotion_intent(root, work_item="W-0002")
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
        self.assertIn("multiple pending intents", reason(result))

    def test_stop_prune_never_deletes_the_summary_it_just_wrote(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            sessions = root / ".stage" / ".runtime" / "sessions"
            sessions.mkdir(parents=True)
            stamp = 1_000_000
            for index in range(stage_guard.SESSION_SUMMARY_KEEP):
                path = sessions / f"old-{index}.md"
                path.write_text(f"# old {index}\n", encoding="utf-8")
                os.utime(path, (stamp, stamp))

            stage_guard.handle_event("stop", {"cwd": str(root), "session_id": "sess-tied"})
            written = sessions / "sess-tied.md"
            # Force the pathological tie and prune again directly.
            os.utime(written, (stamp, stamp))
            stage_guard.prune_session_summaries(root / ".stage", keep_path=written)

            self.assertTrue(written.exists())

    def test_prune_spares_fresh_summaries_beyond_cap(self):
        # Under clock skew a live session's just-written handoff can sort below
        # older files; anything younger than a day must survive pruning.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            sessions = root / ".stage" / ".runtime" / "sessions"
            sessions.mkdir(parents=True)
            import time as _time
            ahead = _time.time() + 3600
            for index in range(stage_guard.SESSION_SUMMARY_KEEP):
                path = sessions / f"ahead-{index}.md"
                path.write_text(f"# ahead {index}\n", encoding="utf-8")
                os.utime(path, (ahead, ahead))
            fresh_behind = sessions / "sess-fresh.md"
            fresh_behind.write_text("# fresh but sorted last\n", encoding="utf-8")
            behind = _time.time() - 600
            os.utime(fresh_behind, (behind, behind))

            stage_guard.prune_session_summaries(root / ".stage")

            self.assertTrue(fresh_behind.exists())

    def test_prune_holds_cap_when_pinned_summary_is_oldest(self):
        # Another host's clock running ahead can leave the just-written summary
        # older than five existing files; the cap must still hold with the
        # pinned file retained.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            sessions = root / ".stage" / ".runtime" / "sessions"
            sessions.mkdir(parents=True)
            for index in range(stage_guard.SESSION_SUMMARY_KEEP + 1):
                path = sessions / f"future-{index}.md"
                path.write_text(f"# future {index}\n", encoding="utf-8")
                os.utime(path, (2_000_000, 2_000_000))
            pinned = sessions / "sess-behind.md"
            pinned.write_text("# behind\n", encoding="utf-8")
            os.utime(pinned, (1_000_000, 1_000_000))

            stage_guard.prune_session_summaries(root / ".stage", keep_path=pinned)

            remaining = list(sessions.glob("*.md"))
            self.assertEqual(len(remaining), stage_guard.SESSION_SUMMARY_KEEP)
            self.assertTrue(pinned.exists())

    def test_consume_race_denies_the_losing_session(self):
        # The rename is the atomic reservation: if another session consumed the
        # intent between validation and acquisition, the losing write is denied
        # instead of riding the same one-shot authorization.
        from unittest import mock

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

            with mock.patch.object(
                stage_guard.Path, "rename", side_effect=FileNotFoundError
            ):
                result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("consumed by another session", reason(result))

    def test_replanting_absolute_and_relative_path_is_one_slot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".stage").mkdir()
            intent = {"work_item": "W-0001", "type": "promotion"}
            first = stage_guard.write_intent_file(root / ".stage", intent, ".stage/past/canon/principles.md")
            second = stage_guard.write_intent_file(
                root / ".stage", intent, str(root / ".stage/past/canon/principles.md")
            )

            files = list((root / ".stage/.runtime/intents").glob("*.json"))

        self.assertEqual(first, second)
        self.assertEqual(len(files), 1)

    def test_intent_filename_is_bounded_for_deep_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".stage").mkdir()
            deep = ".stage/past/canon/" + "/".join(["sub"] * 40) + "/" + ("x" * 120) + ".md"
            intent = {"work_item": "W-0001", "type": "promotion"}

            target = stage_guard.write_intent_file(root / ".stage", intent, deep)

        self.assertIsNotNone(target)
        self.assertLess(len(target.name), 120)

    def test_legacy_single_slot_intent_is_migrated_and_honored(self):
        # 0.1.0 wrote .runtime/promote-intent.json; upgrading must not deny a
        # promotion that was legitimately prepared under the old layout.
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
            legacy = self.write_stage_file(
                root,
                ".runtime/promote-intent.json",
                json.dumps({"work_item": "W-0001", "paths": [".stage/past/canon/principles.md"]}),
            )
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/past/canon/principles.md",
                    "content": "# Principles\n",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual(decision(result), "allow")
            self.assertFalse(legacy.exists())
            self.assertFalse((root / ".stage" / ".runtime" / "intents" / "W-0001.json").exists())

    def test_legacy_session_summary_is_migrated_into_sessions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            legacy = self.write_stage_file(root, ".runtime/session-summary.md", "# Legacy handoff\n")

            result = stage_guard.handle_event("session-start", {"cwd": str(root)})

            context = result["hookSpecificOutput"]["additionalContext"]
            self.assertIn("Legacy handoff", context)
            self.assertFalse(legacy.exists())
            self.assertTrue((root / ".stage" / ".runtime" / "sessions" / "legacy.md").exists())

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

    def promotable_work_item(self, root: Path, *, promotes: str) -> Path:
        return self.write_work_item(
            root,
            status="completed",
            verification="passed",
            retrospective="completed",
            retrospective_ref="R-0001",
            promotion="approved",
            promotes=promotes,
        )

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_intent_for_one_alias_does_not_authorize_sibling_alias(self):
        # Round 12: promotion capabilities are exact ENTRIES. Two leaves
        # aliasing the same target must not share one authorization — an unlink
        # of `b.md` acts on the entry `b.md`, whatever it points at.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.promotable_work_item(root, promotes=".stage/past/canon/a.md")
            self.write_promotion_intent(root, paths=[".stage/past/canon/a.md"])
            canon = root / ".stage" / "past" / "canon"
            canon.mkdir(parents=True, exist_ok=True)
            (canon / "shared.md").write_text("x", encoding="utf-8")
            (canon / "a.md").symlink_to(canon / "shared.md")
            (canon / "b.md").symlink_to(canon / "shared.md")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": ".stage/past/canon/b.md", "content": "y"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("promotion", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_intent_for_symlink_leaf_still_authorizes_that_leaf(self):
        # Companion to the alias deny: the NAMED leaf itself stays authorized.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.promotable_work_item(root, promotes=".stage/past/canon/a.md")
            self.write_promotion_intent(root, paths=[".stage/past/canon/a.md"])
            canon = root / ".stage" / "past" / "canon"
            canon.mkdir(parents=True, exist_ok=True)
            (canon / "shared.md").write_text("x", encoding="utf-8")
            (canon / "a.md").symlink_to(canon / "shared.md")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": ".stage/past/canon/a.md", "content": "y"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_apply_patch_on_symlinked_work_item_still_projects_hunks(self):
        # Round 12: the patch projection must match headers the same way the
        # target was selected (either form), or a symlinked work-item leaf gets
        # an empty projection and `parent: W-999` slips past the hierarchy gate.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "outside_W.md").write_text(
                "---\nid: W-2\ntitle: t\nstatus: active\n---\n# W-2\n", encoding="utf-8"
            )
            items = root / ".stage" / "present" / "work" / "items"
            items.mkdir(parents=True, exist_ok=True)
            (items / "W-2.md").symlink_to(root / "outside_W.md")
            patch = (
                "*** Begin Patch\n"
                "*** Update File: .stage/present/work/items/W-2.md\n"
                "@@\n"
                "+parent: W-999\n"
                "*** End Patch\n"
            )
            payload = {"tool_name": "apply_patch", "cwd": str(root), "tool_input": {"command": patch}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("parent", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_script_suffix_symlink_entry_in_stage_is_blocked(self):
        # Round 12: `.stage/run.sh -> outside.txt` — the resolved target ends
        # `.txt`, but the entry left inside `.stage` is an `.sh` script.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "outside.txt").write_text("x", encoding="utf-8")
            (root / ".stage" / "run.sh").symlink_to(root / "outside.txt")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": ".stage/run.sh", "content": "echo hi"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("portability", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_excluded_prefix_still_matches_when_symlink_escapes(self):
        # Round 12: `exclude_paths: generated` with `generated -> <outside>`
        # must keep excluding lexical writes under `generated/` — the prefix's
        # lexical form must survive canonicalization alongside the resolved one.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "ws"
            outside = base / "ext"
            outside.mkdir(parents=True)
            root.mkdir(parents=True)
            self.write_stage_file(
                root,
                "settings.json",
                json.dumps({"governance": {"exclude_paths": ["generated"]}}),
            )
            (root / "generated").symlink_to(outside, target_is_directory=True)
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "generated/foo.txt", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_symlinked_settings_stays_repairable_when_malformed(self):
        # Round 12: the malformed-governance gate promises settings.json stays
        # repairable; a symlinked settings entry must classify as stage-internal
        # even though its resolve lands outside.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "ws"
            (root / ".stage").mkdir(parents=True)
            (base / "ext").mkdir()
            (base / "ext" / "settings.json").write_text("{oops", encoding="utf-8")
            (root / ".stage" / "settings.json").symlink_to(base / "ext" / "settings.json")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {
                    "file_path": ".stage/settings.json",
                    "content": "{\"governance\": {}}",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_find_traversal_options_do_not_hide_stage_roots(self):
        # Round 12 (2nd pass): `-H/-L/-P` are pre-path traversal options — the
        # root scan must skip them, not stop at them and record no roots.
        for command in (
            "find -L .stage -delete",
            "find -P .stage -exec rm -rf {} +",
            "find -H -L .stage -delete",
        ):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.write_stage_file(root, "index.md", "# Stage\n")
                payload = {
                    "tool_name": "Bash",
                    "cwd": str(root),
                    "tool_input": {"command": command},
                }

                result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual(decision(result), "deny", command)
            self.assertIn("deleting", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_aliased_parent_with_outward_leaf_stays_registration_gated(self):
        # Round 12 (2nd pass): deleting `alias/link` (alias -> src, link ->
        # outside) names the entry `src/link`; under `governance.paths: [src]`
        # the entry form must keep it governed.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(
                root, "settings.json", json.dumps({"governance": {"paths": ["src"]}})
            )
            (root / "src").mkdir()
            (root / "outside.txt").write_text("x", encoding="utf-8")
            (root / "src" / "link").symlink_to(root / "outside.txt")
            (root / "alias").symlink_to(root / "src", target_is_directory=True)
            patch = "*** Begin Patch\n*** Delete File: alias/link\n*** End Patch\n"
            payload = {"tool_name": "apply_patch", "cwd": str(root), "tool_input": {"command": patch}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration", reason(result).lower())

    def test_find_double_dash_and_ancestor_roots_are_blocked(self):
        # Round 12 (3rd pass): `--` ends find's options (paths follow), and a
        # destructive find rooted at an ANCESTOR of `.stage` traverses into it.
        for command in (
            "find -- .stage -delete",
            "find . -delete",
            "find . -name '*.pyc' -delete",
            "rm -rf .",
            "rm -rf ..",
        ):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.write_stage_file(root, "index.md", "# Stage\n")
                payload = {
                    "tool_name": "Bash",
                    "cwd": str(root),
                    "tool_input": {"command": command},
                }

                result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual(decision(result), "deny", command)
            self.assertIn("deleting", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_find_follow_mode_dereferences_symlink_root(self):
        # Round 12 (4th pass): `-H`/`-L`/`-follow` make find TRAVERSE a symlink
        # root — the rm-style "final symlink deletes only the link" exemption
        # must not apply.
        for command in (
            "find -H alias -depth -exec rm -rf {} +",
            "find -L alias -delete",
            "find alias -follow -delete",
        ):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.write_stage_file(root, "index.md", "# Stage\n")
                (root / "alias").symlink_to(root / ".stage", target_is_directory=True)
                payload = {
                    "tool_name": "Bash",
                    "cwd": str(root),
                    "tool_input": {"command": command},
                }

                result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual(decision(result), "deny", command)
            self.assertIn("deleting", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_find_without_follow_keeps_symlink_root_exempt(self):
        # Companion: default `-P` find does not follow a symlink root — deleting
        # it removes only the link, which stays allowed.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "alias").symlink_to(root / ".stage", target_is_directory=True)
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "find alias -delete"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_deleting_entry_with_excluded_target_needs_registration(self):
        # Round 12 (4th pass): `src/link -> generated/file` with `generated`
        # excluded — deleting the ENTRY acts on the governed source tree, so the
        # leaf-deref exclusion must not ungovern it.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(
                root, "settings.json", json.dumps({"governance": {"exclude_paths": ["generated"]}})
            )
            (root / "generated").mkdir()
            (root / "generated" / "file").write_text("x", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "link").symlink_to(root / "generated" / "file")
            patch = "*** Begin Patch\n*** Delete File: src/link\n*** End Patch\n"
            payload = {"tool_name": "apply_patch", "cwd": str(root), "tool_input": {"command": patch}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration", reason(result).lower())

    def test_direct_write_into_excluded_dir_stays_ungoverned(self):
        # Companion: writes spelled under the excluded dir itself stay excluded.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(
                root, "settings.json", json.dumps({"governance": {"exclude_paths": ["generated"]}})
            )
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "generated/foo.txt", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_scope_does_not_cross_authorize_aliased_leaves(self):
        # Round 12 (4th pass): `src/a.py` and `other/b.py` aliasing one target —
        # a scope covering only `src` must not authorize deleting the distinct
        # entry `other/b.py` through the shared resolved path.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", scope="src")
            (root / "src").mkdir()
            (root / "other").mkdir()
            (root / "src" / "shared.py").write_text("x", encoding="utf-8")
            (root / "src" / "a.py").symlink_to(root / "src" / "shared.py")
            (root / "other" / "b.py").symlink_to(root / "src" / "shared.py")
            patch = "*** Begin Patch\n*** Delete File: other/b.py\n*** End Patch\n"
            payload = {"tool_name": "apply_patch", "cwd": str(root), "tool_input": {"command": patch}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_clustered_bsd_find_flags_are_scanned_past(self):
        # Round 12 (5th pass): BSD find clusters pre-path flags (`-Lx`, `-dsx`)
        # — an exact-token skip stops at the cluster and records no roots.
        cases = [
            ("find -Lx .stage -delete", False),
            ("find -dsx .stage -delete", False),
            ("find -Lx alias -delete", True),  # cluster carries follow mode
        ]
        for command, needs_alias in cases:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.write_stage_file(root, "index.md", "# Stage\n")
                if needs_alias:
                    (root / "alias").symlink_to(root / ".stage", target_is_directory=True)
                payload = {
                    "tool_name": "Bash",
                    "cwd": str(root),
                    "tool_input": {"command": command},
                }

                result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual(decision(result), "deny", command)
            self.assertIn("deleting", reason(result).lower())

    def test_cd_rebases_relative_delete_operands(self):
        # Round 12 (5th pass): `cd build && find . -delete` traverses build,
        # not the workspace — relative operands follow the tracked cwd. The
        # workspace stays protected through the rebased spelling.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            allow_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build && find . -delete"},
            }
            deny_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build && rm -rf ../.stage"},
            }

            allowed = stage_guard.handle_event("pre-tool-use", allow_payload)
            denied = stage_guard.handle_event("pre-tool-use", deny_payload)

        self.assertEqual(decision(allowed), "allow")
        self.assertEqual(decision(denied), "deny")
        self.assertIn("deleting", reason(denied).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_ancestor_delete_covers_externally_symlinked_stage(self):
        # Round 12 (5th pass): `.stage -> <outside>` — deleting the workspace
        # removes the logical `.stage` entry (detaches the harness) even though
        # the real tree lives elsewhere.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "ws"
            outside = base / "stage-data"
            outside.mkdir(parents=True)
            root.mkdir(parents=True)
            (root / ".stage").symlink_to(outside, target_is_directory=True)
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": f"rm -rf {root}"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_workspace_stage_symlink_entry_is_never_exempt(self):
        # Round 12 (6th pass): `.stage -> <external>` — deleting the LOGICAL
        # `.stage` entry detaches the harness; the link-only exemption must not
        # apply to the workspace's own `.stage` entry.
        for command in ("rm -rf .stage", "find .stage -delete"):
            with tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp)
                root = base / "ws"
                outside = base / "stage-data"
                outside.mkdir(parents=True)
                root.mkdir(parents=True)
                (root / ".stage").symlink_to(outside, target_is_directory=True)
                payload = {
                    "tool_name": "Bash",
                    "cwd": str(root),
                    "tool_input": {"command": command},
                }

                result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual(decision(result), "deny", command)

    def test_foreign_stage_basename_outside_project_is_allowed(self):
        # Round 12 (6th pass): once canonical classification succeeds, the
        # lexical basename fallback must not deny a DIFFERENT project's
        # `.stage` (`cd build && rm -rf .stage` removes build/.stage).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build" / ".stage").mkdir(parents=True)
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build && rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_find_implicit_current_directory_root(self):
        # Round 12 (6th pass): GNU `find -delete` roots at `.` implicitly.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            deny_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "find -delete"},
            }
            allow_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build && find -delete"},
            }

            denied = stage_guard.handle_event("pre-tool-use", deny_payload)
            allowed = stage_guard.handle_event("pre-tool-use", allow_payload)

        self.assertEqual(decision(denied), "deny")
        self.assertIn("deleting", reason(denied).lower())
        self.assertEqual(decision(allowed), "allow")

    def test_failed_cd_keeps_previous_anchor(self):
        # Round 12 (6th pass): `cd missing || find . -delete` — the shell stays
        # in the workspace when cd fails, so the rebase must require an
        # existing directory.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd missing || find . -delete"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_lexical_collapse_does_not_smuggle_scope_authorization(self):
        # Round 12 (6th pass): `alias/../other/file.py` (alias -> src/nested)
        # lands in src/other/, but its lexical collapse reads other/ — a scope
        # covering only `other` must not authorize it.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", scope="other")
            (root / "src" / "nested").mkdir(parents=True)
            (root / "src" / "other").mkdir(parents=True)
            (root / "other").mkdir()
            (root / "alias").symlink_to(root / "src" / "nested", target_is_directory=True)
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "alias/../other/file.py", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_last_find_traversal_option_wins(self):
        # Round 12 (6th pass): POSIX find honors the LAST of -H/-L/-P — a
        # final -P removes only the symlink, which stays allowed.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "alias").symlink_to(root / ".stage", target_is_directory=True)
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "find -L -P alias -delete"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_conditional_cd_keeps_workspace_anchor(self):
        # Round 12 (7th pass): `false && cd build ; rm -rf .stage` — the cd may
        # be short-circuited, so both cwd states must be considered.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "false && cd build ; rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_deleting_entry_with_structurally_excluded_target_needs_registration(self):
        # Round 12 (7th pass): `src/link -> .git/config` — deleting the ENTRY
        # acts on the governed source tree; the structural `.git` exclusion
        # must not win through the dereferenced leaf.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / ".git").mkdir()
            (root / ".git" / "config").write_text("x", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "link").symlink_to(root / ".git" / "config")
            patch = "*** Begin Patch\n*** Delete File: src/link\n*** End Patch\n"
            deny_payload = {
                "tool_name": "apply_patch",
                "cwd": str(root),
                "tool_input": {"command": patch},
            }

            denied = stage_guard.handle_event("pre-tool-use", deny_payload)

            self.write_work_item(root, status="active", scope="src")
            allowed = stage_guard.handle_event("pre-tool-use", deny_payload)

        self.assertEqual(decision(denied), "deny")
        self.assertIn("registration", reason(denied).lower())
        self.assertEqual(decision(allowed), "allow")

    def test_pipeline_cd_does_not_replace_anchor(self):
        # Round 12 (8th pass): `cd build | rm -rf .stage` — a pipeline-local cd
        # never changes the cwd rm runs from.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build | rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_cd_dash_returns_to_previous_anchor(self):
        # Round 12 (8th pass): `cd -` returns to OLDPWD — the tracker must not
        # stay in build while the real shell is back in the workspace.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build ; cd - ; rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_scope_declared_with_dot_segments_authorizes_its_target(self):
        # Round 12 (8th pass): `scope: alias/../other` must keep its dot
        # segments until entry canonicalization — a lexical pre-collapse to
        # `other` rejects the exact declared spelling.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", scope="alias/../other")
            (root / "src" / "nested").mkdir(parents=True)
            (root / "src" / "other").mkdir(parents=True)
            (root / "alias").symlink_to(root / "src" / "nested", target_is_directory=True)
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "alias/../other/x.py", "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_promotes_declared_with_dot_segments_authorizes_its_target(self):
        # Round 12 (8th pass): promotes/intent spelled through a symlink and
        # `..` must canonicalize to the same entry as the write target.
        path = "alias/../../past/canon/principles.md"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.promotable_work_item(root, promotes=path)
            (root / ".stage" / "past" / "canon").mkdir(parents=True, exist_ok=True)
            (root / ".stage" / "present" / "x").mkdir(parents=True, exist_ok=True)
            (root / "alias").symlink_to(
                root / ".stage" / "present" / "x", target_is_directory=True
            )
            stage_guard.write_intent_file(
                root / ".stage", {"type": "promotion", "work_item": "W-0001"}, path
            )
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": path, "content": "x"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_attached_separators_split_before_delete_scan(self):
        # Round 12 (9th pass): shlex leaves `true;`/`-delete;` as one token —
        # the delete command must still be identified without whitespace around
        # separators. Newlines also separate commands.
        for command in (
            "true; find .stage -delete",
            "rm -rf .stage; echo done",
            "echo hi\nrm -rf .stage",
            "echo hi & rm -rf .stage",
        ):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.write_stage_file(root, "index.md", "# Stage\n")
                payload = {
                    "tool_name": "Bash",
                    "cwd": str(root),
                    "tool_input": {"command": command},
                }

                result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual(decision(result), "deny", command)
            self.assertIn("deleting", reason(result).lower())

    def test_quoted_separator_is_not_split(self):
        # Companion: a quoted `;` stays inside its token (not a real separator).
        # shell_tokens carries a sentinel for the quoted operator; restoring it
        # yields the literal, and there is no standalone `;` separator token.
        tokens = stage_guard.shell_tokens('rm "a;b"')
        self.assertEqual([stage_guard._restore_sentinels(t) for t in tokens], ["rm", "a;b"])
        self.assertNotIn(";", tokens)

    def test_failed_dotted_cd_keeps_workspace_anchor(self):
        # Round 12 (9th pass): `cd build/missing/..` fails (build/missing is
        # absent) even though resolve() would collapse it to build; the real
        # shell stays in the workspace.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            deny_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build/missing/.. ; rm -rf .stage"},
            }
            # A cd through an EXISTING intermediate succeeds and rebases.
            (root / "build" / "sub").mkdir()
            allow_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build/sub/.. ; rm -rf .stage"},
            }

            denied = stage_guard.handle_event("pre-tool-use", deny_payload)
            allowed = stage_guard.handle_event("pre-tool-use", allow_payload)

        self.assertEqual(decision(denied), "deny")
        self.assertEqual(decision(allowed), "allow")

    def test_popd_returns_to_directory_stack_entry(self):
        # Round 12 (9th pass): `pushd build ; cd /tmp ; popd` returns to the
        # workspace (stack entry), not to the cwd before the last cd.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "pushd build ; cd /tmp ; popd ; rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_find_follow_flag_ignores_exec_program_arguments(self):
        # Round 12 (9th pass): `-P` as an argument to echo inside -exec must not
        # be read as find's own traversal option and cancel the -L follow mode.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "alias").symlink_to(root / ".stage", target_is_directory=True)
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {
                    "command": "find -L alias -depth -exec rm -rf {} + -exec echo -P {} +",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_multiline_quotes_and_continuations_are_preserved(self):
        # Round 12 (10th pass): tokenizing per physical line breaks multiline
        # quotes and backslash continuations, dropping a later destructive
        # command from inspection.
        for command in (
            'echo "line1\nline2" ; rm -rf .stage',
            "rm -rf \\\n.stage",
            "echo hi\nrm -rf .stage",
        ):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.write_stage_file(root, "index.md", "# Stage\n")
                payload = {
                    "tool_name": "Bash",
                    "cwd": str(root),
                    "tool_input": {"command": command},
                }

                result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual(decision(result), "deny", repr(command))
            self.assertIn("deleting", reason(result).lower())

    def test_heredoc_body_is_not_an_executable_group(self):
        # Round 12 (10th pass): a heredoc body containing `rm -rf .stage` is
        # data, not a command — it must not be denied.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cat <<EOF\nrm -rf .stage\nEOF"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_write_scan_stops_at_background_operator(self):
        # Round 12 (10th pass): `cp a .stage/past/x & echo done` — the past
        # write must be seen, not masked by taking `done` as the destination.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", scope="*")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cp a .stage/past/x & echo done"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("promotion", reason(result).lower())

    def test_background_cd_does_not_move_caller(self):
        # Round 12 (10th pass): `cd build & rm -rf .stage` runs cd in a
        # background subshell; rm still deletes from the workspace.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build & rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_failed_cd_branch_is_retained_across_anchors(self):
        # Round 12 (10th pass): `false && cd build ; cd sub ; rm -rf .stage`
        # with only build/sub present — cd sub fails from the workspace branch,
        # which must survive.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build" / "sub").mkdir(parents=True)
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "false && cd build ; cd sub ; rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_bare_pushd_swaps_directory_stack(self):
        # Round 12 (10th pass): bare `pushd` swaps cwd with the stack top;
        # `pushd build ; cd /tmp ; pushd ; rm -rf .stage` returns to workspace.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "pushd build ; cd /tmp ; pushd ; rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_multi_operand_cd_fails(self):
        # Round 12 (10th pass): `cd build extra` is a bash error (too many
        # arguments); the shell stays in the workspace.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build extra ; rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_escaped_exec_terminator_keeps_delete_in_find_group(self):
        # Round 12 (10th pass): `\;` unescapes to `;`; the find -exec clause
        # terminator must not split the group and drop `-delete`.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "find .stage -exec echo {} \\; -delete"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_find_dash_prefixed_root_after_ddash(self):
        # Round 12 (10th pass): `find -- -.cache -delete` has a valid dash-led
        # root that is not `.stage` — must not be over-denied via implicit `.`.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "-.cache").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "find -- -.cache -delete"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_file_symlink_scope_does_not_cross_authorize(self):
        # Round 12 (10th pass): `scope: aliases/link.py` (link.py -> src/actual.py)
        # must not authorize a direct write to the distinct entry src/actual.py.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "aliases").mkdir()
            (root / "src" / "actual.py").write_text("x", encoding="utf-8")
            (root / "aliases" / "link.py").symlink_to(root / "src" / "actual.py")
            self.write_work_item(root, status="active", scope="aliases/link.py")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "src/actual.py", "content": "y"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration", reason(result).lower())

    def test_quoted_heredoc_operator_is_not_a_heredoc(self):
        # Round 12 (11th pass): a quoted `<<EOF` is literal text, not a heredoc
        # declaration — the following rm must still be inspected.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "echo '<<EOF'\nrm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_exec_terminator_only_applies_inside_find(self):
        # Round 12 (11th pass): `-exec` outside find must not swallow a `;`
        # separator (`echo -exec ; rm -rf .stage`).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "echo -exec ; rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_cd_redirection_is_not_an_operand(self):
        # Round 12 (11th pass): `cd build >/dev/null` is a successful cd with a
        # redirection, not a multi-operand error — the rebase must apply.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            deny_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build >/dev/null && rm -rf ../.stage"},
            }
            # cd succeeds → find runs from build, whose .stage does not exist.
            allow_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build > /dev/null && find . -delete"},
            }

            denied = stage_guard.handle_event("pre-tool-use", deny_payload)
            allowed = stage_guard.handle_event("pre-tool-use", allow_payload)

        self.assertEqual(decision(denied), "deny")
        self.assertEqual(decision(allowed), "allow")

    def test_arithmetic_shift_is_not_a_heredoc(self):
        # Round 12 (12th pass): `<<` inside `$(( ))` is a shift, not a heredoc.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "n=$((1<<2))\nrm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_heredoc_delimiter_with_punctuation(self):
        # Round 12 (12th pass): a hyphenated delimiter must be captured whole,
        # so the body ends and the following rm is inspected.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            deny_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cat <<END-MARKER\ndata\nEND-MARKER\nrm -rf .stage"},
            }
            # Body content is still ignored.
            allow_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cat <<END-MARKER\nrm -rf .stage\nEND-MARKER"},
            }

            denied = stage_guard.handle_event("pre-tool-use", deny_payload)
            allowed = stage_guard.handle_event("pre-tool-use", allow_payload)

        self.assertEqual(decision(denied), "deny")
        self.assertEqual(decision(allowed), "allow")

    def test_quoted_control_operator_is_not_a_separator(self):
        # Round 12 (12th pass): a quoted `;` is an argument, not a separator —
        # `printf ';' cd build` is one command, so cd never runs and rm deletes
        # from the workspace.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "printf ';' cd build; rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_pushd_n_flag_does_not_change_cwd(self):
        # Round 12 (12th pass): `pushd -n build` only edits the stack; the shell
        # stays in the workspace.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "pushd -n build ; rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_fd_redirection_is_not_a_background_separator(self):
        # Round 12 (12th pass): `2>&1` is a redirection, not `&` background —
        # cd succeeds, so a following relative delete is anchored at build.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            allow_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build 2>&1 ; rm -rf .stage"},
            }
            deny_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build 2>&1 ; rm -rf ../.stage"},
            }

            allowed = stage_guard.handle_event("pre-tool-use", allow_payload)
            denied = stage_guard.handle_event("pre-tool-use", deny_payload)

        self.assertEqual(decision(allowed), "allow")
        self.assertEqual(decision(denied), "deny")

    def test_failed_cd_does_not_update_oldpwd(self):
        # Round 12 (13th pass): `cd build ; cd missing ; cd - ; rm -rf .stage`
        # — cd missing fails, so cd - returns to the workspace, not build.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build ; cd missing ; cd - ; rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_attached_ampersand_redirect_is_stripped(self):
        # Round 12 (13th pass): `&>/dev/null` is an attached redirect, not a cd
        # operand.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build &>/dev/null ; rm -rf ../.stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_wrapped_and_powershell_cd_forms_are_tracked(self):
        # Round 12 (13th pass): `command cd build` and PowerShell `Set-Location`
        # both change the cwd.
        for command in (
            "command cd build ; rm -rf ../.stage",
            "Set-Location build ; Remove-Item ../.stage -Recurse -Force",
        ):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.write_stage_file(root, "index.md", "# Stage\n")
                (root / "build").mkdir()
                payload = {
                    "tool_name": "Bash",
                    "cwd": str(root),
                    "tool_input": {"command": command},
                }

                result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual(decision(result), "deny", command)
            self.assertIn("deleting", reason(result).lower())

    def test_bare_arithmetic_command_is_not_a_heredoc(self):
        # Round 12 (13th pass): bare `((1 << END))` is arithmetic, not a heredoc.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "((1 << END)) ;\nrm -rf .stage ;\nEND"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_cd_ddash_dash_prefixed_operand(self):
        # Round 12 (13th pass): `cd -- -foo` enters the directory named -foo.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "-foo").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd -- -foo ; rm -rf ../.stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_whole_tree_delete_allowed_without_stage(self):
        # Round 12 (13th pass): a pre-init workspace has no `.stage` to protect,
        # so `rm -rf .` must not be denied.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "rm -rf ."},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_backslash_and_split_quote_heredoc_delimiter(self):
        # Round 12 (13th pass): `<<\EOF` and `<<E"OF"` are valid quoted heredoc
        # delimiters — body must be treated as data.
        for command in (
            "cat <<\\EOF\nrm -rf .stage\nEOF",
            'cat <<E"OF"\nrm -rf .stage\nEOF',
        ):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.write_stage_file(root, "index.md", "# Stage\n")
                payload = {
                    "tool_name": "Bash",
                    "cwd": str(root),
                    "tool_input": {"command": command},
                }

                result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual(decision(result), "allow", command)

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_logical_cwd_dotdot_after_symlink(self):
        # Round 12 (14th pass): bash `cd -L` applies `..` to the LOGICAL path —
        # `cd link ; cd ..` (link -> build/deep) returns to the workspace.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build" / "deep").mkdir(parents=True)
            (root / "link").symlink_to(root / "build" / "deep", target_is_directory=True)
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd link ; cd .. ; rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    @unittest.skipIf(os.name == "nt" or os.geteuid() == 0, "needs POSIX non-root for X_OK")
    def test_cd_into_untraversable_dir_fails(self):
        # Round 12 (14th pass): a dir without execute permission cannot be
        # entered; `cd build ; rm -rf .stage` stays in the workspace.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            build = root / "build"
            build.mkdir()
            build.chmod(0)
            try:
                payload = {
                    "tool_name": "Bash",
                    "cwd": str(root),
                    "tool_input": {"command": "cd build ; rm -rf .stage"},
                }
                result = stage_guard.handle_event("pre-tool-use", payload)
            finally:
                build.chmod(0o700)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_external_wrapper_cd_is_not_peeled(self):
        # Over-engineering audit: `nohup`/`nice`/`time` cannot run the shell
        # builtin `cd`, so the shell stays put — the wrapper must NOT be peeled
        # to track a phantom cd (which would be fail-open).
        for command in (
            "nohup cd build ; rm -rf .stage",
            "nice cd build ; rm -rf .stage",
        ):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.write_stage_file(root, "index.md", "# Stage\n")
                (root / "build").mkdir()
                payload = {
                    "tool_name": "Bash",
                    "cwd": str(root),
                    "tool_input": {"command": command},
                }

                result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual(decision(result), "deny", command)
            self.assertIn("deleting", reason(result).lower())

    def test_powershell_backtick_escaped_separator(self):
        # Round 12 (14th pass): a PowerShell backtick escapes the following `;`
        # — `Write-Output `; Set-Location build` is one command, so the delete
        # runs from the workspace.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {
                    "command": "Write-Output `; Set-Location build ; Remove-Item .stage -Recurse",
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_heredoc_terminator_space_indent_is_not_end(self):
        # Round 12 (14th pass): a plain `<<EOF` terminator must match exactly; a
        # space-indented `  EOF` is still body, so the rm below it is data.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cat <<EOF\n  EOF\nrm -rf .stage\nEOF"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    def test_cd_attached_redirection_is_split(self):
        # Round 12 (15th pass, representative): `cd build>/dev/null` is a
        # successful cd with an attached redirection.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd build>/dev/null ; cd .. ; rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    def test_unknown_cd_option_fails_closed(self):
        # Round 12 (15th pass, representative): bash rejects `cd -Z`, so the
        # shell stays in the workspace.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "build").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "cd -Z build ; rm -rf .stage"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("deleting", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_content_write_through_excluded_symlink_is_governed(self):
        # Round 12 (15th pass, representative): a Write to `.git/link.py`
        # (-> src/app.py) modifies the governed source through the symlink; the
        # structural `.git` exclusion applies to unlink, not content writes.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / ".git").mkdir()
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("x", encoding="utf-8")
            (root / ".git" / "link.py").symlink_to(root / "src" / "app.py")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": ".git/link.py", "content": "y"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration", reason(result).lower())

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_content_write_matches_scope_by_resolved_target(self):
        # Round 12 (15th pass, representative): a Write to `aliases/link.py`
        # (-> src/app.py) modifies src/app.py; a scope of only `aliases` must
        # not authorize it (content writes follow the symlink).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "aliases").mkdir()
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("x", encoding="utf-8")
            (root / "aliases" / "link.py").symlink_to(root / "src" / "app.py")
            self.write_work_item(root, status="active", scope="aliases")
            payload = {
                "tool_name": "Write",
                "cwd": str(root),
                "tool_input": {"file_path": "aliases/link.py", "content": "y"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration", reason(result).lower())

    def test_destructive_find_below_stage_sibling_is_allowed(self):
        # Companion: a destructive find rooted OUTSIDE `.stage`'s branch stays
        # allowed — ancestor detection must not blanket-deny cleanups.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            (root / "src").mkdir()
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {"command": "find src -name '*.pyc' -delete"},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")

    @unittest.skipIf(os.name == "nt", "symlink creation needs privileges on Windows")
    def test_scope_covers_aliased_parent_with_outward_leaf(self):
        # Companion: a work item scoped to `src` authorizes the same deletion —
        # the entry form must reach the scope match, not just the gate.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_work_item(root, status="active", scope="src")
            (root / "src").mkdir()
            (root / "outside.txt").write_text("x", encoding="utf-8")
            (root / "src" / "link").symlink_to(root / "outside.txt")
            (root / "alias").symlink_to(root / "src", target_is_directory=True)
            patch = "*** Begin Patch\n*** Delete File: alias/link\n*** End Patch\n"
            payload = {"tool_name": "apply_patch", "cwd": str(root), "tool_input": {"command": patch}}

            result = stage_guard.handle_event("pre-tool-use", payload)

        self.assertEqual(decision(result), "allow")


class ConfiguredWriteToolTest(unittest.TestCase):
    """settings.json `extra_write_tools` — the registration seam for host/MCP
    file-writing tools whose names are not in the built-in allowlist."""

    def write_stage_file(self, root: Path, relative: str, content: str) -> Path:
        path = root / ".stage" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_work_item(self, root: Path, *, scope: str) -> Path:
        return self.write_stage_file(
            root,
            "present/work/items/W-0001.md",
            (
                "---\nid: W-0001\ntitle: Test work\nstatus: active\nverification: pending\n"
                f"retrospective: pending\nretrospective_ref:\npromotion: pending\nscope: {scope}\n"
                "promotes:\n---\n# W-0001 Test work\n"
            ),
        )

    def write_settings(self, root: Path, data: dict) -> Path:
        return self.write_stage_file(root, "settings.json", json.dumps(data))

    def payload(self, root: Path, target: str) -> dict:
        return {
            "tool_name": "mcp__filesystem__write_file",
            "cwd": str(root),
            "tool_input": {"path": target, "content": "x"},
        }

    def test_unregistered_tool_name_bypasses_gates_by_default(self):
        # Documented limit: a tool name the harness does not know is not gated.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")

            result = stage_guard.handle_event("pre-tool-use", self.payload(root, "src/app.py"))

        self.assertEqual(decision(result), "allow")

    def test_configured_write_tool_hits_registration_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.write_settings(root, {"extra_write_tools": ["mcp__filesystem__write_file"]})

            result = stage_guard.handle_event("pre-tool-use", self.payload(root, "src/app.py"))

        self.assertEqual(decision(result), "deny")
        self.assertIn("registration", reason(result).lower())

    def test_configured_write_tool_with_matching_scope_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.write_settings(root, {"extra_write_tools": ["mcp__filesystem__write_file"]})
            self.write_work_item(root, scope="src")

            result = stage_guard.handle_event("pre-tool-use", self.payload(root, "src/app.py"))

        self.assertEqual(decision(result), "allow")

    def test_configured_write_tool_hits_promotion_gate_for_past(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.write_settings(root, {"extra_write_tools": ["mcp__filesystem__write_file"]})

            result = stage_guard.handle_event(
                "pre-tool-use", self.payload(root, ".stage/past/canon/principles.md")
            )

        self.assertEqual(decision(result), "deny")
        self.assertIn("promotion", reason(result).lower())

    def test_malformed_settings_drops_extra_tools_but_keeps_builtin_gates(self):
        # Registration read from broken settings yields no extra tools — the
        # unknown name falls back to the documented ungated default, while
        # built-in tools stay behind the governance fail-closed deny.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_stage_file(root, "index.md", "# Stage\n")
            self.write_stage_file(root, "settings.json", "{not json")

            unknown = stage_guard.handle_event("pre-tool-use", self.payload(root, "src/app.py"))
            builtin = stage_guard.handle_event(
                "pre-tool-use",
                {
                    "tool_name": "Write",
                    "cwd": str(root),
                    "tool_input": {"file_path": "src/app.py", "content": "x"},
                },
            )

        self.assertEqual(decision(unknown), "allow")
        self.assertEqual(decision(builtin), "deny")
        self.assertIn("governance", reason(builtin).lower())


if __name__ == "__main__":
    unittest.main()
