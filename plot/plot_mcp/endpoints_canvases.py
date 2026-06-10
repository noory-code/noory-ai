"""Canvas GET/PUT endpoints (D-2026-06-11-B).

Extracted from the api_endpoints.py god module. Owns the per-canvas
serialisation enrichments (MD parse warnings + per-node dirty signal)
that ride the response envelope without polluting the persisted model.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from plot_mcp.endpoints_common import _ApiError, _error, _parse_canvas_kind, _require_plot_root
from plot_mcp.folder_io import read_canvas, sync_details_with_overview, write_canvas
from plot_mcp.models import CanvasDoc


async def canvas_get_endpoint(request: Request) -> JSONResponse:
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    kind_raw = request.path_params["kind"]
    canvas_kind = _parse_canvas_kind(kind_raw)
    if canvas_kind is None:
        return _error(f"unknown canvas kind: {kind_raw!r}")
    service_id = request.query_params.get("service_id")
    if canvas_kind == "service_detail" and not service_id:
        return _error("service_id query param required for service_detail")
    try:
        canvas = read_canvas(plot_root, project_id, canvas_kind, service_id)
    except FileNotFoundError as exc:
        return _error(str(exc), status=404)
    raw = canvas.model_dump(by_alias=True)
    # v0.13 Phase 7 — enrich foundation nodes with MD-parse warnings so
    # the Inspector can surface a yellow ⚠ + actionable hint. Not part of
    # the model (stays clean on write); pure response decoration.
    from plot_mcp.folder_io import (
        _incident_edges,
        collect_foundation_md_warnings,
        is_node_dirty,
    )
    from plot_mcp.md_publish import can_publish

    warnings_by_node = collect_foundation_md_warnings(plot_root, project_id, canvas)
    if warnings_by_node:
        for n in raw.get("nodes", []):
            warns = warnings_by_node.get(n.get("id"))
            if warns:
                n["_md_warnings"] = warns
    # v0.22.0 (D-2026-05-17-H) — per-node dirty signal for the Inspector
    # publish button gate. Pure response decoration (matches the
    # ``_md_warnings`` pattern); never written back to disk.
    nodes_by_id = {n.id: n for n in canvas.nodes}
    for n in raw.get("nodes", []):
        node_obj = nodes_by_id.get(n.get("id"))
        if node_obj is None or not can_publish(node_obj):
            continue
        n["_dirty"] = is_node_dirty(node_obj, _incident_edges(canvas.edges, node_obj.id))
    return JSONResponse(raw)


async def canvas_put_endpoint(request: Request) -> JSONResponse:
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    kind_raw = request.path_params["kind"]
    canvas_kind = _parse_canvas_kind(kind_raw)
    if canvas_kind is None:
        return _error(f"unknown canvas kind: {kind_raw!r}")
    try:
        body: dict[str, Any] = await request.json()
    except json.JSONDecodeError:
        return _error("invalid JSON body")
    body["canvas_kind"] = canvas_kind
    try:
        canvas = CanvasDoc.model_validate(body)
    except ValidationError as exc:
        return _error(str(exc), status=422)
    try:
        write_canvas(plot_root, project_id, canvas)
    except FileNotFoundError as exc:
        return _error(str(exc), status=404)
    sync: dict[str, list[str]] = {"created": [], "archived": [], "skipped_archive": []}
    if canvas_kind == "services":
        sync = sync_details_with_overview(plot_root, project_id)
    # v0.24.12 (D-2026-05-21-A) — decorate response canvas with the
    # per-node ``_dirty`` signal so the Inspector's publish button gate
    # updates without a separate GET. Mirrors the GET endpoint's
    # decoration. Before v0.24.12, PUT returned a bare canvas and the
    # viewer's _dirty stayed stale until the next full reload — the
    # publish button never lit up for edits made in the current session.
    from plot_mcp.folder_io import _incident_edges, is_node_dirty
    from plot_mcp.md_publish import can_publish

    raw = canvas.model_dump(by_alias=True)
    nodes_by_id = {n.id: n for n in canvas.nodes}
    for n in raw.get("nodes", []):
        node_obj = nodes_by_id.get(n.get("id"))
        if node_obj is None or not can_publish(node_obj):
            continue
        n["_dirty"] = is_node_dirty(node_obj, _incident_edges(canvas.edges, node_obj.id))
    return JSONResponse({"canvas": raw, "sync": sync})
