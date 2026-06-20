"""Publish + unpublish + published-list endpoints (D-2026-06-11-B).

Extracted from the api_endpoints.py god module. Covers the project-level
blueprint publish (semver bump + git tag), the per-node publish + revert,
and the published-versions listing for the Inspector's history view.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, cast

from starlette.requests import Request
from starlette.responses import JSONResponse

from plot_mcp.endpoints_common import (
    _ALLOWED_CANVAS_KINDS,
    _ApiError,
    _error,
    _require_plot_root,
)
from plot_mcp.folder_io import (
    PublishNotEligibleError,
    UnpublishNotEligibleError,
    publish_node,
    unpublish_node,
)
from plot_mcp.git_store import GitNotInitializedError, TagAlreadyExistsError, tag_snapshot
from plot_mcp.models import CanvasKind
from plot_mcp.workspace import workspace_root_from_plot_root


def _git_not_initialized_response(workspace_root: object) -> JSONResponse:
    """Structured 409 the viewer turns into the 'Initialize git repo?' modal
    (D-2026-06-11-D)."""
    return JSONResponse(
        {
            "error": "git not initialized in workspace",
            "needs_git_init": True,
            "workspace_root": str(workspace_root),
        },
        status_code=409,
    )

# ---------------------------------------------------------------------------
# v0.24.13 (D-2026-05-21-B) — project-level blueprint publish endpoint
# ---------------------------------------------------------------------------


def _bump_blueprint_version(current: str, bump: str) -> str:
    """Bump ``v<MAJOR>.<MINOR>.<PATCH>`` per the chosen level.

    - "major": ``v1.2.3`` → ``v2.0.0``
    - "minor": ``v1.2.3`` → ``v1.3.0``
    - "patch": ``v1.2.3`` → ``v1.2.4``
    """
    if not current.startswith("v"):
        raise ValueError(f"invalid blueprint version (must start with 'v'): {current!r}")
    parts = current[1:].split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"invalid semver (need v<MAJOR>.<MINOR>.<PATCH>): {current!r}")
    major, minor, patch = (int(p) for p in parts)
    if bump == "major":
        return f"v{major + 1}.0.0"
    if bump == "minor":
        return f"v{major}.{minor + 1}.0"
    if bump == "patch":
        return f"v{major}.{minor}.{patch + 1}"
    raise ValueError(f"bump must be one of major/minor/patch, got {bump!r}")


async def project_publish_endpoint(request: Request) -> JSONResponse:
    """``POST /api/projects/{project_id}/publish``

    Body: ``{"bump": "major" | "minor" | "patch", "message": "..."}``

    Bumps ``ProjectDoc.blueprint_version``, persists the project, and
    creates a git tag at the resulting version. Tag name = the new
    version string (e.g. ``v0.2.0``). Idempotent for the *project*
    write (tags are unique, second call with the same target version
    after manual revert would 409).

    Returns ``{from_version, to_version, tag}``.
    """
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
    bump = body.get("bump")
    if bump not in ("major", "minor", "patch"):
        return _error("'bump' must be one of major/minor/patch")
    message_input = body.get("message")
    message = (
        message_input
        if isinstance(message_input, str) and message_input.strip()
        else None
    )

    from plot_mcp.folder_io import read_project, write_project

    project = read_project(plot_root, project_id)
    from_version = project.blueprint_version
    try:
        to_version = _bump_blueprint_version(from_version, bump)
    except ValueError as exc:
        return _error(str(exc))
    bumped = project.model_copy(update={"blueprint_version": to_version})
    write_project(plot_root, bumped)
    workspace_root = workspace_root_from_plot_root(plot_root)
    try:
        tag = tag_snapshot(workspace_root, to_version, message=message or to_version)
    except GitNotInitializedError:
        write_project(plot_root, project)
        return _git_not_initialized_response(workspace_root)
    except TagAlreadyExistsError as exc:
        # Roll back the project version on tag collision.
        write_project(plot_root, project)
        return _error(str(exc), status=409)
    return JSONResponse(
        {"from_version": from_version, "to_version": to_version, "tag": tag},
        status_code=201,
    )


# ---------------------------------------------------------------------------
# v0.18.0 Phase 3 (D-2026-05-16-E) — publish endpoint
# ---------------------------------------------------------------------------


async def node_publish_endpoint(request: Request) -> JSONResponse:
    """``POST /api/projects/{project_id}/canvases/{canvas_kind}/nodes/{node_id}/publish``

    Optional query parameter ``service_id`` for feature canvases.
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
    except GitNotInitializedError:
        return _git_not_initialized_response(workspace_root_from_plot_root(plot_root))
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

    Optional ``service_id`` for feature canvases.
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
    except GitNotInitializedError:
        return _git_not_initialized_response(workspace_root_from_plot_root(plot_root))
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
    # Resolve the canvas to locate the node + derive its kind.
    from plot_mcp.folder_io import read_canvas

    try:
        canvas = read_canvas(
            plot_root, project_id, cast("CanvasKind", canvas_kind), service_id
        )
    except FileNotFoundError as exc:
        return _error(str(exc), status=404)
    except ValueError as exc:
        # v0.27.13 (D-2026-05-28-H) — read_canvas raises ValueError when
        # canvas_kind=="feature" but service_id is missing. Surface
        # as 400 so the caller gets a useful message instead of an
        # uncaught-exception 500.
        return _error(str(exc), status=400)
    node = next((n for n in canvas.nodes if n.id == node_id), None)
    if node is None:
        return _error(f"node not found: {node_id}", status=404)
    # v0.24.3 (D-2026-05-18-A) — folder name = node id, not slug.
    from plot_mcp.folder_io import _canvas_file

    canvas_dir = _canvas_file(
        plot_root, project_id, cast("CanvasKind", canvas_kind), service_id
    ).parent
    node_dir = canvas_dir / "published" / node.kind / node.id
    if not node_dir.is_dir():
        return JSONResponse({"versions": []})
    versions: list[dict[str, Any]] = []
    for entry in node_dir.iterdir():
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
