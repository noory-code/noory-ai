"""Blocks of record ids a PO session holds on a card for a PM session (DE-00000094).

Every remote here is a bare repository in a temporary directory; no test reaches
a network remote.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
RECORD_IDS_CLI = SCRIPTS / "stage_record_ids.py"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_test_config import isolate_git_config  # noqa: E402

isolate_git_config()

import stage_id_blocks  # noqa: E402
import stage_record_ids  # noqa: E402

CARD = ".stage/work/current/W-00000002/_story.md"


def git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.stdout


def ids_cli(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RECORD_IDS_CLI), "--project-root", str(root), "--no-reserve", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class IdBlockTest(unittest.TestCase):
    """A bare remote seeded with one started card and one decision, and two clones."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.remote = self.tmp / "remote.git"
        git(self.tmp, "init", "-q", "--bare", str(self.remote))
        seed = self.tmp / "seed"
        seed.mkdir()
        git(seed, "init", "-q", "-b", "main")
        write(seed / ".stage/settings.json", '{"schema_version": 5}\n')
        write(seed / CARD, "---\nid: W-00000002\nstatus: active\n---\n\n# W-00000002 Seed\n")
        write(
            seed / ".stage/decisions/pending/DE-00000003.md",
            "---\nid: DE-00000003\n---\n\n# DE-00000003 Seed\n",
        )
        git(seed, "add", "-A")
        git(seed, "commit", "-q", "-m", "seed")
        git(seed, "push", "-q", str(self.remote), "main:refs/heads/main")
        self.main = self.tmp / "main-session"
        self.other = self.tmp / "other-session"
        for clone in (self.main, self.other):
            git(self.tmp, "clone", "-q", "-b", "main", str(self.remote), str(clone))

    def test_reserving_writes_the_block_on_the_card_and_later_ids_skip_it(self) -> None:
        proc = ids_cli(self.main, "--reserve-for", "W-00000002", "--count", "2", "DE")

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual("DE-00000004 DE-00000005", proc.stdout.strip())
        card = (self.main / CARD).read_text(encoding="utf-8")
        self.assertIn("reserved_ids: DE-00000004, DE-00000005\n---\n", card)
        self.assertEqual("DE-00000006", ids_cli(self.main, "DE").stdout.strip())

    def test_another_clone_counts_the_pushed_block_after_fetch(self) -> None:
        ids_cli(self.main, "--reserve-for", "W-00000002", "--count", "2", "DE")
        git(self.main, "commit", "-q", "-am", "reserve ids for the sub-session")
        git(self.main, "push", "-q", "origin", "HEAD:refs/heads/main-session")

        self.assertEqual("DE-00000004", ids_cli(self.other, "DE").stdout.strip())
        git(self.other, "fetch", "-q", "origin")
        self.assertEqual("DE-00000006", ids_cli(self.other, "DE").stdout.strip())

    def test_the_sub_session_takes_unused_ids_from_the_block_in_order(self) -> None:
        ids_cli(self.main, "--reserve-for", "W-00000002", "--count", "2", "DE")

        self.assertEqual("DE-00000004", ids_cli(self.main, "--from-card", "W-00000002", "DE").stdout.strip())
        write(
            self.main / ".stage/decisions/pending/DE-00000004.md",
            "---\nid: DE-00000004\n---\n\n# DE-00000004 Used\n",
        )
        self.assertEqual("DE-00000005", ids_cli(self.main, "--from-card", "W-00000002", "DE").stdout.strip())
        write(
            self.main / ".stage/decisions/pending/DE-00000005.md",
            "---\nid: DE-00000005\n---\n\n# DE-00000005 Used\n",
        )
        exhausted = ids_cli(self.main, "--from-card", "W-00000002", "DE")
        self.assertEqual(1, exhausted.returncode)
        self.assertIn("ask the PO session for more", exhausted.stderr)

    def test_a_second_reservation_adds_to_the_block(self) -> None:
        ids_cli(self.main, "--reserve-for", "W-00000002", "DE")
        proc = ids_cli(self.main, "--reserve-for", "W-00000002", "DE")

        self.assertEqual("DE-00000005", proc.stdout.strip())
        card = (self.main / CARD).read_text(encoding="utf-8")
        self.assertIn("reserved_ids: DE-00000004, DE-00000005\n", card)
        self.assertEqual(1, card.count("reserved_ids:"))

    def test_other_prefixes_ignore_the_block(self) -> None:
        ids_cli(self.main, "--reserve-for", "W-00000002", "--count", "2", "DE")

        self.assertEqual("O-00000001", ids_cli(self.main, "O").stdout.strip())

    def test_a_card_that_is_not_started_cannot_hold_a_block(self) -> None:
        proc = ids_cli(self.main, "--reserve-for", "W-00000099", "DE")

        self.assertEqual(1, proc.returncode)
        self.assertIn("W-00000099: no started card", proc.stderr)

    def test_reserved_numbers_reads_only_the_reserved_ids_line(self) -> None:
        text = "---\nid: W-1\nreserved_ids: DE-00000007, O-00000002\n---\nSee DE-00000009.\n"

        self.assertEqual({7}, stage_record_ids.reserved_numbers(text, "DE"))
        self.assertEqual({2}, stage_record_ids.reserved_numbers(text, "O"))
        self.assertIsNotNone(stage_id_blocks.current_card_path(self.main / ".stage", "W-00000002"))


if __name__ == "__main__":
    unittest.main()
