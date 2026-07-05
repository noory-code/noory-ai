"""Deterministic stand-in for :class:`EmbedderPort` used in unit tests.

Maps text to a fixed-dimensional unit vector via character-bucket counts.
Identical input → identical output. Different texts produce different
vectors. No model download required.
"""

from __future__ import annotations

import numpy as np


class FakeEmbedder:
    def __init__(self, dim: int = 16):
        self._dim = int(dim)

    @property
    def dim(self) -> int:
        return self._dim

    def _vec(self, text: str) -> np.ndarray:
        v = np.zeros(self._dim, dtype=np.float32)
        sample = text[:2048]
        for ch in sample:
            v[ord(ch) % self._dim] += 1.0
        norm = float(np.linalg.norm(v))
        if norm > 0:
            v /= norm
        return v

    def encode_passages(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self._dim), dtype=np.float32)
        return np.stack([self._vec(t) for t in texts])

    def encode_query(self, text: str) -> np.ndarray:
        return self._vec(text)
