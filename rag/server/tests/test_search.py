"""Unit tests for :class:`rag_mcp.application.searcher.Searcher`."""

from __future__ import annotations

from rag_mcp.application.indexer import Indexer
from rag_mcp.application.searcher import Searcher
from rag_mcp.domain.models import ChunkData, EntityData, RelationData
from rag_mcp.infrastructure.graph_kuzu import KuzuGraphIndex
from rag_mcp.infrastructure.manifest_json import JsonManifest
from rag_mcp.infrastructure.sources_fs import FilesystemSources
from rag_mcp.infrastructure.vector_sqlitevec import SqliteVecIndex


def _wire(tmp_state, fake_embedder):
    vector = SqliteVecIndex(tmp_state.vec_db, dim=fake_embedder.dim)
    graph = KuzuGraphIndex(tmp_state.graph_dir)
    _ = graph.conn
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
    searcher = Searcher(embedder=fake_embedder, vector=vector, graph=graph)
    return indexer, searcher, graph


def _seed(indexer: Indexer) -> None:
    indexer.upsert_file(
        "riverpod.md",
        [
            ChunkData(text="riverpod provides state management"),
            ChunkData(text="riverpod uses providers and notifiers"),
        ],
        entities=[
            EntityData(id="riverpod", name="Riverpod", type="library", chunk_indices=[0, 1]),
            EntityData(id="notifier", name="Notifier", type="concept", chunk_indices=[1]),
        ],
        relations=[RelationData(src_id="riverpod", dst_id="notifier", weight=1.0)],
    )
    indexer.upsert_file(
        "drift.md",
        [ChunkData(text="drift is a sql ORM for flutter applications")],
        entities=[
            EntityData(id="drift", name="Drift", type="library", chunk_indices=[0]),
            EntityData(id="sql", name="SQL", type="concept", chunk_indices=[0]),
        ],
        relations=[RelationData(src_id="drift", dst_id="sql", weight=1.0)],
    )


def test_search_returns_chunks_and_subgraph(tmp_state, fake_embedder) -> None:
    indexer, searcher, graph = _wire(tmp_state, fake_embedder)
    _seed(indexer)

    result = searcher.search("riverpod provides state management", k=3, expand_depth=2)
    assert len(result.chunks) >= 1
    # Vector top hit should be the exact match.
    top = result.chunks[0]
    assert top.rel_path == "riverpod.md"
    entity_names = {e.name for e in result.entities}
    assert "Riverpod" in entity_names
    graph.close()


def test_search_graph_only_from_entity_name(tmp_state, fake_embedder) -> None:
    indexer, searcher, graph = _wire(tmp_state, fake_embedder)
    _seed(indexer)

    sub = searcher.search_graph("Drift", depth=2)
    names = {n.name for n in sub.nodes}
    assert "Drift" in names and "SQL" in names
    graph.close()


def test_search_expand_depth_zero_skips_graph_expansion(tmp_state, fake_embedder) -> None:
    indexer, searcher, graph = _wire(tmp_state, fake_embedder)
    _seed(indexer)

    result = searcher.search("riverpod provides state management", k=3, expand_depth=0)
    assert len(result.chunks) >= 1
    assert {e.name for e in result.entities}  # mentioned entities still surfaced
    assert result.subgraph.nodes == []
    assert result.subgraph.edges == []
    graph.close()


def test_search_empty_corpus_returns_empty(tmp_state, fake_embedder) -> None:
    _, searcher, graph = _wire(tmp_state, fake_embedder)
    result = searcher.search("anything", k=5)
    assert result.chunks == [] and result.entities == []
    graph.close()
