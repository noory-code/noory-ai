"""Pure value objects shared by the domain and the use cases."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# --------------------------------------------------------- input value objects


@dataclass(frozen=True)
class ChunkData:
    """A single text chunk that will be embedded and indexed."""

    text: str
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EntityData:
    """An entity extracted from one or more chunks of a single document."""

    id: str
    name: str
    type: str
    chunk_indices: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class RelationData:
    """A relation between two entities (by id)."""

    src_id: str
    dst_id: str
    type: str = "RELATED_TO"
    weight: float = 1.0


@dataclass(frozen=True)
class SourceSpec:
    """A configured source path with include/exclude patterns."""

    path: str
    recursive: bool = True
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()


@dataclass(frozen=True)
class Probe:
    """A representative user question used to evaluate indexing quality.

    Stored in `.noory/rag/probes.json` (per-project, gitignored by default).
    Indexing/searching never reads probes — they are purely a measurement
    aid that the user manages via `/rag:rag-probe-*` skills.
    """

    id: str
    query: str
    note: str = ""


# -------------------------------------------------------- output value objects


@dataclass(frozen=True)
class SearchHit:
    chunk_id: int
    rel_path: str
    chunk_idx: int
    text: str
    meta: dict[str, Any]
    distance: float


@dataclass(frozen=True)
class EntityRow:
    id: str
    name: str
    type: str
    community_id: int | None = None
    summary: str = ""


@dataclass
class Subgraph:
    nodes: list[EntityRow] = field(default_factory=list)
    edges: list[tuple[str, str, str, float]] = field(default_factory=list)


@dataclass(frozen=True)
class FileDiff:
    added: tuple[str, ...]
    changed: tuple[str, ...]
    removed: tuple[str, ...]

    def is_empty(self) -> bool:
        return not (self.added or self.changed or self.removed)

    def to_dict(self) -> dict[str, list[str]]:
        return {
            "added": list(self.added),
            "changed": list(self.changed),
            "removed": list(self.removed),
        }
