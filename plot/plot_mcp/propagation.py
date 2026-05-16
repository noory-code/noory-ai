"""v0.20.0 Phase 4 (D-2026-05-17-C) — MINOR propagation walk.

Pure module: no I/O. Given a starting node id and a dict of loaded
canvases, walks the ancestor chain and returns the list of logical
ancestors whose JSON ``version`` field should be MINOR-bumped.

**Walk rule** (locked by D-2026-05-17-C, derived from user's
2026-05-17 direction "이건 노드로 제한합니다. refs 는 링크만
걸리는거잖아요. 그래서 페어런트와 자식 관계만"):

1. From the start id, follow the ``parent_id`` chain.
2. When the same id appears in multiple canvases (e.g. ServiceDetail
   root service ↔ Services master service), all presences are
   collected as a single ``LogicalAncestor`` — bumping must update
   every file it appears in. Mirror crossing happens implicitly via
   id-matching; no explicit ref is read.
3. ``actor_ref``, ``mission_ref``, ``value_ref``, ``identity_ref``
   fields (``ref_*_id``) and ``CanvasDoc.service_ref`` are *never*
   walked. They are link relationships, not parent–child.
4. The walk terminates when no canvas presence of the current id has
   a non-null ``parent_id`` (i.e. the chain has hit a true root).

The function deliberately does not raise on data invariant
violations (orphan ``parent_id``, missing nodes); it simply
terminates the walk early. ``CanvasDoc`` validators already enforce
these invariants at write time — Phase 4 only reads.
"""

from __future__ import annotations

from dataclasses import dataclass

from plot_mcp.models import CanvasDoc, SketchNode


@dataclass(frozen=True)
class LogicalAncestor:
    """One ancestor along the chain.

    A single logical node may have file-presence in multiple canvases
    when an id is mirrored (e.g. a service's root mirror in its
    ServiceDetail canvas + the master in the Services canvas). All
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
    ``"service_detail:<service_id>"``); the walk only needs them to be
    unique within the dict.
    """
    index = _build_id_index(canvases)
    visited: set[str] = {start_node_id}
    ancestors: list[LogicalAncestor] = []
    current_id = start_node_id

    while True:
        parent_id = _resolve_parent_id(current_id, index)
        if parent_id is None or parent_id in visited:
            break

        parent_presences = index.get(parent_id, [])
        if not parent_presences:
            # Orphan parent_id (CanvasDoc validators normally reject
            # this at write time; defend in depth for robustness).
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


def _resolve_parent_id(
    node_id: str,
    index: dict[str, list[tuple[str, SketchNode]]],
) -> str | None:
    """Return any non-null ``parent_id`` across the node's presences.

    The mirror-crossing rule: if a node id appears in two canvases and
    one presence has ``parent_id = null`` (e.g. ServiceDetail root
    service) while the other has ``parent_id = something`` (Services
    master service), prefer the non-null parent so the walk continues
    up the structural chain.
    """
    for _canvas_key, node in index.get(node_id, []):
        if node.parent_id is not None:
            return node.parent_id
    return None
