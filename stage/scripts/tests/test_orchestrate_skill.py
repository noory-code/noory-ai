"""The stage-orchestrate skill gives the PO role and owns the cloud session procedure.

DE-00000103 names the layers: the PO session, the plan, PM, verify, and research sessions under
it, and the specialist sub-agents under a PM session. stage-handoff points to this skill.
"""

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
        self.assertIn("## One PO session at a time", text)
        self.assertIn("Follow-up candidate: <text> — evidence: ", text)
        self.assertIn("Waiting on user: <question>", text)

    def test_the_skill_covers_what_the_first_conducting_run_filled_by_hand(self) -> None:
        text = read("stage-orchestrate")
        cloud = (SKILLS.parent / "operations" / "cloud-execution.md").read_text(encoding="utf-8")

        self.assertIn("## Open observations", text)
        self.assertIn("## Sessions that committed card records", text)
        self.assertIn("No PM session has to be open for this rule.", text)
        self.assertIn("`parent_session_id`", text)
        self.assertIn("in this session's own conversation", text)
        self.assertIn("`not reserved on the remote`", text)
        self.assertIn("Order: <before or after which card>", text)
        self.assertIn("pushes nothing more until you", text)
        self.assertIn("it pushes no commit until the PO session answers", cloud)
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

    def test_a_verify_session_is_not_the_gate_on_closing(self) -> None:
        text = read("stage-orchestrate")
        cloud = (SKILLS.parent / "operations" / "cloud-execution.md").read_text(encoding="utf-8")
        review = (SKILLS.parent / "operations" / "review.md").read_text(encoding="utf-8")

        self.assertIn("A verify session is not the gate on closing a card (DE-00000101).", text)
        self.assertIn("can be observed only by\n      a whole session doing the thing", text)
        self.assertIn("then: start none; close the card, for an epic too", text)
        self.assertIn("Copy each `--criterion` from\nthe card", text)
        self.assertIn("add to the card's `## Verification`, on your branch", text)
        self.assertNotIn("The verify session's verdict decides whether you close", text)
        self.assertIn("The close review\n   is the only gate", cloud)
        self.assertIn(
            "The verify session and the session on the user's machine do not decide the close",
            review,
        )

    def test_the_skill_has_a_session_print_its_own_brief_for_every_role(self) -> None:
        text = read("stage-orchestrate")

        self.assertIn("## Give a session its brief", text)
        self.assertIn("--first-message", text)
        self.assertIn("the session runs it in its own checkout and reads its brief", text)
        self.assertNotIn("send it as the session's first message, unedited", text)
        self.assertNotIn("a first message you write", text)
        for role in ("pm", "verify", "plan", "research"):
            self.assertIn(f"| `{role}` |", text)
        for gone in ("work", "discussion", "planning", "consolidation"):
            self.assertNotIn(f"| `{gone}` |", text)
            self.assertNotIn(f"--role {gone}", text)
        self.assertIn("--po-session <this-session-id>", text)
        self.assertNotIn("--main-session", text)
        # A session's rules live in its brief, not in the skill.
        self.assertNotIn("first_message_must_say", text)

    def test_the_user_talks_with_the_po_session_only(self) -> None:
        """DE-00000103: the talk stays in one session; plan drafts, the PO registers."""
        text = read("stage-orchestrate")
        flat = " ".join(text.split())

        self.assertIn("The user talks with one session, the PO session", text)
        self.assertIn("in this session's conversation and nowhere else", flat)
        self.assertIn("- send the user to another session to answer or to talk", text)
        self.assertIn("- a session that exists to talk with the user", text)
        self.assertNotIn("start a discussion session", text)
        # The digest carries the user's words; the plan session drafts; the PO registers.
        self.assertIn("## Start a plan session", text)
        self.assertIn("with the user's words quoted exactly", flat)
        self.assertIn("then send the digest as one message to that session", flat)
        self.assertIn("Register each card draft yourself (`stage-work`)", flat)
        self.assertIn("the plan session registers nothing", flat)
        self.assertIn("register from this session only; no other session of this project registers", flat)
        # Research returns options and never chooses.
        self.assertIn("## Start a research session", text)
        self.assertIn("The user chooses; the research session does not.", flat)

    def test_sessions_tags_and_sub_agents_follow_the_naming_rule(self) -> None:
        """DE-00000103, "네이밍 룰": titles, tags, and the specialists' names."""
        text = read("stage-orchestrate")
        flat = " ".join(text.split())

        for title in (
            'po: "PO <project>"',
            'plan: "Plan <topic>"',
            'pm: "PM <W-id> <short title>"',
            'verify: "Verify <W-id> <short title>"',
            'research: "Research <question>"',
        ):
            self.assertIn(title, text)
        for title in (
            "`PM <W-id> <short title>`", "`Verify <W-id> <short title>`", "`Plan <topic>`",
            "`Research <question>`",
        ):
            self.assertIn(f"| {title} |", text)
        self.assertIn("`<project-tag>`, `stage-role:<role>`, and `stage-po:<this-session-id>`", flat)
        self.assertIn("tag this session `<project-tag>` and `stage-role:po`", flat)
        self.assertIn("title it `PO <project>`", flat)
        self.assertIn("name: one profession noun (`developer`, `designer`, `planner`, `writer`, `tester`)", text)
        self.assertIn('run_description: "<profession> <W-id> <piece>"', text)
        self.assertIn("no number in a name", text)

    def test_a_new_po_finds_sessions_that_carry_the_earlier_tags(self) -> None:
        text = read("stage-orchestrate")
        take_over = text.split("## Take over from the records\n", 1)[1].split("\n## ", 1)[0]
        flat = " ".join(take_over.split())

        self.assertIn("a kept row's `stage-po:<id>` tag, or of its earlier `stage-main-session:<id>` tag", flat)
        self.assertIn("tagged `stage-role:po` or, from before DE-00000103, `stage-orchestrator`", flat)
        one_po = text.split("## One PO session at a time\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("on a session of before DE-00000103 `stage-orchestrator`", one_po)

    def test_gathering_rule_candidates_is_a_research_task(self) -> None:
        text = read("stage-orchestrate")
        operations = SKILLS.parent / "operations"
        retrospective = (operations / "retrospective.md").read_text(encoding="utf-8")
        promotion = (SKILLS / "stage-retrospective" / "rule-promotion.md").read_text(encoding="utf-8")

        self.assertIn("### The rule-candidates task\n", text)
        self.assertIn("`--role research --task rule-candidates --branch <its own branch>`", text)
        self.assertIn("the only file a research session ever writes", text)
        self.assertIn("`Rule candidates are due`", text)
        for name, document in (
            ("skill", text), ("retrospective", retrospective), ("promotion", promotion),
            ("closing skill", read("stage-retrospective")),
        ):
            with self.subTest(document=name):
                self.assertNotIn("consolidation session", document)
        for document in (retrospective, promotion):
            self.assertIn('("The rule-candidates task")', document)

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
        self.assertIn("never_written_by: the PM session that built the card", section)
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

    def test_the_driver_skill_states_its_boundary_with_the_po_session(self) -> None:
        self.assertIn("PO session (`stage-orchestrate`)", read("stage-drive"))

    def test_the_operations_name_the_sessions_as_the_decision_does(self) -> None:
        operations = SKILLS.parent / "operations"
        cloud = (operations / "cloud-execution.md").read_text(encoding="utf-8")
        review = (operations / "review.md").read_text(encoding="utf-8")

        self.assertIn("## Close a PM session's card\n", cloud)
        self.assertIn("its role: `po`, `plan`, `pm`, `verify`, or `research`", cloud)
        self.assertIn("`- Observed <date> by verify session <session-id> ...`", review)
        for name, document in (("cloud", cloud), ("review", review)):
            flat = " ".join(document.split()).lower()
            with self.subTest(document=name):
                for gone in ("main session", "sub-session", "work session", "orchestrator, from"):
                    self.assertNotIn(gone, flat)


if __name__ == "__main__":
    unittest.main()
