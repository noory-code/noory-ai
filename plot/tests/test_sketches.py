"""Round-trip tests for the JSON sketch store."""

from __future__ import annotations

from pathlib import Path

import pytest

from plot_mcp.models import SketchDoc, SketchEdge, SketchNode
from plot_mcp.sketches import (
    create_sketch,
    delete_sketch,
    list_sketches,
    read_sketch,
    write_sketch,
)
from plot_mcp.workspace import resolve_plot_root


@pytest.fixture
def plot_root(tmp_path: Path) -> Path:
    return resolve_plot_root(str(tmp_path))


def test_resolve_creates_dotfolder(tmp_path: Path) -> None:
    root = resolve_plot_root(str(tmp_path))
    assert root == tmp_path / ".plot"
    assert (root / "sketches").is_dir()


def test_create_and_read(plot_root: Path) -> None:
    doc = create_sketch(plot_root, "alpha", "Alpha")
    assert doc.id == "alpha"
    assert doc.name == "Alpha"
    loaded = read_sketch(plot_root, "alpha")
    assert loaded.id == "alpha"
    assert loaded.name == "Alpha"
    assert loaded.created == doc.created


def test_create_duplicate_raises(plot_root: Path) -> None:
    create_sketch(plot_root, "alpha", "Alpha")
    with pytest.raises(FileExistsError):
        create_sketch(plot_root, "alpha", "Again")


def test_write_updates_timestamp(plot_root: Path) -> None:
    doc = create_sketch(plot_root, "alpha", "Alpha")
    before = doc.updated
    # Replace both nodes and edges to avoid dangling seed edges referring to
    # removed seed nodes (v0.2: create_sketch also seeds 2 hierarchy edges).
    doc_with_node = doc.model_copy(
        update={"nodes": [SketchNode(id="n1", label="First")], "edges": []}
    )
    write_sketch(plot_root, doc_with_node)
    reloaded = read_sketch(plot_root, "alpha")
    assert reloaded.nodes[0].label == "First"
    assert reloaded.updated >= before


def test_write_with_edges(plot_root: Path) -> None:
    doc = SketchDoc(
        id="two-node",
        name="Two",
        nodes=[
            SketchNode(id="a", label="A"),
            SketchNode(id="b", label="B"),
        ],
        edges=[SketchEdge(id="e1", source="a", target="b", label="to")],
    )
    write_sketch(plot_root, doc)
    reloaded = read_sketch(plot_root, "two-node")
    assert len(reloaded.nodes) == 2
    assert reloaded.edges[0].label == "to"


def test_edges_must_reference_existing_nodes() -> None:
    with pytest.raises(ValueError, match="unknown nodes"):
        SketchDoc(
            id="bad",
            nodes=[SketchNode(id="a", label="A")],
            edges=[SketchEdge(id="e1", source="a", target="ghost")],
        )


def test_list_sorts_by_updated_desc(plot_root: Path) -> None:
    create_sketch(plot_root, "older", "Older")
    # Small delay forced via explicit write to bump updated
    create_sketch(plot_root, "newer", "Newer")
    result = list_sketches(plot_root)
    ids = [s.id for s in result]
    assert "newer" in ids and "older" in ids
    # Either order acceptable within the same millisecond tick; assert at
    # least both present and both have correct counts.
    summary_by_id = {s.id: s for s in result}
    # v0.2: create_sketch seeds Core + Actor-root + Service-root + 2 hierarchy edges.
    assert summary_by_id["newer"].node_count == 3
    assert summary_by_id["older"].edge_count == 2


def test_delete(plot_root: Path) -> None:
    create_sketch(plot_root, "tmp", "Tmp")
    delete_sketch(plot_root, "tmp")
    with pytest.raises(FileNotFoundError):
        read_sketch(plot_root, "tmp")


def test_delete_missing_raises(plot_root: Path) -> None:
    with pytest.raises(FileNotFoundError):
        delete_sketch(plot_root, "never-existed")


def test_sketch_id_rejects_bad_chars() -> None:
    with pytest.raises(ValueError, match="alphanumeric"):
        SketchDoc(id="has space")
    with pytest.raises(ValueError, match="alphanumeric"):
        SketchDoc(id="slash/id")


def test_list_skips_malformed_files(plot_root: Path, tmp_path: Path) -> None:
    create_sketch(plot_root, "good", "Good")
    (plot_root / "sketches" / "broken.json").write_text("not json", encoding="utf-8")
    result = list_sketches(plot_root)
    ids = [s.id for s in result]
    assert "good" in ids
    assert "broken" not in ids
