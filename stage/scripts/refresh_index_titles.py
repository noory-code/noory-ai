#!/usr/bin/env python3
"""Fill the title cells of a project's decision indexes and work archive index.

A session finds a record by topic from a title (DE-00000100). A project that was created by
an earlier Stage has indexes without them: its official decision index has no title column,
and its work archive index gained the column header when the next card was archived while
every older row stayed as it was. Run this once after updating the Stage plugin:

    python3 stage/scripts/refresh_index_titles.py --project-root .

It runs three steps and prints one line for each:

1. the pending-decision index is rendered from its records (`refresh_decision_index.py`);
2. the official decision index gets a current title on every row (the same module);
3. the work archive index gets a title on every row that has none.

Step 3 never replaces a title a row already carries, and leaves a row as it is when no
archived card has its id; the audit reports such a row (ARCHIVE004). Titles come from each
archived card's `title:` field, or from its first heading. The command is idempotent.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

HOOK_ROOT = Path(__file__).resolve().parents[1] / "hooks"
SCRIPT_ROOT = Path(__file__).resolve().parent
for import_dir in (HOOK_ROOT, SCRIPT_ROOT):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

import refresh_decision_index  # noqa: E402
import stage_topology  # noqa: E402
from stage_paths import ACTIVE_TOPOLOGY_V4, active_topology  # noqa: E402
from stage_record_paths import record_paths  # noqa: E402
from stage_work import parse_frontmatter  # noqa: E402

# First header cell of the work archive table, and the title cell that ends its header.
WORK_TITLE_CELLS = {"Work": "Title", "작업": "제목"}
TITLE_COLUMN = 3
NO_TITLE = frozenset({"", "—", "-"})
_SEPARATOR_CELL = re.compile(r":?-{3,}:?")


def work_archive_index_relative() -> Path:
    return Path(stage_topology.get_zone("work", "official").index_surfaces[0])


def archived_card_paths(stage_root: Path) -> dict[str, Path]:
    """Every archived work card by id; the first file that declares an id owns it."""

    items_root = stage_root / work_archive_index_relative().parent / "items"
    cards: dict[str, Path] = {}
    if not items_root.is_dir():
        return cards
    for path in record_paths(items_root):
        item_id = (parse_frontmatter(path).get("id") or "").strip()
        if item_id:
            cards.setdefault(item_id, path)
    return cards


def render_work_archive_index(existing: str, cards: dict[str, Path]) -> tuple[str, int, int]:
    """The work archive index with a title on every row that lacked one.

    Returns `(text, rows_filled, rows_without_a_title)`. The last count is the rows that
    have no title afterwards: no card in `cards` has their id, or the card has neither a `title:` field
    nor a heading. A row whose card is unknown keeps its bytes. Text with no table whose
    first header cell names work records is returned unchanged.
    """
    split_row = refresh_decision_index._split_row
    lines = existing.splitlines(keepends=True)
    for position, line in enumerate(lines[:-1]):
        header = split_row(line)
        separator = split_row(lines[position + 1])
        if (
            not header
            or header[0] not in WORK_TITLE_CELLS
            or not separator
            or len(separator) != len(header)
            or not all(_SEPARATOR_CELL.fullmatch(cell) for cell in separator)
        ):
            continue
        newline = "\r\n" if line.endswith("\r\n") else "\n"
        rendered = [line, lines[position + 1]]
        filled = untitled = 0
        end = position + 2
        while end < len(lines):
            cells = split_row(lines[end])
            if cells is None:
                break
            row = lines[end]
            lacks_title = len(cells) == TITLE_COLUMN or (
                len(cells) > TITLE_COLUMN and cells[TITLE_COLUMN] in NO_TITLE
            )
            if lacks_title:
                card = cards.get(cells[0])
                title = refresh_decision_index.title_cell(card, cells[0]) if card else "—"
                if title in NO_TITLE:
                    untitled += 1
                else:
                    filled += 1
                if card is not None:
                    ending = row[len(row.rstrip("\r\n")) :]
                    cells[TITLE_COLUMN:TITLE_COLUMN + 1] = [title]
                    row = "| " + " | ".join(cells) + " |" + ending
            rendered.append(row)
            end += 1
        if len(header) == TITLE_COLUMN and end > position + 2:
            # Rows carry a fourth cell now, so the header names it.
            header.append(WORK_TITLE_CELLS[header[0]])
            separator.append("---")
            rendered[0] = "| " + " | ".join(header) + " |" + newline
            rendered[1] = "|" + "|".join(separator) + "|" + newline
        text = "".join(lines[:position]) + "".join(rendered) + "".join(lines[end:])
        return text, filled, untitled
    return existing, 0, 0


def work_archive_titles(stage_root: Path) -> Optional[tuple[str, str, int, int]]:
    """`(existing, rendered, rows_filled, rows_without_a_title)` for the work archive index.

    None when the project is not on the current topology or the index cannot be read.
    """
    if active_topology(stage_root) != ACTIVE_TOPOLOGY_V4:
        return None
    index_path = stage_root / work_archive_index_relative()
    try:
        existing = index_path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    rendered, filled, untitled = render_work_archive_index(
        existing, archived_card_paths(stage_root)
    )
    return existing, rendered, filled, untitled


def refresh_work_archive_titles(project_root: Path) -> tuple[bool, int]:
    """Write the work archive index when a row gains a title.

    Returns `(changed, rows_without_a_title)`.
    """
    stage_root = project_root.resolve() / ".stage"
    result = work_archive_titles(stage_root)
    if result is None:
        return False, 0
    existing, rendered, _filled, untitled = result
    if rendered == existing:
        return False, untitled
    # Bytes, so the index keeps the line endings it has.
    (stage_root / work_archive_index_relative()).write_bytes(rendered.encode("utf-8"))
    return True, untitled


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument(
        "--project-root", default=".", help="Project root containing .stage (default: cwd)."
    )
    args = parser.parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    stage_root = project_root / ".stage"
    if active_topology(stage_root) != ACTIVE_TOPOLOGY_V4:
        print(
            "Cannot refresh index titles: this project is not on the current Stage layout. "
            "Run the stage-migrate skill first.",
            file=sys.stderr,
        )
        return 2
    status = refresh_decision_index.main_for(project_root)
    if status:
        return status
    try:
        changed, untitled = refresh_work_archive_titles(project_root)
    except OSError as exc:
        print(f"Cannot refresh work archive titles: {exc}", file=sys.stderr)
        return 2
    outcome = "refreshed" if changed else "already current"
    print(f"Work archive titles {outcome}: .stage/{work_archive_index_relative().as_posix()}")
    if untitled:
        print(
            f"{untitled} work archive row(s) still have no title: no archived card has their "
            "id, or the card has no `title:` field and no heading. "
            "`python3 stage/scripts/audit_stage.py --project-root .` names the index."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
