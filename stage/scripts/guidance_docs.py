#!/usr/bin/env python3
"""Shared guidance-template comparison and refresh rules."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import init_stage


SEPARATOR_CELL_RE = re.compile(r"^:?-{3,}:?$")


@dataclass(frozen=True)
class MarkdownTable:
    header: int
    separator: int
    data_start: int
    data_end: int

    @property
    def is_empty(self) -> bool:
        return self.data_start == self.data_end


@dataclass(frozen=True)
class RefreshPlan:
    action: str
    content: str | None
    reason: str = ""


def _table_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _is_separator(line: str) -> bool:
    cells = _table_cells(line)
    return bool(cells) and all(SEPARATOR_CELL_RE.fullmatch(cell) for cell in cells)


def markdown_tables(text: str) -> list[MarkdownTable]:
    """Return conventional Markdown tables and their contiguous data-row spans."""
    lines = text.splitlines()
    tables: list[MarkdownTable] = []
    index = 0
    while index + 1 < len(lines):
        header_cells = _table_cells(lines[index])
        if header_cells and _is_separator(lines[index + 1]):
            data_end = index + 2
            while data_end < len(lines) and _table_cells(lines[data_end]):
                data_end += 1
            tables.append(
                MarkdownTable(
                    header=index,
                    separator=index + 1,
                    data_start=index + 2,
                    data_end=data_end,
                )
            )
            index = data_end
            continue
        index += 1
    return tables


def template_mode(template_text: str) -> tuple[str, str]:
    """Classify a template from its table shape, without path-specific lists."""
    tables = markdown_tables(template_text)
    empty_tables = [table for table in tables if table.is_empty]
    if len(empty_tables) > 1:
        return "refused", "template has multiple empty tables"
    if empty_tables and len(tables) > 1:
        return "refused", "template mixes project-owned and populated tables"
    if empty_tables:
        return "empty_table", ""
    if tables:
        return "populated_table", ""
    return "no_table", ""


def _merge_project_rows(template_text: str, project_text: str | None) -> RefreshPlan:
    template_table = markdown_tables(template_text)[0]
    if project_text is None:
        return RefreshPlan("refresh", template_text)

    project_tables = markdown_tables(project_text)
    if len(project_tables) != 1:
        return RefreshPlan(
            "refused",
            None,
            "project document does not contain exactly one matching table",
        )

    template_lines = template_text.splitlines()
    project_lines = project_text.splitlines()
    project_table = project_tables[0]
    # Existing index writers append rows at EOF. Some templates end with a
    # blank line, so those rows are not contiguous with the separator even
    # though they remain the sole table's project-owned data.
    project_rows = [
        line
        for index, line in enumerate(project_lines)
        if index > project_table.separator
        and _table_cells(line)
        and not _is_separator(line)
    ]
    merged_lines = (
        template_lines[: template_table.data_start]
        + project_rows
        + template_lines[template_table.data_end :]
    )
    merged = "\n".join(merged_lines)
    if template_text.endswith("\n"):
        merged += "\n"
    return RefreshPlan("refresh", merged)


def plan_refresh(
    template_text: str,
    project_text: str | None,
    *,
    selected: bool,
) -> RefreshPlan:
    """Plan one refresh according to DE-00000029's three table-shape branches."""
    mode, reason = template_mode(template_text)
    if mode == "refused":
        return RefreshPlan("refused", None, reason)
    if mode == "populated_table" and not selected:
        return RefreshPlan(
            "skipped",
            None,
            "template has a populated table; select the file explicitly to replace it",
        )
    if mode == "empty_table":
        return _merge_project_rows(template_text, project_text)
    return RefreshPlan("refresh", template_text)


def guidance_matches(template_text: str, project_text: str) -> bool:
    """Compare plugin-owned guidance while ignoring empty-table project rows."""
    mode, _reason = template_mode(template_text)
    if mode != "empty_table":
        return mode != "refused" and project_text == template_text

    template_table = markdown_tables(template_text)[0]
    project_tables = markdown_tables(project_text)
    if len(project_tables) != 1:
        return False
    project_table = project_tables[0]

    def guidance_only(text: str, table: MarkdownTable) -> str:
        lines = [
            line
            for index, line in enumerate(text.splitlines())
            if not (
                index > table.separator
                and _table_cells(line)
                and not _is_separator(line)
            )
        ]
        # Existing index writers remove the template's trailing blank line
        # before appending their first row. Treat only that table-boundary
        # whitespace as data-layout detail.
        while table.separator + 1 < len(lines) and not lines[table.separator + 1]:
            del lines[table.separator + 1]
        return "\n".join(lines)

    return guidance_only(project_text, project_table) == guidance_only(
        template_text,
        template_table,
    )


def load_settings(stage_root: Path) -> dict[str, object]:
    try:
        data = json.loads((stage_root / "settings.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def project_language(stage_root: Path) -> str:
    language = load_settings(stage_root).get("language")
    if isinstance(language, str) and init_stage.LANGUAGE_TAG_RE.fullmatch(language):
        return language
    return init_stage.DEFAULT_LANGUAGE


def guidance_paths() -> list[Path]:
    return sorted(
        path.relative_to(init_stage.TEMPLATE_ROOT)
        for path in init_stage.TEMPLATE_ROOT.rglob("*.md")
        if path.is_file()
    )


def localized_template(relative: Path, language: str) -> Path:
    return init_stage.template_source(relative, language)
