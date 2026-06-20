"""Retired-kind drop-on-read (D-2026-06-19-H — `group` retirement, 2026-06-20).

When a kind leaves the palette its discriminant is removed from the
``SketchNode`` union, so a node of that kind in an older ``canvas.json`` would
fail ``CanvasDoc.model_validate``. ``canvas_io._drop_retired_kinds`` strips such
nodes (and any edge incident to them) on read — loss-free for surviving content
(retiring ``group`` drops only the container, never its member step/decision
nodes). These tests pin that behaviour at the unit level (the read_canvas wiring
is one call; the full suite guards no-regression).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from plot_mcp.canvas_io import RETIRED_KINDS, _drop_retired_kinds
from plot_mcp.git_store import init_workspace_repo
from plot_mcp.workspace import resolve_plot_root


@pytest.fixture
def plot_root(tmp_path: Path) -> Path:
    init_workspace_repo(tmp_path)
    return resolve_plot_root(str(tmp_path))


def test_group_is_a_retired_kind() -> None:
    """`group` retired 2026-06-20 (D-2026-06-19-H — chunking = feature level;
    folding a flow is a view affordance, not a node kind)."""
    assert "group" in RETIRED_KINDS


def test_drop_retired_kinds_strips_group_and_incident_edges(plot_root: Path) -> None:
    raw = {
        "nodes": [
            {"id": "s1", "kind": "step", "label": "do"},
            {"id": "g1", "kind": "group", "label": "chunk", "member_ids": ["s1"]},
        ],
        "edges": [{"id": "e1", "source": "g1", "target": "s1"}],
    }
    out = _drop_retired_kinds(plot_root, "alpha", "feature", "svc1", raw)
    assert "group" not in {n["kind"] for n in out["nodes"]}, "retired group node dropped"
    assert [n["id"] for n in out["nodes"]] == ["s1"], "member step survives (loss-free)"
    assert out["edges"] == [], "edge incident to the dropped group is removed"


def test_drop_retired_kinds_is_noop_without_retired_nodes(plot_root: Path) -> None:
    raw = {"nodes": [{"id": "s1", "kind": "step"}], "edges": []}
    out = _drop_retired_kinds(plot_root, "alpha", "feature", "svc1", raw)
    assert out == raw, "a canvas with no retired kinds is returned unchanged"
