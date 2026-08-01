from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SCRIPT_ROOT / "refresh_decision_index.py"


class RefreshDecisionIndexTest(unittest.TestCase):
    def write_work(self, root: Path, item_id: str, *, archived: bool) -> None:
        relative = (
            f"official/work/archive/items/{item_id}/_story.md"
            if archived
            else f"work/current/{item_id}/_story.md"
        )
        path = root / ".stage" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        status = "archived" if archived else "active"
        path.write_text(
            f"---\nid: {item_id}\nstatus: {status}\n---\n# {item_id}\n",
            encoding="utf-8",
        )

    def write_decision(self, root: Path, decision_id: str, item_id: str) -> None:
        path = root / ".stage/decisions/pending" / f"{decision_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            (
                f"---\nid: {decision_id}\nwork_item: {item_id}\nstatus: decided\n"
                "authorizes: venue_exception\n---\n"
                f"# {decision_id}\n"
            ),
            encoding="utf-8",
        )

    def run_cli(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--project-root", str(root)],
            capture_output=True,
            text=True,
        )

    def test_refreshes_legacy_korean_table_and_preserves_surrounding_prose(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index = root / ".stage/decisions/index.md"
            index.parent.mkdir(parents=True)
            index.write_text(
                (
                    "# 대기 중 결정\n\n사람이 쓴 설명이다.\n\n"
                    "| 결정 | 상태 | 소유자 | 링크 |\n"
                    "|---|---|---|---|\n"
                    "| DE-00000099 | decided | old | [old](pending/old.md) |\n\n"
                    "## 남겨 둘 절\n\n이 내용은 지우지 않는다.\n"
                ),
                encoding="utf-8",
            )
            self.write_work(root, "W-00000002", archived=True)
            self.write_work(root, "W-00000001", archived=False)
            self.write_decision(root, "DE-00000002", "W-00000002")
            self.write_decision(root, "DE-00000001", "W-00000001")

            result = self.run_cli(root)
            rendered = index.read_text(encoding="utf-8")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("사람이 쓴 설명이다.", rendered)
        self.assertIn("## 남겨 둘 절\n\n이 내용은 지우지 않는다.", rendered)
        self.assertIn(
            "| 결정 | 결정 상태 | 소유 항목 | 소유 항목 상태 | 효력 | 링크 |",
            rendered,
        )
        self.assertIn(
            "| DE-00000001 | decided | "
            "[W-00000001](../work/current/W-00000001/_story.md) | "
            "active | active | [pending/DE-00000001.md](pending/DE-00000001.md) |",
            rendered,
        )
        self.assertIn(
            "| DE-00000002 | decided | "
            "[W-00000002](../official/work/archive/items/W-00000002/_story.md) | "
            "archived | expired | [pending/DE-00000002.md](pending/DE-00000002.md) |",
            rendered,
        )
        self.assertLess(rendered.index("DE-00000001"), rendered.index("DE-00000002"))

    def test_refuses_an_unrecognized_table_without_changing_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index = root / ".stage/decisions/index.md"
            index.parent.mkdir(parents=True)
            before = "# Custom\n\n| Name | Note |\n|---|---|\n| Keep | Me |\n"
            index.write_text(before, encoding="utf-8")
            self.write_work(root, "W-00000001", archived=False)
            self.write_decision(root, "DE-00000001", "W-00000001")

            result = self.run_cli(root)
            after = index.read_text(encoding="utf-8")

        self.assertEqual(2, result.returncode)
        self.assertIn("recognized pending-decision table", result.stderr)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
