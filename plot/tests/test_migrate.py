"""v0.1 → v0.2 migration — single-file ``{id}.json`` → folder layout."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from plot_mcp.folder_io import list_service_details, read_canvas, read_project
from plot_mcp.migrate import migrate_v01_to_v02
from plot_mcp.sketches import create_sketch, read_sketch, write_sketch
from plot_mcp.workspace import resolve_plot_root


@pytest.fixture
def plot_root(tmp_path: Path) -> Path:
    return resolve_plot_root(str(tmp_path))


# ---------------------------------------------------------------------------
# bare v0.1 seed (Core + Actor-root + Service-root only)
# ---------------------------------------------------------------------------


def test_migrates_bare_v01_sketch(plot_root: Path) -> None:
    create_sketch(plot_root, "alpha", "Alpha")
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
    create_sketch(plot_root, "alpha", "Alpha")
    migrate_v01_to_v02(plot_root)
    core = read_canvas(plot_root, "alpha", "core")
    kinds = sorted({n.kind for n in core.nodes if n.kind is not None})
    assert "core" in kinds and "mission" in kinds and "identity" in kinds


def test_migrated_actors_canvas_starts_empty_or_has_root(plot_root: Path) -> None:
    """Bare v0.1 only seeds actor-root (is_root=True). It should land in actors.json."""
    create_sketch(plot_root, "alpha", "Alpha")
    migrate_v01_to_v02(plot_root)
    actors = read_canvas(plot_root, "alpha", "actors")
    # actor-root moves to actors.json as a top-level actor (parent_id cleared)
    assert all(n.kind == "actor" for n in actors.nodes)
    assert all(n.parent_id is None for n in actors.nodes)


def test_migrated_services_overview_has_no_nested(plot_root: Path) -> None:
    create_sketch(plot_root, "alpha", "Alpha")
    migrate_v01_to_v02(plot_root)
    overview = read_canvas(plot_root, "alpha", "services_overview")
    assert all(n.parent_id is None for n in overview.nodes)
    # Bare v0.1 seed has service-root only; it becomes a top-level service.


def test_migration_is_idempotent(plot_root: Path) -> None:
    create_sketch(plot_root, "alpha", "Alpha")
    migrate_v01_to_v02(plot_root)
    # second pass — nothing to do (already migrated)
    assert migrate_v01_to_v02(plot_root) == []


# ---------------------------------------------------------------------------
# richer v0.1 — mission/core-values/identity text on core-root
# ---------------------------------------------------------------------------


def test_identity_fields_promoted_to_nodes(plot_root: Path) -> None:
    doc = create_sketch(plot_root, "alpha", "Alpha")
    # write identity text into the core-root node
    core_node = next(n for n in doc.nodes if n.id == "core-root")
    updated = doc.model_copy(
        update={
            "nodes": [
                n.model_copy(
                    update={
                        "mission": "Deliver value",
                        "core_values": "Speed\nClarity",
                        "identity": "Tone: warm",
                    }
                )
                if n.id == core_node.id
                else n
                for n in doc.nodes
            ],
            "updated": datetime.now(UTC).isoformat(),
        }
    )
    write_sketch(plot_root, updated)

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
    doc = create_sketch(plot_root, "alpha", "Alpha")
    from plot_mcp.models import SketchEdge, SketchNode

    with_services = doc.model_copy(
        update={
            "nodes": [
                *doc.nodes,
                SketchNode(
                    id="order",
                    kind="service",
                    label="주문",
                    parent_id="service-root",
                ),
                SketchNode(
                    id="order-cart",
                    kind="service",
                    label="장바구니",
                    parent_id="order",
                ),
                SketchNode(
                    id="pay",
                    kind="service",
                    label="결제",
                    parent_id="service-root",
                ),
            ],
            "edges": [
                *doc.edges,
                SketchEdge(
                    id="e-order-cart",
                    source="order",
                    target="order-cart",
                    label="decomposes",
                    action_verb="decomposes",
                ),
            ],
            "updated": datetime.now(UTC).isoformat(),
        }
    )
    write_sketch(plot_root, with_services)

    migrate_v01_to_v02(plot_root)
    # Overview: two top-level services — order, pay — plus service-root?
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
    create_sketch(plot_root, "ok", "OK")
    (plot_root / "sketches" / "broken.json").write_text("not json", encoding="utf-8")
    migrated = migrate_v01_to_v02(plot_root)
    assert migrated == ["ok"]
    # Broken file is left alone
    assert (plot_root / "sketches" / "broken.json").exists()


def test_migrated_project_still_loadable_by_read_sketch_backup(plot_root: Path) -> None:
    """The ``.v01.bak`` file is still valid JSON so humans can inspect it."""
    create_sketch(plot_root, "alpha", "Alpha")
    migrate_v01_to_v02(plot_root)
    raw = json.loads((plot_root / "sketches" / "alpha.json.v01.bak").read_text(encoding="utf-8"))
    assert raw["id"] == "alpha"
    # Loading the old doc via read_sketch now fails because the file moved;
    # we don't expect it to work — just that the backup is inspectable.
    with pytest.raises(FileNotFoundError):
        read_sketch(plot_root, "alpha")
