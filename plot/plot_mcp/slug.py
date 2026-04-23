"""Folder-path slug for node → folder mapping (v0.7).

Produces the relative path used by ``SketchNode.folder_path``. The rule is
deliberately mechanical so both sides (Python server, TypeScript client)
can compute it independently: ``workspace/{canvas}/{kind}-{label-slug}/``.

Korean and other non-ASCII characters are preserved — they work fine on
every modern filesystem and they read better than transliteration.
"""

from __future__ import annotations

import re

# Non-Korean letter ranges we want to preserve. Keep it inclusive: Latin
# letters+digits, Hangul (AC00–D7AF for syllables, 1100–11FF for jamo,
# A960–A97F extended), CJK in case user mixes. Everything else collapses
# to a single dash.
_PRESERVE_RE = re.compile(
    r"[^a-z0-9"
    r"가-힯"
    r"ᄀ-ᇿ"
    r"ꥠ-꥿"
    r"぀-ヿ"  # Hiragana/Katakana — may as well
    r"一-鿿"  # CJK Unified
    r"]+",
    re.IGNORECASE,
)


def slugify(text: str) -> str:
    """Lowercase ASCII letters/digits, preserve Korean/CJK, collapse
    everything else to single dashes, trim leading/trailing dashes."""
    lowered = text.lower().strip()
    replaced = _PRESERVE_RE.sub("-", lowered)
    return replaced.strip("-")


def folder_slug(kind: str, label: str, canvas: str = "core") -> str:
    """Compose a ``workspace/{canvas}/{kind}-{label}`` relative folder path.

    Called by both server and client to agree on the default location for a
    new node's folder. The server then uniquifies if taken.
    """
    kind_slug = slugify(kind) or "node"
    label_slug = slugify(label)
    stem = f"{kind_slug}-{label_slug}" if label_slug else kind_slug
    canvas_slug = slugify(canvas) or "core"
    return f"workspace/{canvas_slug}/{stem}"
