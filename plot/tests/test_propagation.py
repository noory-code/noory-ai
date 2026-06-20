"""v0.20.0 Phase 4 (D-2026-05-17-C) — ancestor-walk tests.
v0.26.0 (D-2026-05-25-A) — rewritten to express hierarchy via directed
edges instead of the (now-removed) ``parent_id`` field.

Covers ``plot_mcp.propagation.walk_ancestors`` + ``LogicalAncestor``.
The walk follows incoming directed edges strictly (refs and
undirected edges are ignored). When a node id appears in multiple
canvases (e.g. ServiceDetail root service mirrors Services master
service), the walk treats them as the same logical node and crosses
the canvas boundary via id-matching only — ``service_ref``,
``actor_ref``, and the ``*_ref`` kinds are *not* walked.
"""

from __future__ import annotations

import pytest

from plot_mcp.models import (
    ActorNode,
    ActorRefNode,
    CanvasDoc,
    CategoryNode,
    FeatureNode,
    IdentityNode,
    MissionNode,
    ServiceNode,
    SketchEdge,
    StepNode,
)
from plot_mcp.propagation import LogicalAncestor, walk_ancestors


def _edge(source: str, target: str, relation: str = "flow") -> SketchEdge:
    """Helper: build a directed edge with a stable id."""
    return SketchEdge(
        id=f"e_{source}_{target}",
        source=source,
        target=target,
        directed=True,
        relation=relation,  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# Top-level peer (Foundation) — no ancestors
# ---------------------------------------------------------------------------


def test_walk_ancestors_returns_empty_for_foundation_top_level_peer() -> None:
    """Mission / core_value / identity sit at the top level of Foundation;
    they have no parent and no mirror in another canvas. Publishing a
    mission therefore propagates to nothing."""
    foundation = CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[
            MissionNode(id="m1", label="Mission"),
            IdentityNode(id="i1", label="Identity"),
        ],
    )
    ancestors = walk_ancestors("m1", {"foundation": foundation})
    assert ancestors == []


def test_walk_ancestors_returns_empty_for_actor() -> None:
    """Actors live at the top level of the Actors canvas with no mirror;
    publishing one propagates to nothing."""
    actors = CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=[
            ActorNode(id="a1", label="Customer", side="user"),
            ActorNode(id="a2", label="Owner", side="operator"),
        ],
    )
    ancestors = walk_ancestors("a1", {"actors": actors})
    assert ancestors == []


# ---------------------------------------------------------------------------
# Same-canvas walk — Services canvas category/service relation
# ---------------------------------------------------------------------------


def test_walk_ancestors_walks_service_to_category_same_canvas() -> None:
    services = CanvasDoc(
        canvas_id="services",
        canvas_kind="services",
        nodes=[
            CategoryNode(id="cat-1", label="Customer Acquisition"),
            ServiceNode(id="svc-1", label="Onboarding"),
        ],
        edges=[_edge("cat-1", "svc-1")],
    )
    ancestors = walk_ancestors("svc-1", {"services": services})
    assert ancestors == [LogicalAncestor(node_id="cat-1", canvas_keys=("services",))]


# ---------------------------------------------------------------------------
# Cross-canvas walk — ServiceDetail step → root service mirror → master → category
# ---------------------------------------------------------------------------


def test_walk_ancestors_crosses_to_services_via_root_feature_mirror() -> None:
    """A step in a service_detail canvas has an incoming directed edge
    from the root feature (D-2026-06-17-D — the detail canvas drills into
    a feature, not a service). The root feature node (in service_detail)
    has no incoming edge, but the mirror feature node (same id, in the
    Services canvas) has an incoming edge from the category. The walk
    crosses via id-matching only — ``service_ref`` is never read."""
    services = CanvasDoc(
        canvas_id="services",
        canvas_kind="services",
        nodes=[
            CategoryNode(id="cat-1", label="Customer Acquisition"),
            FeatureNode(id="svc-onboarding", label="Onboarding"),
        ],
        edges=[_edge("cat-1", "svc-onboarding")],
    )
    detail = CanvasDoc(
        canvas_id="svc-onboarding",
        canvas_kind="service_detail",
        service_ref="svc-onboarding",
        nodes=[
            # Root feature mirror.
            FeatureNode(id="svc-onboarding", label="Onboarding"),
            # Step is the leaf being published.
            StepNode(id="step-1", label="Verify email"),
            # Two actor_refs satisfy the service-minimum-baseline validator.
            ActorRefNode(
                id="aref-user",
                ref_actor_id="actor-user",
                side="user",
            ),
            ActorRefNode(
                id="aref-op",
                ref_actor_id="actor-op",
                side="operator",
            ),
        ],
        edges=[
            _edge("svc-onboarding", "step-1"),
            _edge("svc-onboarding", "aref-user"),
            _edge("svc-onboarding", "aref-op"),
        ],
    )
    canvases = {"services": services, "service_detail:svc-onboarding": detail}

    ancestors = walk_ancestors("step-1", canvases)

    # Two logical ancestors: root feature (mirrored in 2 canvases) + category (1 canvas).
    assert len(ancestors) == 2
    # The root feature appears in BOTH the service_detail canvas and Services.
    assert ancestors[0].node_id == "svc-onboarding"
    assert set(ancestors[0].canvas_keys) == {"services", "service_detail:svc-onboarding"}
    # The category appears in Services only.
    assert ancestors[1] == LogicalAncestor(node_id="cat-1", canvas_keys=("services",))


def test_walk_ancestors_from_feature_in_services_canvas_propagates_to_category() -> None:
    """Publishing the drill-target feature from the Services canvas (not a
    step) should still propagate to the category. The starting node has
    presences in both Services and the ServiceDetail mirror; the walk
    picks any incoming directed edge across all presences."""
    services = CanvasDoc(
        canvas_id="services",
        canvas_kind="services",
        nodes=[
            CategoryNode(id="cat-1", label="Customer Acquisition"),
            FeatureNode(id="svc-onboarding", label="Onboarding"),
        ],
        edges=[_edge("cat-1", "svc-onboarding")],
    )
    detail = CanvasDoc(
        canvas_id="svc-onboarding",
        canvas_kind="service_detail",
        service_ref="svc-onboarding",
        nodes=[
            FeatureNode(id="svc-onboarding", label="Onboarding"),
            ActorRefNode(
                id="aref-user",
                ref_actor_id="actor-user",
                side="user",
            ),
            ActorRefNode(
                id="aref-op",
                ref_actor_id="actor-op",
                side="operator",
            ),
        ],
        edges=[
            _edge("svc-onboarding", "aref-user"),
            _edge("svc-onboarding", "aref-op"),
        ],
    )
    canvases = {"services": services, "service_detail:svc-onboarding": detail}

    ancestors = walk_ancestors("svc-onboarding", canvases)

    assert ancestors == [LogicalAncestor(node_id="cat-1", canvas_keys=("services",))]


# ---------------------------------------------------------------------------
# Refs are NOT walked
# ---------------------------------------------------------------------------


def test_walk_ancestors_ignores_actor_ref_pointer() -> None:
    """An ``actor_ref`` node has ``ref_actor_id`` pointing at an Actor in
    another canvas. The walk MUST NOT follow that pointer. It only
    follows incoming directed edges (same canvas) and id-matching
    mirrors."""
    actors = CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=[
            ActorNode(id="actor-customer", label="Customer", side="user"),
            ActorNode(id="actor-owner", label="Owner", side="operator"),
        ],
    )
    services = CanvasDoc(
        canvas_id="services",
        canvas_kind="services",
        nodes=[
            CategoryNode(id="cat-1", label="C"),
            FeatureNode(id="svc-1", label="Onboarding"),
        ],
        edges=[_edge("cat-1", "svc-1")],
    )
    detail = CanvasDoc(
        canvas_id="svc-1",
        canvas_kind="service_detail",
        service_ref="svc-1",
        nodes=[
            FeatureNode(id="svc-1", label="Onboarding"),
            ActorRefNode(
                id="aref-1",
                ref_actor_id="actor-customer",
                side="user",
            ),
            ActorRefNode(
                id="aref-2",
                ref_actor_id="actor-owner",
                side="operator",
            ),
        ],
        edges=[
            _edge("svc-1", "aref-1"),
            _edge("svc-1", "aref-2"),
        ],
    )
    canvases = {
        "actors": actors,
        "services": services,
        "service_detail:svc-1": detail,
    }

    ancestors = walk_ancestors("aref-1", canvases)

    # Walk: aref-1 → svc-1 (directed edge) → cat-1 (directed edge via Services mirror) → null.
    # The Actor "actor-customer" is referenced but NOT walked.
    ancestor_ids = [a.node_id for a in ancestors]
    assert "actor-customer" not in ancestor_ids
    assert ancestor_ids == ["svc-1", "cat-1"]


# ---------------------------------------------------------------------------
# Defensive — orphan source and cycles
# ---------------------------------------------------------------------------


def test_walk_ancestors_unknown_start_returns_empty() -> None:
    """Defensive: if the start id doesn't appear in any canvas, return
    empty rather than raising."""
    foundation = CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[MissionNode(id="m1"), IdentityNode(id="i1")],
    )
    assert walk_ancestors("no-such-node", {"foundation": foundation}) == []


def test_walk_ancestors_breaks_cycles_defensively() -> None:
    """The walk uses a ``visited`` set so a directed-edge cycle in the
    graph terminates rather than looping forever. We can construct a
    cyclic CanvasDoc here (no parent_id cycle validator anymore in
    v0.26), so unlike pre-v0.26 we exercise the visited-set guard
    directly rather than skipping."""
    canvas = CanvasDoc(
        canvas_id="services",
        canvas_kind="services",
        nodes=[
            CategoryNode(id="cat-1", label="A"),
            CategoryNode(id="cat-2", label="B"),
        ],
        edges=[_edge("cat-1", "cat-2"), _edge("cat-2", "cat-1")],
    )
    ancestors = walk_ancestors("cat-1", {"services": canvas})
    # The chain visits cat-2 once then stops (cat-1 already visited).
    assert [a.node_id for a in ancestors] == ["cat-2"]


def test_walk_ancestors_picks_deterministic_parent_with_multi_in() -> None:
    """If a node has multiple incoming directed edges (multi-parent),
    the walk picks the lexicographically smallest source id. The
    v0.26 migration always produces a single incoming edge per node;
    multi-parent only arises from explicit user-drawn extras."""
    canvas = CanvasDoc(
        canvas_id="services",
        canvas_kind="services",
        nodes=[
            CategoryNode(id="cat-a", label="A"),
            CategoryNode(id="cat-b", label="B"),
            ServiceNode(id="svc", label="Svc"),
        ],
        edges=[_edge("cat-b", "svc"), _edge("cat-a", "svc")],
    )
    ancestors = walk_ancestors("svc", {"services": canvas})
    # ``cat-a`` < ``cat-b`` so the walk picks cat-a.
    assert [a.node_id for a in ancestors] == ["cat-a"]


# Keep pytest import non-orphan for any future skip use.
_ = pytest


# ---------------------------------------------------------------------------
# v0.30.2 (D-2026-05-31-E) — relation-aware walk
# ---------------------------------------------------------------------------


def test_walk_ancestors_inheritance_edge_bumps_superclass() -> None:
    """An inheritance edge points subclass→superclass (source=subclass,
    target=superclass). Publishing the subclass must walk UP to the
    superclass (the fold parent is the edge target, inverted)."""
    actors = CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=[
            ActorNode(id="sub", label="Hero", side="user"),
            ActorNode(id="sup", label="User", side="user"),
        ],
        edges=[_edge("sub", "sup", relation="inheritance")],
    )
    assert walk_ancestors("sub", {"actors": actors}) == [
        LogicalAncestor(node_id="sup", canvas_keys=("actors",))
    ]
    # Publishing the superclass walks nothing (it has no fold parent).
    assert walk_ancestors("sup", {"actors": actors}) == []


def test_walk_ancestors_injection_edge_never_walked() -> None:
    """Injection edges are an essence overlay, not containment — they
    never participate in the publish-propagation walk (either direction)."""
    foundation = CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[
            MissionNode(id="m1", label="Mission"),
            IdentityNode(id="id1", label="Voice"),
        ],
        edges=[_edge("m1", "id1", relation="injection")],
    )
    assert walk_ancestors("m1", {"foundation": foundation}) == []
    assert walk_ancestors("id1", {"foundation": foundation}) == []
