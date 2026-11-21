"""Reserving record ids on the remote (DE-00000092).

Every remote here is a bare repository in a temporary directory; no test
reaches a network remote.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
STAGE_ROOT = SCRIPTS.parent
RECORD_IDS_CLI = SCRIPTS / "stage_record_ids.py"
REGISTER_CLI = STAGE_ROOT / "skills" / "stage-work" / "register_work.py"
ROADMAP_CLI = STAGE_ROOT / "skills" / "stage-roadmap" / "manage_roadmap.py"
sys.path.insert(0, str(SCRIPTS))
import stage_record_ids  # noqa: E402

ACTIVE = (
    "# Active Work\n\n"
    "| Work | Kind | Venue | Purpose | Status | Owner | Item |\n"
    "|---|---|---|---|---|---|---|\n"
)


def git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-c", "user.name=Stage Test", "-c", "user.email=stage@example.invalid", *args],
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return proc.stdout


def load_roadmap_module():
    spec = importlib.util.spec_from_file_location("manage_roadmap_under_test", ROADMAP_CLI)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReservationFixture(unittest.TestCase):
    """A bare remote seeded with one card and one decision, and two clones of it
    that never fetch each other's work."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.remote = self.tmp / "remote.git"
        git(self.tmp, "init", "-q", "--bare", str(self.remote))
        seed = self.tmp / "seed"
        seed.mkdir()
        git(seed, "init", "-q", "-b", "main")
        (seed / ".stage/work/current/W-00000002").mkdir(parents=True)
        (seed / ".stage/work/planned").mkdir(parents=True)
        (seed / ".stage/work/planned/.gitkeep").write_text("", encoding="utf-8")
        (seed / ".stage/official/work/archive/items").mkdir(parents=True)
        (seed / ".stage/decisions/pending").mkdir(parents=True)
        (seed / ".stage/work/active.md").write_text(ACTIVE, encoding="utf-8")
        (seed / ".stage/settings.json").write_text('{"schema_version": 5}\n', encoding="utf-8")
        (seed / ".stage/work/current/W-00000002/_story.md").write_text(
            "---\nid: W-00000002\n---\n\n# W-00000002 Seed\n", encoding="utf-8"
        )
        (seed / ".stage/decisions/pending/DE-00000003.md").write_text(
            "---\nid: DE-00000003\n---\n\n# DE-00000003 Seed\n", encoding="utf-8"
        )
        git(seed, "add", "-A")
        git(seed, "commit", "-q", "-m", "seed")
        git(seed, "push", "-q", str(self.remote), "main:refs/heads/main")
        git(self.tmp, "--git-dir", str(self.remote), "symbolic-ref", "HEAD", "refs/heads/main")
        self.a = self.clone("a")
        self.b = self.clone("b")

    def clone(self, name: str) -> Path:
        git(self.tmp, "clone", "-q", str(self.remote), name)
        return self.tmp / name

    def reserved_refs(self) -> list[str]:
        text = git(self.tmp, "--git-dir", str(self.remote), "for-each-ref",
                   "--format=%(refname)", "refs/stage-ids")
        return text.split()

    def record_ids(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(RECORD_IDS_CLI), "--project-root", str(root), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def register(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(REGISTER_CLI), "--project-root", str(root),
             "--title", "T", "--kind", "design", "--scope", "src", "--scale", "story",
             "--purpose", "Deliver the outcome", "--success-criterion", "It is observable",
             *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )


class RecordIdsReservationTest(ReservationFixture):
    def test_two_unfetched_clones_get_different_ids_in_turn(self):
        first = self.record_ids(self.a, "DE")
        second = self.record_ids(self.b, "DE")

        self.assertEqual(("DE-00000004\n", ""), (first.stdout, first.stderr))
        self.assertEqual(("DE-00000005\n", ""), (second.stdout, second.stderr))
        self.assertEqual(
            ["refs/stage-ids/DE-00000004", "refs/stage-ids/DE-00000005"], self.reserved_refs()
        )

    def test_a_reservation_lost_after_the_remote_was_read_moves_to_the_next_id(self):
        reserver = stage_record_ids.IdReserver(self.b)
        self.assertEqual(set(), reserver.remote_ids())  # snapshot taken before A reserves
        self.assertEqual("DE-00000004", self.record_ids(self.a, "DE").stdout.strip())

        chosen = stage_record_ids.next_record_id(self.b, "DE", reserver)

        self.assertEqual("DE-00000005", chosen)
        self.assertEqual({"DE-00000005"}, reserver.reserved)
        self.assertEqual("", reserver.unreserved_note(chosen))

    def test_same_second_reservations_of_one_id_do_not_both_succeed(self):
        first = stage_record_ids.IdReserver(self.a)
        second = stage_record_ids.IdReserver(self.b)
        first.remote_ids()
        second.remote_ids()

        self.assertTrue(first.claim("DE-00000004"))
        self.assertFalse(second.claim("DE-00000004"))
        self.assertTrue(second.available)

    def test_reservation_pushes_no_branch_work(self):
        (self.a / "unpushed.txt").write_text("local only\n", encoding="utf-8")
        git(self.a, "add", "-A")
        git(self.a, "commit", "-q", "-m", "local only")
        local_head = git(self.a, "rev-parse", "HEAD").strip()

        self.assertEqual(0, self.record_ids(self.a, "DE").returncode)

        missing = subprocess.run(
            ["git", "--git-dir", str(self.remote), "cat-file", "-e", local_head],
            capture_output=True,
        )
        self.assertNotEqual(0, missing.returncode)

    def test_no_reserve_touches_no_remote(self):
        proc = self.record_ids(self.a, "--no-reserve", "DE")

        self.assertEqual(("DE-00000004\n", ""), (proc.stdout, proc.stderr))
        self.assertEqual([], self.reserved_refs())

    def test_unreachable_remote_falls_back_with_one_line(self):
        git(self.a, "remote", "set-url", "origin", str(self.tmp / "missing.git"))

        proc = self.record_ids(self.a, "DE")

        self.assertEqual(0, proc.returncode)
        self.assertEqual("DE-00000004\n", proc.stdout)
        self.assertEqual(1, len(proc.stderr.splitlines()), proc.stderr)
        self.assertIn("DE-00000004: not reserved on the remote", proc.stderr)

    def test_refused_push_falls_back_with_one_line(self):
        hook = self.remote / "hooks" / "pre-receive"
        hook.write_text(f"#!{sys.executable}\nimport sys\nsys.exit(1)\n", encoding="utf-8")
        hook.chmod(0o755)
        if sys.platform == "win32":
            self.skipTest("bare-repository hooks need a POSIX shebang")

        proc = self.record_ids(self.a, "DE")

        self.assertEqual("DE-00000004\n", proc.stdout)
        self.assertIn("refused the push", proc.stderr)
        self.assertEqual([], self.reserved_refs())

    def test_project_without_remote_gets_the_same_id_as_before(self):
        git(self.a, "remote", "remove", "origin")

        proc = self.record_ids(self.a, "DE")

        self.assertEqual("DE-00000004\n", proc.stdout)
        self.assertEqual(
            stage_record_ids.next_record_id(self.a, "DE"), proc.stdout.strip()
        )
        self.assertIn("not reserved on the remote (no git remote)", proc.stderr)

    def test_default_remote_follows_the_branch_upstream(self):
        git(self.a, "remote", "add", "other", str(self.remote))
        git(self.a, "config", "branch.main.remote", "other")

        self.assertEqual("other", stage_record_ids.default_remote(self.a))


class RegisterWorkReservationTest(ReservationFixture):
    def created_ids(self, root: Path) -> list[str]:
        return sorted(path.name for path in (root / ".stage/work/current").glob("W-*"))

    def test_two_unfetched_clones_register_different_cards(self):
        first = self.register(self.a)
        second = self.register(self.b)

        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(0, second.returncode, second.stderr)
        self.assertNotIn("not reserved", first.stderr + second.stderr)
        self.assertEqual(["W-00000002", "W-00000003"], self.created_ids(self.a))
        self.assertEqual(["W-00000002", "W-00000004"], self.created_ids(self.b))
        self.assertEqual(
            ["refs/stage-ids/W-00000003", "refs/stage-ids/W-00000004"], self.reserved_refs()
        )

    def test_planned_cards_reserve_too(self):
        first = self.register(self.a, "--backlog")
        second = self.register(self.b, "--backlog")

        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(0, second.returncode, second.stderr)
        self.assertIn("W-00000003", first.stdout)
        self.assertIn("W-00000004", second.stdout)

    def test_unreachable_remote_still_registers_and_says_so(self):
        git(self.a, "remote", "set-url", "origin", str(self.tmp / "missing.git"))

        proc = self.register(self.a)

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(["W-00000002", "W-00000003"], self.created_ids(self.a))
        self.assertIn("W-00000003: not reserved on the remote", proc.stderr)


class RoadmapReservationTest(ReservationFixture):
    def test_roadmap_ids_skip_ids_reserved_by_another_clone(self):
        roadmap = load_roadmap_module()
        themes_a = self.a / "themes"
        themes_b = self.b / "themes"
        themes_a.mkdir()
        themes_b.mkdir()

        first = roadmap._create_atomic(themes_a, "TH", [], lambda record_id: record_id, self.a)
        second = roadmap._create_atomic(themes_b, "TH", [], lambda record_id: record_id, self.b)

        self.assertEqual("TH-00000001", first)
        self.assertEqual("TH-00000002", second)
        self.assertEqual(
            ["refs/stage-ids/TH-00000001", "refs/stage-ids/TH-00000002"], self.reserved_refs()
        )


if __name__ == "__main__":
    unittest.main()
