"""The briefs that give each session of a main session its role (DE-00000094, DE-00000099)."""

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
        [sys.executable, str(BRIEF), "--project-root", str(root), "--main-session", "session_main", *args],
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

    def test_a_card_with_reserved_ids_tells_the_sub_session_how_to_take_them(self) -> None:
        self.card("reserved_ids: DE-00000008, DE-00000009\n")

        proc = brief(self.root, "W-00000002", "--branch", "claude/w2")

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn("sub-session of the main session `session_main`", out)
        self.assertIn("`.stage/work/current/W-00000002/_story.md`", out)
        self.assertIn("`.stage/decisions/pending/DE-00000007.md`", out)
        self.assertIn("`python3 -m unittest -q`", out)
        self.assertIn("reserved `DE-00000008, DE-00000009`", out)
        self.assertIn("--from-card W-00000002 <PREFIX>", out)
        self.assertIn("own branch `claude/w2`", out)
        self.assertIn("Do not run `start_work.py`, `register_work.py`, `close_work.py`", out)
        self.assertIn("send the main session `session_main` one message", out)
        self.assertIn("Do not edit the card's `## Progress` or `## Next action` section", out)

    def test_the_brief_asks_for_scope_crossings_in_the_commit_report(self) -> None:
        self.card()

        out = brief(self.root, "W-00000002").stdout

        self.assertIn("outside the scope, and why, in that report's `Decisions made:`", out)
        self.assertIn("reads only the commit's report, not your message", out)

    def test_the_brief_leaves_other_os_checks_to_the_main_session(self) -> None:
        self.card()

        out = brief(self.root, "W-00000002").stdout

        self.assertIn("Checks that must run on another OS (for example Windows) are not yours to run", out)
        self.assertIn("The main session opens the pull request and reads its CI jobs.", out)

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
        self.assertIn("work session of the main session `session_main`. You build one Stage epic", out)
        self.assertIn("the close review judges each story\n(DE-00000094, DE-00000099, DE-00000101)", out)
        self.assertNotIn("verification session", out)
        self.assertIn(
            "- W-00000002 Build it (`active`): `.stage/work/current/W-00000001/W-00000002/_story.md`",
            out,
        )
        self.assertIn("  - scope: `src/`", out)
        self.assertIn("  - check: `python3 -m unittest -q`", out)
        self.assertIn("- W-00000003 Document it (`completed`)", out)
        self.assertIn("status is not one of `archived`, `completed`, `rejected`", out)
        self.assertIn("Do not create\n  another cloud session for a story", out)
        self.assertIn("Commit each story as its own commit, with the story's id", out)
        self.assertIn("Write one `### Executor report` per story", out)
        self.assertIn("each story's id and the commit that carries its executor report", out)
        self.assertIn("Do not edit any card's `status`", out)

    def test_a_story_brief_has_no_stories_section(self) -> None:
        self.card()

        out = brief(self.root, "W-00000002").stdout

        self.assertNotIn("## Stories", out)
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
        self.assertIn("verification session of the main session `session_main`. For one Stage card", out)
        self.assertIn("observe what only a whole session can observe; you change nothing", out)
        self.assertIn("the main session closes and merges it", out)
        self.assertIn("The change is commit `abc1234` on branch `claude/w2`.", out)
        self.assertIn("`.stage/work/current/W-00000002/_story.md`", out)
        self.assertIn("`.stage/decisions/pending/DE-00000007.md`", out)
        self.assertIn(f"\n- {self.SESSION_ONLY}\n", out)
        self.assertNotIn("- The suite passes", out)
        self.assertIn("Do not edit, commit, or push anything", out)
        self.assertIn("Do not write a review verdict file", out)
        self.assertIn("Do not run `start_work.py`, `register_work.py`, `close_work.py`", out)
        self.assertIn("`held`, `did not hold`, or `could not observe`", out)
        self.assertIn("Send the main session `session_main` one message with:", out)
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
        # The work session reports which lines it used: the only record of the index's use.
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
        self.assertIn("Then wait, and push no commit until the main session answers", proc.stdout)

    def test_a_discussion_brief_needs_no_card_and_writes_no_record(self) -> None:
        proc = brief(self.root, "--role", "discussion", "--topic", "Whether  to split\nthe driver")

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn("You are a discussion session of the main session `session_main`.", out)
        self.assertIn("## Topic\n\nWhether to split the driver\n", out)
        self.assertIn("You build nothing", out)
        self.assertIn("keep the user's words", out)
        self.assertIn("do not create a card, a decision record, or\n  any record that needs a new id", out)
        self.assertIn("Do not invent a purpose or a success criterion", out)
        self.assertIn("Do not run `start_work.py`, `register_work.py`, `close_work.py`", out)
        self.assertIn("When the user says the talk is finished, send the main session", out)
        self.assertIn("- each decision the talk reached", out)
        self.assertIn("- each card the talk proposes", out)
        self.assertIn("- the ids of the records you opened because the session index below", out)
        self.assertNotIn("## Card:", out)
        self.assertNotIn("Executor report", out)

    def test_a_planning_brief_designs_what_to_achieve_and_never_how(self) -> None:
        proc = brief(self.root, "--role", "planning", "--topic", "Cut the migration into cards")

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn("You are a planning session of the main session `session_main`.", out)
        self.assertIn("You never design how a card is executed", out)
        self.assertIn("It carries no steps,\n  no file-level design, and no method.", out)
        self.assertIn("docs/PHILOSOPHY.md`", out)
        self.assertIn("- each card you propose, in the order to run them and why that order", out)
        self.assertIn("only the user's machine or a whole session can observe", out)
        self.assertIn("Do not edit, commit, or push anything", out)

    def test_a_talk_brief_lists_a_started_card_to_read_when_one_is_named(self) -> None:
        self.card()

        for role in ("discussion", "planning"):
            with self.subTest(role=role):
                out = brief(self.root, "W-00000002", "--role", role, "--topic", "Change course").stdout

                self.assertIn("- `.stage/work/current/W-00000002/_story.md`", out)
                self.assertIn("- `.stage/decisions/pending/DE-00000007.md`", out)
                self.assertNotIn("## Record ids", out)

    def test_a_talk_brief_is_refused_without_a_topic_or_for_an_unstarted_card(self) -> None:
        for role in ("discussion", "planning"):
            with self.subTest(role=role):
                no_topic = brief(self.root, "--role", role, "--topic", " ")
                no_card = brief(self.root, "W-00000099", "--role", role, "--topic", "Change course")

                self.assertEqual((1, ""), (no_topic.returncode, no_topic.stdout))
                self.assertIn(f"--role {role} needs --topic", no_topic.stderr)
                self.assertEqual((1, ""), (no_card.returncode, no_card.stdout))
                self.assertIn("start it first", no_card.stderr)

    def test_a_consolidation_brief_writes_only_the_candidate_list(self) -> None:
        proc = brief(self.root, "--role", "consolidation", "--branch", "claude/candidates")

        self.assertEqual(0, proc.returncode, proc.stderr)
        out = proc.stdout
        self.assertIn("You are a consolidation session of the main session `session_main`.", out)
        self.assertIn("skills/stage-retrospective/rule-promotion.md`", out)
        self.assertIn("every retrospective newer than that list's `through:` id", out)
        self.assertIn("Write only `.stage/state/rule-candidates.md`.", out)
        self.assertIn("branch `claude/candidates`", out)
        self.assertIn("Do not edit a retrospective, a decision record, a rule file, a skill, or a card", out)
        self.assertIn("mark a candidate `proposed: promote` and stop there", out)
        self.assertIn("- each `proposed: promote` line with the retrospectives it cites", out)

    def test_a_consolidation_brief_takes_no_card_and_a_card_role_needs_one(self) -> None:
        self.card()

        with_card = brief(self.root, "W-00000002", "--role", "consolidation")
        self.assertEqual((1, ""), (with_card.returncode, with_card.stdout))
        self.assertIn("pass no W-id", with_card.stderr)
        for role in ("work", "verify"):
            with self.subTest(role=role):
                proc = brief(self.root, "--role", role)

                self.assertEqual((1, ""), (proc.returncode, proc.stdout))
                self.assertIn(f"--role {role} needs the started card's W-id", proc.stderr)

    ROLE_ARGUMENTS = {
        "work": ["W-00000002", "--branch", "claude/w2"],
        "verify": [
            "W-00000002", "--role", "verify", "--branch", "claude/w2", "--commit", "abc1234",
            "--criterion", "A new cloud session takes the role and reports back",
        ],
        "discussion": ["--role", "discussion", "--topic", "Whether it's time to split `drive.py`"],
        "planning": ["W-00000002", "--role", "planning", "--topic", "Cut the migration"],
        "consolidation": ["--role", "consolidation", "--branch", "claude/candidates"],
    }

    def test_the_first_message_has_the_session_print_the_same_brief_itself(self) -> None:
        self.card()
        names = {"verify": "verification"}

        for role, arguments in self.ROLE_ARGUMENTS.items():
            with self.subTest(role=role):
                pasted = brief(self.root, *arguments)
                proc = brief(self.root, *arguments, "--first-message")

                self.assertEqual(0, proc.returncode, proc.stderr)
                message = proc.stdout
                self.assertIn(
                    f"You are a {names.get(role, role)} session of the main session `session_main`.",
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
                # What the session gets by running the command is what the main session would paste.
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
            SCRIPTS.parent.parent, "work", "session_main", ["W-00000002", "--role", "work"]
        )

        self.assertIn(
            f"    python3 {SCRIPTS.parent.name}/scripts/subsession_brief.py --project-root . "
            "W-00000002 --role work\n",
            message,
        )
        self.assertNotIn("<installed Stage plugin>", message)

    def test_the_first_message_is_refused_when_the_brief_would_be(self) -> None:
        self.card()

        for arguments in (["W-00000099"], ["W-00000002", "--role", "verify"], ["--role", "planning"]):
            with self.subTest(arguments=arguments):
                proc = brief(self.root, *arguments, "--first-message")

                self.assertEqual((1, ""), (proc.returncode, proc.stdout))

    def test_the_new_roles_end_with_the_index_and_stay_within_the_hook_limit(self) -> None:
        self.card()
        for number in range(100, 500):
            write(
                self.root / f".stage/official/decisions/records/DE-{number:08d}.md",
                f"---\nid: DE-{number:08d}\nstatus: promoted\n---\n\n"
                f"# DE-{number:08d} A decision with a reasonably long title, number {number}\n",
            )

        for role in ("discussion", "planning", "consolidation"):
            with self.subTest(role=role):
                proc = brief(self.root, *self.ROLE_ARGUMENTS[role])

                self.assertEqual(0, proc.returncode, proc.stderr)
                self.assertLessEqual(len(proc.stdout), 10_000)
                head, index = proc.stdout.split("\n## Session index\n", 1)
                self.assertIn("- DE-00000499 ", index)
                self.assertIn("older decisions not shown — read", index)
                # The brief's own rules are never what gets shortened.
                self.assertIn("Then wait. The main session", head)

    def test_an_unknown_role_is_refused(self) -> None:
        self.card()

        proc = brief(self.root, "W-00000002", "--role", "plan")

        self.assertEqual(2, proc.returncode)
        self.assertIn("invalid choice", proc.stderr)

    def test_a_card_that_is_not_started_has_no_brief(self) -> None:
        proc = brief(self.root, "W-00000099")

        self.assertEqual(1, proc.returncode)
        self.assertIn("start it first", proc.stderr)


if __name__ == "__main__":
    unittest.main()
