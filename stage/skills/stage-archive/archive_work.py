#!/usr/bin/env python3
"""One-shot archive of completed Stage work items.

Archiving is record keeping, not promotion, and it passes exactly ONE gate — a
per-path archive intent — because `.stage/` is excluded from `is_source_path`
(`stage/hooks/stage_paths.py: DEFAULT_EXCLUDED_PREFIXES`). No new work item is
required. This script is the sanctioned fast path: it validates each item is in
a closed terminal state, then moves it and its retrospective into
`official/work/archive/`, records the terminal status in `archive/index.md`, and
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

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "stage-retrospective")
)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from lifecycle_paths import relative_record_link, v4_lifecycle_paths  # noqa: E402
from worktree_guard import ORDER_CONTRACT, dirty_paths_in_scope  # noqa: E402
from stage_paths import (  # noqa: E402
    ACTIVE_TOPOLOGY_V4,
    active_topology,
    schema_migration_banner,
)
from stage_work import WorkItem, load_all_work_items, non_terminal_children  # noqa: E402

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


def set_or_insert_frontmatter_field(
    text: str, field: str, value: str, *, after: str
) -> str:
    updated = set_frontmatter_field(text, field, value)
    if updated != text or re.search(rf"^{re.escape(field)}:", text, re.MULTILINE):
        return updated
    inserted, count = re.subn(
        rf"^({re.escape(after)}:[^\n]*\n)",
        rf"\g<1>{field}: {value}\n",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError(f"work card has no `{after}:` field")
    return inserted


def table_rows(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip().startswith("|")]


def drop_table_row(text: str, item_id: str, item_link: str | None = None) -> str:
    link = item_link or f"items/{item_id}.md"
    kept = [
        line
        for line in text.splitlines()
        if not (line.strip().startswith("|") and link in line)
    ]
    return "\n".join(kept) + ("\n" if text.endswith("\n") else "")


def append_index_row(
    index_text: str,
    item_id: str,
    final_status: str,
    item_link: str | None = None,
) -> str:
    link = item_link or f"items/{item_id}.md"
    row = f"| {item_id} | {final_status} | [{link}]({link}) |"
    if re.search(rf"\|\s*{re.escape(item_id)}\s*\|", index_text):
        return index_text  # idempotent
    body = index_text.rstrip("\n")
    return f"{body}\n{row}\n"


def _archive_paths(stage_root: Path) -> tuple[str, str, str, str, str, str]:
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        paths = v4_lifecycle_paths()
        return (
            paths.current_cards,
            paths.current_retrospectives,
            paths.archive_cards,
            paths.archive_retrospectives,
            paths.review_index,
            paths.archive_index,
        )
    return (
        Path("present", "work", "items").as_posix(),
        Path("present", "work", "retrospectives").as_posix(),
        Path("past", "work", "archive", "items").as_posix(),
        Path("past", "work", "archive", "retrospectives").as_posix(),
        Path("present", "work", "review.md").as_posix(),
        Path("past", "work", "archive", "index.md").as_posix(),
    )


def completed_ids_from_review(stage_root: Path) -> list[str]:
    current_root, _, _, _, review_relative, _ = _archive_paths(stage_root)
    review = stage_root / review_relative
    if not review.exists():
        return []
    ids: list[str] = []
    for line in table_rows(review.read_text(encoding="utf-8")):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or not cells[0].startswith("W-"):
            continue
        item_path = stage_root / current_root / f"{cells[0]}.md"
        if not item_path.exists():
            continue
        if frontmatter_field(item_path.read_text(encoding="utf-8"), "status") in TERMINAL_STATUSES:
            ids.append(cells[0])
    return ids


def blocking_children_by_parent(stage_root: Path) -> dict[str, list[WorkItem]]:
    """Non-terminal children across current, planned, and archive zones."""

    items = load_all_work_items(stage_root)
    parent_ids = {item.parent for item in items if item.parent}
    return {
        parent_id: children
        for parent_id in sorted(parent_ids)
        if (children := non_terminal_children(parent_id, items))
    }


def archive_one(
    stage_root: Path,
    item_id: str,
    blocking_children: dict[str, list[WorkItem]],
) -> str:
    (
        current_root,
        current_retro_root,
        archive_root,
        archive_retro_root,
        review_relative,
        index_relative,
    ) = _archive_paths(stage_root)
    present_item = stage_root / current_root / f"{item_id}.md"
    archive_item = stage_root / archive_root / f"{item_id}.md"

    if archive_item.exists() and not present_item.exists():
        return f"{item_id}: already archived (skipped)"
    if not present_item.exists():
        return f"{item_id}: ERROR no present item file"

    text = present_item.read_text(encoding="utf-8")
    status = frontmatter_field(text, "status")
    if status not in TERMINAL_STATUSES:
        return f"{item_id}: ERROR status `{status}` is not completed/rejected"

    try:
        dirty_paths = dirty_paths_in_scope(stage_root.parent, frontmatter_field(text, "scope"))
    except RuntimeError as exc:
        return f"{item_id}: ERROR cannot verify worktree state; refusing to archive: {exc}"
    if dirty_paths:
        return (
            f"{item_id}: ERROR uncommitted path(s) inside scope: {', '.join(dirty_paths)}; "
            f"required order: {ORDER_CONTRACT}"
        )

    retro_completed = frontmatter_field(text, "retrospective") == "completed"
    if not retro_completed:
        return f"{item_id}: ERROR retrospective is not completed"
    ref = frontmatter_field(text, "retrospective_ref")
    if not ref:
        return f"{item_id}: ERROR no retrospective_ref"
    present_retro = stage_root / current_retro_root / f"{ref}.md"
    if not present_retro.exists():
        return f"{item_id}: ERROR retrospective file {ref}.md not found"
    if item_id in blocking_children:
        detail = ", ".join(
            f"{child.item_id} (`{child.status}`)"
            for child in blocking_children[item_id]
        )
        return f"{item_id}: ERROR non-terminal children still name it as parent: {detail}"

    archive_retro = stage_root / archive_retro_root / f"{ref}.md"
    index_path = stage_root / index_relative
    review_path = stage_root / review_relative

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
    archived_text = set_frontmatter_field(text, "status", "archived")
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        disposition = "accepted" if status == "completed" else "rejected"
        archived_text = set_or_insert_frontmatter_field(
            archived_text,
            "terminal_disposition",
            disposition,
            after="status",
        )
    archive_item.write_text(archived_text, encoding="utf-8")
    archive_retro.write_text(present_retro.read_text(encoding="utf-8"), encoding="utf-8")

    # Record the terminal status the `archived` overwrite erases, then drop the
    # present-flow rows and files.
    index_path.write_text(
        append_index_row(
            index_path.read_text(encoding="utf-8"),
            item_id,
            status,
            relative_record_link(index_relative, f"{archive_root}/{item_id}.md"),
        ),
        encoding="utf-8",
    )
    if review_path.exists():
        review_link = relative_record_link(
            review_relative, f"{current_root}/{item_id}.md"
        )
        review_path.write_text(
            drop_table_row(
                review_path.read_text(encoding="utf-8"), item_id, review_link
            ),
            encoding="utf-8",
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
    schema_blocker = schema_migration_banner(stage_root)
    if schema_blocker:
        print(schema_blocker, file=sys.stderr)
        return 2

    ids = list(args.items)
    if args.all_completed:
        ids = completed_ids_from_review(stage_root)
    if not ids:
        print("No work items to archive.", file=sys.stderr)
        return 1

    blocking_children = blocking_children_by_parent(stage_root)
    failed = False
    for item_id in ids:
        result = archive_one(stage_root, item_id, blocking_children)
        print(result)
        if "ERROR" in result:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
