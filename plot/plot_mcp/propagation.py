"""v0.20.0 Phase 4 (D-2026-05-17-C) — MINOR propagation walk.
v0.26.0 (D-2026-05-25-A) — rewritten to walk directed edges instead
of the (now-removed) ``parent_id`` field.

Pure module: no I/O. Given a starting node id and a dict of loaded
canvases, walks the ancestor chain and returns the list of logical
ancestors whose JSON ``version`` field should be MINOR-bumped.

**Walk rule** (locked by D-2026-05-17-C, re-expressed for the v0.26
directed-edge model):

1. From the start id, follow incoming directed edges (``target ==
   current_id`` and ``edge.directed is True``) across all canvases.
   The ``source`` of such an edge is the structural parent.
2. When the same id appears in multiple canvases (e.g. FeatureDetail
   root service ↔ Services master service), every canvas's edges are
   considered together — bumping must update every file the parent
   appears in. Mirror crossing happens implicitly via id-matching.
3. Undirected edges, ``actor_ref`` / ``mission_ref`` / ``value_ref``
   / ``identity_ref`` fields, and ``CanvasDoc.feature_ref`` are
   *never* walked. They are link relationships, not parent–child.
4. If a node has multiple incoming directed edges (multi-parent), the
   walk picks the lexicographically smallest source id — deterministic
   single-parent choice. v0.26 migration always produces a single
   incoming edge per node (from the former parent_id), so multi-parent
   only arises when a user explicitly draws extra directed edges.
5. The walk terminates when no incoming directed edge exists for the
   current id (i.e. the chain has hit a true root).

The function deliberately does not raise on data invariant
violations (orphan source, missing nodes); it simply terminates the
walk early.
"""

from __future__ import annotations

from dataclasses import dataclass

from plot_mcp.edge_semantics import fold_endpoints
from plot_mcp.models import CanvasDoc, SketchEdge, SketchNode


@dataclass(frozen=True)
class LogicalAncestor:
    """One ancestor along the chain.

    A single logical node may have file-presence in multiple canvases
    when an id is mirrored (e.g. a service's root mirror in its
    FeatureDetail canvas + the master in the Services canvas). All
    presences must be bumped in lockstep to keep the mirrors
    consistent.

    ``canvas_keys`` is sorted alphabetically for deterministic
    ordering (test stability + trailer reproducibility).
    """

    node_id: str
    canvas_keys: tuple[str, ...]


def walk_ancestors(
    start_node_id: str,
    canvases: dict[str, CanvasDoc],
) -> list[LogicalAncestor]:
    """Return the ancestor chain of ``start_node_id`` across all canvases.

    The returned list is ordered from immediate parent to root.
    ``canvases`` keys are arbitrary identifiers chosen by the caller
    (typically ``"foundation"``, ``"actors"``, ``"services"``,
    ``"feature:<service_id>"``); the walk only needs them to be
    unique within the dict.
    """
    node_index = _build_id_index(canvases)
    parent_lookup = _build_parent_lookup(canvases)
    visited: set[str] = {start_node_id}
    ancestors: list[LogicalAncestor] = []
    current_id = start_node_id

    while True:
        parent_id = _pick_parent(current_id, parent_lookup)
        if parent_id is None or parent_id in visited:
            break

        parent_presences = node_index.get(parent_id, [])
        if not parent_presences:
            # Orphan source (no node carries this id anywhere).
            break

        canvas_keys = tuple(sorted(key for key, _ in parent_presences))
        ancestors.append(LogicalAncestor(node_id=parent_id, canvas_keys=canvas_keys))
        visited.add(parent_id)
        current_id = parent_id

    return ancestors


def _build_id_index(
    canvases: dict[str, CanvasDoc],
) -> dict[str, list[tuple[str, SketchNode]]]:
    """Map ``node.id`` to every ``(canvas_key, node)`` it appears in."""
    index: dict[str, list[tuple[str, SketchNode]]] = {}
    for canvas_key, canvas in canvases.items():
        for node in canvas.nodes:
            index.setdefault(node.id, []).append((canvas_key, node))
    return index


def _build_parent_lookup(
    canvases: dict[str, CanvasDoc],
) -> dict[str, set[str]]:
    """Map child id → set of source ids of incoming directed edges.

    A directed edge from S to T means S is a structural parent of T.
    Multiple parents (more than one incoming directed edge) are
    collected as a set; ``_pick_parent`` resolves the choice
    deterministically.
    """
    lookup: dict[str, set[str]] = {}
    for canvas in canvases.values():
        for edge in canvas.edges:
            # v0.30.2 (D-2026-05-31-E) — parent/child per the edge's
            # stored ``relation`` (flow source=parent, inheritance
            # target=parent inverted, injection excluded), reading the
            # same SSOT as the viewer fold (foldHierarchy.foldEndpoints).
            ep = fold_endpoints(edge)
            if ep is None:
                continue
            parent, child = ep
            lookup.setdefault(child, set()).add(parent)
    return lookup


def _is_directed(edge: SketchEdge) -> bool:
    """Tolerate pre-v0.26 wire data (no ``directed`` key) by treating
    a missing flag as True — that matches the migration default."""
    return getattr(edge, "directed", True)


def _pick_parent(
    node_id: str,
    parent_lookup: dict[str, set[str]],
) -> str | None:
    """Pick the deterministic single parent for ``node_id``.

    If multiple incoming directed edges exist, return the
    lexicographically smallest source id. Returns None if there is no
    incoming directed edge (i.e. the chain has reached a root).
    """
    parents = parent_lookup.get(node_id)
    if not parents:
        return None
    return min(parents)
