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
import shutil
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "stage-retrospective")
)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from lifecycle_paths import relative_record_link, v4_lifecycle_paths  # noqa: E402
from stage_record_paths import (  # noqa: E402
    record_path,
    record_paths,
    top_level_item_path,
)
from worktree_guard import ORDER_CONTRACT, dirty_paths_in_scope  # noqa: E402
from stage_paths import (  # noqa: E402
    ACTIVE_TOPOLOGY_V4,
    active_topology,
    schema_migration_banner,
)
from stage_runtime import delete_pending_intents_for_work_item  # noqa: E402
from stage_work import (  # noqa: E402
    WorkItem,
    load_all_work_items,
    load_work_items,
    non_terminal_children,
)

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
    link = item_link or record_path(Path("items"), item_id).as_posix()
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
    link = item_link or record_path(Path("items"), item_id).as_posix()
    row = f"| {item_id} | {final_status} | [{link}]({link}) |"
    if re.search(rf"\|\s*{re.escape(item_id)}\s*\|", index_text):
        return index_text  # idempotent
    body = index_text.rstrip("\n")
    return f"{body}\n{row}\n"


def _archive_paths(stage_root: Path) -> tuple[str, str, str, str, str, str, str]:
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        paths = v4_lifecycle_paths()
        return (
            paths.current_cards,
            paths.current_retrospectives,
            paths.archive_cards,
            paths.archive_retrospectives,
            paths.active_index,
            paths.review_index,
            paths.archive_index,
        )
    return (
        Path("present", "work", "items").as_posix(),
        Path("present", "work", "retrospectives").as_posix(),
        Path("past", "work", "archive", "items").as_posix(),
        Path("past", "work", "archive", "retrospectives").as_posix(),
        Path("present", "work", "active.md").as_posix(),
        Path("present", "work", "review.md").as_posix(),
        Path("past", "work", "archive", "index.md").as_posix(),
    )


def _planned_paths(stage_root: Path) -> tuple[str, str]:
    if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
        paths = v4_lifecycle_paths()
        return paths.planned_cards, paths.planned_index
    return (
        Path("future", "backlog", "items").as_posix(),
        Path("future", "backlog", "index.md").as_posix(),
    )


def completed_ids_from_review(stage_root: Path) -> list[str]:
    _, _, _, _, _, review_relative, _ = _archive_paths(stage_root)
    review = stage_root / review_relative
    if not review.exists():
        return []
    current_items = {item.item_id: item for item in load_work_items(stage_root)}
    ids: list[str] = []
    for line in table_rows(review.read_text(encoding="utf-8")):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or not cells[0].startswith("W-"):
            continue
        item = current_items.get(cells[0])
        if item is None:
            continue
        if item.status in TERMINAL_STATUSES:
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
        active_relative,
        review_relative,
        index_relative,
    ) = _archive_paths(stage_root)
    planned_root, planned_index_relative = _planned_paths(stage_root)
    current_items_root = stage_root / current_root
    planned_items_root = stage_root / planned_root
    archive_items_root = stage_root / archive_root
    current_item = record_path(current_items_root, item_id)
    planned_item = record_path(planned_items_root, item_id)
    archived_match = record_path(archive_items_root, item_id)

    source_matches = [path for path in (current_item, planned_item) if path.exists()]
    if archived_match.exists() and not source_matches:
        return f"{item_id}: already archived (skipped)"
    if not source_matches:
        return f"{item_id}: ERROR no current or planned item file"
    if len(source_matches) != 1:
        return f"{item_id}: ERROR work item exists in both current and planned"
    source_item = source_matches[0]
    source_items_root = (
        planned_items_root if source_item == planned_item else current_items_root
    )
    source_is_planned = source_item == planned_item

    source_unit = top_level_item_path(source_items_root, source_item)
    if source_unit.is_dir() and source_item.parent != source_unit:
        return (
            f"{item_id}: ERROR archive the top-level hierarchy "
            f"{source_unit.name}, not a nested item"
        )
    archive_unit = archive_items_root / source_unit.name
    if archive_unit.exists():
        return f"{item_id}: ERROR archive move unit already exists: {archive_unit}"
    records = (
        (source_item, *record_paths(source_unit))
        if source_unit.is_dir()
        else (source_item,)
    )
    record_data: list[tuple[Path, str, str, str, Path | None]] = []
    dirty_paths: set[str] = set()
    for record in records:
        text = record.read_text(encoding="utf-8")
        record_id = frontmatter_field(text, "id") or record.stem
        status = frontmatter_field(text, "status")
        if status not in TERMINAL_STATUSES:
            return (
                f"{item_id}: ERROR hierarchy record {record_id} status `{status}` "
                "is not completed/rejected"
            )
        if source_is_planned and status != "rejected":
            return (
                f"{item_id}: ERROR planned hierarchy record {record_id} status "
                f"`{status}` is not rejected"
            )
        try:
            dirty_paths.update(
                dirty_paths_in_scope(
                    stage_root.parent,
                    frontmatter_field(text, "scope"),
                )
            )
        except RuntimeError as exc:
            return (
                f"{item_id}: ERROR cannot verify worktree state; refusing to archive: {exc}"
            )
        if source_is_planned:
            record_data.append((record, record_id, status, "", None))
            continue
        if frontmatter_field(text, "retrospective") != "completed":
            return f"{item_id}: ERROR {record_id} retrospective is not completed"
        ref = frontmatter_field(text, "retrospective_ref")
        if not ref:
            return f"{item_id}: ERROR {record_id} has no retrospective_ref"
        present_retro = record_path(stage_root / current_retro_root, ref)
        if not present_retro.exists():
            return f"{item_id}: ERROR retrospective file {ref}.md not found"
        record_data.append((record, record_id, status, ref, present_retro))
    if dirty_paths:
        return (
            f"{item_id}: ERROR uncommitted path(s) inside scope: "
            f"{', '.join(sorted(dirty_paths))}; required order: {ORDER_CONTRACT}"
        )
    if item_id in blocking_children:
        detail = ", ".join(
            f"{child.item_id} (`{child.status}`)"
            for child in blocking_children[item_id]
        )
        return f"{item_id}: ERROR non-terminal children still name it as parent: {detail}"

    index_path = stage_root / index_relative
    planned_index_path = stage_root / planned_index_relative
    active_path = stage_root / active_relative
    review_path = stage_root / review_relative
    for _record, record_id, _status, ref, _present_retro in record_data:
        if ref:
            archive_retro = record_path(stage_root / archive_retro_root, ref)
            if archive_retro.exists():
                archived_work_item = frontmatter_field(
                    archive_retro.read_text(encoding="utf-8"), "work_item"
                )
                if archived_work_item and archived_work_item != record_id:
                    return (
                        f"{item_id}: ERROR retrospective id collision: {ref}.md already "
                        f"belongs to {archived_work_item}; refusing to overwrite it"
                    )
        failed_intents = delete_pending_intents_for_work_item(stage_root, record_id)
        if failed_intents:
            names = ", ".join(path.name for path in failed_intents)
            return f"{item_id}: ERROR cannot delete pending intent(s): {names}"

    root_text = source_item.read_text(encoding="utf-8")
    root_status = frontmatter_field(root_text, "status")
    for record, _record_id, status, _ref, _present_retro in record_data:
        relative = (
            record.relative_to(source_unit)
            if source_unit.is_dir()
            else Path(record.name)
        )
        target = (
            archive_unit / relative
            if source_unit.is_dir()
            else archive_unit
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        archived_text = set_frontmatter_field(
            record.read_text(encoding="utf-8"), "status", "archived"
        )
        if active_topology(stage_root) == ACTIVE_TOPOLOGY_V4:
            archived_text = set_or_insert_frontmatter_field(
                archived_text,
                "terminal_disposition",
                "accepted" if status == "completed" else "rejected",
                after="status",
            )
        target.write_text(archived_text, encoding="utf-8")
    for _record, _record_id, _status, ref, present_retro in record_data:
        if not ref or present_retro is None:
            continue
        archive_retro = record_path(stage_root / archive_retro_root, ref)
        archive_retro.parent.mkdir(parents=True, exist_ok=True)
        archive_retro.write_text(
            present_retro.read_text(encoding="utf-8"), encoding="utf-8"
        )

    archived_item = record_path(archive_items_root, item_id)
    archived_link = relative_record_link(
        index_relative,
        archived_item.relative_to(stage_root).as_posix(),
    )
    index_path.write_text(
        append_index_row(
            index_path.read_text(encoding="utf-8"),
            item_id,
            root_status,
            archived_link,
        ),
        encoding="utf-8",
    )
    active_text = active_path.read_text(encoding="utf-8") if active_path.exists() else ""
    review_text = review_path.read_text(encoding="utf-8") if review_path.exists() else ""
    planned_index_text = (
        planned_index_path.read_text(encoding="utf-8")
        if planned_index_path.exists()
        else ""
    )
    for record, record_id, _status, _ref, _present_retro in record_data:
        if source_is_planned:
            planned_link = relative_record_link(
                planned_index_relative,
                record.relative_to(stage_root).as_posix(),
            )
            planned_index_text = drop_table_row(
                planned_index_text,
                record_id,
                planned_link,
            )
        else:
            record_link = relative_record_link(
                active_relative,
                record.relative_to(stage_root).as_posix(),
            )
            active_text = drop_table_row(active_text, record_id, record_link)
            review_link = relative_record_link(
                review_relative,
                record.relative_to(stage_root).as_posix(),
            )
            review_text = drop_table_row(review_text, record_id, review_link)
    if active_path.exists() and not source_is_planned:
        active_path.write_text(active_text, encoding="utf-8")
    if review_path.exists() and not source_is_planned:
        review_path.write_text(review_text, encoding="utf-8")
    if planned_index_path.exists() and source_is_planned:
        planned_index_path.write_text(planned_index_text, encoding="utf-8")
    if source_unit.is_dir():
        shutil.rmtree(source_unit)
    else:
        source_unit.unlink()
    for _record, _record_id, _status, _ref, present_retro in record_data:
        if present_retro is not None:
            present_retro.unlink()
    return (
        f"{item_id}: archived hierarchy ({len(record_data)} record(s), "
        f"final status {root_status})"
    )


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
