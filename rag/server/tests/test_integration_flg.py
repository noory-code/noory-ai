"""End-to-end simulation against the ``flutter-cask`` corpus.

Uses the real ``intfloat/multilingual-e5-small`` embedder and the deterministic
surrogate chunker + entity/relation extractor in place of the LLM step. Marked
``slow`` because the first run downloads the embedding model.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from rag_mcp.application.indexer import Indexer
from rag_mcp.application.rebalancer import Rebalancer
from rag_mcp.application.searcher import Searcher
from rag_mcp.domain.models import SourceSpec
from rag_mcp.infrastructure.community_leiden import LeidenCommunityDetector
from rag_mcp.infrastructure.embedder_st import SentenceTransformersEmbedder
from rag_mcp.infrastructure.graph_kuzu import KuzuGraphIndex
from rag_mcp.infrastructure.manifest_json import JsonManifest
from rag_mcp.infrastructure.paths import RagPaths
from rag_mcp.infrastructure.sources_fs import FilesystemSources
from rag_mcp.infrastructure.vector_sqlitevec import SqliteVecIndex

from _helpers.surrogate import chunk_and_extract

pytestmark = pytest.mark.slow

FLG_SRC = (
    Path(__file__).resolve().parents[3]
    / "flutter-cask"
    / "skills"
)


@pytest.fixture(scope="session")
def flg_state(tmp_path_factory):
    if not FLG_SRC.exists():
        pytest.skip("flutter-cask corpus not found")

    root = tmp_path_factory.mktemp("flg-project")
    target = root / "docs"
    shutil.copytree(FLG_SRC, target)

    paths = RagPaths.from_cwd(root)
    paths.ensure_state_layout()

    embedder = SentenceTransformersEmbedder("intfloat/multilingual-e5-small")
    vector = SqliteVecIndex(paths.vec_db, dim=embedder.dim)
    graph = KuzuGraphIndex(paths.graph_dir)
    _ = graph.conn
    manifest = JsonManifest(paths.manifest_file)
    sources = FilesystemSources(paths.project_root)
    indexer = Indexer(
        embedder=embedder,
        vector=vector,
        graph=graph,
        manifest=manifest,
        sources=sources,
        project_root=paths.project_root,
    )
    searcher = Searcher(embedder=embedder, vector=vector, graph=graph)
    rebalancer = Rebalancer(graph=graph, community=LeidenCommunityDetector())

    spec = SourceSpec(path="docs/", recursive=True, include=("**/*.md",))

    # Initial full ingest using the surrogate as the LLM stand-in.
    walked = sources.walk([spec])
    for path in walked:
        rel = sources.rel_to_project(path)
        text = path.read_text(encoding="utf-8")
        chunks, extracted = chunk_and_extract(rel, text)
        indexer.upsert_file(rel, chunks, extracted.entities, extracted.relations)
    indexer.manifest.save(indexer.current_hashes([spec]))

    yield {
        "paths": paths,
        "indexer": indexer,
        "searcher": searcher,
        "rebalancer": rebalancer,
        "vector": vector,
        "graph": graph,
        "sources": sources,
        "spec": spec,
        "root": root,
    }

    graph.close()
    vector.close()


def test_indexing_produces_meaningful_corpus(flg_state) -> None:
    vstats = flg_state["vector"].stats()
    gstats = flg_state["graph"].stats()
    assert vstats["files"] >= 10
    assert vstats["chunks"] >= 30
    assert gstats["entities"] >= 10
    assert gstats["relations"] >= 5


@pytest.mark.parametrize(
    "query,expected_token",
    [
        ("riverpod provider pattern state management", "guide-lib-riverpod"),
        ("freezed data class code generation", "guide-lib-freezed"),
        ("widget test writing", "guide-lib-widget-test"),
        ("go_router screen transition routing", "guide-lib-go-router"),
    ],
)
def test_search_returns_topic_relevant_chunks(flg_state, query, expected_token) -> None:
    result = flg_state["searcher"].search(query, k=5, expand_depth=1)
    top_paths = [hit.rel_path for hit in result.chunks]
    assert any(expected_token in p for p in top_paths), (
        f"'{expected_token}' not in top-5 for query={query!r}: {top_paths}"
    )


def test_graph_neighbors_around_riverpod(flg_state) -> None:
    sub = flg_state["searcher"].search_graph("riverpod", depth=2)
    assert len(sub.nodes) >= 2


def test_list_entities_by_substring(flg_state) -> None:
    entities = flg_state["graph"].list_entities(q="test")
    names = {e.name.lower() for e in entities}
    # Expect at least one of the test-related libraries.
    assert any(n in names for n in {"widget-test", "integration-test", "patrol"})


def test_reindex_detects_single_file_change(flg_state) -> None:
    paths = flg_state["paths"]
    sources = flg_state["sources"]
    indexer = flg_state["indexer"]
    spec = flg_state["spec"]

    target = paths.project_root / "docs" / "guide-lib-riverpod" / "SKILL.md"
    if not target.exists():
        candidates = list((paths.project_root / "docs").rglob("SKILL.md"))
        assert candidates, "no SKILL.md files under docs/"
        target = candidates[0]
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text(original + "\n\n## Probe\nadded for diff test\n", encoding="utf-8")
        diff = indexer.diff([spec])
        rel = sources.rel_to_project(target)
        assert rel in diff.changed
        assert diff.added == ()
    finally:
        target.write_text(original, encoding="utf-8")
        indexer.manifest.save(indexer.current_hashes([spec]))


def test_rebalance_prep_produces_candidates(flg_state) -> None:
    prep = flg_state["rebalancer"].prep()
    # Communities should be detected from the corpus.
    assert prep.communities, "Leiden produced no communities"
    # Aliases may be empty in this corpus; just confirm the structure is sane.
    assert isinstance(prep.alias_candidates, list)
