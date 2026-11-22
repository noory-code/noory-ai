#!/usr/bin/env python3
"""Print the brief a main session sends the session that builds or judges one started card.

DE-00000094 splits the work: the main session (the orchestrator) starts the card,
holds record ids for it, and later closes it. DE-00000099 gives every other session
its role through its first message instead of a skill:

- `--role work` (default): the session builds the card, commits, pushes, and reports.
  When the card is an epic, its stories run in sub-agents inside that session and
  each story gets its own commit.
- `--role verify`: the session judges the card's success criteria and reports a
  verdict. It changes nothing; closing and merging stay with the main session.

This prints the session's whole instruction from the card, so the main session never
writes the rules into a prompt by hand. Paste stdout as the session's first message.

Usage:
    python3 stage/scripts/subsession_brief.py --project-root . W-00000001 \
        --main-session session_0123 --branch claude/w1-feature
    python3 stage/scripts/subsession_brief.py --project-root . W-00000001 \
        --main-session session_0123 --branch claude/w1-feature --role verify --commit <sha>
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
    "anything that needs the user's confirmation",
    "follow-up work candidates (do not register them)",
)
VERDICT_ITEMS = (
    "each success criterion copied exactly, `PASS` or `FAIL`, and a one-line reason that names the "
    "command you ran and what it showed, or says that you did not run it",
    "`approved: true` when every criterion passes, otherwise `approved: false`",
    "checks run and their results",
    "changed paths the executor report leaves out, and paths outside the scope it does not name",
    "anything that needs the user's confirmation",
)


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
            "will close and merge it, and a separate verification session judges each story",
            "(DE-00000094, DE-00000099).",
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
        "Then wait. The main session answers with a review result or a user decision.",
    ]
    return lines


def verify_brief(
    project_root: Path,
    card: Path,
    fields: dict[str, object],
    main_session: str,
    branch: str,
    commit: str,
) -> list[str]:
    item_id = str(fields.get("id") or "").strip()
    scope = str(fields.get("scope") or "").strip()
    acceptance = list(parse_string_list(fields.get("acceptance")))
    stories = story_cards(card)
    unit = "one Stage epic, story by story" if stories else "one Stage card"
    where = f"branch `{branch}`" if branch else "the branch you were created from"
    if commit:
        change = f"The change is commit `{commit}` on {where}."
    else:
        change = (
            f"The change is on {where}: for each card, the last commit whose message names its id."
        )

    lines = [
        f"You are a verification session of the main session `{main_session}`. You judge {unit};",
        "you change nothing. A work session built it, and the main session closes and merges it",
        "(DE-00000099).",
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
        lines += ["", "Judge each story on its own commit, then the epic's own success criteria."]
    lines += [
        "",
        "## What to judge",
        "",
        change,
        "",
        "- Read the `### Executor report` in that commit's body (`git log -1 --format=%B <commit>`).",
        "- Open every path in its `Changed paths (JSON):` line, and compare that line with",
        "  `git show --name-only --format= <commit>`.",
        "- Judge every item under the card's `## Success criteria`. When a criterion asks for a",
        "  command to be run or a behavior to be observed, run or observe it yourself; the work",
        "  session's transcript is a claim.",
        "- Judge whether `Decisions made:` names every changed path outside the scope, and why.",
    ]
    if acceptance:
        lines += ["", "Run these checks yourself:", *[f"- `{command}`" for command in acceptance]]
    lines += [
        "",
        "## Rules",
        "",
        "- Do not edit, commit, or push anything. When a check writes files, restore the working",
        "  tree (`git status --short` prints nothing) before you report.",
        "- Do not fix what you find. A failed criterion goes into your verdict.",
        LIFECYCLE_RULE,
        "- Do not write a review verdict file; `close_work.py` owns it.",
        "- Do not open or merge a pull request.",
        "- Checks that must run on another OS (for example Windows) are not yours to run: say which",
        "  ones in your verdict.",
        "",
        "## Verdict",
        "",
        f"Send the main session `{main_session}` one message"
        f"{' per story, and one for the epic,' if stories else ''} with:",
        *[f"- {item}" for item in VERDICT_ITEMS],
        "",
        "Then wait. The main session answers with a new commit to judge or a user decision.",
    ]
    return lines


def build_brief(
    project_root: Path,
    item_id: str,
    main_session: str,
    branch: str,
    role: str = "work",
    commit: str = "",
) -> str:
    if role not in ROLES:
        raise LookupError(f"{role}: unknown role; use one of {', '.join(ROLES)}")
    card = current_card_path(project_root / ".stage", item_id)
    if card is None:
        raise LookupError(f"{item_id}: no started card in .stage/work/current; start it first")
    fields = parse_frontmatter(card)
    if role == "verify":
        lines = verify_brief(project_root, card, fields, main_session, branch, commit)
    else:
        lines = work_brief(project_root, card, fields, main_session, branch)
    return "\n".join(lines) + "\n"


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
        help="work: build the card (an epic runs its stories in sub-agents). verify: judge only.",
    )
    parser.add_argument("--commit", default="", help="Verify role: the commit to judge.")
    parser.add_argument("item", help="The started card's W-id.")
    args = parser.parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    try:
        brief = build_brief(
            project_root, args.item, args.main_session, args.branch, args.role, args.commit
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
