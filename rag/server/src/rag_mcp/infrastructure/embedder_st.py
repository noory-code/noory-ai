"""sentence-transformers adapter implementing :class:`EmbedderPort`."""

from __future__ import annotations

import numpy as np

_MODEL_CACHE: dict[str, object] = {}


def _is_e5(model_name: str) -> bool:
    return "multilingual-e5" in model_name or "/e5-" in model_name


def _load_model(model_name: str) -> object:
    cached = _MODEL_CACHE.get(model_name)
    if cached is not None:
        return cached
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    _MODEL_CACHE[model_name] = model
    return model


class SentenceTransformersEmbedder:
    """Local embedding model. Lazily loads on first encode call."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self._model: object | None = None
        self._dim: int | None = None

    def _ensure(self) -> object:
        if self._model is None:
            model = _load_model(self.model_name)
            self._model = model
            getter = (
                getattr(model, "get_embedding_dimension", None)
                or getattr(model, "get_sentence_embedding_dimension", None)
            )
            self._dim = int(getter() or 0) if getter else 0  # type: ignore[misc]
        return self._model

    @property
    def dim(self) -> int:
        if self._dim is None:
            self._ensure()
        assert self._dim is not None
        return self._dim

    def _encode(self, payload: list[str]) -> np.ndarray:
        model = self._ensure()
        arr = model.encode(  # type: ignore[attr-defined]
            payload,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return np.asarray(arr, dtype=np.float32)

    def encode_passages(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        payload = [f"passage: {t}" for t in texts] if _is_e5(self.model_name) else texts
        return self._encode(payload)

    def encode_query(self, text: str) -> np.ndarray:
        payload = [f"query: {text}"] if _is_e5(self.model_name) else [text]
        return self._encode(payload)[0]
