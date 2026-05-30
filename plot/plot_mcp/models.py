"""Pydantic models for Plot sketches.

v0.2 schema — introduces typed node `kind` + `parent_id` for nested containers,
and edge `action_verb` + `value_form` for value-flow semantics. See
`plot/docs/PHILOSOPHY.md` for the design rationale (two-layer structure,
Service-as-hub, composition vs decomposition).

v0.1 files remain loadable: all new fields default to None/[] and legacy
fields are unchanged.
"""

from __future__ import annotations

import re
from typing import Annotated, Any, Literal

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
    # v0.28.0: decision — a flowchart decision (diamond) branch point in a
    #   service_detail flow (user choice or system judgment). See
    #   docs/DECISIONS.md D-2026-05-30-C.
    "decision",
    # v0.29.0: group — a container that chunks a busy service_detail flow
    #   (collapse N branches into one). See docs/DECISIONS.md D-2026-05-30-I.
    "group",
    # v0.12: ``category`` is a thematic grouping of services. Replaces what
    # used to be the "top-level service" idiom — categories are pure
    # containers (no value creation themselves), and the actual services
    # they contain are leaf nodes (no further sub-service nesting). See
    # docs/IDENTITY.md for the why.
    "category",
]

# Composition kinds: must live inside a service (applies to SketchDoc and
# service_detail CanvasDoc alike).
# v0.10 Step 5: metric + step join the family. v0.28.0: decision joins.
# v0.29.0: group joins.
_COMPOSITION_KINDS = {"rule", "content", "metric", "step", "decision", "group"}


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
    # v0.24.15 (D-2026-05-24-A) — reduced from 140×60 to 80×36, follow-up
    # to D-2026-05-17-N. Tighter default suits Services / ServiceDetail
    # hub-spoke layouts without overflow. Existing nodes keep their own
    # values in canvas.json; only nodes that omit width/height (defaults
    # filled by Pydantic) get the new size.
    width: float = 80.0
    height: float = 36.0
    color: str = "#ffffff"
    shape: Shape = "rounded"
    icon: str | None = None
    # v0.26.0 (D-2026-05-25-A) — ``parent_id`` removed. Hierarchy /
    # containment is now expressed via directed edges (``SketchEdge.directed``).
    # The v0.26 read-time migration in ``folder_io._migrate_parent_id_to_directed_edges``
    # converts pre-v0.26 ``parent_id`` to directed edges on first read.
    collapsed: bool = False
    is_root: bool = False
    details_path: str | None = None
    # v0.16.12 — owner identifier for multi-user prep. ``None`` when
    # authored by an anonymous / single-user session. Server fills
    # from session context once multi-user lands.
    owner: str | None = None
    # v0.17.2 Phase 2 (D-2026-05-16-C) — per-node version laying the
    # ground for Phase 3 "Publish" (MAJOR bump) + Phase 4 MINOR
    # propagation. Format: ``v<MAJOR>.<MINOR>`` (e.g. ``v1.0`` /
    # ``v2.3``). Defaults to ``v1.0`` so pre-Phase-2 canvases auto-fill
    # on read; first write after open serialises the new key.
    version: str = "v1.0"
    # v0.22.0 (D-2026-05-17-H) — publish dirty baseline. Captures the
    # content snapshot at the most recent publish (typed-text fields +
    # label + body + incident edges); visual fields excluded. Server
    # compares this to the current node + incident edges to compute
    # ``_dirty`` for the Inspector's publish button gate. ``None`` ⇒
    # never published (or pre-v0.22.0 migration) ⇒ treated as dirty
    # (initial publish is always allowed). Persisted in canvas.json
    # under the leading-underscore alias to mark it server-managed.
    publish_baseline: dict[str, Any] | None = Field(
        default=None, alias="_publish_baseline"
    )

    model_config = {"populate_by_name": True}

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

    @model_validator(mode="after")
    def _version_is_valid(self) -> BaseNodeFields:
        if not re.match(r"^v\d+\.\d+$", self.version):
            raise ValueError(
                f"node {self.id!r} version must match ``^v\\d+\\.\\d+$`` "
                f"(e.g. ``v1.0``), got {self.version!r}"
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
    """v0.17 Phase 1: mission kind. JSON = SSOT. Every typed-text field
    value (``what_we_do`` / ``why`` / ``direction`` / ``body``) is an
    MD-formatted string. Per-node MD files are publish-output only
    (Phase 3+). Pre-v0.17 projects are absorbed on first read via
    ``_absorb_md_typed_text_into_json``."""

    kind: Literal["mission"] = "mission"
    what_we_do: str = ""
    why: str = ""
    direction: str = ""
    body: str = ""


class CoreValueNode(BaseNodeFields):
    """v0.17 Phase 1: core_value kind. JSON = SSOT. Every typed-text field
    value (``definition`` / ``do`` / ``dont`` / ``body``) is an
    MD-formatted string. Per-node MD files are publish-output only
    (Phase 3+)."""

    kind: Literal["core_value"] = "core_value"
    definition: str = ""
    do: str = ""
    dont: str = ""
    body: str = ""


class IdentityNode(BaseNodeFields):
    """v0.17 Phase 1: identity kind. JSON = SSOT. Every typed-text field
    value (``description`` / ``do`` / ``dont`` / ``body``) is an
    MD-formatted string. Per-node MD files are publish-output only
    (Phase 3+)."""

    kind: Literal["identity"] = "identity"
    description: str = ""
    do: str = ""
    dont: str = ""
    body: str = ""


# Discriminated union — the runtime + IDE narrows on ``kind`` automatically.
# Used by Phase 3's MD template I/O to instantiate the correct subclass per
# node (Pydantic dispatches via the ``kind`` literal).
FoundationNode = Annotated[
    ProjectNode | MissionNode | CoreValueNode | IdentityNode,
    Field(discriminator="kind"),
]

# Per-kind H2-section field map for the *legacy* MD template parser.
# Each entry lists the typed fields that ``parse_md_template`` extracts
# from ``## Heading`` sections of pre-v0.17 ``foundation/{kind}-{slug}.md``
# files. Phase 1's ``_absorb_md_typed_text_into_json`` uses this to know
# which JSON keys to absorb from H2 content; the ``body`` field is
# separately sourced from the post-``---`` free prose, so it is NOT in
# this map. Keep in sync with the subclass definitions above.
FOUNDATION_TYPED_TEXT_FIELDS: dict[str, list[str]] = {
    "project": [],
    "mission": ["what_we_do", "why", "direction"],
    "core_value": ["definition", "do", "dont"],
    "identity": ["description", "do", "dont"],
}

# Per-kind *all-MD-syntax-fields-per-kind* map. JSON SSOT consumers
# (viewer MD-aware inspectors, Phase 3 publish output) iterate this
# list to know every field whose value is an MD-formatted string.
# Equals ``FOUNDATION_TYPED_TEXT_FIELDS[kind] + ["body"]`` for the 3
# typed-text kinds, empty otherwise.
FOUNDATION_MD_FIELDS: dict[str, list[str]] = {
    "project": [],
    "mission": ["what_we_do", "why", "direction", "body"],
    "core_value": ["definition", "do", "dont", "body"],
    "identity": ["description", "do", "dont", "body"],
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
    body: str = ""


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
    body: str = ""


class CategoryNode(BaseNodeFields):
    """v0.15 Phase 1: ``category`` kind. Thematic grouping of services on
    the Services canvas; a pure container with no value creation of its
    own. ``theme`` is the one-line statement of the common thread."""

    kind: Literal["category"] = "category"
    theme: str = ""
    body: str = ""


class MissionRefNode(BaseNodeFields):
    """v0.15 Phase 1: ``mission_ref`` kind. References a Foundation
    Mission master; lets a service declare which Mission it answers to.
    v0.24.x (D-2026-05-17-M): ``notes_in_context`` for service-context
    typed notes (4-ref symmetry with ActorRefNode's gives/receives)."""

    kind: Literal["mission_ref"] = "mission_ref"
    ref_mission_id: str | None = None
    notes_in_context: str = ""

    @model_validator(mode="after")
    def _ref_mission_id_required(self) -> MissionRefNode:
        if not self.ref_mission_id:
            raise ValueError(f"node {self.id!r} of kind 'mission_ref' requires ref_mission_id")
        return self


class ValueRefNode(BaseNodeFields):
    """v0.15 Phase 1: ``value_ref`` kind. References a Foundation
    CoreValue master; lets a service declare which Core Value it
    answers to. v0.24.x (D-2026-05-17-M): ``notes_in_context``."""

    kind: Literal["value_ref"] = "value_ref"
    ref_value_id: str | None = None
    notes_in_context: str = ""

    @model_validator(mode="after")
    def _ref_value_id_required(self) -> ValueRefNode:
        if not self.ref_value_id:
            raise ValueError(f"node {self.id!r} of kind 'value_ref' requires ref_value_id")
        return self


class IdentityRefNode(BaseNodeFields):
    """v0.15 Phase 1: ``identity_ref`` kind. References a Foundation
    Identity master; lets a service declare which Identity aspect it
    expresses. v0.24.x (D-2026-05-17-M): ``notes_in_context``."""

    kind: Literal["identity_ref"] = "identity_ref"
    ref_identity_id: str | None = None
    notes_in_context: str = ""

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
    body: str = ""


class StepNode(BaseNodeFields):
    """v0.15 Phase 1.2: ``step`` kind. An ordered procedural step in the
    service flow. ``order`` may be None for unordered / parallel branches."""

    kind: Literal["step"] = "step"
    order: int | None = None
    outcome: str = ""
    body: str = ""
    # v0.28.2 (D-2026-05-30-E): outcome valence for negative-case
    # (failure) visual distinction. "neutral" = happy-path default.
    polarity: Literal["positive", "negative", "neutral"] = "neutral"


class DecisionNode(BaseNodeFields):
    """v0.28.0 (D-2026-05-30-C): ``decision`` kind. A flowchart decision
    (diamond) branch point inside a service_detail flow — a user choice
    (방식 선택) or a system judgment (검증 성공/실패). The branches are
    user-drawn labelled outgoing edges; the node carries only the
    question (``label``) + optional notes (``body``)."""

    kind: Literal["decision"] = "decision"
    body: str = ""


class GroupNode(BaseNodeFields):
    """v0.29.0 (D-2026-05-30-I): ``group`` kind. A container that chunks
    a busy service_detail flow — collapse N branches into one node.
    Membership lives here as ``member_ids`` (SSOT on the group; step /
    decision carry no group field). ``collapsed`` (BaseNodeFields)
    hides the members."""

    kind: Literal["group"] = "group"
    member_ids: list[str] = Field(default_factory=list)
    body: str = ""


class RuleNode(BaseNodeFields):
    """v0.15 Phase 1.2: ``rule`` kind. A composition element inside a
    service expressing an enforced policy (with per-actor permissions)."""

    kind: Literal["rule"] = "rule"
    policy: str = ""
    enforcement: str = ""
    actor_permissions: dict[str, str] = Field(default_factory=dict)
    body: str = ""


class ContentNode(BaseNodeFields):
    """v0.15 Phase 1.2: ``content`` kind. A produced / consumed artifact
    inside a service (JSON / MD / image, with producer + consumer actor
    masters by id)."""

    kind: Literal["content"] = "content"
    format: str = ""
    producer_actor_id: str | None = None
    consumer_actor_id: str | None = None
    body: str = ""


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
    | DecisionNode
    | GroupNode
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
    | DecisionNode
    | GroupNode
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

    # v0.26.0 (D-2026-05-25-A) — directed edges carry parent→child
    # semantics. When True, the renderer draws an arrowhead at the
    # target end and the fold / hierarchy logic treats source as
    # parent. New edges default to True; the v0.26 read-time migration
    # converts pre-v0.26 nodes' parent_id into directed=True edges.
    directed: bool = True

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
        "decision",
        "group",
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
        dangling = [e for e in self.edges if e.source not in node_ids or e.target not in node_ids]
        if dangling:
            # Report the *missing endpoint ids*, not the edge ids.
            # The previous ``{e.id for e in dangling}`` produced misleading
            # error text (it surfaced edge ids as if they were missing
            # nodes), which sent D-2026-05-13-I diagnosis down a wrong
            # path. Fixed in D-2026-05-13-M.
            missing = sorted(
                {ep for e in dangling for ep in (e.source, e.target) if ep not in node_ids}
            )
            raise ValueError(f"edges reference unknown nodes: {missing}")
        return self

    # v0.26.0 (D-2026-05-25-A) — ``_parent_ids_are_valid`` removed
    # alongside the ``parent_id`` field. Hierarchy invariants (no
    # self-parent, no cycles) are now properties of the directed-edge
    # graph; if needed, add a ``_directed_edge_acyclic`` validator
    # later. Pre-v0.26 data is migrated read-side, not validated here.

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
        # v0.26.0 (D-2026-05-25-A) — parent_id checks removed alongside
        # the field. Project-node top-levelness is now implicit (no
        # incoming directed edge); not validated at schema level.
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

    # v0.26.0 (D-2026-05-25-A) — ``_services_canvas_rules`` removed.
    # The "service must be nested in a category" and "category must be
    # top-level" invariants were enforced via ``parent_id``; with the
    # field gone, containment is expressed via directed edges, and the
    # canvas no longer enforces shape at the schema level. Domain
    # guidance moves to docs (CONCEPTS.md / SPEC.md §Services).

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
        # v0.26.0 (D-2026-05-25-A) — composition-kind parent_id checks
        # removed alongside the field. Containment of category / step /
        # rule / metric / content under their root-service is now
        # expressed via directed edges; not validated at schema level.
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
        # v0.27.16 (D-2026-05-28-K) — loosened from ≥ 2 to ≥ 1.
        # Per D-2026-05-28-J the operator side of a service is the
        # *service itself* (not a separate Admin / System actor),
        # so a single user-side actor_ref is enough. The pre-v0.27.16
        # rule ("≥ 2: operator + user") forced an Admin placeholder
        # on canvases that semantically had no second human actor,
        # which the user flagged as a category error on 2026-05-28.
        # We keep ≥ 1 because every step needs a subject (D-2026-05-28-J);
        # zero actor_refs means there's no one doing the steps.
        if self.canvas_kind != "service_detail":
            return self
        actor_refs = [n for n in self.nodes if n.kind == "actor_ref"]
        if len(actor_refs) < 1:
            raise ValueError(
                f"service_detail {self.canvas_id!r} requires at least 1 "
                f"actor_ref node (the subject of the service's steps), "
                f"got 0. See SPEC.md §Service composition model "
                f"(D-2026-05-28-J)."
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
    # v0.24.13 (D-2026-05-21-B) — project-level semver. Distinct from
    # ``version`` (schema migration counter). Represents the *blueprint
    # release version* — bumped explicitly via the publish endpoint
    # (major/minor/patch), each bump creates a git tag. Default "v0.1.0"
    # for new projects; migration backfills existing projects.
    blueprint_version: str = "v0.1.0"

    @field_validator("id")
    @classmethod
    def _kebab_id(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(f"project id must be alphanumeric with -/_ only, got {v!r}")
        return v
