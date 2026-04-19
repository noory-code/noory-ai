"""Starlette HTTP handlers for sketch CRUD + health."""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from plot_mcp.models import SketchDoc
from plot_mcp.sketches import (
    create_sketch,
    delete_sketch,
    list_sketches,
    read_sketch,
    write_sketch,
)
from plot_mcp.workspace import resolve_plot_root

_log = logging.getLogger(__name__)


def _project_path(request: Request) -> str | None:
    return request.query_params.get("project_path")


def _error(msg: str, status: int = 400) -> JSONResponse:
    return JSONResponse({"error": msg}, status_code=status)


async def health_endpoint(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "plot"})


async def sketches_list_endpoint(request: Request) -> JSONResponse:
    project_path = _project_path(request)
    if not project_path:
        return _error("project_path query param is required")
    try:
        plot_root = resolve_plot_root(project_path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return _error(str(exc), status=404)
    sketches = list_sketches(plot_root)
    return JSONResponse([s.model_dump() for s in sketches])


async def sketch_get_endpoint(request: Request) -> JSONResponse:
    project_path = _project_path(request)
    if not project_path:
        return _error("project_path query param is required")
    sketch_id = request.path_params["sketch_id"]
    try:
        plot_root = resolve_plot_root(project_path)
        doc = read_sketch(plot_root, sketch_id)
    except FileNotFoundError as exc:
        return _error(str(exc), status=404)
    except NotADirectoryError as exc:
        return _error(str(exc), status=404)
    return JSONResponse(doc.model_dump(by_alias=True))


async def sketch_post_endpoint(request: Request) -> JSONResponse:
    project_path = _project_path(request)
    if not project_path:
        return _error("project_path query param is required")
    try:
        body: dict[str, Any] = await request.json()
    except json.JSONDecodeError:
        return _error("invalid JSON body")
    sketch_id = body.get("id")
    name = body.get("name") or ""
    if not sketch_id or not isinstance(sketch_id, str):
        return _error("'id' is required and must be a string")
    try:
        plot_root = resolve_plot_root(project_path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return _error(str(exc), status=404)
    try:
        doc = create_sketch(plot_root, sketch_id, name)
    except FileExistsError as exc:
        return _error(str(exc), status=409)
    except ValidationError as exc:
        return _error(str(exc), status=422)
    return JSONResponse(doc.model_dump(by_alias=True), status_code=201)


async def sketch_put_endpoint(request: Request) -> JSONResponse:
    project_path = _project_path(request)
    if not project_path:
        return _error("project_path query param is required")
    sketch_id = request.path_params["sketch_id"]
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return _error("invalid JSON body")
    # Force id coherence between URL and body
    body["id"] = sketch_id
    try:
        doc = SketchDoc.model_validate(body)
    except ValidationError as exc:
        return _error(str(exc), status=422)
    try:
        plot_root = resolve_plot_root(project_path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return _error(str(exc), status=404)
    write_sketch(plot_root, doc)
    return JSONResponse({"ok": True, "id": doc.id})


async def sketch_delete_endpoint(request: Request) -> Response:
    project_path = _project_path(request)
    if not project_path:
        return _error("project_path query param is required")
    sketch_id = request.path_params["sketch_id"]
    try:
        plot_root = resolve_plot_root(project_path)
        delete_sketch(plot_root, sketch_id)
    except FileNotFoundError as exc:
        return _error(str(exc), status=404)
    except NotADirectoryError as exc:
        return _error(str(exc), status=404)
    return JSONResponse({"ok": True})
