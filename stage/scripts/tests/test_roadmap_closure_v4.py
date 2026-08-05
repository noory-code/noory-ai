"""Schema-v4 milestone closure snapshot and revalidation contracts."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


STAGE_ROOT = Path(__file__).resolve().parents[2]
HOOK_ROOT = STAGE_ROOT / "hooks"
HOOK_TEST_ROOT = HOOK_ROOT / "tests"
ROADMAP = STAGE_ROOT / "skills" / "stage-roadmap" / "manage_roadmap.py"
REGISTER = STAGE_ROOT / "skills" / "stage-work" / "register_work.py"
ARCHIVE = STAGE_ROOT / "skills" / "stage-archive" / "archive_work.py"
V4_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "v4" / "project-stage"
for import_root in (HOOK_ROOT, HOOK_TEST_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from hook_test_environment import sanitize_current_hook_environment  # noqa: E402


sanitize_current_hook_environment()

import stage_roadmap  # noqa: E402
import stage_roadmap_closure  # noqa: E402
import stage_guard  # noqa: E402


def run_cli(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROADMAP), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
    )


def run_tool(cli: Path, root: Path, *args: str) -> subprocess.CompletedProcess:
    if cli == REGISTER and "--scale" not in args:
        args = ("--scale", "story", *args)
    if cli == REGISTER and "--purpose" not in args:
        args = (*args, "--purpose", "Deliver the requested outcome")
    if cli == REGISTER and "--success-criterion" not in args:
        args = (*args, "--success-criterion", "The user observes the requested outcome")
    return subprocess.run(
        [sys.executable, str(cli), "--project-root", str(root), *args],
        capture_output=True,
        text=True,
    )


def set_field(path: Path, field: str, value: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        rf"^({re.escape(field)}:)[ \t]*.*$",
        rf"\g<1> {value}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise AssertionError(f"missing field {field} in {path}")
    path.write_text(updated, encoding="utf-8")


class ClosureFixture(unittest.TestCase):
    def make_fixture(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        shutil.copytree(V4_TEMPLATE_ROOT, root / ".stage")
        theme = run_cli(
            root,
            "create-theme",
            "--title",
            "Delivery reliability",
            "--intent",
            "Ship predictably",
        )
        milestone = run_cli(
            root,
            "create-milestone",
            "--theme",
            "TH-00000001",
            "--title",
            "Stable release",
            "--completion-criteria",
            "All release checks pass",
        )
        pursuit = run_cli(root, "open-pursuit", "M-00000001")
        self.assertEqual(0, theme.returncode, theme.stderr)
        self.assertEqual(0, milestone.returncode, milestone.stderr)
        self.assertEqual(0, pursuit.returncode, pursuit.stderr)
        return tmp, root

    def write_work(
        self,
        root: Path,
        item_id: str,
        *,
        location: str,
        status: str,
        disposition: str = "",
        milestone: str = "M-00000001",
    ) -> Path:
        path = root / ".stage" / location / f"{item_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        disposition_line = (
            f"terminal_disposition: {disposition}\n" if disposition else ""
        )
        path.write_text(
            "---\n"
            f"id: {item_id}\n"
            f"milestone: {milestone}\n"
            f"status: {status}\n"
            f"{disposition_line}"
            "---\n\n"
            f"# {item_id} Closure evidence\n",
            encoding="utf-8",
        )
        return path

    def close(self, root: Path, attestation: str = "All release checks passed in CI"):
        return run_cli(
            root,
            "close-milestone",
            "M-00000001",
            "--attestation",
            attestation,
        )


class CloseMilestoneCliTest(ClosureFixture):
    def test_refuses_and_lists_each_non_terminal_linked_card(self):
        tmp, root = self.make_fixture()
        with tmp:
            self.write_work(
                root,
                "W-00000001",
                location="work/current",
                status="active",
            )
            self.write_work(
                root,
                "W-00000002",
                location="work/planned",
                status="captured",
            )

            result = self.close(root)

            self.assertEqual(1, result.returncode)
            self.assertIn("W-00000001", result.stderr)
            self.assertIn("status active", result.stderr)
            self.assertIn("W-00000002", result.stderr)
            self.assertIn("status captured", result.stderr)
            self.assertFalse(
                (root / ".stage/decisions/pending/DE-00000002.md").exists()
            )

    def test_captures_exact_sorted_basis_dispositions_and_attestation(self):
        tmp, root = self.make_fixture()
        with tmp:
            self.write_work(
                root,
                "W-00000002",
                location="official/work/archive/items",
                status="archived",
                disposition="rejected",
            )
            self.write_work(
                root,
                "W-00000001",
                location="official/work/archive/items",
                status="archived",
                disposition="accepted",
            )

            result = self.close(root, "CI, release notes, and rollback drill passed.")

            self.assertEqual(0, result.returncode, result.stderr)
            decision = root / ".stage/decisions/pending/DE-00000002.md"
            text = decision.read_text(encoding="utf-8")
            decision_index = (root / ".stage/decisions/index.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("DE-00000002", decision_index)
            self.assertIn("transition: closure", text)
            self.assertIn("predecessor: DE-00000001", text)
            self.assertIn("| W-00000001 | accepted |", text)
            self.assertIn("| W-00000002 | rejected |", text)
            self.assertLess(text.index("W-00000001"), text.index("W-00000002"))
            self.assertIn("CI, release notes, and rollback drill passed.", text)
            entries, attestation, issues = stage_roadmap_closure.load_closure_basis(
                decision
            )
            self.assertEqual([], list(issues))
            self.assertEqual(
                [("W-00000001", "accepted"), ("W-00000002", "rejected")],
                [(entry.work_item_id, entry.terminal_disposition) for entry in entries],
            )
            self.assertEqual(
                "CI, release notes, and rollback drill passed.", attestation
            )
            state = stage_roadmap.roadmap_record_state(
                root / ".stage",
                root / ".stage/roadmap/milestones/M-00000001.md",
            )
            self.assertEqual("closed", state.status)
            self.assertEqual("DE-00000002", state.effective_head)


class ClosurePromotionRevalidationTest(ClosureFixture):
    def closed_fixture(self) -> tuple[tempfile.TemporaryDirectory, Path, Path]:
        tmp, root = self.make_fixture()
        self.write_work(
            root,
            "W-00000001",
            location="official/work/archive/items",
            status="archived",
            disposition="accepted",
        )
        result = self.close(root)
        self.assertEqual(0, result.returncode, result.stderr)
        return tmp, root, root / ".stage/decisions/pending/DE-00000002.md"

    def test_live_basis_match_passes(self):
        tmp, root, decision = self.closed_fixture()
        with tmp:
            self.assertEqual(
                (),
                stage_roadmap_closure.closure_basis_diff(root / ".stage", decision),
            )

    def test_disposition_drift_is_denied_with_exact_diff(self):
        tmp, root, decision = self.closed_fixture()
        with tmp:
            card = root / ".stage/official/work/archive/items/W-00000001.md"
            set_field(card, "terminal_disposition", "rejected")

            diff = stage_roadmap_closure.closure_basis_diff(
                root / ".stage", decision
            )

            self.assertIn(
                "W-00000001: expected terminal_disposition `accepted`, actual `rejected`",
                diff,
            )

    def test_missing_basis_card_is_denied_with_exact_diff(self):
        tmp, root, decision = self.closed_fixture()
        with tmp:
            (root / ".stage/official/work/archive/items/W-00000001.md").unlink()

            diff = stage_roadmap_closure.closure_basis_diff(
                root / ".stage", decision
            )

            self.assertIn(
                "W-00000001: expected terminal_disposition `accepted`, actual `missing`",
                diff,
            )

    def test_new_unlisted_linked_card_is_denied_with_exact_diff(self):
        tmp, root, decision = self.closed_fixture()
        with tmp:
            self.write_work(
                root,
                "W-00000002",
                location="official/work/archive/items",
                status="archived",
                disposition="rejected",
            )

            diff = stage_roadmap_closure.closure_basis_diff(
                root / ".stage", decision
            )

            self.assertIn(
                "W-00000002: expected `absent`, actual terminal_disposition `rejected`",
                diff,
            )

    def test_projected_new_nested_linked_card_is_denied_with_exact_diff(self):
        tmp, root, decision = self.closed_fixture()
        with tmp:
            diff = stage_roadmap_closure.closure_basis_diff(
                root / ".stage",
                decision,
                {
                    "official/work/archive/items/W-00000002/_story.md": (
                        "---\n"
                        "id: W-00000002\n"
                        "milestone: M-00000001\n"
                        "status: archived\n"
                        "terminal_disposition: rejected\n"
                        "---\n"
                    )
                },
            )

            self.assertIn(
                "W-00000002: expected `absent`, actual terminal_disposition `rejected`",
                diff,
            )


class ReopenStateTest(ClosureFixture):
    def test_superseding_reopen_returns_computed_status_to_active(self):
        tmp, root = self.make_fixture()
        with tmp:
            self.write_work(
                root,
                "W-00000001",
                location="official/work/archive/items",
                status="archived",
                disposition="accepted",
            )
            closed = self.close(root)
            self.assertEqual(0, closed.returncode, closed.stderr)
            stage_root = root / ".stage"
            reopen = stage_root / "decisions/pending/DE-00000003.md"
            reopen.write_text(
                "---\n"
                "id: DE-00000003\n"
                "roadmap_item: M-00000001\n"
                "status: decided\n"
                "transition: reopen\n"
                "predecessor: DE-00000002\n"
                "supersedes: DE-00000002\n"
                "---\n\n"
                "# DE-00000003 Reopen milestone\n",
                encoding="utf-8",
            )
            milestone = stage_root / "roadmap/milestones/M-00000001.md"
            set_field(
                milestone,
                "decision_refs",
                "DE-00000001, DE-00000002, DE-00000003",
            )

            state = stage_roadmap.roadmap_record_state(stage_root, milestone)

            self.assertEqual("active", state.status)
            self.assertEqual("DE-00000003", state.effective_head)


class ClosureEndToEndTest(ClosureFixture):
    def test_archive_close_promote_then_deny_illegal_reattribution(self):
        tmp, root = self.make_fixture()
        with tmp:
            stage_root = root / ".stage"
            for item_id, status, promotion, retro_id in (
                ("W-00000001", "completed", "not_applicable", "R-00000001"),
                ("W-00000002", "rejected", "rejected", "R-00000002"),
            ):
                registered = run_tool(
                    REGISTER,
                    root,
                    "--title",
                    f"Milestone evidence {item_id}",
                    "--kind",
                    "development",
                    "--scope",
                    f"fixture/{item_id}",
                    "--venue",
                    "codex",
                    "--milestone",
                    "M-00000001",
                )
                self.assertEqual(0, registered.returncode, registered.stderr)
                card = stage_root / "work/current" / item_id / "_story.md"
                set_field(card, "status", status)
                set_field(card, "retrospective", "completed")
                set_field(card, "retrospective_ref", retro_id)
                set_field(card, "promotion", promotion)
                (stage_root / "work/retrospectives" / f"{retro_id}.md").write_text(
                    "---\n"
                    f"id: {retro_id}\n"
                    f"work_item: {item_id}\n"
                    "---\n\n"
                    f"# {retro_id} Closure evidence\n",
                    encoding="utf-8",
                )
                archived = run_tool(ARCHIVE, root, item_id)
                self.assertEqual(
                    0, archived.returncode, archived.stdout + archived.stderr
                )

            accepted = (
                stage_root
                / "official/work/archive/items/W-00000001/_story.md"
            ).read_text(encoding="utf-8")
            rejected = (
                stage_root
                / "official/work/archive/items/W-00000002/_story.md"
            ).read_text(encoding="utf-8")
            self.assertIn("terminal_disposition: accepted", accepted)
            self.assertIn("terminal_disposition: rejected", rejected)

            closed = self.close(root, "Both delivery outcomes satisfy the criterion.")
            self.assertEqual(0, closed.returncode, closed.stderr)
            closure_id = "DE-00000002"
            pending = stage_root / "decisions/pending" / f"{closure_id}.md"
            official_relative = (
                f".stage/official/decisions/records/{closure_id}.md"
            )
            promoter = stage_root / "work/current/W-00000099.md"
            promoter.write_text(
                "---\n"
                "id: W-00000099\n"
                "title: Promote closure fixture\n"
                "status: completed\n"
                "verification: passed\n"
                "retrospective: completed\n"
                "promotion: approved\n"
                f"promotes: {official_relative}\n"
                "scope:\n"
                "---\n",
                encoding="utf-8",
            )
            intent = stage_guard.write_intent_file(
                stage_root,
                {"type": "promotion", "work_item": "W-00000099"},
                official_relative,
            )
            self.assertIsNotNone(intent)
            promote_payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "session_id": "closure-e2e",
                "tool_input": {
                    "command": (
                        f"mv .stage/decisions/pending/{closure_id}.md "
                        f"{official_relative}"
                    )
                },
            }
            promotion_gate = stage_guard.handle_event(
                "pre-tool-use", promote_payload
            )
            self.assertEqual({}, promotion_gate)
            set_field(pending, "status", "promoted")
            official = stage_root / "official/decisions/records" / pending.name
            pending.replace(official)
            stage_guard.handle_event("post-tool-use", promote_payload)

            illegal_payload = {
                "tool_name": "Edit",
                "cwd": str(root),
                "tool_input": {
                    "file_path": (
                        ".stage/official/work/archive/items/"
                        "W-00000001/_story.md"
                    ),
                    "old_string": "milestone: M-00000001",
                    "new_string": "milestone: M-00000077",
                },
            }
            denied = stage_guard.handle_event("pre-tool-use", illegal_payload)
            denial_reason = denied["hookSpecificOutput"][
                "permissionDecisionReason"
            ]
            self.assertEqual(
                "deny", denied["hookSpecificOutput"]["permissionDecision"]
            )
            self.assertIn(closure_id, denial_reason)
            self.assertIn("re-attribution", denial_reason.lower())


if __name__ == "__main__":
    unittest.main()
