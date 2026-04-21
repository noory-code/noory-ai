"""v0.1 → v0.2 migration — single-file ``{id}.json`` → folder layout."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from plot_mcp.folder_io import list_service_details, read_canvas, read_project
from plot_mcp.migrate import migrate_v01_to_v02
from plot_mcp.workspace import resolve_plot_root


@pytest.fixture
def plot_root(tmp_path: Path) -> Path:
    return resolve_plot_root(str(tmp_path))


# ---------------------------------------------------------------------------
# helpers — write a v0.1 sketch JSON without depending on the deleted
# ``plot_mcp.sketches`` module. Keeps the legacy format visible in the
# tests rather than hiding it behind a fixture builder.
# ---------------------------------------------------------------------------


def _v01_node(node_id: str, **overrides: Any) -> dict[str, Any]:
    """Build a v0.1 SketchNode dict, letting callers override any field."""
    base: dict[str, Any] = {
        "id": node_id,
        "label": node_id,
        "body": "",
        "x": 0,
        "y": 0,
        "width": 180,
        "height": 80,
        "color": "#ffffff",
        "shape": "rounded",
        "icon": None,
        "kind": None,
        "parent_id": None,
        "collapsed": False,
        "is_root": False,
        "mission": "",
        "core_values": "",
        "identity": "",
        "ref_actor_id": None,
    }
    base.update(overrides)
    return base


def _v01_seed_nodes() -> list[dict[str, Any]]:
    """The three root nodes v0.1 ``create_sketch`` used to plant."""
    return [
        _v01_node(
            "core-root",
            kind="core",
            label="alpha",
            x=-90,
            y=-70,
            width=180,
            height=140,
            color="#fde68a",
            shape="octagon",
            icon="star",
        ),
        _v01_node(
            "actor-root",
            kind="actor",
            label="Actors",
            is_root=True,
            parent_id="core-root",
            x=-320,
            y=180,
            width=140,
            height=140,
            color="#fecaca",
            shape="circle",
            icon="users",
        ),
        _v01_node(
            "service-root",
            kind="service",
            label="Services",
            is_root=True,
            parent_id="core-root",
            x=180,
            y=180,
            width=200,
            height=120,
            color="#bae6fd",
            shape="rounded",
            icon="zap",
        ),
    ]


def _v01_seed_edges() -> list[dict[str, Any]]:
    return [
        {
            "id": "e-core-actor",
            "source": "core-root",
            "target": "actor-root",
            "sourceHandle": None,
            "targetHandle": None,
            "label": "decomposes",
            "style": "dashed",
            "action_verb": "decomposes",
            "value_form": [],
        },
        {
            "id": "e-core-service",
            "source": "core-root",
            "target": "service-root",
            "sourceHandle": None,
            "targetHandle": None,
            "label": "decomposes",
            "style": "dashed",
            "action_verb": "decomposes",
            "value_form": [],
        },
    ]


def _write_v01_sketch(
    plot_root: Path,
    sketch_id: str,
    name: str,
    *,
    nodes: list[dict[str, Any]] | None = None,
    edges: list[dict[str, Any]] | None = None,
) -> None:
    """Drop a v0.1 ``{id}.json`` onto disk for the migrator to find."""
    doc = {
        "id": sketch_id,
        "name": name,
        "created": "2026-01-01",
        "updated": "2026-01-01T00:00:00+00:00",
        "version": 1,
        "nodes": nodes or _v01_seed_nodes(),
        "edges": edges or _v01_seed_edges(),
    }
    sketches_dir = plot_root / "sketches"
    sketches_dir.mkdir(exist_ok=True)
    (sketches_dir / f"{sketch_id}.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# bare v0.1 seed (Core + Actor-root + Service-root only)
# ---------------------------------------------------------------------------


def test_migrates_bare_v01_sketch(plot_root: Path) -> None:
    _write_v01_sketch(plot_root, "alpha", "Alpha")
    migrated = migrate_v01_to_v02(plot_root)
    assert migrated == ["alpha"]

    # folder exists
    folder = plot_root / "sketches" / "alpha"
    assert folder.is_dir()

    # v0.1 file was backed up, not deleted
    assert (plot_root / "sketches" / "alpha.json.v01.bak").is_file()
    assert not (plot_root / "sketches" / "alpha.json").exists()

    # project metadata
    proj = read_project(plot_root, "alpha")
    assert proj.id == "alpha"
    assert proj.name == "Alpha"
    assert proj.version == 2


def test_migrated_core_canvas_has_seeds(plot_root: Path) -> None:
    """v0.4: migrated Core canvas promotes mission/core_values/identity
    into top-level pillars (no ``core`` anchor)."""
    _write_v01_sketch(plot_root, "alpha", "Alpha")
    migrate_v01_to_v02(plot_root)
    core = read_canvas(plot_root, "alpha", "core")
    kinds = sorted({n.kind for n in core.nodes if n.kind is not None})
    assert "mission" in kinds and "identity" in kinds and "core_value" in kinds
    assert "core" not in kinds


def test_migrated_actors_canvas_starts_empty_or_has_root(plot_root: Path) -> None:
    """Bare v0.1 only seeds actor-root (is_root=True). It should land in actors.json."""
    _write_v01_sketch(plot_root, "alpha", "Alpha")
    migrate_v01_to_v02(plot_root)
    actors = read_canvas(plot_root, "alpha", "actors")
    # actor-root moves to actors.json as a top-level actor (parent_id cleared)
    assert all(n.kind == "actor" for n in actors.nodes)
    assert all(n.parent_id is None for n in actors.nodes)


def test_migrated_services_overview_has_no_nested(plot_root: Path) -> None:
    _write_v01_sketch(plot_root, "alpha", "Alpha")
    migrate_v01_to_v02(plot_root)
    overview = read_canvas(plot_root, "alpha", "services_overview")
    assert all(n.parent_id is None for n in overview.nodes)
    # Bare v0.1 seed has service-root only; it becomes a top-level service.


def test_migration_is_idempotent(plot_root: Path) -> None:
    _write_v01_sketch(plot_root, "alpha", "Alpha")
    migrate_v01_to_v02(plot_root)
    # second pass — nothing to do (already migrated)
    assert migrate_v01_to_v02(plot_root) == []


# ---------------------------------------------------------------------------
# richer v0.1 — mission/core-values/identity text on core-root
# ---------------------------------------------------------------------------


def test_identity_fields_promoted_to_nodes(plot_root: Path) -> None:
    nodes = _v01_seed_nodes()
    # Patch core-root with identity text fields (v0.1 carried them on the node itself).
    for n in nodes:
        if n["id"] == "core-root":
            n["mission"] = "Deliver value"
            n["core_values"] = "Speed\nClarity"
            n["identity"] = "Tone: warm"
    _write_v01_sketch(plot_root, "alpha", "Alpha", nodes=nodes)

    migrate_v01_to_v02(plot_root)
    core = read_canvas(plot_root, "alpha", "core")
    by_kind = {n.kind: n for n in core.nodes}
    assert by_kind["mission"].body == "Deliver value" or by_kind["mission"].label
    # Two core_value nodes from "Speed\nClarity"
    values = [n for n in core.nodes if n.kind == "core_value"]
    labels = {n.label for n in values}
    assert {"Speed", "Clarity"} <= labels
    # Identity text lives on the identity node (label or body)
    assert "warm" in by_kind["identity"].body or "warm" in by_kind["identity"].label


# ---------------------------------------------------------------------------
# populated v0.1 — sub-services under service-root become Details
# ---------------------------------------------------------------------------


def test_top_level_services_get_detail_canvases(plot_root: Path) -> None:
    nodes = _v01_seed_nodes()
    nodes.extend(
        [
            _v01_node(
                "order",
                kind="service",
                label="주문",
                parent_id="service-root",
            ),
            _v01_node(
                "order-cart",
                kind="service",
                label="장바구니",
                parent_id="order",
            ),
            _v01_node(
                "pay",
                kind="service",
                label="결제",
                parent_id="service-root",
            ),
        ]
    )
    edges = _v01_seed_edges()
    edges.append(
        {
            "id": "e-order-cart",
            "source": "order",
            "target": "order-cart",
            "sourceHandle": None,
            "targetHandle": None,
            "label": "decomposes",
            "style": "solid",
            "action_verb": "decomposes",
            "value_form": [],
        }
    )
    _write_v01_sketch(plot_root, "alpha", "Alpha", nodes=nodes, edges=edges)

    migrate_v01_to_v02(plot_root)
    overview = read_canvas(plot_root, "alpha", "services_overview")
    labels = {n.label for n in overview.nodes}
    assert "주문" in labels and "결제" in labels

    # Detail canvases exist for both top-level services
    details = set(list_service_details(plot_root, "alpha"))
    assert {"order", "pay"} <= details

    # Order detail contains its sub-service and the decomposes edge
    order_detail = read_canvas(plot_root, "alpha", "service_detail", service_id="order")
    sub_labels = {n.label for n in order_detail.nodes}
    assert "장바구니" in sub_labels and "주문" in sub_labels
    assert any(e.id == "e-order-cart" for e in order_detail.edges)


# ---------------------------------------------------------------------------
# malformed v0.1 files
# ---------------------------------------------------------------------------


def test_malformed_v01_file_is_skipped(plot_root: Path) -> None:
    _write_v01_sketch(plot_root, "ok", "OK")
    (plot_root / "sketches" / "broken.json").write_text("not json", encoding="utf-8")
    migrated = migrate_v01_to_v02(plot_root)
    assert migrated == ["ok"]
    # Broken file is left alone
    assert (plot_root / "sketches" / "broken.json").exists()


def test_migrated_backup_is_inspectable(plot_root: Path) -> None:
    """The ``.v01.bak`` file is still valid JSON so humans can diff it
    against the new folder layout or roll back by hand."""
    _write_v01_sketch(plot_root, "alpha", "Alpha")
    migrate_v01_to_v02(plot_root)
    raw = json.loads((plot_root / "sketches" / "alpha.json.v01.bak").read_text(encoding="utf-8"))
    assert raw["id"] == "alpha"
    assert raw["version"] == 1
