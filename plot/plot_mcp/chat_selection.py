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
from plot_mcp.chat_context import SELECTION_DETAIL_CAP
from plot_mcp.models_canvas import CanvasKind
from plot_mcp.workspace import enumerate_projects

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
    base, _, service_id = scope.partition(":")
    if base not in _VALID_CANVAS_KINDS:
        return ""

    projects = enumerate_projects(plot_root)
    if not projects:
        return ""
    project_id = projects[0].id

    try:
        canvas = read_canvas(plot_root, project_id, _as_canvas_kind(base), service_id or None)
    except Exception:  # noqa: BLE001 — a corrupt / missing canvas must not break a turn
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


def _as_canvas_kind(base: str) -> CanvasKind:
    """Narrow a validated base scope string to ``CanvasKind`` for the reader.

    ``base`` is already checked against ``_VALID_CANVAS_KINDS`` by the caller, so
    this is a typing narrowing, not a runtime gate.
    """
    return base  # type: ignore[return-value]
