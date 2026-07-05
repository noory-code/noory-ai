"""Unit tests for :mod:`rag_mcp.infrastructure.sources_fs`."""

from __future__ import annotations

from pathlib import Path

import pytest

from rag_mcp.domain.models import SourceSpec
from rag_mcp.infrastructure.sources_fs import FilesystemSources


def _make_tree(root: Path) -> None:
    (root / "docs").mkdir()
    (root / "docs" / "a.md").write_text("# A")
    (root / "docs" / "b.txt").write_text("B")
    (root / "docs" / "sub").mkdir()
    (root / "docs" / "sub" / "c.md").write_text("# C")
    (root / "docs" / "sub" / "ignore.log").write_text("noise")
    (root / "README.md").write_text("# README")
    (root / "node_modules").mkdir()
    (root / "node_modules" / "pkg.md").write_text("should be excluded")


def test_walk_includes_recursive_by_default(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    src = SourceSpec(path="docs/", recursive=True, include=("**/*.md",))
    fs = FilesystemSources(tmp_path)
    found = [fs.rel_to_project(p) for p in fs.walk([src])]
    assert found == ["docs/a.md", "docs/sub/c.md"]


def test_walk_non_recursive_skips_subdirs(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    src = SourceSpec(path="docs/", recursive=False, include=("**/*.md",))
    fs = FilesystemSources(tmp_path)
    found = [fs.rel_to_project(p) for p in fs.walk([src])]
    assert found == ["docs/a.md"]


def test_walk_excludes_patterns(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    src = SourceSpec(
        path="docs/",
        recursive=True,
        include=("**/*.md",),
        exclude=("**/sub/*",),
    )
    fs = FilesystemSources(tmp_path)
    found = [fs.rel_to_project(p) for p in fs.walk([src])]
    assert found == ["docs/a.md"]


def test_walk_single_file_source(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    src = SourceSpec(path="README.md", include=(), exclude=())
    fs = FilesystemSources(tmp_path)
    found = [fs.rel_to_project(p) for p in fs.walk([src])]
    assert found == ["README.md"]


def test_walk_rejects_escape(tmp_path: Path) -> None:
    src = SourceSpec(path="../etc/", recursive=True, include=("**/*",))
    fs = FilesystemSources(tmp_path)
    with pytest.raises(ValueError):
        fs.walk([src])
