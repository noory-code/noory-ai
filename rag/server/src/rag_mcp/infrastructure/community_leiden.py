"""Leiden community detection adapter implementing :class:`CommunityDetectorPort`."""

from __future__ import annotations


class LeidenCommunityDetector:
    """Detect communities over a weighted, undirected projection of edges.

    The adapter uses ``igraph`` + ``leidenalg``. Empty inputs return an empty
    assignment. Isolated nodes get their own singleton community.
    """

    def detect(
        self,
        node_ids: list[str],
        edges: list[tuple[str, str, float]],
        *,
        seed: int = 42,
    ) -> dict[str, int]:
        if not node_ids:
            return {}
        import igraph as ig
        import leidenalg as la

        idx = {n: i for i, n in enumerate(node_ids)}
        g = ig.Graph(directed=False)
        g.add_vertices(len(node_ids))

        symmetric_weights: dict[tuple[int, int], float] = {}
        for src, dst, weight in edges:
            if src not in idx or dst not in idx:
                continue
            a, b = idx[src], idx[dst]
            if a == b:
                continue
            key = (min(a, b), max(a, b))
            symmetric_weights[key] = symmetric_weights.get(key, 0.0) + float(weight)

        if symmetric_weights:
            es, ws = zip(*symmetric_weights.items())
            g.add_edges(list(es))
            g.es["weight"] = list(ws)
            partition = la.find_partition(
                g,
                la.RBConfigurationVertexPartition,
                weights="weight",
                seed=int(seed),
            )
        else:
            partition = la.find_partition(
                g, la.RBConfigurationVertexPartition, seed=int(seed)
            )

        membership = partition.membership
        return {node_ids[i]: int(c) for i, c in enumerate(membership)}
