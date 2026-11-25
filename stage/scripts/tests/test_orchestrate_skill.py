"""The stage-orchestrate skill owns the cloud session procedure; stage-handoff points to it."""

from __future__ import annotations

import unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2] / "skills"


def read(skill: str) -> str:
    return (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")


class OrchestrateSkillTest(unittest.TestCase):
    def test_the_skill_names_itself_and_both_generated_briefs(self) -> None:
        text = read("stage-orchestrate")

        self.assertTrue(text.startswith("---\nname: stage-orchestrate\ndescription: "))
        self.assertIn("subsession_brief.py --project-root . [<W-id>]", text)
        self.assertIn("--role verify", text)
        self.assertIn("## Take over from the records", text)
        self.assertIn("`list_sessions`", text)
        self.assertIn("scripts/started_cards.py --project-root .", text)
        self.assertIn("waiting_sessions:", text)
        self.assertIn("`limit: 100`", text)
        self.assertIn("`<project-tag>`", text)
        self.assertNotIn("<repository>", text)
        self.assertIn("SESSION_STATUS_ARCHIVED", text)
        self.assertIn("## One conductor at a time", text)
        self.assertIn("Follow-up candidate: <text> — evidence: ", text)
        self.assertIn("Waiting on user: <question>", text)

    def test_the_skill_covers_what_the_first_conducting_run_filled_by_hand(self) -> None:
        text = read("stage-orchestrate")
        cloud = (SKILLS.parent / "operations" / "cloud-execution.md").read_text(encoding="utf-8")

        self.assertIn("## Open observations", text)
        self.assertIn("## Sessions that committed card records", text)
        self.assertIn("No work session has to be open for this rule.", text)
        self.assertIn("`parent_session_id`", text)
        self.assertIn("in this session's own conversation", text)
        self.assertIn("`not reserved on the remote`", text)
        self.assertIn("Order: <before or after which card>", text)
        self.assertIn("pushes nothing more until you", text)
        self.assertIn("it pushes no commit until the main session answers", cloud)
        self.assertIn("`retrospective: completed` and `retrospective_ref: <R-id>`", cloud)
        self.assertIn("`<type>(<scope>): <the card's whole change> (<W-id>)`", cloud)
        self.assertNotIn("git commit -C FETCH_HEAD", cloud)
        self.assertIn("runs and is recorded once", cloud)

    def test_a_follow_up_candidate_needs_evidence_to_become_a_card(self) -> None:
        """DE-00000102: the brief, the skill, and both gates state the same two conditions."""
        operations = SKILLS.parent / "operations"
        before = (operations / "before.md").read_text(encoding="utf-8")
        after = (operations / "after.md").read_text(encoding="utf-8")
        cloud = (operations / "cloud-execution.md").read_text(encoding="utf-8")
        skill = read("stage-orchestrate")
        brief = (SKILLS.parent / "scripts" / "subsession_brief.py").read_text(encoding="utf-8")

        for name, text in (("before", before), ("after", after), ("skill", skill), ("brief", brief)):
            flat = " ".join(text.replace('"', " ").split())
            with self.subTest(document=name):
                self.assertIn("broken now", flat)
                self.assertIn("reproduces", flat)
                self.assertRegex(flat, r"open milestone's `?(## )?[Cc]ompletion criteria")
        for name, text in (("after", after), ("skill", skill), ("cloud", cloud)):
            with self.subTest(document=name):
                self.assertIn('`operations/before.md`, "Follow-up candidates"', " ".join(text.split()))
                self.assertIn("Follow-up candidates: registered <n>, discarded <m>", text)
        self.assertIn("## Follow-up candidates", before)
        self.assertIn("discard it and record it nowhere", before)
        self.assertIn("Follow-up candidates: registered <n>, discarded <m>", before)
        self.assertIn("do not write the candidate anywhere", skill)
        self.assertIn("Follow-up candidates discarded: <n>", skill)
        self.assertNotIn("follow-up candidates that are not cards yet live there", skill)
        self.assertNotIn("Route follow-up plans", after)

    def test_a_verification_session_is_not_the_gate_on_closing(self) -> None:
        text = read("stage-orchestrate")
        cloud = (SKILLS.parent / "operations" / "cloud-execution.md").read_text(encoding="utf-8")
        review = (SKILLS.parent / "operations" / "review.md").read_text(encoding="utf-8")

        self.assertIn("A verification session is not the gate on closing a card (DE-00000101).", text)
        self.assertIn("can be observed only by\n      a whole session doing the thing", text)
        self.assertIn("then: start none; close the card, for an epic too", text)
        self.assertIn("Copy each `--criterion` from\nthe card", text)
        self.assertIn("add to the card's `## Verification`, on your branch", text)
        self.assertNotIn("The verification session's verdict decides whether you close", text)
        self.assertIn("The close review\n   is the only gate", cloud)
        self.assertIn(
            "The verification session and the session on the user's machine do not decide the close",
            review,
        )

    def test_the_skill_has_a_session_print_its_own_brief_for_every_role(self) -> None:
        text = read("stage-orchestrate")

        self.assertIn("## Give a session its brief", text)
        self.assertIn("--first-message", text)
        self.assertIn("the session runs it in its own checkout and reads its brief", text)
        self.assertNotIn("send it as the session's first message, unedited", text)
        self.assertNotIn("a first message you write", text)
        for role in ("work", "verify", "discussion", "planning", "consolidation"):
            self.assertIn(f"| `{role}` |", text)
        # The consolidation session's rules live in its brief, not in the skill.
        self.assertNotIn("first_message_must_say", text)

    def test_the_close_procedure_covers_the_paths_made_up_by_hand(self) -> None:
        text = read("stage-orchestrate")
        cloud = (SKILLS.parent / "operations" / "cloud-execution.md").read_text(encoding="utf-8")

        for section in (
            "Import again after a rejected close review",
            "Merge a card that waits for the user's machine",
        ):
            self.assertIn(f"### {section}\n", cloud)
            self.assertIn(f'("{section}")', text)
        self.assertIn("do not reset, revert, amend, or rebase it", cloud)
        self.assertIn("`git checkout FETCH_HEAD -- <path>`", cloud)
        self.assertIn("`git diff FETCH_HEAD -- <the card's scope paths", cloud)
        self.assertIn("--commit <first-squash> --commit HEAD", cloud)
        self.assertIn("no close review runs", cloud)
        self.assertIn("`This change was merged without a close review.`", cloud)
        self.assertIn("that close review is the card's\n    first", cloud)
        self.assertIn("- if: the card's `## Sessions` has a `verify` line", cloud)

    def test_the_procedures_state_the_judgment_contract_and_the_stand_in_permission(self) -> None:
        cloud = (SKILLS.parent / "operations" / "cloud-execution.md").read_text(encoding="utf-8")
        review = (SKILLS.parent / "operations" / "review.md").read_text(encoding="utf-8")

        self.assertIn("## How the reviewer judges", review)
        for method in ("| `ran` |", "| `read` |", "| `unable` |"):
            self.assertIn(method, review)
        self.assertIn("(1 PASS ran, 2 FAIL read, ...)", review)
        self.assertIn("lets it run any shell command", cloud)
        self.assertIn("the stand-in denies `git push` and `git commit`", cloud)
        self.assertIn("the reviewer changes something outside the repository", cloud)
        self.assertNotIn("and run `python3 -m unittest`; it may not edit project", cloud)

    def test_a_check_recorded_on_the_card_closes_a_machine_only_criterion(self) -> None:
        text = read("stage-orchestrate")
        cloud = (SKILLS.parent / "operations" / "cloud-execution.md").read_text(encoding="utf-8")
        review = (SKILLS.parent / "operations" / "review.md").read_text(encoding="utf-8")
        section = review.split("## A check recorded on the card\n", 1)[1].split("\n## ", 1)[0]

        # The two lines a machine-only criterion is judged from, with every part named.
        self.assertIn(
            "`- Checked <date> on <machine> at <commit>: <criterion> — <held\\|did not hold>; "
            "<the command or action> — <what it showed>`",
            section,
        )
        self.assertIn('`- User verdict <date>: <criterion> — <held\\|did not hold>; "<the user\'s words>"', section)
        # Allowed with method read; without a record it stays a FAIL.
        self.assertIn(
            "  - if: the newest line for the criterion says `held` and has every part\n"
            "    then: method is read and the verdict is PASS\n",
            section,
        )
        self.assertIn(
            "  - if: the card has no line for the criterion\n"
            "    then: method is unable and the verdict is FAIL, as before\n",
            section,
        )
        self.assertIn("never_written_by: the work session that built the card", section)
        self.assertIn("a statement in the executor report, the work log", section)
        # The procedures that write the lines point at the section that owns their form.
        for document in (cloud, text):
            self.assertIn('(`operations/review.md`, "A check recorded on the card"', document)
        self.assertIn("as one `- Checked` line per criterion", cloud)
        self.assertNotIn("first, and it judges every criterion\n", cloud)

    def test_handoff_keeps_no_copy_of_the_sub_session_procedure(self) -> None:
        text = read("stage-handoff")

        self.assertIn("see `stage-orchestrate`", text)
        for moved in ("subsession_brief.py", "--reserve-for", "split_when", "start_work.py <W-id>"):
            self.assertNotIn(moved, text)

    def test_the_driver_skill_states_its_boundary_with_the_orchestrator(self) -> None:
        self.assertIn("`stage-orchestrate`", read("stage-drive"))


if __name__ == "__main__":
    unittest.main()
