"""Tests for search-feedback self-improvement (US-003).

Deterministic/local path: feedback store round-trip, boost aggregation, the
pure re-rank function, and the Searcher applying feedback. The "user decides
good/bad" judgement is a session action (outside pytest) — here verdicts are
supplied directly.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from rag_mcp.application.indexer import Indexer
from rag_mcp.application.searcher import Searcher, apply_feedback_boost
from rag_mcp.domain.models import ChunkData, SearchHit
from rag_mcp.infrastructure import feedback_json
from rag_mcp.infrastructure.graph_kuzu import KuzuGraphIndex
from rag_mcp.infrastructure.manifest_json import JsonManifest
from rag_mcp.infrastructure.sources_fs import FilesystemSources
from rag_mcp.infrastructure.vector_sqlitevec import SqliteVecIndex


# ------------------------------------------------------------------- store

def test_feedback_roundtrip_and_aggregate(tmp_path: Path) -> None:
    f = tmp_path / "feedback.json"
    assert feedback_json.load(f) == []
    feedback_json.append(f, "auth flow", "docs/auth.md", "good")
    feedback_json.append(f, "auth flow", "docs/auth.md", "good")
    feedback_json.append(f, "auth flow", "docs/old.md", "bad")
    records = feedback_json.load(f)
    assert len(records) == 3
    boosts = feedback_json.aggregate_boosts(records)
    assert boosts["docs/auth.md"] == 2.0
    assert boosts["docs/old.md"] == -1.0


def test_feedback_rejects_bad_verdict(tmp_path: Path) -> None:
    f = tmp_path / "feedback.json"
    with pytest.raises(feedback_json.FeedbackError):
        feedback_json.append(f, "q", "docs/a.md", "meh")


# -------------------------------------------------------------- pure re-rank

def _hit(rel_path: str, distance: float) -> SearchHit:
    return SearchHit(
        chunk_id=0, rel_path=rel_path, chunk_idx=0, text="", meta={}, distance=distance
    )


def test_apply_feedback_boost_reorders() -> None:
    hits = [_hit("a.md", 0.30), _hit("b.md", 0.35)]
    out = apply_feedback_boost(hits, {"b.md": 2.0}, factor=0.05)
    assert [h.rel_path for h in out] == ["b.md", "a.md"]


def test_apply_feedback_boost_empty_is_stable() -> None:
    hits = [_hit("a.md", 0.30), _hit("b.md", 0.35)]
    assert apply_feedback_boost(hits, {}) == hits


# ----------------------------------------------------------- searcher wiring

def _wire(tmp_state, fake_embedder, boosts: dict[str, float]):
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
    searcher = Searcher(
        embedder=fake_embedder, vector=vector, graph=graph, feedback_boosts=lambda: boosts
    )
    return indexer, searcher, graph


def test_searcher_applies_feedback(tmp_state, fake_embedder) -> None:
    boosts: dict[str, float] = {}
    indexer, searcher, graph = _wire(tmp_state, fake_embedder, boosts)
    indexer.upsert_file("good.md", [ChunkData(text="alpha beta gamma")], [], [])
    indexer.upsert_file("bad.md", [ChunkData(text="alpha beta gamma delta")], [], [])

    base = searcher.search("alpha beta gamma", k=5, expand_depth=1)
    base_order = [h.rel_path for h in base.chunks]
    assert len(base_order) == 2

    # Strongly boost whichever was ranked last → it should move to the top.
    last = base_order[-1]
    boosts[last] = 100.0
    boosted = searcher.search("alpha beta gamma", k=5, expand_depth=1)
    assert boosted.chunks[0].rel_path == last
    graph.close()


# ---------------------------------------------------------- MCP tool surface

def test_feedback_mcp_tools_roundtrip(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    monkeypatch.setenv("RAG_PROJECT_ROOT", str(project))
    from rag_mcp import server

    r1 = server.tool_record_feedback("auth flow", "docs/auth.md", "good")
    assert r1["ok"] is True
    r2 = server.tool_get_feedback()
    assert r2["ok"] is True
    assert r2["count"] == 1
    assert r2["boosts"]["docs/auth.md"] == 1.0

    bad = server.tool_record_feedback("q", "docs/a.md", "nope")
    assert bad["ok"] is False
