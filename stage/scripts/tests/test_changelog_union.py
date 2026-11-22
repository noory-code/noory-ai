"""Pin what git does to a changelog line when a release and a card meet in one merge.

The root `.gitattributes` gives every `CHANGELOG.md` `merge=union` (DE-00000091). A release
(`release_plugin.py`) titles the queued `## Unreleased` body with a version and opens a new empty
`## Unreleased` above it; the queued lines do not move. A card branch that forked before the
release adds a line to the old `## Unreleased` body. Git places that line by its neighbours, and
its neighbours now sit under the version heading, so the line lands in the released section and
the merge reports nothing (W-00000384).

A line added first under `## Unreleased` (this repository's convention) and the release's new
heading are inserted at the same place, so the two sides conflict and union resolves the conflict
by writing the side being merged into first. The result therefore depends on the direction:

- merging the card into the released branch puts the line under the released heading;
- merging the released branch into the card branch, as `.gitattributes` asks before a pull
  request is merged, keeps the line under `## Unreleased` but drops the blank line before the
  released heading.

A line added after the last queued line does not conflict at all and lands in the released section
in both directions, with or without union.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_test_config import isolate_git_config  # noqa: E402

isolate_git_config()

import release_plugin  # noqa: E402

RELEASE_DATE = date(2026, 2, 1)
QUEUED = "- Queued before the release.\n"
CARD = "- Added by a card after its branch forked.\n"
BASE_CHANGELOG = (
    "# Changelog\n\n"
    "## Unreleased\n\n"
    f"{QUEUED}"
    "\n## 0.1.0 — 2026-01-01\n\n"
    "- Previous release.\n"
)
# A top line merged into the released branch: it sits under the released heading and the new
# `## Unreleased` stays empty.
MISPLACED_TOP = (
    "# Changelog\n\n"
    "## Unreleased\n\n"
    "## 0.2.0 — 2026-02-01\n\n"
    f"{CARD}"
    f"{QUEUED}"
    "\n## 0.1.0 — 2026-01-01\n\n"
    "- Previous release.\n"
)
# A top line when the released branch is merged into the card branch: the line stays queued, but
# no blank line separates it from the released heading.
KEPT_TOP = (
    "# Changelog\n\n"
    "## Unreleased\n\n"
    f"{CARD}"
    "## 0.2.0 — 2026-02-01\n\n"
    f"{QUEUED}"
    "\n## 0.1.0 — 2026-01-01\n\n"
    "- Previous release.\n"
)
# A bottom line in any direction: it sits under the released heading.
MISPLACED_BOTTOM = (
    "# Changelog\n\n"
    "## Unreleased\n\n"
    "## 0.2.0 — 2026-02-01\n\n"
    f"{QUEUED}"
    f"{CARD}"
    "\n## 0.1.0 — 2026-01-01\n\n"
    "- Previous release.\n"
)
# What the merge should have produced, and what the card's handling restores by hand.
INTENDED = (
    "# Changelog\n\n"
    "## Unreleased\n\n"
    f"{CARD}"
    "\n## 0.2.0 — 2026-02-01\n\n"
    f"{QUEUED}"
    "\n## 0.1.0 — 2026-01-01\n\n"
    "- Previous release.\n"
)


def git(repository: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repository,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def section(changelog: str, heading: str) -> str:
    """Return the body under one `## ` heading, up to the next `## ` heading."""

    lines = changelog.splitlines(keepends=True)
    start = next(index for index, line in enumerate(lines) if line.rstrip("\n") == heading)
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return "".join(lines[start + 1 : end])


class ChangelogUnionMergeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.repositories = 0

    def make_base(self, *, union: bool) -> None:
        # Each call starts a fresh repository so subtests share nothing.
        self.repositories += 1
        self.repository = Path(self.temporary_directory.name) / f"repository-{self.repositories}"
        self.repository.mkdir()
        self.changelog = self.repository / "stage" / "CHANGELOG.md"
        git(self.repository, "init", "-q", "-b", "main")
        # Merges in this test must not depend on the platform's line-ending conversion.
        git(self.repository, "config", "core.autocrlf", "false")
        plugin = self.repository / "stage"
        for manifest in (".claude-plugin", ".codex-plugin"):
            (plugin / manifest).mkdir(parents=True)
            (plugin / manifest / "plugin.json").write_text(
                '{\n  "name": "stage",\n  "version": "0.1.0"\n}\n', encoding="utf-8"
            )
        self.changelog.write_bytes(BASE_CHANGELOG.encode("utf-8"))
        if union:
            # The same rule the repository root carries.
            (self.repository / ".gitattributes").write_text(
                "CHANGELOG.md merge=union\n", encoding="utf-8"
            )
        git(self.repository, "add", "-A")
        git(self.repository, "commit", "-q", "-m", "base")

    def release_on_main(self) -> str:
        git(self.repository, "checkout", "-q", "main")
        released = release_plugin.release_plugin(
            self.repository, "stage", "minor", release_date=RELEASE_DATE
        )
        self.assertEqual("0.2.0", released)
        git(self.repository, "commit", "-q", "-am", "release stage 0.2.0")
        return git(self.repository, "rev-parse", "HEAD").stdout.strip()

    def add_card_line(self, *, at_top: bool) -> None:
        git(self.repository, "checkout", "-q", "-b", "card", "main")
        text = self.changelog.read_bytes().decode("utf-8")
        if at_top:
            # The repository's convention: a new entry goes first under `## Unreleased`.
            text = text.replace("## Unreleased\n\n", f"## Unreleased\n\n{CARD}", 1)
        else:
            text = text.replace(QUEUED, f"{QUEUED}{CARD}", 1)
        self.changelog.write_bytes(text.encode("utf-8"))
        git(self.repository, "commit", "-q", "-am", "card line")

    def merged_text(self) -> str:
        return self.changelog.read_bytes().decode("utf-8")

    def test_union_places_a_top_line_by_merge_direction(self) -> None:
        for into, other, expected in (
            ("main", "card", MISPLACED_TOP),
            ("card", "main", KEPT_TOP),
        ):
            with self.subTest(merge_into=into):
                self.make_base(union=True)
                self.add_card_line(at_top=True)
                self.release_on_main()
                git(self.repository, "checkout", "-q", into)
                merge = git(self.repository, "merge", "--no-edit", other, check=False)
                self.assertEqual(0, merge.returncode, merge.stdout + merge.stderr)
                self.assertEqual(expected, self.merged_text())

    def test_without_union_a_top_line_conflicts(self) -> None:
        # GitHub's merge button ignores `merge=union`, so this is what it sees.
        self.make_base(union=False)
        self.add_card_line(at_top=True)
        self.release_on_main()
        git(self.repository, "checkout", "-q", "card")
        merge = git(self.repository, "merge", "--no-edit", "main", check=False)
        self.assertNotEqual(0, merge.returncode)
        self.assertIn("CONFLICT (content): Merge conflict in stage/CHANGELOG.md", merge.stdout)

    def test_a_bottom_line_lands_in_the_released_section_in_every_merge(self) -> None:
        # The release edits only the heading line; a line added after the last queued line is a
        # separate hunk, so plain three-way merging places it too and nothing conflicts.
        for union in (True, False):
            for into, other in (("main", "card"), ("card", "main")):
                with self.subTest(union=union, merge_into=into):
                    self.make_base(union=union)
                    self.add_card_line(at_top=False)
                    self.release_on_main()
                    git(self.repository, "checkout", "-q", into)
                    merge = git(self.repository, "merge", "--no-edit", other, check=False)
                    self.assertEqual(0, merge.returncode, merge.stdout + merge.stderr)
                    self.assertEqual(MISPLACED_BOTTOM, self.merged_text())

    def test_comparing_the_released_section_with_the_release_commit_finds_the_line(self) -> None:
        # The card's handling: the released section must equal the one the release commit wrote.
        self.make_base(union=True)
        self.add_card_line(at_top=True)
        release_commit = self.release_on_main()
        git(self.repository, "merge", "--no-edit", "card")

        at_release = git(self.repository, "show", f"{release_commit}:stage/CHANGELOG.md").stdout
        heading = "## 0.2.0 — 2026-02-01"
        released_lines = section(at_release, heading).splitlines(keepends=True)
        merged_lines = section(self.merged_text(), heading).splitlines(keepends=True)
        extra = [line for line in merged_lines if line not in released_lines]
        self.assertEqual([CARD], extra)

        # Moving the extra lines back under `## Unreleased` gives the intended changelog.
        repaired = self.merged_text().replace(CARD, "", 1)
        repaired = repaired.replace(
            f"## Unreleased\n\n{heading}", f"## Unreleased\n\n{CARD}\n{heading}", 1
        )
        self.assertEqual(INTENDED, repaired)


if __name__ == "__main__":
    unittest.main()
