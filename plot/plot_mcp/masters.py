"""Create a lightweight upstream master from a downstream reference (D-2026-06-19-C).

A service / feature reference to an actor / core_value / identity is
**pick-OR-create**: when no existing master matches, a real master node is
created on its HOME canvas — name only, flagged incomplete, deepened later by the
home-canvas coach (mission/core_value = D-2026-06-16-K/L, etc.) — instead of
free-typing (which D-2026-06-17-B bans). This module is the single home for two
facts: which canvas owns each referenceable master kind, and how a fresh one is
positioned so it doesn't stack on the anchor.
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from plot_mcp.canvas_io import read_canvas, write_canvas
from plot_mcp.models import ActorNode, CoreValueNode, IdentityNode, SketchNode
from plot_mcp.models_canvas import CanvasKind

# Referenceable master kind → its home canvas (the SSOT for where each master
# lives). Actors own ``actor``; Foundation owns ``core_value`` + ``identity``.
_MASTER_HOME: dict[str, CanvasKind] = {
    "actor": "actors",
    "core_value": "foundation",
    "identity": "foundation",
}

# Where a freshly-created master is dropped on its home canvas. Staggered down by
# how many of its kind already exist so successive creates don't stack.
_FRESH_X = 160.0
_FRESH_Y0 = 120.0
_FRESH_DY = 80.0


def create_master(plot_root: Path, project_id: str, kind: str, label: str) -> str:
    """Create a lightweight master node of ``kind`` on its home canvas; return id.

    ``kind`` must be one of ``actor`` / ``core_value`` / ``identity`` (the
    referenceable masters); anything else raises ``ValueError``. ``label`` is the
    master's name and must be non-blank. The node carries only its label (deep
    typed fields stay empty — filled later by the home-canvas coach), so it reads
    as incomplete until then. The id is minted server-side.
    """
    if kind not in _MASTER_HOME:
        raise ValueError(f"not a referenceable master kind: {kind!r}")
    name = label.strip()
    if not name:
        raise ValueError("master label required")
    home = _MASTER_HOME[kind]
    canvas = read_canvas(plot_root, project_id, home)
    node_id = f"{kind}_{uuid4().hex[:8]}"
    canvas.nodes.append(_build_master(kind, node_id, name, canvas.nodes))
    write_canvas(plot_root, project_id, canvas)
    return node_id


def _build_master(kind: str, node_id: str, label: str, existing: list[SketchNode]) -> SketchNode:
    rank = sum(1 for n in existing if n.kind == kind)
    x, y = _FRESH_X, _FRESH_Y0 + _FRESH_DY * rank
    if kind == "actor":
        return ActorNode(id=node_id, label=label, x=x, y=y)
    if kind == "core_value":
        return CoreValueNode(id=node_id, label=label, x=x, y=y)
    return IdentityNode(id=node_id, label=label, x=x, y=y)
