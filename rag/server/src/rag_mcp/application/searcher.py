"""Hybrid search use case: vector top-k + graph expansion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..domain.models import EntityRow, SearchHit, Subgraph
from ..domain.ports import EmbedderPort, GraphIndexPort, VectorIndexPort


@dataclass
class SearchResult:
    chunks: list[SearchHit]
    entities: list[EntityRow]
    subgraph: Subgraph


BOOST_FACTOR = 0.05


def apply_feedback_boost(
    hits: list[SearchHit], boosts: dict[str, float], factor: float = BOOST_FACTOR
) -> list[SearchHit]:
    """Re-rank hits by feedback: rel_paths with net-positive feedback get a
    lower effective distance (rank up), net-negative get higher (rank down).
    Empty boosts → unchanged order."""
    if not boosts:
        return hits
    return sorted(hits, key=lambda h: h.distance - factor * boosts.get(h.rel_path, 0.0))


class Searcher:
    def __init__(
        self,
        *,
        embedder: EmbedderPort,
        vector: VectorIndexPort,
        graph: GraphIndexPort,
        feedback_boosts: Callable[[], dict[str, float]] | None = None,
    ):
        self.embedder = embedder
        self.vector = vector
        self.graph = graph
        self.feedback_boosts = feedback_boosts

    def search(self, query: str, k: int = 8, expand_depth: int = 2) -> SearchResult:
        q_vec = self.embedder.encode_query(query)
        hits = self.vector.search(q_vec, k=k)
        if not hits:
            return SearchResult(chunks=[], entities=[], subgraph=Subgraph())
        if self.feedback_boosts is not None:
            hits = apply_feedback_boost(hits, self.feedback_boosts())

        chunk_graph_ids = [str(h.chunk_id) for h in hits]
        entities = self.graph.entities_mentioned_by_chunks(chunk_graph_ids)
        # expand_depth=0 means "no graph expansion": skip the traversal entirely.
        subgraph = (
            self.graph.expand_neighbors([e.id for e in entities], depth=expand_depth)
            if entities and expand_depth > 0
            else Subgraph()
        )
        return SearchResult(chunks=hits, entities=entities, subgraph=subgraph)

    def search_graph(self, entity_name_or_id: str, depth: int = 2) -> Subgraph:
        match = self.graph.find_entity_by_name(entity_name_or_id)
        seed_id = match.id if match else entity_name_or_id
        return self.graph.expand_neighbors([seed_id], depth=depth)
