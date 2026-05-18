"""v0.18.0 Phase 3 (D-2026-05-16-E) — per-node publish MD renderer.

Phase 3 emits a per-node ``published/{kind}-{slug}-{version}.md`` file
on every Publish action. This module owns the render. The shape is
**uniform across all 15 kinds**:

- YAML frontmatter with exactly 7 keys:
  ``id`` / ``kind`` / ``version`` / ``label`` / ``parent_id`` /
  ``canvas`` / ``published_at``
- One H2 section per declared typed field on the per-kind Pydantic
  class (skipping the ``BaseNodeFields`` graph layer and the
  ``kind`` discriminator). Field name is converted snake_case →
  Title Case for the heading; the value is rendered verbatim if it
  is a string, or as inline YAML otherwise (``int`` / ``dict`` /
  ``Optional[Literal]`` etc.).
- Empty fields still emit the heading with an empty body — keeps
  the per-kind MD shape stable across publish versions
  (diff-friendly).

Separated from the legacy ``md_template.py`` (still bound to the
v0.17 absorb path) so the two render rules cannot drift.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from plot_mcp.models import BaseNodeFields, SketchNode

# Frontmatter key order — pinned. Phase 4 / 5 parsers depend on the
# YAML round-trip; do not reorder without a fresh D-entry.
_FRONTMATTER_KEYS: tuple[str, ...] = (
    "id",
    "kind",
    "version",
    "label",
    "parent_id",
    "canvas",
    "published_at",
)

# Fields on ``BaseNodeFields`` are graph-layer; they're carried in the
# YAML frontmatter (``id`` / ``parent_id``) and on canvas.json itself,
# not as MD H2 sections.
_BASE_FIELD_NAMES: frozenset[str] = frozenset(BaseNodeFields.model_fields.keys())


def _snake_to_title(field: str) -> str:
    """``what_we_do`` → ``What we do``; ``dont`` → ``Dont``;
    ``actor_permissions`` → ``Actor permissions``.

    Lowercase 'd', 'o', 'n', 't' on the second through final words —
    we render the field exactly as it appears on the Pydantic class
    (no spelling normalisation; ``dont`` stays ``Dont``)."""
    parts = field.split("_")
    if not parts:
        return field
    head, *rest = parts
    return " ".join([head.capitalize(), *rest])


def _kind_typed_fields(node: SketchNode) -> list[str]:
    """Per-kind typed fields in declaration order, skipping
    ``BaseNodeFields`` graph fields and the ``kind`` discriminator."""
    return [
        name
        for name in node.__class__.model_fields.keys()
        if name not in _BASE_FIELD_NAMES and name != "kind"
    ]


def _render_field_value(value: Any) -> str:
    """Render the body of one H2 section.

    - String → verbatim (preserves MD newlines / Markdown syntax).
    - Anything else → inline YAML on one or more lines (round-trip).
    - None / empty string / empty dict → empty body (heading only).
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    # YAML scalars (int / float / bool) emit cleanly via ``str()``; the
    # ``yaml.safe_dump`` path appends a document-end ``...`` marker on
    # top-level scalars, which is noise here. Reserve YAML dump for
    # structured values (dict / list).
    if isinstance(value, int | float | bool):
        return str(value)
    dumped: str = yaml.safe_dump(value, allow_unicode=True, sort_keys=False)
    return dumped.rstrip()


def render_node_md(node: SketchNode, *, canvas: str) -> str:
    """Return the MD file contents for ``node`` published from
    ``canvas``. ``node.version`` is the version of the publish;
    callers bump it before passing in.

    Output ends with a single trailing newline (POSIX text file
    convention)."""
    frontmatter: dict[str, Any] = {
        "id": node.id,
        "kind": node.kind,
        "version": node.version,
        "label": node.label,
        "parent_id": node.parent_id,
        "canvas": canvas,
        "published_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    # Re-pack in canonical key order (PyYAML preserves insertion order
    # under sort_keys=False).
    ordered = {k: frontmatter[k] for k in _FRONTMATTER_KEYS}
    fm_yaml = yaml.safe_dump(ordered, allow_unicode=True, sort_keys=False).rstrip()

    parts: list[str] = [
        "---",
        fm_yaml,
        "---",
        "",
    ]
    for field in _kind_typed_fields(node):
        value = getattr(node, field)
        body = _render_field_value(value)
        parts.append(f"## {_snake_to_title(field)}")
        parts.append("")
        if body:
            parts.append(body)
            parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def published_md_path(canvas_dir: Path, *, kind: str, node_id: str, version: str) -> Path:
    """Resolve the absolute path for a published node's MD file.

    Pattern (v0.24.3, D-2026-05-18-A): ``<canvas_dir>/published/<kind>/<node_id>/<version>.md``.
    Node ``id`` is the stable SSOT (never renames), and Plot's id
    policy nudges users to ASCII — both yield clean ASCII folder
    names. Pre-v0.24.3 used ``slugify(label)`` which could create
    Korean / CJK folder names; the user requested ASCII-only paths.

    Migration paths handled in folder_io.py:
      - Pre-v0.23.0 flat (``<kind>-<slug>-<version>.md``) → covered
        by ``_migrate_published_flat_to_kind_slug`` (still runs on
        first read for back-compat).
      - v0.23.x slug-folder (``<kind>/<slug>/<version>.md``) →
        ``_migrate_published_slug_to_id`` walks the canvas and
        renames each ``<slug>`` folder to ``<node_id>``."""
    return canvas_dir / "published" / kind / node_id / f"{version}.md"


# ---------------------------------------------------------------------------
# Eligibility (mirror in viewer/src/domain/publishEligibility.ts)
# ---------------------------------------------------------------------------


_REF_KINDS: frozenset[str] = frozenset({"actor_ref", "mission_ref", "value_ref", "identity_ref"})


def can_publish(node: SketchNode) -> bool:
    """Return True iff ``node`` is publish-eligible.

    Hidden (returns False) for:
    - ``project`` anchor (mirrors ProjectDoc.name, not its own SSOT).
    - ``service`` with ``is_root`` (ServiceDetail mirror of a
      Services-canvas master; the master gets published, the mirror
      follows). v0.24.10 / D-2026-05-19-C narrowed this from
      "all is_root" to "service is_root only" so that actor masters
      (Bana / Admin / Guest) can publish their own typed text directly.
    - ``*_ref`` kinds (aliases; publish the referent instead).

    All other kinds + non-root nodes return True. ``actor`` is_root
    is now eligible (own version, direct publish; Phase 5 referent
    flow will layer cross-canvas referent updates on top)."""
    if node.kind == "project":
        return False
    if node.is_root and node.kind == "service":
        return False
    if node.kind in _REF_KINDS:
        return False
    return True


def bump_major(version: str) -> str:
    """Increment the MAJOR component of a ``v<MAJOR>.<MINOR>`` string;
    reset MINOR to 0. ``v1.0`` → ``v2.0``; ``v1.3`` → ``v2.0``.

    Caller has already validated the format via
    ``BaseNodeFields._version_is_valid``; we still re-parse here as a
    Fail-Fast guard.
    """
    if not (version.startswith("v") and "." in version):
        raise ValueError(f"bump_major: invalid version format {version!r}")
    major_str, _minor_str = version[1:].split(".", 1)
    return f"v{int(major_str) + 1}.0"


def bump_minor(version: str) -> str:
    """Increment the MINOR component of a ``v<MAJOR>.<MINOR>`` string;
    leave MAJOR unchanged. ``v1.0`` → ``v1.1``; ``v2.3`` → ``v2.4``.

    Used by Phase 4 (D-2026-05-17-C) when a descendant publishes and
    its ancestor chain is silently bumped — the ancestor's content did
    not change, so MAJOR stays put.
    """
    if not (version.startswith("v") and "." in version):
        raise ValueError(f"bump_minor: invalid version format {version!r}")
    major_str, minor_str = version[1:].split(".", 1)
    return f"v{int(major_str)}.{int(minor_str) + 1}"
