from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "escalate_work.py"
DECISION_TEMPLATE = """---
id: DE-00000000
work_item: W-00000000
status: open
---

# DE-00000000 Title

## Question


## Options


## Principles applied


## Chosen direction


## Reason


## Follow-up
"""
ACTIVE_INDEX = (
    "# Active Work\n\n"
    "| Work | Kind | Venue | Purpose | Status | Owner | Item |\n"
    "|---|---|---|---|---|---|---|\n"
    "| W-00000001 | development | codex | Stop safely | active | codex | "
    "[current/W-00000001.md](current/W-00000001.md) |\n"
)
WORK_ITEM = """---
id: W-00000001
title: Stop safely
kind: development
venue: codex
parent:
status: {status}
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
scope: src
promotes:
decision_refs: DE-00000003
---

# W-00000001 Stop safely

## Progress
"""


class EscalateWorkTest(unittest.TestCase):
    def make_project(self, status: str = "active") -> tuple[tempfile.TemporaryDirectory, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        stage_root = root / ".stage"
        (stage_root / "work/current").mkdir(parents=True)
        (stage_root / "decisions/pending").mkdir(parents=True)
        (stage_root / "official/decisions/records").mkdir(parents=True)
        (stage_root / "settings.json").write_text(
            json.dumps({"schema_version": 4}), encoding="utf-8"
        )
        (stage_root / "work/current/W-00000001.md").write_text(
            WORK_ITEM.format(status=status), encoding="utf-8"
        )
        (stage_root / "work/active.md").write_text(ACTIVE_INDEX, encoding="utf-8")
        (stage_root / "work/review.md").write_text("# Review Candidates\n", encoding="utf-8")
        (stage_root / "decisions/pending/_template.md").write_text(
            DECISION_TEMPLATE, encoding="utf-8"
        )
        (stage_root / "decisions/index.md").write_text(
            "# Pending Decisions\n\n| Decision | Status | Owner | Link |\n"
            "|---|---|---|---|\n",
            encoding="utf-8",
        )
        (stage_root / "decisions/pending/DE-00000005.md").write_text(
            "---\nid: DE-00000005\nstatus: open\n---\n", encoding="utf-8"
        )
        (stage_root / "official/decisions/records/DE-00000007.md").write_text(
            "---\nid: DE-00000007\nstatus: promoted\n---\n", encoding="utf-8"
        )
        return tmp, root

    def run_cli(self, root: Path, reason: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--project-root",
                str(root),
                "W-00000001",
                "--reason",
                reason,
            ],
            capture_output=True,
            text=True,
        )

    def test_active_item_becomes_blocked_with_linked_pending_decision(self):
        tmp, root = self.make_project()
        with tmp:
            reason = "Acceptance failed repeatedly; decide whether to revise the requirement."

            result = self.run_cli(root, reason)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            item = (root / ".stage/work/current/W-00000001.md").read_text(encoding="utf-8")
            decision_path = root / ".stage/decisions/pending/DE-00000008.md"
            decision = decision_path.read_text(encoding="utf-8")
            active = (root / ".stage/work/active.md").read_text(encoding="utf-8")
            decision_index = (root / ".stage/decisions/index.md").read_text(encoding="utf-8")

            self.assertRegex(item, r"(?m)^status: blocked$")
            self.assertRegex(item, r"(?m)^decision_refs: DE-00000003, DE-00000008$")
            self.assertIn("work_item: W-00000001", decision)
            self.assertIn("status: open", decision)
            self.assertIn(reason, decision)
            self.assertIn("| blocked |", active)
            self.assertIn("W-00000001", active)
            self.assertIn("DE-00000008", decision_index)
            self.assertIn("DE-00000008", result.stdout)

    def test_non_open_item_is_refused_without_changes(self):
        tmp, root = self.make_project(status="completed")
        with tmp:
            item_path = root / ".stage/work/current/W-00000001.md"
            before = item_path.read_text(encoding="utf-8")

            result = self.run_cli(root, "Need a decision.")

            self.assertEqual(1, result.returncode)
            self.assertIn("refusing", result.stderr)
            self.assertEqual(before, item_path.read_text(encoding="utf-8"))
            self.assertEqual(
                ["DE-00000005.md", "_template.md"],
                sorted(path.name for path in (root / ".stage/decisions/pending").glob("*.md")),
            )
            self.assertNotRegex(
                (root / ".stage/decisions/index.md").read_text(encoding="utf-8"),
                re.compile(r"DE-00000008"),
            )


if __name__ == "__main__":
    unittest.main()
