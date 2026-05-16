"""Pydantic models for Plot sketches.

v0.2 schema — introduces typed node `kind` + `parent_id` for nested containers,
and edge `action_verb` + `value_form` for value-flow semantics. See
`plot/docs/PHILOSOPHY.md` for the design rationale (two-layer structure,
Service-as-hub, composition vs decomposition).

v0.1 files remain loadable: all new fields default to None/[] and legacy
fields are unchanged.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter, field_validator, model_validator

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
#   actor            — a class of people in the value economy. People only —
#                      external APIs / systems / bots / infrastructure are
#                      *not* actors (out of scope until Mode 2 / time-axis).
#                      v0.11 redefines this from "person/system/organisation"
#                      to "class of people" — see plot/docs/IDENTITY.md.
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
    # v0.10 Step 3: Foundation symbol refs (Symbol/Component pattern). The
    # masters live on the Foundation canvas; instances can be placed on
    # Services and Service-Detail canvases to declare which Foundation
    # commitment a service answers to. See docs/CONCEPTS.md.
    "mission_ref",
    "value_ref",
    "identity_ref",
    # v0.10 Step 5: composition kinds inside a service_detail canvas.
    #   metric — how the service is measured (KPI, success rate, latency).
    #   step   — an ordered procedural step in the service's flow.
    "metric",
    "step",
    # v0.12: ``category`` is a thematic grouping of services. Replaces what
    # used to be the "top-level service" idiom — categories are pure
    # containers (no value creation themselves), and the actual services
    # they contain are leaf nodes (no further sub-service nesting). See
    # docs/IDENTITY.md for the why.
    "category",
]

# Composition kinds: must live inside a service (applies to SketchDoc and
# service_detail CanvasDoc alike).
# v0.10 Step 5: metric + step join the family.
_COMPOSITION_KINDS = {"rule", "content", "metric", "step"}


ValueForm = Literal[
    "economic",  # 경제 — 돈, 결제, 수수료
    "attention",  # 주목 — 관심, 트래픽, 도달
    "social",  # 사회 — 이름, 명성, 관계, 신뢰
    "cognitive",  # 인지 — 정보, 데이터, 노하우
    "experience",  # 경험 — 즐거움, 편의, 성취
    "access",  # 접근권 — 기회, 멤버십, 독점성
    "effort",  # 시간·노력 — 투입 시간, 창의 노동
]


# ---------------------------------------------------------------------------
# v0.15 Phase 1 — 15-way discriminated union (god ``SketchNode`` retired)
# ---------------------------------------------------------------------------
#
# Through v0.14 the canvas node model was a single god ``SketchNode``
# class carrying every typed field for every kind as a default-empty
# string / None. v0.15 splits this per kind via a Pydantic discriminated
# union (one ``BaseNodeFields`` subclass per kind, dispatched on the
# ``kind`` literal). See D-2026-05-12-B for the rationale.
#
# Class layout below:
#   BaseNodeFields                              — shared graph layer
#   ProjectNode / MissionNode / CoreValueNode   — Foundation 4 (v0.13)
#   IdentityNode
#   ActorNode / ActorRefNode / ServiceNode      — Actors + Services (v0.15.1)
#   CategoryNode / MissionRefNode / ValueRefNode
#   IdentityRefNode
#   MetricNode / StepNode / RuleNode / ContentNode  — composition (v0.15.2)
#
#   FoundationNode  — Foundation-only sub-union (4 kinds)
#   SketchNode      — full 15-way discriminated union


class BaseNodeFields(BaseModel):
    """Shared graph-level fields for every canvas node kind.

    Every per-kind class extends this; typed text fields are declared on
    the per-kind class only (no god-object pool of all fields).

    The ``_details_path_is_safe`` validator runs on every subclass so
    that any node carrying a ``details_path`` is path-traversal-checked
    at construction time.
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
    parent_id: str | None = None
    collapsed: bool = False
    is_root: bool = False
    details_path: str | None = None
    # v0.16.12 — owner identifier for multi-user prep. ``None`` when
    # authored by an anonymous / single-user session. Server fills
    # from session context once multi-user lands.
    owner: str | None = None

    @model_validator(mode="after")
    def _details_path_is_safe(self) -> BaseNodeFields:
        if self.details_path is None:
            return self
        path = self.details_path.strip()
        if not path:
            raise ValueError(f"node {self.id!r} details_path must not be blank")
        if path.startswith("/"):
            raise ValueError(f"node {self.id!r} details_path must be relative, got {path!r}")
        # Reject ``..`` segments to prevent escape; normalise slashes first.
        parts = path.replace("\\", "/").split("/")
        if any(part == ".." or part == "" for part in parts):
            raise ValueError(
                f"node {self.id!r} details_path must not contain '..' or empty segments"
            )
        return self


class ProjectNode(BaseNodeFields):
    """v0.13 Phase 1: ``project`` kind anchor.

    In v0.13 the project anchor's data lives in ``ProjectDoc.anchors`` and
    is rendered as a synthetic node by the viewer (not stored in
    canvas.json). This class is kept for symmetry with the other kinds and
    for the rare fully-derived case; canvas.json should not normally
    contain a ProjectNode.
    """

    kind: Literal["project"] = "project"


class MissionNode(BaseNodeFields):
    """v0.13 Phase 1: mission kind. Typed text (``what_we_do`` / ``why`` /
    ``direction``) lives in the per-node MD template, not in JSON."""

    kind: Literal["mission"] = "mission"
    what_we_do: str = ""
    why: str = ""
    direction: str = ""


class CoreValueNode(BaseNodeFields):
    """v0.13 Phase 1: core_value kind. Typed text (``definition`` / ``do`` /
    ``dont``) lives in the per-node MD template, not in JSON."""

    kind: Literal["core_value"] = "core_value"
    definition: str = ""
    do: str = ""
    dont: str = ""


class IdentityNode(BaseNodeFields):
    """v0.13 Phase 1: identity kind. Typed text (``description`` / ``do`` /
    ``dont``) lives in the per-node MD template, not in JSON."""

    kind: Literal["identity"] = "identity"
    description: str = ""
    do: str = ""
    dont: str = ""


# Discriminated union — the runtime + IDE narrows on ``kind`` automatically.
# Used by Phase 3's MD template I/O to instantiate the correct subclass per
# node (Pydantic dispatches via the ``kind`` literal).
FoundationNode = Annotated[
    ProjectNode | MissionNode | CoreValueNode | IdentityNode,
    Field(discriminator="kind"),
]

# Per-kind text-field map (used by Phase 3 to render / parse the MD
# template). Keep in sync with the subclass definitions above.
FOUNDATION_TYPED_TEXT_FIELDS: dict[str, list[str]] = {
    "project": [],
    "mission": ["what_we_do", "why", "direction"],
    "core_value": ["definition", "do", "dont"],
    "identity": ["description", "do", "dont"],
}

# v0.13 Phase 0 — the project anchor lives in ``ProjectDoc.anchors``,
# not in ``canvas.nodes``. The viewer injects a synthetic node with
# this id so user-drawn edges can legitimately reference it
# (D-2026-05-04-B: *"User may draw edges from / to the anchor like
# any other node"*). Mirrors ``viewer/src/canvases/sketch/constants.ts``
# ``PROJECT_ANCHOR_ID``. See D-2026-05-13-M.
PROJECT_ANCHOR_ID = "__project_anchor__"


# ---------------------------------------------------------------------------
# v0.15 Phase 1 — non-Foundation per-class Pydantic models
# ---------------------------------------------------------------------------
#
# Extends the v0.13 Phase-1 ``BaseNodeFields`` + ``FoundationNode``
# discriminated-union pattern to the remaining 11 node kinds. Each kind
# now owns only its own typed fields rather than living as defaults on
# the god ``SketchNode`` class.
#
# These classes are additive in v0.14.15; ``CanvasDoc.nodes`` still uses
# god ``SketchNode`` until v0.14.16 promotes ``SketchNode`` to the full
# 15-way discriminated union.
#
# The four ref classes carry their own ``@model_validator`` that mirrors
# the dispatch ``_ref_kind_requires_ref_id`` on god ``SketchNode``.


class ActorNode(BaseNodeFields):
    """v0.15 Phase 1: ``actor`` kind. A class of people in the value
    economy (PHILOSOPHY P5, IDENTITY.md ``Actor as class``)."""

    kind: Literal["actor"] = "actor"
    motivation: str = ""
    pain: str = ""
    side: Literal["operator", "user"] | None = None


class ActorRefNode(BaseNodeFields):
    """v0.15 Phase 1: ``actor_ref`` kind. References an actor master that
    lives on the Actors canvas. ``gives`` / ``receives`` capture the
    per-actor-per-service value flow (PHILOSOPHY P6 weakened form).
    ``side`` mirrors the referenced actor's side so the canvas can
    colour-code without dereferencing the master each render."""

    kind: Literal["actor_ref"] = "actor_ref"
    ref_actor_id: str | None = None
    gives: str = ""
    receives: str = ""
    side: Literal["operator", "user"] | None = None

    @model_validator(mode="after")
    def _ref_actor_id_required(self) -> ActorRefNode:
        if not self.ref_actor_id:
            raise ValueError(f"node {self.id!r} of kind 'actor_ref' requires ref_actor_id")
        return self


class ServiceNode(BaseNodeFields):
    """v0.15 Phase 1: ``service`` kind. The value-creating hub
    (PHILOSOPHY P5). Top-level (parent_id None) and sub-service share
    the same shape — the Inspector surfaces different fields per role."""

    kind: Literal["service"] = "service"
    target_side: Literal["operator", "user", "both"] | None = None
    what: str = ""
    value_created: str = ""
    scope: str = ""
    trigger: str = ""
    how: str = ""
    outcome: str = ""
    do: str = ""
    dont: str = ""


class CategoryNode(BaseNodeFields):
    """v0.15 Phase 1: ``category`` kind. Thematic grouping of services on
    the Services canvas; a pure container with no value creation of its
    own. ``theme`` is the one-line statement of the common thread."""

    kind: Literal["category"] = "category"
    theme: str = ""


class MissionRefNode(BaseNodeFields):
    """v0.15 Phase 1: ``mission_ref`` kind. References a Foundation
    Mission master; lets a service declare which Mission it answers to."""

    kind: Literal["mission_ref"] = "mission_ref"
    ref_mission_id: str | None = None

    @model_validator(mode="after")
    def _ref_mission_id_required(self) -> MissionRefNode:
        if not self.ref_mission_id:
            raise ValueError(f"node {self.id!r} of kind 'mission_ref' requires ref_mission_id")
        return self


class ValueRefNode(BaseNodeFields):
    """v0.15 Phase 1: ``value_ref`` kind. References a Foundation
    CoreValue master; lets a service declare which Core Value it
    answers to."""

    kind: Literal["value_ref"] = "value_ref"
    ref_value_id: str | None = None

    @model_validator(mode="after")
    def _ref_value_id_required(self) -> ValueRefNode:
        if not self.ref_value_id:
            raise ValueError(f"node {self.id!r} of kind 'value_ref' requires ref_value_id")
        return self


class IdentityRefNode(BaseNodeFields):
    """v0.15 Phase 1: ``identity_ref`` kind. References a Foundation
    Identity master; lets a service declare which Identity aspect it
    expresses."""

    kind: Literal["identity_ref"] = "identity_ref"
    ref_identity_id: str | None = None

    @model_validator(mode="after")
    def _ref_identity_id_required(self) -> IdentityRefNode:
        if not self.ref_identity_id:
            raise ValueError(f"node {self.id!r} of kind 'identity_ref' requires ref_identity_id")
        return self


# ---------------------------------------------------------------------------
# v0.15 Phase 1.2 — composition kinds (live inside service_detail canvases)
# ---------------------------------------------------------------------------


class MetricNode(BaseNodeFields):
    """v0.15 Phase 1.2: ``metric`` kind. How a service is measured
    (KPI, success rate, latency)."""

    kind: Literal["metric"] = "metric"
    target: str = ""
    measurement: str = ""


class StepNode(BaseNodeFields):
    """v0.15 Phase 1.2: ``step`` kind. An ordered procedural step in the
    service flow. ``order`` may be None for unordered / parallel branches."""

    kind: Literal["step"] = "step"
    order: int | None = None
    outcome: str = ""


class RuleNode(BaseNodeFields):
    """v0.15 Phase 1.2: ``rule`` kind. A composition element inside a
    service expressing an enforced policy (with per-actor permissions)."""

    kind: Literal["rule"] = "rule"
    policy: str = ""
    enforcement: str = ""
    actor_permissions: dict[str, str] = Field(default_factory=dict)


class ContentNode(BaseNodeFields):
    """v0.15 Phase 1.2: ``content`` kind. A produced / consumed artifact
    inside a service (JSON / MD / image, with producer + consumer actor
    masters by id)."""

    kind: Literal["content"] = "content"
    format: str = ""
    producer_actor_id: str | None = None
    consumer_actor_id: str | None = None


# ---------------------------------------------------------------------------
# v0.15 Phase 1.2 — 15-way discriminated union (replaces god ``SketchNode``)
# ---------------------------------------------------------------------------
#
# Pydantic dispatches construction / validation on the ``kind`` literal.
# ``CanvasDoc.nodes: list[SketchNode]`` automatically narrows each node to
# its correct kind subclass. Use ``SketchNode`` for type annotations and
# the per-kind classes for direct construction.

SketchNode = Annotated[
    ProjectNode
    | MissionNode
    | CoreValueNode
    | IdentityNode
    | ActorNode
    | ActorRefNode
    | ServiceNode
    | CategoryNode
    | MissionRefNode
    | ValueRefNode
    | IdentityRefNode
    | MetricNode
    | StepNode
    | RuleNode
    | ContentNode,
    Field(discriminator="kind"),
]

# Validate raw dicts against the discriminated union without going through
# a ``CanvasDoc`` wrapper. Equivalent to ``BaseModel.model_validate`` on
# the legacy god class — call sites that need per-kind dispatch on a
# standalone dict use ``SketchNodeAdapter.validate_python(raw)``.
SketchNodeAdapter: TypeAdapter[
    ProjectNode
    | MissionNode
    | CoreValueNode
    | IdentityNode
    | ActorNode
    | ActorRefNode
    | ServiceNode
    | CategoryNode
    | MissionRefNode
    | ValueRefNode
    | IdentityRefNode
    | MetricNode
    | StepNode
    | RuleNode
    | ContentNode
] = TypeAdapter(SketchNode)


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
#   foundation        — project / mission / core_value / identity (singleton).
#                       v0.10 renamed from ``core``.
#   actors            — Actor definitions (singleton, SSOT for actor identities)
#   services          — top-level services (singleton). v0.8 renamed from
#                       ``services_overview``; paired with ``service_detail``
#                       for the per-service drill-down.
#   service_detail    — per-service drill-down (one per service in overview)
#
# Each ``CanvasDoc`` enforces its own allowed ``NodeKind`` set and structural
# rules; shared validators (edge refs, parent cycles, unique ids) still apply.

CanvasKind = Literal["foundation", "actors", "services", "service_detail"]

# v0.10 Step 3: Foundation refs are admitted on the Services overview *and*
# Service-Detail canvases — services can declare which Mission / Value /
# Identity they answer to without leaving the canvas.
_FOUNDATION_REFS = {"mission_ref", "value_ref", "identity_ref"}

_ALLOWED_KINDS_BY_CANVAS: dict[str, set[str]] = {
    "foundation": {"project", "mission", "core_value", "identity"},
    # v0.11.4 — project anchor is now visible on every primary canvas so the
    # mental model "everything spreads out from the project" reads at a
    # glance. The Foundation canvas remains the sole master (label-sync
    # source from ProjectDoc.name); the actors / services instances are
    # auto-seeded copies kept in sync.
    "actors": {"actor", "project"},
    # v0.12 — services canvas (top view) carries:
    #   - project anchor (centre)
    #   - category (thematic grouping)
    #   - service (leaf, child of a category via parent_id)
    # Categories sit at the top level; services are nested inside them.
    # All sub-service / refs / composition still live in service_detail.
    "services": {"project", "category", "service"},
    "service_detail": {
        "service",
        "rule",
        "content",
        "metric",
        "step",
        "actor_ref",
    }
    | _FOUNDATION_REFS,
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
        # The synthetic project anchor lives in ``ProjectDoc.anchors``,
        # not in ``self.nodes`` — but user-drawn edges may legitimately
        # reference it per D-2026-05-04-B SPEC mandate. Treat its id as
        # a known endpoint for validation. See D-2026-05-13-M.
        node_ids = {n.id for n in self.nodes} | {PROJECT_ANCHOR_ID}
        dangling = [
            e for e in self.edges
            if e.source not in node_ids or e.target not in node_ids
        ]
        if dangling:
            # Report the *missing endpoint ids*, not the edge ids.
            # The previous ``{e.id for e in dangling}`` produced misleading
            # error text (it surfaced edge ids as if they were missing
            # nodes), which sent D-2026-05-13-I diagnosis down a wrong
            # path. Fixed in D-2026-05-13-M.
            missing = sorted({
                ep for e in dangling
                for ep in (e.source, e.target)
                if ep not in node_ids
            })
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
    def _foundation_canvas_rules(self) -> CanvasDoc:
        if self.canvas_kind != "foundation":
            return self
        # v0.13 Phase 0: project anchor is now stored in ProjectDoc.anchors,
        # not as a node here. Old v0.12 files may still have a project node;
        # tolerate it (the migrator removes them) but enforce uniqueness +
        # top-level if present.
        projects = [n for n in self.nodes if n.kind == "project"]
        if len(projects) > 1:
            raise ValueError(
                f"foundation canvas may carry at most one legacy project node; "
                f"found {len(projects)}"
            )
        if projects and projects[0].parent_id is not None:
            raise ValueError(
                f"project node {projects[0].id!r} must be top-level (parent_id = null)"
            )
        missions = [n for n in self.nodes if n.kind == "mission"]
        identities = [n for n in self.nodes if n.kind == "identity"]
        if len(missions) < 1:
            raise ValueError(
                f"foundation canvas requires at least one mission node; found {len(missions)}"
            )
        if len(identities) < 1:
            raise ValueError(
                f"foundation canvas requires at least one identity node; found {len(identities)}"
            )
        return self

    @model_validator(mode="after")
    def _services_canvas_rules(self) -> CanvasDoc:
        if self.canvas_kind != "services":
            return self
        # v0.12 — nested nodes are now allowed (a category contains its
        # services), but only in this specific shape:
        #   * project anchor: top-level (parent_id is None)
        #   * category: top-level
        #   * service: must have parent_id set, and the parent must be a
        #     category (services are leaves nested inside categories)
        by_id = {n.id: n for n in self.nodes}
        for n in self.nodes:
            if n.kind == "service":
                if n.parent_id is None:
                    raise ValueError(
                        f"service {n.id!r} on services canvas must be nested "
                        "inside a category (parent_id required). v0.12: "
                        "top-level services are now categories."
                    )
                parent = by_id.get(n.parent_id)
                if parent is None or parent.kind != "category":
                    parent_kind = parent.kind if parent else "missing"
                    raise ValueError(
                        f"service {n.id!r}'s parent must be a category, got {parent_kind!r}"
                    )
            elif n.kind == "category":
                if n.parent_id is not None:
                    raise ValueError(
                        f"category {n.id!r} must be top-level on services "
                        "canvas (no nested categories in v0.12)"
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

    @model_validator(mode="after")
    def _actors_canvas_minimum(self) -> CanvasDoc:
        # v0.11 — IDENTITY.md "Service minimum baseline": every project needs
        # ≥ 2 actor classes (typically operator + user). Without two sides,
        # value exchange can't happen.
        if self.canvas_kind != "actors":
            return self
        actors = [n for n in self.nodes if n.kind == "actor"]
        if len(actors) < 2:
            raise ValueError(
                f"actors canvas requires at least 2 actor classes "
                f"(operator + user), got {len(actors)}. See IDENTITY.md."
            )
        return self

    @model_validator(mode="after")
    def _service_detail_actor_refs_minimum(self) -> CanvasDoc:
        # v0.11 — every service must have ≥ 2 participating actor_refs.
        # IDENTITY.md "Service minimum baseline": a playground with one
        # person isn't a playground. Side-mix (operator + user explicitly)
        # is encouraged via Inspector UI for v0.11.0 — hard side-mix
        # validation deferred to a later release once migration is complete.
        if self.canvas_kind != "service_detail":
            return self
        actor_refs = [n for n in self.nodes if n.kind == "actor_ref"]
        if len(actor_refs) < 2:
            raise ValueError(
                f"service_detail {self.canvas_id!r} requires at least 2 "
                f"actor_ref nodes (operator + user), got {len(actor_refs)}. "
                "See IDENTITY.md."
            )
        return self


class AnchorPlacement(BaseModel):
    """v0.13 Phase 0: per-canvas position/visual of the Project anchor.

    Before v0.13, every primary canvas (foundation/actors/services) carried
    its own ``project`` kind node, redundantly storing label / position / size /
    colour / shape on each. ProjectDoc.name was the only true SSOT for the
    label; positions duplicated.

    v0.13 promotes the anchor itself to ProjectDoc — one ``AnchorPlacement``
    per canvas kind. Canvas .json files no longer carry a ``project`` node;
    the renderer derives the anchor from ProjectDoc + canvas_kind and injects
    it into React Flow's node array at render time.
    """

    x: float = -75.0
    y: float = -75.0
    width: float = 150.0
    height: float = 150.0
    color: str = "#fef3c7"
    shape: Shape = "circle"


def _default_anchors() -> dict[str, AnchorPlacement]:
    return {
        "foundation": AnchorPlacement(),
        "actors": AnchorPlacement(),
        "services": AnchorPlacement(),
    }


class ProjectDoc(BaseModel):
    """Project-level metadata. Stored as ``.plot/sketches/{project_id}/project.json``.

    Replaces v0.1's monolithic ``SketchDoc`` as the top-level entity; nodes and
    edges move into per-canvas ``CanvasDoc`` files alongside.

    v0.13 Phase 0: ``anchors`` becomes the SSOT for the per-canvas Project
    anchor (was duplicated as a ``project`` node in every canvas .json).
    """

    id: str = Field(..., min_length=1)
    name: str = ""
    created: str = ""  # ISO date
    updated: str = ""  # ISO datetime
    version: int = 3
    # v0.13 Phase 0 — per-canvas project anchor positions. Default-seeded so
    # any project loaded from a v0.12 file gets sensible defaults without an
    # explicit migration; the migrator overwrites these from the old per-
    # canvas ``project`` nodes if any are present.
    anchors: dict[str, AnchorPlacement] = Field(default_factory=_default_anchors)

    @field_validator("id")
    @classmethod
    def _kebab_id(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(f"project id must be alphanumeric with -/_ only, got {v!r}")
        return v
