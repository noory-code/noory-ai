"""Single filesystem boundary for locating Stage record files."""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path


FRONTMATTER_ID_RE = re.compile(r"^id:[ \t]*(?P<record_id>\S+)[ \t]*$", re.MULTILINE)
EPIC_RECORD_NAME = "_epic.md"
STORY_RECORD_NAME = "_story.md"


def record_paths(root: Path, *, pattern: str = "*.md") -> tuple[Path, ...]:
    """Return records below one declared root in deterministic order.

    Recursion is boundary policy: callers cannot accidentally choose a flat scan
    after work records gain epic and story directories. Root-level underscore
    files are copyable templates; underscore records below a hierarchy root are
    real ``_epic.md`` and ``_story.md`` records.
    """

    candidates = (
        path
        for path in root.rglob("*.md")
        if path.parent != root or not path.name.startswith("_")
    )
    if pattern == "*.md":
        return tuple(sorted(candidates))

    matches = []
    for path in candidates:
        if fnmatch.fnmatchcase(path.name, pattern):
            matches.append(path)
            continue
        text = path.read_text(encoding="utf-8")
        identity = FRONTMATTER_ID_RE.search(text)
        if (
            identity is not None
            and fnmatch.fnmatchcase(f"{identity.group('record_id')}.md", pattern)
        ):
            matches.append(path)
    return tuple(sorted(matches))


def record_path(root: Path, record_id: str) -> Path:
    """Resolve one record ID across flat and hierarchical layouts.

    The flat fallback preserves creation callers until registration becomes
    hierarchy-aware. Existing records are found by their frontmatter identity,
    because epic and story records have fixed filenames. Relative roots are
    path-calculation inputs, not filesystem search roots, so their result never
    depends on the process working directory.
    """

    if not root.is_absolute():
        return root / f"{record_id}.md"

    matches = []
    for path in record_paths(root):
        if path.name == f"{record_id}.md":
            matches.append(path)
            continue
        text = path.read_text(encoding="utf-8")
        match = FRONTMATTER_ID_RE.search(text)
        if match is not None and match.group("record_id") == record_id:
            matches.append(path)
    if len(matches) > 1:
        rendered = ", ".join(path.as_posix() for path in matches)
        raise ValueError(f"record id {record_id!r} resolves to multiple paths: {rendered}")
    if matches:
        return matches[0]
    return root / f"{record_id}.md"


def top_level_item_path(root: Path, record: Path) -> Path:
    """Return the whole lifecycle move unit containing ``record``."""

    try:
        relative = record.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"record is outside its lifecycle root: {record}") from exc
    if not relative.parts:
        raise ValueError("record path must be below its lifecycle root")
    return root / relative.parts[0]


def work_record_scale(root: Path, record: Path) -> str:
    """Return the scale encoded by one hierarchical work-record path.

    A root-level Markdown file is the legacy flat shape. Callers may continue
    reading that shape during the schema-v5 rollout, but new hierarchy-aware
    writes can reject it explicitly.
    """

    try:
        relative = record.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"record is outside its lifecycle root: {record}") from exc
    parts = relative.parts
    if len(parts) == 1 and record.suffix == ".md":
        return "legacy"
    if record.name == EPIC_RECORD_NAME and len(parts) == 2:
        return "epic"
    if record.name == STORY_RECORD_NAME and len(parts) in {2, 3}:
        return "story"
    if (
        record.suffix == ".md"
        and not record.name.startswith("_")
        and len(parts) in {2, 3}
    ):
        return "action"
    raise ValueError(f"work record has no valid epic/story/action location: {record}")


def hierarchy_parent_record_path(root: Path, record: Path) -> Path | None:
    """Return the parent record encoded by ``record``'s folder path."""

    scale = work_record_scale(root, record)
    relative = record.relative_to(root)
    if scale in {"epic", "legacy"}:
        return None
    if scale == "story":
        if len(relative.parts) == 2:
            return None
        return root / relative.parts[0] / EPIC_RECORD_NAME
    return record.parent / STORY_RECORD_NAME
