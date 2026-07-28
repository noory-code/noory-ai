"""Single filesystem boundary for locating Stage record files."""

from __future__ import annotations

from pathlib import Path


def record_paths(
    root: Path, *, pattern: str = "*.md", recursive: bool = False
) -> tuple[Path, ...]:
    """Return Markdown records in deterministic order using the current flat layout."""

    paths = root.rglob(pattern) if recursive else root.glob(pattern)
    return tuple(sorted(paths))


def record_path(root: Path, record_id: str) -> Path:
    """Return the current flat-layout path for one record ID."""

    return root / f"{record_id}.md"
