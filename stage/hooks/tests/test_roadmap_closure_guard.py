"""Schema-v4 closure promotion and frozen-basis write gates."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path


STAGE_ROOT = Path(__file__).resolve().parents[2]
HOOK_ROOT = STAGE_ROOT / "hooks"
V4_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "v4" / "project-stage"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))

import stage_guard  # noqa: E402


def decision(result: dict) -> str:
    if not result:
        return "allow"
    return result["hookSpecificOutput"]["permissionDecision"]


def reason(result: dict) -> str:
    output = result.get("hookSpecificOutput", {})
    return output.get("permissionDecisionReason", "")


class ClosureGuardFixture(unittest.TestCase):
    def make_fixture(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        shutil.copytree(V4_TEMPLATE_ROOT, root / ".stage")
        stage_root = root / ".stage"
        (stage_root / "roadmap/milestones/M-00000001.md").write_text(
            "---\n"
            "id: M-00000001\n"
            "theme:\n"
            "decision_refs: DE-00000001\n"
            "---\n\n"
            "# M-00000001 Frozen milestone\n",
            encoding="utf-8",
        )
        (stage_root / "decisions/pending/DE-00000001.md").write_text(
            "---\n"
            "id: DE-00000001\n"
            "roadmap_item: M-00000001\n"
            "status: decided\n"
            "transition: closure\n"
            "predecessor:\n"
            "supersedes:\n"
            "---\n\n"
            "# DE-00000001 Close milestone\n\n"
            "## Frozen basis\n\n"
            "| Work item | terminal_disposition |\n"
            "|---|---|\n"
            "| W-00000001 | accepted |\n\n"
            "## Completion-criteria attestation\n\n"
            "Release checks passed.\n",
            encoding="utf-8",
        )
        archive = stage_root / "official/work/archive/items/W-00000001.md"
        archive.write_text(
            "---\n"
            "id: W-00000001\n"
            "milestone: M-00000001\n"
            "status: archived\n"
            "terminal_disposition: accepted\n"
            "---\n\n"
            "# W-00000001 Accepted work\n",
            encoding="utf-8",
        )
        return tmp, root

    def write_promoter(self, root: Path, target: str) -> None:
        path = root / ".stage/work/current/W-00000099.md"
        path.write_text(
            "---\n"
            "id: W-00000099\n"
            "title: Authorize fixture mutation\n"
            "status: completed\n"
            "verification: passed\n"
            "retrospective: completed\n"
            "promotion: approved\n"
            f"promotes: {target}\n"
            "scope:\n"
            "---\n",
            encoding="utf-8",
        )
        created = stage_guard.write_intent_file(
            root / ".stage",
            {"type": "promotion", "work_item": "W-00000099"},
            target,
        )
        self.assertIsNotNone(created)

    def edit_payload(self, root: Path) -> dict:
        return {
            "tool_name": "Edit",
            "cwd": str(root),
            "tool_input": {
                "file_path": ".stage/official/work/archive/items/W-00000001.md",
                "old_string": "milestone: M-00000001",
                "new_string": "milestone: M-00000002",
            },
        }


class ReattributionGateTest(ClosureGuardFixture):
    def test_denies_milestone_change_named_by_effective_closure(self):
        tmp, root = self.make_fixture()
        with tmp:
            result = stage_guard.handle_event("pre-tool-use", self.edit_payload(root))

            self.assertEqual("deny", decision(result))
            self.assertIn("DE-00000001", reason(result))
            self.assertIn("re-attribution", reason(result).lower())

    def test_shell_milestone_edit_fails_closed(self):
        tmp, root = self.make_fixture()
        with tmp:
            payload = {
                "tool_name": "Bash",
                "cwd": str(root),
                "tool_input": {
                    "command": (
                        "sed -i 's/milestone: M-00000001/milestone: M-00000002/' "
                        ".stage/official/work/archive/items/W-00000001.md"
                    )
                },
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual("deny", decision(result))
            self.assertIn("DE-00000001", reason(result))
            self.assertIn("re-attribution", reason(result).lower())

    def test_allows_when_same_patch_adds_chain_member_superseding_closure(self):
        tmp, root = self.make_fixture()
        with tmp:
            target = ".stage/official/work/archive/items/W-00000001.md"
            self.write_promoter(root, target)
            patch = """*** Begin Patch
*** Update File: .stage/official/work/archive/items/W-00000001.md
@@
-milestone: M-00000001
+milestone: M-00000002
*** Update File: .stage/roadmap/milestones/M-00000001.md
@@
-decision_refs: DE-00000001
+decision_refs: DE-00000001, DE-00000002
*** Add File: .stage/decisions/pending/DE-00000002.md
+---
+id: DE-00000002
+roadmap_item: M-00000001
+status: decided
+transition: reopen
+predecessor: DE-00000001
+supersedes: DE-00000001
+---
+# DE-00000002 Reopen milestone
*** End Patch"""
            payload = {
                "tool_name": "apply_patch",
                "cwd": str(root),
                "tool_input": {"command": patch},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual("allow", decision(result), reason(result))

    def test_allows_when_closure_is_already_superseded(self):
        tmp, root = self.make_fixture()
        with tmp:
            stage_root = root / ".stage"
            (stage_root / "decisions/pending/DE-00000002.md").write_text(
                "---\n"
                "id: DE-00000002\n"
                "roadmap_item: M-00000001\n"
                "status: decided\n"
                "transition: reopen\n"
                "predecessor: DE-00000001\n"
                "supersedes: DE-00000001\n"
                "---\n",
                encoding="utf-8",
            )
            milestone = stage_root / "roadmap/milestones/M-00000001.md"
            milestone.write_text(
                milestone.read_text(encoding="utf-8").replace(
                    "decision_refs: DE-00000001",
                    "decision_refs: DE-00000001, DE-00000002",
                ),
                encoding="utf-8",
            )
            target = ".stage/official/work/archive/items/W-00000001.md"
            self.write_promoter(root, target)

            result = stage_guard.handle_event("pre-tool-use", self.edit_payload(root))

            self.assertEqual("allow", decision(result), reason(result))


class PromotionGateTest(ClosureGuardFixture):
    def promotion_payload(self, root: Path) -> dict:
        return {
            "tool_name": "Bash",
            "cwd": str(root),
            "tool_input": {
                "command": (
                    "mv .stage/decisions/pending/DE-00000001.md "
                    ".stage/official/decisions/records/DE-00000001.md"
                )
            },
        }

    def test_promotion_revalidation_passes_for_matching_live_basis(self):
        tmp, root = self.make_fixture()
        with tmp:
            target = ".stage/official/decisions/records/DE-00000001.md"
            self.write_promoter(root, target)

            result = stage_guard.handle_event("pre-tool-use", self.promotion_payload(root))

            self.assertEqual("allow", decision(result), reason(result))

    def test_promotion_revalidation_denies_and_preserves_intent_on_diff(self):
        tmp, root = self.make_fixture()
        with tmp:
            target = ".stage/official/decisions/records/DE-00000001.md"
            self.write_promoter(root, target)
            card = root / ".stage/official/work/archive/items/W-00000001.md"
            card.write_text(
                card.read_text(encoding="utf-8").replace(
                    "terminal_disposition: accepted",
                    "terminal_disposition: rejected",
                ),
                encoding="utf-8",
            )

            result = stage_guard.handle_event("pre-tool-use", self.promotion_payload(root))

            self.assertEqual("deny", decision(result))
            self.assertIn(
                "W-00000001: expected terminal_disposition `accepted`, actual `rejected`",
                reason(result),
            )
            self.assertEqual(
                1, len(list((root / ".stage/.runtime/intents").glob("*.json")))
            )

    def test_promotion_revalidation_denies_missing_basis_card_with_diff(self):
        tmp, root = self.make_fixture()
        with tmp:
            target = ".stage/official/decisions/records/DE-00000001.md"
            self.write_promoter(root, target)
            (root / ".stage/official/work/archive/items/W-00000001.md").unlink()

            result = stage_guard.handle_event("pre-tool-use", self.promotion_payload(root))

            self.assertEqual("deny", decision(result))
            self.assertIn(
                "W-00000001: expected terminal_disposition `accepted`, actual `missing`",
                reason(result),
            )

    def test_promotion_revalidation_denies_new_linked_card_with_diff(self):
        tmp, root = self.make_fixture()
        with tmp:
            target = ".stage/official/decisions/records/DE-00000001.md"
            self.write_promoter(root, target)
            (root / ".stage/official/work/archive/items/W-00000002.md").write_text(
                "---\n"
                "id: W-00000002\n"
                "milestone: M-00000001\n"
                "status: archived\n"
                "terminal_disposition: rejected\n"
                "---\n",
                encoding="utf-8",
            )

            result = stage_guard.handle_event("pre-tool-use", self.promotion_payload(root))

            self.assertEqual("deny", decision(result))
            self.assertIn(
                "W-00000002: expected `absent`, actual terminal_disposition `rejected`",
                reason(result),
            )

    def test_promotion_revalidates_projected_work_changes_in_same_patch(self):
        tmp, root = self.make_fixture()
        with tmp:
            target = ".stage/official/decisions/records/DE-00000001.md"
            self.write_promoter(root, target)
            patch = """*** Begin Patch
*** Update File: .stage/official/work/archive/items/W-00000001.md
@@
-terminal_disposition: accepted
+terminal_disposition: rejected
*** Update File: .stage/decisions/pending/DE-00000001.md
*** Move to: .stage/official/decisions/records/DE-00000001.md
@@
-status: decided
+status: promoted
*** End Patch"""
            payload = {
                "tool_name": "apply_patch",
                "cwd": str(root),
                "tool_input": {"command": patch},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual("deny", decision(result))
            self.assertIn(
                "W-00000001: expected terminal_disposition `accepted`, actual `rejected`",
                reason(result),
            )

    def test_promotion_cannot_rewrite_frozen_basis_to_match_live_state(self):
        tmp, root = self.make_fixture()
        with tmp:
            target = ".stage/official/decisions/records/DE-00000001.md"
            self.write_promoter(root, target)
            patch = """*** Begin Patch
*** Update File: .stage/decisions/pending/DE-00000001.md
*** Move to: .stage/official/decisions/records/DE-00000001.md
@@
-status: decided
+status: promoted
-| W-00000001 | accepted |
+| W-00000001 | rejected |
*** End Patch"""
            payload = {
                "tool_name": "apply_patch",
                "cwd": str(root),
                "tool_input": {"command": patch},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual("deny", decision(result))
            self.assertIn("DE-00000001", reason(result))
            self.assertIn("immutable", reason(result))

    def test_promotion_cannot_retarget_closure_frontmatter(self):
        tmp, root = self.make_fixture()
        with tmp:
            target = ".stage/official/decisions/records/DE-00000001.md"
            self.write_promoter(root, target)
            patch = """*** Begin Patch
*** Update File: .stage/decisions/pending/DE-00000001.md
*** Move to: .stage/official/decisions/records/DE-00000001.md
@@
-status: decided
+status: promoted
-roadmap_item: M-00000001
+roadmap_item: M-00000002
*** End Patch"""
            payload = {
                "tool_name": "apply_patch",
                "cwd": str(root),
                "tool_input": {"command": patch},
            }

            result = stage_guard.handle_event("pre-tool-use", payload)

            self.assertEqual("deny", decision(result))
            self.assertIn("roadmap_item", reason(result))
            self.assertIn("immutable", reason(result))


if __name__ == "__main__":
    unittest.main()
