# The PreToolUse enum gate rejects a work-item write whose projected frontmatter
# carries an invalid status/verification/retrospective/promotion value — the
# `retrospective: not_required` class of typo that the audit only caught after
# the write landed (WORK005). Valid values pass.
from __future__ import annotations

import importlib.util
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
    if not result:
        return "allow"
    return result.get("hookSpecificOutput", {}).get("permissionDecision", "allow")


VALID = (
    "---\nid: W-00000001\nkind: chore\nparent:\nsource:\nstatus: active\n"
    "verification: pending\nretrospective: pending\nretrospective_ref:\n"
    "promotion: pending\nscope: x\npromotes:\ndecision_refs:\n---\n\n# W-00000001 X\n"
)


class EnumGateTest(unittest.TestCase):
    def payload(self, root: Path, content: str) -> dict:
        return {
            "cwd": str(root),
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(root / ".stage/present/work/items/W-00000001.md"),
                "content": content,
            },
        }

    def make(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / ".stage/present/work/items").mkdir(parents=True)
        return tmp, root

    def test_valid_enums_allowed(self):
        tmp, root = self.make()
        with tmp:
            self.assertEqual(decision(stage_guard.validate_pre_tool(self.payload(root, VALID))), "allow")

    def test_invalid_retrospective_denied(self):
        tmp, root = self.make()
        with tmp:
            bad = VALID.replace("retrospective: pending", "retrospective: not_required")
            self.assertEqual(decision(stage_guard.validate_pre_tool(self.payload(root, bad))), "deny")

    def test_invalid_status_denied(self):
        tmp, root = self.make()
        with tmp:
            bad = VALID.replace("status: active", "status: done")
            self.assertEqual(decision(stage_guard.validate_pre_tool(self.payload(root, bad))), "deny")


if __name__ == "__main__":
    unittest.main()
