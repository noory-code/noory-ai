"""Pytest fixtures shared across the rag test suite."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make ``_helpers`` importable without packaging tests/.
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))


@pytest.fixture
def tmp_state(tmp_path: Path):
    """Yield a freshly-constructed RagPaths anchored at a tmp project root."""
    from rag_mcp.infrastructure.paths import RagPaths

    project = tmp_path / "project"
    project.mkdir()
    paths = RagPaths.from_cwd(project)
    paths.ensure_state_layout()
    return paths


@pytest.fixture
def fake_embedder():
    from _helpers.fake_embedder import FakeEmbedder

    return FakeEmbedder(dim=16)


@pytest.fixture
def st_embedder():
    """Real sentence-transformers embedder. Lazily loaded once per session."""
    from rag_mcp.infrastructure.embedder_st import SentenceTransformersEmbedder

    enc = SentenceTransformersEmbedder("intfloat/multilingual-e5-small")
    _ = enc.dim  # eager load
    return enc
