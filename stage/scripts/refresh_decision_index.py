#!/usr/bin/env python3
"""Render the pending-decision index, and the title column of the official decision index.

The pending index is derived whole from the pending records and their work cards. The
official index keeps its hand-written rows; this command owns only its title column, which
it fills from each record's heading so a reader can find a decision by topic (DE-00000100).
"""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
from dataclasses import dataclass
from pathlib import Path


HOOK_ROOT = Path(__file__).resolve().parents[1] / "hooks"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))

from stage_memory_index import record_title  # noqa: E402
from stage_record_paths import record_paths  # noqa: E402
import stage_roadmap  # noqa: E402
import stage_topology  # noqa: E402
from stage_work import parse_frontmatter  # noqa: E402


INDEX_RELATIVE = Path("decisions/index.md")
PENDING_RELATIVE = Path("decisions/pending")
OFFICIAL_INDEX_RELATIVE = Path("official/decisions/index.md")
OFFICIAL_RELATIVE = Path("official/decisions/records")
# First header cell of the official table, and the title cell this command adds after it.
OFFICIAL_TITLE_CELLS = {"Decision": "Title", "결정": "제목"}
WORK_ROOTS = (Path("work/current"), Path("official/work/archive/items"))
TABLE_HEADERS = {
    "| Decision | Status | Owner | Link |": "en",
    "| Decision | Decision status | Owner record | Owner status | Effect | Link |": "en",
    "| Decision | Decision status | Owner record | Owner status | Link |": "en",
    "| Decision | Title | Decision status | Owner record | Owner status | Link |": "en",
    "| 결정 | 상태 | 소유자 | 링크 |": "ko",
    "| 결정 | 결정 상태 | 소유 항목 | 소유 항목 상태 | 효력 | 링크 |": "ko",
    "| 결정 | 결정 상태 | 소유 항목 | 소유 항목 상태 | 링크 |": "ko",
    "| 결정 | 제목 | 결정 상태 | 소유 항목 | 소유 항목 상태 | 링크 |": "ko",
}
RENDERED_HEADERS = {
    "en": "| Decision | Title | Decision status | Owner record | Owner status | Link |",
    "ko": "| 결정 | 제목 | 결정 상태 | 소유 항목 | 소유 항목 상태 | 링크 |",
}


class IndexFormatError(ValueError):
    """The index does not contain exactly one table that this command owns."""


@dataclass(frozen=True)
class WorkRecord:
    item_id: str
    status: str
    relative_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Refresh .stage/decisions/index.md from pending decision records, and the title "
            "column of .stage/official/decisions/index.md from the official records."
        )
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root containing .stage (default: cwd).",
    )
    return parser.parse_args()


def _work_records(stage_root: Path) -> dict[str, WorkRecord]:
    records: dict[str, WorkRecord] = {}
    for relative_root in WORK_ROOTS:
        root = stage_root / relative_root
        if not root.is_dir():
            continue
        for path in record_paths(root):
            fields = parse_frontmatter(path)
            item_id = (fields.get("id") or "").strip()
            if not item_id:
                continue
            records.setdefault(
                item_id,
                WorkRecord(
                    item_id=item_id,
                    status=(fields.get("status") or "missing").strip() or "missing",
                    relative_path=path.relative_to(stage_root),
                ),
            )
    return records


def _pending_decisions(
    stage_root: Path, excluded_ids: frozenset[str] = frozenset()
) -> list[tuple[Path, dict[str, str]]]:
    root = stage_root / PENDING_RELATIVE
    if not root.is_dir():
        return []
    decisions = []
    for path in record_paths(root):
        fields = parse_frontmatter(path)
        decision_id = (fields.get("id") or "").strip()
        if decision_id and decision_id not in excluded_ids:
            decisions.append((path, fields))
    return sorted(decisions, key=lambda entry: (entry[1].get("id", ""), entry[0]))


def _roadmap_record(stage_root: Path, record_id: str) -> WorkRecord | None:
    if not re.fullmatch(r"(?:TH|M)-\d{3,}", record_id):
        return None
    reference = stage_topology.resolve_artifact_reference(record_id)
    for candidate in reference.candidate_paths:
        path = stage_root / candidate
        if path.is_file():
            state = stage_roadmap.roadmap_record_state(stage_root, path)
            return WorkRecord(record_id, state.status, path.relative_to(stage_root))
    return None


def title_cell(path: Path, record_id: str) -> str:
    """A record's title as one table cell: one line, pipes escaped, `—` when it has none."""

    return " ".join(record_title(path, record_id).split()).replace("|", "\\|") or "—"


def _relative_link(target: Path) -> str:
    return posixpath.relpath(target.as_posix(), INDEX_RELATIVE.parent.as_posix())


def render_table(
    stage_root: Path,
    language: str,
    excluded_ids: frozenset[str] = frozenset(),
) -> str:
    work_by_id = _work_records(stage_root)
    lines = [RENDERED_HEADERS[language], "|---|---|---|---|---|---|"]
    for decision_path, fields in _pending_decisions(stage_root, excluded_ids):
        decision_id = fields["id"].strip()
        decision_status = (fields.get("status") or "missing").strip() or "missing"
        owner_id = (
            (fields.get("work_item") or "").strip()
            or (fields.get("roadmap_item") or "").strip()
            or "missing"
        )
        owner = work_by_id.get(owner_id) or _roadmap_record(stage_root, owner_id)
        if owner is None:
            owner_cell = owner_id
            owner_status = "missing"
        else:
            owner_link = _relative_link(owner.relative_path)
            owner_cell = f"[{owner_id}]({owner_link})"
            owner_status = owner.status
        decision_link = _relative_link(decision_path.relative_to(stage_root))
        lines.append(
            f"| {decision_id} | {title_cell(decision_path, decision_id)} | {decision_status} | "
            f"{owner_cell} | {owner_status} | "
            f"[{decision_link}]({decision_link}) |"
        )
    return "\n".join(lines) + "\n"


def render_index(
    stage_root: Path,
    existing: str,
    excluded_ids: frozenset[str] = frozenset(),
) -> str:
    lines = existing.splitlines(keepends=True)
    candidates: list[tuple[int, int, str, str]] = []
    for position, line in enumerate(lines):
        header = line.rstrip("\r\n").strip()
        language = TABLE_HEADERS.get(header)
        if language is None or position + 1 >= len(lines):
            continue
        separator = lines[position + 1].rstrip("\r\n").strip()
        cells = [cell.strip() for cell in separator.strip("|").split("|")]
        header_cells = [cell.strip() for cell in header.strip("|").split("|")]
        if (
            not separator.startswith("|")
            or not separator.endswith("|")
            or not cells
            or len(cells) != len(header_cells)
            or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)
        ):
            continue
        end = position + 2
        while end < len(lines):
            stripped = lines[end].strip()
            if not (stripped.startswith("|") and stripped.endswith("|")):
                break
            end += 1
        newline = "\r\n" if line.endswith("\r\n") else "\n"
        candidates.append((position, end, language, newline))
    if len(candidates) != 1:
        raise IndexFormatError(
            "decisions/index.md must contain exactly one recognized pending-decision table"
        )
    start, end, language, newline = candidates[0]
    rendered = render_table(stage_root, language, excluded_ids).replace("\n", newline)
    return "".join(lines[:start]) + rendered + "".join(lines[end:])


def _split_row(line: str) -> list[str] | None:
    """The cells of one table row, pipes escaped inside a cell kept; None for any other line."""

    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")) or len(stripped) < 2:
        return None
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", stripped[1:-1])]


def render_official_index(stage_root: Path, existing: str) -> str:
    """Return the official decision index with a current title cell on every decision row.

    The rows are written by hand at promotion, so everything but the title column is kept
    as it is. Text with no table whose first header cell names decisions is returned
    unchanged.
    """
    lines = existing.splitlines(keepends=True)
    for position, line in enumerate(lines[:-1]):
        header = _split_row(line)
        separator = _split_row(lines[position + 1])
        if (
            not header
            or header[0] not in OFFICIAL_TITLE_CELLS
            or not separator
            or len(separator) != len(header)
            or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator)
        ):
            continue
        title_name = OFFICIAL_TITLE_CELLS[header[0]]
        has_title = len(header) > 1 and header[1] == title_name
        newline = "\r\n" if line.endswith("\r\n") else "\n"
        if not has_title:
            header.insert(1, title_name)
            separator.insert(1, "---")
        rendered = [
            "| " + " | ".join(header) + " |" + newline,
            "|" + "|".join(separator) + "|" + newline,
        ]
        end = position + 2
        while end < len(lines):
            cells = _split_row(lines[end])
            if cells is None:
                break
            row_newline = "\r\n" if lines[end].endswith("\r\n") else newline
            if not has_title:
                cells.insert(1, "—")
            record = stage_root / OFFICIAL_RELATIVE / f"{cells[0]}.md"
            if len(cells) > 1 and record.is_file():
                cells[1] = title_cell(record, cells[0])
            rendered.append("| " + " | ".join(cells) + " |" + row_newline)
            end += 1
        if lines[end - 1].endswith(("\n", "\r\n")) is False:
            rendered[-1] = rendered[-1].rstrip("\r\n")
        return "".join(lines[:position]) + "".join(rendered) + "".join(lines[end:])
    return existing


def refresh_official_titles(project_root: Path) -> bool:
    """Write the official index when a title cell is missing or stale; False when current."""

    stage_root = project_root.resolve() / ".stage"
    index_path = stage_root / OFFICIAL_INDEX_RELATIVE
    if not index_path.is_file():
        return False
    existing = index_path.read_bytes().decode("utf-8")
    rendered = render_official_index(stage_root, existing)
    if rendered == existing:
        return False
    index_path.write_bytes(rendered.encode("utf-8"))
    return True


def refresh_index(project_root: Path) -> bool:
    stage_root = project_root.resolve() / ".stage"
    index_path = stage_root / INDEX_RELATIVE
    existing = index_path.read_text(encoding="utf-8")
    rendered = render_index(stage_root, existing)
    if rendered == existing:
        return False
    index_path.write_text(rendered, encoding="utf-8")
    return True


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    try:
        changed = refresh_index(project_root)
    except (OSError, IndexFormatError) as exc:
        print(f"Cannot refresh pending-decision index: {exc}", file=sys.stderr)
        return 2
    outcome = "refreshed" if changed else "already current"
    print(f"Pending-decision index {outcome}: .stage/{INDEX_RELATIVE.as_posix()}")
    try:
        changed = refresh_official_titles(project_root)
    except OSError as exc:
        print(f"Cannot refresh official decision titles: {exc}", file=sys.stderr)
        return 2
    outcome = "refreshed" if changed else "already current"
    print(f"Official decision titles {outcome}: .stage/{OFFICIAL_INDEX_RELATIVE.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
