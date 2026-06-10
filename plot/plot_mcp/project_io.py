"""ProjectDoc read/write, seeds, create/rename/delete.

Split out of the folder_io god-module (D-2026-06-10-D). folder_io.py re-exports
everything, so import sites and tests are unchanged.
"""

from __future__ import annotations

import shutil
from datetime import UTC, date, datetime
from pathlib import Path

from plot_mcp.canvas_io import list_service_details, read_canvas, write_canvas  # noqa: F401
from plot_mcp.git_store import (
    ensure_repo,
)
from plot_mcp.models import (
    ActorNode,
    CanvasDoc,
    CoreValueNode,
    IdentityNode,
    MissionNode,
    ProjectDoc,
)
from plot_mcp.storage import (  # noqa: F401
    _canvas_file,
    _ensure_project,
    _project_dir,
    _project_file,
    _read_json,
    _write_json,
    read_project,
    write_project,
)

# ---------------------------------------------------------------------------
# project-level IO
# ---------------------------------------------------------------------------



def rename_project(plot_root: Path, project_id: str, new_name: str) -> ProjectDoc:
    """Update ``ProjectDoc.name``. v0.13 Phase 0: there is no per-canvas
    project node any more — label is derived from ProjectDoc.name at render
    time. Touching the foundation canvas via read still triggers the
    legacy-anchor eviction migrator for old projects.
    """
    proj = read_project(plot_root, project_id)
    renamed = proj.model_copy(update={"name": new_name})
    write_project(plot_root, renamed)
    # v0.13 Phase 0: project anchors no longer carry the label as a node
    # field — label SSOT is ProjectDoc.name, derived at render. Touch the
    # foundation canvas via read so the legacy-anchor eviction migrator
    # runs if the project predates v0.13.
    try:
        read_canvas(plot_root, project_id, "foundation")
    except FileNotFoundError:
        pass
    return read_project(plot_root, project_id)


# ---------------------------------------------------------------------------
# create / delete
# ---------------------------------------------------------------------------


def _seed_foundation_canvas(project_name: str) -> CanvasDoc:  # noqa: ARG001
    """Minimum valid Foundation canvas — Mission / Core Value / Identity.

    v0.13 Phase 0: the Project anchor is no longer a node here. It lives in
    ``ProjectDoc.anchors["foundation"]`` and is rendered by the viewer at
    display time. ``project_name`` argument retained for signature stability
    but unused.
    """
    return CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[
            MissionNode(
                id="mission",
                label="Mission",
                x=-360,
                y=-45,
                width=200,
                height=90,
                color="#fef3c7",
                shape="rounded",
            ),
            CoreValueNode(
                id="core-value-1",
                label="Core value",
                x=-90,
                y=-260,
                width=180,
                height=80,
                color="#fde68a",
                shape="rounded",
            ),
            IdentityNode(
                id="identity",
                label="Voice",
                x=160,
                y=-45,
                width=200,
                height=90,
                color="#fed7aa",
                shape="rounded",
            ),
        ],
    )


def _seed_actors_canvas(project_name: str) -> CanvasDoc:  # noqa: ARG001
    """v0.11 — actors canvas seeds with two placeholder classes ("Operator"
    and "User") to satisfy the IDENTITY.md "≥ 2 actor classes" minimum.

    v0.13 Phase 0: project anchor moved to ``ProjectDoc.anchors``; not seeded
    here.
    """
    return CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=[
            ActorNode(
                id="operator",
                label="Operator",
                side="operator",
                x=-260,
                y=-50,
                width=140,
                height=80,
                color="#bae6fd",
                shape="rounded",
            ),
            ActorNode(
                id="user",
                label="User",
                side="user",
                x=140,
                y=-50,
                width=140,
                height=80,
                color="#fecaca",
                shape="rounded",
            ),
        ],
    )


def _seed_services_canvas(project_name: str) -> CanvasDoc:  # noqa: ARG001
    """v0.13 Phase 0: services canvas starts empty (project anchor moved to
    ``ProjectDoc.anchors``). Categories + services are added by the user.
    """
    return CanvasDoc(
        canvas_id="services",
        canvas_kind="services",
        nodes=[],
    )


def create_project(plot_root: Path, project_id: str, name: str) -> ProjectDoc:
    """Create a fresh project folder, seeded with Core / Actors / Services.

    v0.8 layout: one folder per project (``.plot/{project_id}/``) with a
    subfolder per canvas kind. Each canvas folder holds a ``canvas.json``.
    Service-detail canvases join the relevant service folder later via
    ``sync_details_with_overview``.

    Raises ``FileExistsError`` if ``project_id`` is taken.
    """
    folder = _project_dir(plot_root, project_id)
    if folder.exists():
        raise FileExistsError(f"project already exists: {project_id}")
    folder.mkdir(parents=True)
    # Initialise the workspace-level git repo (at plot_root = .plot/) now so
    # ``tag_snapshot`` works later without any extra wiring. One repo tracks
    # every project in the workspace; it stays empty until the first tag.
    # (D-2026-06-09-C — git lives at the workspace, not per project.)
    ensure_repo(plot_root)

    now = datetime.now(UTC).isoformat()
    proj = ProjectDoc(
        id=project_id,
        name=name or project_id,
        created=date.today().isoformat(),
        updated=now,
        version=3,
    )
    _write_json(_project_file(plot_root, project_id), proj.model_dump())

    _write_json(
        _canvas_file(plot_root, project_id, "foundation"),
        _seed_foundation_canvas(proj.name).model_dump(by_alias=True),
    )
    _write_json(
        _canvas_file(plot_root, project_id, "actors"),
        _seed_actors_canvas(proj.name).model_dump(by_alias=True),
    )
    _write_json(
        _canvas_file(plot_root, project_id, "services"),
        _seed_services_canvas(proj.name).model_dump(by_alias=True),
    )
    # v0.13 Phase 2 — write per-kind JSON Schema + MD template files into
    # ``.plot/{proj}/schema/`` so external tools (Obsidian YAML LSP, custom
    # validators) can verify Foundation node files.
    from plot_mcp.schema_export import export_all_schemas

    export_all_schemas(plot_root, project_id)
    return proj


def delete_project(plot_root: Path, project_id: str) -> None:
    folder = _project_dir(plot_root, project_id)
    if not folder.exists():
        raise FileNotFoundError(f"project not found: {project_id}")
    shutil.rmtree(folder)


