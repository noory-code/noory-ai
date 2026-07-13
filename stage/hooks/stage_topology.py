"""Schema v4 topology registry.

This module is the tooling SSOT for the v4 Stage layout.  It intentionally has no
filesystem side effects so hooks and scripts can import it on every supported host.
Schema-v3 paths remain resolve-only inputs for audit and the one-shot migration.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


SCHEMA_VERSION = 4
SCHEMA_VERSION_KEY = "schema_version"
LIFECYCLE_STATES = ("planned", "current", "official")
SINGLE_CLASSIFICATION = True
OFFICIAL_ROOT = "official"
MAINTENANCE_MARKER = ".runtime/schema-v4-maintenance.json"

PLANNED_WORK_STATUSES = (
    "captured",
    "triaged",
    "ready",
    "selected",
    "deferred",
    "rejected",
)
CURRENT_WORK_STATUSES = ("active", "blocked", "review", "completed", "rejected")
OFFICIAL_WORK_STATUSES = ("archived",)


@dataclass(frozen=True)
class ZoneRecord:
    """One physical responsibility zone and its lifecycle projection."""

    name: str
    canonical_path: str
    lifecycle_state: str | None
    allowed_statuses: tuple[str, ...]
    record_roots: tuple[str, ...]
    index_surfaces: tuple[str, ...]
    template_source: str | None
    transition_destination: str | None
    resolver_policy: str
    v3_relocation_origin: str | None


@dataclass(frozen=True)
class FamilyRecord:
    """A responsibility family containing one or more disjoint zones."""

    name: str
    zones: tuple[ZoneRecord, ...]


@dataclass(frozen=True)
class ArtifactPrefix:
    """Identity and counter policy for an artifact prefix."""

    prefix: str
    family: str
    record_kind: str
    counter_family: str
    mintable: bool = True
    legacy_resolve_only: bool = False


@dataclass(frozen=True)
class ArtifactReference:
    """Registry-derived candidate locations for an artifact reference."""

    artifact_id: str
    family: str
    candidate_paths: tuple[str, ...]
    legacy: bool


def _zone(
    name: str,
    path: str,
    lifecycle: str | None,
    *,
    statuses: tuple[str, ...] = (),
    roots: tuple[str, ...] = (),
    indexes: tuple[str, ...] = (),
    template: str | None = None,
    destination: str | None = None,
    resolver: str = "path",
    origin: str | None = None,
) -> ZoneRecord:
    return ZoneRecord(
        name=name,
        canonical_path=path,
        lifecycle_state=lifecycle,
        allowed_statuses=statuses,
        record_roots=roots or (path,),
        index_surfaces=indexes,
        template_source=template,
        transition_destination=destination,
        resolver_policy=resolver,
        v3_relocation_origin=origin,
    )


FAMILIES: dict[str, FamilyRecord] = {
    "canon": FamilyRecord(
        "canon",
        (
            _zone(
                "official",
                "official/canon",
                "official",
                roots=(
                    "official/canon/principles",
                    "official/canon/vocabulary",
                    "official/canon/invariants",
                ),
                indexes=(
                    "official/canon/principles.md",
                    "official/canon/vocabulary.md",
                    "official/canon/invariants.md",
                ),
                template="project-stage/official/canon",
                origin="past/canon",
            ),
        ),
    ),
    "model": FamilyRecord(
        "model",
        (
            _zone(
                "official",
                "official/model",
                "official",
                roots=(
                    "official/model/components",
                    "official/model/boundaries",
                    "official/model/interfaces",
                ),
                indexes=(
                    "official/model/overview.md",
                    "official/model/boundaries.md",
                    "official/model/interfaces.md",
                ),
                template="project-stage/official/model",
                origin="past/model",
            ),
        ),
    ),
    "decisions": FamilyRecord(
        "decisions",
        (
            _zone(
                "pending",
                "decisions/pending",
                "current",
                statuses=("open", "decided"),
                indexes=("decisions/index.md",),
                template="project-stage/decisions/pending/_template.md",
                destination="official",
                resolver="decision-reference",
                origin="present/work/decisions",
            ),
            _zone(
                "official",
                "official/decisions/records",
                "official",
                statuses=("promoted", "decided"),
                indexes=("official/decisions/index.md",),
                template="project-stage/official/decisions/records/_template.md",
                resolver="decision-reference",
                origin="past/decisions/records",
            ),
        ),
    ),
    "work": FamilyRecord(
        "work",
        (
            _zone(
                "planned",
                "work/planned",
                "planned",
                statuses=PLANNED_WORK_STATUSES,
                indexes=("work/planned/index.md",),
                template="project-stage/work/planned/_template.md",
                destination="current",
                resolver="work-status",
                origin="future/backlog/items",
            ),
            _zone(
                "current",
                "work/current",
                "current",
                statuses=CURRENT_WORK_STATUSES,
                indexes=("work/active.md", "work/review.md"),
                template="project-stage/work/current/_template.md",
                destination="official",
                resolver="work-status",
                origin="present/work/items",
            ),
            _zone(
                "retrospectives",
                "work/retrospectives",
                "current",
                template="project-stage/work/retrospectives/_template.md",
                destination="official",
                resolver="work-reference",
                origin="present/work/retrospectives",
            ),
            _zone(
                "views",
                "work/views",
                "planned",
                template="project-stage/work/views",
                resolver="derived-view",
                origin="future/backlog/views",
            ),
            _zone(
                "official",
                "official/work/archive",
                "official",
                statuses=OFFICIAL_WORK_STATUSES,
                roots=(
                    "official/work/archive/items",
                    "official/work/archive/retrospectives",
                ),
                indexes=("official/work/archive/index.md",),
                template="project-stage/official/work/archive",
                resolver="work-reference",
                origin="past/work/archive",
            ),
        ),
    ),
    "state": FamilyRecord(
        "state",
        (
            _zone(
                "current",
                "state",
                "current",
                roots=(
                    "state/observations",
                    "state/questions",
                    "state/assumptions",
                    "state/risks",
                ),
                indexes=(
                    "state/current.md",
                    "state/questions.md",
                    "state/assumptions.md",
                    "state/risks.md",
                ),
                template="project-stage/state",
                resolver="state-prefix",
                origin="present/state",
            ),
        ),
    ),
    "proposals": FamilyRecord(
        "proposals",
        (
            _zone(
                "planned",
                "proposals",
                "planned",
                indexes=("proposals/index.md",),
                template="project-stage/proposals/_template.md",
                resolver="proposal-reference",
                origin="future/proposals",
            ),
        ),
    ),
    "roadmap": FamilyRecord(
        "roadmap",
        (
            _zone(
                "themes",
                "roadmap/themes",
                None,
                indexes=("roadmap/themes/index.md",),
                template="project-stage/roadmap/themes/_template.md",
                resolver="decision-chain",
                origin="future/roadmap/themes",
            ),
            _zone(
                "milestones",
                "roadmap/milestones",
                None,
                indexes=("roadmap/milestones/index.md",),
                template="project-stage/roadmap/milestones/_template.md",
                resolver="decision-chain",
                origin="future/roadmap/milestones",
            ),
        ),
    ),
    "operations": FamilyRecord(
        "operations",
        (
            _zone(
                "rules",
                "operations",
                "official",
                indexes=("operations/verification.md",),
                template="project-stage/operations",
                resolver="path",
            ),
        ),
    ),
}


ARTIFACT_PREFIXES: dict[str, ArtifactPrefix] = {
    "W": ArtifactPrefix("W", "work", "work item", "work"),
    "DE": ArtifactPrefix("DE", "decisions", "decision", "decisions"),
    "D": ArtifactPrefix(
        "D", "decisions", "legacy decision", "decisions", False, True
    ),
    "TH": ArtifactPrefix("TH", "roadmap", "theme", "theme"),
    "M": ArtifactPrefix("M", "roadmap", "milestone", "milestone"),
    "O": ArtifactPrefix("O", "state", "observation", "observation"),
    "Q": ArtifactPrefix("Q", "state", "question", "question"),
    "A": ArtifactPrefix("A", "state", "assumption", "assumption"),
    "K": ArtifactPrefix("K", "state", "risk", "risk"),
    "P": ArtifactPrefix("P", "proposals", "proposal", "proposals"),
}


V3_TO_V4_RELOCATIONS: dict[str, str] = {
    "past": "official",
    "present/work/items": "work/current",
    "present/work/retrospectives": "work/retrospectives",
    "present/work/active.md": "work/active.md",
    "present/work/review.md": "work/review.md",
    "present/work/decisions": "decisions/pending",
    "present/state": "state",
    "future/backlog/items": "work/planned",
    "future/backlog/index.md": "work/planned/index.md",
    "future/backlog/views": "work/views",
    "future/proposals": "proposals",
    "future/roadmap": "roadmap",
}


def get_family(name: str) -> FamilyRecord:
    """Return a family or fail on an unknown registry key."""

    try:
        return FAMILIES[name]
    except KeyError as exc:
        raise ValueError(f"unknown Stage family: {name}") from exc


def get_zone(family: str, zone: str) -> ZoneRecord:
    """Return a named zone within a family."""

    for record in get_family(family).zones:
        if record.name == zone:
            return record
    raise ValueError(f"unknown Stage zone: {family}/{zone}")


def _clean_stage_path(path: str) -> str:
    value = re.sub(r"/+", "/", path.strip().replace("\\", "/")).strip("/")
    if value == ".stage":
        return ""
    if value.startswith(".stage/"):
        return value[len(".stage/") :]
    return value


def _contains(root: str, path: str) -> bool:
    return path == root or path.startswith(root + "/")


def resolve_zone(path: str) -> tuple[str, ZoneRecord] | None:
    """Resolve a canonical v4 path to exactly one family zone."""

    clean = _clean_stage_path(path)
    matches = [
        (family.name, zone)
        for family in FAMILIES.values()
        for zone in family.zones
        if _contains(zone.canonical_path, clean)
    ]
    if not matches:
        return None
    matches.sort(key=lambda match: len(match[1].canonical_path), reverse=True)
    longest = len(matches[0][1].canonical_path)
    winners = [match for match in matches if len(match[1].canonical_path) == longest]
    if len(winners) != 1:
        raise ValueError(f"path has multiple Stage zone classifications: {path}")
    return winners[0]


def resolve_lifecycle(
    path: str,
    *,
    status: str | None = None,
    decision_state: str | None = None,
) -> str:
    """Resolve one artifact lifecycle, validating location/status agreement.

    Roadmap records keep a fixed residence, so callers provide the lifecycle derived
    from their effective decision chain through ``decision_state``.
    """

    resolved = resolve_zone(path)
    if resolved is None:
        raise ValueError(f"path is outside the Stage topology: {path}")
    _, zone = resolved
    if zone.resolver_policy == "decision-chain":
        if decision_state not in LIFECYCLE_STATES:
            raise ValueError("roadmap lifecycle requires a planned/current/official decision_state")
        return decision_state
    if status is not None and zone.allowed_statuses and status not in zone.allowed_statuses:
        raise ValueError(f"status {status!r} is not allowed in {zone.canonical_path}")
    if zone.lifecycle_state is None:
        raise ValueError(f"zone has no static lifecycle: {zone.canonical_path}")
    return zone.lifecycle_state


def card_location_for_status(status: str, *, lifecycle: str | None = None) -> str:
    """Return the W-card record root for a status.

    ``rejected`` is valid before and after work starts, so its caller must also provide
    ``lifecycle`` to preserve single classification.
    """

    matches = [
        zone
        for zone in get_family("work").zones
        if status in zone.allowed_statuses
        and (lifecycle is None or zone.lifecycle_state == lifecycle)
    ]
    if len(matches) != 1:
        detail = " with lifecycle" if lifecycle is not None else ""
        raise ValueError(f"work status {status!r}{detail} does not resolve to exactly one zone")
    zone = matches[0]
    if zone.name == "official":
        return "official/work/archive/items"
    return zone.canonical_path


def retrospective_locations(retrospective_id: str | None = None) -> tuple[str, str]:
    """Return current and official retrospective locations, optionally for one R id."""

    roots = ("work/retrospectives", "official/work/archive/retrospectives")
    if retrospective_id is None:
        return roots
    if re.fullmatch(r"R-\d{3,}", retrospective_id) is None:
        raise ValueError(f"invalid retrospective id: {retrospective_id}")
    return (
        f"{roots[0]}/{retrospective_id}.md",
        f"{roots[1]}/{retrospective_id}.md",
    )


def scan_roots(purpose: str) -> tuple[str, ...]:
    """Derive deterministic record, audit, or session-context scan roots."""

    record_roots = {
        root for family in FAMILIES.values() for zone in family.zones for root in zone.record_roots
    }
    if purpose == "records":
        roots = record_roots
    elif purpose == "audit":
        roots = record_roots | {
            path
            for family in FAMILIES.values()
            for zone in family.zones
            for path in zone.index_surfaces
        }
    elif purpose == "context":
        roots = {
            root
            for root in record_roots
            if not root.startswith("official/canon")
            and not root.startswith("official/model")
            and not root.startswith("operations")
        }
    else:
        raise ValueError(f"unknown scan purpose: {purpose}")
    return tuple(sorted(roots))


_ID_PATTERN = re.compile(r"^(DE|TH|W|D|M|O|Q|A|K|P)-(\d{3,})$")


def parse_artifact_id(artifact_id: str) -> tuple[ArtifactPrefix, int]:
    """Parse a supported id; legacy widths of three or more remain valid."""

    match = _ID_PATTERN.fullmatch(artifact_id)
    if match is None:
        raise ValueError(f"invalid Stage artifact id: {artifact_id}")
    return ARTIFACT_PREFIXES[match.group(1)], int(match.group(2))


def next_artifact_id(prefix: str, existing_ids: Iterable[str]) -> str:
    """Mint the next 8-digit id using the prefix's family-local counter."""

    try:
        policy = ARTIFACT_PREFIXES[prefix]
    except KeyError as exc:
        raise ValueError(f"unknown Stage artifact prefix: {prefix}") from exc
    if not policy.mintable:
        raise ValueError(f"Stage artifact prefix {prefix} is legacy-resolve-only")
    values = []
    for artifact_id in existing_ids:
        try:
            candidate, number = parse_artifact_id(artifact_id)
        except ValueError:
            continue
        if candidate.counter_family == policy.counter_family:
            values.append(number)
    return f"{prefix}-{max(values, default=0) + 1:08d}"


def resolve_artifact_reference(artifact_id: str) -> ArtifactReference:
    """Return all legal record locations for an artifact id.

    Legacy ``D-`` references resolve only against the official decision archive.  New
    ``DE-`` identities retain the same filename through promotion.
    """

    prefix, _ = parse_artifact_id(artifact_id)
    filename = artifact_id + ".md"
    by_prefix = {
        "W": ("work/planned", "work/current", "official/work/archive/items"),
        "DE": ("decisions/pending", "official/decisions/records"),
        "D": ("official/decisions/records",),
        "TH": ("roadmap/themes",),
        "M": ("roadmap/milestones",),
        "O": ("state/observations",),
        "Q": ("state/questions",),
        "A": ("state/assumptions",),
        "K": ("state/risks",),
        "P": ("proposals",),
    }
    paths = tuple(f"{root}/{filename}" for root in by_prefix[prefix.prefix])
    return ArtifactReference(artifact_id, prefix.family, paths, prefix.legacy_resolve_only)


def legacy_root(path: str) -> str | None:
    """Return the retired schema-v3 root containing a path, if any."""

    clean = _clean_stage_path(path)
    legacy_roots = {origin.split("/", 1)[0] for origin in V3_TO_V4_RELOCATIONS}
    matches = [root for root in legacy_roots if _contains(root, clean)]
    return max(matches, key=len) if matches else None


def is_legacy_path(path: str) -> bool:
    """Return whether a path targets a schema-v3 topology root."""

    return legacy_root(path) is not None


def legacy_replacement_paths(path: str) -> tuple[str, ...]:
    """Return registry-derived v4 replacements for one retired v3 path.

    A recognized relocation resolves to one exact destination. A path under a
    retired wrapper but outside the known v3 tree resolves to the possible v4
    responsibility families that replaced that wrapper.
    """

    clean = _clean_stage_path(path)
    if not is_legacy_path(clean):
        return ()
    matches = [origin for origin in V3_TO_V4_RELOCATIONS if _contains(origin, clean)]
    if matches:
        origin = max(matches, key=len)
        suffix = clean[len(origin) :]
        return (V3_TO_V4_RELOCATIONS[origin] + suffix,)
    root = legacy_root(clean)
    if root is None:
        return ()
    return tuple(
        sorted(
            {
                destination.split("/", 1)[0]
                for origin, destination in V3_TO_V4_RELOCATIONS.items()
                if origin.split("/", 1)[0] == root
            }
        )
    )


def relocate_v3_path(path: str) -> str:
    """Translate one schema-v3 path through the longest matching relocation."""

    original = path.strip().replace("\\", "/")
    stage_prefixed = original.startswith(".stage/")
    clean = _clean_stage_path(original)
    matches = [origin for origin in V3_TO_V4_RELOCATIONS if _contains(origin, clean)]
    if not matches:
        return original
    origin = max(matches, key=len)
    suffix = clean[len(origin) :]
    relocated = V3_TO_V4_RELOCATIONS[origin] + suffix
    return (".stage/" if stage_prefixed else "") + relocated
