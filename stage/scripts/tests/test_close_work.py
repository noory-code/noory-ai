from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI = Path(__file__).resolve().parents[2] / "skills" / "stage-retrospective" / "close_work.py"

ITEM = """---
id: W-00000001
kind: chore
status: active
verification: pending
retrospective: {retro}
retrospective_ref: {ref}
promotion: {promotion}
---

# W-00000001 Sample

## Verification


## Retrospective

See R.

## Promotion decision
"""

ACTIVE = (
    "# Active Work\n\n| Work | Kind | Venue | Purpose | Status | Owner | Item |\n|---|---|---|---|---|---|---|\n"
    "| W-00000001 | chore | claude | x | active | Claude | [items/W-00000001.md](items/W-00000001.md) |\n"
)
REVIEW = "# Review Candidates\n\n| Artifact | Verification | Retrospective | Promotion | Item |\n|---|---|---|---|---|\n"


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), "--project-root", str(root), *args], capture_output=True, text=True
    )


class CloseWorkTest(unittest.TestCase):
    def make(self, retro="completed", ref="R-00000001", promotion="not_applicable", with_ref_file=True):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / ".stage/present/work/items").mkdir(parents=True)
        (root / ".stage/present/work/retrospectives").mkdir(parents=True)
        (root / ".stage/present/work/items/W-00000001.md").write_text(
            ITEM.format(retro=retro, ref=ref, promotion=promotion), encoding="utf-8"
        )
        if with_ref_file and ref:
            (root / ".stage/present/work/retrospectives" / f"{ref}.md").write_text("---\nid: R\n---\n", encoding="utf-8")
        (root / ".stage/present/work/active.md").write_text(ACTIVE, encoding="utf-8")
        (root / ".stage/present/work/review.md").write_text(REVIEW, encoding="utf-8")
        return tmp, root

    def test_passing_check_closes_and_moves(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", "python3 -c \"print('ok')\"")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = (root / ".stage/present/work/items/W-00000001.md").read_text(encoding="utf-8")
            self.assertIn("status: completed", item)
            self.assertIn("verification: passed", item)
            self.assertIn("print('ok')", item)  # evidence embedded
            self.assertNotIn("W-00000001", (root / ".stage/present/work/active.md").read_text(encoding="utf-8"))
            self.assertIn("[items/W-00000001.md]", (root / ".stage/present/work/review.md").read_text(encoding="utf-8"))

    def test_failing_check_changes_nothing(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", "python3 -c \"import sys; sys.exit(1)\"")
            self.assertEqual(proc.returncode, 1)
            item = (root / ".stage/present/work/items/W-00000001.md").read_text(encoding="utf-8")
            self.assertIn("status: active", item)
            self.assertIn("verification: pending", item)

    def test_refuses_without_completed_retrospective(self):
        tmp, root = self.make(retro="pending")
        with tmp:
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("retrospective", proc.stderr)

    def test_refuses_missing_retro_file(self):
        tmp, root = self.make(with_ref_file=False)
        with tmp:
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)

    def test_refuses_non_final_promotion(self):
        tmp, root = self.make(promotion="pending")
        with tmp:
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("promotion", proc.stderr)

    def test_refuses_no_check(self):
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("no --check", proc.stderr)

    def test_check_output_with_backslashes_does_not_crash(self):
        # Regression: check output is spliced into the Verification section; it must
        # not be read as regex-replacement escapes (\1, \U...) — that once crashed
        # set_section and left the item permanently un-closable.
        tmp, root = self.make()
        with tmp:
            proc = run(root, "W-00000001", "--check", r"""python3 -c "print(r'C:\Users\x back \1 \d+')" """)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            item = (root / ".stage/present/work/items/W-00000001.md").read_text(encoding="utf-8")
            self.assertIn("status: completed", item)
            self.assertIn(r"C:\Users\x", item)

    def test_refuses_item_without_verification_section(self):
        tmp, root = self.make()
        with tmp:
            p = root / ".stage/present/work/items/W-00000001.md"
            p.write_text(p.read_text(encoding="utf-8").replace("## Verification\n", "## Notes\n"), encoding="utf-8")
            proc = run(root, "W-00000001", "--check", "true")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("Verification", proc.stderr)

    def test_promotion_arg_sets_final(self):
        tmp, root = self.make(promotion="pending")
        with tmp:
            proc = run(root, "W-00000001", "--promotion", "not_applicable", "--check", "true")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("promotion: not_applicable", (root / ".stage/present/work/items/W-00000001.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
