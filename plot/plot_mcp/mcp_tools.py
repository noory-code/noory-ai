"""FastMCP tool surface for Plot.

Five tools map 1:1 to the HTTP sketch endpoints. Claude Code uses these to
read the current map, propose additions, and mutate sketches on the user's
behalf — the "AI collaborates on the same canvas" loop.
"""

from __future__ import annotations

import webbrowser
from typing import Any

from fastmcp import FastMCP

from plot_mcp.models import SketchDoc
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
