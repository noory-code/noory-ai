"""Dependency-injection container.

Wires concrete infrastructure adapters into the application use cases. The
MCP interface layer talks to this container, never to concrete classes
directly. Tests can replace ports with fakes by instantiating Container with
keyword arguments.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .application.indexer import Indexer
from .application.rebalancer import Rebalancer
from .application.searcher import Searcher
from .domain.ports import (
    CommunityDetectorPort,
    EmbedderPort,
    GraphIndexPort,
    ManifestPort,
    SourcesPort,
    VectorIndexPort,
)
from .infrastructure import feedback_json
from .infrastructure.community_leiden import LeidenCommunityDetector
from .infrastructure.embedder_st import SentenceTransformersEmbedder
from .infrastructure.graph_kuzu import KuzuGraphIndex
from .infrastructure.manifest_json import JsonManifest
from .infrastructure.paths import RagPaths
from .infrastructure.settings_json import Settings
from .infrastructure.sources_fs import FilesystemSources
from .infrastructure.vector_sqlitevec import SqliteVecIndex


@dataclass
class Container:
    paths: RagPaths
    settings: Settings
    embedder: EmbedderPort
    vector: VectorIndexPort
    graph: GraphIndexPort
    manifest: ManifestPort
    sources: SourcesPort
    community: CommunityDetectorPort
    indexer: Indexer
    searcher: Searcher
    rebalancer: Rebalancer

    @classmethod
    def wire(cls, paths: RagPaths, settings: Settings) -> "Container":
        embedder: EmbedderPort = SentenceTransformersEmbedder(settings.embedding.model)
        vector: VectorIndexPort = SqliteVecIndex(paths.vec_db, dim=settings.embedding.dim)
        graph: GraphIndexPort = KuzuGraphIndex(paths.graph_dir)
        manifest: ManifestPort = JsonManifest(paths.manifest_file)
        sources: SourcesPort = FilesystemSources(paths.project_root)
        community: CommunityDetectorPort = LeidenCommunityDetector()

        indexer = Indexer(
            embedder=embedder,
            vector=vector,
            graph=graph,
            manifest=manifest,
            sources=sources,
            project_root=paths.project_root,
        )
        searcher = Searcher(
            embedder=embedder,
            vector=vector,
            graph=graph,
            feedback_boosts=lambda: feedback_json.aggregate_boosts(
                feedback_json.load(paths.feedback_file)
            ),
        )
        rebalancer = Rebalancer(graph=graph, community=community)

        return cls(
            paths=paths,
            settings=settings,
            embedder=embedder,
            vector=vector,
            graph=graph,
            manifest=manifest,
            sources=sources,
            community=community,
            indexer=indexer,
            searcher=searcher,
            rebalancer=rebalancer,
        )

    def close(self) -> None:
        try:
            self.vector.close()
        except Exception:
            pass
        try:
            self.graph.close()
        except Exception:
            pass
