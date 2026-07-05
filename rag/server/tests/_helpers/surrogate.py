"""Deterministic chunker + entity/relation extractor for integration tests.

In production these jobs are performed by Claude (the calling LLM). The
surrogate gives tests a realistic-shaped feed without requiring an LLM
call, by leaning on markdown structure and simple regex heuristics.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Iterable

from rag_mcp.domain.models import ChunkData, EntityData, RelationData

H2_OR_H3 = re.compile(r"^(##|###)\s+(.*)$", re.MULTILINE)
GUIDE_LIB = re.compile(r"\bguide-lib-([a-z][a-z0-9-]*)\b", re.IGNORECASE)
LIB_HINT = re.compile(r"\b([A-Za-z][A-Za-z0-9_]+)\.dart\b")
HEADING_WORDS = re.compile(r"#{1,3}\s+([A-Za-z\uac00-\ud7a3][\w\-_/.]+)")


def _stable_id(*parts: str) -> str:
    h = hashlib.sha1("\x1f".join(parts).encode("utf-8")).hexdigest()[:16]
    return h


def chunk_markdown(text: str, *, max_chars: int = 1600) -> list[ChunkData]:
    """Split markdown text into chunks on H2/H3 boundaries.

    Falls back to a single chunk if no headings are present. Each chunk is
    capped at ``max_chars`` (excess goes into a follow-on chunk).
    """
    if not text.strip():
        return []

    positions = [(m.start(), m.group(0)) for m in H2_OR_H3.finditer(text)]
    if not positions:
        slices = _split_by_size(text, max_chars)
        return [
            ChunkData(text=s, meta={"section": "_prelude_", "part": i})
            for i, s in enumerate(slices)
        ]

    if positions[0][0] > 0:
        positions.insert(0, (0, ""))

    chunks: list[ChunkData] = []
    for i, (start, heading) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        body = text[start:end].strip()
        if not body:
            continue
        section = heading.strip().lstrip("#").strip() or "_prelude_"
        for j, piece in enumerate(_split_by_size(body, max_chars)):
            chunks.append(
                ChunkData(text=piece, meta={"section": section, "part": j})
            )
    return chunks


def _split_by_size(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    out: list[str] = []
    lines = text.splitlines(keepends=True)
    buf: list[str] = []
    size = 0
    for line in lines:
        if size + len(line) > max_chars and buf:
            out.append("".join(buf).rstrip())
            buf = [line]
            size = len(line)
        else:
            buf.append(line)
            size += len(line)
    if buf:
        out.append("".join(buf).rstrip())
    return out


@dataclass(frozen=True)
class Extracted:
    entities: list[EntityData]
    relations: list[RelationData]


def extract_from_chunks(rel_path: str, chunks: list[ChunkData]) -> Extracted:
    """Pull crude entities/relations from markdown chunks.

    Heuristics (deterministic):
      - ``guide-lib-<lib>`` slugs and ``<libname>`` headings → `library` entities
      - ``Something.dart`` tokens → `module` entities
      - Co-occurrence within the same chunk → ``RELATED_TO`` edges
    """
    entity_chunks: dict[str, set[int]] = {}
    entity_names: dict[str, tuple[str, str]] = {}  # id -> (name, type)

    def _register(name: str, etype: str, chunk_idx: int) -> str:
        ident = _stable_id(etype, name.lower())
        entity_chunks.setdefault(ident, set()).add(chunk_idx)
        entity_names.setdefault(ident, (name, etype))
        return ident

    pair_weights: dict[tuple[str, str], int] = {}
    for idx, chunk in enumerate(chunks):
        local_ids: set[str] = set()
        for m in GUIDE_LIB.finditer(chunk.text):
            local_ids.add(_register(m.group(1).lower(), "library", idx))
        for m in LIB_HINT.finditer(chunk.text):
            local_ids.add(_register(m.group(1), "module", idx))
        for m in HEADING_WORDS.finditer(chunk.text):
            token = m.group(1)
            if len(token) > 2 and not token.startswith("/"):
                local_ids.add(_register(token, "topic", idx))

        local_list = sorted(local_ids)
        for i in range(len(local_list)):
            for j in range(i + 1, len(local_list)):
                key = (local_list[i], local_list[j])
                pair_weights[key] = pair_weights.get(key, 0) + 1

    entities = [
        EntityData(
            id=ident,
            name=entity_names[ident][0],
            type=entity_names[ident][1],
            chunk_indices=sorted(entity_chunks[ident]),
        )
        for ident in sorted(entity_chunks.keys())
    ]
    relations = [
        RelationData(src_id=a, dst_id=b, type="RELATED_TO", weight=float(w))
        for (a, b), w in sorted(pair_weights.items())
    ]
    return Extracted(entities=entities, relations=relations)


def chunk_and_extract(rel_path: str, text: str) -> tuple[list[ChunkData], Extracted]:
    chunks = chunk_markdown(text)
    ext = extract_from_chunks(rel_path, chunks)
    return chunks, ext


def files_under(root_path, patterns: Iterable[str] = ("**/*.md",)) -> list:
    from pathlib import Path

    root = Path(root_path)
    out: list = []
    for pat in patterns:
        for p in sorted(root.glob(pat)):
            if p.is_file():
                out.append(p)
    return out
