"""Unit tests for :class:`rag_mcp.application.indexer.Indexer`."""

from __future__ import annotations

from rag_mcp.application.indexer import Indexer
from rag_mcp.domain.models import ChunkData, EntityData, RelationData, SourceSpec
from rag_mcp.infrastructure.graph_kuzu import KuzuGraphIndex
from rag_mcp.infrastructure.manifest_json import JsonManifest
from rag_mcp.infrastructure.sources_fs import FilesystemSources
from rag_mcp.infrastructure.vector_sqlitevec import SqliteVecIndex


def _make_indexer(tmp_state, fake_embedder) -> tuple[Indexer, SqliteVecIndex, KuzuGraphIndex]:
    vector = SqliteVecIndex(tmp_state.vec_db, dim=fake_embedder.dim)
    graph = KuzuGraphIndex(tmp_state.graph_dir)
    _ = graph.conn  # init schema
    manifest = JsonManifest(tmp_state.manifest_file)
    sources = FilesystemSources(tmp_state.project_root)
    indexer = Indexer(
        embedder=fake_embedder,
        vector=vector,
        graph=graph,
        manifest=manifest,
        sources=sources,
        project_root=tmp_state.project_root,
    )
    return indexer, vector, graph


def test_upsert_file_persists_chunks_and_entities(tmp_state, fake_embedder) -> None:
    indexer, vector, graph = _make_indexer(tmp_state, fake_embedder)
    chunks = [ChunkData(text="riverpod is great"), ChunkData(text="freezed makes sealed classes")]
    entities = [
        EntityData(id="riverpod", name="Riverpod", type="library", chunk_indices=[0]),
        EntityData(id="freezed", name="Freezed", type="library", chunk_indices=[1]),
    ]
    relations = [RelationData(src_id="riverpod", dst_id="freezed", weight=2.0)]
    result = indexer.upsert_file("a.md", chunks, entities, relations)
    assert len(result.chunk_ids) == 2
    assert set(result.entity_ids) == {"riverpod", "freezed"}

    assert vector.stats() == {"files": 1, "chunks": 2}
    gstats = graph.stats()
    assert gstats["entities"] == 2
    assert gstats["relations"] == 1
    assert gstats["mentions"] == 2
    graph.close()


def test_upsert_is_idempotent_on_reupload(tmp_state, fake_embedder) -> None:
    indexer, vector, graph = _make_indexer(tmp_state, fake_embedder)
    indexer.upsert_file("a.md", [ChunkData(text="one")], [], [])
    indexer.upsert_file("a.md", [ChunkData(text="two")], [], [])
    assert vector.stats() == {"files": 1, "chunks": 1}
    graph.close()


def test_upsert_empty_deletes_file(tmp_state, fake_embedder) -> None:
    indexer, vector, graph = _make_indexer(tmp_state, fake_embedder)
    indexer.upsert_file("a.md", [ChunkData(text="hello")], [], [])
    assert vector.stats()["chunks"] == 1
    indexer.upsert_file("a.md", [], [], [])
    assert vector.stats()["chunks"] == 0
    graph.close()


def test_diff_against_manifest(tmp_state, fake_embedder) -> None:
    indexer, vector, graph = _make_indexer(tmp_state, fake_embedder)
    root = tmp_state.project_root
    (root / "docs").mkdir()
    (root / "docs" / "a.md").write_text("# A")
    (root / "docs" / "b.md").write_text("# B")
    src = SourceSpec(path="docs/", recursive=True, include=("**/*.md",))

    diff1 = indexer.diff([src])
    assert set(diff1.added) == {"docs/a.md", "docs/b.md"}

    hashes = indexer.current_hashes([src])
    indexer.manifest.save(hashes)

    (root / "docs" / "a.md").write_text("# A v2")
    (root / "docs" / "c.md").write_text("# C")
    (root / "docs" / "b.md").unlink()

    diff2 = indexer.diff([src])
    assert set(diff2.added) == {"docs/c.md"}
    assert set(diff2.changed) == {"docs/a.md"}
    assert set(diff2.removed) == {"docs/b.md"}
    graph.close()
