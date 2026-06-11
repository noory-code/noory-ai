"""FastMCP tool surface for Plot (v0.4).

Claude Code uses these tools to read and mutate a Plot project. The
surface mirrors the HTTP API one-to-one so a session can move between
both interchangeably.
"""

from __future__ import annotations

import webbrowser
from pathlib import Path
from typing import Any, cast

from fastmcp import FastMCP

from plot_mcp.folder_io import (
    PublishNotEligibleError,
    create_project,
    delete_project,
    list_service_details,
    publish_node,
    read_canvas,
    read_project,
    sync_details_with_overview,
    write_canvas,
)
from plot_mcp.folder_io import (
    rename_project as rename_project_folder,
)
from plot_mcp.git_store import (
    GitNotInitializedError,
    TagAlreadyExistsError,
    delete_tag,
    list_tags,
    tag_snapshot,
)
from plot_mcp.migrate import migrate_v01_to_v02
from plot_mcp.models import CanvasDoc, CanvasKind
from plot_mcp.workspace import (
    discover_projects,
    enumerate_projects,
    resolve_plot_root,
    resolved_port,
    workspace_root_from_plot_root,
)

mcp = FastMCP(
    "plot",
    instructions=(
        "Plot stores projects as folders of per-canvas JSON files under "
        "``.noory/plot/{project}/``. Use ``list_projects`` / ``get_project`` "
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
    """List every project folder directly under ``.noory/plot/`` (R9 layout)."""
    plot_root = resolve_plot_root(project_path)
    return [p.model_dump() for p in enumerate_projects(plot_root)]


@mcp.tool()
def discover_workspace_projects(project_path: str) -> list[dict[str, Any]]:
    """Discover every Plot project anywhere under the workspace root, each with
    its directory relative to the root (``"."`` for a root-level project).

    Mirrors ``GET /api/workspace/projects`` (v0.32.0)."""
    root = Path(project_path).expanduser().resolve()
    return [{"project": p.model_dump(), "dir": d} for p, d in discover_projects(root)]


@mcp.tool()
def get_project(project_path: str, project_id: str) -> dict[str, Any]:
    """Read a project's metadata + its service-detail ids + tags."""
    plot_root = resolve_plot_root(project_path)
    proj = read_project(plot_root, project_id)
    return {
        **proj.model_dump(),
        "service_details": list_service_details(plot_root, project_id),
        "tags": list_tags(workspace_root_from_plot_root(plot_root)),
    }


@mcp.tool()
def create_project_tool(project_path: str, project_id: str, name: str = "") -> dict[str, Any]:
    """Create a new project folder seeded with Core / Actors / Services-Overview."""
    plot_root = resolve_plot_root(project_path)
    proj = create_project(plot_root, project_id, name)
    return proj.model_dump()


@mcp.tool()
def rename_project(project_path: str, project_id: str, name: str) -> dict[str, Any]:
    """Update a project's ``name`` and mirror it onto the Core canvas's
    Project anchor label in one shot."""
    plot_root = resolve_plot_root(project_path)
    return rename_project_folder(plot_root, project_id, name).model_dump()


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
def update_canvas(project_path: str, project_id: str, canvas: dict[str, Any]) -> dict[str, Any]:
    """Overwrite a canvas. Writing ``services_overview`` auto-creates /
    archives Detail canvases so Overview and Detail stay 1:1. The
    response reports the reconciliation."""
    plot_root = resolve_plot_root(project_path)
    validated = CanvasDoc.model_validate(canvas)
    write_canvas(plot_root, project_id, validated)
    sync: dict[str, list[str]] = {"created": [], "archived": [], "skipped_archive": []}
    if validated.canvas_kind == "services":
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
    workspace_root = workspace_root_from_plot_root(plot_root)
    try:
        # D-2026-06-11-C/D — git lives at the workspace root. The tag
        # snapshots `.noory/plot/` inside that repo, not a single project.
        # project_id is kept on the tool signature for call-site clarity
        # and future per-project naming.
        return tag_snapshot(workspace_root, name, message=message)
    except GitNotInitializedError as exc:
        raise ValueError(
            f"git not initialized at workspace root {workspace_root}. "
            "Open the workspace in the viewer and accept the 'Initialize "
            "git repo' prompt, or run `git init` there manually."
        ) from exc
    except TagAlreadyExistsError as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
def publish_node_tool(
    project_path: str,
    project_id: str,
    canvas_kind: str,
    node_id: str,
    service_id: str | None = None,
) -> dict[str, Any]:
    """Publish a single node (D-2026-05-16-E + D-2026-05-17-C).

    Bumps the node's ``version`` MAJOR component (``v1.0`` → ``v2.0``),
    writes a per-node MD file at
    ``<canvas>/published/{kind}-{slug}-{version}.md``, MINOR-propagates
    the bump up the ``parent_id`` chain (v0.20.0 / D-2026-05-17-C), and
    creates a single git commit with machine-readable ``Publish-*:``
    base trailers + one ``Publish-Propagated-Ancestor:`` trailer per
    bumped ancestor.

    Eligibility: project anchor / ``service`` is_root (ServiceDetail
    mirror) / ``*_ref`` kinds are rejected with ValueError. All other
    kinds are publish-eligible — including ``actor`` is_root masters
    like Bana / Admin / Guest (v0.24.10 / D-2026-05-19-C).

    Returns ``{node_id, from_version, to_version, md_path, sha,
    propagated}``. ``propagated`` is the list of ancestor records
    (``{node_id, from_version, to_version, canvases}``) so the caller
    can refresh affected views without a separate request.
    """
    plot_root = resolve_plot_root(project_path)
    try:
        return publish_node(
            plot_root,
            project_id,
            cast("CanvasKind", canvas_kind),
            node_id,
            service_id=service_id,
        )
    except PublishNotEligibleError as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
def list_project_tags(project_path: str, project_id: str) -> list[dict[str, Any]]:
    """Return tags for a project, newest first."""
    plot_root = resolve_plot_root(project_path)
    return list_tags(workspace_root_from_plot_root(plot_root))


@mcp.tool()
def delete_project_tag(project_path: str, project_id: str, name: str) -> str:
    """Drop a tag from a project. The commit it pointed at stays reachable."""
    plot_root = resolve_plot_root(project_path)
    try:
        delete_tag(workspace_root_from_plot_root(plot_root), name)
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
