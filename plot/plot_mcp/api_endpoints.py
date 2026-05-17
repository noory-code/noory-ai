"""Starlette HTTP handlers for the v0.4 project / canvas / tag surface.

The legacy v0.1 ``/api/sketches/*`` endpoints have been removed — new
callers use the project/canvas shape directly. ``plot_mcp/sketches.py``
now only serves the in-process migration script.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, cast

from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response

from plot_mcp.file_io import (
    ALLOWED_IMAGE_EXTENSIONS,
    ExtensionNotAllowedError,
    UnsafePathError,
    ensure_folder,
    read_text_file,
    resolve_safe_path,
    uniquify_folder,
    write_text_file,
)
from plot_mcp.folder_io import (
    PublishNotEligibleError,
    UnpublishNotEligibleError,
    create_project,
    delete_project,
    list_service_details,
    publish_node,
    read_canvas,
    read_project,
    rename_project,
    sync_details_with_overview,
    unpublish_node,
    write_canvas,
    write_project,
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
    ("foundation", "actors", "services", "service_detail"),
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


async def project_anchor_patch_endpoint(request: Request) -> JSONResponse:
    """v0.13 Phase 0: PATCH the project anchor for a given canvas.

    Body fields (all optional):
      x, y, width, height, color, shape
    Only supplied fields are updated; the rest stay as before.
    """
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    canvas = request.path_params["canvas"]
    if canvas not in {"foundation", "actors", "services"}:
        return _error(f"unknown canvas {canvas!r}", status=400)
    try:
        body: dict[str, Any] = await request.json()
    except json.JSONDecodeError:
        return _error("invalid JSON body")
    try:
        proj = read_project(plot_root, project_id)
    except FileNotFoundError as exc:
        return _error(str(exc), status=404)
    from plot_mcp.models import AnchorPlacement

    current = proj.anchors.get(canvas, AnchorPlacement())
    patched = current.model_copy(update={k: v for k, v in body.items() if v is not None})
    new_anchors = {**proj.anchors, canvas: patched}
    proj = proj.model_copy(update={"anchors": new_anchors})
    write_project(plot_root, proj)
    return JSONResponse(proj.model_dump())


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


# ---------------------------------------------------------------------------
# v0.18.0 Phase 3 (D-2026-05-16-E) — publish endpoint
# ---------------------------------------------------------------------------


async def node_publish_endpoint(request: Request) -> JSONResponse:
    """``POST /api/projects/{project_id}/canvases/{canvas_kind}/nodes/{node_id}/publish``

    Optional query parameter ``service_id`` for service_detail canvases.
    Returns ``{node_id, from_version, to_version, md_path, sha,
    propagated}``. ``propagated`` (v0.20.0 / D-2026-05-17-C) is the
    list of ancestor nodes whose MINOR version was bumped — each item
    is ``{node_id, from_version, to_version, canvases}``.
    Errors:
      - 404 if project / node not found
      - 409 if node not publish-eligible (kind/role disallows)
    """
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    canvas_kind = request.path_params["canvas_kind"]
    node_id = request.path_params["node_id"]
    if canvas_kind not in _ALLOWED_CANVAS_KINDS:
        return _error(f"invalid canvas_kind: {canvas_kind}", status=400)
    service_id = request.query_params.get("service_id") or None
    try:
        result = publish_node(
            plot_root,
            project_id,
            cast("CanvasKind", canvas_kind),
            node_id,
            service_id=service_id,
        )
    except FileNotFoundError as exc:
        return _error(str(exc), status=404)
    except KeyError as exc:
        return _error(str(exc.args[0]), status=404)
    except PublishNotEligibleError as exc:
        return _error(str(exc), status=409)
    return JSONResponse(result, status_code=201)


# ---------------------------------------------------------------------------
# v0.23.x (D-2026-05-17-J) — unpublish
# ---------------------------------------------------------------------------


async def node_unpublish_endpoint(request: Request) -> JSONResponse:
    """``POST /api/projects/{id}/canvases/{kind}/nodes/{node_id}/unpublish``

    Reverts the most recent publish commit for the node.
    Returns ``{node_id, from_version, to_version, reverted_sha,
    revert_commit_sha}``.

    Optional ``service_id`` for service_detail canvases.
    Errors:
      - 404 if project / canvas / node not found
      - 409 if the node has no publish commit to revert
    """
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    canvas_kind = request.path_params["canvas_kind"]
    node_id = request.path_params["node_id"]
    if canvas_kind not in _ALLOWED_CANVAS_KINDS:
        return _error(f"invalid canvas_kind: {canvas_kind}", status=400)
    service_id = request.query_params.get("service_id") or None
    try:
        result = unpublish_node(
            plot_root,
            project_id,
            cast("CanvasKind", canvas_kind),
            node_id,
            service_id=service_id,
        )
    except FileNotFoundError as exc:
        return _error(str(exc), status=404)
    except KeyError as exc:
        return _error(str(exc.args[0]), status=404)
    except UnpublishNotEligibleError as exc:
        return _error(str(exc), status=409)
    return JSONResponse(result, status_code=201)


# ---------------------------------------------------------------------------
# v0.23.0 (D-2026-05-17-I) — list a node's published versions
# ---------------------------------------------------------------------------


_FRONTMATTER_PUBLISHED_AT_RE = re.compile(
    r"^published_at:\s*'?([^'\n]+)'?\s*$", re.MULTILINE
)


def _read_published_at(md_path: Path) -> str | None:
    """Read ``published_at`` from a published MD file's YAML frontmatter.

    Returns None on any parse failure — the field is informational, so
    a malformed file shouldn't break the listing.
    """
    try:
        head = md_path.read_text(encoding="utf-8", errors="replace")[:2048]
    except OSError:
        return None
    match = _FRONTMATTER_PUBLISHED_AT_RE.search(head)
    return match.group(1).strip() if match else None


def _git_commit_sha_for_path(project_dir: Path, rel_path: str) -> str | None:
    """Short sha of the commit that introduced ``rel_path``. None on any failure."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "log", "--diff-filter=A", "-1", "--format=%h", "--", rel_path],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    sha = result.stdout.strip()
    return sha or None


_VERSION_FILENAME_RE = re.compile(r"^v(\d+\.\d+)\.md$")


async def node_published_list_endpoint(request: Request) -> JSONResponse:
    """``GET /api/projects/{id}/canvases/{kind}/nodes/{node_id}/published``

    Returns a list of published MD file metadata for the node, newest
    version first. Each entry: ``{version, path, published_at, sha, size}``.
    Empty list when the node has never been published or its slug folder
    doesn't exist.

    Optional ``service_id`` query parameter (mirrors publish endpoint).
    """
    try:
        plot_root = _require_plot_root(request)
    except _ApiError as exc:
        return exc.response
    project_id = request.path_params["project_id"]
    canvas_kind = request.path_params["canvas_kind"]
    node_id = request.path_params["node_id"]
    if canvas_kind not in _ALLOWED_CANVAS_KINDS:
        return _error(f"invalid canvas_kind: {canvas_kind}", status=400)
    service_id = request.query_params.get("service_id") or None
    project_dir = plot_root / project_id
    if not project_dir.is_dir():
        return _error(f"project not found: {project_id}", status=404)
    # Resolve the canvas to locate the node + derive its kind+slug.
    from plot_mcp.folder_io import read_canvas
    from plot_mcp.slug import slugify

    try:
        canvas = read_canvas(
            plot_root, project_id, cast("CanvasKind", canvas_kind), service_id
        )
    except FileNotFoundError as exc:
        return _error(str(exc), status=404)
    node = next((n for n in canvas.nodes if n.id == node_id), None)
    if node is None:
        return _error(f"node not found: {node_id}", status=404)
    slug = slugify(node.label) or "untitled"
    # Locate the slug folder. The canvas's on-disk parent is the
    # canvas directory used by published_md_path.
    from plot_mcp.folder_io import _canvas_file

    canvas_dir = _canvas_file(plot_root, project_id, cast("CanvasKind", canvas_kind), service_id).parent
    slug_dir = canvas_dir / "published" / node.kind / slug
    if not slug_dir.is_dir():
        return JSONResponse({"versions": []})
    versions: list[dict[str, Any]] = []
    for entry in slug_dir.iterdir():
        if not entry.is_file():
            continue
        match = _VERSION_FILENAME_RE.match(entry.name)
        if not match:
            continue
        version = "v" + match.group(1)
        rel_path = str(entry.relative_to(project_dir))
        versions.append(
            {
                "version": version,
                "path": rel_path,
                "published_at": _read_published_at(entry),
                "sha": _git_commit_sha_for_path(project_dir, rel_path),
                "size": entry.stat().st_size,
            }
        )
    # Sort newest version first; parse "v<MAJOR>.<MINOR>" into tuple.
    versions.sort(
        key=lambda v: tuple(int(p) for p in v["version"][1:].split(".")),
        reverse=True,
    )
    return JSONResponse({"versions": versions})


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


async def file_raw_endpoint(request: Request) -> Response:
    """v0.24.0 (D-2026-05-17-L) — serve raw bytes for image embeds.

    Same query shape as ``file_get_endpoint`` (``project_path`` +
    ``project_id`` + ``path``), but returns the file's bytes via
    ``FileResponse`` so the browser ``<img>`` tag can render it
    directly. Extension allow-list = ``ALLOWED_IMAGE_EXTENSIONS``
    (.png/.jpg/.jpeg/.gif/.webp/.avif/.svg). Path-traversal safety
    via the existing ``resolve_safe_path``.
    """
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
        target = resolve_safe_path(project_root, rel_path)
    except UnsafePathError as exc:
        return _error(str(exc), status=400)
    if target.suffix.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        return _error(
            f"extension {target.suffix!r} not allowed for raw image read",
            status=400,
        )
    if not target.is_file():
        return _error(f"file not found: {rel_path}", status=404)
    return FileResponse(target)


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
