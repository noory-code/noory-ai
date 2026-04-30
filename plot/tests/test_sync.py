"""Overview ↔ Detail auto-sync."""

from __future__ import annotations

from pathlib import Path

import pytest

from plot_mcp.folder_io import (
    create_project,
    list_service_details,
    read_canvas,
    sync_details_with_overview,
    write_canvas,
)
from plot_mcp.models import CanvasDoc, SketchNode
from plot_mcp.workspace import resolve_plot_root


@pytest.fixture
def plot_root(tmp_path: Path) -> Path:
    return resolve_plot_root(str(tmp_path))


def _overview_with(service_labels: dict[str, str]) -> CanvasDoc:
    """v0.11 Phase C2 — services canvas with services needs ≥ 1 anchor."""
    nodes: list[SketchNode] = [
        SketchNode(id=sid, kind="service", label=label) for sid, label in service_labels.items()
    ]
    if nodes:
        nodes.append(
            SketchNode(
                id="anchor-mission",
                kind="mission_ref",
                ref_mission_id="mission",
                label="→ Mission",
            )
        )
    return CanvasDoc(
        canvas_id="services",
        canvas_kind="services",
        nodes=nodes,
    )


def test_sync_creates_detail_for_new_service(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    write_canvas(plot_root, "alpha", _overview_with({"order": "주문"}))
    result = sync_details_with_overview(plot_root, "alpha")
    assert result["created"] == ["order"]
    assert list_service_details(plot_root, "alpha") == ["order"]
    detail = read_canvas(plot_root, "alpha", "service_detail", service_id="order")
    assert detail.service_ref == "order"
    assert any(n.id == "order" for n in detail.nodes)


def test_sync_archives_removed_service(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    write_canvas(plot_root, "alpha", _overview_with({"order": "주문", "pay": "결제"}))
    sync_details_with_overview(plot_root, "alpha")
    # remove "pay" from overview
    write_canvas(plot_root, "alpha", _overview_with({"order": "주문"}))
    result = sync_details_with_overview(plot_root, "alpha")
    assert result["archived"] == ["pay"]
    # pay detail moved to _archive, no longer listed as a live detail
    assert "pay" not in list_service_details(plot_root, "alpha")
    # v0.8: archived service folder moves to ``services/_archive/{sid}/``
    # with its ``detail.json`` (and any ``index.md``) intact.
    archive = plot_root / "alpha" / "services" / "_archive" / "pay" / "detail.json"
    assert archive.is_file()


def test_sync_is_noop_when_overview_matches(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    write_canvas(plot_root, "alpha", _overview_with({"order": "주문"}))
    sync_details_with_overview(plot_root, "alpha")
    again = sync_details_with_overview(plot_root, "alpha")
    assert again == {"created": [], "archived": []}


def test_sync_on_empty_overview_is_noop(plot_root: Path) -> None:
    create_project(plot_root, "alpha", "Alpha")
    result = sync_details_with_overview(plot_root, "alpha")
    assert result == {"created": [], "archived": []}
