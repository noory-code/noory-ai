#!/usr/bin/env python3
"""Print the brief that gives a session of the main session its role.

DE-00000094 splits the work: the main session (the orchestrator) starts the card,
holds record ids for it, and later closes it. DE-00000099 gives every other session
its role through its first message instead of a skill:

- `--role work` (default): the session builds the card, commits, pushes, and reports.
  When the card is an epic, its stories run in sub-agents inside that session and
  each story gets its own commit.
- `--role verify`: the session observes the success criteria that only a whole
  session can observe, named with `--criterion`, and reports what it saw. It changes
  nothing and is not the gate on closing (DE-00000101): the main session writes the
  observation on the card's `## Verification`, where the close reviewer reads it.

- `--role discussion`: the session holds a long talk with the user about `--topic`
  and reports what the user chose and which cards the talk proposes.
- `--role planning`: the session designs what to achieve for `--topic` (purposes,
  success criteria, where to cut the work), never how, and reports the cards.
- `--role consolidation`: the session groups the retrospectives' rule candidates
  into `.stage/state/rule-candidates.md` and proposes which to promote (DE-00000100).

The role names are the ones a card's `## Sessions` line uses
(`operations/cloud-execution.md`, "Sessions on the card"). `work` and `verify` need a
started card. `discussion` and `planning` take one when the talk is about a started
card. `consolidation` takes none. The last three write no card and no decision
record: the main session registers what they report.

This prints the session's whole instruction from the records, so the main session
never writes the rules into a prompt by hand. A session receives it in one of two ways:

- The session prints it itself. `--first-message` prints a short first message that
  names the role and this same command without that flag; the session runs the
  command in its own checkout and reads its brief. The brief and its index together
  run to the hook's limit, more than a first message carries well.
- The main session pastes stdout as the session's first message, when the session's
  host cannot run this script.

Every brief ends with the session index a SessionStart hook gives a session on the
device (DE-00000100): Stage hooks do not run in a cloud session, so the brief is the
only way that session learns which decisions and rule candidates exist. The index is
shortened so the whole brief stays within the hook's limit.

Usage:
    python3 stage/scripts/subsession_brief.py --project-root . W-00000001 \
        --main-session session_0123 --branch claude/w1-feature
    python3 stage/scripts/subsession_brief.py --project-root . W-00000001 \
        --main-session session_0123 --branch claude/w1-feature --role verify --commit <sha> \
        --criterion "<a success criterion copied from the card>"
    python3 stage/scripts/subsession_brief.py --project-root . \
        --main-session session_0123 --branch claude/talk --role discussion --topic "<topic>"
    python3 stage/scripts/subsession_brief.py --project-root . W-00000001 \
        --main-session session_0123 --branch claude/w1-feature --first-message
"""

from __future__ import annotations

import argparse
import re
import shlex
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
STAGE_ROOT = SCRIPTS.parent
sys.path.insert(0, str(STAGE_ROOT / "hooks"))
sys.path.insert(0, str(SCRIPTS))
from stage_id_blocks import current_card_path  # noqa: E402
from stage_record_ids import RESERVED_FIELD  # noqa: E402
from stage_record_paths import record_paths  # noqa: E402
from stage_work import WORK_FINAL_STATUSES, parse_frontmatter, parse_string_list  # noqa: E402
import stage_context  # noqa: E402
from stage_memory_index import SESSION_CONTEXT_CHAR_LIMIT  # noqa: E402

CARD_ROLES = ("work", "verify")
TALK_ROLES = ("discussion", "planning")
ROLES = (*CARD_ROLES, *TALK_ROLES, "consolidation")
ROLE_NAMES = {"verify": "verification"}
RULE_CANDIDATES = ".stage/state/rule-candidates.md"
INDEX_REPORT_ITEM = (
    "the ids of the records you opened because the session index below listed them, or `none`"
)
LIFECYCLE_RULE = (
    "- Do not run `start_work.py`, `register_work.py`, `close_work.py`, or `archive_work.py`."
)
RECORD_FIELDS = ("status", "verification", "review", "retrospective", "retrospective_ref", "promotion")
REPORT_ITEMS = (
    "branch and head commit",
    "every path changed for the card",
    "checks run and their results",
    "decisions made",
    "paths changed outside the card's scope, and why",
    INDEX_REPORT_ITEM,
    "anything that needs the user's confirmation",
    "follow-up work candidates (do not register them)",
)
OBSERVATION_ITEMS = (
    "each criterion above copied exactly, then every command or action you took for it and what "
    "it showed",
    "for each criterion one of `held`, `did not hold`, or `could not observe` with the reason",
    "anything that needs the user's confirmation",
)


SESSION_INDEX_INTRO = (
    "",
    "## Session index",
    "",
    "Stage hooks do not run in this session. This is the index a SessionStart hook gives a",
    "session on the device, made from the records when this brief was written: one line per",
    "record, never its content. When a line bears on your work, open the record it names.",
)


def with_session_index(project_root: Path, lines: list[str]) -> str:
    """The brief followed by the SessionStart index, the whole within the hook's limit."""

    brief = "\n".join(lines) + "\n"
    intro = "\n".join(SESSION_INDEX_INTRO) + "\n"
    room = SESSION_CONTEXT_CHAR_LIMIT - len(brief) - len(intro) - 1
    index = stage_context.session_index(project_root, room) if room > 0 else ""
    return brief + intro + index + "\n" if index else brief


def stage_path(project_root: Path, relative: str) -> str:
    """Name a file in the Stage plugin as the sub-session will find it."""

    target = STAGE_ROOT / relative
    try:
        return target.relative_to(project_root).as_posix()
    except ValueError:
        return f"<installed Stage plugin>/{relative}"


def decision_paths(stage_root: Path, refs: str) -> list[str]:
    paths = []
    for record_id in re.findall(r"DE-\d{8}", refs):
        for root in ("decisions/pending", "official/decisions/records"):
            path = stage_root / root / f"{record_id}.md"
            if path.is_file():
                paths.append(f".stage/{root}/{record_id}.md")
                break
    return paths


def story_cards(card: Path) -> list[Path]:
    """The story cards directly inside an epic, in id order; empty for any other card."""

    if card.name != "_epic.md":
        return []
    return [
        path
        for path in record_paths(card.parent)
        if path.name == "_story.md" and path.parent.parent == card.parent
    ]


def success_criteria_text(card: Path) -> str:
    """A card's `## Success criteria` section with every run of whitespace as one space."""

    text = card.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^## Success criteria[ \t]*\n(.*?)(?=^## |\Z)", text)
    return " ".join((match.group(1) if match else "").split())


def unknown_criteria(card: Path, criteria: list[str]) -> list[str]:
    """The given criteria that neither the card nor one of an epic's stories states."""

    stated = [success_criteria_text(path) for path in (card, *story_cards(card))]
    return [
        criterion
        for criterion in criteria
        if not criterion.split() or not any(" ".join(criterion.split()) in text for text in stated)
    ]


def story_lines(project_root: Path, stories: list[Path]) -> list[str]:
    lines = []
    for story in stories:
        fields = parse_frontmatter(story)
        status = (fields.get("status") or "").strip()
        lines.append(
            f"- {(fields.get('id') or '').strip()} {(fields.get('title') or '').strip()} "
            f"(`{status}`): `{story.relative_to(project_root).as_posix()}`"
        )
        lines.append(f"  - scope: `{(fields.get('scope') or '').strip()}`")
        lines += [f"  - check: `{command}`" for command in parse_string_list(fields.get("acceptance"))]
    return lines


def read_first_entries(
    project_root: Path, card: Path | None, decisions: list[str], last: str
) -> list[str]:
    read_first = ["the project's `CLAUDE.md` or `AGENTS.md`, whichever exists"]
    if card is None:
        return [*read_first, f"`{stage_path(project_root, last)}`"]
    stage_root = project_root / ".stage"
    ancestors = [
        parent_card.relative_to(project_root).as_posix()
        for directory in reversed(card.parent.parents)
        if stage_root / "work" / "current" in directory.parents
        for parent_card in (directory / "_epic.md", directory / "_story.md")
        if parent_card.is_file() and parent_card != card
    ]
    if card.name != "_story.md" and card.name != "_epic.md":
        ancestors += [
            sibling.relative_to(project_root).as_posix()
            for sibling in (card.parent / "_epic.md", card.parent / "_story.md")
            if sibling.is_file()
        ]
    read_first += [f"`{path}` (ancestor)" for path in ancestors]
    read_first.append(f"`{card.relative_to(project_root).as_posix()}`")
    read_first += [f"`{path}`" for path in decisions]
    read_first.append(f"`{stage_path(project_root, last)}`")
    return read_first


def work_brief(
    project_root: Path, card: Path, fields: dict[str, object], main_session: str, branch: str
) -> list[str]:
    item_id = str(fields.get("id") or "").strip()
    scope = str(fields.get("scope") or "").strip()
    acceptance = list(parse_string_list(fields.get("acceptance")))
    reserved = str(fields.get(RESERVED_FIELD) or "").strip()
    stories = story_cards(card)
    cloud_doc = stage_path(project_root, "operations/cloud-execution.md")

    if stories:
        lines = [
            f"You are a work session of the main session `{main_session}`. You build one Stage epic;",
            "its stories run in sub-agents inside this session. The main session started the epic and",
            "will close and merge it, and the close review judges each story",
            "(DE-00000094, DE-00000099, DE-00000101).",
        ]
    else:
        lines = [
            f"You are a sub-session of the main session `{main_session}`. You build one Stage card;",
            "the main session started it and will review, close, and merge it (DE-00000094).",
        ]
    lines += [
        "",
        f"## Card: {item_id} {str(fields.get('title') or '').strip()}".rstrip(),
        "",
        "Read first, in order:",
        *[
            f"- {entry}"
            for entry in read_first_entries(
                project_root,
                card,
                decision_paths(project_root / ".stage", str(fields.get("decision_refs") or "")),
                "operations/cloud-execution.md",
            )
        ],
        "",
        f"Scope: `{scope}`. Work outside it when the card's purpose needs it, and report each crossing.",
    ]
    if acceptance:
        lines += ["", "Run these checks before reporting:", *[f"- `{command}`" for command in acceptance]]
    if stories:
        lines += [
            "",
            "## Stories",
            "",
            *story_lines(project_root, stories),
            "",
            f"- Build every story whose status is not one of `{'`, `'.join(sorted(WORK_FINAL_STATUSES))}`.",
            "- Give each story to a sub-agent of this session, in this working folder. Do not create",
            "  another cloud session for a story. Hand the sub-agent the story card, this epic card,",
            "  and the rules below.",
            "- Run two stories at the same time only when their scopes share no path; otherwise run",
            "  them one after another in id order.",
            "- Run each story's checks yourself after its sub-agent finishes; a sub-agent's summary",
            "  is a claim.",
            "- Commit each story as its own commit, with the story's id in the commit message.",
        ]
    lines += ["", "## Record ids", ""]
    if reserved:
        lines += [
            f"The main session reserved `{reserved}` for this card. Take each id with",
            f"`python3 {stage_path(project_root, 'scripts/stage_record_ids.py')} --project-root . "
            f"--from-card {item_id} <PREFIX>` and never pick a number any other way.",
        ]
    else:
        lines += [
            "No ids are reserved for this card. Do not create records that need a new id (decisions,",
            "observations, cards); put what you would have recorded in your report instead.",
        ]
    card_word = "any card's" if stories else "the card's"
    lines += [
        "",
        "## Rules",
        "",
        LIFECYCLE_RULE,
        f"- Do not edit {card_word} `{'`, `'.join(RECORD_FIELDS)}` fields.",
        f"- Do not edit {card_word} `## Progress` or `## Next action` section; the main session writes",
        "  them from your report.",
        "- Do not open or merge a pull request.",
        f"- Commit and push only to your own branch{f' `{branch}`' if branch else ''}.",
    ]
    if stories:
        lines += [
            "- Write one `### Executor report` per story, in the body of that story's commit, as",
            f"  `{cloud_doc}` describes; its",
            "  `Changed paths (JSON):` lists every path changed for that story, across all its commits.",
        ]
    else:
        lines += [
            "- Write the `### Executor report` in the body of your last commit, as",
            f"  `{cloud_doc}` describes; its",
            "  `Changed paths (JSON):` lists every path you changed for the card, across all commits.",
        ]
    lines += [
        "- Name every path you changed outside the scope, and why, in that report's `Decisions made:`",
        "  line too. The reviewer reads only the commit's report, not your message (W-00000382).",
        "- Checks that must run on another OS (for example Windows) are not yours to run: say which",
        "  ones in your report. The main session opens the pull request and reads its CI jobs.",
        "- Do not write a `- Checked` or `- User verdict` line on the card's `## Verification`; the",
        f"  close reviewer judges from them (`{stage_path(project_root, 'operations/review.md')}`,",
        "  \"A check recorded on the card\").",
        "",
        "## Report",
        "",
        f"When the change is pushed, send the main session `{main_session}` one message with:",
    ]
    if stories:
        lines.append("- each story's id and the commit that carries its executor report")
    lines += [
        *[f"- {item}" for item in REPORT_ITEMS],
        "",
        "Then wait, and push no commit until the main session answers: it reviews the commit you",
        "reported. The main session answers with a review result or a user decision.",
    ]
    return lines


def verify_brief(
    project_root: Path,
    card: Path,
    fields: dict[str, object],
    main_session: str,
    branch: str,
    commit: str,
    criteria: list[str],
) -> list[str]:
    item_id = str(fields.get("id") or "").strip()
    scope = str(fields.get("scope") or "").strip()
    stories = story_cards(card)
    unit = "one Stage epic" if stories else "one Stage card"
    where = f"branch `{branch}`" if branch else "the branch you were created from"
    if commit:
        change = f"The change is commit `{commit}` on {where}."
    else:
        change = (
            f"The change is on {where}: for each card, the last commit whose message names its id."
        )

    lines = [
        f"You are a verification session of the main session `{main_session}`. For {unit} you",
        "observe what only a whole session can observe; you change nothing. A work session built",
        "it, and the main session closes and merges it (DE-00000099).",
        "",
        "You are not the gate on closing (DE-00000101). The main session writes what you observed",
        "on the card's `## Verification`; the close reviewer reads it there and judges every",
        "success criterion.",
        "",
        f"## Card: {item_id} {str(fields.get('title') or '').strip()}".rstrip(),
        "",
        "Read first, in order:",
        *[
            f"- {entry}"
            for entry in read_first_entries(
                project_root,
                card,
                decision_paths(project_root / ".stage", str(fields.get("decision_refs") or "")),
                "operations/review.md",
            )
        ],
        "",
        f"Scope: `{scope}`.",
    ]
    if stories:
        lines += ["", "## Stories", "", *story_lines(project_root, stories)]
    lines += [
        "",
        "## What to observe",
        "",
        change,
        "",
        "Only a session that does the thing itself can judge these success criteria:",
        "",
        *[f"- {' '.join(criterion.split())}" for criterion in criteria],
        "",
        "- Do what each criterion describes yourself, in this session. The work session's",
        "  transcript and the `### Executor report` in the commit body are claims.",
        "- Keep each command or action and what it showed; the main session copies them onto the",
        "  card.",
        "- Leave the card's other success criteria alone: the close reviewer judges them.",
        "",
        "## Rules",
        "",
        "- Do not edit, commit, or push anything. When a command writes files, restore the working",
        "  tree (`git status --short` prints nothing) before you report.",
        "- Do not fix what you find. A criterion that did not hold goes into your observation.",
        LIFECYCLE_RULE,
        "- Do not write a review verdict file; the close reviewer owns it.",
        "- Do not open or merge a pull request.",
        "- What must be observed on another OS (for example Windows) is not yours to observe: say",
        "  which criteria in your observation.",
        "",
        "## Observation",
        "",
        f"Send the main session `{main_session}` one message with:",
        *[f"- {item}" for item in OBSERVATION_ITEMS],
        "",
        "Then wait. The main session answers with a new commit to observe or a user decision.",
    ]
    return lines


TALK_PARTS = {
    "discussion": {
        "opening": (
            "You hold a long talk with the user about new work or a change of direction, so that",
            "the main session's context does not carry it (DE-00000099). You build nothing; the",
            "talk ends in what the user chose and the cards it proposes.",
        ),
        "last": "operations/before.md",
        "rules": (
            "- Talk with the user in this session's own conversation. For each choice the user",
            "  makes, keep the user's words.",
        ),
        "when": "When the user says the talk is finished",
        "report": (
            "each decision the talk reached: the question, the options that were weighed, and what "
            "the user chose, in the user's words",
            "each card the talk proposes: title, purpose, success criteria, what is included and "
            "excluded, and the user's words that back it",
            "what the user left undecided",
        ),
    },
    "planning": {
        "opening": (
            "You design what to achieve: purposes, success criteria, and where to cut the work",
            "into cards (DE-00000099). You never design how a card is executed; its executor",
            "chooses that. You build nothing.",
        ),
        "last": "docs/PHILOSOPHY.md",
        "rules": (
            "- A proposed card carries a purpose, success criteria that someone independent can",
            "  judge, what is included and excluded, and the user's choices. It carries no steps,",
            "  no file-level design, and no method.",
        ),
        "when": "When the plan is complete",
        "report": (
            "each card you propose, in the order to run them and why that order: title, kind, "
            "purpose, success criteria, what is included and excluded",
            "each success criterion that only the user's machine or a whole session can observe",
            "each purpose or success criterion the user stated or confirmed, in the user's words",
        ),
    },
}
NO_RECORD_RULES = (
    "- Do not edit, commit, or push anything, and do not create a card, a decision record, or",
    "  any record that needs a new id: the main session registers what you report.",
    "- Do not invent a purpose or a success criterion. When the records and the user do not",
    "  state one, ask the user in this session.",
    LIFECYCLE_RULE,
    "- Do not open or merge a pull request.",
)


def talk_brief(
    project_root: Path, role: str, card: Path | None, main_session: str, topic: str
) -> list[str]:
    """The brief of a discussion or planning session; `card` only adds what to read."""

    parts = TALK_PARTS[role]
    fields = parse_frontmatter(card) if card else {}
    decisions = decision_paths(project_root / ".stage", str(fields.get("decision_refs") or ""))
    return [
        f"You are a {role} session of the main session `{main_session}`.",
        *parts["opening"],
        "",
        "## Topic",
        "",
        topic,
        "",
        "Read first, in order:",
        *[
            f"- {entry}"
            for entry in read_first_entries(project_root, card, decisions, str(parts["last"]))
        ],
        "",
        "## Rules",
        "",
        *parts["rules"],
        *NO_RECORD_RULES,
        "",
        "## Report",
        "",
        f"{parts['when']}, send the main session `{main_session}` one message with:",
        *[f"- {item}" for item in parts["report"]],
        f"- {INDEX_REPORT_ITEM}",
        "- anything that needs the user's confirmation",
        "",
        "Then wait. The main session answers with what it registered or a question.",
    ]


def consolidation_brief(project_root: Path, main_session: str, branch: str) -> list[str]:
    promotion_doc = stage_path(project_root, "skills/stage-retrospective/rule-promotion.md")
    return [
        f"You are a consolidation session of the main session `{main_session}`. You group the rule",
        "candidates the retrospectives state into one list and propose which to promote. You",
        "promote nothing (DE-00000100).",
        "",
        "Read first, in order:",
        "- the project's `CLAUDE.md` or `AGENTS.md`, whichever exists",
        f"- `{promotion_doc}`;",
        '  its "Consolidating candidates" section owns the list\'s place and format',
        f"- `{RULE_CANDIDATES}`, when it exists",
        "- every retrospective newer than that list's `through:` id; with no list, every",
        "  retrospective that has a `## Rule candidate` section",
        "",
        "## Rules",
        "",
        f"- Write only `{RULE_CANDIDATES}`. Commit and push it only to your own",
        f"  branch{f' `{branch}`' if branch else ''}.",
        "- Do not edit a retrospective, a decision record, a rule file, a skill, or a card.",
        "- Do not promote anything: mark a candidate `proposed: promote` and stop there.",
        LIFECYCLE_RULE,
        "- Do not open or merge a pull request.",
        "",
        "## Report",
        "",
        f"When the list is pushed, send the main session `{main_session}` one message with:",
        "- branch and head commit",
        "- how many retrospectives you read and how many candidates the list holds",
        "- each `proposed: promote` line with the retrospectives it cites",
        "- each candidate left out because a rule file already states it, and that file",
        f"- {INDEX_REPORT_ITEM}",
        "- anything that needs the user's confirmation",
        "",
        "Then wait. The main session merges the list and shows the user each proposal.",
    ]


def first_message(project_root: Path, role: str, main_session: str, arguments: list[str]) -> str:
    """The short first message that has a session print its own brief with this script."""

    script = stage_path(project_root, "scripts/subsession_brief.py")
    installed = script.startswith("<")
    command = f"python3 {script if installed else shlex.quote(script)} --project-root . "
    lines = [
        f"You are a {ROLE_NAMES.get(role, role)} session of the main session `{main_session}`. Your",
        "brief is what this command prints. Run it in the root of the checkout you were created",
        "in, read all of its output, and follow it:",
        "",
        f"    {command}{shlex.join(arguments)}",
        "",
        "Use `python` where the host has no `python3`. When the command fails, send its error",
        f"text to the main session `{main_session}` and wait; do not start without the brief.",
    ]
    if installed:
        lines.append(
            "Replace `<installed Stage plugin>` with the folder of the Stage plugin on this host."
        )
    return "\n".join(lines) + "\n"


def build_brief(
    project_root: Path,
    item_id: str,
    main_session: str,
    branch: str,
    role: str = "work",
    commit: str = "",
    criteria: list[str] | None = None,
    topic: str = "",
) -> str:
    if role not in ROLES:
        raise LookupError(f"{role}: unknown role; use one of {', '.join(ROLES)}")
    if role == "consolidation":
        if item_id:
            raise LookupError("a consolidation session reads retrospectives, not a card: pass no W-id")
        return with_session_index(project_root, consolidation_brief(project_root, main_session, branch))
    if role in CARD_ROLES and not item_id:
        raise LookupError(f"--role {role} needs the started card's W-id")
    card = current_card_path(project_root / ".stage", item_id) if item_id else None
    if item_id and card is None:
        raise LookupError(f"{item_id}: no started card in .stage/work/current; start it first")
    if role in TALK_ROLES:
        topic = " ".join(topic.split())
        if not topic:
            raise LookupError(f"--role {role} needs --topic: one sentence that says what it is about")
        return with_session_index(
            project_root, talk_brief(project_root, role, card, main_session, topic)
        )
    assert card is not None
    fields = parse_frontmatter(card)
    if role == "verify":
        criteria = criteria or []
        if not criteria:
            raise LookupError(
                "a verification session is started only for success criteria that only a whole "
                "session can observe (DE-00000101): name each with --criterion, copied from the "
                "card. The close review judges every other criterion without one"
            )
        unknown = unknown_criteria(card, criteria)
        if unknown:
            raise LookupError(
                f"{item_id}: not under `## Success criteria` of the card or its stories: "
                + "; ".join(repr(criterion) for criterion in unknown)
            )
        lines = verify_brief(project_root, card, fields, main_session, branch, commit, criteria)
    else:
        lines = work_brief(project_root, card, fields, main_session, branch)
    return with_session_index(project_root, lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--main-session", required=True, help="Session id the report goes to.")
    parser.add_argument(
        "--branch",
        default="",
        help=(
            "Work and consolidation roles: the session's own branch. Verify role: the branch "
            "that holds the change."
        ),
    )
    parser.add_argument(
        "--role",
        choices=ROLES,
        default="work",
        help=(
            "work: build the card (an epic runs its stories in sub-agents). "
            "verify: observe the --criterion items only. "
            "discussion: talk with the user about --topic. "
            "planning: design what to achieve for --topic. "
            "consolidation: group the retrospectives' rule candidates into one list."
        ),
    )
    parser.add_argument(
        "--topic",
        default="",
        help="Discussion and planning roles, required: one sentence that says what it is about.",
    )
    parser.add_argument(
        "--first-message",
        action="store_true",
        help=(
            "Print, instead of the brief, the short first message that has the session print "
            "its own brief with this command. The brief is still built, so a refusal shows here."
        ),
    )
    parser.add_argument("--commit", default="", help="Verify role: the commit to observe.")
    parser.add_argument(
        "--criterion",
        action="append",
        default=[],
        help=(
            "Verify role, repeatable and required: a success criterion, copied from the card or "
            "one of its stories, that only a whole session can observe."
        ),
    )
    parser.add_argument(
        "item",
        nargs="?",
        default="",
        help=(
            "The started card's W-id. Required for work and verify, optional for discussion "
            "and planning, refused for consolidation."
        ),
    )
    args = parser.parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    try:
        brief = build_brief(
            project_root,
            args.item,
            args.main_session,
            args.branch,
            args.role,
            args.commit,
            args.criterion,
            args.topic,
        )
    except LookupError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.first_message:
        arguments = [args.item] if args.item else []
        arguments += ["--main-session", args.main_session, "--role", args.role]
        for flag, value in (("--branch", args.branch), ("--commit", args.commit), ("--topic", args.topic)):
            arguments += [flag, value] if value else []
        for criterion in args.criterion:
            arguments += ["--criterion", criterion]
        brief = first_message(project_root, args.role, args.main_session, arguments)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(brief)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
