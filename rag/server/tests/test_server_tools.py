"""Server-tool-level tests: response shapes, export ordering, argument
bounds, corrupt-manifest surfacing, and settings staleness.

These drive the ``tool_*`` functions directly (same pattern as
``test_evaluate``): a tmp project root via ``RAG_PROJECT_ROOT`` plus
``tool_set_settings`` with a never-loaded "fake" embedding model, so no real
sentence-transformers model is ever downloaded.
"""

from __future__ import annotations

import io
import json
import os
import tarfile
from pathlib import Path
from typing import Any

import pytest

from rag_mcp import server as srv


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("RAG_PROJECT_ROOT", str(tmp_path))
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    srv._State.reset()
    yield tmp_path
    srv._State.reset()


def _settings_payload() -> dict[str, Any]:
    return {
        "sources": [{"path": ".noory/rag/raw/", "recursive": True}],
        "embedding": {"provider": "local", "model": "fake", "dim": 16},
        "chunking": {"target_tokens": 400, "max_tokens": 800, "min_tokens": 100},
        "graph": {"expand_depth": 1, "community_algo": "leiden"},
    }


def _configure(project: Path) -> None:
    r = srv.tool_set_settings(_settings_payload())
    assert r["ok"], r


def _inject_fake_embedder() -> None:
    """Swap the wired embedder/vector/indexer/searcher for FakeEmbedder(16).

    Obtained through ``_State.get()`` so the container's staleness bookkeeping
    stays intact; only the embedding-touching parts are replaced.
    """
    from _helpers.fake_embedder import FakeEmbedder

    from rag_mcp.application.indexer import Indexer
    from rag_mcp.application.searcher import Searcher
    from rag_mcp.infrastructure.vector_sqlitevec import SqliteVecIndex

    container = srv._State.get()
    fake = FakeEmbedder(dim=16)
    container.embedder = fake
    container.vector.close()
    container.vector = SqliteVecIndex(container.paths.vec_db, dim=16)
    container.indexer = Indexer(
        embedder=fake,
        vector=container.vector,
        graph=container.graph,
        manifest=container.manifest,
        sources=container.sources,
        project_root=container.paths.project_root,
    )
    container.searcher = Searcher(
        embedder=fake, vector=container.vector, graph=container.graph
    )


# ------------------------------------------------------------ MAJOR-2: export


def test_export_computes_stats_before_close_before_tarball(
    project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """rag_export must compute stats on the live handles, then close (flush),
    then read the tarball — otherwise stats reopens the connections the close
    was supposed to flush."""
    _configure(project)
    container = srv._State.get()
    events: list[str] = []

    orig_close = container.close
    orig_vstats = container.vector.stats
    orig_export = srv.snap.export_snapshot

    def close_spy() -> None:
        events.append("close")
        orig_close()

    def vstats_spy() -> dict[str, int]:
        events.append("stats")
        return orig_vstats()

    def export_spy(*args: Any, **kwargs: Any) -> Any:
        events.append("export")
        return orig_export(*args, **kwargs)

    monkeypatch.setattr(container, "close", close_spy)
    monkeypatch.setattr(container.vector, "stats", vstats_spy)
    monkeypatch.setattr(srv.snap, "export_snapshot", export_spy)

    out = project / "snap.tar.gz"
    r = srv.tool_export(str(out))
    assert r["ok"], r
    assert out.exists()
    assert {"stats", "close", "export"} <= set(events)
    assert events.index("stats") < events.index("close") < events.index("export")


# ----------------------------------------------------- MINOR-1: schema bounds


def test_search_rejects_out_of_bounds_k(project: Path) -> None:
    _configure(project)
    for bad in (0, 65):
        r = srv.tool_search("anything", k=bad)
        assert r["ok"] is False, r
        assert "out of range" in r["error"] and "k" in r["error"]


def test_search_rejects_out_of_bounds_expand_depth(project: Path) -> None:
    _configure(project)
    for bad in (-1, 5):
        r = srv.tool_search("anything", expand_depth=bad)
        assert r["ok"] is False, r
        assert "out of range" in r["error"] and "expand_depth" in r["error"]


def test_search_graph_rejects_out_of_bounds_depth(project: Path) -> None:
    _configure(project)
    for bad in (0, 5):
        r = srv.tool_search_graph("Whatever", depth=bad)
        assert r["ok"] is False, r
        assert "out of range" in r["error"] and "depth" in r["error"]


def test_evaluate_rejects_out_of_bounds_k(project: Path) -> None:
    _configure(project)
    r0 = srv.tool_set_probes([{"id": "p1", "query": "q"}])
    assert r0["ok"], r0
    for bad in (0, 33):
        r = srv.tool_evaluate(k=bad)
        assert r["ok"] is False, r
        assert "out of range" in r["error"] and "k" in r["error"]


def test_evaluate_rejects_out_of_bounds_expand_depth(project: Path) -> None:
    _configure(project)
    r0 = srv.tool_set_probes([{"id": "p1", "query": "q"}])
    assert r0["ok"], r0
    r = srv.tool_evaluate(expand_depth=5)
    assert r["ok"] is False, r
    assert "out of range" in r["error"] and "expand_depth" in r["error"]


# ------------------------------------------- MINOR-2: corrupt manifest warning


def test_diff_files_surfaces_corrupt_manifest_warning(project: Path) -> None:
    _configure(project)
    raw = project / ".noory" / "rag" / "raw"
    (raw / "a.md").write_text("# A", encoding="utf-8")
    manifest = project / ".noory" / "rag" / "manifest.json"
    manifest.write_text("{definitely not json", encoding="utf-8")

    r = srv.tool_diff_files()
    assert r["ok"] is True, r
    assert ".noory/rag/raw/a.md" in r["added"]
    assert "corrupt" in r.get("warning", "")


def test_diff_files_no_warning_when_manifest_healthy(project: Path) -> None:
    _configure(project)
    raw = project / ".noory" / "rag" / "raw"
    (raw / "a.md").write_text("# A", encoding="utf-8")

    r = srv.tool_diff_files()
    assert r["ok"] is True, r
    assert "warning" not in r


def test_upsert_chunks_surfaces_corrupt_manifest_warning(project: Path) -> None:
    _configure(project)
    _inject_fake_embedder()
    raw = project / ".noory" / "rag" / "raw"
    (raw / "a.md").write_text("# A", encoding="utf-8")
    manifest = project / ".noory" / "rag" / "manifest.json"
    manifest.write_text("{definitely not json", encoding="utf-8")

    r = srv.tool_upsert_chunks(
        file=".noory/rag/raw/a.md", chunks=[{"text": "alpha"}]
    )
    assert r["ok"] is True, r
    assert "corrupt" in r.get("warning", "")
    # The manifest is usable again after the incremental save.
    hashes = json.loads(manifest.read_text(encoding="utf-8"))["hashes"]
    assert ".noory/rag/raw/a.md" in hashes


# ------------------------------------------------ MINOR-3: structured errors


def test_import_corrupt_tarball_returns_structured_error(project: Path) -> None:
    bad = project / "corrupt.tar.gz"
    bad.write_bytes(b"this is not a tarball at all")
    r = srv.tool_import(str(bad))
    assert r["ok"] is False, r
    assert "snapshot" in r["error"]


def test_import_tarball_missing_header_returns_structured_error(project: Path) -> None:
    _configure(project)
    weird = project / "weird.tar.gz"
    with tarfile.open(weird, "w:gz") as tar:
        payload = b"x"
        info = tarfile.TarInfo("random.txt")
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))
    r = srv.tool_import(str(weird))
    assert r["ok"] is False, r
    assert "snapshot" in r["error"]


def test_import_unsupported_mode_returns_structured_error(project: Path) -> None:
    _configure(project)
    r = srv.tool_import(str(project / "whatever.tar.gz"), mode="sideways")
    assert r["ok"] is False, r
    assert "mode" in r["error"]


def test_search_unconfigured_project_returns_structured_error(project: Path) -> None:
    # No settings.json written: the error must be the structured shape, not
    # a raised SettingsError.
    r = srv.tool_search("anything")
    assert r["ok"] is False, r
    assert "settings" in r["error"]


# --------------------------------------------- MINOR-5: settings staleness


def test_external_settings_edit_is_seen_by_next_tool_call(project: Path) -> None:
    _configure(project)
    r1 = srv.tool_stats()
    assert r1["ok"], r1
    assert r1["embedding_model"] == "fake"

    settings_file = project / ".noory" / "rag" / "settings.json"
    data = json.loads(settings_file.read_text(encoding="utf-8"))
    data["embedding"]["model"] = "fake-v2"
    settings_file.write_text(json.dumps(data), encoding="utf-8")
    # Force an observable mtime bump even on coarse-timestamp filesystems.
    st = settings_file.stat()
    os.utime(settings_file, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000_000))

    r2 = srv.tool_stats()
    assert r2["ok"], r2
    assert r2["embedding_model"] == "fake-v2"


def test_untouched_settings_keep_container_cached(project: Path) -> None:
    _configure(project)
    c1 = srv._State.get()
    c2 = srv._State.get()
    assert c1 is c2
