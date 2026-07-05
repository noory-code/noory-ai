"""Unit tests for :mod:`rag_mcp.infrastructure.vector_sqlitevec`."""

from __future__ import annotations

import numpy as np

from rag_mcp.domain.models import ChunkData
from rag_mcp.infrastructure.vector_sqlitevec import SqliteVecIndex


def _embed(idx: int, dim: int = 8) -> np.ndarray:
    v = np.zeros(dim, dtype=np.float32)
    v[idx % dim] = 1.0
    return v


def test_add_and_search_top_k(tmp_state) -> None:
    store = SqliteVecIndex(tmp_state.vec_db, dim=8)
    chunks = [ChunkData(text=f"chunk {i}", meta={"i": i}) for i in range(3)]
    embeddings = np.stack([_embed(i) for i in range(3)])
    ids = store.add_file("a.md", chunks, embeddings)
    assert len(ids) == 3

    hits = store.search(_embed(1), k=3)
    assert hits[0].chunk_id == ids[1]
    assert hits[0].rel_path == "a.md"
    assert hits[0].text == "chunk 1"
    assert hits[0].distance <= hits[1].distance <= hits[2].distance


def test_re_add_replaces(tmp_state) -> None:
    store = SqliteVecIndex(tmp_state.vec_db, dim=8)
    chunks = [ChunkData(text=f"chunk {i}", meta={}) for i in range(2)]
    store.add_file("a.md", chunks, np.stack([_embed(i) for i in range(2)]))
    assert store.stats()["chunks"] == 2

    store.add_file(
        "a.md",
        [ChunkData(text="only", meta={})],
        _embed(0).reshape(1, -1),
    )
    assert store.stats()["chunks"] == 1
    hits = store.search(_embed(0), k=5)
    assert all(h.rel_path == "a.md" for h in hits)
    assert hits[0].text == "only"


def test_delete_file(tmp_state) -> None:
    store = SqliteVecIndex(tmp_state.vec_db, dim=8)
    store.add_file("a.md", [ChunkData(text="x", meta={})], _embed(0).reshape(1, -1))
    store.add_file("b.md", [ChunkData(text="y", meta={})], _embed(1).reshape(1, -1))
    assert store.stats()["files"] == 2
    n = store.delete_file("a.md")
    assert n == 1
    assert store.stats() == {"files": 1, "chunks": 1}
    assert store.list_files() == ["b.md"]


def test_dim_mismatch_rejected(tmp_state) -> None:
    store = SqliteVecIndex(tmp_state.vec_db, dim=8)
    import pytest

    with pytest.raises(ValueError):
        store.add_file(
            "a.md",
            [ChunkData(text="x", meta={})],
            np.zeros((1, 16), dtype=np.float32),
        )
