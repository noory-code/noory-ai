"""Tests for the probe-driven evaluation tools (rag_get_probes /
rag_set_probes / rag_evaluate).

The evaluation tool sits on top of the wired Container's searcher, so we
build a small in-memory corpus first via tool_set_settings + tool_upsert_chunks
(reusing the same flow that init-rag + rag-reindex drive in production),
then assert that rag_evaluate's response shape and aggregates are sane.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from rag_mcp import server as srv


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("RAG_PROJECT_ROOT", str(tmp_path))
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    srv._State.reset()
    yield tmp_path
    srv._State.reset()


def _init_settings_and_index(project: Path) -> None:
    """Bootstrap a minimal corpus so `rag_evaluate` has something to find."""
    from _helpers.fake_embedder import FakeEmbedder

    # Settings first.
    payload = {
        "sources": [{"path": ".noory/rag/raw/", "recursive": True}],
        "embedding": {"provider": "local", "model": "fake", "dim": 16},
        "chunking": {"target_tokens": 400, "max_tokens": 800, "min_tokens": 100},
        "graph": {"expand_depth": 1, "community_algo": "leiden"},
    }
    r = srv.tool_set_settings(payload)
    assert r["ok"], r

    # Swap embedder for a deterministic in-memory one before wiring.
    srv._State.reset()
    from rag_mcp.container import Container
    from rag_mcp.infrastructure import settings_json as sio
    from rag_mcp.infrastructure.paths import RagPaths

    paths = RagPaths.from_cwd()
    settings = sio.load(paths.settings_file)
    container = Container.wire(paths, settings)
    # Replace embedder + searcher to use the FakeEmbedder so tests are fast/deterministic.
    fake = FakeEmbedder(dim=16)
    container.embedder = fake
    container.vector.close()
    from rag_mcp.infrastructure.vector_sqlitevec import SqliteVecIndex

    container.vector = SqliteVecIndex(paths.vec_db, dim=16)
    from rag_mcp.application.indexer import Indexer
    from rag_mcp.application.searcher import Searcher

    container.indexer = Indexer(
        embedder=fake,
        vector=container.vector,
        graph=container.graph,
        manifest=container.manifest,
        sources=container.sources,
        project_root=paths.project_root,
    )
    container.searcher = Searcher(
        embedder=fake, vector=container.vector, graph=container.graph
    )
    srv._State.container = container
    srv._State.paths = paths
    # Pin the staleness marker: _State.get() rebuilds the container when
    # settings.json's mtime differs from the recorded one, which would
    # discard the FakeEmbedder wiring above.
    srv._State._settings_mtime_ns = srv._State._mtime_ns(paths.settings_file)

    # Upsert two files.
    srv.tool_upsert_chunks(
        file="auth.md",
        chunks=[
            {"text": "The project's authentication flow proceeds via OAuth-based session token issuance."}
        ],
        entities=[],
        relations=[],
    )
    srv.tool_upsert_chunks(
        file="payment.md",
        chunks=[
            {"text": "The payment module has PENDING → AUTH → CAPTURED → SETTLED states."}
        ],
        entities=[],
        relations=[],
    )


def test_get_probes_returns_empty_initially(project: Path) -> None:
    r = srv.tool_get_probes()
    assert r == {"ok": True, "probes": []}


def test_set_probes_writes_to_state_dir(project: Path) -> None:
    r = srv.tool_set_probes(
        [
            {"id": "auth-flow", "query": "What is the authentication flow?", "note": "onboarding"},
            {"id": "payment_state", "query": "payment status"},
        ]
    )
    assert r == {"ok": True, "count": 2}
    probes_file = project / ".noory/rag" / "probes.json"
    assert probes_file.is_file()
    assert "auth-flow" in probes_file.read_text()


def test_set_probes_validates(project: Path) -> None:
    bad = srv.tool_set_probes([{"id": "with space", "query": "q"}])
    assert bad["ok"] is False
    assert "invalid probes" in bad["error"]


def test_set_probes_rejects_duplicate_ids(project: Path) -> None:
    bad = srv.tool_set_probes(
        [{"id": "dup", "query": "a"}, {"id": "dup", "query": "b"}]
    )
    assert bad["ok"] is False


def test_evaluate_no_probes_returns_error(project: Path) -> None:
    _init_settings_and_index(project)
    r = srv.tool_evaluate()
    assert r["ok"] is False
    assert "no probes registered" in r["error"]


def test_evaluate_runs_each_probe(project: Path) -> None:
    _init_settings_and_index(project)
    srv.tool_set_probes(
        [
            {"id": "auth-flow", "query": "authentication flow"},
            {"id": "payment_state", "query": "payment status"},
        ]
    )
    r = srv.tool_evaluate(k=3)
    assert r["ok"] is True
    assert r["k"] == 3
    assert len(r["results"]) == 2
    ids = {row["probe_id"] for row in r["results"]}
    assert ids == {"auth-flow", "payment_state"}

    for row in r["results"]:
        assert "chunks" in row
        assert "stats" in row
        # FakeEmbedder is deterministic but topical similarity isn't guaranteed;
        # we only check that the shape is right.
        assert isinstance(row["stats"]["unique_files"], int)


def test_evaluate_filters_by_probe_ids(project: Path) -> None:
    _init_settings_and_index(project)
    srv.tool_set_probes(
        [
            {"id": "auth-flow", "query": "authentication flow"},
            {"id": "payment_state", "query": "payment status"},
        ]
    )
    r = srv.tool_evaluate(probe_ids=["auth-flow"], k=2)
    assert r["ok"] is True
    assert len(r["results"]) == 1
    assert r["results"][0]["probe_id"] == "auth-flow"


def test_evaluate_unknown_probe_id_fails(project: Path) -> None:
    _init_settings_and_index(project)
    srv.tool_set_probes([{"id": "real", "query": "q"}])
    r = srv.tool_evaluate(probe_ids=["nope"])
    assert r["ok"] is False


def test_probe_tools_surface_env_config_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If the project root cannot be resolved, probe tools should return the
    structured _err response instead of crashing — same as settings tools."""
    monkeypatch.delenv("RAG_PROJECT_ROOT", raising=False)
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    srv._State.reset()

    r1 = srv.tool_get_probes()
    assert r1["ok"] is False and "RAG_PROJECT_ROOT" in r1["error"]
    r2 = srv.tool_set_probes([{"id": "a", "query": "b"}])
    assert r2["ok"] is False and "RAG_PROJECT_ROOT" in r2["error"]
