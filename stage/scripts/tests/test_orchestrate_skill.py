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
        self.assertIn("subsession_brief.py --project-root . <W-id>", text)
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
        self.assertIn("Follow-up candidate: <text>", text)
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

    def test_a_verification_session_is_not_the_gate_on_closing(self) -> None:
        text = read("stage-orchestrate")
        cloud = (SKILLS.parent / "operations" / "cloud-execution.md").read_text(encoding="utf-8")
        review = (SKILLS.parent / "operations" / "review.md").read_text(encoding="utf-8")

        self.assertIn("A verification session is not the gate on closing a card (DE-00000101).", text)
        self.assertIn("can be observed only by\n      a whole session doing the thing", text)
        self.assertIn("then: start none; close the card, for an epic too", text)
        self.assertIn('--criterion "<success criterion copied from the card>"', text)
        self.assertIn("add to the card's `## Verification`, on your branch", text)
        self.assertNotIn("The verification session's verdict decides whether you close", text)
        self.assertIn("The close review\n   is the only gate", cloud)
        self.assertIn("The verification session does\nnot decide the close.", review)

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

    def test_handoff_keeps_no_copy_of_the_sub_session_procedure(self) -> None:
        text = read("stage-handoff")

        self.assertIn("see `stage-orchestrate`", text)
        for moved in ("subsession_brief.py", "--reserve-for", "split_when", "start_work.py <W-id>"):
            self.assertNotIn(moved, text)

    def test_the_driver_skill_states_its_boundary_with_the_orchestrator(self) -> None:
        self.assertIn("`stage-orchestrate`", read("stage-drive"))


if __name__ == "__main__":
    unittest.main()
