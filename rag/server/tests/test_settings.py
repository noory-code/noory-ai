"""Unit tests for :mod:`rag_mcp.infrastructure.settings_json`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rag_mcp.infrastructure.settings_json import (
    DEFAULT_EMBED_DIM,
    DEFAULT_EMBED_MODEL,
    SettingsError,
    default_settings,
    load,
    save,
    validate_dict,
)


def test_default_settings_has_raw_source() -> None:
    s = default_settings()
    assert len(s.sources) == 1
    assert s.sources[0].path == ".noory/rag/raw/"
    assert s.embedding.model == DEFAULT_EMBED_MODEL
    assert s.embedding.dim == DEFAULT_EMBED_DIM


def test_save_load_roundtrip(tmp_path: Path) -> None:
    file = tmp_path / "settings.json"
    save(file, default_settings())
    loaded = load(file)
    assert loaded.sources[0].path == ".noory/rag/raw/"
    assert loaded.embedding.dim == DEFAULT_EMBED_DIM


def test_load_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(SettingsError):
        load(tmp_path / "nope.json")


def test_invalid_chunking_rejected() -> None:
    bad = {
        "sources": [{"path": ".noory/rag/raw/"}],
        "chunking": {"target_tokens": 800, "max_tokens": 100, "min_tokens": 50},
    }
    with pytest.raises(SettingsError):
        validate_dict(bad)


@pytest.mark.parametrize(
    "patch",
    [
        {"embedding": {"provider": "local", "model": "fake", "dim": 0}},
        {"chunking": {"target_tokens": 0, "max_tokens": 800, "min_tokens": 100}},
        {"chunking": {"target_tokens": 400, "max_tokens": 800, "min_tokens": 0}},
        {"chunking": {"target_tokens": 400, "max_tokens": 800, "min_tokens": 500}},
        {"graph": {"expand_depth": -1, "community_algo": "leiden"}},
    ],
)
def test_invalid_numeric_bounds_rejected(patch: dict) -> None:
    bad = {"sources": [{"path": ".noory/rag/raw/"}], **patch}
    with pytest.raises(SettingsError):
        validate_dict(bad)


def test_load_corrupt_json(tmp_path: Path) -> None:
    file = tmp_path / "settings.json"
    file.write_text("{not json")
    with pytest.raises(SettingsError):
        load(file)


def test_to_dict_is_json_serialisable() -> None:
    s = default_settings()
    js = json.dumps(s.to_dict())
    again = validate_dict(json.loads(js))
    assert again.embedding.model == s.embedding.model
