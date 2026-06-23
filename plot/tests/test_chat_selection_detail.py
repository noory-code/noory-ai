"""Lever 1a — inject the selected node's actual content into the chat context.

The per-turn context used to list only each selected node's kind / label / id
(``docs/idea/chat/00-problem.md``): "polish this mission" reached the agent
*without the mission text*, so it invented one. This renders the selected nodes'
typed text fields (statement / body / definition / …) by reading the canvas
engine-side — the SSOT both delivery layers share — keyed off the single project
under the data root (canonical one-project-per-root layout, D-2026-06-21-AB).
The renderer is generic (dump non-empty text fields, drop structural / visual /
server keys) so a new kind needs no per-kind branch.
"""

from __future__ import annotations

from pathlib import Path

from plot_mcp.chat_selection import (
    render_canvas_map,
    render_cross_canvas_registry,
    render_node_content,
    render_selection_detail,
)
from plot_mcp.folder_io import create_project, write_canvas
from plot_mcp.models import (
    ActorNode,
    CanvasDoc,
    CoreValueNode,
    EntityNode,
    IdentityNode,
    MissionNode,
    SketchNode,
)
from plot_mcp.workspace import resolve_plot_root

# --- pure renderer ---------------------------------------------------------


def test_render_node_content_keeps_typed_text_drops_structural() -> None:
    body = render_node_content(
        {
            "kind": "mission",
            "id": "m1",
            "label": "Our mission",
            "x": 10.0,
            "y": 20.0,
            "color": "#ffffff",
            "version": "v1.0",
            "statement": "Make planning effortless",
            "body": "We believe in clarity.",
        }
    )
    assert "Make planning effortless" in body
    assert "We believe in clarity." in body
    # structural / visual / server fields never leak into the body
    assert "10.0" not in body
    assert "#ffffff" not in body
    assert "v1.0" not in body
    # id + label belong to the header line, not the rendered body
    assert "m1" not in body


def test_render_node_content_empty_when_no_typed_text() -> None:
    assert render_node_content({"kind": "project", "id": "p", "label": "P", "x": 0.0}) == ""


def test_render_node_content_drops_underscore_server_keys() -> None:
    out = render_node_content(
        {"kind": "mission", "id": "m", "label": "L", "_dirty": True, "statement": "S"}
    )
    assert "S" in out
    assert "_dirty" not in out


# --- fs-backed selection detail --------------------------------------------


def _mission_canvas() -> CanvasDoc:
    nodes: list[SketchNode] = [
        MissionNode(
            id="m1",
            label="Our mission",
            statement="Make planning effortless",
            body="We believe in clarity.",
        ),
        # Foundation requires ≥1 identity node alongside the mission.
        IdentityNode(id="i1", label="Identity"),
    ]
    return CanvasDoc(canvas_id="foundation", canvas_kind="foundation", nodes=nodes)


def _setup(tmp_path: Path) -> Path:
    plot_root = resolve_plot_root(str(tmp_path))
    create_project(plot_root, "alpha", "Alpha")
    write_canvas(plot_root, "alpha", _mission_canvas())
    return plot_root


def test_selection_detail_injects_node_body(tmp_path: Path) -> None:
    plot_root = _setup(tmp_path)
    out = render_selection_detail(
        plot_root, "foundation", [{"id": "m1", "kind": "mission", "label": "Our mission"}]
    )
    assert "Make planning effortless" in out
    assert "We believe in clarity." in out
    assert "m1" in out  # header still names the node


def test_selection_detail_empty_for_project_scope(tmp_path: Path) -> None:
    plot_root = _setup(tmp_path)
    out = render_selection_detail(
        plot_root, "project", [{"id": "m1", "kind": "mission", "label": "x"}]
    )
    assert out == ""


def test_selection_detail_graceful_when_node_absent(tmp_path: Path) -> None:
    plot_root = _setup(tmp_path)
    out = render_selection_detail(
        plot_root, "foundation", [{"id": "ghost", "kind": "mission", "label": "x"}]
    )
    assert out == ""


def test_selection_detail_empty_when_no_project(tmp_path: Path) -> None:
    plot_root = resolve_plot_root(str(tmp_path))  # no create_project
    out = render_selection_detail(
        plot_root, "foundation", [{"id": "m1", "kind": "mission", "label": "x"}]
    )
    assert out == ""


# --- active canvas map (Phase 2a) ------------------------------------------


def _two_value_canvas() -> CanvasDoc:
    nodes: list[SketchNode] = [
        MissionNode(id="m1", label="Our mission", statement="Make planning effortless"),
        IdentityNode(id="i1", label="Identity"),
        CoreValueNode(id="v1", label="Clarity", definition="Always favour the clear path"),
        CoreValueNode(id="v2", label="Trust", definition="Default to candour"),
    ]
    return CanvasDoc(canvas_id="foundation", canvas_kind="foundation", nodes=nodes)


def test_canvas_map_lists_every_node(tmp_path: Path) -> None:
    plot_root = resolve_plot_root(str(tmp_path))
    create_project(plot_root, "alpha", "Alpha")
    write_canvas(plot_root, "alpha", _two_value_canvas())
    out = render_canvas_map(plot_root, "foundation", [])
    # all four authored nodes appear by label
    for label in ("Our mission", "Identity", "Clarity", "Trust"):
        assert label in out
    assert "foundation" in out  # canvas named in the header


def test_canvas_map_marks_selected_nodes(tmp_path: Path) -> None:
    plot_root = resolve_plot_root(str(tmp_path))
    create_project(plot_root, "alpha", "Alpha")
    write_canvas(plot_root, "alpha", _two_value_canvas())
    out = render_canvas_map(
        plot_root, "foundation", [{"id": "v1", "kind": "core_value", "label": "Clarity"}]
    )
    # the selected node carries a marker the others don't
    selected_line = next(line for line in out.splitlines() if "Clarity" in line)
    trust_line = next(line for line in out.splitlines() if "Trust" in line)
    assert "selected" in selected_line.lower()
    assert "selected" not in trust_line.lower()


def test_canvas_map_empty_for_project_scope(tmp_path: Path) -> None:
    plot_root = resolve_plot_root(str(tmp_path))
    create_project(plot_root, "alpha", "Alpha")
    write_canvas(plot_root, "alpha", _two_value_canvas())
    assert render_canvas_map(plot_root, "project", []) == ""


def test_canvas_map_empty_when_no_project(tmp_path: Path) -> None:
    plot_root = resolve_plot_root(str(tmp_path))
    assert render_canvas_map(plot_root, "foundation", []) == ""


# --- cross-canvas registry (Phase 2b) --------------------------------------


def _actors_canvas() -> CanvasDoc:
    nodes: list[SketchNode] = [
        ActorNode(id="a1", label="Operator"),
        ActorNode(id="a2", label="Reader"),
    ]
    return CanvasDoc(canvas_id="actors", canvas_kind="actors", nodes=nodes)


def _entities_canvas() -> CanvasDoc:
    nodes: list[SketchNode] = [
        EntityNode(id="e1", label="Post", summary="A published article"),
    ]
    return CanvasDoc(canvas_id="entities", canvas_kind="entities", nodes=nodes)


def _setup_registry(tmp_path: Path) -> Path:
    plot_root = resolve_plot_root(str(tmp_path))
    create_project(plot_root, "alpha", "Alpha")
    write_canvas(plot_root, "alpha", _actors_canvas())
    write_canvas(plot_root, "alpha", _entities_canvas())
    return plot_root


def test_registry_lists_actors_and_entities_on_feature_scope(tmp_path: Path) -> None:
    plot_root = _setup_registry(tmp_path)
    out = render_cross_canvas_registry(plot_root, "feature:svc1")
    assert "Operator" in out and "Reader" in out
    assert "Post" in out and "A published article" in out


def test_registry_lists_actors_on_services_scope(tmp_path: Path) -> None:
    plot_root = _setup_registry(tmp_path)
    out = render_cross_canvas_registry(plot_root, "services")
    assert "Operator" in out


def test_registry_empty_on_foundation_scope(tmp_path: Path) -> None:
    plot_root = _setup_registry(tmp_path)
    # foundation is about essence — it doesn't reference actors/entities.
    assert render_cross_canvas_registry(plot_root, "foundation") == ""


def test_registry_empty_when_no_project(tmp_path: Path) -> None:
    plot_root = resolve_plot_root(str(tmp_path))
    assert render_cross_canvas_registry(plot_root, "feature:x") == ""
