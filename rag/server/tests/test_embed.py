"""Real-model unit test for :class:`SentenceTransformersEmbedder`.

Downloads ``intfloat/multilingual-e5-small`` on first run (cached under
``~/.cache/huggingface``). Marked ``slow`` so it can be skipped via
``pytest -k 'not slow'`` when iterating quickly.
"""

from __future__ import annotations

import numpy as np
import pytest

from rag_mcp.infrastructure.embedder_st import SentenceTransformersEmbedder

pytestmark = pytest.mark.slow


def test_dim_matches_expected() -> None:
    enc = SentenceTransformersEmbedder("intfloat/multilingual-e5-small")
    assert enc.dim == 384


def test_encode_passages_shape_and_normalisation() -> None:
    enc = SentenceTransformersEmbedder("intfloat/multilingual-e5-small")
    arr = enc.encode_passages(["hello world", "hello there"])
    assert arr.shape == (2, 384)
    norms = np.linalg.norm(arr, axis=1)
    np.testing.assert_allclose(norms, np.ones(2), atol=1e-3)


def test_encode_query_is_deterministic() -> None:
    enc = SentenceTransformersEmbedder("intfloat/multilingual-e5-small")
    a = enc.encode_query("riverpod provider pattern")
    b = enc.encode_query("riverpod provider pattern")
    np.testing.assert_allclose(a, b, atol=1e-6)


def test_encode_passages_empty_returns_zero_rows() -> None:
    enc = SentenceTransformersEmbedder("intfloat/multilingual-e5-small")
    arr = enc.encode_passages([])
    assert arr.shape == (0, 384)
