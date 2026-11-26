"""The briefs that give each session under the PO session its role (DE-00000094, DE-00000103)."""

from __future__ import annotations

import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
BRIEF = SCRIPTS / "subsession_brief.py"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def brief(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BRIEF), "--project-root", str(root), "--po-session", "session_po", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class SubsessionBriefTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        write(self.root / ".stage/settings.json", '{"schema_version": 5}\n')
        write(
            self.root / ".stage/decisions/pending/DE-00000007.md",
            "---\nid: DE-00000007\n---\n\n# DE-00000007 Choice\n",
        )

    def card(self, extra: str = "", where: str = "W-00000002/_story.md") -> None:
        write(
            self.root / ".stage/work/current" / where,
            "---\nid: W-00000002\ntitle: Build it\nstatus: active\nscope: src/\n"
            "acceptance:\n  - \"python3 -m unittest -q\"\n"
            f"decision_refs: DE-00000007\n{extra}---\n\n# W-00000002 Build it\n\n"
            "## Success criteria\n\n- The suite passes\n"
            "- A new cloud session takes the role\n  and reports back\n\n## Progress\n\n- Not a criterion\n",
        )

    def test_a_card_with_reserved_ids_tells_the_pm_session_how_to_take_them(self) -> None:
        self.card("reserved_ids: DE-00000008, DE-00000009\n")

        proc = brief(self.root, "W-00000002", "--branch", "claude/w2")

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn("You are a PM session of the PO session `session_po`. You manage one Stage card", out)
        self.assertIn("`.stage/work/current/W-00000002/_story.md`", out)
        self.assertIn("`.stage/decisions/pending/DE-00000007.md`", out)
        self.assertIn("`python3 -m unittest -q`", out)
        self.assertIn("reserved `DE-00000008, DE-00000009`", out)
        self.assertIn("--from-card W-00000002 <PREFIX>", out)
        self.assertIn("own branch `claude/w2`", out)
        self.assertIn("Do not run `start_work.py`, `register_work.py`, `close_work.py`", out)
        self.assertIn("send the PO session `session_po` one message", out)
        self.assertIn("Do not edit the card's `## Progress` or `## Next action` section", out)

    def test_the_brief_asks_for_scope_crossings_in_the_commit_report(self) -> None:
        self.card()

        out = brief(self.root, "W-00000002").stdout

        self.assertIn("outside the scope, and why, in that report's `Decisions made:`", out)
        self.assertIn("reads only the commit's report, not your message", out)

    def test_the_brief_leaves_other_os_checks_to_the_po_session(self) -> None:
        self.card()

        out = brief(self.root, "W-00000002").stdout

        self.assertIn("Checks that must run on another OS (for example Windows) are not yours to run", out)

    def test_the_brief_keeps_recorded_checks_out_of_the_builders_hands(self) -> None:
        self.card()

        out = brief(self.root, "W-00000002").stdout

        self.assertIn(
            "- Do not write a `- Checked` or `- User verdict` line on the card's `## Verification`",
            out,
        )
        self.assertIn('operations/review.md`,\n  "A check recorded on the card").', out)
        self.assertIn("The PO session opens the pull request and reads its CI jobs.", out)

    def test_the_brief_asks_for_evidence_with_each_follow_up_candidate(self) -> None:
        """DE-00000102: a candidate without evidence never becomes a card."""
        self.card()

        out = brief(self.root, "W-00000002").stdout

        self.assertIn("- follow-up work candidates (do not register them), each with its evidence:", out)
        self.assertIn("the command that reproduces what is broken now and what it prints", out)
        self.assertIn("one line quoted from an open milestone's `## Completion criteria`", out)
        self.assertIn("discards the rest unrecorded (DE-00000102)", out)

    def test_a_card_without_reserved_ids_forbids_new_records(self) -> None:
        self.card()

        out = brief(self.root, "W-00000002").stdout

        self.assertIn("No ids are reserved for this card", out)
        self.assertNotIn("--from-card", out)

    def test_a_nested_story_lists_its_epic_first(self) -> None:
        write(
            self.root / ".stage/work/current/W-00000001/_epic.md",
            "---\nid: W-00000001\ntitle: Epic\nstatus: active\n---\n",
        )
        self.card(where="W-00000001/W-00000002/_story.md")

        out = brief(self.root, "W-00000002").stdout

        epic = out.index("W-00000001/_epic.md` (ancestor)")
        story = out.index("W-00000001/W-00000002/_story.md`")
        self.assertLess(epic, story)

    def epic(self) -> None:
        write(
            self.root / ".stage/work/current/W-00000001/_epic.md",
            "---\nid: W-00000001\ntitle: Ship it\nstatus: active\nscope: src/, docs/\n"
            "acceptance: []\n---\n\n# W-00000001 Ship it\n",
        )
        self.card(where="W-00000001/W-00000002/_story.md")
        write(
            self.root / ".stage/work/current/W-00000001/W-00000003/_story.md",
            "---\nid: W-00000003\ntitle: Document it\nstatus: completed\nscope: docs/\n"
            "acceptance: []\n---\n\n# W-00000003 Document it\n",
        )

    def test_an_epic_brief_runs_its_stories_in_sub_agents_with_one_commit_each(self) -> None:
        self.epic()

        proc = brief(self.root, "W-00000001", "--branch", "claude/w1")

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn("PM session of the PO session `session_po`. You manage one Stage epic", out)
        self.assertIn("review judges each story (DE-00000094, DE-00000101, DE-00000103)", out)
        self.assertNotIn("verify session", out)
        self.assertIn("Give each story to a specialist sub-agent of this session", out)
        self.assertIn("Inspect each story yourself against its completion condition", out)
        self.assertNotIn("## Pieces and specialists", out)
        self.assertIn(
            "- W-00000002 Build it (`active`): `.stage/work/current/W-00000001/W-00000002/_story.md`",
            out,
        )
        self.assertIn("  - scope: `src/`", out)
        self.assertIn("  - check: `python3 -m unittest -q`", out)
        self.assertIn("- W-00000003 Document it (`completed`)", out)
        self.assertIn("status is not one of `archived`, `completed`, `rejected`", out)
        self.assertIn("Do\n  not create another cloud session for a story", out)
        self.assertIn("Commit each story as its own commit, with the story's id", out)
        self.assertIn("Write one `### Executor report` per story", out)
        self.assertIn("each story's id and the commit that carries its executor report", out)
        self.assertIn("Do not edit any card's `status`", out)

    def test_a_story_brief_has_no_stories_section(self) -> None:
        self.card()

        out = brief(self.root, "W-00000002").stdout

        self.assertNotIn("## Stories", out)
        self.assertIn("## Pieces and specialists", out)
        self.assertIn("Write the `### Executor report` in the body of your last commit", out)

    SESSION_ONLY = "A new cloud session takes the role and reports back"

    def test_a_verify_brief_observes_the_named_criteria_and_changes_nothing(self) -> None:
        self.card("reserved_ids: DE-00000008\n")

        proc = brief(
            self.root, "W-00000002", "--role", "verify", "--branch", "claude/w2",
            "--commit", "abc1234", "--criterion", self.SESSION_ONLY,
        )

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn("verify session of the PO session `session_po`. For one Stage card", out)
        self.assertIn("observe what only a whole session can observe; you change nothing", out)
        self.assertIn("the PO session closes and merges it", out)
        self.assertIn("The change is commit `abc1234` on branch `claude/w2`.", out)
        self.assertIn("`.stage/work/current/W-00000002/_story.md`", out)
        self.assertIn("`.stage/decisions/pending/DE-00000007.md`", out)
        self.assertIn(f"\n- {self.SESSION_ONLY}\n", out)
        self.assertNotIn("- The suite passes", out)
        self.assertIn("Do not edit, commit, or push anything", out)
        self.assertIn("Do not write a review verdict file", out)
        self.assertIn("Do not run `start_work.py`, `register_work.py`, `close_work.py`", out)
        self.assertIn("`held`, `did not hold`, or `could not observe`", out)
        self.assertIn("Send the PO session `session_po` one message with:", out)
        self.assertNotIn("## Record ids", out)
        self.assertNotIn("--from-card", out)
        self.assertNotIn("Commit and push only to your own branch", out)

    def test_a_verify_brief_says_the_session_is_not_the_gate_on_closing(self) -> None:
        self.card()

        out = brief(
            self.root, "W-00000002", "--role", "verify", "--criterion", self.SESSION_ONLY
        ).stdout

        self.assertIn("You are not the gate on closing (DE-00000101).", out)
        self.assertIn("writes what you observed\non the card's `## Verification`", out)
        self.assertIn("the close reviewer reads it there and judges every\nsuccess criterion", out)
        self.assertIn("Leave the card's other success criteria alone", out)
        # The session reports observations, not a verdict that decides the close.
        for verdict_word in ("`PASS`", "`FAIL`", "approved:", "Run these checks yourself"):
            self.assertNotIn(verdict_word, out)

    def test_a_verify_brief_is_refused_without_a_session_only_criterion(self) -> None:
        self.card()

        proc = brief(self.root, "W-00000002", "--role", "verify", "--commit", "abc1234")

        self.assertEqual(1, proc.returncode)
        self.assertEqual("", proc.stdout)
        self.assertIn("only a whole session can observe (DE-00000101)", proc.stderr)
        self.assertIn("--criterion", proc.stderr)

    def test_a_verify_brief_refuses_a_criterion_the_card_does_not_state(self) -> None:
        self.card()

        for criterion in ("The reviewer is happy", "Not a criterion", " "):
            with self.subTest(criterion=criterion):
                proc = brief(self.root, "W-00000002", "--role", "verify", "--criterion", criterion)

                self.assertEqual(1, proc.returncode)
                self.assertEqual("", proc.stdout)
                self.assertIn("not under `## Success criteria`", proc.stderr)

    def test_a_verify_brief_without_a_commit_finds_the_card_by_id_in_the_log(self) -> None:
        self.card()

        out = brief(
            self.root, "W-00000002", "--role", "verify", "--criterion", self.SESSION_ONLY
        ).stdout

        self.assertIn(
            "The change is on the branch you were created from: for each card, the last commit "
            "whose message names its id.",
            out,
        )

    def test_a_verify_brief_for_an_epic_takes_a_criterion_from_a_story(self) -> None:
        self.epic()

        proc = brief(
            self.root, "W-00000001", "--role", "verify", "--branch", "claude/w1",
            "--criterion", self.SESSION_ONLY,
        )

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn("For one Stage epic you", out)
        self.assertIn("- W-00000002 Build it (`active`)", out)
        self.assertIn(f"\n- {self.SESSION_ONLY}\n", out)

    def test_the_brief_ends_with_the_index_the_session_start_hook_gives(self) -> None:
        self.card()
        sys.path.insert(0, str(SCRIPTS.parent / "hooks"))
        import stage_context

        for role_args in ([], ["--role", "verify", "--criterion", "The suite passes"]):
            with self.subTest(role=role_args):
                proc = brief(self.root, "W-00000002", "--branch", "claude/w2", *role_args)

                self.assertEqual(0, proc.returncode, proc.stderr)
                head, index = proc.stdout.split("\n## Session index\n", 1)
                self.assertIn("- DE-00000007 Choice", index)
                self.assertIn("| W-00000002 | Build it |", index)
                # The same function the hook calls, so the two cannot drift apart.
                self.assertTrue(
                    index.rstrip("\n").endswith(stage_context.session_index(self.root)), index
                )
                self.assertNotIn("## Stage context", proc.stdout)
        # The PM session reports which lines it used: the only record of the index's use.
        self.assertIn(
            "- the ids of the records you opened because the session index below listed them",
            brief(self.root, "W-00000002").stdout,
        )

    def test_the_brief_with_its_index_stays_within_the_hook_limit(self) -> None:
        self.card()
        for number in range(100, 500):
            write(
                self.root / f".stage/official/decisions/records/DE-{number:08d}.md",
                f"---\nid: DE-{number:08d}\nstatus: promoted\n---\n\n"
                f"# DE-{number:08d} A decision with a reasonably long title, number {number}\n",
            )

        proc = brief(self.root, "W-00000002", "--branch", "claude/w2")

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertLessEqual(len(proc.stdout), 10_000)
        self.assertIn("- DE-00000499 ", proc.stdout)
        self.assertNotIn("- DE-00000100 ", proc.stdout)
        self.assertIn("older decisions not shown — read", proc.stdout)
        # The brief's own rules are never what gets shortened.
        self.assertIn("Then wait, and push no commit until the PO session answers", proc.stdout)

    def test_a_pm_brief_hands_pieces_to_specialists_and_does_a_small_card_itself(self) -> None:
        """DE-00000103: the PM inspects what specialists return; one piece it does itself."""
        self.card()

        out = brief(self.root, "W-00000002", "--role", "pm").stdout
        flat = " ".join(out.split())

        self.assertEqual(out, brief(self.root, "W-00000002").stdout)
        self.assertIn(
            "- if: the card's change splits into two or more pieces that can each be finished and "
            "checked on its own then: give each piece to a specialist sub-agent of this session",
            flat,
        )
        self.assertIn("- else: do the card yourself, and start no sub-agent for it.", out)
        self.assertIn("Do not create another cloud session for a piece.", flat)
        self.assertIn(
            "Name a specialist by one profession noun: `developer`, `designer`, `planner`, "
            "`writer`, `tester`;",
            out,
        )
        self.assertIn("Put no number in the name.", out)
        self.assertIn("Describe each run as `<profession> <card id> <piece>`", out)
        self.assertIn("`developer W-00000002 parser`", out)
        self.assertIn("that piece's completion condition", out)
        self.assertIn("Inspect each piece yourself against its completion condition", out)
        self.assertIn("A specialist's summary is a claim.", out)
        self.assertIn("A specialist decides nothing either: it returns a decision to you", out)

    def test_a_plan_brief_drafts_cards_from_the_digest_and_registers_nothing(self) -> None:
        proc = brief(self.root, "--role", "plan", "--topic", "Cut  the migration\ninto cards")

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn("You are a plan session of the PO session `session_po`.", out)
        self.assertIn("## Topic\n\nCut the migration into cards\n", out)
        self.assertIn("sends you its digest of that talk, with the\nuser's words quoted", out)
        self.assertIn("From the digest you write card drafts", out)
        self.assertIn("You build nothing and register nothing: the PO\nsession registers your drafts.", out)
        self.assertIn("When you\nhave this brief and no digest, ask the PO session for it and wait.", out)
        self.assertIn("You never design how a card is\nexecuted", out)
        self.assertIn("It carries no steps,\n  no file-level design, and no method.", out)
        self.assertIn("docs/PHILOSOPHY.md`", out)
        self.assertIn("do not invent it: leave it empty in the draft", out)
        self.assertIn("do not create a card, a decision record, or\n  any record that needs a new id", out)
        self.assertIn("Do not edit, commit, or push anything", out)
        self.assertIn("Do not run `start_work.py`, `register_work.py`, `close_work.py`", out)
        self.assertIn("When the drafts are complete, send the PO session", out)
        self.assertIn("- each card draft, in the order to run them and why that order", out)
        self.assertIn("the user's words that back it, quoted from the digest", out)
        self.assertIn("the PO session asks the user before it registers that card", out)
        self.assertIn("only the user's machine or a whole session can observe", out)
        self.assertIn("- the ids of the records you opened because the session index below", out)
        self.assertNotIn("## Card:", out)
        self.assertNotIn("Executor report", out)

    def test_a_research_brief_returns_options_and_decides_nothing(self) -> None:
        proc = brief(self.root, "--role", "research", "--topic", "Which lock works on Windows?")

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn("You are a research session of the PO session `session_po`.", out)
        self.assertIn("## Question\n\nWhich lock works on Windows?\n", out)
        self.assertIn("return the options and the evidence for each (DE-00000103)", out)
        self.assertIn("You decide nothing and\nbuild nothing. Keep the work as small as the question.", out)
        self.assertIn("Do not choose among the options; the user chooses, through the PO session.", out)
        self.assertIn("a file path and line, a command and\n  what it printed, or a URL", out)
        self.assertIn("Do not edit, commit, or push anything", out)
        self.assertIn("- each option, with the evidence for and against it", out)
        self.assertIn("- what you could not find out", out)
        self.assertNotIn("rule-candidates.md", out)
        self.assertNotIn("Write only", out)

    def test_every_brief_sends_questions_for_the_user_to_the_po_session(self) -> None:
        """DE-00000103: the user talks with the PO session only."""
        self.card()

        for role, arguments in self.ROLE_ARGUMENTS.items():
            with self.subTest(role=role):
                proc = brief(self.root, *arguments)

                self.assertEqual(0, proc.returncode, proc.stderr)
                head = proc.stdout.split("\n## Session index\n", 1)[0]
                self.assertIn(
                    "- Do not ask the user anything in this session's conversation: the user talks "
                    "with the PO\n  session only (DE-00000103). Put every question for the user in "
                    "your report to the PO\n  session; it asks the user and sends you the answer.",
                    head,
                )
                self.assertIn("send the user's words, quoted, to the PO\n  session", head)
                self.assertIn("- anything that needs the user's confirmation", head)
                # DE-00000103, "의사결정은 PO 에서 한다": no session under the PO decides.
                self.assertIn(
                    "- Do not make a decision yourself: every decision is made at the PO session "
                    "(DE-00000103).",
                    head,
                )
                flat = " ".join(head.split())
                for kind in (
                    "selects between two or more viable options",
                    "would need more than one file edited to reverse",
                    "sets a value another card depends on (a name, a path, a schema, an interface)",
                    "changes a file under `official/`",
                    "changes a card's scope or leaves a success criterion unmet",
                ):
                    self.assertIn(kind, flat)
                self.assertIn(
                    "Before you build what depends on a decision, send the PO session the options "
                    "and the one you recommend, and wait for its answer.",
                    flat,
                )
                self.assertIn("Send the decisions you can see ahead in one message", flat)
                self.assertIn(
                    "A how-detail that touches one file and is undone by undoing that file is "
                    "yours to settle.",
                    flat,
                )
                for gone in ("ask the user in this session", "Talk with the user in this session"):
                    self.assertNotIn(gone, head)

    def test_a_topic_brief_lists_a_started_card_to_read_when_one_is_named(self) -> None:
        self.card()

        for role in ("plan", "research"):
            with self.subTest(role=role):
                out = brief(self.root, "W-00000002", "--role", role, "--topic", "Change course").stdout

                self.assertIn("- `.stage/work/current/W-00000002/_story.md`", out)
                self.assertIn("- `.stage/decisions/pending/DE-00000007.md`", out)
                self.assertNotIn("## Record ids", out)

    def test_a_topic_brief_is_refused_without_a_topic_or_for_an_unstarted_card(self) -> None:
        for role in ("plan", "research"):
            with self.subTest(role=role):
                no_topic = brief(self.root, "--role", role, "--topic", " ")
                no_card = brief(self.root, "W-00000099", "--role", role, "--topic", "Change course")

                self.assertEqual((1, ""), (no_topic.returncode, no_topic.stdout))
                self.assertIn(f"--role {role} needs --topic", no_topic.stderr)
                self.assertEqual((1, ""), (no_card.returncode, no_card.stdout))
                self.assertIn("start it first", no_card.stderr)

    def test_the_rule_candidates_task_is_the_only_one_that_writes_a_file(self) -> None:
        """DE-00000103: gathering rule candidates is a task of a research session."""
        proc = brief(
            self.root, "--role", "research", "--task", "rule-candidates", "--branch", "claude/candidates"
        )

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn(
            "You are a research session of the PO session `session_po`. Your task is to gather\n"
            "rule candidates",
            out,
        )
        self.assertNotIn("consolidation session", out)
        self.assertIn("skills/stage-retrospective/rule-promotion.md`", out)
        self.assertIn("every retrospective newer than that list's `through:` id", out)
        self.assertIn(
            "Write only `.stage/state/rule-candidates.md`: a research session writes a file in "
            "this task only.",
            out,
        )
        self.assertIn("branch `claude/candidates`", out)
        self.assertIn("Do not edit a retrospective, a decision record, a rule file, a skill, or a card", out)
        self.assertIn("mark a candidate `proposed: promote` and stop there", out)
        self.assertIn("- each `proposed: promote` line with the retrospectives it cites", out)

    def test_the_task_takes_no_card_no_topic_and_no_other_role(self) -> None:
        self.card()

        for arguments, message in (
            (["W-00000002", "--role", "research"], "pass no W-id"),
            (["--role", "research", "--topic", "Anything"], "pass no --topic"),
            (["--role", "plan"], "pass --role research"),
            (["W-00000002"], "pass --role research"),
        ):
            with self.subTest(arguments=arguments):
                proc = brief(self.root, *arguments, "--task", "rule-candidates")

                self.assertEqual((1, ""), (proc.returncode, proc.stdout))
                self.assertIn(message, proc.stderr)

    def test_a_card_role_needs_a_card(self) -> None:
        for role in ("pm", "verify"):
            with self.subTest(role=role):
                proc = brief(self.root, "--role", role)

                self.assertEqual((1, ""), (proc.returncode, proc.stdout))
                self.assertIn(f"--role {role} needs the started card's W-id", proc.stderr)

    ROLE_ARGUMENTS = {
        "pm": ["W-00000002", "--branch", "claude/w2"],
        "verify": [
            "W-00000002", "--role", "verify", "--branch", "claude/w2", "--commit", "abc1234",
            "--criterion", "A new cloud session takes the role and reports back",
        ],
        "plan": ["W-00000002", "--role", "plan", "--topic", "Cut the migration"],
        "research": ["--role", "research", "--topic", "Whether it's time to split `drive.py`"],
        "research task": [
            "--role", "research", "--task", "rule-candidates", "--branch", "claude/candidates",
        ],
    }

    def test_the_first_message_has_the_session_print_the_same_brief_itself(self) -> None:
        self.card()
        names = {"pm": "PM", "research task": "research"}

        for role, arguments in self.ROLE_ARGUMENTS.items():
            with self.subTest(role=role):
                pasted = brief(self.root, *arguments)
                proc = brief(self.root, *arguments, "--first-message")

                self.assertEqual(0, proc.returncode, proc.stderr)
                message = proc.stdout
                self.assertIn(
                    f"You are a {names.get(role, role)} session of the PO session `session_po`.",
                    message,
                )
                self.assertIn("brief is what this command prints", message)
                self.assertIn("do not start without the brief", message)
                self.assertNotIn("## Session index", message)
                self.assertLess(len(message), 1_500)
                [command] = [line.strip() for line in message.splitlines() if line.startswith("    ")]
                self.assertNotIn("--first-message", command)
                # The plugin is outside this project, so the message names where to find it.
                prefix = "python3 <installed Stage plugin>/scripts/subsession_brief.py --project-root . "
                self.assertTrue(command.startswith(prefix), command)
                self.assertIn("Replace `<installed Stage plugin>`", message)
                # What the session gets by running the command is what the PO session would paste.
                rerun = subprocess.run(
                    [sys.executable, str(BRIEF), "--project-root", str(self.root)]
                    + shlex.split(command[len(prefix):]),
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                )
                self.assertEqual(0, rerun.returncode, rerun.stderr)
                self.assertEqual(pasted.stdout, rerun.stdout)

    def test_the_first_message_names_the_script_inside_the_project_by_its_path(self) -> None:
        sys.path.insert(0, str(SCRIPTS))
        import subsession_brief

        message = subsession_brief.first_message(
            SCRIPTS.parent.parent, "pm", "session_po", ["W-00000002", "--role", "pm"]
        )

        self.assertIn(
            f"    python3 {SCRIPTS.parent.name}/scripts/subsession_brief.py --project-root . "
            "W-00000002 --role pm\n",
            message,
        )
        self.assertNotIn("<installed Stage plugin>", message)

    def test_the_first_message_is_refused_when_the_brief_would_be(self) -> None:
        self.card()

        for arguments in (["W-00000099"], ["W-00000002", "--role", "verify"], ["--role", "plan"]):
            with self.subTest(arguments=arguments):
                proc = brief(self.root, *arguments, "--first-message")

                self.assertEqual((1, ""), (proc.returncode, proc.stdout))

    def test_the_topic_roles_end_with_the_index_and_stay_within_the_hook_limit(self) -> None:
        self.card()
        for number in range(100, 500):
            write(
                self.root / f".stage/official/decisions/records/DE-{number:08d}.md",
                f"---\nid: DE-{number:08d}\nstatus: promoted\n---\n\n"
                f"# DE-{number:08d} A decision with a reasonably long title, number {number}\n",
            )

        for role in ("plan", "research", "research task"):
            with self.subTest(role=role):
                proc = brief(self.root, *self.ROLE_ARGUMENTS[role])

                self.assertEqual(0, proc.returncode, proc.stderr)
                self.assertLessEqual(len(proc.stdout), 10_000)
                head, index = proc.stdout.split("\n## Session index\n", 1)
                self.assertIn("- DE-00000499 ", index)
                self.assertIn("older decisions not shown — read", index)
                # The brief's own rules are never what gets shortened.
                self.assertIn("Then wait. The PO session", head)

    def test_the_roles_of_before_the_po_layers_are_refused(self) -> None:
        """DE-00000103 removed discussion and consolidation and renamed work and planning."""
        self.card()

        for role in ("discussion", "consolidation", "work", "planning"):
            with self.subTest(role=role):
                proc = brief(self.root, "W-00000002", "--role", role, "--topic", "Anything")

                self.assertEqual(2, proc.returncode)
                self.assertEqual("", proc.stdout)
                self.assertIn("invalid choice", proc.stderr)
                # argparse quotes the choices on some Python versions and not on others.
                choices = proc.stderr.split("choose from", 1)[-1].replace("'", "")
                self.assertIn("pm, verify, plan, research", choices)

    def test_a_card_that_is_not_started_has_no_brief(self) -> None:
        proc = brief(self.root, "W-00000099")

        self.assertEqual(1, proc.returncode)
        self.assertIn("start it first", proc.stderr)


if __name__ == "__main__":
    unittest.main()
