"""Starlette HTTP handlers for the v0.4 project / canvas / tag surface.

The legacy v0.1 ``/api/sketches/*`` endpoints have been removed — new
callers use the project/canvas shape directly. ``plot_mcp/sketches.py``
now only serves the in-process migration script.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from plot_mcp.file_io import (
    ExtensionNotAllowedError,
    UnsafePathError,
    ensure_folder,
    read_text_file,
    uniquify_folder,
    write_text_file,
)
from plot_mcp.folder_io import (
    create_project,
    delete_project,
    list_service_details,
    read_canvas,
    read_project,
    rename_project,
    sync_details_with_overview,
    write_canvas,
)
from plot_mcp.git_store import (
    TagAlreadyExistsError,
    delete_tag,
    list_tags,
    tag_snapshot,
)
from plot_mcp.migrate import migrate_v01_to_v02
from plot_mcp.models import CanvasDoc, CanvasKind
from plot_mcp.workspace import resolve_plot_root

_log = logging.getLogger(__name__)

_ALLOWED_CANVAS_KINDS: frozenset[str] = frozenset(
    ("core", "actors", "services", "service_detail"),
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _project_path(request: Request) -> str | None:
    return request.query_params.get("project_path")


def _error(msg: str, status: int = 400) -> JSONResponse:
    return JSONResponse({"error": msg}, status_code=status)


class _ApiError(Exception):
    """Raised by ``_require_plot_root`` to short-circuit to a JSONResponse."""

    def __init__(self, response: JSONResponse):
        self.response = response


def _require_plot_root(request: Request) -> Path:
    """Return the resolved ``plot_root`` or raise ``_ApiError`` for a 4xx reply."""
    project_path = _project_path(request)
    if not project_path:
        raise _ApiError(_error("project_path query param is required"))
    try:
        return resolve_plot_root(project_path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise _ApiError(_error(str(exc), status=404)) from exc


# ---------------------------------------------------------------------------
# health
# ---------------------------------------------------------------------------


async def health_endpoint(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "plot"})


# ---------------------------------------------------------------------------
# projects
# ---------------------------------------------------------------------------


async def projects_list_endpoint(request: Request) -> JSONResponse:
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    # Silently migrate any leftover v0.1 files in the (now-legacy)
    # ``sketches/`` root. Only runs if that directory still exists.
    migrated = migrate_v01_to_v02(plot_root)
    # Enumerate project folders, newest-first by ``updated``. In the v0.8
    # layout each project is a direct child of ``plot_root``; we skip the
    # legacy ``sketches/`` folder (migration landing pad) and any other
    # non-project child that has no ``project.json``.
    projects: list[dict[str, Any]] = []
    if plot_root.is_dir():
        for child in sorted(plot_root.iterdir()):
            if not child.is_dir() or child.name == "sketches":
                continue
            try:
                proj = read_project(plot_root, child.name)
            except (FileNotFoundError, ValueError):
                continue
            projects.append(proj.model_dump())
    projects.sort(key=lambda p: p.get("updated", ""), reverse=True)
    return JSONResponse({"projects": projects, "migrated": migrated})


async def project_post_endpoint(request: Request) -> JSONResponse:
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    try:
        body: dict[str, Any] = await request.json()
    except json.JSONDecodeError:
        return _error("invalid JSON body")
    project_id = body.get("id")
    name = body.get("name") or ""
    if not project_id or not isinstance(project_id, str):
        return _error("'id' is required and must be a string")
    try:
        proj = create_project(plot_root, project_id, name)
    except FileExistsError as exc:
        return _error(str(exc), status=409)
    except ValidationError as exc:
        return _error(str(exc), status=422)
    return JSONResponse(proj.model_dump(), status_code=201)


async def project_get_endpoint(request: Request) -> JSONResponse:
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    try:
        proj = read_project(plot_root, project_id)
    except FileNotFoundError as exc:
        return _error(str(exc), status=404)
    details = list_service_details(plot_root, project_id)
    tags = list_tags(plot_root / project_id)
    return JSONResponse(
        {
            **proj.model_dump(),
            "service_details": details,
            "tags": tags,
        }
    )


async def project_patch_endpoint(request: Request) -> JSONResponse:
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    try:
        body: dict[str, Any] = await request.json()
    except json.JSONDecodeError:
        return _error("invalid JSON body")
    name = body.get("name")
    if not isinstance(name, str) or not name.strip():
        return _error("'name' is required and must be a non-empty string")
    try:
        renamed = rename_project(plot_root, project_id, name)
    except FileNotFoundError as exc:
        return _error(str(exc), status=404)
    return JSONResponse(renamed.model_dump())


async def project_delete_endpoint(request: Request) -> Response:
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    try:
        delete_project(plot_root, project_id)
    except FileNotFoundError as exc:
        return _error(str(exc), status=404)
    return JSONResponse({"ok": True})


# ---------------------------------------------------------------------------
# canvases
# ---------------------------------------------------------------------------


def _parse_canvas_kind(raw: str) -> CanvasKind | None:
    if raw not in _ALLOWED_CANVAS_KINDS:
        return None
    # mypy is happy with the narrowed literal here.
    return raw  # type: ignore[return-value]


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
    return JSONResponse(canvas.model_dump(by_alias=True))


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
    sync: dict[str, list[str]] = {"created": [], "archived": []}
    if canvas_kind == "services":
        sync = sync_details_with_overview(plot_root, project_id)
    return JSONResponse({"canvas": canvas.model_dump(by_alias=True), "sync": sync})


# ---------------------------------------------------------------------------
# tags (git session bookmarks)
# ---------------------------------------------------------------------------


async def tags_list_endpoint(request: Request) -> JSONResponse:
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    folder = plot_root / project_id
    if not folder.is_dir():
        return _error(f"project not found: {project_id}", status=404)
    return JSONResponse({"tags": list_tags(folder)})


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
        result = tag_snapshot(folder, name, message=message)
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
        delete_tag(folder, name)
    except KeyError as exc:
        return _error(f"tag not found: {exc.args[0]}", status=404)
    return JSONResponse({"ok": True})


# ---------------------------------------------------------------------------
# v0.7 text-file + folder surface — powers the Inspector MD editor.
# ---------------------------------------------------------------------------


def _project_scoped_root(plot_root: Path, project_id: str) -> Path:
    """v0.8: everything a project owns lives under ``.plot/{project_id}/``.
    File/folder API paths are relative to this scope so a request can't
    climb up into another project (or outside ``.plot/``).
    """
    return plot_root / project_id


async def file_get_endpoint(request: Request) -> JSONResponse:
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.query_params.get("project_id")
    if not project_id:
        return _error("'project_id' query param is required")
    rel_path = request.query_params.get("path")
    if not rel_path:
        return _error("'path' query param is required")
    project_root = _project_scoped_root(plot_root, project_id)
    if not project_root.is_dir():
        return _error(f"project not found: {project_id}", status=404)
    try:
        content = read_text_file(project_root, rel_path)
    except (UnsafePathError, ExtensionNotAllowedError) as exc:
        return _error(str(exc), status=400)
    except ValueError as exc:
        return _error(str(exc), status=413)
    return JSONResponse({"path": rel_path, "content": content})


async def file_put_endpoint(request: Request) -> JSONResponse:
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.query_params.get("project_id")
    if not project_id:
        return _error("'project_id' query param is required")
    rel_path = request.query_params.get("path")
    if not rel_path:
        return _error("'path' query param is required")
    try:
        body: dict[str, Any] = await request.json()
    except json.JSONDecodeError:
        return _error("invalid JSON body")
    content = body.get("content")
    if not isinstance(content, str):
        return _error("'content' must be a string")
    project_root = _project_scoped_root(plot_root, project_id)
    if not project_root.is_dir():
        return _error(f"project not found: {project_id}", status=404)
    try:
        write_text_file(project_root, rel_path, content)
    except (UnsafePathError, ExtensionNotAllowedError) as exc:
        return _error(str(exc), status=400)
    except ValueError as exc:
        return _error(str(exc), status=413)
    # v0.9: no longer mirrors a summary back into the canvas — typed
    # fields live on the node directly, so writing ``details.md`` is a
    # leaf operation. The watcher still picks up the disk change and
    # broadcasts ``project_changed`` for any open client.
    return JSONResponse({"path": rel_path, "ok": True})


async def folder_post_endpoint(request: Request) -> JSONResponse:
    """Create ``.plot/{project_id}/{path}`` with a fresh ``index.md``. Returns
    the path actually created (may have a ``-2``/``-3`` suffix when the
    desired name was taken)."""
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    try:
        body: dict[str, Any] = await request.json()
    except json.JSONDecodeError:
        return _error("invalid JSON body")
    project_id = body.get("project_id")
    if not isinstance(project_id, str) or not project_id:
        return _error("'project_id' is required and must be a non-empty string")
    desired = body.get("path")
    if not isinstance(desired, str) or not desired.strip():
        return _error("'path' is required and must be a non-empty string")
    project_root = _project_scoped_root(plot_root, project_id)
    if not project_root.is_dir():
        return _error(f"project not found: {project_id}", status=404)
    try:
        actual = uniquify_folder(project_root, desired)
        ensure_folder(project_root, actual)
    except UnsafePathError as exc:
        return _error(str(exc), status=400)
    return JSONResponse({"path": actual}, status_code=201)
