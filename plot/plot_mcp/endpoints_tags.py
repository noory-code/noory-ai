"""Tag (git session bookmark) + read-only "view at tag" endpoints
(D-2026-06-11-B).

Extracted from the api_endpoints.py god module. ``project_at_tag``
streams a frozen snapshot of the project's canvases at a given git tag
using ``git show <tag>:<path>`` so the working tree is never touched.
"""

from __future__ import annotations

import json
from typing import Any, cast

from starlette.requests import Request
from starlette.responses import JSONResponse

from plot_mcp.endpoints_common import _ApiError, _error, _require_plot_root
from plot_mcp.git_store import TagAlreadyExistsError, delete_tag, list_tags, tag_snapshot


async def tags_list_endpoint(request: Request) -> JSONResponse:
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    folder = plot_root / project_id
    if not folder.is_dir():
        return _error(f"project not found: {project_id}", status=404)
    return JSONResponse({"tags": list_tags(plot_root)})


async def tag_post_endpoint(request: Request) -> JSONResponse:
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    folder = plot_root / project_id
    if not folder.is_dir():
        return _error(f"project not found: {project_id}", status=404)
    try:
        body: dict[str, Any] = await request.json()
    except json.JSONDecodeError:
        return _error("invalid JSON body")
    name = body.get("name")
    message = body.get("message")
    if not isinstance(name, str) or not name.strip():
        return _error("'name' is required and must be a non-empty string")
    try:
        result = tag_snapshot(plot_root, name, message=message)
    except TagAlreadyExistsError as exc:
        return _error(str(exc), status=409)
    return JSONResponse(result, status_code=201)


async def tag_delete_endpoint(request: Request) -> JSONResponse:
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    name = request.path_params["tag_name"]
    folder = plot_root / project_id
    if not folder.is_dir():
        return _error(f"project not found: {project_id}", status=404)
    try:
        delete_tag(plot_root, name)
    except KeyError as exc:
        return _error(f"tag not found: {exc.args[0]}", status=404)
    return JSONResponse({"ok": True})


# ---------------------------------------------------------------------------
# v0.24.14 (D-2026-05-21-C) — read-only "view at tag" endpoint
# ---------------------------------------------------------------------------


async def project_at_tag_endpoint(request: Request) -> JSONResponse:
    """``GET /api/projects/{project_id}/at-tag/{tag}``

    Returns the project's full state at the given git tag without
    touching the working tree (uses ``git show <tag>:<path>`` internally).
    Response body:

    ``{
        "project": ProjectDoc,
        "canvases": {
            "foundation": CanvasDoc,
            "actors": CanvasDoc,
            "services": CanvasDoc,
            "service_detail:<id>": CanvasDoc,
            ...
        }
    }``

    Read-only by construction — the viewer drops this into a separate
    snapshot cache slot; no PUT path operates on tag-scoped data.
    """
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    tag = request.path_params["tag"]
    folder = plot_root / project_id
    if not folder.is_dir():
        return _error(f"project not found: {project_id}", status=404)

    from plot_mcp.git_store import read_file_at_tag

    def _read_canvas_json(rel: str) -> dict[str, Any] | None:
        try:
            raw = read_file_at_tag(plot_root, tag, f"{project_id}/{rel}")
        except FileNotFoundError:
            return None
        try:
            return cast("dict[str, Any]", json.loads(raw.decode("utf-8")))
        except json.JSONDecodeError:
            return None

    project_raw = _read_canvas_json("project.json")
    if project_raw is None:
        return _error(f"project.json not at tag {tag!r}", status=404)
    canvases: dict[str, dict[str, Any]] = {}
    for kind in ("foundation", "actors", "services"):
        c = _read_canvas_json(f"{kind}/canvas.json")
        if c is not None:
            canvases[kind] = c
    # service_detail canvases live under services/<service_id>/detail.json —
    # discover by listing the services canvas's category/service nodes.
    services_canvas = canvases.get("services")
    if isinstance(services_canvas, dict):
        for n in services_canvas.get("nodes", []):
            if not isinstance(n, dict):
                continue
            if n.get("kind") != "service" or not n.get("is_root"):
                continue
            sid = n.get("id")
            if not isinstance(sid, str):
                continue
            d = _read_canvas_json(f"services/{sid}/detail.json")
            if d is not None:
                canvases[f"service_detail:{sid}"] = d
    return JSONResponse({"project": project_raw, "canvases": canvases})
