#!/usr/bin/env python3
"""Render the pending-decision index from pending records and their work cards."""

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

from stage_record_paths import record_paths  # noqa: E402
import stage_roadmap  # noqa: E402
import stage_topology  # noqa: E402
from stage_work import WORK_FINAL_STATUSES, parse_frontmatter  # noqa: E402


INDEX_RELATIVE = Path("decisions/index.md")
PENDING_RELATIVE = Path("decisions/pending")
WORK_ROOTS = (Path("work/current"), Path("official/work/archive/items"))
TABLE_HEADERS = {
    "| Decision | Status | Owner | Link |": "en",
    "| Decision | Decision status | Owner record | Owner status | Effect | Link |": "en",
    "| 결정 | 상태 | 소유자 | 링크 |": "ko",
    "| 결정 | 결정 상태 | 소유 항목 | 소유 항목 상태 | 효력 | 링크 |": "ko",
}
RENDERED_HEADERS = {
    "en": "| Decision | Decision status | Owner record | Owner status | Effect | Link |",
    "ko": "| 결정 | 결정 상태 | 소유 항목 | 소유 항목 상태 | 효력 | 링크 |",
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
        description="Refresh .stage/decisions/index.md from pending decision records."
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


def _pending_decisions(stage_root: Path) -> list[tuple[Path, dict[str, str]]]:
    root = stage_root / PENDING_RELATIVE
    if not root.is_dir():
        return []
    decisions = []
    for path in record_paths(root):
        fields = parse_frontmatter(path)
        decision_id = (fields.get("id") or "").strip()
        if decision_id:
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


def _relative_link(target: Path) -> str:
    return posixpath.relpath(target.as_posix(), INDEX_RELATIVE.parent.as_posix())


def render_table(stage_root: Path, language: str) -> str:
    work_by_id = _work_records(stage_root)
    lines = [RENDERED_HEADERS[language], "|---|---|---|---|---|---|"]
    for decision_path, fields in _pending_decisions(stage_root):
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
        effect = (
            "expired"
            if (
                (fields.get("authorizes") or "").strip() == "venue_exception"
                and owner_status in WORK_FINAL_STATUSES
            )
            else "active"
        )
        decision_link = _relative_link(decision_path.relative_to(stage_root))
        lines.append(
            f"| {decision_id} | {decision_status} | {owner_cell} | {owner_status} | "
            f"{effect} | [{decision_link}]({decision_link}) |"
        )
    return "\n".join(lines) + "\n"


def render_index(stage_root: Path, existing: str) -> str:
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
    rendered = render_table(stage_root, language).replace("\n", newline)
    return "".join(lines[:start]) + rendered + "".join(lines[end:])


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
