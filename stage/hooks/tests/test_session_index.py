"""The record-derived index a session starts with, and its size limit (DE-00000100)."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path


STAGE_ROOT = Path(__file__).resolve().parents[2]
HOOK_ROOT = STAGE_ROOT / "hooks"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))

import stage_context  # noqa: E402
import stage_memory_index  # noqa: E402
from stage_memory_index import Block, fit_blocks  # noqa: E402


V4_TEMPLATE_ROOT = STAGE_ROOT / "templates" / "v4" / "project-stage"
LIMIT = stage_memory_index.SESSION_CONTEXT_CHAR_LIMIT
BODY = "Decision body text that must never reach the session."


def card(item_id: str, title: str) -> str:
    return (
        f"---\nid: {item_id}\ntitle: {title}\nkind: development\nvenue: claude\n"
        "status: active\nverification: pending\nretrospective: pending\n"
        "retrospective_ref:\npromotion: pending\nreview: not_required\nscope: src\n---\n"
        f"# {item_id} {title}\n"
    )


class SessionIndexFixture(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.stage_root = self.root / ".stage"
        shutil.copytree(V4_TEMPLATE_ROOT, self.stage_root)

    def write_decisions(self, count: int, folder: str = "official/decisions/records") -> None:
        directory = self.stage_root / folder
        directory.mkdir(parents=True, exist_ok=True)
        for number in range(1, count + 1):
            record_id = f"DE-{number:08d}"
            (directory / f"{record_id}.md").write_text(
                f"---\nid: {record_id}\nwork_item: W-00000001\nstatus: decided\n---\n\n"
                f"# {record_id} Decision title number {number} with a topic\n\n"
                f"## Question\n\n{BODY}\n",
                encoding="utf-8",
            )

    def write_active_card(self) -> None:
        folder = self.stage_root / "work" / "current" / "W-00000900"
        folder.mkdir(parents=True)
        (folder / "_story.md").write_text(
            card("W-00000900", "The card in progress"), encoding="utf-8"
        )

    def write_retrospectives(self, count: int, candidate: str = "") -> None:
        directory = self.stage_root / "official" / "work" / "archive" / "retrospectives"
        directory.mkdir(parents=True, exist_ok=True)
        for number in range(1, count + 1):
            (directory / f"R-{number:08d}.md").write_text(
                f"# R-{number:08d}\n\n## Rule candidate\n\n{candidate}\n\n## Other\n\ntext\n",
                encoding="utf-8",
            )


class SessionContextLimitTest(SessionIndexFixture):
    def test_a_few_decisions_are_all_listed_newest_first_without_bodies(self):
        self.write_decisions(3)
        self.write_decisions(1, folder="decisions/pending")  # same id: listed once

        context = stage_context.session_context(self.root)

        listed = [line for line in context.splitlines() if line.startswith("- DE-")]
        self.assertEqual(
            [
                "- DE-00000003 Decision title number 3 with a topic",
                "- DE-00000002 Decision title number 2 with a topic",
                "- DE-00000001 Decision title number 1 with a topic",
            ],
            listed,
        )
        self.assertNotIn(BODY, context)
        self.assertNotIn("not shown", context)
        self.assertLessEqual(len(context), LIMIT)

    def test_an_undecided_decision_says_its_status(self):
        directory = self.stage_root / "decisions" / "pending"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "DE-00000007.md").write_text(
            "---\nid: DE-00000007\nstatus: proposed\n---\n\n# DE-00000007 Open choice\n",
            encoding="utf-8",
        )

        self.assertEqual(
            ["- DE-00000007 Open choice (proposed)"],
            stage_memory_index.decision_title_lines(self.stage_root),
        )

    def test_over_the_limit_the_oldest_decisions_go_and_current_work_stays(self):
        self.write_decisions(400)
        self.write_active_card()

        context = stage_context.session_context(self.root)

        self.assertLessEqual(len(context), LIMIT)
        self.assertIn("W-00000900 The card in progress", context)
        self.assertIn("### Active work", context)
        listed = [line.split()[1] for line in context.splitlines() if line.startswith("- DE-")]
        self.assertTrue(listed)
        # What stays is the newest run, with no gap.
        self.assertEqual([f"DE-{n:08d}" for n in range(400, 400 - len(listed), -1)], listed)
        self.assertIn(
            f"- …{400 - len(listed)} older decisions not shown — read "
            "`.stage/decisions/pending/` and `.stage/official/decisions/records/`",
            context,
        )
        # The limit is used, not undershot by more than one line.
        self.assertGreater(len(context), LIMIT - 200)

    def test_the_limit_holds_when_what_is_never_shortened_is_already_too_long(self):
        directory = self.stage_root / "state" / "observations"
        directory.mkdir(parents=True, exist_ok=True)
        for number in range(1, 121):
            (directory / f"O-{number:08d}.md").write_text(
                f"---\nid: O-{number:08d}\nopened: 2026-08-01\n"
                "title: " + "an observation with a long title " * 8 + "\n---\n",
                encoding="utf-8",
            )
        self.write_decisions(50)

        context = stage_context.session_context(self.root)

        self.assertLessEqual(len(context), LIMIT)
        self.assertIn("…cut at", context.splitlines()[-1])

    def test_a_project_without_stage_stays_within_the_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "CLAUDE.md").write_text("# Rules\n", encoding="utf-8")

            context = stage_context.session_context(root)

        self.assertIn("- `CLAUDE.md`", context)
        self.assertLessEqual(len(context), LIMIT)

    def test_the_index_alone_is_what_a_brief_embeds(self):
        self.write_decisions(3)
        self.write_active_card()

        index = stage_context.session_index(self.root, 2_000)
        context = stage_context.session_context(self.root)

        self.assertLessEqual(len(index), 2_000)
        self.assertNotIn("## Stage context", index)
        self.assertIn("- DE-00000003 Decision title number 3 with a topic", index)
        self.assertTrue(context.endswith(stage_context.session_index(self.root)))


class RuleCandidateIndexTest(SessionIndexFixture):
    def test_without_a_list_the_index_counts_retrospectives_that_state_a_candidate(self):
        self.write_retrospectives(3, candidate="- **Do the thing.** Evidence.")
        directory = self.stage_root / "official" / "work" / "archive" / "retrospectives"
        for number, said in enumerate(("없음.", "- 없다.", "", "<!-- hint -->"), start=10):
            (directory / f"R-{number:08d}.md").write_text(
                f"# R\n\n## Rule candidate\n\n{said}\n", encoding="utf-8"
            )

        candidates, status = stage_memory_index.rule_candidate_lines(self.stage_root)

        self.assertEqual([], candidates)
        self.assertEqual(1, len(status))
        self.assertIn("No consolidated list yet (`.stage/state/rule-candidates.md`)", status[0])
        self.assertIn("3 retrospectives state a candidate", status[0])

    def test_no_candidates_and_no_list_adds_nothing(self):
        self.write_retrospectives(2)

        self.assertEqual(([], []), stage_memory_index.rule_candidate_lines(self.stage_root))
        self.assertNotIn("### Rule candidates", stage_context.session_context(self.root))

    def test_the_list_gives_one_line_per_candidate_and_says_when_consolidation_is_due(self):
        self.write_retrospectives(25, candidate="- Something.")
        (self.stage_root / "state" / "rule-candidates.md").write_text(
            "---\nthrough: R-00000005\n---\n# Rule candidates\n\n"
            "- **Count every place a contract lands.** (seen 2: R-00000001, R-00000004)\n"
            "  A continuation line that is not a candidate of its own.\n"
            "- **Name the session.** (seen 1: R-00000002)\n",
            encoding="utf-8",
        )

        candidates, status = stage_memory_index.rule_candidate_lines(self.stage_root)
        context = stage_context.session_context(self.root)

        self.assertEqual(
            [
                "- **Count every place a contract lands.** (seen 2: R-00000001, R-00000004)",
                "- **Name the session.** (seen 1: R-00000002)",
            ],
            candidates,
        )
        self.assertIn("through R-00000005; 20 are newer.", status[0])
        self.assertIn("A consolidation session is due", status[0])
        self.assertIn("### Rule candidates (not yet rules)\n" + candidates[0], context)

    def test_fewer_than_twenty_new_retrospectives_is_not_due(self):
        self.write_retrospectives(24, candidate="- Something.")
        (self.stage_root / "state" / "rule-candidates.md").write_text(
            "---\nthrough: R-00000005\n---\n- **One.** (seen 1: R-00000001)\n", encoding="utf-8"
        )

        _candidates, status = stage_memory_index.rule_candidate_lines(self.stage_root)

        self.assertIn("19 are newer.", status[0])
        self.assertNotIn("due", status[0])


class FitBlocksTest(unittest.TestCase):
    def blocks(self) -> list[Block]:
        return [
            Block("### Now", ["- now " + "x" * 40]),
            Block(
                "### Decisions",
                [f"- D{n} " + "d" * 40 for n in range(9, 0, -1)],
                shed=1,
                noun="older decisions",
                read_at="`decisions/`",
            ),
            Block(
                "### Candidates",
                [f"- C{n} " + "c" * 40 for n in range(1, 4)],
                tail=["- status"],
                shed=2,
                noun="candidates",
                read_at="`list`",
            ),
        ]

    def test_under_the_limit_nothing_is_dropped(self):
        text = fit_blocks(self.blocks(), 10_000)

        self.assertNotIn("not shown", text)
        self.assertIn("- D1 ", text)

    def test_decisions_are_dropped_before_candidates_and_oldest_first(self):
        full = len(fit_blocks(self.blocks(), 10_000))

        text = fit_blocks(self.blocks(), full - 60)

        self.assertLessEqual(len(text), full - 60)
        self.assertIn("- D9 ", text)
        self.assertNotIn("- D1 ", text)
        self.assertIn("older decisions not shown — read `decisions/`", text)
        self.assertIn("- C3 ", text)

    def test_candidates_go_only_after_every_decision_and_fixed_lines_stay(self):
        text = fit_blocks(self.blocks(), 230)

        self.assertLessEqual(len(text), 230)
        self.assertIn("- …9 older decisions not shown — read `decisions/`", text)
        self.assertIn("candidates not shown — read `list`", text)
        self.assertIn("- now ", text)
        self.assertIn("- status", text)

    def test_the_limit_holds_when_nothing_can_be_dropped(self):
        text = fit_blocks([Block("### Now", ["- " + "x" * 500])], 120)

        self.assertEqual(120, len(text))
        self.assertTrue(text.endswith("read `.stage/index.md` for the rest"))


if __name__ == "__main__":
    unittest.main()
