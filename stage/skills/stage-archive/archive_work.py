#!/usr/bin/env python3
"""One-shot archive of completed Stage work items.

Archiving is record keeping, not promotion, and it passes exactly ONE gate — a
per-path archive intent — because `.stage/` is excluded from `is_source_path`
(`stage/hooks/stage_paths.py: DEFAULT_EXCLUDED_PREFIXES`). No new work item is
required. This script is the sanctioned fast path: it validates each item is in
a closed terminal state, then moves it and its retrospective into
`past/work/archive/`, records the terminal status in `archive/index.md`, and
drops the present-flow rows. It re-enforces the same invariants the promotion
gate checks, and is idempotent.

Usage:
    python3 archive_work.py [--project-root .] W-00000001 [W-00000002 ...]
    python3 archive_work.py [--project-root .] --all-completed
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TERMINAL_STATUSES = {"completed", "rejected"}


def frontmatter_field(text: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}:[ \t]*(.*)$", text, re.MULTILINE)
    return match.group(1).strip().strip("'\"") if match else ""


def set_frontmatter_field(text: str, field: str, value: str) -> str:
    return re.sub(
        rf"^({re.escape(field)}:)[ \t]*.*$",
        rf"\g<1> {value}",
        text,
        count=1,
        flags=re.MULTILINE,
    )


def table_rows(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip().startswith("|")]


def drop_table_row(text: str, item_id: str) -> str:
    item_link = f"items/{item_id}.md"
    kept = [
        line
        for line in text.splitlines()
        if not (line.strip().startswith("|") and item_link in line)
    ]
    return "\n".join(kept) + ("\n" if text.endswith("\n") else "")


def append_index_row(index_text: str, item_id: str, final_status: str) -> str:
    row = f"| {item_id} | {final_status} | [items/{item_id}.md](items/{item_id}.md) |"
    if re.search(rf"\|\s*{re.escape(item_id)}\s*\|", index_text):
        return index_text  # idempotent
    body = index_text.rstrip("\n")
    return f"{body}\n{row}\n"


def completed_ids_from_review(stage_root: Path) -> list[str]:
    review = stage_root / "present" / "work" / "review.md"
    if not review.exists():
        return []
    ids: list[str] = []
    for line in table_rows(review.read_text(encoding="utf-8")):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or not cells[0].startswith("W-"):
            continue
        item_path = stage_root / "present" / "work" / "items" / f"{cells[0]}.md"
        if not item_path.exists():
            continue
        if frontmatter_field(item_path.read_text(encoding="utf-8"), "status") in TERMINAL_STATUSES:
            ids.append(cells[0])
    return ids


def open_parents(stage_root: Path) -> set[str]:
    """Item IDs still named as `parent` by an active/review/blocked work item."""
    parents: set[str] = set()
    items_dir = stage_root / "present" / "work" / "items"
    if not items_dir.exists():
        return parents
    for path in items_dir.glob("W-*.md"):
        text = path.read_text(encoding="utf-8")
        if frontmatter_field(text, "status") in {"active", "review", "blocked"}:
            parent = frontmatter_field(text, "parent")
            if parent:
                parents.add(parent)
    return parents


def archive_one(stage_root: Path, item_id: str, blocking_parents: set[str]) -> str:
    present_item = stage_root / "present" / "work" / "items" / f"{item_id}.md"
    archive_item = stage_root / "past" / "work" / "archive" / "items" / f"{item_id}.md"

    if archive_item.exists() and not present_item.exists():
        return f"{item_id}: already archived (skipped)"
    if not present_item.exists():
        return f"{item_id}: ERROR no present item file"

    text = present_item.read_text(encoding="utf-8")
    status = frontmatter_field(text, "status")
    if status not in TERMINAL_STATUSES:
        return f"{item_id}: ERROR status `{status}` is not completed/rejected"

    retro_completed = frontmatter_field(text, "retrospective") == "completed"
    if not retro_completed:
        return f"{item_id}: ERROR retrospective is not completed"
    ref = frontmatter_field(text, "retrospective_ref")
    if not ref:
        return f"{item_id}: ERROR no retrospective_ref"
    present_retro = stage_root / "present" / "work" / "retrospectives" / f"{ref}.md"
    if not present_retro.exists():
        return f"{item_id}: ERROR retrospective file {ref}.md not found"
    if item_id in blocking_parents:
        return f"{item_id}: ERROR an open work item still names it as parent"

    archive_retro = stage_root / "past" / "work" / "archive" / "retrospectives" / f"{ref}.md"
    index_path = stage_root / "past" / "work" / "archive" / "index.md"
    review_path = stage_root / "present" / "work" / "review.md"

    if archive_retro.exists():
        archived_work_item = frontmatter_field(
            archive_retro.read_text(encoding="utf-8"), "work_item"
        )
        if archived_work_item and archived_work_item != item_id:
            return (
                f"{item_id}: ERROR retrospective id collision: {ref}.md already belongs "
                f"to {archived_work_item}; refusing to overwrite it"
            )

    # Move the item (status -> archived) and its retrospective (verbatim).
    archive_item.parent.mkdir(parents=True, exist_ok=True)
    archive_retro.parent.mkdir(parents=True, exist_ok=True)
    archive_item.write_text(set_frontmatter_field(text, "status", "archived"), encoding="utf-8")
    archive_retro.write_text(present_retro.read_text(encoding="utf-8"), encoding="utf-8")

    # Record the terminal status the `archived` overwrite erases, then drop the
    # present-flow rows and files.
    index_path.write_text(
        append_index_row(index_path.read_text(encoding="utf-8"), item_id, status),
        encoding="utf-8",
    )
    if review_path.exists():
        review_path.write_text(
            drop_table_row(review_path.read_text(encoding="utf-8"), item_id), encoding="utf-8"
        )
    present_item.unlink()
    present_retro.unlink()
    return f"{item_id}: archived (final status {status}, {ref}.md)"


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive completed Stage work items.")
    parser.add_argument("--project-root", default=".", help="Project root (default: cwd).")
    parser.add_argument("--all-completed", action="store_true", help="Archive every completed item in review.md.")
    parser.add_argument("items", nargs="*", help="Work item IDs, e.g. W-00000001.")
    args = parser.parse_args()

    stage_root = Path(args.project_root).expanduser().resolve() / ".stage"
    if not stage_root.exists():
        print(f"Stage root not found: {stage_root}", file=sys.stderr)
        return 2

    ids = list(args.items)
    if args.all_completed:
        ids = completed_ids_from_review(stage_root)
    if not ids:
        print("No work items to archive.", file=sys.stderr)
        return 1

    blocking_parents = open_parents(stage_root)
    failed = False
    for item_id in ids:
        result = archive_one(stage_root, item_id, blocking_parents)
        print(result)
        if "ERROR" in result:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
