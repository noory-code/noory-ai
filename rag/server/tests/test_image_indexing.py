"""Tests for image content indexing support (US-001).

Covers the deterministic/local path only. The "Claude looks at the image and
writes a description" step is a session action (outside pytest); here the
description text is injected as a fixture so the pipeline beneath it
(walk → hash → chunk → search, with image-source meta) is verified.
"""

from __future__ import annotations

from pathlib import Path

from rag_mcp.application.indexer import Indexer
from rag_mcp.application.searcher import Searcher
from rag_mcp.domain.models import ChunkData, SourceSpec
from rag_mcp.infrastructure.graph_kuzu import KuzuGraphIndex
from rag_mcp.infrastructure.manifest_json import JsonManifest, hash_file
from rag_mcp.infrastructure.settings_json import default_settings
from rag_mcp.infrastructure.sources_fs import FilesystemSources
from rag_mcp.infrastructure.vector_sqlitevec import SqliteVecIndex

IMAGE_EXTS = ("png", "jpg", "jpeg", "gif", "webp")

# Minimal PNG signature + a few bytes; content is irrelevant for walk/hash.
_PNG_BYTES = bytes.fromhex("89504e470d0a1a0a0000000d49484452")


def test_default_include_has_image_extensions() -> None:
    settings = default_settings()
    include = settings.sources[0].include
    joined = " ".join(include)
    for ext in IMAGE_EXTS:
        assert f"*.{ext}" in joined, f"default include missing image ext .{ext}"


def test_walk_picks_up_image_files(tmp_path: Path) -> None:
    (tmp_path / "diagrams").mkdir()
    (tmp_path / "diagrams" / "auth-flow.png").write_bytes(_PNG_BYTES)
    (tmp_path / "diagrams" / "notes.md").write_text("# notes")
    src = SourceSpec(
        path="diagrams/",
        recursive=True,
        include=("**/*.png", "**/*.md"),
    )
    fs = FilesystemSources(tmp_path)
    found = [fs.rel_to_project(p) for p in fs.walk([src])]
    assert "diagrams/auth-flow.png" in found
    assert "diagrams/notes.md" in found


def test_image_binary_change_is_detected(tmp_path: Path) -> None:
    img = tmp_path / "shot.png"
    img.write_bytes(_PNG_BYTES)
    before = hash_file(img)
    img.write_bytes(_PNG_BYTES + b"\x00extra-pixels")
    assert before != hash_file(img)


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


def test_image_description_chunk_indexed_and_searchable(tmp_state, fake_embedder) -> None:
    """An image's description text is indexed under the image path and is
    retrievable, with meta marking it as image-derived."""
    indexer, searcher, graph = _wire(tmp_state, fake_embedder)
    description = "auth flow diagram: user logs in via oauth, token stored in provider"
    indexer.upsert_file(
        "diagrams/auth-flow.png",
        [ChunkData(text=description, meta={"source_type": "image"})],
        entities=[],
        relations=[],
    )
    result = searcher.search(description, k=3, expand_depth=1)
    assert len(result.chunks) >= 1
    top = result.chunks[0]
    assert top.rel_path == "diagrams/auth-flow.png"
    assert top.rel_path.endswith(".png")
    assert top.meta.get("source_type") == "image"
    graph.close()
