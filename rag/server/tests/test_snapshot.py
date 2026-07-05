"""Unit tests for :mod:`rag_mcp.infrastructure.snapshot`."""

from __future__ import annotations

import pytest

from rag_mcp.infrastructure import snapshot as snap


def test_export_then_import_replace_roundtrip(tmp_path, tmp_state) -> None:
    # Seed the state with some content.
    (tmp_state.state_dir / "vec.db").write_bytes(b"vec-bytes")
    (tmp_state.graph_dir).mkdir(exist_ok=True)
    (tmp_state.graph_dir / "kuzu.kz").write_bytes(b"graph-bytes")
    (tmp_state.manifest_file).write_text('{"hashes": {"a.md": "h"}}')
    (tmp_state.settings_file).write_text("{}")

    out = tmp_path / "snap.tar.gz"
    header = snap.export_snapshot(
        tmp_state.state_dir,
        out,
        embedding_model="m",
        embedding_dim=384,
        plugin_version="0.1.0",
        stats={"chunks": 3},
    )
    assert out.exists()
    assert header.embedding_dim == 384

    # Wipe and re-import.
    import shutil

    shutil.rmtree(tmp_state.state_dir)
    snap.import_snapshot(
        out,
        tmp_state.state_dir,
        expected_model="m",
        expected_dim=384,
        plugin_major="0",
        mode="replace",
    )
    assert (tmp_state.state_dir / "vec.db").read_bytes() == b"vec-bytes"
    assert (tmp_state.graph_dir / "kuzu.kz").read_bytes() == b"graph-bytes"


def test_import_rejects_dim_mismatch(tmp_path, tmp_state) -> None:
    (tmp_state.state_dir / "vec.db").write_bytes(b"x")
    out = tmp_path / "snap.tar.gz"
    snap.export_snapshot(
        tmp_state.state_dir,
        out,
        embedding_model="m",
        embedding_dim=384,
        plugin_version="0.1.0",
    )
    with pytest.raises(snap.IncompatibleSnapshot):
        snap.import_snapshot(
            out,
            tmp_state.state_dir,
            expected_model="m",
            expected_dim=768,
            plugin_major="0",
        )


def test_import_rejects_model_mismatch(tmp_path, tmp_state) -> None:
    out = tmp_path / "snap.tar.gz"
    snap.export_snapshot(
        tmp_state.state_dir,
        out,
        embedding_model="a",
        embedding_dim=384,
        plugin_version="0.1.0",
    )
    with pytest.raises(snap.IncompatibleSnapshot):
        snap.import_snapshot(
            out,
            tmp_state.state_dir,
            expected_model="b",
            expected_dim=384,
            plugin_major="0",
        )


def test_import_rejects_major_mismatch(tmp_path, tmp_state) -> None:
    out = tmp_path / "snap.tar.gz"
    snap.export_snapshot(
        tmp_state.state_dir,
        out,
        embedding_model="m",
        embedding_dim=384,
        plugin_version="0.1.0",
    )
    with pytest.raises(snap.IncompatibleSnapshot):
        snap.import_snapshot(
            out,
            tmp_state.state_dir,
            expected_model="m",
            expected_dim=384,
            plugin_major="1",
        )
