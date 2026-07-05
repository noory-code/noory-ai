"""Upsert use case.

Takes pre-chunked text + pre-extracted entities/relations (produced by the
calling Claude session) and persists them across the vector and graph stores,
keeping the file-hash manifest in sync.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..domain.models import ChunkData, EntityData, FileDiff, RelationData, SourceSpec
from ..domain.ports import (
    EmbedderPort,
    GraphIndexPort,
    ManifestPort,
    SourcesPort,
    VectorIndexPort,
)


@dataclass(frozen=True)
class UpsertResult:
    rel_path: str
    chunk_ids: list[int]
    entity_ids: list[str]


class Indexer:
    def __init__(
        self,
        *,
        embedder: EmbedderPort,
        vector: VectorIndexPort,
        graph: GraphIndexPort,
        manifest: ManifestPort,
        sources: SourcesPort,
        project_root: Path,
    ):
        self.embedder = embedder
        self.vector = vector
        self.graph = graph
        self.manifest = manifest
        self.sources = sources
        self.project_root = project_root

    # ------------------------------------------------------------ diff source

    def diff(self, sources: list[SourceSpec]) -> FileDiff:
        current = {
            self.sources.rel_to_project(p): self.sources.hash_file(p)
            for p in self.sources.walk(sources)
        }
        return self.manifest.diff(current)

    def current_hashes(self, sources: list[SourceSpec]) -> dict[str, str]:
        return {
            self.sources.rel_to_project(p): self.sources.hash_file(p)
            for p in self.sources.walk(sources)
        }

    # ------------------------------------------------------------------ writes

    def upsert_file(
        self,
        rel_path: str,
        chunks: list[ChunkData],
        entities: list[EntityData],
        relations: list[RelationData],
    ) -> UpsertResult:
        if not chunks:
            self.delete_file(rel_path)
            return UpsertResult(rel_path=rel_path, chunk_ids=[], entity_ids=[])

        embeddings = self.embedder.encode_passages([c.text for c in chunks])
        chunk_ids = self.vector.add_file(rel_path, chunks, embeddings)
        graph_chunk_ids = [str(cid) for cid in chunk_ids]

        # Old chunk nodes for this file get detached + replaced.
        self.graph.delete_chunks_by_path(rel_path)
        for idx, gid in enumerate(graph_chunk_ids):
            self.graph.upsert_chunk(gid, rel_path, idx)

        # Entities: upsert nodes, then connect MENTIONS to chunk graph ids.
        for ent in entities:
            self.graph.upsert_entity(ent.id, ent.name, ent.type)
            for chunk_idx in ent.chunk_indices:
                if 0 <= chunk_idx < len(graph_chunk_ids):
                    self.graph.mention(graph_chunk_ids[chunk_idx], ent.id)

        # Relations between entities.
        for rel in relations:
            self.graph.relate(
                rel.src_id, rel.dst_id, rtype=rel.type, weight=rel.weight
            )

        # The manifest entry for this file is written by the interface layer
        # (tool_upsert_chunks) immediately after a successful upsert —
        # incrementally per file, not deferred to the end of a reindex.
        return UpsertResult(
            rel_path=rel_path,
            chunk_ids=chunk_ids,
            entity_ids=[e.id for e in entities],
        )

    def delete_file(self, rel_path: str) -> None:
        self.vector.delete_file(rel_path)
        self.graph.delete_chunks_by_path(rel_path)
