"""Unit tests for :mod:`rag_mcp.infrastructure.probes_json`."""

from __future__ import annotations

from pathlib import Path

import pytest

from rag_mcp.domain.models import Probe
from rag_mcp.infrastructure import probes_json


def test_load_returns_empty_when_file_missing(tmp_path: Path) -> None:
    probes_file = tmp_path / "probes.json"
    assert probes_json.load(probes_file) == ()


def test_save_then_load_roundtrip(tmp_path: Path) -> None:
    probes_file = tmp_path / "probes.json"
    payload = [
        Probe(id="auth-flow", query="What is the project's authentication flow?", note="onboarding"),
        Probe(id="payment_state", query="payment status diagram", note=""),
    ]
    probes_json.save(probes_file, payload)
    loaded = probes_json.load(probes_file)
    assert loaded == tuple(payload)


def test_save_creates_parent_dir(tmp_path: Path) -> None:
    deep = tmp_path / "nested" / ".noory/rag" / "probes.json"
    probes_json.save(deep, [Probe(id="x", query="y")])
    assert deep.is_file()


def test_load_rejects_invalid_json(tmp_path: Path) -> None:
    probes_file = tmp_path / "probes.json"
    probes_file.write_text("not json{", encoding="utf-8")
    with pytest.raises(probes_json.ProbesError):
        probes_json.load(probes_file)


def test_load_rejects_invalid_schema(tmp_path: Path) -> None:
    probes_file = tmp_path / "probes.json"
    probes_file.write_text('{"probes": [{"id": "ok"}]}', encoding="utf-8")  # missing query
    with pytest.raises(probes_json.ProbesError):
        probes_json.load(probes_file)


def test_save_rejects_duplicate_ids(tmp_path: Path) -> None:
    probes_file = tmp_path / "probes.json"
    with pytest.raises(probes_json.ProbesError, match="duplicate"):
        probes_json.save(
            probes_file,
            [Probe(id="dup", query="a"), Probe(id="dup", query="b")],
        )


def test_save_rejects_blank_query(tmp_path: Path) -> None:
    probes_file = tmp_path / "probes.json"
    with pytest.raises(probes_json.ProbesError):
        probes_json.save(probes_file, [Probe(id="x", query="   ")])


def test_save_rejects_bad_id_pattern(tmp_path: Path) -> None:
    probes_file = tmp_path / "probes.json"
    for bad_id in ("with space", "café", "--leading-dash", ""):
        with pytest.raises(probes_json.ProbesError):
            probes_json.save(probes_file, [Probe(id=bad_id, query="q")])


def test_validate_payload_accepts_dict_form() -> None:
    out = probes_json.validate_payload(
        {"probes": [{"id": "ok", "query": "Q"}, {"id": "ok-2", "query": "Q2", "note": "n"}]}
    )
    assert len(out) == 2
    assert out[0].id == "ok"
    assert out[1].note == "n"


def test_validate_payload_unknown_keys_default_to_empty() -> None:
    """Pydantic default ignores unknown keys → result is an empty tuple.

    The MCP `rag_set_probes` tool always passes `{"probes": [...]}` so this
    permissive behavior is acceptable; the alternative (strict reject) would
    just make future schema migrations noisier.
    """
    assert probes_json.validate_payload({"items": []}) == ()
