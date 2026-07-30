#!/usr/bin/env python3
"""Shared guidance-template comparison and refresh rules."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import init_stage
from stage_paths import read_settings


SEPARATOR_CELL_RE = re.compile(r"^:?-{3,}:?$")
LIST_ITEM_RE = re.compile(
    r"^(?P<indent>[ \t]*)(?P<marker>[-+*])(?:[ \t]+(?P<body>.*))?$"
)
EMPTY_LIST_ITEM_RE = re.compile(r"^[ \t]*[-+*][ \t]*$")


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
class MarkdownList:
    start: int
    end: int
    indent: str
    empty: bool


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


def _indent_width(indent: str) -> int:
    return len(indent.expandtabs(4))


def markdown_lists(text: str) -> list[MarkdownList]:
    """Return top-level Markdown list spans, including indented item continuations."""
    lines = text.splitlines()
    lists: list[MarkdownList] = []
    index = 0
    while index < len(lines):
        first_match = LIST_ITEM_RE.fullmatch(lines[index])
        if first_match is None:
            index += 1
            continue

        indent = first_match.group("indent")
        indent_width = _indent_width(indent)
        end = index + 1
        item_count = 1
        has_continuation = False
        while end < len(lines):
            line = lines[end]
            item_match = LIST_ITEM_RE.fullmatch(line)
            if item_match is not None and item_match.group("indent") == indent:
                item_count += 1
                end += 1
                continue
            if line and _indent_width(line[: len(line) - len(line.lstrip())]) > indent_width:
                has_continuation = True
                end += 1
                continue
            if not line:
                next_index = end + 1
                while next_index < len(lines) and not lines[next_index]:
                    next_index += 1
                if next_index < len(lines):
                    next_line = lines[next_index]
                    next_match = LIST_ITEM_RE.fullmatch(next_line)
                    next_indent = next_line[: len(next_line) - len(next_line.lstrip())]
                    if (
                        next_match is not None
                        and next_match.group("indent") == indent
                    ) or _indent_width(next_indent) > indent_width:
                        has_continuation = True
                        end = next_index
                        continue
                break
            break

        lists.append(
            MarkdownList(
                start=index,
                end=end,
                indent=indent,
                empty=(
                    item_count == 1
                    and not has_continuation
                    and EMPTY_LIST_ITEM_RE.fullmatch(lines[index]) is not None
                ),
            )
        )
        index = end
    return lists


def template_mode(template_text: str) -> tuple[str, str]:
    """Classify a template from its project-owned container shape."""
    tables = markdown_tables(template_text)
    empty_tables = [table for table in tables if table.is_empty]
    lists = markdown_lists(template_text)
    empty_lists = [markdown_list for markdown_list in lists if markdown_list.empty]
    if len(empty_tables) + len(empty_lists) > 1:
        return "refused", "template has multiple empty containers"
    if empty_tables and len(tables) > 1:
        return "refused", "template mixes project-owned and populated tables"
    if empty_tables:
        return "empty_table", ""
    if empty_lists:
        return "empty_list", ""
    if tables:
        return "populated_table", ""
    return "no_container", ""


def unexplained_line_count(template_text: str, project_text: str) -> int:
    """Count non-empty project lines that the current template does not contain."""
    template_lines = {
        line
        for line in template_text.splitlines()
        if line.strip() and not _is_separator(line)
    }
    return sum(
        1
        for line in project_text.splitlines()
        if line.strip() and not _is_separator(line) and line not in template_lines
    )


def _missing_container_plan(
    template_text: str,
    *,
    kind: str,
    selected: bool,
) -> RefreshPlan:
    if selected:
        return RefreshPlan("refresh", template_text)
    return RefreshPlan(
        "skipped",
        None,
        f"project document does not contain the template's {kind} container exactly once; "
        "select the file explicitly to replace it",
    )


def _merge_project_rows(
    template_text: str,
    project_text: str | None,
    *,
    selected: bool,
) -> RefreshPlan:
    template_table = markdown_tables(template_text)[0]
    if project_text is None:
        return RefreshPlan("refresh", template_text)

    project_tables = markdown_tables(project_text)
    if len(project_tables) != 1:
        return _missing_container_plan(
            template_text,
            kind="table",
            selected=selected,
        )

    template_lines = template_text.splitlines(keepends=True)
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
    if not project_rows:
        return RefreshPlan("refresh", template_text)

    prefix = "".join(template_lines[: template_table.data_start])
    suffix = "".join(template_lines[template_table.data_end :])
    separator_line = template_lines[template_table.separator]
    newline = separator_line[len(separator_line.rstrip("\r\n")) :] or "\n"
    if prefix and not prefix.endswith(("\r", "\n")):
        prefix += newline
    rows = newline.join(project_rows)
    if suffix or template_text.endswith(("\r", "\n")):
        rows += newline
    return RefreshPlan("refresh", prefix + rows + suffix)


def _merge_project_list(
    template_text: str,
    project_text: str | None,
    *,
    selected: bool,
) -> RefreshPlan:
    template_lists = markdown_lists(template_text)
    template_index = next(
        index
        for index, markdown_list in enumerate(template_lists)
        if markdown_list.empty
    )
    template_list = template_lists[template_index]
    if project_text is None:
        return RefreshPlan("refresh", template_text)

    project_lists = markdown_lists(project_text)
    if len(project_lists) != len(template_lists):
        return _missing_container_plan(
            template_text,
            kind="list",
            selected=selected,
        )
    project_list = project_lists[template_index]
    if project_list.empty:
        return RefreshPlan("refresh", template_text)

    template_lines = template_text.splitlines(keepends=True)
    project_lines = project_text.splitlines()
    prefix = "".join(template_lines[: template_list.start])
    suffix = "".join(template_lines[template_list.end :])
    placeholder_line = template_lines[template_list.start]
    newline = placeholder_line[len(placeholder_line.rstrip("\r\n")) :] or "\n"
    if prefix and not prefix.endswith(("\r", "\n")):
        prefix += newline
    items = newline.join(project_lines[project_list.start : project_list.end])
    if suffix or template_text.endswith(("\r", "\n")):
        items += newline
    return RefreshPlan("refresh", prefix + items + suffix)


def plan_refresh(
    template_text: str,
    project_text: str | None,
    *,
    selected: bool,
) -> RefreshPlan:
    """Plan one refresh according to DE-00000047's container-shape branches."""
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
        return _merge_project_rows(
            template_text,
            project_text,
            selected=selected,
        )
    if mode == "empty_list":
        return _merge_project_list(
            template_text,
            project_text,
            selected=selected,
        )
    if mode == "no_container" and project_text is not None and not selected:
        unexplained = unexplained_line_count(template_text, project_text)
        if unexplained:
            noun = "line" if unexplained == 1 else "lines"
            return RefreshPlan(
                "skipped",
                None,
                f"project document has {unexplained} {noun} not present in the template; "
                "select the file explicitly to replace it",
            )
    return RefreshPlan("refresh", template_text)


def guidance_matches(template_text: str, project_text: str) -> bool:
    """Compare plugin-owned guidance while ignoring project-owned container items."""
    mode, _reason = template_mode(template_text)
    if mode not in {"empty_table", "empty_list"}:
        return mode != "refused" and project_text == template_text

    if mode == "empty_list":
        template_lists = markdown_lists(template_text)
        project_lists = markdown_lists(project_text)
        if len(project_lists) != len(template_lists):
            return False
        template_index = next(
            index
            for index, markdown_list in enumerate(template_lists)
            if markdown_list.empty
        )

        def list_guidance_only(text: str, markdown_list: MarkdownList) -> str:
            lines = text.splitlines()
            del lines[markdown_list.start : markdown_list.end]
            return "\n".join(lines)

        return list_guidance_only(
            project_text,
            project_lists[template_index],
        ) == list_guidance_only(
            template_text,
            template_lists[template_index],
        )

    template_table = markdown_tables(template_text)[0]
    project_tables = markdown_tables(project_text)
    if len(project_tables) != 1:
        return False
    project_table = project_tables[0]

    def table_guidance_only(text: str, table: MarkdownTable) -> str:
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

    return table_guidance_only(project_text, project_table) == table_guidance_only(
        template_text,
        template_table,
    )


def load_settings(stage_root: Path) -> dict[str, object]:
    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
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
