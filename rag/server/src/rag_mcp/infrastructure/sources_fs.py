"""Filesystem implementation of :class:`SourcesPort`."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Iterator

from ..domain.models import SourceSpec
from .manifest_json import hash_file


@lru_cache(maxsize=256)
def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a forward-slash glob to a regex matching the whole path.

    Supports:
      ``*``   – any chars except ``/``
      ``**``  – zero or more path segments (with a trailing ``/`` consumed too)
      ``?``   – single char except ``/``
    """
    out: list[str] = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c == "*" and i + 1 < n and pattern[i + 1] == "*":
            if i + 2 < n and pattern[i + 2] == "/":
                out.append("(?:.*/)?")
                i += 3
            else:
                out.append(".*")
                i += 2
        elif c == "*":
            out.append("[^/]*")
            i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def _matches_any(rel: str, patterns: tuple[str, ...]) -> bool:
    normalised = rel.replace("\\", "/")
    return any(_glob_to_regex(p).match(normalised) for p in patterns)


def _walk_source(source: SourceSpec, project_root: Path) -> Iterator[Path]:
    base = (project_root / source.path).resolve()
    try:
        base.relative_to(project_root.resolve())
    except ValueError:
        raise ValueError(f"source path escapes project root: {source.path}")
    if not base.exists():
        return
    if base.is_file():
        yield base
        return
    if not source.recursive:
        for child in sorted(base.iterdir()):
            if child.is_file():
                yield child
        return
    for path in sorted(base.rglob("*")):
        if path.is_file():
            yield path


class FilesystemSources:
    """Concrete adapter that walks the local filesystem."""

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()

    def walk(self, sources: list[SourceSpec]) -> list[Path]:
        seen: set[Path] = set()
        out: list[Path] = []
        for source in sources:
            base = (self.project_root / source.path).resolve()
            base_is_dir = base.is_dir()
            for path in _walk_source(source, self.project_root):
                rel_from_base = (
                    str(path.relative_to(base)) if base_is_dir else path.name
                )
                if source.include and not _matches_any(rel_from_base, source.include):
                    continue
                if source.exclude and _matches_any(rel_from_base, source.exclude):
                    continue
                if path in seen:
                    continue
                seen.add(path)
                out.append(path)
        out.sort()
        return out

    def rel_to_project(self, path: Path) -> str:
        return str(path.resolve().relative_to(self.project_root)).replace("\\", "/")

    def hash_file(self, path: Path) -> str:
        return hash_file(path)
