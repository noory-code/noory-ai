"""The record-derived index a session starts with, and its size limit (DE-00000100)."""

from __future__ import annotations

import json
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
import stage_paths  # noqa: E402
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
        self.assertIn("| W-00000900 | The card in progress |", context)
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

    def test_the_list_gives_one_line_per_promote_candidate_and_says_when_candidates_are_due(self):
        self.write_retrospectives(25, candidate="- Something.")
        (self.stage_root / "state" / "rule-candidates.md").write_text(
            "---\nthrough: R-00000005\n---\n# Rule candidates\n\n"
            "- **Count every place a contract lands.** (seen 2: R-00000001, R-00000004)\n"
            "  A continuation line that is not a candidate of its own — proposed: promote\n"
            "- **Name the session.** (seen 2: R-00000002, R-00000003) — proposed: promote\n",
            encoding="utf-8",
        )

        candidates, status = stage_memory_index.rule_candidate_lines(self.stage_root)
        context = stage_context.session_context(self.root)

        self.assertEqual(
            [
                "- **Count every place a contract lands.** (seen 2: R-00000001, R-00000004)",
                "- **Name the session.** (seen 2: R-00000002, R-00000003) — proposed: promote",
            ],
            candidates,
        )
        # Every candidate is listed, so no line counts unlisted ones.
        self.assertEqual(1, len(status))
        self.assertNotIn("are not listed", context)
        self.assertIn("through R-00000005; 20 are newer.", status[0])
        self.assertIn("Rule candidates are due (20 or more): give a research session", status[0])
        self.assertNotIn("consolidation session", status[0])
        self.assertIn("### Rule candidates (not yet rules)\n" + candidates[0], context)

    def test_fewer_than_twenty_new_retrospectives_is_not_due(self):
        self.write_retrospectives(24, candidate="- Something.")
        (self.stage_root / "state" / "rule-candidates.md").write_text(
            "---\nthrough: R-00000005\n---\n- **One.** (seen 1: R-00000001)\n", encoding="utf-8"
        )

        candidates, status = stage_memory_index.rule_candidate_lines(self.stage_root)

        self.assertEqual([], candidates)
        self.assertIn("19 are newer.", status[-1])
        self.assertNotIn("due", status[-1])


def candidate_list(count: int, promote_every: int = 0) -> str:
    """A consolidated list of `count` wrapped bullets in the documented format.

    Every `promote_every`-th bullet proposes promotion on its wrapped line; the rest hold.
    """
    bullets = []
    for number in range(1, count + 1):
        proposal = "promote" if promote_every and number % promote_every == 0 else "hold"
        bullets.append(
            f"- **Candidate behavior number {number} written as one imperative sentence.** "
            f"(seen 2: R-{number:08d},\n  R-{number + 100:08d}) — proposed: {proposal}\n"
        )
    return "---\nthrough: R-00000399\n---\n# Rule candidates\n\n" + "".join(bullets)


HOLD_COUNT_LINE = (
    "- {count} more candidates are `proposed: hold` and are not listed — read "
    "`.stage/state/rule-candidates.md`."
)


class CandidatesGiveWayToDecisionsTest(SessionIndexFixture):
    """W-00000413: 39 candidates had left the index with no decision title at all."""

    def write_candidates(self, count: int, promote_every: int = 0) -> None:
        (self.stage_root / "state" / "rule-candidates.md").write_text(
            candidate_list(count, promote_every), encoding="utf-8"
        )

    def test_only_promote_proposals_are_listed_and_the_rest_are_counted(self):
        """DE-00000104: a candidate below the threshold stays in the list, not in the index."""
        self.write_candidates(6, promote_every=3)

        candidates, status = stage_memory_index.rule_candidate_lines(self.stage_root)
        index = stage_context.session_index(self.root)

        self.assertEqual(
            [3, 6],
            [int(line.split("number ")[1].split()[0]) for line in candidates],
        )
        self.assertEqual(
            [
                HOLD_COUNT_LINE.format(count=4),
                "- `.stage/state/rule-candidates.md` covers retrospectives through R-00000399; "
                "0 are newer.",
            ],
            status,
        )
        self.assertIn(
            "### Rule candidates (not yet rules)\n" + "\n".join(candidates + status), index
        )

    def test_a_bullet_without_a_proposal_counts_as_hold(self):
        (self.stage_root / "state" / "rule-candidates.md").write_text(
            "---\nthrough: R-00000001\n---\n- **First.** (seen 1: R-00000001)\n"
            "- **Second.** (seen 2: R-00000001,\n  R-00000002) — proposed: promote\n",
            encoding="utf-8",
        )

        candidates, status = stage_memory_index.rule_candidate_lines(self.stage_root)

        self.assertEqual(["- **Second.** (seen 2: R-00000001,"], candidates)
        self.assertEqual(HOLD_COUNT_LINE.format(count=1), status[0])

    def test_a_list_of_hold_candidates_alone_still_shows_their_count(self):
        self.write_candidates(4)

        candidates, status = stage_memory_index.rule_candidate_lines(self.stage_root)
        index = stage_context.session_index(self.root)

        self.assertEqual([], candidates)
        self.assertEqual(2, len(status))
        self.assertIn(
            "### Rule candidates (not yet rules)\n" + HOLD_COUNT_LINE.format(count=4) + "\n"
            "- `.stage/state/rule-candidates.md` covers retrospectives through",
            index,
        )
        self.assertNotIn("- **Candidate", index)

    def test_a_list_without_a_through_id_still_counts_the_unlisted_candidates(self):
        (self.stage_root / "state" / "rule-candidates.md").write_text(
            "- **First.** (seen 1: R-00000001) — proposed: hold\n", encoding="utf-8"
        )

        candidates, status = stage_memory_index.rule_candidate_lines(self.stage_root)

        self.assertEqual([], candidates)
        self.assertEqual(HOLD_COUNT_LINE.format(count=1), status[0])
        self.assertIn("declares no `through: R-<id>`", status[1])

    def test_thirty_nine_candidates_leave_the_decision_titles_in_the_index(self):
        self.write_decisions(82)
        self.write_active_card()
        self.write_candidates(39, promote_every=1)

        context = stage_context.session_context(self.root)

        self.assertLessEqual(len(context), LIMIT)
        listed = [line.split()[1] for line in context.splitlines() if line.startswith("- DE-")]
        self.assertTrue(listed, "no decision title is shown")
        self.assertEqual("DE-00000082", listed[0])
        shown = [line for line in context.splitlines() if line.startswith("- **Candidate")]
        # Decisions lose a title only after every candidate line is gone.
        if "older decisions not shown" in context:
            self.assertEqual([], shown)
            self.assertIn(
                "- …39 candidates not shown — read `.stage/state/rule-candidates.md`", context
            )
        else:
            self.assertEqual(82, len(listed))

    def test_five_active_cards_and_thirty_nine_candidates_keep_every_decision_title(self):
        """W-00000417: the standing rules were cut so that this state fits."""
        settings_path, settings, error = stage_paths.read_settings(self.stage_root)
        self.assertIsNone(error)
        settings["language"] = "ko"
        settings["venue_routing"] = {
            kind: "codex"
            for kind in (
                "planning", "design", "documentation", "development", "fix",
                "qa", "ops", "release", "chore", "feature",
            )
        }
        settings_path.write_text(json.dumps(settings), encoding="utf-8")
        self.write_decisions(82)
        for number in range(901, 906):
            folder = self.stage_root / "work" / "current" / f"W-{number:08d}"
            folder.mkdir(parents=True)
            (folder / "_story.md").write_text(
                card(f"W-{number:08d}", "A card in progress whose title runs to a usual length"),
                encoding="utf-8",
            )
        for name in ("CLAUDE.md", "AGENTS.md"):
            (self.root / name).write_text("# Instructions\n", encoding="utf-8")
        self.write_candidates(39, promote_every=1)

        context = stage_context.session_context(self.root)

        self.assertLessEqual(len(context), LIMIT)
        self.assertNotIn("older decisions not shown", context)
        listed = [line for line in context.splitlines() if line.startswith("- DE-")]
        self.assertEqual(82, len(listed))
        self.assertEqual(5, sum(line.startswith("| W-000009") for line in context.splitlines()))

    def test_the_standing_rules_stay_short(self):
        """Every character of the rules is one the index cannot use (W-00000417)."""
        settings_path, settings, error = stage_paths.read_settings(self.stage_root)
        self.assertIsNone(error)
        settings["language"] = "ko"
        settings["venue_routing"] = {"design": "claude", "development": "codex"}
        settings_path.write_text(json.dumps(settings), encoding="utf-8")

        rules = stage_context.session_context(self.root).split("\n\n### ", 1)[0]

        self.assertTrue(rules.startswith("## Stage context\n"))
        self.assertLessEqual(len(rules), 1_500, rules)
        for line in rules.splitlines()[1:]:
            self.assertTrue(line.startswith("- "), line)

    def test_listed_candidates_are_left_out_from_the_end_and_the_hold_count_stays(self):
        self.write_decisions(3)
        self.write_candidates(39, promote_every=5)
        full = stage_context.session_index(self.root)
        self.assertNotIn("not shown", full)
        self.assertEqual(7, sum(line.startswith("- **Candidate") for line in full.splitlines()))

        index = stage_context.session_index(self.root, len(full) - 300)

        shown = [line for line in index.splitlines() if line.startswith("- **Candidate")]
        numbers = [int(line.split("number ")[1].split()[0]) for line in shown]
        self.assertTrue(numbers, "no promote candidate is shown")
        self.assertLess(len(numbers), 7)
        self.assertEqual([5, 10, 15, 20, 25, 30, 35][: len(numbers)], numbers)
        # The line that counts what was left out counts promote lines only.
        self.assertIn(
            f"- …{7 - len(numbers)} candidates not shown — read "
            "`.stage/state/rule-candidates.md`\n" + HOLD_COUNT_LINE.format(count=32),
            index,
        )
        self.assertEqual(
            3, sum(1 for line in index.splitlines() if line.startswith("- DE-"))
        )
        self.assertNotIn("older decisions not shown", index)


class FitBlocksTest(unittest.TestCase):
    def blocks(self) -> list[Block]:
        return [
            Block("### Now", ["- now " + "x" * 40]),
            Block(
                "### Decisions",
                [f"- D{n} " + "d" * 40 for n in range(9, 0, -1)],
                shed=2,
                noun="older decisions",
                read_at="`decisions/`",
            ),
            Block(
                "### Candidates",
                [f"- C{n} " + "c" * 40 for n in range(1, 4)],
                tail=["- status"],
                shed=1,
                noun="candidates",
                read_at="`list`",
            ),
        ]

    def test_under_the_limit_nothing_is_dropped(self):
        text = fit_blocks(self.blocks(), 10_000)

        self.assertNotIn("not shown", text)
        self.assertIn("- D1 ", text)

    def test_candidates_are_dropped_before_decisions_and_from_the_end(self):
        full = len(fit_blocks(self.blocks(), 10_000))

        text = fit_blocks(self.blocks(), full - 5)

        self.assertLessEqual(len(text), full - 5)
        self.assertIn("- C1 ", text)
        self.assertNotIn("- C3 ", text)
        self.assertIn("candidates not shown — read `list`", text)
        self.assertIn("- D9 ", text)
        self.assertIn("- D1 ", text)
        self.assertNotIn("older decisions not shown", text)

    def test_decisions_go_only_after_every_candidate_oldest_first_and_fixed_lines_stay(self):
        text = fit_blocks(self.blocks(), 420)

        self.assertLessEqual(len(text), 420)
        self.assertIn("- …3 candidates not shown — read `list`", text)
        self.assertIn("older decisions not shown — read `decisions/`", text)
        self.assertIn("- D9 ", text)
        self.assertNotIn("- D1 ", text)
        self.assertIn("- now ", text)
        self.assertIn("- status", text)

    def test_the_limit_holds_when_nothing_can_be_dropped(self):
        text = fit_blocks([Block("### Now", ["- " + "x" * 500])], 120)

        self.assertEqual(120, len(text))
        self.assertTrue(text.endswith("read `.stage/index.md` for the rest"))


if __name__ == "__main__":
    unittest.main()
