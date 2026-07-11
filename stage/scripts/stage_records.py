"""Typed record graph for the Stage audit.

Scans every frontmattered record once and exposes typed nodes plus reference
edges, so link checks read one shared graph instead of re-globbing and
re-parsing their own corner of the tree.

Reference topology of the `.stage` record space (frontmatter field -> target):

| src family    | field             | target family | notes                       |
|---------------|-------------------|---------------|-----------------------------|
| work          | parent            | work          | hierarchy (cycle/final gate)|
| work          | source            | backlog       | symmetric with realized_by  |
| work          | retrospective_ref | retrospective | path ref, back: work_item   |
| work          | decision_refs     | decision      | path refs, back: work_item  |
| backlog       | parent            | backlog       |                             |
| backlog       | realized_by       | work          | symmetric with source       |
| decision      | work_item         | work          | required (orphan check)     |
| retrospective | work_item         | work          | required (orphan check)     |
| state         | work_items        | work          | multi-valued                |

The audit owns which finding each broken edge raises and reads some fields
node-locally where finding order or status coupling demands it; `edges()`
serves the uniform dangling-reference sweeps.
"""

# The audit must run wherever `python3` points on a host machine (3.9+), so
# this module keeps the same annotation-laziness contract as audit_stage.py.
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HOOK_ROOT = PLUGIN_ROOT / "hooks"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))

import stage_guard  # noqa: E402


SKIP_NAMES = {"README.md", "_template.md"}
# Proposal / milestone / approved-decision records are body-only: the ID
# lives in the first heading instead of frontmatter.
HEADING_ID_RE = re.compile(r"^#\s+(?P<record_id>(?:DE|[WRDOQAKBPM])-\d{3,})\b", re.MULTILINE)


@dataclass(frozen=True)
class AuditedItem:
    item: stage_guard.WorkItem
    fields: dict[str, str]
    location: str


@dataclass(frozen=True)
class RecordNode:
    record_id: str
    path: Path
    fields: dict[str, str]


@dataclass(frozen=True)
class Edge:
    src_id: str
    src_path: Path
    field: str
    ref: str


def _scan_nodes(roots: tuple[Path, ...]) -> list[RecordNode]:
    """Frontmattered records in scan order (roots in the given order, sorted
    filenames within each). Body-only legacy files carry no frontmatter and
    are not part of the record graph — matching what the audit inspects."""
    nodes: list[RecordNode] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.glob("*.md")):
            if path.name in SKIP_NAMES:
                continue
            fields = stage_guard.parse_frontmatter(path)
            if not fields:
                continue
            record_id = (fields.get("id") or "").strip() or path.stem
            nodes.append(RecordNode(record_id=record_id, path=path, fields=fields))
    return nodes


def _scan_heading_nodes(roots: tuple[Path, ...]) -> list[RecordNode]:
    """Body-only records in scan order, identified by their first-heading ID.
    Files without a heading ID (and index/README/template files) are not part
    of the record graph."""
    nodes: list[RecordNode] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.glob("*.md")):
            if path.name in SKIP_NAMES or path.name == "index.md":
                continue
            try:
                match = HEADING_ID_RE.search(path.read_text(encoding="utf-8"))
            except OSError:
                continue
            if match:
                nodes.append(
                    RecordNode(record_id=match.group("record_id"), path=path, fields={})
                )
    return nodes


class RecordGraph:
    def __init__(self, stage_root: Path) -> None:
        # Work items keep every file — one with no frontmatter still becomes a
        # node (and fails the required-field checks), unlike the other
        # families, where body-only files are legacy and stay unaudited.
        self.work: list[AuditedItem] = []
        for location, root in (
            ("present", stage_root / "present" / "work" / "items"),
            ("archive", stage_root / "past" / "work" / "archive" / "items"),
        ):
            if not root.exists():
                continue
            for path in sorted(root.glob("*.md")):
                if path.name in SKIP_NAMES:
                    continue
                fields = stage_guard.parse_frontmatter(path)
                self.work.append(
                    AuditedItem(
                        item=stage_guard.item_from_fields(
                            path, fields, stage_guard.AUDIT_FIELD_DEFAULTS
                        ),
                        fields=fields,
                        location=location,
                    )
                )

        self.backlog: list[RecordNode] = _scan_nodes(
            (stage_root / "future" / "backlog" / "items",)
        )
        self.decisions: list[RecordNode] = _scan_nodes(
            (stage_root / "present" / "work" / "decisions",)
        )
        self.retrospectives: list[RecordNode] = _scan_nodes(
            (
                stage_root / "present" / "work" / "retrospectives",
                stage_root / "past" / "work" / "archive" / "retrospectives",
            )
        )
        self.state: list[RecordNode] = _scan_nodes(
            tuple(
                stage_root / "present" / "state" / family
                for family in ("observations", "questions", "assumptions", "risks")
            )
        )
        self.milestones: list[RecordNode] = _scan_heading_nodes(
            (stage_root / "future" / "roadmap" / "milestones",)
        )
        self.proposals: list[RecordNode] = _scan_heading_nodes(
            (stage_root / "future" / "proposals",)
        )

        self.work_ids: set[str] = {entry.item.item_id for entry in self.work}
        self.backlog_ids: set[str] = {node.record_id for node in self.backlog}
        # Duplicate ids keep the first position and the LAST node/source —
        # the same shape the audit's per-id dict builds historically produced.
        self.backlog_by_id: dict[str, RecordNode] = {}
        for node in self.backlog:
            self.backlog_by_id[node.record_id] = node
        self.work_source_by_id: dict[str, str] = {
            entry.item.item_id: (entry.fields.get("source") or "").strip() for entry in self.work
        }

    def edges(self, family: str, field: str, multi: bool = False) -> list[Edge]:
        """Id-reference edges for one (family, field), in node scan order.

        A single-valued field yields one edge per node with the stripped value
        (empty included, so a required-link check treats "" as dangling); a
        multi-valued field is split like a scope declaration."""
        if family == "work":
            nodes = [(entry.item.item_id, entry.item.path, entry.fields) for entry in self.work]
        else:
            family_nodes = {
                "backlog": self.backlog,
                "decision": self.decisions,
                "retrospective": self.retrospectives,
                "state": self.state,
            }[family]
            nodes = [(node.record_id, node.path, node.fields) for node in family_nodes]
        edges: list[Edge] = []
        for record_id, path, fields in nodes:
            raw = (fields.get(field) or "").strip()
            if multi:
                for ref in stage_guard.split_scope(raw):
                    edges.append(Edge(src_id=record_id, src_path=path, field=field, ref=ref))
            else:
                edges.append(Edge(src_id=record_id, src_path=path, field=field, ref=raw))
        return edges


def resolve_retrospective_ref(
    project_root: Path, stage_root: Path, raw_ref: str, location: str = "present"
) -> Path:
    ref = stage_guard.normalize_path_text(raw_ref)
    if ref.startswith(".stage/"):
        return project_root / ref
    if ref.startswith("present/work/retrospectives/") or ref.startswith("past/work/archive/retrospectives/"):
        return stage_root / ref
    local_root = (
        stage_root / "past" / "work" / "archive"
        if location == "archive"
        else stage_root / "present" / "work"
    )
    if ref.startswith("retrospectives/"):
        return local_root / ref
    if "/" in ref:
        return stage_root / ref
    filename = ref if ref.endswith(".md") else f"{ref}.md"
    return local_root / "retrospectives" / filename


def resolve_decision_ref(project_root: Path, stage_root: Path, raw_ref: str) -> Path:
    ref = stage_guard.normalize_path_text(raw_ref)
    if ref.startswith(".stage/"):
        return project_root / ref
    if ref.startswith("present/work/decisions/"):
        return stage_root / ref
    if ref.startswith("decisions/"):
        return stage_root / "present" / "work" / ref
    if "/" in ref:
        return stage_root / ref
    filename = ref if ref.endswith(".md") else f"{ref}.md"
    return stage_root / "present" / "work" / "decisions" / filename
