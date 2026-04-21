"""CanvasDoc + per-canvas-kind validators for Plot v0.2 multi-canvas split.

Each canvas enforces its own allowed ``NodeKind`` set and structural rules.
See the ``Target Data Model`` section of the v0.2 plan.
"""

from __future__ import annotations

import pytest

from plot_mcp.models import CanvasDoc, SketchEdge, SketchNode

# ---------------------------------------------------------------------------
# core canvas
# ---------------------------------------------------------------------------


def _core_seed_nodes() -> list[SketchNode]:
    """Minimal valid core-canvas content: root + mission + identity."""
    return [
        SketchNode(id="core-root", kind="core", label="Project"),
        SketchNode(id="mission", kind="mission", parent_id="core-root", label="M"),
        SketchNode(id="identity", kind="identity", parent_id="core-root", label="I"),
    ]


def test_core_canvas_minimum_seed_ok() -> None:
    CanvasDoc(canvas_id="core", canvas_kind="core", nodes=_core_seed_nodes())


def test_core_canvas_multiple_core_values_ok() -> None:
    CanvasDoc(
        canvas_id="core",
        canvas_kind="core",
        nodes=[
            *_core_seed_nodes(),
            SketchNode(id="cv1", kind="core_value", parent_id="core-root", label="빠름"),
            SketchNode(id="cv2", kind="core_value", parent_id="core-root", label="정확함"),
        ],
    )


def test_core_canvas_identity_facets_ok() -> None:
    CanvasDoc(
        canvas_id="core",
        canvas_kind="core",
        nodes=[
            *_core_seed_nodes(),
            SketchNode(id="tone", kind="identity_facet", parent_id="identity", label="Tone"),
            SketchNode(id="voice", kind="identity_facet", parent_id="identity", label="Voice"),
        ],
    )


def test_core_canvas_missing_mission_rejected() -> None:
    with pytest.raises(ValueError, match="mission"):
        CanvasDoc(
            canvas_id="core",
            canvas_kind="core",
            nodes=[
                SketchNode(id="core-root", kind="core", label="Project"),
                SketchNode(id="identity", kind="identity", parent_id="core-root", label="I"),
            ],
        )


def test_core_canvas_missing_identity_rejected() -> None:
    with pytest.raises(ValueError, match="identity"):
        CanvasDoc(
            canvas_id="core",
            canvas_kind="core",
            nodes=[
                SketchNode(id="core-root", kind="core", label="Project"),
                SketchNode(id="mission", kind="mission", parent_id="core-root", label="M"),
            ],
        )


def test_core_canvas_two_missions_rejected() -> None:
    with pytest.raises(ValueError, match="exactly one mission"):
        CanvasDoc(
            canvas_id="core",
            canvas_kind="core",
            nodes=[
                *_core_seed_nodes(),
                SketchNode(id="m2", kind="mission", parent_id="core-root", label="M2"),
            ],
        )


def test_core_canvas_two_identities_rejected() -> None:
    with pytest.raises(ValueError, match="exactly one identity"):
        CanvasDoc(
            canvas_id="core",
            canvas_kind="core",
            nodes=[
                *_core_seed_nodes(),
                SketchNode(id="i2", kind="identity", parent_id="core-root", label="I2"),
            ],
        )


def test_core_canvas_identity_facet_outside_identity_rejected() -> None:
    with pytest.raises(ValueError, match="identity_facet"):
        CanvasDoc(
            canvas_id="core",
            canvas_kind="core",
            nodes=[
                *_core_seed_nodes(),
                SketchNode(id="tone", kind="identity_facet", parent_id="core-root", label="T"),
            ],
        )


def test_core_canvas_actor_kind_rejected() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="core",
            canvas_kind="core",
            nodes=[
                *_core_seed_nodes(),
                SketchNode(id="a1", kind="actor", label="Stray"),
            ],
        )


# ---------------------------------------------------------------------------
# actors canvas
# ---------------------------------------------------------------------------


def test_actors_canvas_single_actor_ok() -> None:
    CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=[SketchNode(id="user", kind="actor", label="사용자")],
    )


def test_actors_canvas_sub_actor_via_parent_id_ok() -> None:
    CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=[
            SketchNode(id="team", kind="actor", label="Team"),
            SketchNode(id="member", kind="actor", parent_id="team", label="Member"),
        ],
    )


def test_actors_canvas_service_rejected() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[
                SketchNode(id="s1", kind="service", label="Stray service"),
            ],
        )


def test_actors_canvas_actor_ref_rejected() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[
                SketchNode(id="r1", kind="actor_ref", ref_actor_id="user", label="ref"),
            ],
        )


# ---------------------------------------------------------------------------
# services_overview canvas
# ---------------------------------------------------------------------------


def test_overview_top_level_services_ok() -> None:
    CanvasDoc(
        canvas_id="services_overview",
        canvas_kind="services_overview",
        nodes=[
            SketchNode(id="order", kind="service", label="주문"),
            SketchNode(id="pay", kind="service", label="결제"),
        ],
    )


def test_overview_nested_service_rejected() -> None:
    """Overview forbids decomposition — that's what Detail canvases are for."""
    with pytest.raises(ValueError, match="nested"):
        CanvasDoc(
            canvas_id="services_overview",
            canvas_kind="services_overview",
            nodes=[
                SketchNode(id="order", kind="service", label="주문"),
                SketchNode(id="order-sub", kind="service", parent_id="order", label="Sub"),
            ],
        )


def test_overview_actor_rejected() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="services_overview",
            canvas_kind="services_overview",
            nodes=[SketchNode(id="a1", kind="actor", label="Stray")],
        )


# ---------------------------------------------------------------------------
# service_detail canvas
# ---------------------------------------------------------------------------


def _detail_seed(canvas_id: str = "order") -> list[SketchNode]:
    return [SketchNode(id=canvas_id, kind="service", label="주문")]


def test_detail_canvas_minimum_ok() -> None:
    CanvasDoc(
        canvas_id="order",
        canvas_kind="service_detail",
        service_ref="order",
        nodes=_detail_seed(),
    )


def test_detail_canvas_service_ref_must_match_canvas_id() -> None:
    with pytest.raises(ValueError, match="service_ref"):
        CanvasDoc(
            canvas_id="order",
            canvas_kind="service_detail",
            service_ref="pay",  # mismatch
            nodes=_detail_seed(),
        )


def test_detail_canvas_service_ref_required() -> None:
    with pytest.raises(ValueError, match="service_ref"):
        CanvasDoc(
            canvas_id="order",
            canvas_kind="service_detail",
            nodes=_detail_seed(),
        )


def test_detail_canvas_sub_services_rules_contents_ok() -> None:
    CanvasDoc(
        canvas_id="order",
        canvas_kind="service_detail",
        service_ref="order",
        nodes=[
            *_detail_seed(),
            SketchNode(id="sub1", kind="service", parent_id="order", label="장바구니"),
            SketchNode(id="r1", kind="rule", parent_id="order", label="가격 규칙"),
            SketchNode(id="c1", kind="content", parent_id="order", label="썸네일"),
        ],
    )


def test_detail_canvas_actor_ref_ok() -> None:
    CanvasDoc(
        canvas_id="order",
        canvas_kind="service_detail",
        service_ref="order",
        nodes=[
            *_detail_seed(),
            SketchNode(
                id="ref-user",
                kind="actor_ref",
                ref_actor_id="user",  # references actor in actors canvas
                label="사용자",
            ),
        ],
    )


def test_detail_canvas_actor_ref_without_ref_id_rejected() -> None:
    with pytest.raises(ValueError, match="ref_actor_id"):
        CanvasDoc(
            canvas_id="order",
            canvas_kind="service_detail",
            service_ref="order",
            nodes=[
                *_detail_seed(),
                SketchNode(id="bad-ref", kind="actor_ref", label="Orphan"),
            ],
        )


def test_detail_canvas_actor_kind_rejected() -> None:
    """Raw actors belong in the Actor canvas, not Detail."""
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="order",
            canvas_kind="service_detail",
            service_ref="order",
            nodes=[
                *_detail_seed(),
                SketchNode(id="a1", kind="actor", label="Raw actor"),
            ],
        )


def test_detail_canvas_missing_root_service_rejected() -> None:
    with pytest.raises(ValueError, match="root service"):
        CanvasDoc(
            canvas_id="order",
            canvas_kind="service_detail",
            service_ref="order",
            nodes=[],
        )


# ---------------------------------------------------------------------------
# shared validators (edges + parent_id) still apply
# ---------------------------------------------------------------------------


def test_edges_referencing_unknown_nodes_rejected() -> None:
    with pytest.raises(ValueError, match="unknown nodes"):
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[SketchNode(id="user", kind="actor", label="U")],
            edges=[SketchEdge(id="e1", source="user", target="ghost")],
        )


def test_parent_cycle_rejected() -> None:
    with pytest.raises(ValueError, match="cycle"):
        CanvasDoc(
            canvas_id="actors",
            canvas_kind="actors",
            nodes=[
                SketchNode(id="a", kind="actor", parent_id="b", label="A"),
                SketchNode(id="b", kind="actor", parent_id="a", label="B"),
            ],
        )
