#!/usr/bin/env python3
"""Create and inspect schema-v4 roadmap records and milestone transitions."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Callable


# A caller may pass a criterion already written as a list item; the record adds its own marker.
LIST_MARKER_RE = re.compile(r"^\s*[-*+]\s+")

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
HOOK_ROOT = PLUGIN_ROOT / "hooks"
SCRIPT_ROOT = PLUGIN_ROOT / "scripts"
for import_root in (HOOK_ROOT, SCRIPT_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import stage_roadmap  # noqa: E402
import stage_roadmap_closure  # noqa: E402
import stage_topology  # noqa: E402
import refresh_decision_index  # noqa: E402
from stage_record_ids import (  # noqa: E402
    IdReserver,
    used_numbers,
)
from stage_paths import (  # noqa: E402
    ACTIVE_TOPOLOGY_V4,
    active_topology,
    schema_migration_banner,
)
from stage_work import parse_frontmatter, split_scope  # noqa: E402


def _set_field(text: str, field: str, value: str) -> str:
    updated, count = re.subn(
        rf"^({re.escape(field)}:)[ \t]*.*$",
        rf"\g<1> {value}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError(f"template has no `{field}:` field")
    return updated


def _replace_section(text: str, heading: str, value: str) -> str:
    if not value:
        return text
    pattern = rf"(^## {re.escape(heading)}[ \t]*$\n)(.*?)(?=^## |\Z)"
    updated, count = re.subn(
        pattern,
        lambda match: match.group(1) + "\n" + value.strip() + "\n\n",
        text,
        count=1,
        flags=re.MULTILINE | re.DOTALL,
    )
    if count != 1:
        raise ValueError(f"template has no `## {heading}` section")
    return updated


def _insert_table_row(text: str, row: str) -> str:
    lines = text.splitlines()
    separator = next(
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
    if separator is None:
        return text.rstrip("\n") + "\n" + row + "\n"
    insertion = separator + 1
    while insertion < len(lines) and lines[insertion].lstrip().startswith("|"):
        insertion += 1
    lines.insert(insertion, row)
    return "\n".join(lines) + "\n"


def _ensure_index_row(index_path: Path, record_id: str, row: str) -> None:
    text = index_path.read_text(encoding="utf-8")
    if any(cells and cells[0].strip() == record_id for cells in _parse_rows(index_path)):
        return
    index_path.write_text(_insert_table_row(text, row), encoding="utf-8")


def _parse_rows(path: Path) -> tuple[tuple[str, ...], ...]:
    rows: list[tuple[str, ...]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = tuple(cell.strip() for cell in line.strip().strip("|").split("|"))
        if cells and not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            rows.append(cells)
    return tuple(rows[1:]) if rows else ()


def _template_for(zone_name: str) -> Path:
    zone = stage_topology.get_zone("roadmap", zone_name)
    if zone.template_source is None:
        raise RuntimeError(f"roadmap zone has no template: {zone_name}")
    return PLUGIN_ROOT / "templates" / "v4" / zone.template_source


def _chain_decision_target(stage_root: Path) -> tuple[Path, str, Path]:
    """Where a roadmap chain decision is born, and the body it is born with.

    A chain decision is settled the moment this command writes it: the command
    already validated the transition, and nothing verifies it afterwards. It
    therefore goes straight into the official records zone, so no later step has
    to carry it there. The pending zone's template still supplies the body,
    because the official zone's template predates decision frontmatter.
    """
    zone = stage_topology.get_zone("decisions", "official")
    directory = stage_root / zone.canonical_path
    template_source = stage_topology.get_zone("decisions", "pending").template_source
    template_path = PLUGIN_ROOT / "templates" / "v4" / str(template_source)
    if not directory.is_dir() or not template_path.is_file():
        raise RuntimeError("official-decision directory or bundled template is missing")
    return (
        directory,
        template_path.read_text(encoding="utf-8"),
        stage_root / zone.index_surfaces[0],
    )


def _add_chain_decision_row(
    stage_root: Path, records_index: Path, decision_id: str, milestone_id: str
) -> None:
    """Index a chain decision in the official decision index, title cell included.

    The title column is brought up to date first, so the new row has the same cells as the
    rows above it in an index written before the column existed (DE-00000100).
    """
    refresh_decision_index.refresh_official_titles(stage_root.parent)
    title = refresh_decision_index.title_cell(
        records_index.parent / "records" / f"{decision_id}.md", decision_id
    )
    _ensure_index_row(
        records_index,
        decision_id,
        f"| {decision_id} | {title} | decided | {milestone_id} | "
        f"[records/{decision_id}.md](records/{decision_id}.md) |",
    )


def _create_atomic(
    directory: Path,
    prefix: str,
    content_for: Callable[[str], str],
    project_root: Path,
) -> str:
    # `used_numbers` owns what counts as used: this checkout's records, numbers a started
    # card holds back in `reserved_ids:` (DE-00000094), records on other local or
    # remote-tracking branches, and ids reserved on the remote (DE-00000092).
    reserver = IdReserver(project_root)
    number = max(used_numbers(project_root, prefix, reserver), default=0) + 1
    for _ in range(1000):
        candidate = f"{prefix}-{number:08d}"
        number += 1
        path = directory / f"{candidate}.md"
        if path.exists() or not reserver.claim(candidate):
            continue
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(content_for(candidate))
        except FileExistsError:
            continue
        note = reserver.unreserved_note(candidate)
        if note:
            print(note, file=sys.stderr)
        return candidate
    raise RuntimeError(f"could not allocate a free {prefix} id")


def _clean_cell(value: str) -> str:
    return " ".join(value.split()).replace("|", "\\|")


def create_theme(stage_root: Path, args: argparse.Namespace) -> int:
    zone = stage_topology.get_zone("roadmap", "themes")
    directory = stage_root / zone.canonical_path
    index_path = stage_root / zone.index_surfaces[0]
    template_path = _template_for("themes")
    if not directory.is_dir() or not index_path.is_file() or not template_path.is_file():
        raise RuntimeError("theme directory, index, or bundled template is missing")
    template = template_path.read_text(encoding="utf-8")

    def content_for(record_id: str) -> str:
        text = template.replace("TH-00000000 Title", f"{record_id} {args.title}")
        text = _set_field(text, "id", record_id)
        text = _replace_section(text, "Intent", args.intent)
        text = _replace_section(text, "Background", args.background)
        return text

    record_id = _create_atomic(
        directory, "TH", content_for, stage_root.parent
    )
    row = f"| {record_id} | {_clean_cell(args.title)} | [{record_id}.md]({record_id}.md) |"
    _ensure_index_row(index_path, record_id, row)
    print(f"{record_id}: theme created")
    return 0


def create_milestone(stage_root: Path, args: argparse.Namespace) -> int:
    if re.fullmatch(r"TH-\d{8}", args.theme) is None:
        print(f"refusing: --theme must look like TH-00000001, got {args.theme}", file=sys.stderr)
        return 2
    theme_path = stage_root / stage_topology.resolve_artifact_reference(
        args.theme
    ).candidate_paths[0]
    if not theme_path.is_file():
        print(f"refusing: theme not found: {args.theme}", file=sys.stderr)
        return 1
    zone = stage_topology.get_zone("roadmap", "milestones")
    directory = stage_root / zone.canonical_path
    index_path = stage_root / zone.index_surfaces[0]
    template_path = _template_for("milestones")
    if not directory.is_dir() or not index_path.is_file() or not template_path.is_file():
        raise RuntimeError("milestone directory, index, or bundled template is missing")
    template = template_path.read_text(encoding="utf-8")

    def content_for(record_id: str) -> str:
        text = template.replace("M-00000000 Title", f"{record_id} {args.title}")
        text = _set_field(text, "id", record_id)
        text = _set_field(text, "theme", args.theme)
        text = _replace_section(text, "Purpose", args.purpose)
        text = _replace_section(text, "Period", args.period)
        text = _replace_section(text, "Scope", args.scope)
        text = _replace_section(text, "Theme", args.theme)
        completion_criteria = "\n".join(
            f"- {LIST_MARKER_RE.sub('', criterion, count=1)}"
            for criterion in args.completion_criteria
        )
        text = _replace_section(text, "Completion criteria", completion_criteria)
        return text

    record_id = _create_atomic(
        directory, "M", content_for, stage_root.parent
    )
    row = (
        f"| {record_id} | {args.theme} | {_clean_cell(args.title)} | "
        f"{_clean_cell(args.period)} | [{record_id}.md]({record_id}.md) |"
    )
    _ensure_index_row(index_path, record_id, row)
    print(f"{record_id}: milestone created under {args.theme}")
    return 0


def _decision_content(
    template: str, decision_id: str, milestone: stage_roadmap.RoadmapRecord
) -> str:
    title = f"Pursue {milestone.record_id} {milestone.title}".strip()
    text = template.replace("DE-00000000 Title", f"{decision_id} {title}")
    text = _set_field(text, "id", decision_id)
    text = _set_field(text, "status", "decided")
    text, count = re.subn(
        r"^work_item:[^\n]*$",
        f"roadmap_item: {milestone.record_id}\n"
        "transition: pursuit\n"
        "predecessor:\n"
        "supersedes:",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError("decision template has no `work_item:` anchor")
    sections = {
        "Question": f"Should {milestone.record_id} enter active pursuit?",
        "Options": "- Open pursuit.\n- Keep the milestone planned.",
        "Principles applied": (
            "- SSOT — the decision chain is the sole owner of roadmap lifecycle.\n"
            "- Honesty — the milestone becomes active only after this decided record exists."
        ),
        "Chosen direction": f"Open pursuit for {milestone.record_id}.",
        "Reason": "The stage-roadmap command records the user-initiated pursuit transition.",
        "Follow-up": "Attribute work with the milestone field and keep the chain explicit.",
    }
    for heading, value in sections.items():
        text = _replace_section(text, heading, value)
    return text


def _closure_decision_content(
    template: str,
    decision_id: str,
    milestone: stage_roadmap.RoadmapRecord,
    predecessor: str,
    entries: tuple[stage_roadmap_closure.ClosureBasisEntry, ...],
    attestation: str,
) -> str:
    title = f"Close {milestone.record_id} {milestone.title}".strip()
    text = template.replace("DE-00000000 Title", f"{decision_id} {title}")
    text = _set_field(text, "id", decision_id)
    text = _set_field(text, "status", "decided")
    text, count = re.subn(
        r"^work_item:[^\n]*$",
        f"roadmap_item: {milestone.record_id}\n"
        "transition: closure\n"
        f"predecessor: {predecessor}\n"
        "supersedes:",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError("decision template has no `work_item:` anchor")
    sections = {
        "Question": f"Has {milestone.record_id} met its completion criteria?",
        "Options": "- Close the milestone with the frozen basis.\n- Keep pursuit active.",
        "Principles applied": (
            "- SSOT — each card owns its terminal_disposition.\n"
            "- Honesty — closure records exact terminal evidence and an explicit attestation."
        ),
        "Chosen direction": f"Close {milestone.record_id} on the frozen basis below.",
        "Reason": "Every linked work card is terminal at closure time.",
        "Follow-up": (
            "Promotion must revalidate this basis; reopening requires a decision that "
            f"supersedes {decision_id}."
        ),
    }
    for heading, value in sections.items():
        text = _replace_section(text, heading, value)
    basis_lines = [
        "| Work item | terminal_disposition |",
        "|---|---|",
        *[
            f"| {entry.work_item_id} | {entry.terminal_disposition} |"
            for entry in entries
        ],
    ]
    return (
        text.rstrip()
        + f"\n\n## {stage_roadmap_closure.FROZEN_BASIS_HEADING}\n\n"
        + "\n".join(basis_lines)
        + f"\n\n## {stage_roadmap_closure.ATTESTATION_HEADING}\n\n"
        + attestation.strip()
        + "\n"
    )


def _append_decision_ref(record_path: Path, decision_id: str) -> None:
    text = record_path.read_text(encoding="utf-8")
    fields = parse_frontmatter(record_path)
    refs = list(split_scope(fields.get("decision_refs", "")))
    if decision_id in refs:
        return
    refs.append(decision_id)
    record_path.write_text(
        _set_field(text, "decision_refs", ", ".join(refs)), encoding="utf-8"
    )


def _validate_decision_index(stage_root: Path) -> None:
    index_path = stage_root / refresh_decision_index.INDEX_RELATIVE
    refresh_decision_index.render_index(
        stage_root, index_path.read_text(encoding="utf-8")
    )


def open_pursuit(stage_root: Path, args: argparse.Namespace) -> int:
    if re.fullmatch(r"M-\d{8}", args.milestone) is None:
        print(
            f"refusing: milestone must look like M-00000001, got {args.milestone}",
            file=sys.stderr,
        )
        return 2
    reference = stage_topology.resolve_artifact_reference(args.milestone)
    milestone_path = stage_root / reference.candidate_paths[0]
    if not milestone_path.is_file():
        print(f"refusing: milestone not found: {args.milestone}", file=sys.stderr)
        return 1
    milestone = stage_roadmap.load_roadmap_record(milestone_path)
    state = stage_roadmap.roadmap_record_state(stage_root, milestone_path)
    if state.status == stage_roadmap.ROADMAP_ACTIVE:
        print(f"{args.milestone}: pursuit already active ({state.effective_head})")
        return 0
    if state.status == stage_roadmap.ROADMAP_CLOSED:
        print(
            "refusing: reopening a closed milestone belongs to a later transition",
            file=sys.stderr,
        )
        return 1
    if state.status == stage_roadmap.ROADMAP_INVALID or milestone.decision_refs:
        detail = state.issues[0].message if state.issues else "the chain has no effective decision"
        print(f"refusing: milestone decision chain is not openable: {detail}", file=sys.stderr)
        return 1

    records_dir, template, records_index = _chain_decision_target(stage_root)
    _validate_decision_index(stage_root)
    decision_id = _create_atomic(
        records_dir,
        "DE",
        lambda item_id: _decision_content(template, item_id, milestone),
        stage_root.parent,
    )
    _append_decision_ref(milestone_path, decision_id)
    _add_chain_decision_row(stage_root, records_index, decision_id, args.milestone)
    refresh_decision_index.refresh_index(stage_root.parent)
    print(f"{args.milestone}: pursuit active via {decision_id}")
    return 0


def close_milestone(stage_root: Path, args: argparse.Namespace) -> int:
    if re.fullmatch(r"M-\d{8}", args.milestone) is None:
        print(
            f"refusing: milestone must look like M-00000001, got {args.milestone}",
            file=sys.stderr,
        )
        return 2
    reference = stage_topology.resolve_artifact_reference(args.milestone)
    milestone_path = stage_root / reference.candidate_paths[0]
    if not milestone_path.is_file():
        print(f"refusing: milestone not found: {args.milestone}", file=sys.stderr)
        return 1
    milestone = stage_roadmap.load_roadmap_record(milestone_path)
    state = stage_roadmap.roadmap_record_state(stage_root, milestone_path)
    if state.status == stage_roadmap.ROADMAP_CLOSED:
        print(f"{args.milestone}: already closed ({state.effective_head})")
        return 0
    if state.status != stage_roadmap.ROADMAP_ACTIVE or state.effective_head is None:
        detail = state.issues[0].message if state.issues else f"status is {state.status}"
        print(
            f"refusing: milestone must have one active pursuit head before closure: {detail}",
            file=sys.stderr,
        )
        return 1

    entries, blockers = stage_roadmap_closure.closure_capture(
        stage_root, args.milestone
    )
    if blockers:
        print(
            f"refusing: {args.milestone} has non-terminal linked work:",
            file=sys.stderr,
        )
        for blocker in blockers:
            print(f"- {blocker}", file=sys.stderr)
        return 1

    records_dir, template, records_index = _chain_decision_target(stage_root)
    _validate_decision_index(stage_root)
    decision_id = _create_atomic(
        records_dir,
        "DE",
        lambda item_id: _closure_decision_content(
            template,
            item_id,
            milestone,
            state.effective_head or "",
            entries,
            args.attestation,
        ),
        stage_root.parent,
    )
    _append_decision_ref(milestone_path, decision_id)
    _add_chain_decision_row(stage_root, records_index, decision_id, args.milestone)
    refresh_decision_index.refresh_index(stage_root.parent)
    print(
        f"{args.milestone}: closed via {decision_id} "
        f"(frozen basis: {len(entries)} work cards)"
    )
    return 0


def list_roadmap(stage_root: Path, _args: argparse.Namespace) -> int:
    print("Themes")
    print("| Theme | Title | Status |")
    print("|---|---|---|")
    themes = stage_roadmap.roadmap_records(stage_root, "themes")
    if not themes:
        print("| — | — | none |")
    for record in themes:
        state = stage_roadmap.roadmap_record_state(stage_root, record.path)
        print(f"| {record.record_id} | {_clean_cell(record.title)} | {state.status} |")

    print("\nMilestones")
    print("| Milestone | Theme | Title | Status |")
    print("|---|---|---|---|")
    milestones = stage_roadmap.roadmap_records(stage_root, "milestones")
    if not milestones:
        print("| — | — | — | none |")
    for record in milestones:
        state = stage_roadmap.roadmap_record_state(stage_root, record.path)
        print(
            f"| {record.record_id} | {record.theme or '—'} | "
            f"{_clean_cell(record.title)} | {state.status} |"
        )
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage schema-v4 Stage roadmap records.")
    parser.add_argument("--project-root", default=".")
    commands = parser.add_subparsers(dest="command", required=True)

    theme = commands.add_parser("create-theme", help="Create a theme and sync its index.")
    theme.add_argument("--title", required=True)
    theme.add_argument("--intent", default="")
    theme.add_argument("--background", default="")
    theme.set_defaults(handler=create_theme)

    milestone = commands.add_parser(
        "create-milestone", help="Create a milestone under an existing theme."
    )
    milestone.add_argument("--theme", required=True)
    milestone.add_argument("--title", required=True)
    milestone.add_argument("--purpose", default="")
    milestone.add_argument("--period", default="")
    milestone.add_argument("--scope", default="")
    milestone.add_argument(
        "--completion-criteria",
        action="append",
        default=[],
        help="Milestone completion criterion written as a list item (repeatable).",
    )
    milestone.set_defaults(handler=create_milestone)

    pursuit = commands.add_parser(
        "open-pursuit", help="Create the initial milestone pursuit decision."
    )
    pursuit.add_argument("milestone")
    pursuit.set_defaults(handler=open_pursuit)

    closure = commands.add_parser(
        "close-milestone",
        help="Close a milestone with an immutable terminal-work basis.",
    )
    closure.add_argument("milestone")
    closure.add_argument(
        "--attestation",
        "--completion-criteria-attestation",
        dest="attestation",
        required=True,
        help="Exact text attesting that the milestone completion criteria were met.",
    )
    closure.set_defaults(handler=close_milestone)

    listing = commands.add_parser("list", help="List computed roadmap state.")
    listing.set_defaults(handler=list_roadmap)
    return parser


def main() -> int:
    args = _parser().parse_args()
    stage_root = Path(args.project_root).expanduser().resolve() / ".stage"
    if active_topology(stage_root) != ACTIVE_TOPOLOGY_V4:
        print(
            schema_migration_banner(stage_root)
            or "stage-roadmap requires a Stage project with schema_version: 4; no files changed.",
            file=sys.stderr,
        )
        return 2
    try:
        return args.handler(stage_root, args)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"stage-roadmap failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
