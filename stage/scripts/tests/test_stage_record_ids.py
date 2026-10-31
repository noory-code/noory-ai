from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
CLI = SCRIPTS / "stage_record_ids.py"
sys.path.insert(0, str(SCRIPTS))
import stage_record_ids  # noqa: E402


def record(record_id: str) -> str:
    return f"---\nid: {record_id}\nstatus: active\n---\n\n# {record_id} Title\n"


class StageRecordIdsTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.stage = self.root / ".stage"

    def write(self, relative: str, record_id: str) -> None:
        path = self.stage / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(record(record_id), encoding="utf-8")

    def git(self, *args: str) -> None:
        subprocess.run(
            ["git", "-c", "user.name=Stage Test", "-c", "user.email=stage@example.invalid", *args],
            cwd=self.root,
            check=True,
            capture_output=True,
        )

    def commit_all(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def test_local_numbers_skip_templates_and_runtime_files(self):
        self.write("work/current/W-00000003/_story.md", "W-00000003")
        self.write("work/current/_template.md", "W-00000000")
        self.write(".runtime/driver/logs/W-00000009.md", "W-00000009")
        self.write("decisions/pending/DE-00000004.md", "DE-00000004")

        self.assertEqual({3}, stage_record_ids.local_record_numbers(self.stage, "W"))
        self.assertEqual({4}, stage_record_ids.local_record_numbers(self.stage, "DE"))

    def test_counts_records_that_exist_only_on_other_local_and_remote_branches(self):
        self.git("init", "-q", "-b", "main")
        self.write("work/current/W-00000002/_story.md", "W-00000002")
        self.commit_all("base")
        self.git("checkout", "-q", "-b", "side")
        self.write("work/current/W-00000007/_story.md", "W-00000007")
        self.write("decisions/pending/DE-00000005.md", "DE-00000005")
        self.commit_all("side work")
        self.git("checkout", "-q", "-b", "remote-work", "main")
        self.write("state/observations/O-00000011.md", "O-00000011")
        self.commit_all("remote work")
        self.git("update-ref", "refs/remotes/origin/parallel", "HEAD")
        self.git("checkout", "-q", "main")
        self.git("branch", "-q", "-D", "remote-work")

        branch_w = stage_record_ids.branch_record_numbers(self.root, "W")

        self.assertEqual({2}, stage_record_ids.local_record_numbers(self.stage, "W"))
        self.assertEqual({"side"}, branch_w[7])
        self.assertEqual("W-00000008", stage_record_ids.next_record_id(self.root, "W"))
        self.assertEqual("DE-00000006", stage_record_ids.next_record_id(self.root, "DE"))
        self.assertEqual(
            {"origin/parallel"}, stage_record_ids.branch_record_numbers(self.root, "O")[11]
        )
        self.assertEqual("O-00000012", stage_record_ids.next_record_id(self.root, "O"))

    def test_outside_git_only_the_checkout_counts(self):
        self.write("work/current/W-00000004/_story.md", "W-00000004")

        self.assertEqual({}, stage_record_ids.branch_record_numbers(self.root, "W"))
        self.assertEqual("W-00000005", stage_record_ids.next_record_id(self.root, "W"))
        self.assertEqual("DE-00000001", stage_record_ids.next_record_id(self.root, "DE"))

    def test_cli_prints_the_next_id_and_rejects_bad_prefixes(self):
        self.write("decisions/pending/DE-00000009.md", "DE-00000009")

        ok = subprocess.run(
            [sys.executable, str(CLI), "--project-root", str(self.root), "DE"],
            capture_output=True,
            text=True,
        )
        bad = subprocess.run(
            [sys.executable, str(CLI), "--project-root", str(self.root), "de-1"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(("DE-00000010\n", 0), (ok.stdout, ok.returncode))
        self.assertEqual(2, bad.returncode)


if __name__ == "__main__":
    unittest.main()
