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

Shape = Literal["rectangle", "rounded", "circle", "ellipse", "diamond", "hexagon"]

# v0.2 node kinds. See PHILOSOPHY.md (P5, P11).
#   core      — single project-identity node (the "true" root). Anchors the
#               two trees (actor-root + service-root) beneath it.
#   actor     — participant in the value economy. May have is_root=True to
#               mark the centre of the actor tree.
#   service   — value-creating hub. May have is_root=True for the service tree.
#   rule      — composition element inside a service (data-only, Inspector).
#   content   — composition element inside a service (data-only, Inspector).
# Sub-service and sub-actor are not new kinds — they're service/actor with
# a non-null parent_id (hierarchy / decomposition).
NodeKind = Literal["core", "actor", "service", "rule", "content"]

# Composition kinds: must live inside a service.
_COMPOSITION_KINDS = {"rule", "content"}


class SketchNode(BaseModel):
    """A freeform node on the canvas."""

    id: str = Field(..., min_length=1)
    label: str = ""
    body: str = ""
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
    is_root: bool = False
    mission: str = ""
    core_values: str = ""
    identity: str = ""


ValueForm = Literal[
    "economic",    # 경제 — 돈, 결제, 수수료
    "attention",   # 주목 — 관심, 트래픽, 도달
    "social",      # 사회 — 이름, 명성, 관계, 신뢰
    "cognitive",   # 인지 — 정보, 데이터, 노하우
    "experience",  # 경험 — 즐거움, 편의, 성취
    "access",      # 접근권 — 기회, 멤버십, 독점성
    "effort",      # 시간·노력 — 투입 시간, 창의 노동
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


class SketchDoc(BaseModel):
    """Full sketch document. One file per sketch under ``.plot/sketches/``."""

    id: str = Field(..., min_length=1)
    name: str = ""
    created: str = ""  # ISO date (YYYY-MM-DD)
    updated: str = ""  # ISO datetime
    version: int = 1
    nodes: list[SketchNode] = Field(default_factory=list)
    edges: list[SketchEdge] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def _kebab_id(cls, v: str) -> str:
        """Sketch ids become filenames — reject anything that could surprise the filesystem."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                f"sketch id must be alphanumeric with -/_ only, got {v!r}"
            )
        return v

    @model_validator(mode="after")
    def _edges_reference_nodes(self) -> SketchDoc:
        node_ids = {n.id for n in self.nodes}
        dangling = [
            e for e in self.edges if e.source not in node_ids or e.target not in node_ids
        ]
        if dangling:
            missing = sorted({e.id for e in dangling})
            raise ValueError(f"edges reference unknown nodes: {missing}")
        if len({e.id for e in self.edges}) != len(self.edges):
            raise ValueError("edge ids must be unique")
        if len({n.id for n in self.nodes}) != len(self.nodes):
            raise ValueError("node ids must be unique")
        return self

    @model_validator(mode="after")
    def _parent_ids_are_valid(self) -> SketchDoc:
        """parent_id must point to an existing node, not be self, and not loop."""
        by_id = {n.id: n for n in self.nodes}
        for n in self.nodes:
            if n.parent_id is None:
                continue
            if n.parent_id == n.id:
                raise ValueError(f"node {n.id!r} cannot be its own parent")
            if n.parent_id not in by_id:
                raise ValueError(
                    f"node {n.id!r}.parent_id points to unknown node {n.parent_id!r}"
                )
        # Cycle check — walk parent chain up to at most len(nodes) steps.
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
    def _at_most_one_root_per_kind(self) -> SketchDoc:
        """v0.2: at most one Core, one Actor-root, and one Service-root per sketch.

        Actor-root and Service-root use ``is_root=True`` with their own
        kinds; Core has ``kind="core"`` (singular by design). Actor-root
        and Service-root may optionally sit under the Core via parent_id.
        """
        # Core is a singleton.
        cores = [n for n in self.nodes if n.kind == "core"]
        if len(cores) > 1:
            raise ValueError(
                f"at most one core node allowed per sketch; found {sorted(n.id for n in cores)}"
            )

        # Actor-/Service-root markers are per-kind singletons.
        roots = [n for n in self.nodes if n.is_root]
        by_kind: dict[str, list[str]] = {}
        for r in roots:
            if r.kind not in ("actor", "service"):
                raise ValueError(
                    f"node {r.id!r} is_root=True but kind is {r.kind!r} "
                    "(only actor or service may be is_root)"
                )
            by_kind.setdefault(r.kind, []).append(r.id)
        for kind, ids in by_kind.items():
            if len(ids) > 1:
                raise ValueError(
                    f"at most one {kind}-root allowed per sketch; found {sorted(ids)}"
                )
        return self

    @model_validator(mode="after")
    def _composition_kinds_live_in_service(self) -> SketchDoc:
        """Rule and Content must be nested inside a Service."""
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
            if parent is None:
                # Already caught by parent-id validator, but defensively skip here.
                continue
            if parent.kind != "service":
                raise ValueError(
                    f"node {n.id!r} of kind {n.kind!r} must be a child of a service, "
                    f"but parent {n.parent_id!r} has kind {parent.kind!r}"
                )
        return self


class SketchSummary(BaseModel):
    """Lightweight sketch metadata for the list endpoint."""

    id: str
    name: str
    updated: str
    node_count: int
    edge_count: int
