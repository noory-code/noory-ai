#!/usr/bin/env python3
"""Scaffold a Stage work item and its active.md index row.

The human plans and confirms scope; this turns that decision into the files so
the enum/index bookkeeping manual edits get wrong is done once, correctly.
`.stage/` is not governed source, so this write passes no registration/intent
gate — the value is correctness, not gate-bypass.

Usage:
    register_work.py --project-root . --title "..." --kind feature \
        --scope "stage/skills, stage/scripts" [--venue claude] [--owner Claude] \
        [--purpose "..."] [--id W-00000008]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from lifecycle_paths import (  # noqa: E402
    milestone_record_roots,
    relative_record_link,
    v4_lifecycle_paths,
)
from stage_paths import (  # noqa: E402
    ACTIVE_TOPOLOGY_V4,
    active_topology,
    load_review_config,
    load_venue_routing,
    resolve_review_command,
)
from stage_work import (  # noqa: E402
    VENUE_SPLIT_TOKEN,
    venue_exception_error,
)

ID_RE = re.compile(r"^W-(\d{8})$")
MILESTONE_RE = re.compile(r"^M-\d{8}$")
_PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_TEMPLATE = _PLUGIN_ROOT.joinpath(
    "templates", "project-stage", "present", "work", "items", "_template.md"
)


def set_field(text: str, field: str, value: str) -> str:
    return re.sub(
        rf"^({re.escape(field)}:)[ \t]*.*$", rf"\g<1> {value}", text, count=1, flags=re.MULTILINE
    )


def set_optional_field(text: str, field: str, value: str, *, after: str) -> str:
    """Set an optional scalar field, inserting it only when a value was supplied."""

    if not value:
        return text
    if re.search(rf"^{re.escape(field)}:", text, re.MULTILINE):
        return set_field(text, field, value)
    match = re.search(rf"^{re.escape(after)}:[^\n]*", text, re.MULTILINE)
    if match is None:
        raise ValueError(f"template has no `{after}:` anchor for `{field}:`")
    return text[: match.end()] + f"\n{field}: {value}" + text[match.end() :]


def _v4_template(template_source: str) -> Path:
    return _PLUGIN_ROOT / "templates" / "v4" / template_source


def existing_numbers(stage_root: Path) -> set[int]:
    numbers: set[int] = set()
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        paths = v4_lifecycle_paths()
        bases = (paths.planned_cards, paths.current_cards, paths.archive_cards)
    else:
        bases = (
            Path("present", "work", "items").as_posix(),
            Path("past", "work", "archive", "items").as_posix(),
            Path("future", "backlog", "items").as_posix(),
        )
    for base in bases:
        for path in (stage_root / base).glob("W-*.md"):
            match = ID_RE.match(path.stem)
            if match:
                numbers.add(int(match.group(1)))
    return numbers


def fill_item(
    template: str,
    *,
    item_id: str,
    title: str,
    kind: str,
    venue: str,
    scope: str,
    purpose: str,
    review: bool,
    decision: str = "",
    milestone: str = "",
) -> str:
    text = template.replace("W-00000000 Title", f"{item_id} {title}")
    text = set_field(text, "id", item_id)
    text = set_field(text, "title", title)
    text = set_field(text, "kind", kind)
    text = set_field(text, "venue", venue)
    text = set_optional_field(text, "milestone", milestone, after="parent")
    text = set_field(text, "scope", scope)
    if review:
        text = set_field(text, "review", "pending")  # opt this item into a required review
    if decision:
        text = set_field(text, "decision_refs", decision)
    if purpose:
        text = text.replace("## Purpose\n\n", f"## Purpose\n\n{purpose}\n", 1)
    return text


def active_row(
    item_id: str,
    kind: str,
    venue: str,
    purpose: str,
    owner: str,
    item_link: str | None = None,
) -> str:
    # Link form is required: audit_stage matches items via the [..](items/<id>.md) link, not a bare id.
    summary = (purpose.splitlines()[0] if purpose else "").strip()[:60]
    link = item_link or f"items/{item_id}.md"
    return f"| {item_id} | {kind} | {venue} | {summary} | active | {owner} | [{link}]({link}) |"


def insert_table_row(text: str, row: str) -> str:
    """Insert a row after the final data row in the first Markdown table."""
    lines = text.splitlines()
    separator_index = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.lstrip().startswith("|")
            and lines[index - 1].lstrip().startswith("|")
            and all(
                re.fullmatch(r":?-{3,}:?", cell.strip())
                for cell in line.strip().strip("|").split("|")
            )
        ),
        None,
    )
    if separator_index is None:
        body = text.rstrip("\n")
        return f"{body}\n{row}\n" if body else f"{row}\n"

    insertion_index = separator_index + 1
    while insertion_index < len(lines) and lines[insertion_index].lstrip().startswith("|"):
        insertion_index += 1
    lines.insert(insertion_index, row)
    return "\n".join(lines) + "\n"


def ensure_active_row(
    active_path: Path,
    item_id: str,
    row: str,
    item_link: str | None = None,
) -> None:
    """Insert the row if the item is not already indexed. Re-run reconciles:
    it never duplicates and never rewrites an existing row.

    Index membership is eventually-consistent: this read-modify-write can lose a
    row if two windows register at once. The id allocation (O_EXCL) is the atomic
    part; a dropped row is self-detected by the audit (INDEX003) and repaired by a
    re-run."""
    text = active_path.read_text(encoding="utf-8") if active_path.exists() else ""
    link = item_link or f"items/{item_id}.md"
    if re.search(rf"\({re.escape(link)}\)", text):
        return
    active_path.write_text(insert_table_row(text, row), encoding="utf-8")


def create_item_atomic(items_dir: Path, numbers: set[int], content_for) -> str:
    """Allocate the next free id with O_EXCL so two concurrent windows never
    take the same number. On a race (file appeared between scan and create),
    step to the next candidate and retry."""
    candidate = (max(numbers) + 1) if numbers else 1
    for _ in range(1000):
        item_id = f"W-{candidate:08d}"
        path = items_dir / f"{item_id}.md"
        try:
            with open(path, "x", encoding="utf-8") as handle:
                handle.write(content_for(item_id))
            return item_id
        except FileExistsError:
            candidate += 1
    raise RuntimeError("could not allocate a free work-item id")


_BACKLOG_TEMPLATE = (
    _PLUGIN_ROOT.joinpath(
        "templates", "project-stage", "future", "backlog", "items", "_template.md"
    )
)


def backlog_row(
    item_id: str,
    title: str,
    kind: str,
    priority: str,
    item_link: str | None = None,
) -> str:
    link = item_link or f"items/{item_id}.md"
    return (
        f"| {item_id} | {title} | {kind} | captured | {priority} |  | "
        f"[{link}]({link}) |"
    )


def ensure_backlog_row(
    index_path: Path,
    item_id: str,
    row: str,
    item_link: str | None = None,
) -> None:
    text = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    link = item_link or f"items/{item_id}.md"
    if re.search(rf"\({re.escape(link)}\)", text):
        return
    index_path.write_text(insert_table_row(text, row), encoding="utf-8")


def register_backlog_card(stage_root: Path, args) -> int:
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        paths = v4_lifecycle_paths()
        backlog_relative = paths.planned_cards
        index_relative = paths.planned_index
        backlog_dir = stage_root / backlog_relative
        index_path = stage_root / index_relative
        template_path = _v4_template(paths.planned_template)
    else:
        backlog_relative = Path("future", "backlog", "items").as_posix()
        index_relative = Path("future", "backlog", "index.md").as_posix()
        backlog_dir = stage_root / "future" / "backlog" / "items"
        index_path = stage_root / "future" / "backlog" / "index.md"
        template_path = _BACKLOG_TEMPLATE
    if not backlog_dir.exists():
        print(f"Stage backlog dir not found: {backlog_dir}", file=sys.stderr)
        return 2
    if not template_path.exists():
        print(f"Planned-card template not found: {template_path}", file=sys.stderr)
        return 2
    template = template_path.read_text(encoding="utf-8")

    def content_for(item_id: str) -> str:
        text = template.replace("W-00000000 Title", f"{item_id} {args.title}")
        text = set_field(text, "id", item_id)
        text = set_field(text, "title", args.title)
        text = set_field(text, "kind", args.kind)
        text = set_optional_field(text, "milestone", args.milestone, after="parent")
        if args.priority:
            text = set_field(text, "priority", args.priority)
        if args.purpose:
            text = text.replace("## Purpose\n\n", f"## Purpose\n\n{args.purpose}\n", 1)
        return text

    item_id = create_item_atomic(backlog_dir, existing_numbers(stage_root), content_for)
    item_link = relative_record_link(
        index_relative, f"{backlog_relative}/{item_id}.md"
    )
    ensure_backlog_row(
        index_path,
        item_id,
        backlog_row(item_id, args.title, args.kind, args.priority, item_link),
        item_link,
    )
    print(f"{item_id}: captured (planned card in {backlog_relative})")
    return 0


def milestone_decision_chain_is_open(stage_root: Path, milestone_path: Path) -> bool:
    """Conservative C5 boundary for the decision-chain evaluator delivered by C6.

    C5 can discover milestone records but cannot truthfully classify pursuit or
    closure before C6 owns those transition semantics. Returning false prevents
    the skill from asking a milestone question on an unproved premise.
    """

    del stage_root, milestone_path
    return False


def count_open_milestones(stage_root: Path) -> int:
    """Count milestones whose decision chain proves pursuit without closure."""

    if active_topology(stage_root) != ACTIVE_TOPOLOGY_V4:
        return 0
    paths = (
        path
        for relative in milestone_record_roots()
        for path in sorted((stage_root / relative).glob("M-*.md"))
        if path.name not in {"README.md", "_template.md"}
    )
    return sum(milestone_decision_chain_is_open(stage_root, path) for path in paths)


def _run_open_milestone_count_mode(argv: list[str]) -> int | None:
    """Keep the established required registration arguments byte-for-byte intact."""

    if "--count-open-milestones" not in argv:
        return None
    parser = argparse.ArgumentParser(description="Count open Stage milestones.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--count-open-milestones", action="store_true", required=True)
    args = parser.parse_args(argv)
    stage_root = Path(args.project_root).expanduser().resolve() / ".stage"
    print(count_open_milestones(stage_root))
    return 0


def main() -> int:
    count_result = _run_open_milestone_count_mode(sys.argv[1:])
    if count_result is not None:
        return count_result

    parser = argparse.ArgumentParser(description="Scaffold a Stage work item + active.md row.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--title", required=True)
    parser.add_argument("--kind", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--venue", default="")
    parser.add_argument("--owner", default="Claude")
    parser.add_argument("--purpose", default="")
    parser.add_argument(
        "--milestone",
        action="append",
        default=[],
        help="Optional single milestone attribution (M-NNNNNNNN).",
    )
    parser.add_argument("--id", default=None, help="Explicit W-NNNNNNNN; default allocates the next free id.")
    parser.add_argument("--review", action="store_true", help="Require a review (review: pending) before this item can complete.")
    parser.add_argument(
        "--decision",
        default="",
        help="Decision record id (DE-*) authorizing a venue-policy exception "
        "(decided/promoted with `authorizes: venue_exception`); stamped into decision_refs.",
    )
    parser.add_argument(
        "--backlog",
        action="store_true",
        help="Capture a planned card in future/backlog/items (status captured) instead of "
        "starting work in present; the venue/split contract applies later, at start_work.",
    )
    parser.add_argument(
        "--priority",
        default="",
        help="Optional ordering hint for a planned card (shown in the backlog index).",
    )
    args = parser.parse_args()

    stage_root = Path(args.project_root).expanduser().resolve() / ".stage"
    if len(args.milestone) > 1:
        print("--milestone accepts at most one M-NNNNNNNN value", file=sys.stderr)
        return 2
    args.milestone = args.milestone[0] if args.milestone else ""
    if args.milestone and not MILESTONE_RE.fullmatch(args.milestone):
        print(
            f"--milestone must look like M-00000001, got {args.milestone}",
            file=sys.stderr,
        )
        return 2

    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        paths = v4_lifecycle_paths()
        planned_relative = paths.planned_cards
        items_relative = paths.current_cards
        active_relative = paths.active_index
        archive_relative = paths.archive_cards
        items_dir = stage_root / items_relative
        active_path = stage_root / active_relative
        template_path = _v4_template(paths.current_template)
    else:
        planned_relative = ""
        items_relative = Path("present", "work", "items").as_posix()
        active_relative = Path("present", "work", "active.md").as_posix()
        archive_relative = Path("past", "work", "archive", "items").as_posix()
        items_dir = stage_root / "present" / "work" / "items"
        active_path = stage_root / "present" / "work" / "active.md"
        template_path = _TEMPLATE

    # A planned card (DE-00000007) is captured, not started: it waits in
    # future/backlog/items and the venue/split contract applies when
    # scripts/start_work.py moves it to present.
    if args.backlog:
        return register_backlog_card(stage_root, args)

    # Role policy (DE-00000004/DE-00000005): derive an omitted venue from the
    # declared kind -> venue routing. A split-marked kind or a
    # policy-contradicting venue registers only with a validated exception
    # decision (--decision): existing, decided/promoted, and declaring
    # `authorizes: venue_exception` — the same contract the audit enforces.
    routing = load_venue_routing(stage_root)
    routed = routing.get(args.kind.strip().lower(), "")
    exception_reason = ""
    if routed == VENUE_SPLIT_TOKEN:
        exception_reason = (
            f"kind `{args.kind}` is declared mixed (`{VENUE_SPLIT_TOKEN}`): register separate "
            "design and implementation items with `parent` lineage instead, or pass "
            "--decision <DE-id> naming a decided decision with `authorizes: venue_exception` "
            "for a deliberate single item"
        )
    elif not args.venue and routed:
        args.venue = routed
        print(f"venue derived from venue_routing: {args.kind} -> {routed}")
    elif args.venue and routed and args.venue != routed:
        exception_reason = (
            f"venue `{args.venue}` contradicts venue_routing ({args.kind} -> {routed}); pass "
            "--decision <DE-id> naming a decided decision with `authorizes: venue_exception`"
        )

    if args.decision:
        error = venue_exception_error(stage_root, args.decision)
        if error:
            print(f"refusing: {error}", file=sys.stderr)
            return 1
        print(
            f"venue exception authorized by {args.decision} "
            "(set its work_item to the allocated item id; the audit checks the back-link)"
        )
    elif exception_reason:
        print(f"refusing: {exception_reason}", file=sys.stderr)
        return 1

    if not items_dir.exists():
        print(f"Stage present items dir not found: {items_dir}", file=sys.stderr)
        return 2
    if not template_path.exists():
        print(f"Work-item template not found: {template_path}", file=sys.stderr)
        return 2
    template = template_path.read_text(encoding="utf-8")

    def content_for(item_id: str) -> str:
        return fill_item(
            template,
            item_id=item_id,
            title=args.title,
            kind=args.kind,
            venue=args.venue,
            scope=args.scope,
            purpose=args.purpose,
            review=args.review,
            decision=args.decision,
            milestone=args.milestone,
        )

    def item_link_for(item_id: str) -> str:
        return relative_record_link(active_relative, f"{items_relative}/{item_id}.md")

    def row_for(item_id: str) -> str:
        item_link = item_link_for(item_id)
        return active_row(
            item_id,
            args.kind,
            args.venue,
            args.purpose,
            args.owner,
            item_link,
        )

    if args.id:
        if not ID_RE.match(args.id):
            print(f"--id must look like W-00000001, got {args.id}", file=sys.stderr)
            return 2
        item_path = items_dir / f"{args.id}.md"
        if planned_relative and (
            stage_root / planned_relative / f"{args.id}.md"
        ).exists():
            print(
                f"{args.id}: refusing — id already used by a planned card",
                file=sys.stderr,
            )
            return 1
        archived = (stage_root / archive_relative / f"{args.id}.md").exists()
        if archived:
            print(f"{args.id}: refusing — id already used by an archived item", file=sys.stderr)
            return 1
        if item_path.exists():
            # Re-run reconciles the index rather than overwriting authored content.
            ensure_active_row(
                active_path, args.id, row_for(args.id), item_link_for(args.id)
            )
            print(f"{args.id}: already exists; index reconciled")
            return 0
        try:
            with open(item_path, "x", encoding="utf-8") as handle:
                handle.write(content_for(args.id))
        except FileExistsError:
            ensure_active_row(
                active_path, args.id, row_for(args.id), item_link_for(args.id)
            )
            print(f"{args.id}: already exists; index reconciled")
            return 0
        item_id = args.id
    else:
        item_id = create_item_atomic(items_dir, existing_numbers(stage_root), content_for)

    ensure_active_row(active_path, item_id, row_for(item_id), item_link_for(item_id))
    if args.review:
        command, _err = resolve_review_command(load_review_config(stage_root), "implementation")
        if not command:
            print(
                f"{item_id}: WARNING review: pending, but settings.json configures no implementation "
                "review command — close_work will refuse to close this item until one is set (or the "
                "review field is cleared).",
                file=sys.stderr,
            )
    print(f"{item_id}: registered ({items_dir / f'{item_id}.md'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
