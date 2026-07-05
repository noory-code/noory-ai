"""Ports (interfaces) that infrastructure adapters implement.

Application use cases depend on these Protocols — never on concrete
adapters. This is the Dependency Inversion seam.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

import numpy as np

from .models import ChunkData, EntityRow, FileDiff, SearchHit, SourceSpec, Subgraph


@runtime_checkable
class EmbedderPort(Protocol):
    @property
    def dim(self) -> int: ...

    def encode_passages(self, texts: list[str]) -> np.ndarray: ...

    def encode_query(self, text: str) -> np.ndarray: ...


@runtime_checkable
class VectorIndexPort(Protocol):
    def add_file(
        self,
        rel_path: str,
        chunks: list[ChunkData],
        embeddings: np.ndarray,
    ) -> list[int]: ...

    def delete_file(self, rel_path: str) -> int: ...

    def search(self, query_vec: np.ndarray, k: int = 8) -> list[SearchHit]: ...

    def list_files(self) -> list[str]: ...

    def stats(self) -> dict[str, int]: ...

    def close(self) -> None: ...


@runtime_checkable
class GraphIndexPort(Protocol):
    def upsert_chunk(self, chunk_id: str, rel_path: str, chunk_idx: int) -> None: ...

    def delete_chunks_by_path(self, rel_path: str) -> None: ...

    def upsert_entity(
        self,
        entity_id: str,
        name: str,
        etype: str,
        *,
        community_id: int | None = None,
        summary: str = "",
    ) -> None: ...

    def delete_entity(self, entity_id: str) -> None: ...

    def mention(self, chunk_id: str, entity_id: str) -> None: ...

    def relate(
        self,
        src_id: str,
        dst_id: str,
        *,
        rtype: str = "RELATED_TO",
        weight: float = 1.0,
    ) -> None: ...

    def chunks_mentioning(self, entity_id: str) -> list[str]: ...

    def relations_of(self, entity_id: str) -> list[tuple[str, str, str, float]]: ...

    def find_entity_by_name(self, name: str) -> EntityRow | None: ...

    def list_entities(
        self, q: str | None = None, community_id: int | None = None
    ) -> list[EntityRow]: ...

    def entities_mentioned_by_chunks(self, chunk_ids: list[str]) -> list[EntityRow]: ...

    def expand_neighbors(self, entity_ids: list[str], depth: int = 2) -> Subgraph: ...

    def all_edges(self) -> list[tuple[str, str, float]]: ...

    def all_entity_ids(self) -> list[str]: ...

    def set_community(self, entity_id: str, community_id: int) -> None: ...

    def set_summary(self, entity_id: str, summary: str) -> None: ...

    def stats(self) -> dict[str, int]: ...

    def close(self) -> None: ...


@runtime_checkable
class ManifestPort(Protocol):
    # True when the most recent load() found the persisted manifest
    # unreadable and degraded to "no known hashes". Callers surface this
    # instead of silently treating the corpus as new.
    corrupt_detected: bool

    def load(self) -> dict[str, str]: ...

    def save(self, hashes: dict[str, str]) -> None: ...

    def diff(self, current: dict[str, str]) -> FileDiff: ...


@runtime_checkable
class SourcesPort(Protocol):
    def walk(self, sources: list[SourceSpec]) -> list[Path]: ...

    def rel_to_project(self, path: Path) -> str: ...

    def hash_file(self, path: Path) -> str: ...


@runtime_checkable
class CommunityDetectorPort(Protocol):
    def detect(
        self,
        node_ids: list[str],
        edges: list[tuple[str, str, float]],
        *,
        seed: int = 42,
    ) -> dict[str, int]: ...
