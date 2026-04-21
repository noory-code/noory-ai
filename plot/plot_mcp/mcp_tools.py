"""FastMCP tool surface for Plot (v0.4).

Claude Code uses these tools to read and mutate a Plot project. The
surface mirrors the HTTP API one-to-one so a session can move between
both interchangeably.
"""

from __future__ import annotations

import webbrowser
from typing import Any

from fastmcp import FastMCP

from plot_mcp.folder_io import (
    create_project,
    delete_project,
    list_service_details,
    read_canvas,
    read_project,
    sync_details_with_overview,
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
from plot_mcp.workspace import resolve_plot_root, resolved_port

mcp = FastMCP(
    "plot",
    instructions=(
        "Plot stores projects as folders of per-canvas JSON files under "
        "``.plot/sketches/{project}/``. Use ``list_projects`` / ``get_project`` "
        "to discover state, ``get_canvas`` / ``update_canvas`` to read or write "
        "a single canvas (``core`` / ``actors`` / ``services_overview`` / "
        "``service_detail``), and ``tag_project`` to plant a named milestone "
        "in the project's git repo. Edits are never auto-committed — only the "
        "tag tools touch git."
    ),
)


# ---------------------------------------------------------------------------
# project CRUD
# ---------------------------------------------------------------------------


@mcp.tool()
def list_projects(project_path: str) -> list[dict[str, Any]]:
    """List every v0.4 project folder under ``.plot/sketches/``."""
    plot_root = resolve_plot_root(project_path)
    folder = plot_root / "sketches"
    if not folder.is_dir():
        return []
    projects: list[dict[str, Any]] = []
    for child in sorted(folder.iterdir()):
        if not child.is_dir():
            continue
        try:
            proj = read_project(plot_root, child.name)
        except (FileNotFoundError, ValueError):
            continue
        projects.append(proj.model_dump())
    projects.sort(key=lambda p: p.get("updated", ""), reverse=True)
    return projects


@mcp.tool()
def get_project(project_path: str, project_id: str) -> dict[str, Any]:
    """Read a project's metadata + its service-detail ids + tags."""
    plot_root = resolve_plot_root(project_path)
    proj = read_project(plot_root, project_id)
    return {
        **proj.model_dump(),
        "service_details": list_service_details(plot_root, project_id),
        "tags": list_tags(plot_root / "sketches" / project_id),
    }


@mcp.tool()
def create_project_tool(
    project_path: str, project_id: str, name: str = ""
) -> dict[str, Any]:
    """Create a new project folder seeded with Core / Actors / Services-Overview."""
    plot_root = resolve_plot_root(project_path)
    proj = create_project(plot_root, project_id, name)
    return proj.model_dump()


@mcp.tool()
def rename_project(
    project_path: str, project_id: str, name: str
) -> dict[str, Any]:
    """Update a project's ``name`` without touching its canvases."""
    plot_root = resolve_plot_root(project_path)
    proj = read_project(plot_root, project_id)
    renamed = proj.model_copy(update={"name": name})
    write_project(plot_root, renamed)
    return read_project(plot_root, project_id).model_dump()


@mcp.tool()
def delete_project_tool(project_path: str, project_id: str) -> str:
    """Delete a project folder (and its git repo)."""
    plot_root = resolve_plot_root(project_path)
    delete_project(plot_root, project_id)
    return f"deleted {project_id}"


# ---------------------------------------------------------------------------
# canvas read / write
# ---------------------------------------------------------------------------


@mcp.tool()
def get_canvas(
    project_path: str,
    project_id: str,
    canvas_kind: CanvasKind,
    service_id: str | None = None,
) -> dict[str, Any]:
    """Read a single canvas. ``canvas_kind`` ∈ ``core`` / ``actors`` /
    ``services_overview`` / ``service_detail``. ``service_id`` is
    required when ``canvas_kind == "service_detail"``."""
    plot_root = resolve_plot_root(project_path)
    canvas = read_canvas(plot_root, project_id, canvas_kind, service_id)
    return canvas.model_dump(by_alias=True)


@mcp.tool()
def update_canvas(
    project_path: str, project_id: str, canvas: dict[str, Any]
) -> dict[str, Any]:
    """Overwrite a canvas. Writing ``services_overview`` auto-creates /
    archives Detail canvases so Overview and Detail stay 1:1. The
    response reports the reconciliation."""
    plot_root = resolve_plot_root(project_path)
    validated = CanvasDoc.model_validate(canvas)
    write_canvas(plot_root, project_id, validated)
    sync: dict[str, list[str]] = {"created": [], "archived": []}
    if validated.canvas_kind == "services_overview":
        sync = sync_details_with_overview(plot_root, project_id)
    return {"canvas": validated.model_dump(by_alias=True), "sync": sync}


@mcp.tool()
def list_detail_canvases(project_path: str, project_id: str) -> list[str]:
    """Return the service ids that have their own Detail canvas."""
    plot_root = resolve_plot_root(project_path)
    return list_service_details(plot_root, project_id)


# ---------------------------------------------------------------------------
# git session tags
# ---------------------------------------------------------------------------


@mcp.tool()
def tag_project(
    project_path: str,
    project_id: str,
    name: str,
    message: str | None = None,
) -> dict[str, Any]:
    """Plant a named git tag at the current state of the project. Use this
    at the start or end of a work session ("session-banas-start",
    "before-refactor") — day-to-day edits don't commit, only tags do."""
    plot_root = resolve_plot_root(project_path)
    try:
        return tag_snapshot(
            plot_root / "sketches" / project_id, name, message=message
        )
    except TagAlreadyExistsError as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
def list_project_tags(project_path: str, project_id: str) -> list[dict[str, Any]]:
    """Return tags for a project, newest first."""
    plot_root = resolve_plot_root(project_path)
    return list_tags(plot_root / "sketches" / project_id)


@mcp.tool()
def delete_project_tag(project_path: str, project_id: str, name: str) -> str:
    """Drop a tag from a project. The commit it pointed at stays reachable."""
    plot_root = resolve_plot_root(project_path)
    try:
        delete_tag(plot_root / "sketches" / project_id, name)
    except KeyError as exc:
        raise ValueError(f"tag not found: {exc.args[0]}") from exc
    return f"deleted tag {name}"


# ---------------------------------------------------------------------------
# migration + utility
# ---------------------------------------------------------------------------


@mcp.tool()
def migrate_v01_sketches(project_path: str) -> list[str]:
    """Migrate any ``sketches/*.json`` (v0.1) files to the v0.4 folder layout.

    Idempotent. Returns the list of project ids that were migrated.
    Originals rename to ``{id}.json.v01.bak``. This also runs automatically
    whenever ``GET /api/projects`` is called from the viewer.
    """
    plot_root = resolve_plot_root(project_path)
    return migrate_v01_to_v02(plot_root)


@mcp.tool()
def open_canvas(project_path: str, project_id: str | None = None) -> str:
    """Open the Plot viewer in the default browser."""
    resolve_plot_root(project_path)  # raises if path is unusable
    port = resolved_port()
    url = f"http://127.0.0.1:{port}/?project_path={project_path}"
    if project_id:
        url += f"&project={project_id}"
    webbrowser.open(url)
    return f"Opened {url}"
