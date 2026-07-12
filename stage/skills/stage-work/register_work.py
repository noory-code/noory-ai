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
from stage_paths import (  # noqa: E402
    load_review_config,
    load_venue_routing,
    resolve_review_command,
)

ID_RE = re.compile(r"^W-(\d{8})$")
_TEMPLATE = (
    Path(__file__).resolve().parents[2]
    / "templates"
    / "project-stage"
    / "present"
    / "work"
    / "items"
    / "_template.md"
)


def set_field(text: str, field: str, value: str) -> str:
    return re.sub(
        rf"^({re.escape(field)}:)[ \t]*.*$", rf"\g<1> {value}", text, count=1, flags=re.MULTILINE
    )


def existing_numbers(stage_root: Path) -> set[int]:
    numbers: set[int] = set()
    for base in ("present/work/items", "past/work/archive/items"):
        for path in (stage_root / base).glob("W-*.md"):
            match = ID_RE.match(path.stem)
            if match:
                numbers.add(int(match.group(1)))
    return numbers


def fill_item(template: str, *, item_id: str, title: str, kind: str, venue: str, scope: str, purpose: str, review: bool) -> str:
    text = template.replace("W-00000000 Title", f"{item_id} {title}")
    text = set_field(text, "id", item_id)
    text = set_field(text, "title", title)
    text = set_field(text, "kind", kind)
    text = set_field(text, "venue", venue)
    text = set_field(text, "scope", scope)
    if review:
        text = set_field(text, "review", "pending")  # opt this item into a required review
    if purpose:
        text = text.replace("## Purpose\n\n", f"## Purpose\n\n{purpose}\n", 1)
    return text


def active_row(item_id: str, kind: str, venue: str, purpose: str, owner: str) -> str:
    # Link form is required: audit_stage matches items via the [..](items/<id>.md) link, not a bare id.
    summary = (purpose.splitlines()[0] if purpose else "").strip()[:60]
    return f"| {item_id} | {kind} | {venue} | {summary} | active | {owner} | [items/{item_id}.md](items/{item_id}.md) |"


def ensure_active_row(active_path: Path, item_id: str, row: str) -> None:
    """Append the row if the item is not already indexed. Re-run reconciles:
    it never duplicates and never rewrites an existing row.

    Index membership is eventually-consistent: this read-modify-write can lose a
    row if two windows register at once. The id allocation (O_EXCL) is the atomic
    part; a dropped row is self-detected by the audit (INDEX003) and repaired by a
    re-run."""
    text = active_path.read_text(encoding="utf-8") if active_path.exists() else ""
    if re.search(rf"\(items/{re.escape(item_id)}\.md\)", text):
        return
    body = text.rstrip("\n")
    active_path.write_text(f"{body}\n{row}\n", encoding="utf-8")


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a Stage work item + active.md row.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--title", required=True)
    parser.add_argument("--kind", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--venue", default="")
    parser.add_argument("--owner", default="Claude")
    parser.add_argument("--purpose", default="")
    parser.add_argument("--id", default=None, help="Explicit W-NNNNNNNN; default allocates the next free id.")
    parser.add_argument("--review", action="store_true", help="Require a review (review: pending) before this item can complete.")
    args = parser.parse_args()

    stage_root = Path(args.project_root).expanduser().resolve() / ".stage"
    items_dir = stage_root / "present" / "work" / "items"
    active_path = stage_root / "present" / "work" / "active.md"

    # Role policy (DE-00000004): derive an omitted venue from the declared
    # kind -> venue routing; announce an explicit contradiction as a policy
    # exception that must carry a decision_refs link (the audit checks it).
    routing = load_venue_routing(stage_root)
    routed = routing.get(args.kind.strip().lower(), "")
    if not args.venue and routed:
        args.venue = routed
        print(f"venue derived from venue_routing: {args.kind} -> {routed}")
    elif args.venue and routed and args.venue != routed:
        print(
            f"policy exception: venue `{args.venue}` contradicts venue_routing "
            f"({args.kind} -> {routed}); link the authorizing decision in decision_refs"
        )

    if not items_dir.exists():
        print(f"Stage present items dir not found: {items_dir}", file=sys.stderr)
        return 2
    if not _TEMPLATE.exists():
        print(f"Work-item template not found: {_TEMPLATE}", file=sys.stderr)
        return 2
    template = _TEMPLATE.read_text(encoding="utf-8")

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
        )

    if args.id:
        if not ID_RE.match(args.id):
            print(f"--id must look like W-00000001, got {args.id}", file=sys.stderr)
            return 2
        item_path = items_dir / f"{args.id}.md"
        archived = (stage_root / "past" / "work" / "archive" / "items" / f"{args.id}.md").exists()
        if archived:
            print(f"{args.id}: refusing — id already used by an archived item", file=sys.stderr)
            return 1
        if item_path.exists():
            # Re-run reconciles the index rather than overwriting authored content.
            ensure_active_row(active_path, args.id, active_row(args.id, args.kind, args.venue, args.purpose, args.owner))
            print(f"{args.id}: already exists; index reconciled")
            return 0
        try:
            with open(item_path, "x", encoding="utf-8") as handle:
                handle.write(content_for(args.id))
        except FileExistsError:
            ensure_active_row(active_path, args.id, active_row(args.id, args.kind, args.venue, args.purpose, args.owner))
            print(f"{args.id}: already exists; index reconciled")
            return 0
        item_id = args.id
    else:
        item_id = create_item_atomic(items_dir, existing_numbers(stage_root), content_for)

    ensure_active_row(active_path, item_id, active_row(item_id, args.kind, args.venue, args.purpose, args.owner))
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
