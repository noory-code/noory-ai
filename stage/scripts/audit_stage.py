#!/usr/bin/env python3
"""Audit a project-local .stage harness."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PLUGIN_ROOT / "templates" / "project-stage"
HOOK_ROOT = PLUGIN_ROOT / "hooks"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))
# Sibling modules load by bare name; file-path loads (tests) lack the script
# directory on sys.path, so insert it the same way the hooks bootstrap does.
SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import stage_guard  # noqa: E402
import stage_records  # noqa: E402
from stage_records import AuditedItem, RecordGraph  # noqa: E402


STATUS_VALUES = stage_guard.WORK_OPEN_STATUSES | stage_guard.WORK_FINAL_STATUSES
VERIFICATION_VALUES = stage_guard.VERIFICATION_DONE | {"pending"}
RETROSPECTIVE_VALUES = stage_guard.RETROSPECTIVE_DONE | {"pending"}
PROMOTION_VALUES = stage_guard.PROMOTION_FINAL | {"pending"}
DECISION_STATUS_VALUES = {"open", "decided", "promoted"}
BACKLOG_STATUS_VALUES = {"captured", "triaged", "ready", "selected", "deferred", "rejected"}
REQUIRED_WORK_FIELDS = (
    "id",
    "title",
    "status",
    "verification",
    "retrospective",
    "promotion",
    "scope",
)
ACTIVE_VIEW_STATUSES = {"active", "blocked"}
REVIEW_VIEW_STATUSES = {"review", "completed", "rejected"}
ITEM_LINK_RE = re.compile(r"\((?:\./)?items/([A-Za-z][A-Za-z0-9]*-\d{3,})\.md(?:#[^)]+)?\)")
# Prefix → owning locations. SSOT for the mapping = operations/artifacts.md
# §Artifact catalog; keep the two in lock-step.
RECORD_LOCATIONS: dict[str, tuple[str, ...]] = {
    "W": ("present/work/items", "past/work/archive/items"),
    "R": ("present/work/retrospectives", "past/work/archive/retrospectives"),
    "DE": ("present/work/decisions",),
    "D": ("past/decisions/records",),
    "O": ("present/state/observations",),
    "Q": ("present/state/questions",),
    "A": ("present/state/assumptions",),
    "K": ("present/state/risks",),
    "B": ("future/backlog/items",),
    "P": ("future/proposals",),
    "M": ("future/roadmap/milestones",),
}
RECORD_ID_RE = re.compile(r"^(?P<prefix>DE|[WRDOQAKBPM])-\d{3,}$")
HEADING_ID_RE = re.compile(r"^#\s+(?P<record_id>(?:DE|[WRDOQAKBPM])-\d{3,})\b", re.MULTILINE)
# Locations without an ID prefix still need index.md routing coverage.
ROUTING_ONLY_LOCATIONS: tuple[str, ...] = (
    "past/canon/principles",
    "past/canon/vocabulary",
    "past/canon/invariants",
    "past/model/components",
    "past/model/boundaries",
    "past/model/interfaces",
    "future/roadmap/themes",
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str = ""

    def to_dict(self) -> dict[str, str]:
        data = {"severity": self.severity, "code": self.code, "message": self.message}
        if self.path:
            data["path"] = self.path
        return data


class Audit:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.stage_root = project_root / ".stage"
        self.findings: list[Finding] = []

    def error(self, code: str, message: str, path: Path | str = "") -> None:
        self.findings.append(Finding("error", code, message, self.display_path(path)))

    def warning(self, code: str, message: str, path: Path | str = "") -> None:
        self.findings.append(Finding("warning", code, message, self.display_path(path)))

    def display_path(self, path: Path | str) -> str:
        if not path:
            return ""
        candidate = Path(path)
        try:
            if candidate.is_absolute():
                return str(candidate.relative_to(self.project_root))
        except ValueError:
            pass
        return str(path).replace("\\", "/")

    def run(self) -> list[Finding]:
        if not self.stage_root.exists():
            self.error("STAGE001", "Stage root not found.", self.stage_root)
            return self.findings
        if not self.stage_root.is_dir():
            self.error("STAGE002", "Stage root is not a directory.", self.stage_root)
            return self.findings

        self.audit_template_files()
        graph = RecordGraph(self.stage_root)
        items = self.audit_work_items(graph)
        self.audit_hierarchy(items)
        self.audit_work_indexes(items)
        self.audit_backlog_items(graph)
        self.audit_lineage(graph)
        self.audit_bidirectional_lineage(graph)
        self.audit_orphan_records(graph)
        self.audit_state_links(graph)
        self.audit_archive_records(graph)
        self.audit_family_shapes()
        self.audit_record_ownership()
        self.audit_routing()
        self.audit_catalog_sync()
        self.audit_canon()
        self.audit_governance()
        return self.findings

    def audit_template_files(self) -> None:
        if not TEMPLATE_ROOT.exists():
            self.error("TEMPLATE001", "Stage template root not found.", TEMPLATE_ROOT)
            return

        for template_path in sorted(TEMPLATE_ROOT.rglob("*")):
            if template_path.is_dir():
                continue
            relative = template_path.relative_to(TEMPLATE_ROOT)
            target = self.stage_root / relative
            if not target.exists():
                self.warning(
                    "TEMPLATE002",
                    "Stage template artifact file is missing. Re-run stage-init to repair.",
                    target,
                )
            elif not target.is_file():
                # A directory (or other non-file) squatting a required file's
                # name reads as "present" to a plain existence check.
                self.error(
                    "TEMPLATE003",
                    "Stage template artifact exists but is not a regular file.",
                    target,
                )

    def audit_work_items(self, graph: RecordGraph) -> list[AuditedItem]:
        # Duplicate detection is scan-order policy: the first occurrence owns
        # the id, every later one reports both paths.
        seen_ids: dict[str, Path] = {}
        for audited_item in graph.work:
            self.audit_work_item_fields(audited_item)
            item = audited_item.item
            previous = seen_ids.get(item.item_id)
            if previous is not None:
                self.error("WORK007", f"Duplicate work item id: {item.item_id}", item.path)
                self.error("WORK007", f"Duplicate work item id: {item.item_id}", previous)
            else:
                seen_ids[item.item_id] = item.path

        return graph.work

    def audit_work_item_fields(self, audited_item: AuditedItem) -> None:
        item = audited_item.item
        path = item.path

        for field in REQUIRED_WORK_FIELDS:
            if field not in audited_item.fields:
                self.error("WORK001", f"Work item frontmatter field is missing: {field}", path)

        if item.item_id != path.stem:
            self.error("WORK002", f"Work item id differs from filename: {item.item_id}", path)
        if item.status not in STATUS_VALUES:
            self.error("WORK003", f"Unknown status value: {item.status}", path)
        if item.verification not in VERIFICATION_VALUES:
            self.error("WORK004", f"Unknown verification value: {item.verification}", path)
        if item.retrospective not in RETROSPECTIVE_VALUES:
            self.error("WORK005", f"Unknown retrospective value: {item.retrospective}", path)
        if item.promotion not in PROMOTION_VALUES:
            self.error("WORK006", f"Unknown promotion value: {item.promotion}", path)
        if item.kind and item.kind not in self.known_kinds():
            self.warning(
                "KIND001",
                f"Work kind `{item.kind}` has no `passed` criterion in operations/verification.md.",
                path,
            )

        for blocker in stage_guard.item_completion_blockers(item):
            self.error("WORK008", f"Completion gate is not closed: {blocker}", path)

        if item.retrospective == "completed":
            self.audit_retrospective_ref(audited_item)

        self.audit_decision_refs(audited_item)

        if audited_item.location == "present" and item.status == "archived":
            self.error(
                "WORK009",
                "An archived work item must move to past/work/archive/items/.",
                path,
            )
        if audited_item.location == "archive" and item.status != "archived":
            self.error(
                "WORK010",
                "Work items in past/work/archive/items/ must have status archived.",
                path,
            )

    def audit_retrospective_ref(self, audited_item: AuditedItem) -> None:
        item = audited_item.item
        raw_ref = audited_item.fields.get("retrospective_ref", "").strip()
        if not raw_ref:
            self.error(
                "WORK011",
                f"A retrospective-completed item has no retrospective_ref: {item.item_id}",
                item.path,
            )
            return

        retro_path = stage_records.resolve_retrospective_ref(
            self.project_root, self.stage_root, raw_ref, audited_item.location
        )
        if not retro_path.exists():
            self.error("WORK012", f"retrospective_ref file not found: {raw_ref}", item.path)
            return

        retro_fields = stage_guard.parse_frontmatter(retro_path)
        linked_item = retro_fields.get("work_item", "").strip()
        if linked_item != item.item_id:
            self.error(
                "WORK013",
                f"Retrospective work_item does not match the work item: {linked_item or 'missing'}",
                retro_path,
            )

    def audit_decision_refs(self, audited_item: AuditedItem) -> None:
        item = audited_item.item
        raw_refs = audited_item.fields.get("decision_refs", "").strip()
        if not raw_refs:
            return

        for raw_ref in stage_guard.split_scope(raw_refs):
            decision_path = stage_records.resolve_decision_ref(
                self.project_root, self.stage_root, raw_ref
            )
            if not decision_path.exists():
                self.error("WORK014", f"decision_refs file not found: {raw_ref}", item.path)
                continue
            decision_fields = stage_guard.parse_frontmatter(decision_path)
            linked_item = decision_fields.get("work_item", "").strip()
            if linked_item != item.item_id:
                self.error(
                    "WORK015",
                    f"Decision record work_item does not match the work item: {linked_item or 'missing'}",
                    decision_path,
                )
            # Status and principle-citation checks run once over all decision
            # records in audit_orphan_records, so they are not repeated here.

    def audit_decision_principles(self, decision_path: Path) -> None:
        try:
            text = decision_path.read_text(encoding="utf-8")
        except OSError:
            return
        match = re.search(r"^## Principles applied\s*$(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
        section = (match.group(1).strip() if match else "")
        if not section:
            self.error(
                "WORK021",
                "Decision record has an empty `Principles applied` section — decisions must cite their governing principles.",
                decision_path,
            )
            return
        known = self.known_principles()
        if known and not any(name in section for name in known):
            self.error(
                "WORK022",
                "Decision record cites no principle from past/canon/principles.md.",
                decision_path,
            )

    def audit_hierarchy(self, audited_items: list[AuditedItem]) -> None:
        by_id = {entry.item.item_id: entry for entry in audited_items}

        for entry in audited_items:
            parent_id = entry.item.parent
            if not parent_id:
                continue
            parent = by_id.get(parent_id)
            if parent is None:
                self.error(
                    "WORK017",
                    f"Parent work item not found: {parent_id}",
                    entry.item.path,
                )
                continue
            if stage_guard.item_is_open(entry.item) and parent.item.status in stage_guard.WORK_FINAL_STATUSES:
                self.error(
                    "WORK019",
                    f"Open work item has a finalized parent ({parent.item.status}): "
                    f"{entry.item.item_id} -> {parent_id}",
                    entry.item.path,
                )

        for entry in audited_items:
            seen: list[str] = []
            cursor = entry.item.item_id
            while cursor:
                if cursor in seen:
                    self.error(
                        "WORK018",
                        "Parent chain forms a cycle: " + " -> ".join(seen + [cursor]),
                        entry.item.path,
                    )
                    break
                seen.append(cursor)
                parent_entry = by_id.get(cursor)
                cursor = parent_entry.item.parent if parent_entry else ""

    def audit_work_indexes(self, audited_items: list[AuditedItem]) -> None:
        present_items = [entry.item for entry in audited_items if entry.location == "present"]
        known_ids = {item.item_id for item in present_items}
        active_ids, active_unknown = self.mentioned_item_ids(
            self.stage_root / "present" / "work" / "active.md", known_ids
        )
        review_ids, review_unknown = self.mentioned_item_ids(
            self.stage_root / "present" / "work" / "review.md", known_ids
        )

        for unknown_id in sorted(active_unknown):
            self.error(
                "INDEX001",
                f"active.md references a work item that does not exist: {unknown_id}",
                "present/work/active.md",
            )
        for unknown_id in sorted(review_unknown):
            self.error(
                "INDEX002",
                f"review.md references a work item that does not exist: {unknown_id}",
                "present/work/review.md",
            )

        by_id = {item.item_id: item for item in present_items}
        for item in present_items:
            if item.status in ACTIVE_VIEW_STATUSES and item.item_id not in active_ids:
                self.error(
                    "INDEX003",
                    f"An active work item is missing from the active.md index: {item.item_id}",
                    item.path,
                )
            if item.status in REVIEW_VIEW_STATUSES and item.item_id not in review_ids:
                self.error(
                    "INDEX004",
                    f"A review/completed/rejected work item is missing from the review.md index: {item.item_id}",
                    item.path,
                )

        for item_id in sorted(active_ids):
            item = by_id.get(item_id)
            if item and item.status not in ACTIVE_VIEW_STATUSES:
                self.error(
                    "INDEX005",
                    f"An active.md entry does not have status active/blocked: {item_id}",
                    item.path,
                )
        for item_id in sorted(review_ids):
            item = by_id.get(item_id)
            if item and item.status not in REVIEW_VIEW_STATUSES:
                self.error(
                    "INDEX006",
                    f"A review.md entry does not have status review/completed/rejected: {item_id}",
                    item.path,
                )

    def mentioned_item_ids(self, path: Path, known_ids: set[str]) -> tuple[set[str], set[str]]:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            self.error("INDEX000", "Work index file cannot be read.", path)
            return set(), set()

        linked_ids = set(ITEM_LINK_RE.findall(text))
        return linked_ids & known_ids, linked_ids - known_ids

    def audit_backlog_items(self, graph: RecordGraph) -> None:
        for node in graph.backlog:
            path = node.path
            item_id = node.record_id
            status = (node.fields.get("status") or "").strip().lower()
            if status not in BACKLOG_STATUS_VALUES:
                self.error("BACKLOG001", f"Unknown backlog status: {status or 'missing'}", path)
            if not (path.stem == item_id or path.stem.startswith(item_id + "-")):
                self.error(
                    "BACKLOG003",
                    f"Backlog filename does not start with its id: {item_id}",
                    path,
                )

            realized_by = (node.fields.get("realized_by") or "").strip()
            if status == "selected" and not realized_by:
                self.warning(
                    "BACKLOG004",
                    f"Selected backlog item has no realized_by work item: {item_id}",
                    path,
                )
            if realized_by and realized_by not in graph.work_ids:
                self.error(
                    "BACKLOG005",
                    f"realized_by work item not found: {realized_by}",
                    path,
                )

        for node in graph.backlog_by_id.values():
            parent_id = (node.fields.get("parent") or "").strip()
            if parent_id and parent_id not in graph.backlog_by_id:
                self.error(
                    "BACKLOG002",
                    f"Parent backlog item not found: {parent_id}",
                    node.path,
                )

    def audit_bidirectional_lineage(self, graph: RecordGraph) -> None:
        """B↔W must point at EACH OTHER, not merely both exist — a one-sided
        link means the lineage graph silently disagrees with itself."""
        for edge in graph.edges("work", "source"):
            if not edge.ref or edge.ref not in graph.backlog_by_id:
                continue
            back = (graph.backlog_by_id[edge.ref].fields.get("realized_by") or "").strip()
            if back != edge.src_id:
                self.error(
                    "WORK023",
                    f"Lineage is one-sided: work item declares source {edge.ref}, but that backlog "
                    f"item's realized_by is {back or 'empty'}.",
                    edge.src_path,
                )
        for node in graph.backlog_by_id.values():
            realized_by = (node.fields.get("realized_by") or "").strip()
            if not realized_by or realized_by not in graph.work_source_by_id:
                continue
            if graph.work_source_by_id.get(realized_by) != node.record_id:
                self.error(
                    "BACKLOG006",
                    f"Lineage is one-sided: backlog item declares realized_by {realized_by}, but "
                    f"that work item's source is {graph.work_source_by_id.get(realized_by) or 'empty'}.",
                    node.path,
                )

    def audit_orphan_records(self, graph: RecordGraph) -> None:
        """Every decision and retrospective record is validated on its own —
        not only when a work item happens to reference it — so an orphan with a
        missing `work_item`, bad status, or no principle citation is caught."""
        for node in graph.decisions:
            work_item = (node.fields.get("work_item") or "").strip()
            if not work_item or work_item not in graph.work_ids:
                self.error(
                    "DECISION001",
                    f"Decision record work_item references a missing work item: {work_item or 'empty'}",
                    node.path,
                )
            status = (node.fields.get("status") or "").strip().lower()
            if status not in DECISION_STATUS_VALUES:
                self.error(
                    "WORK016",
                    f"Unknown decision record status: {status or 'missing'}",
                    node.path,
                )
            self.audit_decision_principles(node.path)

        for edge in graph.edges("retrospective", "work_item"):
            if not edge.ref or edge.ref not in graph.work_ids:
                self.error(
                    "RETRO001",
                    f"Retrospective work_item references a missing work item: {edge.ref or 'empty'}",
                    edge.src_path,
                )

    def audit_lineage(self, graph: RecordGraph) -> None:
        for edge in graph.edges("work", "source"):
            if edge.ref and edge.ref not in graph.backlog_ids:
                self.error(
                    "WORK020",
                    f"source backlog item not found: {edge.ref}",
                    edge.src_path,
                )

    def audit_state_links(self, graph: RecordGraph) -> None:
        for edge in graph.edges("state", "work_items", multi=True):
            if edge.ref not in graph.work_ids:
                self.error(
                    "STATE001",
                    f"work_items references a missing work item: {edge.ref}",
                    edge.src_path,
                )

    def audit_archive_records(self, graph: RecordGraph) -> None:
        """Archived items keep their transition evidence: every archived item
        has an archive-index row whose Final status records the terminal state
        the `archived` overwrite erased, a completed transition keeps its
        closed gates, and every archived item keeps a completed retrospective
        (rejection reasons are learning assets too)."""
        index_path = self.stage_root / "past" / "work" / "archive" / "index.md"
        final_by_id: dict[str, str] = {}
        for cells in stage_guard.parse_index_rows(index_path):
            if cells and cells[0].strip():
                final_by_id.setdefault(
                    cells[0].strip(), cells[1].strip().lower() if len(cells) > 1 else ""
                )

        archived_ids: set[str] = set()
        for entry in graph.work:
            if entry.location != "archive":
                continue
            item = entry.item
            archived_ids.add(item.item_id)
            final = final_by_id.get(item.item_id)
            if final is None:
                self.error(
                    "ARCHIVE001",
                    f"Archived item has no archive index row: {item.item_id}",
                    item.path,
                )
            elif final not in {"completed", "rejected"}:
                self.error(
                    "ARCHIVE002",
                    f"Archive index Final status must be completed or rejected: "
                    f"{item.item_id} `{final or 'missing'}`",
                    index_path,
                )
            if final == "completed":
                open_gates = []
                if item.verification not in stage_guard.VERIFICATION_DONE:
                    open_gates.append(f"verification `{item.verification}`")
                if item.promotion not in stage_guard.PROMOTION_FINAL:
                    open_gates.append(f"promotion `{item.promotion}`")
                if open_gates:
                    self.error(
                        "ARCHIVE003",
                        "Archived completed item has open gates: " + ", ".join(open_gates),
                        item.path,
                    )
            if item.retrospective not in stage_guard.RETROSPECTIVE_DONE or not item.retrospective_ref:
                self.error(
                    "ARCHIVE003",
                    "Archived item has no completed retrospective "
                    f"(rejection reasons are learning assets too): retrospective `{item.retrospective}`",
                    item.path,
                )

        for row_id in final_by_id:
            if row_id not in archived_ids:
                self.error(
                    "ARCHIVE004",
                    f"Archive index row references a missing archived item: {row_id}",
                    index_path,
                )

    def audit_family_shapes(self) -> None:
        required = {
            self.stage_root / "present" / "work" / "retrospectives": ("id", "work_item"),
            self.stage_root / "past" / "work" / "archive" / "retrospectives": ("id", "work_item"),
            self.stage_root / "present" / "work" / "decisions": ("id", "work_item", "status"),
        }
        for family_root, keys in required.items():
            if not family_root.exists():
                continue
            for path in sorted(family_root.glob("*.md")):
                if path.name in {"README.md", "_template.md"}:
                    continue
                fields = stage_guard.parse_frontmatter(path)
                missing = [key for key in keys if key not in fields]
                if missing:
                    self.warning(
                        "FAMILY001",
                        "Record does not follow its family frontmatter shape; missing: " + ", ".join(missing),
                        path,
                    )

    def audit_record_ownership(self) -> None:
        """SSOT + responsibility boundaries over every ID-bearing record file.

        The prefix → location catalog mirrors `operations/artifacts.md`
        §Artifact catalog (that document is the SSOT for the mapping).
        """
        work_item_dirs = set(RECORD_LOCATIONS["W"])
        by_id: dict[str, list[Path]] = {}
        for path in sorted(self.stage_root.rglob("*.md")):
            relative_parent = path.parent.relative_to(self.stage_root).as_posix()
            if relative_parent.startswith(".runtime"):
                continue
            if path.name in {"README.md", "_template.md"}:
                continue
            fields = stage_guard.parse_frontmatter(path)
            record_id = fields.get("id") or ""
            if not record_id:
                # Proposal / milestone / approved-decision templates are
                # body-only: the ID lives in the first heading.
                try:
                    heading = HEADING_ID_RE.search(path.read_text(encoding="utf-8"))
                except OSError:
                    heading = None
                if heading:
                    record_id = heading.group("record_id")
            match = RECORD_ID_RE.match(record_id)
            if not match:
                continue
            by_id.setdefault(record_id, []).append(path)

            prefix = match.group("prefix")
            allowed = RECORD_LOCATIONS.get(prefix)
            if allowed is not None and relative_parent not in allowed:
                self.error(
                    "OWN001",
                    f"Record {record_id} lives outside its owning location "
                    f"({' or '.join(allowed)}). See operations/artifacts.md §Artifact catalog.",
                    path,
                )

        for record_id, paths in sorted(by_id.items()):
            if len(paths) < 2:
                continue
            parents = {path.parent.relative_to(self.stage_root).as_posix() for path in paths}
            if parents <= work_item_dirs:
                continue  # WORK007 owns duplicates within the work-item dirs.
            for path in paths:
                self.error(
                    "SSOT001",
                    f"Duplicate record id {record_id}: one durable fact must have exactly "
                    "one owning file.",
                    path,
                )

    def audit_routing(self) -> None:
        """Every existing artifact location must be reachable from `index.md` routing."""
        index_path = self.stage_root / "index.md"
        try:
            index_text = index_path.read_text(encoding="utf-8")
        except OSError:
            return  # TEMPLATE002 already reports the missing index.

        # Match exact routed cells, not any substring: a longer path in another
        # row (`future/proposals/index.md`) must NOT satisfy the route for
        # `future/proposals/`. Each backtick-quoted token in the index is a
        # routed target; compare against the whole token.
        routed_cells = {token.strip().rstrip("/") for token in re.findall(r"`([^`]+)`", index_text)}

        routed_locations = [
            location for locations in RECORD_LOCATIONS.values() for location in locations
        ] + list(ROUTING_ONLY_LOCATIONS)
        for location in routed_locations:
            if (self.stage_root / location).is_dir() and location not in routed_cells:
                self.warning(
                    "ROUTE001",
                    f"Existing artifact location `{location}/` is not routed in index.md.",
                    self.stage_root / location,
                )

        operations_root = self.stage_root / "operations"
        if operations_root.is_dir():
            for path in sorted(operations_root.glob("*.md")):
                if path.name == "README.md":
                    continue
                if f"operations/{path.name}" not in routed_cells:
                    self.warning(
                        "ROUTE002",
                        f"Operations document `operations/{path.name}` is not routed in index.md.",
                        path,
                    )

    def audit_catalog_sync(self) -> None:
        """The artifact catalog is the SSOT for prefix→location; the audit's
        RECORD_LOCATIONS must not silently drift from it (P32). Parse the
        catalog table and compare each prefix's primary location to the code.
        """
        catalog_path = self.stage_root / "operations" / "artifacts.md"
        try:
            text = catalog_path.read_text(encoding="utf-8")
        except OSError:
            return  # TEMPLATE002 already reports a missing catalog.

        catalog: dict[str, str] = {}
        row_re = re.compile(r"^\|\s*`([A-Z]+)-`\s*\|[^|]*\|\s*`([^`]+?)/?`\s*\|", re.MULTILINE)
        for prefix, location in row_re.findall(text):
            location = location.rstrip("/")
            if prefix in catalog and catalog[prefix] != location:
                self.error(
                    "CATALOG001",
                    f"Artifact catalog has conflicting rows for prefix `{prefix}-` "
                    f"(`{catalog[prefix]}/` and `{location}/`); one prefix must have one location.",
                    catalog_path,
                )
            catalog[prefix] = location

        for prefix, locations in RECORD_LOCATIONS.items():
            primary = locations[0]
            catalog_location = catalog.get(prefix)
            if catalog_location is None:
                self.error(
                    "CATALOG001",
                    f"Artifact catalog has no row for prefix `{prefix}-`, but the audit maps it to "
                    f"`{primary}/`. Keep operations/artifacts.md and RECORD_LOCATIONS in lock-step.",
                    catalog_path,
                )
            elif catalog_location != primary:
                self.error(
                    "CATALOG001",
                    f"Artifact catalog routes `{prefix}-` to `{catalog_location}/` but the audit "
                    f"maps it to `{primary}/`. Keep operations/artifacts.md and RECORD_LOCATIONS in "
                    "lock-step.",
                    catalog_path,
                )

        # The catalog is the SSOT: a prefix it adds but the audit does not map
        # would be silently unsupported by ownership/routing checks.
        for prefix, catalog_location in catalog.items():
            if prefix not in RECORD_LOCATIONS:
                self.error(
                    "CATALOG001",
                    f"Artifact catalog declares prefix `{prefix}-` (`{catalog_location}/`) that the "
                    "audit does not map in RECORD_LOCATIONS; ownership and routing checks would skip "
                    "it. Keep the two in lock-step.",
                    catalog_path,
                )

    def audit_canon(self) -> None:
        principles_path = self.stage_root / "past" / "canon" / "principles.md"
        try:
            text = principles_path.read_text(encoding="utf-8")
        except OSError:
            self.error("CANON001", "past/canon/principles.md is missing — the harness core principles are gone.", principles_path)
            return
        markers = ("SSOT", "MECE", "Fail Fast", "AHA", "## Completion principle", "## Behavior principles")
        missing = [marker for marker in markers if marker not in text]
        if missing:
            self.error(
                "CANON001",
                "Core principles are missing from past/canon/principles.md: " + ", ".join(missing),
                principles_path,
            )

    def audit_governance(self) -> None:
        settings_path = self.stage_root / "settings.json"
        if not settings_path.exists():
            return
        if stage_guard.governance_broken(self.stage_root):
            self.error("GOV000", "settings.json is unreadable or malformed (hooks fail closed until repaired).", settings_path)
            return
        governance = stage_guard.load_governance(self.stage_root)
        legacy_keys = [key for key in ("extensions", "paths") if isinstance(governance.get(key), list) and governance.get(key)]
        if legacy_keys:
            self.warning(
                "GOV001",
                "Governance uses an allowlist (" + ", ".join(legacy_keys) + ") — narrower than the broad default.",
                settings_path,
            )
        narrowing = []
        for key in ("exclude_paths", "exclude_extensions"):
            values = governance.get(key)
            if isinstance(values, list) and values:
                narrowing.extend(str(value) for value in values)
        if narrowing:
            self.warning(
                "GOV002",
                "Governance excludes paths/extensions from the broad default: " + ", ".join(narrowing[:8]),
                settings_path,
            )

    def known_kinds(self) -> set[str]:
        if not hasattr(self, "_known_kinds"):
            self._known_kinds = self.parse_table_first_cells(
                self.stage_root / "operations" / "verification.md"
            )
        return self._known_kinds

    def known_principles(self) -> set[str]:
        if not hasattr(self, "_known_principles"):
            cells = self.parse_table_first_cells(self.stage_root / "past" / "canon" / "principles.md")
            self._known_principles = {cell.split(" (")[0].strip() for cell in cells if cell}
        return self._known_principles

    def parse_table_first_cells(self, path: Path) -> set[str]:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return set()
        cells: set[str] = set()
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            first = stripped.strip("|").split("|")[0].strip().strip("`")
            if first and not re.fullmatch(r":?-{2,}:?", first) and first.lower() not in {"kind", "principle", "field", "prefix", "status"}:
                cells.add(first.lower() if path.name == "verification.md" else first)
        return cells


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the .stage artifact structure and work status.")
    parser.add_argument("--project-root", default=".", help="Project root. Defaults to the current directory.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    return parser.parse_args()


def render_text(project_root: Path, findings: list[Finding]) -> str:
    errors = sum(1 for finding in findings if finding.severity == "error")
    warnings = sum(1 for finding in findings if finding.severity == "warning")
    lines = [f"Stage audit: {project_root / '.stage'}"]
    if not findings:
        lines.append("OK: no findings")
    for finding in findings:
        location = f" [{finding.path}]" if finding.path else ""
        lines.append(f"{finding.severity.upper()} {finding.code}{location}: {finding.message}")
    lines.append(f"Summary: errors={errors}, warnings={warnings}")
    return "\n".join(lines)


def render_json(project_root: Path, findings: list[Finding]) -> str:
    payload: dict[str, Any] = {
        "stage_root": str(project_root / ".stage"),
        "summary": {
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
        },
        "findings": [finding.to_dict() for finding in findings],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    audit = Audit(project_root)
    findings = audit.run()

    if args.format == "json":
        print(render_json(project_root, findings))
    else:
        print(render_text(project_root, findings))

    has_errors = any(finding.severity == "error" for finding in findings)
    has_warnings = any(finding.severity == "warning" for finding in findings)
    if has_errors or (args.strict and has_warnings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
