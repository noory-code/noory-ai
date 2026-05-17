"""v0.22.0 (D-2026-05-17-H) — publish dirty tracking unit tests.

Covers the pure helpers in ``folder_io.py``:
- ``_dirty_snapshot`` excludes visual + structural fields, includes
  content + incident edges.
- ``is_node_dirty`` returns True on baseline None (initial publish),
  False on matching snapshot, True after content edits.
- End-to-end: ``publish_node`` stamps the baseline on target + mirrors;
  Phase 4 MINOR drift on ancestors does NOT touch their baselines.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from plot_mcp.folder_io import (
    _dirty_snapshot,
    _incident_edges,
    create_project,
    is_node_dirty,
    publish_node,
    read_canvas,
    write_canvas,
)
from plot_mcp.models import (
    ActorNode,
    ActorRefNode,
    CanvasDoc,
    CategoryNode,
    IdentityNode,
    ServiceNode,
    SketchEdge,
    StepNode,
)


@pytest.fixture()
def plot_root(tmp_path: Path) -> Path:
    plot = tmp_path / ".plot"
    plot.mkdir()
    return plot


# ---------------------------------------------------------------------------
# _dirty_snapshot
# ---------------------------------------------------------------------------


def test_dirty_snapshot_excludes_visual_fields() -> None:
    n_a = IdentityNode(
        id="id-1",
        label="Voice",
        description="warm and honest",
        do="listen first",
        dont="judge first",
        body="",
        x=10,
        y=20,
        width=200,
        height=80,
        color="#ffcc00",
    )
    n_b = n_a.model_copy(update={"x": 500, "y": 500, "color": "#0000ff", "width": 400})
    assert _dirty_snapshot(n_a, []) == _dirty_snapshot(n_b, [])


def test_dirty_snapshot_excludes_version_and_id_and_parent() -> None:
    n_a = IdentityNode(id="id-1", label="Voice", description="warm")
    n_b = n_a.model_copy(update={"version": "v3.0", "parent_id": "anything"})
    assert _dirty_snapshot(n_a, []) == _dirty_snapshot(n_b, [])


def test_dirty_snapshot_includes_typed_text_change() -> None:
    n_a = IdentityNode(id="id-1", label="Voice", description="warm")
    n_b = n_a.model_copy(update={"description": "cold"})
    assert _dirty_snapshot(n_a, []) != _dirty_snapshot(n_b, [])


def test_dirty_snapshot_includes_label_change() -> None:
    n_a = IdentityNode(id="id-1", label="Voice", description="warm")
    n_b = n_a.model_copy(update={"label": "Tone"})
    assert _dirty_snapshot(n_a, []) != _dirty_snapshot(n_b, [])


def test_dirty_snapshot_includes_body_change() -> None:
    n_a = IdentityNode(id="id-1", label="Voice", description="warm", body="old note")
    n_b = n_a.model_copy(update={"body": "new note"})
    assert _dirty_snapshot(n_a, []) != _dirty_snapshot(n_b, [])


def test_dirty_snapshot_edges_order_independent() -> None:
    n = IdentityNode(id="id-1", label="Voice", description="warm")
    e1 = SketchEdge(id="e1", source="id-1", target="mission")
    e2 = SketchEdge(id="e2", source="id-1", target="core-1")
    snap_a = _dirty_snapshot(n, [e1, e2])
    snap_b = _dirty_snapshot(n, [e2, e1])
    assert snap_a == snap_b


def test_dirty_snapshot_includes_edge_add() -> None:
    n = IdentityNode(id="id-1", label="Voice", description="warm")
    e = SketchEdge(id="e1", source="id-1", target="mission")
    assert _dirty_snapshot(n, []) != _dirty_snapshot(n, [e])


def test_dirty_snapshot_includes_edge_label_edit() -> None:
    n = IdentityNode(id="id-1", label="Voice", description="warm")
    e_a = SketchEdge(id="e1", source="id-1", target="mission", label="")
    e_b = SketchEdge(id="e1", source="id-1", target="mission", label="speaks")
    assert _dirty_snapshot(n, [e_a]) != _dirty_snapshot(n, [e_b])


def test_dirty_snapshot_ignores_edge_id_differences() -> None:
    """Edge ``id`` is ephemeral (server-generated); same content under a
    different id must not flip dirty."""
    n = IdentityNode(id="id-1", label="Voice", description="warm")
    e_a = SketchEdge(id="generated-1", source="id-1", target="mission")
    e_b = SketchEdge(id="generated-2", source="id-1", target="mission")
    assert _dirty_snapshot(n, [e_a]) == _dirty_snapshot(n, [e_b])


# ---------------------------------------------------------------------------
# is_node_dirty
# ---------------------------------------------------------------------------


def test_is_node_dirty_true_when_no_baseline() -> None:
    n = IdentityNode(id="id-1", label="Voice", description="warm")
    assert n.publish_baseline is None
    assert is_node_dirty(n, []) is True


def test_is_node_dirty_false_when_baseline_matches() -> None:
    n = IdentityNode(id="id-1", label="Voice", description="warm")
    snap = _dirty_snapshot(n, [])
    n_with_baseline = n.model_copy(update={"publish_baseline": snap})
    assert is_node_dirty(n_with_baseline, []) is False


def test_is_node_dirty_true_after_typed_text_edit() -> None:
    n = IdentityNode(id="id-1", label="Voice", description="warm")
    snap = _dirty_snapshot(n, [])
    n_edited = n.model_copy(update={"publish_baseline": snap, "description": "cold"})
    assert is_node_dirty(n_edited, []) is True


def test_is_node_dirty_false_after_visual_only_edit() -> None:
    n = IdentityNode(id="id-1", label="Voice", description="warm")
    snap = _dirty_snapshot(n, [])
    n_moved = n.model_copy(update={"publish_baseline": snap, "x": 1000, "color": "#ff0000"})
    assert is_node_dirty(n_moved, []) is False


def test_is_node_dirty_true_after_edge_add() -> None:
    n = IdentityNode(id="id-1", label="Voice", description="warm")
    snap = _dirty_snapshot(n, [])
    n_with_baseline = n.model_copy(update={"publish_baseline": snap})
    e = SketchEdge(id="e1", source="id-1", target="mission")
    assert is_node_dirty(n_with_baseline, [e]) is True


# ---------------------------------------------------------------------------
# _incident_edges
# ---------------------------------------------------------------------------


def test_incident_edges_filters_both_endpoints() -> None:
    edges = [
        SketchEdge(id="e1", source="id-1", target="mission"),
        SketchEdge(id="e2", source="core-1", target="id-1"),
        SketchEdge(id="e3", source="x", target="y"),
    ]
    incident = _incident_edges(edges, "id-1")
    assert {e.id for e in incident} == {"e1", "e2"}


# ---------------------------------------------------------------------------
# publish_node end-to-end
# ---------------------------------------------------------------------------


def _seed_services_with_step(plot_root: Path) -> tuple[str, str, str]:
    # Actors canvas needs both user + operator referents for service_detail's
    # 2-actor_ref requirement.
    actors = read_canvas(plot_root, "alpha", "actors")
    new_actors = actors.model_copy(
        update={
            "nodes": [
                ActorNode(id="user", label="User", is_root=True),
                ActorNode(id="operator", label="Operator", is_root=True),
            ]
        }
    )
    write_canvas(plot_root, "alpha", new_actors)

    services = read_canvas(plot_root, "alpha", "services")
    cat = CategoryNode(id="cat-acq", label="Acquisition")
    svc = ServiceNode(id="svc-onboarding", label="Onboarding", parent_id="cat-acq")
    new_services = services.model_copy(update={"nodes": [cat, svc]})
    write_canvas(plot_root, "alpha", new_services)

    detail = CanvasDoc(
        canvas_id="svc-onboarding",
        canvas_kind="service_detail",
        service_ref="svc-onboarding",
        nodes=[
            ServiceNode(id="svc-onboarding", label="Onboarding"),
            StepNode(
                id="step-verify",
                label="Verify",
                parent_id="svc-onboarding",
                order=1,
            ),
            ActorRefNode(
                id="aref-user",
                parent_id="svc-onboarding",
                ref_actor_id="user",
                side="user",
            ),
            ActorRefNode(
                id="aref-op",
                parent_id="svc-onboarding",
                ref_actor_id="operator",
                side="operator",
            ),
        ],
    )
    write_canvas(plot_root, "alpha", detail)
    return "cat-acq", "svc-onboarding", "step-verify"


def test_publish_node_stamps_baseline_on_target(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    _, sid, _ = _seed_services_with_step(plot_root)

    publish_node(plot_root, "alpha", "services", sid)

    services = read_canvas(plot_root, "alpha", "services")
    svc = next(n for n in services.nodes if n.id == sid)
    assert svc.publish_baseline is not None
    # After publish, the (bumped) svc + its incident edges must hash to
    # the baseline → dirty = False.
    assert is_node_dirty(svc, _incident_edges(services.edges, sid)) is False


def test_publish_node_stamps_baseline_on_mirror(plot_root: Path) -> None:
    """ServiceDetail mirror gets the same baseline so it stays clean too."""
    create_project(plot_root, "alpha", "Alpha")
    _, sid, _ = _seed_services_with_step(plot_root)

    publish_node(plot_root, "alpha", "services", sid)

    detail = read_canvas(plot_root, "alpha", "service_detail", service_id=sid)
    mirror = next(n for n in detail.nodes if n.id == sid)
    assert mirror.publish_baseline is not None


def test_publish_node_ancestor_baseline_unchanged(plot_root: Path) -> None:
    """Phase 4 MINOR propagation must NOT touch the ancestor's
    publish_baseline — typed-text + edges didn't change, only the
    version did."""
    create_project(plot_root, "alpha", "Alpha")
    cat_id, _, step_id = _seed_services_with_step(plot_root)

    # Pre-publish: stamp a baseline on the category by publishing it
    # first, then later publishing the step bumps the category MINOR
    # via Phase 4. The category's baseline must survive.
    publish_node(plot_root, "alpha", "services", cat_id)
    services_after_cat = read_canvas(plot_root, "alpha", "services")
    cat_before = next(n for n in services_after_cat.nodes if n.id == cat_id)
    baseline_before = cat_before.publish_baseline

    # Now publish a descendant; Phase 4 minor-bumps the category.
    publish_node(plot_root, "alpha", "service_detail", step_id, service_id="svc-onboarding")

    services_after = read_canvas(plot_root, "alpha", "services")
    cat_after = next(n for n in services_after.nodes if n.id == cat_id)
    # Version moved (MINOR) but baseline stays put.
    assert cat_after.version != cat_before.version
    assert cat_after.publish_baseline == baseline_before


def test_publish_node_then_edit_marks_dirty(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    _, sid, _ = _seed_services_with_step(plot_root)

    publish_node(plot_root, "alpha", "services", sid)

    # Read post-publish state and verify clean.
    services = read_canvas(plot_root, "alpha", "services")
    svc = next(n for n in services.nodes if n.id == sid)
    assert is_node_dirty(svc, _incident_edges(services.edges, sid)) is False

    # Simulate a typed-text edit (label change) and verify dirty.
    svc_edited = svc.model_copy(update={"label": "Customer Onboarding"})
    assert is_node_dirty(svc_edited, _incident_edges(services.edges, sid)) is True
