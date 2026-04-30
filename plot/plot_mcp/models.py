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
]

# v0.10 Step 3: which ref kind requires which id field. Used by the
# validator below and by callers that need to enumerate ref kinds.
_REF_KIND_TO_ID_FIELD: dict[str, str] = {
    "actor_ref": "ref_actor_id",
    "mission_ref": "ref_mission_id",
    "value_ref": "ref_value_id",
    "identity_ref": "ref_identity_id",
}

# Composition kinds: must live inside a service (applies to SketchDoc and
# service_detail CanvasDoc alike).
# v0.10 Step 5: metric + step join the family.
_COMPOSITION_KINDS = {"rule", "content", "metric", "step"}


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

    # v0.10 Step 3: Foundation refs. Each is required when its corresponding
    # ref kind is set; ignored otherwise. The picker fills these in.
    ref_mission_id: str | None = None
    ref_value_id: str | None = None
    ref_identity_id: str | None = None

    # v0.10 typed fields per kind. All optional ``""`` defaults so the
    # same model carries any subset; the Inspector form chooses which to
    # surface for each kind. The fields are clustered by their owning
    # kind in the comments below; v0.9.1's "all kinds get all fields"
    # generic pool is gone, but the schema is still permissive — any
    # unused field stays empty without runtime cost.
    #
    # mission (Foundation, kind="mission"):
    what_we_do: str = ""
    why: str = ""
    direction: str = ""

    # core_value (Foundation, kind="core_value"):
    #   ``definition`` — one or two sentences explaining what the value means.
    # identity (Foundation, kind="identity"):
    #   ``description`` — how the aspect is expressed (Voice / Energy / …).
    # Shared between core_value and identity (and any future kind that finds
    # the Do/Don't pair useful — see CONCEPTS.md "AI-first" principle):
    #   ``do``   — concrete positive example ("we do X this way")
    #   ``dont`` — concrete anti-pattern ("we never do Y")
    definition: str = ""
    description: str = ""
    do: str = ""
    dont: str = ""

    # service (Services / Service-Detail, kind="service"):
    #   Top-level (parent_id is None) and sub-service (parent_id != None)
    #   share the same model — Inspector decides which fields to surface.
    #   ``what``         — concise statement of what the service is.
    #   ``value_created``— the value this service produces.
    #   ``scope``        — boundary statement (top-level only).
    #   ``trigger``      — what kicks the service off (sub-service).
    #   ``how``          — how it works (sub-service).
    #   ``outcome``      — observable end state (sub-service; shared with
    #                      ``step`` in v0.10 Step 5).
    #   ``do`` / ``dont`` — already declared above for core_value/identity;
    #                      reused here.
    what: str = ""
    value_created: str = ""
    scope: str = ""
    trigger: str = ""
    how: str = ""
    outcome: str = ""

    # metric (service_detail, kind="metric"):
    #   ``target``      — goal value or threshold (e.g. ">99% success").
    #   ``measurement`` — how the metric is measured.
    target: str = ""
    measurement: str = ""

    # step (service_detail, kind="step"):
    #   ``order`` — ordinal position in the procedural sequence; ``None``
    #               leaves the step unordered (e.g. parallel branches).
    #   ``outcome`` is shared with service (declared above).
    order: int | None = None

    # actor (Actors canvas, kind="actor"):
    #   v0.11 — actors carry ``motivation`` (internal driver — why this actor
    #   participates in the project's services) and ``pain`` (struggles or
    #   frustrations the actor faces). Standard persona-design pair, with
    #   the AI-first framing from IDENTITY.md.
    motivation: str = ""
    pain: str = ""

    # actor_ref (service / service_detail, kind="actor_ref"):
    #   v0.11 Phase C3 — each ref captures the value flow between this actor
    #   and the service it sits in. ``gives`` and ``receives`` are
    #   per-actor-per-service; service.value_created is the aggregate. The
    #   weakened version of PHILOSOPHY.md P6 ("arrows carry action + value")
    #   — the value flow lives on the node instead of an explicit edge.
    gives: str = ""
    receives: str = ""
    # ``side`` partitions actors by which side of the value exchange they
    # occupy. v0.11 settles on two values; ``external`` etc. may be added
    # later if a domain demands it.
    #   ``operator`` — service operators / developers. Always explicit on
    #                  every service per IDENTITY.md (moderation duty).
    #   ``user``     — service users / consumers / participants.
    side: Literal["operator", "user"] | None = None

    # rule (service_detail, kind="rule"):
    #   ``policy``      — the rule statement (what's enforced).
    #   ``enforcement`` — how it's enforced (mechanism, system).
    #   ``actor_permissions`` — actor-id → permission-string, e.g.
    #                           ``{"user": "RUD", "admin": "CRUD"}``. The
    #                           permission string is free-form for now;
    #                           "C/R/U/D" is the suggested vocabulary.
    policy: str = ""
    enforcement: str = ""
    actor_permissions: dict[str, str] = Field(default_factory=dict)

    # content (service_detail, kind="content"):
    #   ``format``             — shape of the artifact (JSON, MD, image…).
    #   ``producer_actor_id``  — actor master id that creates the content.
    #   ``consumer_actor_id``  — actor master id that consumes the content.
    format: str = ""
    producer_actor_id: str | None = None
    consumer_actor_id: str | None = None

    # v0.9.1 long-form pointer. Project-relative path (e.g.
    # ``"foundation/mission-1/details.md"``); Plot resolves it under
    # ``.plot/{project_id}/``. ``None`` means the node has no MD file yet
    # — the Inspector offers a "Create details" button to mint one.
    details_path: str | None = None

    @model_validator(mode="after")
    def _ref_kind_requires_ref_id(self) -> SketchNode:
        # v0.10 Step 3: every *_ref kind requires its matching id field set.
        # The pre-existing actor_ref check is a special case of the same rule.
        field = _REF_KIND_TO_ID_FIELD.get(self.kind or "")
        if field and not getattr(self, field, None):
            raise ValueError(f"node {self.id!r} of kind {self.kind!r} requires {field}")
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
    "actors": {"actor"},
    "services": {"service"} | _FOUNDATION_REFS,
    "service_detail": {
        "service",
        "rule",
        "content",
        "metric",
        "step",
        "actor_ref",
    } | _FOUNDATION_REFS,
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
    def _foundation_canvas_rules(self) -> CanvasDoc:
        if self.canvas_kind != "foundation":
            return self
        projects = [n for n in self.nodes if n.kind == "project"]
        missions = [n for n in self.nodes if n.kind == "mission"]
        identities = [n for n in self.nodes if n.kind == "identity"]
        if len(projects) != 1:
            raise ValueError(
                f"foundation canvas requires exactly one project node; found {len(projects)}"
            )
        if projects[0].parent_id is not None:
            raise ValueError(
                f"project node {projects[0].id!r} must be top-level (parent_id = null)"
            )
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
        nested = [n for n in self.nodes if n.parent_id is not None]
        if nested:
            raise ValueError(
                "services canvas forbids nested nodes (use service_detail for "
                f"decomposition); offending: {sorted(n.id for n in nested)}"
            )
        # v0.11 Phase C2 — when at least one top-level service exists on the
        # canvas, at least one Foundation anchor (mission_ref / value_ref /
        # identity_ref) must also be present. This enforces IDENTITY.md's
        # "alignment ownership must be visible" floor without forcing a 1:1
        # service↔anchor mapping (the visual layout carries that nuance).
        # An empty services canvas (no services yet) is fine.
        services = [n for n in self.nodes if n.kind == "service"]
        if services:
            anchors = [
                n
                for n in self.nodes
                if n.kind in {"mission_ref", "value_ref", "identity_ref"}
            ]
            if not anchors:
                raise ValueError(
                    "services canvas with top-level services requires at least "
                    "one Foundation anchor (mission_ref / value_ref / "
                    "identity_ref). See IDENTITY.md."
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
