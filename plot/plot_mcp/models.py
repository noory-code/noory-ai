"""Pydantic models for Plot sketches.

v0.2 schema — introduces typed node `kind` + `parent_id` for nested containers,
and edge `action_verb` + `value_form` for value-flow semantics. See
`plot/docs/PHILOSOPHY.md` for the design rationale (two-layer structure,
Service-as-hub, composition vs decomposition).

v0.1 files remain loadable: all new fields default to None/[] and legacy
fields are unchanged.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

Shape = Literal[
    "rectangle",
    "rounded",
    "circle",
    "ellipse",
    "diamond",
    "hexagon",
    "octagon",
]

# v0.2 node kinds. See PHILOSOPHY.md (P5, P11).
#
# Canvas anchors (Core):
#   project          — central anchor of the Core canvas; exactly 1 per project,
#                      auto-seeded, cannot be deleted, label mirrors ProjectDoc.name.
#   mission          — statement of purpose; 1..N per Core canvas.
#   core_value       — a value the project commits to; 0..N per Core canvas.
#   identity         — an aspect of the project's identity (label = "Voice" /
#                      "Energy" / "Speech style" / "Visual tone" / …); 1..N peers.
#                      v0.5 absorbed the former ``identity_facet`` kind.
#   actor            — participant in the value economy (Actor canvas only).
#   actor_ref        — reference to an actor (Service canvases); carries
#                      ``ref_actor_id`` pointing at an actor in the Actor canvas.
#   service          — value-creating hub (Overview root, Detail root, sub-service).
#   rule             — composition element inside a service (Detail only).
#   content          — composition element inside a service (Detail only).
#
# Sub-service and sub-actor are not new kinds — they're service/actor with
# a non-null parent_id (hierarchy / decomposition).
#
# Deprecated (migrated on open by ``migrate._migrate_v04_core_schema``):
#   core             — former Core root anchor (octagon). Removed in v0.3;
#                      remaining disk nodes are converted to ``project``.
#   identity_facet   — child of identity. Absorbed into ``identity`` in v0.5
#                      with parent_id cleared (flat peer model).
NodeKind = Literal[
    "project",
    "mission",
    "core_value",
    "identity",
    "actor",
    "actor_ref",
    "service",
    "rule",
    "content",
]

# Composition kinds: must live inside a service (applies to SketchDoc and
# service_detail CanvasDoc alike).
_COMPOSITION_KINDS = {"rule", "content"}


class SketchNode(BaseModel):
    """A freeform node on the canvas.

    v0.9 splits content storage cleanly:
      - **Typed short fields** (``tagline`` / ``audience`` / ... / ``summary``)
        live in this model and are written/read only by Plot itself.
      - **Long-form prose** lives in a separate ``details.md`` file
        addressed by ``details_path``. Plot reads/writes that file too,
        but external editors (Obsidian, VS Code) may also edit it
        because Plot keeps no mirror of its content here — there's no
        sync conflict because the data isn't duplicated.

    The previous ``body`` field is gone in v0.9: its dual role (preview
    cache + edit target) was the source of every sync headache from v0.7
    and v0.8.
    """

    id: str = Field(..., min_length=1)
    label: str = ""
    x: float = 0.0
    y: float = 0.0
    width: float = 180.0
    height: float = 80.0
    color: str = "#ffffff"
    shape: Shape = "rounded"
    icon: str | None = None

    # v0.2 additions
    kind: NodeKind | None = None
    parent_id: str | None = None
    collapsed: bool = False

    # v0.2 root fields (2026-04-20)
    # A sketch may designate up to one Actor-root and one Service-root.
    # Roots carry Mission + Core Values + Identity for their respective
    # plane (organization-side vs product-side). Non-root nodes leave
    # these empty.
    #
    # v0.2 multi-canvas (2026-04-21) promotes Mission / CoreValue / Identity
    # to their own nodes inside the Core canvas — these string fields remain
    # for v0.1/v0.2-single-canvas backward compat and for the migration
    # script to read before converting them into nodes.
    is_root: bool = False
    mission: str = ""
    core_values: str = ""
    identity: str = ""

    # v0.2 multi-canvas: actor_ref nodes point at an actor in the Actor canvas.
    # Required when kind == "actor_ref"; ignored otherwise.
    ref_actor_id: str | None = None

    # v0.9.1 long-form pointer. Project-relative path (e.g.
    # ``"core/mission-1/details.md"``); Plot resolves it under
    # ``.plot/{project_id}/``. ``None`` means the node has no MD file yet
    # — the Inspector offers a "Create details" button to mint one.
    #
    # v0.9 briefly carried six typed fields (tagline / audience / method /
    # goal / summary / criteria) for kind-specific Inspector forms. v0.9.1
    # drops them: short text lives in the node's ``label``, long text
    # lives in ``details.md``, and any structure between (Tagline /
    # Audience / etc.) the user expresses freely inside the MD file.
    details_path: str | None = None

    @model_validator(mode="after")
    def _actor_ref_requires_ref_id(self) -> SketchNode:
        if self.kind == "actor_ref" and not self.ref_actor_id:
            raise ValueError(f"node {self.id!r} of kind 'actor_ref' requires ref_actor_id")
        return self

    @model_validator(mode="after")
    def _details_path_is_safe(self) -> SketchNode:
        if self.details_path is None:
            return self
        path = self.details_path.strip()
        if not path:
            raise ValueError(f"node {self.id!r} details_path must not be blank")
        if path.startswith("/"):
            raise ValueError(
                f"node {self.id!r} details_path must be relative, got {path!r}"
            )
        # Reject ``..`` segments to prevent escape; normalise slashes first.
        parts = path.replace("\\", "/").split("/")
        if any(part == ".." or part == "" for part in parts):
            raise ValueError(
                f"node {self.id!r} details_path must not contain '..' or empty segments"
            )
        return self


ValueForm = Literal[
    "economic",  # 경제 — 돈, 결제, 수수료
    "attention",  # 주목 — 관심, 트래픽, 도달
    "social",  # 사회 — 이름, 명성, 관계, 신뢰
    "cognitive",  # 인지 — 정보, 데이터, 노하우
    "experience",  # 경험 — 즐거움, 편의, 성취
    "access",  # 접근권 — 기회, 멤버십, 독점성
    "effort",  # 시간·노력 — 투입 시간, 창의 노동
]


class SketchEdge(BaseModel):
    """A freeform edge between two nodes."""

    id: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    target: str = Field(..., min_length=1)
    source_handle: str | None = Field(default=None, alias="sourceHandle")
    target_handle: str | None = Field(default=None, alias="targetHandle")
    label: str = ""
    style: Literal["solid", "dashed"] = "solid"

    # v0.2 additions
    action_verb: str | None = None
    value_form: list[ValueForm] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# v0.2 multi-canvas (2026-04-21)
# ---------------------------------------------------------------------------
#
# A project is split into four canvas kinds:
#
#   core              — Mission / CoreValue / Identity (singleton)
#   actors            — Actor definitions (singleton, SSOT for actor identities)
#   services          — top-level services (singleton). v0.8 renamed from
#                       ``services_overview``; paired with ``service_detail``
#                       for the per-service drill-down.
#   service_detail    — per-service drill-down (one per service in overview)
#
# Each ``CanvasDoc`` enforces its own allowed ``NodeKind`` set and structural
# rules; shared validators (edge refs, parent cycles, unique ids) still apply.
# The old monolithic ``SketchDoc`` stays alongside during migration.

CanvasKind = Literal["core", "actors", "services", "service_detail"]

_ALLOWED_KINDS_BY_CANVAS: dict[str, set[str]] = {
    "core": {"project", "mission", "core_value", "identity"},
    "actors": {"actor"},
    "services": {"service"},
    "service_detail": {"service", "rule", "content", "actor_ref"},
}


class CanvasDoc(BaseModel):
    """One logical canvas (Core, Actors, Services Overview, or a Service Detail).

    Stored as ``.plot/sketches/{project_id}/{canvas_id}.json`` in v0.2.
    """

    canvas_id: str = Field(..., min_length=1)
    canvas_kind: CanvasKind
    # service_detail only: the ``service`` node id this detail canvas drills into.
    # Must equal ``canvas_id`` to keep the 1:1 pairing with the Overview node.
    service_ref: str | None = None
    nodes: list[SketchNode] = Field(default_factory=list)
    edges: list[SketchEdge] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_ids(self) -> CanvasDoc:
        if len({n.id for n in self.nodes}) != len(self.nodes):
            raise ValueError("node ids must be unique")
        if len({e.id for e in self.edges}) != len(self.edges):
            raise ValueError("edge ids must be unique")
        return self

    @model_validator(mode="after")
    def _edges_reference_nodes(self) -> CanvasDoc:
        node_ids = {n.id for n in self.nodes}
        dangling = [e for e in self.edges if e.source not in node_ids or e.target not in node_ids]
        if dangling:
            missing = sorted({e.id for e in dangling})
            raise ValueError(f"edges reference unknown nodes: {missing}")
        return self

    @model_validator(mode="after")
    def _parent_ids_are_valid(self) -> CanvasDoc:
        by_id = {n.id: n for n in self.nodes}
        for n in self.nodes:
            if n.parent_id is None:
                continue
            if n.parent_id == n.id:
                raise ValueError(f"node {n.id!r} cannot be its own parent")
            if n.parent_id not in by_id:
                raise ValueError(f"node {n.id!r}.parent_id points to unknown node {n.parent_id!r}")
        for start in self.nodes:
            seen: set[str] = set()
            current: str | None = start.id
            while current is not None:
                if current in seen:
                    raise ValueError(f"parent chain contains a cycle at node {current!r}")
                seen.add(current)
                parent = by_id[current]
                current = parent.parent_id
        return self

    @model_validator(mode="after")
    def _kinds_allowed_on_canvas(self) -> CanvasDoc:
        allowed = _ALLOWED_KINDS_BY_CANVAS[self.canvas_kind]
        strays = sorted(
            {n.kind for n in self.nodes if n.kind is not None and n.kind not in allowed}
        )
        if strays:
            raise ValueError(
                f"kinds not allowed on {self.canvas_kind!r} canvas: {strays} "
                f"(allowed: {sorted(allowed)})"
            )
        return self

    @model_validator(mode="after")
    def _core_canvas_rules(self) -> CanvasDoc:
        if self.canvas_kind != "core":
            return self
        projects = [n for n in self.nodes if n.kind == "project"]
        missions = [n for n in self.nodes if n.kind == "mission"]
        identities = [n for n in self.nodes if n.kind == "identity"]
        if len(projects) != 1:
            raise ValueError(
                f"core canvas requires exactly one project node; found {len(projects)}"
            )
        if projects[0].parent_id is not None:
            raise ValueError(
                f"project node {projects[0].id!r} must be top-level (parent_id = null)"
            )
        if len(missions) < 1:
            raise ValueError(
                f"core canvas requires at least one mission node; found {len(missions)}"
            )
        if len(identities) < 1:
            raise ValueError(
                f"core canvas requires at least one identity node; found {len(identities)}"
            )
        return self

    @model_validator(mode="after")
    def _services_canvas_rules(self) -> CanvasDoc:
        if self.canvas_kind != "services":
            return self
        nested = [n for n in self.nodes if n.parent_id is not None]
        if nested:
            raise ValueError(
                "services canvas forbids nested nodes (use service_detail for "
                f"decomposition); offending: {sorted(n.id for n in nested)}"
            )
        return self

    @model_validator(mode="after")
    def _detail_canvas_rules(self) -> CanvasDoc:
        if self.canvas_kind != "service_detail":
            return self
        if not self.service_ref:
            raise ValueError("service_detail canvas requires service_ref")
        if self.service_ref != self.canvas_id:
            raise ValueError(
                f"service_detail service_ref {self.service_ref!r} must match "
                f"canvas_id {self.canvas_id!r}"
            )
        root_services = [n for n in self.nodes if n.kind == "service" and n.id == self.canvas_id]
        if not root_services:
            raise ValueError(
                f"service_detail canvas must contain a root service with id {self.canvas_id!r}"
            )
        # Composition kinds must live inside a service (same rule as SketchDoc).
        by_id = {n.id: n for n in self.nodes}
        for n in self.nodes:
            if n.kind not in _COMPOSITION_KINDS:
                continue
            if n.parent_id is None:
                raise ValueError(
                    f"node {n.id!r} of kind {n.kind!r} requires a parent_id "
                    "(must live inside a service)"
                )
            parent = by_id.get(n.parent_id)
            if parent is not None and parent.kind != "service":
                raise ValueError(
                    f"node {n.id!r} of kind {n.kind!r} must be a child of a "
                    f"service, but parent has kind {parent.kind!r}"
                )
        return self


class ProjectDoc(BaseModel):
    """Project-level metadata. Stored as ``.plot/sketches/{project_id}/project.json``.

    Replaces v0.1's monolithic ``SketchDoc`` as the top-level entity; nodes and
    edges move into per-canvas ``CanvasDoc`` files alongside.
    """

    id: str = Field(..., min_length=1)
    name: str = ""
    created: str = ""  # ISO date
    updated: str = ""  # ISO datetime
    version: int = 2

    @field_validator("id")
    @classmethod
    def _kebab_id(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(f"project id must be alphanumeric with -/_ only, got {v!r}")
        return v
