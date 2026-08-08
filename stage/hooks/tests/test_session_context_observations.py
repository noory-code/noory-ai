"""Session-start view of open observations, and the truncation marker."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


STAGE_ROOT = Path(__file__).resolve().parents[2]
HOOK_ROOT = STAGE_ROOT / "hooks"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))

import stage_context  # noqa: E402


V3_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "project-stage"
V4_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "v4" / "project-stage"

# Twice the count this project carried when the view was built (17), which is
# the scale the card asks the test to hold at.
DOUBLED_OBSERVATION_COUNT = 34


class OpenObservationViewTest(unittest.TestCase):
    def make_fixture(self, template_root: Path):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        shutil.copytree(template_root, root / ".stage")
        return tmp, root

    def write_observations(
        self, directory: Path, count: int, opened: str = "2026-08-01"
    ) -> list[str]:
        """`count` records whose titles are long enough to bite a length cap."""
        ids: list[str] = []
        for index in range(1, count + 1):
            record_id = f"O-{index:08d}"
            ids.append(record_id)
            (directory / f"{record_id}.md").write_text(
                f"---\nid: {record_id}\nopened: {opened}\n"
                f"title: Observation {index} " + "detail " * 20 + "\n"
                "work_items:\n---\n"
                f"# {record_id} Observation {index}\n\n## Observation\n\n"
                + ("Body text that must never reach the session payload. " * 40)
                + "\n",
                encoding="utf-8",
            )
        return ids

    def test_v4_session_lists_every_open_observation_when_the_count_doubles(self):
        tmp, root = self.make_fixture(V4_TEMPLATE_ROOT)
        with tmp:
            stage_root = root / ".stage"
            ids = self.write_observations(
                stage_root / "state" / "observations", DOUBLED_OBSERVATION_COUNT
            )
            context = stage_context.session_context(root)

        self.assertIn("### Open observations", context)
        # Every ID, not a count: a count passes while the tail is dropped, which
        # is the exact defect this view exists to end.
        missing = [record_id for record_id in ids if record_id not in context]
        self.assertEqual(missing, [], f"observations dropped from session start: {missing}")

    def test_v4_session_never_carries_observation_bodies(self):
        tmp, root = self.make_fixture(V4_TEMPLATE_ROOT)
        with tmp:
            stage_root = root / ".stage"
            self.write_observations(
                stage_root / "state" / "observations", DOUBLED_OBSERVATION_COUNT
            )
            context = stage_context.session_context(root)

        self.assertNotIn("Body text that must never reach the session payload", context)
        section = context.split("### Open observations\n", 1)[1].split("\n\n", 1)[0]
        lines = section.splitlines()
        self.assertEqual(len(lines), DOUBLED_OBSERVATION_COUNT)
        for line in lines:
            self.assertLessEqual(len(line), stage_context.SESSION_CONTEXT_LINE_LIMIT)

    def test_legacy_session_lists_every_open_observation(self):
        tmp, root = self.make_fixture(V3_TEMPLATE_ROOT)
        with tmp:
            stage_root = root / ".stage"
            ids = self.write_observations(
                stage_root / "present" / "state" / "observations",
                DOUBLED_OBSERVATION_COUNT,
            )
            context = stage_context.session_context(root)

        self.assertIn("### Open observations", context)
        missing = [record_id for record_id in ids if record_id not in context]
        self.assertEqual(missing, [], f"observations dropped from session start: {missing}")

    def test_each_line_states_how_long_the_observation_has_been_open(self):
        tmp, root = self.make_fixture(V4_TEMPLATE_ROOT)
        with tmp:
            stage_root = root / ".stage"
            directory = stage_root / "state" / "observations"
            (directory / "O-00000002.md").write_text(
                "---\nid: O-00000002\nopened: 2026-07-27\ntitle: Twelve days old\n"
                "work_items:\n---\n# O-00000002 Twelve days old\n",
                encoding="utf-8",
            )
            (directory / "O-00000043.md").write_text(
                "---\nid: O-00000043\nopened: 2026-08-08\ntitle: Opened today\n"
                "work_items:\n---\n# O-00000043 Opened today\n",
                encoding="utf-8",
            )
            lines = stage_context.open_observation_lines(
                stage_root, today=date(2026, 8, 8)
            )

        self.assertEqual(
            lines,
            [
                "- O-00000043 Opened today (open 0d)",
                "- O-00000002 Twelve days old (open 12d)",
            ],
        )

    def test_a_record_without_a_parsable_opened_date_still_appears(self):
        tmp, root = self.make_fixture(V4_TEMPLATE_ROOT)
        with tmp:
            stage_root = root / ".stage"
            directory = stage_root / "state" / "observations"
            (directory / "O-00000001.md").write_text(
                "---\nid: O-00000001\ntitle: No opened field\nwork_items:\n---\n",
                encoding="utf-8",
            )
            (directory / "O-00000002.md").write_text(
                "---\nid: O-00000002\nopened: YYYY-MM-DD\ntitle: Placeholder date\n"
                "work_items:\n---\n",
                encoding="utf-8",
            )
            lines = stage_context.open_observation_lines(
                stage_root, today=date(2026, 8, 8)
            )

        self.assertEqual(
            lines,
            [
                "- O-00000002 Placeholder date (open ?)",
                "- O-00000001 No opened field (open ?)",
            ],
        )

    def test_the_observation_index_file_is_no_longer_dumped_through_the_cap(self):
        """The index dump is what dropped the newest observations; the derived
        list replaces it rather than duplicating it."""
        tmp, root = self.make_fixture(V4_TEMPLATE_ROOT)
        with tmp:
            stage_root = root / ".stage"
            self.write_observations(stage_root / "state" / "observations", 3)
            (stage_root / "state" / "current.md").write_text(
                "# Current State\n\n## Current observations\n\n"
                "- [O-00000001](observations/O-00000001.md) — index prose\n",
                encoding="utf-8",
            )
            context = stage_context.session_context(root)

        self.assertNotIn("### Current state", context)
        self.assertNotIn("index prose", context)


class TruncationMarkerTest(unittest.TestCase):
    def test_truncation_states_how_many_lines_the_session_is_not_seeing(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "work" / "active.md"
            path.parent.mkdir(parents=True)
            path.write_text("\n".join(f"- line {n} " + "x" * 60 for n in range(60)))
            body = stage_context.read_if_exists(path)

        self.assertIn("more lines truncated", body)
        self.assertIn("`work/active.md`", body)
        marker = body.splitlines()[-1]
        dropped = int(marker.split("…", 1)[1].split(" ", 1)[0])
        self.assertEqual(dropped, 60 - (len(body.splitlines()) - 1))

    def test_a_file_under_the_cap_carries_no_marker(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "review.md"
            path.write_text("- one line\n")
            body = stage_context.read_if_exists(path)

        self.assertEqual(body, "- one line")


if __name__ == "__main__":
    unittest.main()
