#!/usr/bin/env python3
"""Print the brief a main session sends the session that builds or judges one started card.

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

This prints the session's whole instruction from the card, so the main session never
writes the rules into a prompt by hand. Paste stdout as the session's first message.

Either brief ends with the session index a SessionStart hook gives a session on the
device (DE-00000100): Stage hooks do not run in a cloud session, so the brief is the
only way that session learns which decisions and rule candidates exist. The index is
shortened so the whole brief stays within the hook's limit.

Usage:
    python3 stage/scripts/subsession_brief.py --project-root . W-00000001 \
        --main-session session_0123 --branch claude/w1-feature
    python3 stage/scripts/subsession_brief.py --project-root . W-00000001 \
        --main-session session_0123 --branch claude/w1-feature --role verify --commit <sha> \
        --criterion "<a success criterion copied from the card>"
"""

from __future__ import annotations

import argparse
import re
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

ROLES = ("work", "verify")
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
    "the ids of the records you opened because the session index below listed them, or `none`",
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


def read_first_entries(project_root: Path, card: Path, decisions: list[str], last: str) -> list[str]:
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
    read_first = ["the project's `CLAUDE.md` or `AGENTS.md`, whichever exists"]
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


def build_brief(
    project_root: Path,
    item_id: str,
    main_session: str,
    branch: str,
    role: str = "work",
    commit: str = "",
    criteria: list[str] | None = None,
) -> str:
    if role not in ROLES:
        raise LookupError(f"{role}: unknown role; use one of {', '.join(ROLES)}")
    card = current_card_path(project_root / ".stage", item_id)
    if card is None:
        raise LookupError(f"{item_id}: no started card in .stage/work/current; start it first")
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
        help="Work role: the session's own branch. Verify role: the branch that holds the change.",
    )
    parser.add_argument(
        "--role",
        choices=ROLES,
        default="work",
        help=(
            "work: build the card (an epic runs its stories in sub-agents). "
            "verify: observe the --criterion items only."
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
    parser.add_argument("item", help="The started card's W-id.")
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
        )
    except LookupError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(brief)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
