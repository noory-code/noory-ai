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
    """Minimal valid core-canvas content: project anchor + 1 mission + 1 identity."""
    return [
        SketchNode(id="project", kind="project", label="Project", shape="circle"),
        SketchNode(id="mission", kind="mission", label="M"),
        SketchNode(id="identity", kind="identity", label="Voice"),
    ]


def test_core_canvas_minimum_seed_ok() -> None:
    CanvasDoc(canvas_id="foundation", canvas_kind="foundation", nodes=_core_seed_nodes())


def test_core_canvas_multiple_core_values_ok() -> None:
    CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[
            *_core_seed_nodes(),
            SketchNode(id="cv1", kind="core_value", label="빠름"),
            SketchNode(id="cv2", kind="core_value", label="정확함"),
        ],
    )


def test_core_canvas_multiple_missions_ok() -> None:
    """v0.5: Mission is 1..N (was exactly 1)."""
    CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[
            *_core_seed_nodes(),
            SketchNode(id="m2", kind="mission", label="M2"),
            SketchNode(id="m3", kind="mission", label="M3"),
        ],
    )


def test_core_canvas_multiple_identities_ok() -> None:
    """v0.5: Identity is 1..N peers (was exactly 1 + facet children)."""
    CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[
            *_core_seed_nodes(),
            SketchNode(id="energy", kind="identity", label="Energy"),
            SketchNode(id="speech", kind="identity", label="Speech style"),
        ],
    )


def test_core_canvas_missing_mission_rejected() -> None:
    with pytest.raises(ValueError, match="mission"):
        CanvasDoc(
            canvas_id="foundation",
            canvas_kind="foundation",
            nodes=[
                SketchNode(id="project", kind="project", label="Project", shape="circle"),
                SketchNode(id="identity", kind="identity", label="I"),
            ],
        )


def test_core_canvas_missing_identity_rejected() -> None:
    with pytest.raises(ValueError, match="identity"):
        CanvasDoc(
            canvas_id="foundation",
            canvas_kind="foundation",
            nodes=[
                SketchNode(id="project", kind="project", label="Project", shape="circle"),
                SketchNode(id="mission", kind="mission", label="M"),
            ],
        )


def test_core_canvas_missing_project_rejected() -> None:
    with pytest.raises(ValueError, match="project"):
        CanvasDoc(
            canvas_id="foundation",
            canvas_kind="foundation",
            nodes=[
                SketchNode(id="mission", kind="mission", label="M"),
                SketchNode(id="identity", kind="identity", label="I"),
            ],
        )


def test_core_canvas_two_projects_rejected() -> None:
    with pytest.raises(ValueError, match="exactly one project"):
        CanvasDoc(
            canvas_id="foundation",
            canvas_kind="foundation",
            nodes=[
                *_core_seed_nodes(),
                SketchNode(id="p2", kind="project", label="P2", shape="circle"),
            ],
        )


def test_core_canvas_nested_project_rejected() -> None:
    """Project anchor must be top-level."""
    with pytest.raises(ValueError, match="top-level"):
        CanvasDoc(
            canvas_id="foundation",
            canvas_kind="foundation",
            nodes=[
                SketchNode(id="mission", kind="mission", label="M"),
                SketchNode(id="identity", kind="identity", label="I"),
                SketchNode(
                    id="project",
                    kind="project",
                    label="P",
                    shape="circle",
                    parent_id="mission",
                ),
            ],
        )


def test_mission_node_carries_typed_fields() -> None:
    """v0.10: mission nodes have ``what_we_do`` / ``why`` / ``direction``
    typed fields stored directly on the node — Plot is the sole editor
    so they go straight into canvas.json, not into details.md."""
    n = SketchNode(
        id="mission-1",
        kind="mission",
        label="Mission",
        what_we_do="우리는 매일 서로의 팬이 되는 커뮤니티를 운영한다",
        why="사람들이 서로 빛나게 하고 싶어서",
        direction="누구나 히어로인 일상으로",
    )
    assert n.what_we_do.startswith("우리는 매일")
    assert "히어로" in n.direction


def test_typed_fields_default_to_empty() -> None:
    """A non-mission node still validates — typed fields default to empty
    strings, so any kind can carry any subset."""
    n = SketchNode(id="x", kind="actor", label="User")
    assert n.what_we_do == ""
    assert n.why == ""
    assert n.direction == ""


def test_node_details_path_absolute_rejected() -> None:
    with pytest.raises(ValueError, match="relative"):
        SketchNode(id="n1", kind="mission", label="M", details_path="/etc/passwd")


def test_node_details_path_traversal_rejected() -> None:
    with pytest.raises(ValueError, match=r"\.\."):
        SketchNode(
            id="n1", kind="mission", label="M", details_path="workspace/../etc"
        )


def test_node_details_path_blank_rejected() -> None:
    with pytest.raises(ValueError, match="blank"):
        SketchNode(id="n1", kind="mission", label="M", details_path="   ")


def test_node_details_path_valid() -> None:
    n = SketchNode(
        id="n1", kind="mission", label="M",
        details_path="workspace/core/mission-mission",
    )
    assert n.details_path == "workspace/core/mission-mission"


def test_core_canvas_actor_kind_rejected() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="foundation",
            canvas_kind="foundation",
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
# services canvas
# ---------------------------------------------------------------------------


def test_overview_top_level_services_ok() -> None:
    CanvasDoc(
        canvas_id="services",
        canvas_kind="services",
        nodes=[
            SketchNode(id="order", kind="service", label="주문"),
            SketchNode(id="pay", kind="service", label="결제"),
        ],
    )


def test_overview_nested_service_rejected() -> None:
    """Overview forbids decomposition — that's what Detail canvases are for."""
    with pytest.raises(ValueError, match="nested"):
        CanvasDoc(
            canvas_id="services",
            canvas_kind="services",
            nodes=[
                SketchNode(id="order", kind="service", label="주문"),
                SketchNode(id="order-sub", kind="service", parent_id="order", label="Sub"),
            ],
        )


def test_overview_actor_rejected() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        CanvasDoc(
            canvas_id="services",
            canvas_kind="services",
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
