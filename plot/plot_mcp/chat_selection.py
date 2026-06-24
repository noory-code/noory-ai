"""Lever 1a — render the selected nodes' actual content for the chat context.

``chat_context.build_context_preamble`` lists each selected node's kind / label
/ id (cheap, no I/O). That tells the agent *which* node "this" is, but not what
the node *says* — so "polish this mission" reached the agent without the mission
text and it invented one (context starvation, ``docs/idea/chat/00-problem.md``).

This module reads the active canvas engine-side — the SSOT both delivery layers
share (D-2026-06-15-D) — and renders the selected nodes' typed text fields. It
imports ``canvas_io`` (filesystem), so it lives apart from the pure
``chat_context`` module; the in-app endpoint and the MCP path both call it.

The project is resolved from the single project under the data root (canonical
one-project-per-root layout, D-2026-06-21-AB). Every failure mode is graceful:
no project, a missing / invalid canvas, or a selection id absent from the canvas
all yield ``""`` rather than a wrong or fabricated detail.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from plot_mcp.canvas_io import read_canvas
from plot_mcp.chat_context import SELECTION_DETAIL_CAP, build_context_preamble
from plot_mcp.models_canvas import CanvasDoc, CanvasKind
from plot_mcp.workspace import enumerate_projects

# Layer 1b (docs/idea/chat/01-levers.md) — how many nodes of the active canvas
# to list in the map before truncating, so a large canvas can't blow the
# context window. Labels only (cheap), so this can be looser than the detail cap.
CANVAS_MAP_CAP = 60

# Graph-level / visual / server-managed fields shared by every node kind
# (``BaseNodeFields``). They carry no project *meaning* — id + label are already
# in the header line, position / size / colour are presentation, and the rest is
# server bookkeeping — so the content renderer drops them and keeps only the
# per-kind typed text. Any leading-underscore key (``_dirty`` /
# ``_publish_baseline`` …) is server-managed and dropped too.
_STRUCTURAL_FIELDS: frozenset[str] = frozenset(
    {
        "kind",
        "id",
        "label",
        "x",
        "y",
        "width",
        "height",
        "color",
        "shape",
        "icon",
        "collapsed",
        "is_root",
        "parent_id",
        "details_path",
        "owner",
        "version",
    }
)

_VALID_CANVAS_KINDS: frozenset[str] = frozenset(
    {"foundation", "actors", "services", "entities", "feature"}
)

# Phase 2b (docs/idea/chat/01-levers.md, Lever 1c) — scopes whose design work
# *references* actors / entities, so the agent must see the existing ones to
# reference rather than reinvent them (dedup). A feature's steps carry
# ``actor_ref`` + ``ref_entity_ids``; a service carries ``ref_actor_ids``. The
# other scopes don't cross-reference, so they skip the registry to spare the
# context window.
_REGISTRY_SCOPES: frozenset[str] = frozenset({"feature", "services"})

# Phase 2b — cap on how many actors / entities to list, so a large project's
# registry can't blow the context window.
REGISTRY_CAP = 40


def build_turn_preamble(plot_root: Path, scope: str, selection: Any) -> str:
    """Assemble the per-turn user-message context — the context-provider seam.

    Single place that builds "what the agent should see this turn" (D-2026-06-17-L):
    active-canvas map → cross-canvas registry → selected-node detail, joined in
    that order (empty parts skipped). The Layer-3 system prompt is delivered
    separately (``build_system_prompt``); this is the Layer-2 user-message body.

    This is the **CAG** implementation (inject everything, bounded by caps). A
    future RAG / graph-traversal provider (D-2026-06-20-P) replaces the body of
    this one function for large projects — callers (the in-app endpoint) don't
    change. The canvas map falls back to the cheap wire-label header when the
    canvas can't be read engine-side.
    """
    canvas_map = render_canvas_map(plot_root, scope, selection)
    context = canvas_map or build_context_preamble(scope, selection)
    registry = render_cross_canvas_registry(plot_root, scope)
    detail = render_selection_detail(plot_root, scope, selection)
    return "\n\n".join(p for p in (context, registry, detail) if p)


def render_node_content(node: dict[str, Any]) -> str:
    """Render one node's typed text fields as ``field: value`` lines.

    Generic by design: every field that isn't structural / visual / server-managed
    (see :data:`_STRUCTURAL_FIELDS`) and carries non-empty text is included, so a
    new kind needs no per-kind branch here. List fields (e.g. ``provenance``) are
    joined; empty values and non-text values are skipped. Returns ``""`` when the
    node has no typed text (e.g. a bare ``project`` anchor).
    """
    lines: list[str] = []
    for key, value in node.items():
        if key in _STRUCTURAL_FIELDS or key.startswith("_"):
            continue
        if isinstance(value, str):
            text = value.strip()
        elif isinstance(value, list):
            text = ", ".join(str(v).strip() for v in value if str(v).strip())
        else:
            continue
        if text:
            lines.append(f"{key}: {text}")
    return "\n".join(lines)


def render_selection_detail(plot_root: Path, scope: str, selection: Any) -> str:
    """Render the selected nodes' content for ``scope`` (Lever 1a).

    Reads the active canvas (``foundation`` / ``actors`` / … / ``feature:<id>``)
    for the single project under ``plot_root`` and renders the typed content of
    every selected node found there. Returns ``""`` for the cross-canvas
    ``project`` scope, a malformed / empty selection, an unresolvable project /
    canvas, or when none of the selected ids exist on the canvas.
    """
    if scope == "project" or not isinstance(selection, list) or not selection:
        return ""
    canvas = _read_active_canvas(plot_root, scope)
    if canvas is None:
        return ""

    by_id = {n.id: n for n in canvas.nodes}
    blocks: list[str] = []
    for sel in selection[:SELECTION_DETAIL_CAP]:
        if not isinstance(sel, dict):
            continue
        node_id = sel.get("id")
        if not isinstance(node_id, str):
            continue
        node = by_id.get(node_id)
        if node is None:
            continue
        content = render_node_content(node.model_dump())
        if not content:
            continue
        blocks.append(f'{node.kind} "{node.label}" ({node.id}):\n{content}')

    if not blocks:
        return ""
    return "[Selected node details]\n" + "\n\n".join(blocks)


def render_canvas_map(plot_root: Path, scope: str, selection: Any) -> str:
    """Render the active canvas as a compact node map (Lever 1b / Phase 2a).

    Lists every node on the active canvas as ``kind "label" (id)``, marking the
    ones in ``selection`` so the agent sees the **whole current screen**, not just
    what's selected — and which of those nodes "this" refers to. Labels only (no
    bodies — those ride in :func:`render_selection_detail` for the selected
    subset, and the agent fetches the rest via its MCP tools). Capped at
    :data:`CANVAS_MAP_CAP` nodes. Returns ``""`` for the cross-canvas ``project``
    scope and every unresolvable-canvas case, so the caller can fall back to the
    cheap wire-label header.
    """
    if scope == "project":
        return ""
    canvas = _read_active_canvas(plot_root, scope)
    if canvas is None or not canvas.nodes:
        return ""

    selected_ids = {
        s.get("id") for s in selection if isinstance(s, dict) and isinstance(s.get("id"), str)
    }
    lines = [f"[Canvas: {scope}] {len(canvas.nodes)} node(s):"]
    for node in canvas.nodes[:CANVAS_MAP_CAP]:
        mark = " [selected]" if node.id in selected_ids else ""
        lines.append(f'- {node.kind} "{node.label}" ({node.id}){mark}')
    if len(canvas.nodes) > CANVAS_MAP_CAP:
        lines.append(f"…and {len(canvas.nodes) - CANVAS_MAP_CAP} more")
    return "\n".join(lines)


def render_cross_canvas_registry(plot_root: Path, scope: str) -> str:
    """Render the existing actors + entities as a compact reference (Phase 2b).

    On a scope whose design work references actors / entities (``feature`` /
    ``services``), the agent must see what already exists so it references them
    instead of minting a duplicate (글 / 게시물 / 포스트 as three entities). Lists
    actors by label and entities by ``label: summary``, both capped at
    :data:`REGISTRY_CAP`. Returns ``""`` for every other scope and when nothing
    is resolvable / present.
    """
    base = scope.split(":", 1)[0]
    if base not in _REGISTRY_SCOPES:
        return ""
    project_id = _resolve_project_id(plot_root)
    if project_id is None:
        return ""

    blocks: list[str] = []
    actors = _safe_read_canvas(plot_root, project_id, "actors")
    if actors is not None:
        actor_nodes = [n for n in actors.nodes if n.kind == "actor"][:REGISTRY_CAP]
        if actor_nodes:
            listed = ", ".join(f'"{n.label}" ({n.id})' for n in actor_nodes)
            blocks.append(f"[Existing actors] {listed}")
    entities = _safe_read_canvas(plot_root, project_id, "entities")
    if entities is not None:
        entity_nodes = [n for n in entities.nodes if n.kind == "entity"][:REGISTRY_CAP]
        if entity_nodes:
            listed = ", ".join(_render_entity_ref(n) for n in entity_nodes)
            blocks.append(f"[Existing entities] {listed}")
    return "\n".join(blocks)


def _render_entity_ref(node: Any) -> str:
    """``"label" (id): summary`` — or without the summary when it's empty."""
    summary = str(getattr(node, "summary", "") or "").strip()
    head = f'"{node.label}" ({node.id})'
    return f"{head}: {summary}" if summary else head


def _read_active_canvas(plot_root: Path, scope: str) -> CanvasDoc | None:
    """Read the active canvas for ``scope`` from the single project under the
    data root, or ``None`` for ``project`` scope / unknown base / no project /
    a corrupt or missing canvas (every failure mode is graceful — a chat turn
    must never break on a read).
    """
    if scope == "project":
        return None
    base, _, service_id = scope.partition(":")
    if base not in _VALID_CANVAS_KINDS:
        return None
    project_id = _resolve_project_id(plot_root)
    if project_id is None:
        return None
    return _safe_read_canvas(plot_root, project_id, _as_canvas_kind(base), service_id or None)


def _resolve_project_id(plot_root: Path) -> str | None:
    """The single project under the data root, or ``None`` (one-project-per-root,
    D-2026-06-21-AB; newest first when a legacy multi-project root survives)."""
    projects = enumerate_projects(plot_root)
    return projects[0].id if projects else None


def _safe_read_canvas(
    plot_root: Path, project_id: str, kind: CanvasKind, service_id: str | None = None
) -> CanvasDoc | None:
    """``read_canvas`` that swallows every error to ``None`` — a corrupt / missing
    canvas must never break a chat turn."""
    try:
        return read_canvas(plot_root, project_id, kind, service_id)
    except Exception:  # noqa: BLE001 — graceful: a bad canvas yields no context
        return None


def _as_canvas_kind(base: str) -> CanvasKind:
    """Narrow a validated base scope string to ``CanvasKind`` for the reader.

    ``base`` is already checked against ``_VALID_CANVAS_KINDS`` by the caller, so
    this is a typing narrowing, not a runtime gate.
    """
    return base  # type: ignore[return-value]
