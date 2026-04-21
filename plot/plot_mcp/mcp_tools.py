"""FastMCP tool surface for Plot.

Five tools map 1:1 to the HTTP sketch endpoints. Claude Code uses these to
read the current map, propose additions, and mutate sketches on the user's
behalf — the "AI collaborates on the same canvas" loop.
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
from plot_mcp.migrate import migrate_v01_to_v02
from plot_mcp.models import CanvasDoc, CanvasKind, SketchDoc
from plot_mcp.sketches import (
    create_sketch,
    delete_sketch,
    list_sketches,
    read_sketch,
    write_sketch,
)
from plot_mcp.workspace import resolve_plot_root, resolved_port

mcp = FastMCP(
    "plot",
    instructions=(
        "Plot exposes a project's sketch canvas as a typed list of nodes and "
        "edges. Use `list_sketches(project_path)` to enumerate, `get_sketch` to "
        "read one, and `update_sketch` to write back the full document after "
        "any edit. Sketches are schema-free — labels and edge semantics are up "
        "to the author; treat node.label and edge.label as the primary signal "
        "when reasoning about the map."
    ),
)


@mcp.tool()
def list_sketches_tool(project_path: str) -> list[dict[str, Any]]:
    """List all sketches in ``{project_path}/.plot/sketches/``."""
    plot_root = resolve_plot_root(project_path)
    return [s.model_dump() for s in list_sketches(plot_root)]


@mcp.tool()
def get_sketch(project_path: str, sketch_id: str) -> dict[str, Any]:
    """Read a single sketch document."""
    plot_root = resolve_plot_root(project_path)
    doc = read_sketch(plot_root, sketch_id)
    return doc.model_dump(by_alias=True)


@mcp.tool()
def create_sketch_tool(project_path: str, sketch_id: str, name: str = "") -> dict[str, Any]:
    """Create an empty sketch. ``sketch_id`` must be unique and kebab-case."""
    plot_root = resolve_plot_root(project_path)
    doc = create_sketch(plot_root, sketch_id, name)
    return doc.model_dump(by_alias=True)


@mcp.tool()
def update_sketch(project_path: str, sketch_id: str, doc: dict[str, Any]) -> dict[str, Any]:
    """Overwrite ``sketch_id`` with the given document. Returns the written document."""
    plot_root = resolve_plot_root(project_path)
    payload = dict(doc)
    payload["id"] = sketch_id
    validated = SketchDoc.model_validate(payload)
    write_sketch(plot_root, validated)
    return validated.model_dump(by_alias=True)


@mcp.tool()
def delete_sketch_tool(project_path: str, sketch_id: str) -> str:
    """Delete a sketch file."""
    plot_root = resolve_plot_root(project_path)
    delete_sketch(plot_root, sketch_id)
    return f"deleted {sketch_id}"


@mcp.tool()
def open_canvas(project_path: str, sketch_id: str | None = None) -> str:
    """Open the Plot viewer in the default browser."""
    resolve_plot_root(project_path)  # raises if path is unusable
    port = resolved_port()
    url = f"http://127.0.0.1:{port}/?project_path={project_path}"
    if sketch_id:
        url += f"&sketch={sketch_id}"
    webbrowser.open(url)
    return f"Opened {url}"


# ---------------------------------------------------------------------------
# v0.2 multi-canvas tools (project folder layout)
# ---------------------------------------------------------------------------
#
# These operate on the per-canvas files under ``.plot/sketches/{project}/``.
# Claude Code reads/writes one canvas at a time instead of the whole sketch.


@mcp.tool()
def list_projects(project_path: str) -> list[dict[str, Any]]:
    """List every v0.2 project folder under ``.plot/sketches/``."""
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
    """Read a project's metadata + its detail canvas ids."""
    plot_root = resolve_plot_root(project_path)
    proj = read_project(plot_root, project_id)
    detail_ids = list_service_details(plot_root, project_id)
    return {**proj.model_dump(), "service_details": detail_ids}


@mcp.tool()
def create_project_tool(
    project_path: str, project_id: str, name: str = ""
) -> dict[str, Any]:
    """Create a new v0.2 project folder seeded with Core / Actors / Services-Overview."""
    plot_root = resolve_plot_root(project_path)
    proj = create_project(plot_root, project_id, name)
    return proj.model_dump()


@mcp.tool()
def delete_project_tool(project_path: str, project_id: str) -> str:
    """Delete a project folder. Detail canvases and their archives go with it."""
    plot_root = resolve_plot_root(project_path)
    delete_project(plot_root, project_id)
    return f"deleted {project_id}"


@mcp.tool()
def get_canvas(
    project_path: str,
    project_id: str,
    canvas_kind: CanvasKind,
    service_id: str | None = None,
) -> dict[str, Any]:
    """Read a single canvas — ``canvas_kind`` is one of ``core`` / ``actors`` /
    ``services_overview`` / ``service_detail``. ``service_id`` is required
    for ``service_detail``."""
    plot_root = resolve_plot_root(project_path)
    canvas = read_canvas(plot_root, project_id, canvas_kind, service_id)
    return canvas.model_dump(by_alias=True)


@mcp.tool()
def update_canvas(
    project_path: str, project_id: str, canvas: dict[str, Any]
) -> dict[str, Any]:
    """Overwrite a canvas. Writing the Overview auto-creates / archives
    Detail canvases to match; the response reports what changed so the
    caller can reconcile its UI."""
    plot_root = resolve_plot_root(project_path)
    validated = CanvasDoc.model_validate(canvas)
    write_canvas(plot_root, project_id, validated)
    sync: dict[str, list[str]] = {"created": [], "archived": []}
    if validated.canvas_kind == "services_overview":
        sync = sync_details_with_overview(plot_root, project_id)
    return {"canvas": validated.model_dump(by_alias=True), "sync": sync}


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
def list_detail_canvases(project_path: str, project_id: str) -> list[str]:
    """Return the service ids that have their own Detail canvas."""
    plot_root = resolve_plot_root(project_path)
    return list_service_details(plot_root, project_id)


@mcp.tool()
def migrate_v01_sketches(project_path: str) -> list[str]:
    """Migrate any ``sketches/*.json`` (v0.1) files to the v0.2 folder layout.

    Idempotent. Returns the list of project ids that were migrated.
    The originals are renamed to ``{id}.json.v01.bak``.
    """
    plot_root = resolve_plot_root(project_path)
    return migrate_v01_to_v02(plot_root)
