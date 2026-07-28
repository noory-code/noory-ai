"""Registry-derived schema-v4 paths shared by Stage lifecycle CLIs."""

from __future__ import annotations

import posixpath
import sys
from dataclasses import dataclass
from pathlib import Path


HOOK_ROOT = Path(__file__).resolve().parents[1] / "hooks"
if str(HOOK_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOK_ROOT))

import stage_topology  # noqa: E402


@dataclass(frozen=True)
class LifecyclePaths:
    planned_cards: str
    planned_index: str
    planned_template: str
    planned_epic_template: str
    planned_story_template: str
    planned_action_template: str
    current_cards: str
    active_index: str
    review_index: str
    current_template: str
    current_epic_template: str
    current_story_template: str
    current_action_template: str
    current_retrospectives: str
    archive_cards: str
    archive_retrospectives: str
    archive_index: str
    archive_epic_template: str
    archive_story_template: str
    archive_action_template: str


def _work_zone(relative: str) -> stage_topology.ZoneRecord:
    resolved = stage_topology.resolve_zone(relative)
    if resolved is None or resolved[0] != "work":
        raise RuntimeError(f"registry lifecycle path has no work-zone owner: {relative}")
    return resolved[1]


def _template_source(zone: stage_topology.ZoneRecord) -> str:
    if zone.template_source is None:
        raise RuntimeError(f"registry zone has no template source: {zone.canonical_path}")
    return zone.template_source


def _hierarchy_templates(action_template: str) -> tuple[str, str, str]:
    action = Path(action_template)
    return (
        action.with_name(stage_topology.EPIC_RECORD_NAME).as_posix(),
        action.with_name(stage_topology.STORY_RECORD_NAME).as_posix(),
        action.as_posix(),
    )


def v4_lifecycle_paths() -> LifecyclePaths:
    """Return every lifecycle and hierarchy-template path from the registry."""

    planned_cards = stage_topology.card_location_for_status("captured")
    current_cards = stage_topology.card_location_for_status("active")
    archive_cards = stage_topology.card_location_for_status("archived")
    planned_zone = _work_zone(planned_cards)
    current_zone = _work_zone(current_cards)
    archive_zone = _work_zone(archive_cards)
    declared_roots = set(stage_topology.scan_roots("records"))
    if any(
        root not in declared_roots
        for root in (planned_cards, current_cards, archive_cards)
    ):
        raise RuntimeError("registry lifecycle path is absent from the record scan roots")
    current_retrospectives, archive_retrospectives = (
        stage_topology.retrospective_locations()
    )
    planned_templates = _hierarchy_templates(_template_source(planned_zone))
    current_templates = _hierarchy_templates(_template_source(current_zone))
    archive_action_template = (
        Path(_template_source(archive_zone)) / "items" / "_template.md"
    ).as_posix()
    archive_templates = _hierarchy_templates(archive_action_template)
    return LifecyclePaths(
        planned_cards=planned_cards,
        planned_index=planned_zone.index_surfaces[0],
        planned_template=planned_templates[2],
        planned_epic_template=planned_templates[0],
        planned_story_template=planned_templates[1],
        planned_action_template=planned_templates[2],
        current_cards=current_cards,
        active_index=current_zone.index_surfaces[0],
        review_index=current_zone.index_surfaces[1],
        current_template=current_templates[2],
        current_epic_template=current_templates[0],
        current_story_template=current_templates[1],
        current_action_template=current_templates[2],
        current_retrospectives=current_retrospectives,
        archive_cards=archive_cards,
        archive_retrospectives=archive_retrospectives,
        archive_index=archive_zone.index_surfaces[0],
        archive_epic_template=archive_templates[0],
        archive_story_template=archive_templates[1],
        archive_action_template=archive_templates[2],
    )


def milestone_record_roots() -> tuple[str, ...]:
    """Return registry scan roots owned by the roadmap milestone zone."""

    roots = []
    for relative in stage_topology.scan_roots("records"):
        resolved = stage_topology.resolve_zone(relative)
        if (
            resolved is not None
            and resolved[0] == "roadmap"
            and resolved[1].name == "milestones"
        ):
            roots.append(relative)
    return tuple(roots)


def relative_record_link(index_relative: str, record_relative: str) -> str:
    """Return a POSIX link from an index file to one record path."""

    return posixpath.relpath(record_relative, posixpath.dirname(index_relative))
