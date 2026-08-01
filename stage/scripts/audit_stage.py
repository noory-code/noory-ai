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
V4_TEMPLATE_ROOT = PLUGIN_ROOT / "templates" / "v4" / "project-stage"
HOOK_ROOT = PLUGIN_ROOT / "hooks"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))
# Sibling modules load by bare name; file-path loads (tests) lack the script
# directory on sys.path, so insert it the same way the hooks bootstrap does.
SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import stage_guard  # noqa: E402
import guidance_docs  # noqa: E402
import stage_roadmap  # noqa: E402
import stage_records  # noqa: E402
import stage_topology  # noqa: E402
import stage_work  # noqa: E402
from stage_record_paths import (  # noqa: E402
    hierarchy_parent_record_path,
    record_paths,
    work_record_scale,
)
from stage_paths import ACTIVE_TOPOLOGY_V4, active_topology, read_settings  # noqa: E402
from stage_records import AuditedItem, RecordGraph  # noqa: E402


# One owning definition in stage_work (re-exported through stage_guard), shared
# by the audit and the PreToolUse enum gate so both accept exactly the same set.
STATUS_VALUES = stage_guard.STATUS_VALUES
WORK_OPEN_STATUSES = stage_guard.WORK_OPEN_STATUSES
VERIFICATION_VALUES = stage_guard.VERIFICATION_VALUES
RETROSPECTIVE_VALUES = stage_guard.RETROSPECTIVE_VALUES
PROMOTION_VALUES = stage_guard.PROMOTION_VALUES
DECISION_STATUS_VALUES = {"open", "decided", "promoted"}
# Planned work cards in future/backlog/items/ (DE-00000007); one owning enum
# in stage_work, shared with the mover CLI.
WORK_PLANNED_STATUSES = stage_guard.WORK_PLANNED_STATUSES
REQUIRED_WORK_FIELDS = (
    "id",
    "title",
    "status",
    "verification",
    "retrospective",
    "promotion",
    "scope",
)
CURRENT_LIFECYCLE_FIELDS = ("verification", "retrospective", "promotion")
PLANNED_REJECTION_OPTIONAL_FIELDS = (*CURRENT_LIFECYCLE_FIELDS, "scope")
ACTIVE_VIEW_STATUSES = {"active", "blocked"}
REVIEW_VIEW_STATUSES = {"review", "completed", "rejected"}
ITEM_LINK_RE = re.compile(r"\((?:\./)?items/([A-Za-z][A-Za-z0-9]*-\d{3,})\.md(?:#[^)]+)?\)")
# Prefix → owning locations. SSOT for the mapping = the plugin-owned
# operations/artifacts.md §Artifact catalog; keep the two in lock-step.
RECORD_LOCATIONS: dict[str, tuple[str, ...]] = {
    "W": ("present/work/items", "past/work/archive/items", "future/backlog/items"),
    "R": ("present/work/retrospectives", "past/work/archive/retrospectives"),
    "DE": ("present/work/decisions",),
    "D": ("past/decisions/records",),
    "O": ("present/state/observations",),
    "Q": ("present/state/questions",),
    "A": ("present/state/assumptions",),
    "K": ("present/state/risks",),
    "P": ("future/proposals",),
    "M": ("future/roadmap/milestones",),
}
RECORD_ID_RE = re.compile(r"^(?P<prefix>DE|[WRDOQAKBPM])-\d{3,}$")
HEADING_ID_RE = re.compile(r"^#\s+(?P<record_id>(?:DE|[WRDOQAKBPM])-\d{3,})\b", re.MULTILINE)
V4_RECORD_ID_RE = re.compile(
    r"^(?P<prefix>DE|TH|[WRDOQAKBPM])-\d{3,}$"
)
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


def v4_record_locations() -> dict[str, tuple[str, ...]]:
    """Return registry-derived v4 locations with the catalog home first."""

    locations: dict[str, tuple[str, ...]] = {}
    for prefix in ("W", "DE", "D", "TH", "O", "Q", "A", "K", "P", "M"):
        reference = stage_topology.resolve_artifact_reference(f"{prefix}-00000000")
        candidates = tuple(
            dict.fromkeys(Path(path).parent.as_posix() for path in reference.candidate_paths)
        )
        if prefix == "W":
            current = stage_topology.card_location_for_status("active")
            candidates = (current, *(location for location in candidates if location != current))
        locations[prefix] = candidates
    locations["R"] = stage_topology.retrospective_locations()
    return locations


def v4_routing_only_locations() -> tuple[str, ...]:
    """Registry-derived v4 locations that carry no audited record prefix."""

    return tuple(
        root
        for family, zone in (
            ("canon", "official"),
            ("model", "official"),
            ("roadmap", "themes"),
        )
        for root in stage_topology.get_zone(family, zone).record_roots
    )


def is_direct_planned_rejection_archive(audited_item: AuditedItem) -> bool:
    """Return whether an archived rejection never entered current work."""

    fields = audited_item.fields
    return (
        audited_item.location == "archive"
        and fields.get("terminal_disposition", "").strip() == "rejected"
        and all(field not in fields for field in CURRENT_LIFECYCLE_FIELDS)
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
        self.topology = active_topology(self.stage_root)
        if self.topology == ACTIVE_TOPOLOGY_V4:
            self.template_root = V4_TEMPLATE_ROOT
            self.record_locations = v4_record_locations()
            self.routing_only_locations = v4_routing_only_locations()
            item_directory = Path(
                stage_topology.card_location_for_status("active")
            ).name
            self.item_link_re = re.compile(
                rf"\((?:\./)?{re.escape(item_directory)}/"
                r"(?:[A-Za-z][A-Za-z0-9]*-\d{3,}/)*"
                r"([A-Za-z][A-Za-z0-9]*-\d{3,})"
                r"(?:\.md|/(?:_epic|_story)\.md)(?:#[^)]+)?\)"
            )
        else:
            self.template_root = TEMPLATE_ROOT
            self.record_locations = RECORD_LOCATIONS
            self.routing_only_locations = ROUTING_ONLY_LOCATIONS
            self.item_link_re = ITEM_LINK_RE

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
        self.audit_archived_work_intents(items)
        self.audit_hierarchy(items)
        self.audit_work_indexes(items)
        self.audit_backlog_items(graph)
        self.audit_retrospective_identities(graph)
        self.audit_orphan_records(graph)
        self.audit_state_links(graph)
        self.audit_archive_records(graph)
        self.audit_future_indexes(graph)
        if self.topology == ACTIVE_TOPOLOGY_V4:
            self.audit_roadmap(graph)
        self.audit_family_shapes()
        self.audit_record_ownership()
        self.audit_routing()
        self.audit_catalog_sync()
        self.audit_operations_ownership()
        self.audit_venue_routing(items)
        self.audit_canon()
        self.audit_governance()
        return self.findings

    def audit_template_files(self) -> None:
        if not self.template_root.exists():
            self.error("TEMPLATE001", "Stage template root not found.", self.template_root)
            return

        settings = self.load_settings()
        guidance_paths = (
            set(guidance_docs.guidance_paths())
            if self.topology == ACTIVE_TOPOLOGY_V4
            else set()
        )
        raw_overrides = settings.get("guidance_overrides", [])
        overrides: set[str] = set()
        if not isinstance(raw_overrides, list) or not all(
            isinstance(value, str) for value in raw_overrides
        ):
            self.error(
                "TEMPLATE005",
                "guidance_overrides must be a list of template-backed paths relative to .stage.",
                self.settings_path,
            )
        else:
            overrides = set(raw_overrides)
            valid_paths = {path.as_posix() for path in guidance_paths}
            for value in sorted(overrides):
                relative = Path(value)
                if (
                    relative.is_absolute()
                    or ".." in relative.parts
                    or value not in valid_paths
                ):
                    self.error(
                        "TEMPLATE005",
                        f"guidance_overrides declares unknown guidance path `{value}`.",
                        self.settings_path,
                    )

        language = guidance_docs.project_language(self.stage_root)
        for template_path in sorted(self.template_root.rglob("*")):
            if template_path.is_dir():
                continue
            relative = template_path.relative_to(self.template_root)
            target = (
                self.settings_path
                if relative == Path("settings.jsonc")
                else self.stage_root / relative
            )
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
            elif (
                relative in guidance_paths
                and relative.as_posix() not in overrides
            ):
                localized = guidance_docs.localized_template(relative, language)
                template_text = localized.read_text(encoding="utf-8")
                try:
                    project_text = target.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    continue
                if not guidance_docs.guidance_matches(
                    template_text,
                    project_text,
                ):
                    self.warning(
                        "TEMPLATE004",
                        "Stage guidance differs from the current localized template. Run "
                        "`python3 stage/scripts/refresh_guidance.py --project-root "
                        f"<project-root> {relative.as_posix()}` or declare the path in "
                        "settings.json guidance_overrides.",
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

        all_items = [entry.item for entry in graph.work]
        all_items.extend(
            stage_work.item_from_fields(
                node.path,
                node.fields,
                stage_work.GATE_FIELD_DEFAULTS,
                items_root=graph.backlog_root,
            )
            for node in graph.backlog
        )
        for audited_item in graph.work:
            item = audited_item.item
            if not stage_guard.item_is_completed(item):
                continue
            for blocker in stage_work.parent_completion_blockers(
                item.item_id, all_items
            ):
                self.error(
                    "WORK024",
                    f"Completion gate is not closed: {blocker}",
                    item.path,
                )

        return graph.work

    def audit_archived_work_intents(
        self, audited_items: list[AuditedItem]
    ) -> None:
        for audited_item in audited_items:
            if audited_item.location != "archive":
                continue
            item_id = audited_item.item.item_id
            for path in stage_guard.pending_intent_files_for_work_item(
                self.stage_root, item_id
            ):
                self.warning(
                    "WORK025",
                    f"Archived work item {item_id} still has a pending intent.",
                    path,
                )

    def audit_work_item_fields(self, audited_item: AuditedItem) -> None:
        item = audited_item.item
        path = item.path
        direct_planned_rejection = is_direct_planned_rejection_archive(audited_item)

        for field in REQUIRED_WORK_FIELDS:
            if direct_planned_rejection and field in PLANNED_REJECTION_OPTIONAL_FIELDS:
                continue
            if field not in audited_item.fields:
                self.error("WORK001", f"Work item frontmatter field is missing: {field}", path)

        expected_id = path.stem
        if self.topology == ACTIVE_TOPOLOGY_V4:
            try:
                scale = work_record_scale(audited_item.items_root, path)
            except ValueError:
                scale = "invalid"
                self.error(
                    "WORK026",
                    "Work record is outside the schema-v5 epic/story/action hierarchy.",
                    path,
                )
            if scale in {"epic", "story"}:
                expected_id = path.parent.name
        if item.item_id != expected_id:
            self.error("WORK002", f"Work item id differs from filename: {item.item_id}", path)
        if item.status not in STATUS_VALUES:
            self.error("WORK003", f"Unknown status value: {item.status}", path)
        if not direct_planned_rejection:
            if item.verification not in VERIFICATION_VALUES:
                self.error("WORK004", f"Unknown verification value: {item.verification}", path)
            if item.retrospective not in RETROSPECTIVE_VALUES:
                self.error("WORK005", f"Unknown retrospective value: {item.retrospective}", path)
            if item.promotion not in PROMOTION_VALUES:
                self.error("WORK006", f"Unknown promotion value: {item.promotion}", path)
        if item.review not in stage_guard.REVIEW_VALUES:
            self.error("WORK013", f"Unknown review value: {item.review}", path)
        if item.kind and item.kind not in self.known_kinds():
            self.warning(
                "KIND001",
                f"Work kind `{item.kind}` has no `passed` criterion in operations/verification.md.",
                path,
            )

        for blocker in stage_guard.item_completion_blockers(item):
            self.error("WORK008", f"Completion gate is not closed: {blocker}", path)

        if audited_item.location == "present" and item.status == "completed" and item.promotion in {
            "approved",
            "promoted",
        }:
            if not item.promotes:
                self.error(
                    "WORK027",
                    "Completed item declared promotion without any promotion paths.",
                    path,
                )
            if item.promotion == "approved":
                self.error(
                    "WORK027",
                    "Completed item approved promotion but has not recorded it as promoted.",
                    path,
                )
            else:
                for promoted in item.promotes:
                    promoted_path = self.project_root / promoted
                    if not promoted_path.is_file():
                        self.error(
                            "WORK027",
                            f"Completed item recorded promotion before this path existed: {promoted}",
                            path,
                        )

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
            # Finished work must not rest on undecided decisions (DE-00000005).
            if (
                item.status in stage_guard.WORK_FINAL_STATUSES
                and decision_fields.get("status", "").strip() == "open"
            ):
                self.error(
                    "DECISION003",
                    f"Work item is {item.status} but linked decision {raw_ref} is still open; "
                    "close the decision (decided/promoted) before completing the work.",
                    item.path,
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
                    f"Work record has no hierarchy location for parent id: {parent_id}",
                    entry.item.path,
                )
                continue
            if stage_guard.item_is_open(entry.item) and parent.item.status in stage_guard.WORK_FINAL_STATUSES:
                self.error(
                    "WORK019",
                    f"Open work record is placed under a finalized hierarchy "
                    f"location ({parent.item.status}): "
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
        if self.topology == ACTIVE_TOPOLOGY_V4:
            active_relative, review_relative = stage_topology.get_zone(
                "work", "current"
            ).index_surfaces
            active_ids, active_unknown = self.mentioned_item_ids(
                self.stage_root / active_relative, known_ids
            )
            review_ids, review_unknown = self.mentioned_item_ids(
                self.stage_root / review_relative, known_ids
            )
        else:
            active_relative = "present/work/active.md"
            review_relative = "present/work/review.md"
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
                active_relative,
            )
        for unknown_id in sorted(review_unknown):
            self.error(
                "INDEX002",
                f"review.md references a work item that does not exist: {unknown_id}",
                review_relative,
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

        linked_ids = set(self.item_link_re.findall(text))
        return linked_ids & known_ids, linked_ids - known_ids

    def audit_backlog_items(self, graph: RecordGraph) -> None:
        """Planned work cards (DE-00000007): future/backlog/items/ holds W
        cards in a planned status; work fields and venue policy apply once the
        card moves to present/work/items/."""
        for node in graph.backlog:
            path = node.path
            item_id = node.record_id
            status = (node.fields.get("status") or "").strip().lower()
            if status not in WORK_PLANNED_STATUSES:
                self.error(
                    "BACKLOG001",
                    f"Planned card status `{status or 'missing'}` is not one of "
                    f"{sorted(WORK_PLANNED_STATUSES)}; started work moves to "
                    "present/work/items/ (scripts/start_work.py).",
                    path,
                )
            expected_id = path.stem
            if self.topology == ACTIVE_TOPOLOGY_V4:
                try:
                    scale = work_record_scale(graph.backlog_root, path)
                except ValueError:
                    scale = "invalid"
                    self.error(
                        "BACKLOG008",
                        "Planned work record is outside the schema-v5 "
                        "epic/story/action hierarchy.",
                        path,
                    )
                if scale in {"epic", "story"}:
                    expected_id = path.parent.name
            if expected_id != item_id:
                self.error(
                    "BACKLOG003",
                    f"Backlog path does not encode its id: {item_id}",
                    path,
                )

        backlog_items = {
            node.record_id: stage_work.item_from_fields(
                node.path,
                node.fields,
                stage_work.AUDIT_FIELD_DEFAULTS,
                items_root=graph.backlog_root,
            )
            for node in graph.backlog_by_id.values()
        }
        for node in graph.backlog_by_id.values():
            parent_id = backlog_items[node.record_id].parent
            if parent_id and parent_id not in graph.backlog_by_id and parent_id not in graph.work_ids:
                self.error(
                    "BACKLOG002",
                    f"Planned work record has no hierarchy location for parent id: {parent_id}",
                    node.path,
                )

        # Same contract as the work hierarchy (WORK018): a parent chain that
        # loops is a self-contradictory plan, not an ordering.
        for node in graph.backlog_by_id.values():
            seen: list[str] = []
            cursor = node.record_id
            while cursor:
                if cursor in seen:
                    self.error(
                        "BACKLOG007",
                        "Backlog parent chain forms a cycle: " + " -> ".join(seen + [cursor]),
                        node.path,
                    )
                    break
                seen.append(cursor)
                parent_item = backlog_items.get(cursor)
                cursor = parent_item.parent if parent_item else ""

    def audit_orphan_records(self, graph: RecordGraph) -> None:
        """Every decision and retrospective record is validated on its own —
        not only when a work item happens to reference it — so an orphan with a
        missing `work_item`, bad status, or no principle citation is caught,
        and a record whose work item does not point BACK at it (a one-sided
        reverse link) is a contradiction, not an indexing nicety."""
        item_by_id: dict[str, AuditedItem] = {}
        for entry in graph.work:
            item_by_id.setdefault(entry.item.item_id, entry)
        roadmap_by_id = {
            node.record_id: node for node in graph.themes + graph.milestones
        }

        for node in graph.decisions:
            work_item = (node.fields.get("work_item") or "").strip()
            roadmap_item = (node.fields.get("roadmap_item") or "").strip()
            if roadmap_item:
                if work_item:
                    self.error(
                        "DECISION001",
                        "Decision record must link to one owner, not both work_item and "
                        "roadmap_item.",
                        node.path,
                    )
                if roadmap_item not in roadmap_by_id:
                    self.error(
                        "DECISION001",
                        f"Decision record roadmap_item references a missing roadmap record: "
                        f"{roadmap_item}",
                        node.path,
                    )
            elif not work_item or work_item not in graph.work_ids:
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
            roadmap_node = roadmap_by_id.get(roadmap_item)
            if roadmap_node is not None:
                declared = set(
                    stage_guard.split_scope(
                        roadmap_node.fields.get("decision_refs", "")
                    )
                )
                if node.record_id not in {Path(ref).stem for ref in declared}:
                    self.error(
                        "DECISION002",
                        f"Decision record is not listed in {roadmap_item}'s decision_refs — "
                        "a roadmap transition must link back.",
                        node.path,
                    )
            entry = item_by_id.get(work_item) if not roadmap_item else None
            if entry is not None:
                declared = {
                    str(
                        stage_records.resolve_decision_ref(
                            self.project_root, self.stage_root, raw_ref
                        )
                    )
                    for raw_ref in stage_guard.split_scope(
                        entry.fields.get("decision_refs", "")
                    )
                }
                if str(node.path) not in declared:
                    self.error(
                        "DECISION002",
                        f"Decision record is not listed in {work_item}'s decision_refs — "
                        "a recorded decision must link back.",
                        node.path,
                    )

        for node in graph.retrospectives:
            work_item = (node.fields.get("work_item") or "").strip()
            if not work_item or work_item not in graph.work_ids:
                self.error(
                    "RETRO001",
                    f"Retrospective work_item references a missing work item: {work_item or 'empty'}",
                    node.path,
                )
                continue
            entry = item_by_id.get(work_item)
            if entry is None or entry.item.retrospective not in stage_guard.RETROSPECTIVE_DONE:
                continue  # an R drafted before completion is a normal state
            bound = stage_records.resolve_retrospective_ref(
                self.project_root,
                self.stage_root,
                entry.item.retrospective_ref,
                entry.location,
            )
            if str(bound) != str(node.path):
                self.error(
                    "RETRO002",
                    f"Work item {work_item} binds retrospective_ref "
                    f"`{entry.item.retrospective_ref or 'empty'}`, not this record — one "
                    "completed item has one binding retrospective.",
                    node.path,
                )

    def audit_retrospective_identities(self, graph: RecordGraph) -> None:
        """Each R-id has one owning location and one work-item binding."""
        seen: dict[str, tuple[str, Path]] = {}
        for node in graph.retrospectives:
            work_item = (node.fields.get("work_item") or "").strip()
            previous = seen.get(node.record_id)
            if previous is None:
                seen[node.record_id] = (work_item, node.path)
                continue
            previous_work_item, previous_path = previous
            self.error(
                "RETRO003",
                f"Retrospective id {node.record_id} appears more than once: "
                f"{previous_work_item or 'missing work_item'} at "
                f"{self.display_path(previous_path)}; {work_item or 'missing work_item'} at "
                f"{self.display_path(node.path)}. Each R-id must have one location and one "
                "work_item.",
                node.path,
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
        """Archived move units keep one index row and every record keeps its
        transition evidence.

        In the hierarchical topology, folder placement owns nesting, so only
        top-level epics and independent stories require archive-index rows.
        Nested records retain their terminal state in `terminal_disposition`;
        legacy nested rows remain valid links but are not required.
        """
        if self.topology == ACTIVE_TOPOLOGY_V4:
            index_relative = stage_topology.get_zone(
                "work", "official"
            ).index_surfaces[0]
            index_path = self.stage_root / index_relative
        else:
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
            indexed = True
            if self.topology == ACTIVE_TOPOLOGY_V4:
                try:
                    indexed = (
                        hierarchy_parent_record_path(entry.items_root, item.path)
                        is None
                    )
                except ValueError:
                    indexed = True
            final = final_by_id.get(item.item_id)
            if indexed and final is None:
                self.error(
                    "ARCHIVE001",
                    f"Archived move unit has no archive index row: {item.item_id}",
                    item.path,
                )
            final_source = "Archive index Final status"
            final_path = index_path
            if not indexed and final is None:
                final_source = "Archived item terminal_disposition"
                final_path = item.path
                final = {
                    "accepted": "completed",
                    "rejected": "rejected",
                }.get(entry.fields.get("terminal_disposition", "").strip(), "")
            if final is not None and final not in {"completed", "rejected"}:
                self.error(
                    "ARCHIVE002",
                    f"{final_source} must be completed or rejected: "
                    f"{item.item_id} `{final or 'missing'}`",
                    final_path,
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
            if (
                not is_direct_planned_rejection_archive(entry)
                and (
                    item.retrospective not in stage_guard.RETROSPECTIVE_DONE
                    or not item.retrospective_ref
                )
            ):
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

    def audit_future_indexes(self, graph: RecordGraph) -> None:
        """Each future family's index owns the current index of its records
        (backlog, roadmap milestones, proposals): every record has a row, and
        every ID-bearing row has a record. Roadmap theme rows carry no record
        ID and are not checked."""
        if self.topology == ACTIVE_TOPOLOGY_V4:
            families = (
                (
                    stage_topology.get_zone("work", "planned").index_surfaces[0],
                    [(node.record_id, node.path) for node in graph.backlog],
                    ("W", "B"),
                    ("BACKLOG008", "BACKLOG009"),
                ),
                (
                    stage_topology.get_zone("proposals", "planned").index_surfaces[0],
                    [(node.record_id, node.path) for node in graph.proposals],
                    ("P",),
                    ("PROPOSAL001", "PROPOSAL002"),
                ),
            )
        else:
            families = (
                (
                    "future/backlog/index.md",
                    [(node.record_id, node.path) for node in graph.backlog],
                    # Planned cards are W records; legacy un-migrated B rows stay
                    # recognized so pre-v3 projects keep a truthful index check.
                    ("W", "B"),
                    ("BACKLOG008", "BACKLOG009"),
                ),
                (
                    "future/roadmap/index.md",
                    [(node.record_id, node.path) for node in graph.milestones],
                    ("M",),
                    ("ROADMAP001", "ROADMAP002"),
                ),
                (
                    "future/proposals/index.md",
                    [(node.record_id, node.path) for node in graph.proposals],
                    ("P",),
                    ("PROPOSAL001", "PROPOSAL002"),
                ),
            )
        for index_relative, records, prefixes, (missing_code, dangling_code) in families:
            index_path = self.stage_root / index_relative
            row_ids: set[str] = set()
            for cells in stage_guard.parse_index_rows(index_path):
                if not cells:
                    continue
                candidate = cells[0].strip()
                match = RECORD_ID_RE.match(candidate)
                if match and match.group("prefix") in prefixes:
                    row_ids.add(candidate)
            record_ids = {record_id for record_id, _ in records}
            for record_id, path in records:
                if record_id not in row_ids:
                    self.error(
                        missing_code,
                        f"Record has no row in `{index_relative}`: {record_id}",
                        path,
                    )
            for row_id in sorted(row_ids - record_ids):
                self.error(
                    dangling_code,
                    f"`{index_relative}` row references a missing record: {row_id}",
                    index_path,
                )

    def audit_roadmap(self, graph: RecordGraph) -> None:
        """Validate v4 roadmap refs, indexes, status ownership, and decision chains."""

        theme_zone = stage_topology.get_zone("roadmap", "themes")
        milestone_zone = stage_topology.get_zone("roadmap", "milestones")
        theme_index = self.stage_root / theme_zone.index_surfaces[0]
        milestone_index = self.stage_root / milestone_zone.index_surfaces[0]

        def rows(path: Path, prefix: str) -> dict[str, list[str]]:
            result: dict[str, list[str]] = {}
            for cells in stage_guard.parse_index_rows(path):
                if cells and re.fullmatch(rf"{prefix}-\d{{3,}}", cells[0].strip()):
                    result.setdefault(cells[0].strip(), cells)
            return result

        theme_rows = rows(theme_index, "TH")
        milestone_rows = rows(milestone_index, "M")
        # C3 consumer fixtures wrote body-only milestone rows into the router
        # before the family index path was wired. Keep only that inert shape
        # readable; every frontmattered v4 record must use the owning index.
        legacy_router_rows = rows(self.stage_root / "roadmap" / "index.md", "M")
        theme_ids = {node.record_id for node in graph.themes}
        milestone_ids = {node.record_id for node in graph.milestones}

        for node in graph.themes:
            record = stage_roadmap.load_roadmap_record(node.path)
            row = theme_rows.get(node.record_id)
            if row is None:
                self.error(
                    "ROADMAP003",
                    f"Theme has no row in `{theme_zone.index_surfaces[0]}`: {node.record_id}",
                    node.path,
                )
            elif (
                len(row) < 3
                or row[1].strip() != record.title
                or f"({node.record_id}.md)" not in row[2]
            ):
                self.error(
                    "ROADMAP008",
                    f"Theme index row does not match its record: {node.record_id}",
                    theme_index,
                )
            if "status" in node.fields:
                self.error(
                    "ROADMAP009",
                    "Theme status must be computed from its decision chain, not authored.",
                    node.path,
                )
            for issue in stage_roadmap.decision_chain_issues(self.stage_root, node.path):
                self.error(issue.code, issue.message, issue.path)

        for row_id in sorted(set(theme_rows) - theme_ids):
            self.error(
                "ROADMAP004",
                f"`{theme_zone.index_surfaces[0]}` row references a missing theme: {row_id}",
                theme_index,
            )

        for node in graph.milestones:
            record = stage_roadmap.load_roadmap_record(node.path)
            row = milestone_rows.get(node.record_id)
            legacy_body_row = not node.fields and node.record_id in legacy_router_rows
            if row is None and not legacy_body_row:
                self.error(
                    "ROADMAP001",
                    f"Milestone has no row in `{milestone_zone.index_surfaces[0]}`: "
                    f"{node.record_id}",
                    node.path,
                )
            elif row is not None and (
                len(row) < 5
                or row[1].strip() != record.theme
                or row[2].strip() != record.title
                or row[3].strip() != record.period
                or f"({node.record_id}.md)" not in row[4]
            ):
                self.error(
                    "ROADMAP007",
                    f"Milestone index row does not match its record: {node.record_id}",
                    milestone_index,
                )
            if record.theme and record.theme not in theme_ids:
                self.error(
                    "ROADMAP006",
                    f"Milestone theme references a missing theme: {record.theme}",
                    node.path,
                )
            if "status" in node.fields:
                self.error(
                    "ROADMAP009",
                    "Milestone status must be computed from its decision chain, not authored.",
                    node.path,
                )
            for issue in stage_roadmap.decision_chain_issues(self.stage_root, node.path):
                self.error(issue.code, issue.message, issue.path)

        for row_id in sorted(set(milestone_rows) - milestone_ids):
            self.error(
                "ROADMAP002",
                f"`{milestone_zone.index_surfaces[0]}` row references a missing milestone: "
                f"{row_id}",
                milestone_index,
            )

        # C5 allowed inert optional milestone text before C6 supplied roadmap
        # semantics. Activate dangling-W enforcement once a real v4 roadmap
        # record exists, preserving those pre-C6 empty-roadmap fixtures.
        roadmap_nodes = graph.themes + graph.milestones
        roadmap_adopted = any(node.fields for node in roadmap_nodes)
        if roadmap_adopted:
            work_records = [
                (entry.fields, entry.item.path) for entry in graph.work
            ] + [(node.fields, node.path) for node in graph.backlog]
            for fields, path in work_records:
                milestone = (fields.get("milestone") or "").strip()
                if milestone and milestone not in milestone_ids:
                    self.error(
                        "ROADMAP005",
                        f"Work milestone references a missing milestone: {milestone}",
                        path,
                    )

    def audit_family_shapes(self) -> None:
        if self.topology == ACTIVE_TOPOLOGY_V4:
            current_retro, official_retro = stage_topology.retrospective_locations()
            decision_roots = stage_topology.resolve_artifact_reference(
                "DE-00000000"
            ).candidate_paths
            required = {
                self.stage_root / current_retro: ("id", "work_item"),
                self.stage_root / official_retro: ("id", "work_item"),
            }
        else:
            required = {
                self.stage_root / "present" / "work" / "retrospectives": ("id", "work_item"),
                self.stage_root / "past" / "work" / "archive" / "retrospectives": ("id", "work_item"),
                self.stage_root / "present" / "work" / "decisions": ("id", "work_item", "status"),
            }
        for family_root, keys in required.items():
            if not family_root.exists():
                continue
            for path in record_paths(family_root):
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
        if self.topology == ACTIVE_TOPOLOGY_V4:
            for family_root in {
                self.stage_root / Path(root).parent for root in decision_roots
            }:
                for path in record_paths(family_root):
                    if path.name in {"README.md", "_template.md"}:
                        continue
                    fields = stage_guard.parse_frontmatter(path)
                    missing = [key for key in ("id", "status") if key not in fields]
                    if "work_item" not in fields and "roadmap_item" not in fields:
                        missing.append("work_item or roadmap_item")
                    if missing:
                        self.warning(
                            "FAMILY001",
                            "Record does not follow its family frontmatter shape; missing: "
                            + ", ".join(missing),
                            path,
                        )

    def audit_record_ownership(self) -> None:
        """SSOT + responsibility boundaries over every ID-bearing record file.

        The prefix → location catalog mirrors `operations/artifacts.md`
        §Artifact catalog (that document is the SSOT for the mapping).
        """
        # WORK007 owns duplicates only where graph.work scans (present +
        # archive); planned cards in future/backlog keep plain SSOT001, and a
        # W id appearing in two lifecycle columns is an SSOT001 error too.
        if self.topology == ACTIVE_TOPOLOGY_V4:
            work_item_dirs = {
                stage_topology.card_location_for_status("active"),
                stage_topology.card_location_for_status("archived"),
            }
            work_record_dirs = work_item_dirs | {
                stage_topology.card_location_for_status("captured"),
            }
        else:
            work_item_dirs = {"present/work/items", "past/work/archive/items"}
            work_record_dirs = set(self.record_locations["W"])
        retrospective_dirs = set(self.record_locations["R"])

        def below(relative: str, roots: set[str] | tuple[str, ...]) -> bool:
            return any(
                relative == root or relative.startswith(f"{root}/")
                for root in roots
            )

        by_id: dict[str, list[Path]] = {}
        for path in record_paths(self.stage_root):
            relative_parent = path.parent.relative_to(self.stage_root).as_posix()
            if relative_parent.startswith(".runtime"):
                continue
            if path.name in {"README.md", "_template.md"}:
                continue
            if (
                path.name
                in {
                    stage_topology.EPIC_RECORD_NAME,
                    stage_topology.STORY_RECORD_NAME,
                }
                and relative_parent in work_record_dirs
            ):
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
            id_pattern = (
                V4_RECORD_ID_RE
                if self.topology == ACTIVE_TOPOLOGY_V4
                else RECORD_ID_RE
            )
            match = id_pattern.match(record_id)
            if not match:
                continue
            by_id.setdefault(record_id, []).append(path)

            prefix = match.group("prefix")
            allowed = self.record_locations.get(prefix)
            owned = allowed is None or relative_parent in allowed
            if prefix == "W" and allowed is not None:
                owned = below(relative_parent, allowed)
            if not owned:
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
            if (
                all(below(parent, work_item_dirs) for parent in parents)
                or parents <= retrospective_dirs
            ):
                continue  # WORK007 owns W duplicates; RETRO003 owns R duplicates.
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

        routed_locations = list(
            dict.fromkeys(
                [
                    location
                    for locations in self.record_locations.values()
                    for location in locations
                ]
                + list(self.routing_only_locations)
            )
        )
        for location in routed_locations:
            if (self.stage_root / location).is_dir() and location not in routed_cells:
                self.warning(
                    "ROUTE001",
                    f"Existing artifact location `{location}/` is not routed in index.md.",
                    self.stage_root / location,
                )

        operations_root = self.stage_root / "operations"
        if operations_root.is_dir():
            for path in record_paths(operations_root):
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
        # The plugin-owned prose catalog is now schema-v4 (the documentation
        # cutover card, C9). It is the SSOT for the v4 prefix→location map, so it
        # is validated on v4 projects; comparing it to a not-yet-migrated v3
        # project would create false drift, so that case is skipped.
        if self.topology != ACTIVE_TOPOLOGY_V4:
            return

        # The catalog is plugin-owned; a project copy (declared override or
        # not-yet-migrated v1 layout) takes precedence so its drift is visible.
        catalog_path = self.stage_root / "operations" / "artifacts.md"
        if not catalog_path.is_file():
            catalog_path = PLUGIN_ROOT / "operations" / "artifacts.md"
        try:
            text = catalog_path.read_text(encoding="utf-8")
        except OSError:
            self.error(
                "CATALOG002",
                "The plugin-owned artifact catalog operations/artifacts.md is missing.",
                catalog_path,
            )
            return

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

        for prefix, locations in self.record_locations.items():
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
            if prefix not in self.record_locations:
                self.error(
                    "CATALOG001",
                    f"Artifact catalog declares prefix `{prefix}-` (`{catalog_location}/`) that the "
                    "audit does not map in RECORD_LOCATIONS; ownership and routing checks would skip "
                    "it. Keep the two in lock-step.",
                    catalog_path,
                )

    def audit_operations_ownership(self) -> None:
        """Common operations docs are plugin-owned (DE-00000002). A project
        `.stage/operations/` file that shadows one is either a declared
        override (settings.json `operations_overrides`) or ownership drift.
        `verification.md` is the project policy surface and never drift;
        project-only extra docs are allowed (ROUTE002 covers their routing).
        """
        settings = self.load_settings()
        settings_path = self.settings_path
        common = self.plugin_common_docs()

        overrides = settings.get("operations_overrides", [])
        if not isinstance(overrides, list) or not all(
            isinstance(name, str) for name in overrides
        ):
            self.error(
                "OPS004",
                "operations_overrides must be a list of plugin common-doc filenames.",
                settings_path,
            )
            overrides = []
        declared = set(overrides)
        for name in sorted(declared):
            if name not in common or name in ("README.md", "verification.md"):
                self.error(
                    "OPS004",
                    f"operations_overrides declares `{name}`, which is not an overridable "
                    f"plugin common doc (known: {sorted(set(common) - {'verification.md'})}).",
                    settings_path,
                )
            elif not (self.stage_root / "operations" / name).is_file():
                self.error(
                    "OPS003",
                    f"operations_overrides declares `{name}` but "
                    f".stage/operations/{name} does not exist.",
                    settings_path,
                )

        # Drift detection applies to the v2 layout only; a v1 project still
        # legitimately carries full copies and SCHEMA001 already points at the
        # generation gap.
        if self.topology == ACTIVE_TOPOLOGY_V4:
            if settings.get("schema_version") != stage_topology.SCHEMA_VERSION:
                return
        else:
            if settings.get("schema_version") != stage_guard.STAGE_SCHEMA_VERSION:
                return
        operations_root = self.stage_root / "operations"
        if not operations_root.is_dir():
            return
        for path in record_paths(operations_root):
            name = path.name
            if name in ("README.md", "verification.md") or name not in common or name in declared:
                continue
            try:
                identical = path.read_bytes() == common[name].read_bytes()
            except OSError:
                continue
            if identical:
                self.warning(
                    "OPS001",
                    f"`operations/{name}` duplicates the plugin-owned common doc byte-for-byte; "
                    "delete it or run scripts/migrate_stage.py.",
                    path,
                )
            else:
                self.error(
                    "OPS002",
                    f"`operations/{name}` shadows a plugin-owned common doc without a declared "
                    "override; add it to settings.json operations_overrides or remove it.",
                    path,
                )

    def audit_venue_routing(self, items: list[AuditedItem]) -> None:
        """The declared `kind -> venue` role policy (DE-00000004). No policy →
        venue stays fully advisory and nothing is reported. Open present items
        only: archived history is not judged against today's policy."""
        settings = self.load_settings()
        settings_path = self.settings_path
        raw = settings.get("venue_routing")
        if raw is None or raw == {}:
            return
        if not isinstance(raw, dict) or not all(
            isinstance(kind, str) and isinstance(venue, str) and kind.strip() and venue.strip()
            for kind, venue in raw.items()
        ):
            self.error(
                "VENUE004",
                "venue_routing must map work-kind strings to venue strings.",
                settings_path,
            )
            return
        routing = {kind.strip().lower(): venue.strip() for kind, venue in raw.items()}
        split_token = stage_guard.VENUE_SPLIT_TOKEN
        declared_venues = {venue for venue in routing.values() if venue != split_token}

        for audited_item in items:
            item = audited_item.item
            if audited_item.location != "present" or item.status not in WORK_OPEN_STATUSES:
                continue
            venue = (audited_item.fields.get("venue") or "").strip()
            routed = routing.get(item.kind, "")

            if routed == split_token and not self.valid_venue_exception(audited_item):
                self.error(
                    "VENUE005",
                    f"Kind `{item.kind}` is declared mixed (`{split_token}`): register separate "
                    "design and implementation items with `parent` lineage, or link a decision "
                    "record with `authorizes: venue_exception` for a deliberate single item.",
                    item.path,
                )

            if not venue:
                if routed and routed != split_token:
                    self.warning(
                        "VENUE001",
                        f"Open work of routed kind `{item.kind}` has no venue; "
                        f"venue_routing derives `{routed}`.",
                        item.path,
                    )
                continue
            if declared_venues and venue not in declared_venues:
                self.warning(
                    "VENUE002",
                    f"Venue `{venue}` is not declared by venue_routing "
                    f"(declared: {sorted(declared_venues)}).",
                    item.path,
                )
            elif (
                routed
                and routed != split_token
                and venue != routed
                and not self.valid_venue_exception(audited_item)
            ):
                self.error(
                    "VENUE003",
                    f"Venue `{venue}` contradicts venue_routing ({item.kind} -> {routed}) "
                    "without a valid exception decision (decided/promoted, "
                    "`authorizes: venue_exception`, linked via decision_refs).",
                    item.path,
                )

    def valid_venue_exception(self, audited_item: AuditedItem) -> bool:
        """CLI-shared contract (stage_work.venue_exception_error) plus the
        work_item back-link the CLI cannot know at registration time. WORK015
        already reports a broken back-link, so it is not re-reported here."""
        refs = (audited_item.fields.get("decision_refs") or "").strip()
        for ref in stage_guard.split_scope(refs):
            if stage_guard.venue_exception_error(self.stage_root, ref):
                continue
            fields = stage_guard.parse_frontmatter(
                stage_records.resolve_decision_ref(self.project_root, self.stage_root, ref)
            )
            if (fields.get("work_item") or "").strip() == audited_item.item.item_id:
                return True
        return False

    def plugin_common_docs(self) -> dict[str, Path]:
        operations_root = PLUGIN_ROOT / "operations"
        if not operations_root.is_dir():
            return {}
        return {path.name: path for path in record_paths(operations_root)}

    def load_settings(self) -> dict[str, Any]:
        if not hasattr(self, "_settings"):
            settings_path, data, error = read_settings(self.stage_root)
            self._settings_path = settings_path
            self._settings_error = error
            if error is not None:
                data = {}
            self._settings = data if isinstance(data, dict) else {}
        return self._settings

    @property
    def settings_path(self) -> Path:
        if not hasattr(self, "_settings_path"):
            self.load_settings()
        return self._settings_path

    def audit_canon(self) -> None:
        if self.topology == ACTIVE_TOPOLOGY_V4:
            principles_relative = next(
                path
                for path in stage_topology.get_zone(
                    "canon", "official"
                ).index_surfaces
                if path.endswith("principles.md")
            )
            principles_path = self.stage_root / principles_relative
        else:
            principles_path = self.stage_root / "past" / "canon" / "principles.md"
        try:
            text = principles_path.read_text(encoding="utf-8")
        except OSError:
            if self.topology == ACTIVE_TOPOLOGY_V4:
                message = (
                    f"{principles_relative} is missing — the harness core principles are gone."
                )
            else:
                message = "past/canon/principles.md is missing — the harness core principles are gone."
            self.error("CANON001", message, principles_path)
            return
        markers = ("SSOT", "MECE", "Fail Fast", "AHA", "## Completion principle", "## Behavior principles")
        missing = [marker for marker in markers if marker not in text]
        if missing:
            if self.topology == ACTIVE_TOPOLOGY_V4:
                catalog = principles_relative
            else:
                catalog = "past/canon/principles.md"
            self.error(
                "CANON001",
                f"Core principles are missing from {catalog}: " + ", ".join(missing),
                principles_path,
            )

    def audit_governance(self) -> None:
        settings_path = self.settings_path
        if not settings_path.exists():
            return
        if stage_guard.governance_broken(self.stage_root):
            settings_error = getattr(self, "_settings_error", None)
            message = (
                str(settings_error)
                if isinstance(settings_error, FileExistsError)
                else "settings file is unreadable or malformed (hooks fail closed until repaired)."
            )
            self.error("GOV000", message, settings_path)
            return
        settings = self.load_settings()
        schema_version = settings.get("schema_version")
        # Exact-type comparison: JSON `true` must not pass as 1 (bool is an
        # int subclass in Python).
        expected_schema_version = (
            stage_topology.SCHEMA_VERSION
            if self.topology == ACTIVE_TOPOLOGY_V4
            else stage_guard.STAGE_SCHEMA_VERSION
        )
        if type(schema_version) is not int or schema_version != expected_schema_version:
            if self.topology == ACTIVE_TOPOLOGY_V4:
                self.warning(
                    "SCHEMA001",
                    "settings.json schema_version "
                    f"`{schema_version if schema_version is not None else 'missing'}` differs from "
                    f"the active topology's contract version `{expected_schema_version}` — the "
                    "harness was initialized by a different plugin generation.",
                    settings_path,
                )
            else:
                self.warning(
                    "SCHEMA001",
                    "settings.json schema_version "
                    f"`{schema_version if schema_version is not None else 'missing'}` differs from "
                    f"the plugin's contract version `{stage_guard.STAGE_SCHEMA_VERSION}` — the "
                    "project is behind the enforced contract; run the stage-migrate skill. "
                    "Read-only audit remains available before migration.",
                    settings_path,
                )
        language = settings.get("language")
        if language is not None and (
            not isinstance(language, str)
            or not stage_guard.LANGUAGE_TAG_RE.match(language)
        ):
            self.warning(
                "LANG001",
                f"settings.json language `{language}` is not a lowercase IETF-style tag "
                "(e.g. `en`, `ko`, `pt-br`); hooks fall back to English.",
                settings_path,
            )
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

        # Review config: a stage whose strength is invalid or has no bound command
        # is an ERROR (not a warning) — close_work fails closed on it, so a silent
        # typo would block every close of that stage.
        review = stage_guard.load_review_config(self.stage_root)
        if review:
            for stage in stage_guard.REVIEW_STAGES:
                _command, review_error = stage_guard.resolve_review_command(review, stage)
                if review_error:
                    self.error("REVIEW001", review_error, settings_path)
            stages = review.get("stages")
            if isinstance(stages, dict):
                for name in stages:
                    if name not in stage_guard.REVIEW_STAGES:
                        self.warning(
                            "REVIEW002",
                            f"review.stages has an unknown stage `{name}` (known: {list(stage_guard.REVIEW_STAGES)})",
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
            if self.topology == ACTIVE_TOPOLOGY_V4:
                principles_relative = next(
                    path
                    for path in stage_topology.get_zone(
                        "canon", "official"
                    ).index_surfaces
                    if path.endswith("principles.md")
                )
                principles_path = self.stage_root / principles_relative
            else:
                principles_path = self.stage_root / "past" / "canon" / "principles.md"
            cells = self.parse_table_first_cells(principles_path)
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
