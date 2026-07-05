"""Unit tests for :mod:`rag_mcp.infrastructure.manifest_json`."""

from __future__ import annotations

from pathlib import Path

from rag_mcp.infrastructure.manifest_json import JsonManifest, diff_maps, hash_file


def test_hash_file_is_stable(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("hello world")
    h1 = hash_file(f)
    h2 = hash_file(f)
    assert h1 == h2
    assert len(h1) == 64


def test_hash_file_changes_on_edit(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("alpha")
    before = hash_file(f)
    f.write_text("beta")
    assert before != hash_file(f)


def test_diff_added_changed_removed() -> None:
    prev = {"a.md": "1", "b.md": "2", "c.md": "3"}
    cur = {"a.md": "1", "b.md": "9", "d.md": "4"}
    diff = diff_maps(cur, prev)
    assert list(diff.added) == ["d.md"]
    assert list(diff.changed) == ["b.md"]
    assert list(diff.removed) == ["c.md"]


def test_jsonmanifest_roundtrip(tmp_path: Path) -> None:
    file = tmp_path / "manifest.json"
    m = JsonManifest(file)
    assert m.load() == {}
    m.save({"a": "h1", "b": "h2"})
    again = JsonManifest(file).load()
    assert again == {"a": "h1", "b": "h2"}


def test_jsonmanifest_corrupt_json_degrades_but_is_flagged(tmp_path: Path) -> None:
    file = tmp_path / "manifest.json"
    file.write_text("{not valid json", encoding="utf-8")
    m = JsonManifest(file)
    assert m.load() == {}
    assert m.corrupt_detected is True
    # A clean save/load cycle clears the flag.
    m.save({"a": "1"})
    assert m.load() == {"a": "1"}
    assert m.corrupt_detected is False


def test_jsonmanifest_non_object_payload_degrades_but_is_flagged(tmp_path: Path) -> None:
    file = tmp_path / "manifest.json"
    file.write_text("[1, 2, 3]", encoding="utf-8")  # valid JSON, wrong shape
    m = JsonManifest(file)
    assert m.load() == {}
    assert m.corrupt_detected is True


def test_jsonmanifest_clean_load_does_not_flag(tmp_path: Path) -> None:
    file = tmp_path / "manifest.json"
    m = JsonManifest(file)
    assert m.load() == {}  # absent file is not corruption
    assert m.corrupt_detected is False


def test_jsonmanifest_diff(tmp_path: Path) -> None:
    file = tmp_path / "manifest.json"
    m = JsonManifest(file)
    m.save({"a": "1", "b": "2"})
    diff = m.diff({"a": "1", "b": "9", "c": "3"})
    assert list(diff.added) == ["c"]
    assert list(diff.changed) == ["b"]
    assert list(diff.removed) == []
