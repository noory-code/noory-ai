#!/usr/bin/env python3
"""Print the brief a main session sends a sub-session that builds one started card.

DE-00000094 splits the work: the main session starts the card, holds record ids
for it, and later closes it; the sub-session only builds, commits, pushes, and
reports. This prints the sub-session's whole instruction from the card, so the
main session never writes the rules into a prompt by hand. Paste stdout as the
sub-session's first message.

Usage:
    python3 stage/scripts/subsession_brief.py --project-root . W-00000001 \
        --main-session session_0123 --branch claude/w1-feature
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
from stage_work import parse_frontmatter, parse_string_list  # noqa: E402

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


def build_brief(
    project_root: Path, item_id: str, main_session: str, branch: str
) -> str:
    stage_root = project_root / ".stage"
    card = current_card_path(stage_root, item_id)
    if card is None:
        raise LookupError(f"{item_id}: no started card in .stage/work/current; start it first")
    fields = parse_frontmatter(card)
    card_rel = card.relative_to(project_root).as_posix()
    title = (fields.get("title") or "").strip()
    scope = (fields.get("scope") or "").strip()
    acceptance = list(parse_string_list(fields.get("acceptance")))
    reserved = (fields.get(RESERVED_FIELD) or "").strip()
    decisions = decision_paths(stage_root, fields.get("decision_refs") or "")

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
    read_first.append(f"`{card_rel}`")
    read_first += [f"`{path}`" for path in decisions]
    read_first.append(f"`{stage_path(project_root, 'operations/cloud-execution.md')}`")

    lines = [
        f"You are a sub-session of the main session `{main_session}`. You build one Stage card;",
        "the main session started it and will review, close, and merge it (DE-00000094).",
        "",
        f"## Card: {item_id} {title}".rstrip(),
        "",
        "Read first, in order:",
        *[f"- {entry}" for entry in read_first],
        "",
        f"Scope: `{scope}`. Work outside it when the card's purpose needs it, and report each crossing.",
    ]
    if acceptance:
        lines += ["", "Run these checks before reporting:", *[f"- `{command}`" for command in acceptance]]
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
    lines += [
        "",
        "## Rules",
        "",
        "- Do not run `start_work.py`, `register_work.py`, `close_work.py`, or `archive_work.py`.",
        f"- Do not edit the card's `{'`, `'.join(RECORD_FIELDS)}` fields.",
        "- Do not open or merge a pull request.",
        f"- Commit and push only to your own branch{f' `{branch}`' if branch else ''}.",
        "- Write the `### Executor report` in the body of your last commit, as",
        f"  `{stage_path(project_root, 'operations/cloud-execution.md')}` describes; its",
        "  `Changed paths (JSON):` lists every path you changed for the card, across all commits.",
        "",
        "## Report",
        "",
        f"When the change is pushed, send the main session `{main_session}` one message with:",
        *[f"- {item}" for item in REPORT_ITEMS],
        "",
        "Then wait. The main session answers with a review result or a user decision.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--main-session", required=True, help="Session id the report goes to.")
    parser.add_argument("--branch", default="", help="The sub-session's own branch, when known.")
    parser.add_argument("item", help="The started card's W-id.")
    args = parser.parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    try:
        brief = build_brief(project_root, args.item, args.main_session, args.branch)
    except LookupError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(brief)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
