"""Folder-based project store for Plot v0.2 multi-canvas.

Disk layout
-----------

    .plot/sketches/{project_id}/
        project.json                 — ProjectDoc
        core.json                    — CanvasDoc (canvas_kind = "core")
        actors.json                  — CanvasDoc (canvas_kind = "actors")
        services-overview.json       — CanvasDoc (canvas_kind = "services_overview")
        services-detail/
            {service_id}.json        — CanvasDoc (canvas_kind = "service_detail")

Every canvas lives in its own file so a write to one canvas never
touches another. Thin wrapper: no caching, atomic replace only.

The old ``sketches.py`` single-file store stays alongside during the
v0.1 → v0.2 migration window.
"""

from __future__ import annotations

import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, cast

from plot_mcp.models import CanvasDoc, CanvasKind, ProjectDoc, SketchNode

_SINGLETON_CANVAS_FILES: dict[str, str] = {
    "core": "core.json",
    "actors": "actors.json",
    "services_overview": "services-overview.json",
}
_DETAIL_SUBDIR = "services-detail"


# ---------------------------------------------------------------------------
# path helpers
# ---------------------------------------------------------------------------


def _sketches_dir(plot_root: Path) -> Path:
    d = plot_root / "sketches"
    d.mkdir(exist_ok=True)
    return d


def _project_dir(plot_root: Path, project_id: str) -> Path:
    return _sketches_dir(plot_root) / project_id


def _project_file(plot_root: Path, project_id: str) -> Path:
    return _project_dir(plot_root, project_id) / "project.json"


def _canvas_file(
    plot_root: Path,
    project_id: str,
    canvas_kind: CanvasKind,
    service_id: str | None = None,
) -> Path:
    folder = _project_dir(plot_root, project_id)
    if canvas_kind == "service_detail":
        if not service_id:
            raise ValueError("service_detail requires service_id")
        return folder / _DETAIL_SUBDIR / f"{service_id}.json"
    return folder / _SINGLETON_CANVAS_FILES[canvas_kind]


def _ensure_project(plot_root: Path, project_id: str) -> Path:
    folder = _project_dir(plot_root, project_id)
    if not folder.is_dir():
        raise FileNotFoundError(f"project not found: {project_id}")
    return folder


# ---------------------------------------------------------------------------
# atomic JSON helpers
# ---------------------------------------------------------------------------


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    """Atomic write — tmp file then rename, so readers never see half a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp.replace(path)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"file not found: {path}")
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


# ---------------------------------------------------------------------------
# project-level IO
# ---------------------------------------------------------------------------


def read_project(plot_root: Path, project_id: str) -> ProjectDoc:
    _ensure_project(plot_root, project_id)
    raw = _read_json(_project_file(plot_root, project_id))
    return ProjectDoc.model_validate(raw)


def write_project(plot_root: Path, project: ProjectDoc) -> None:
    """Persist metadata, refreshing ``updated`` to now."""
    _ensure_project(plot_root, project.id)
    refreshed = project.model_copy(update={"updated": datetime.now(UTC).isoformat()})
    _write_json(
        _project_file(plot_root, project.id),
        refreshed.model_dump(),
    )


# ---------------------------------------------------------------------------
# canvas-level IO
# ---------------------------------------------------------------------------


def read_canvas(
    plot_root: Path,
    project_id: str,
    canvas_kind: CanvasKind,
    service_id: str | None = None,
) -> CanvasDoc:
    _ensure_project(plot_root, project_id)
    path = _canvas_file(plot_root, project_id, canvas_kind, service_id)
    raw = _read_json(path)
    return CanvasDoc.model_validate(raw)


def write_canvas(plot_root: Path, project_id: str, canvas: CanvasDoc) -> None:
    _ensure_project(plot_root, project_id)
    service_id = canvas.service_ref if canvas.canvas_kind == "service_detail" else None
    path = _canvas_file(plot_root, project_id, canvas.canvas_kind, service_id)
    _write_json(path, canvas.model_dump(by_alias=True))
    # bump project.updated whenever a canvas changes
    try:
        meta = read_project(plot_root, project_id)
    except FileNotFoundError:
        return
    write_project(plot_root, meta)


def list_service_details(plot_root: Path, project_id: str) -> list[str]:
    """Return the service ids for which a Detail canvas exists."""
    _ensure_project(plot_root, project_id)
    folder = _project_dir(plot_root, project_id) / _DETAIL_SUBDIR
    if not folder.is_dir():
        return []
    return sorted(p.stem for p in folder.glob("*.json"))


# ---------------------------------------------------------------------------
# create / delete
# ---------------------------------------------------------------------------


def _seed_core_canvas() -> CanvasDoc:
    """Minimum valid Core canvas — root + mission + identity (no core values yet)."""
    return CanvasDoc(
        canvas_id="core",
        canvas_kind="core",
        nodes=[
            SketchNode(
                id="core-root",
                kind="core",
                label="Project",
                x=-90,
                y=-70,
                width=180,
                height=140,
                color="#fde68a",
                shape="octagon",
                icon="star",
            ),
            SketchNode(
                id="mission",
                kind="mission",
                parent_id="core-root",
                label="Mission",
                x=260,
                y=-20,
                width=200,
                height=90,
                color="#fef3c7",
                shape="rounded",
                icon="star",
            ),
            SketchNode(
                id="identity",
                kind="identity",
                parent_id="core-root",
                label="Identity",
                x=260,
                y=120,
                width=200,
                height=90,
                color="#fed7aa",
                shape="rounded",
                icon="star",
            ),
        ],
    )


def create_project(plot_root: Path, project_id: str, name: str) -> ProjectDoc:
    """Create a fresh project folder, seeded with Core / Actors / Services-Overview.

    Raises ``FileExistsError`` if ``project_id`` is taken.
    """
    folder = _project_dir(plot_root, project_id)
    if folder.exists():
        raise FileExistsError(f"project already exists: {project_id}")
    folder.mkdir(parents=True)
    (folder / _DETAIL_SUBDIR).mkdir()

    now = datetime.now(UTC).isoformat()
    proj = ProjectDoc(
        id=project_id,
        name=name or project_id,
        created=date.today().isoformat(),
        updated=now,
        version=2,
    )
    _write_json(_project_file(plot_root, project_id), proj.model_dump())

    _write_json(
        _canvas_file(plot_root, project_id, "core"),
        _seed_core_canvas().model_dump(by_alias=True),
    )
    _write_json(
        _canvas_file(plot_root, project_id, "actors"),
        CanvasDoc(canvas_id="actors", canvas_kind="actors").model_dump(by_alias=True),
    )
    _write_json(
        _canvas_file(plot_root, project_id, "services_overview"),
        CanvasDoc(
            canvas_id="services_overview",
            canvas_kind="services_overview",
        ).model_dump(by_alias=True),
    )
    return proj


def delete_project(plot_root: Path, project_id: str) -> None:
    folder = _project_dir(plot_root, project_id)
    if not folder.exists():
        raise FileNotFoundError(f"project not found: {project_id}")
    shutil.rmtree(folder)


# ---------------------------------------------------------------------------
# Overview ↔ Detail sync
# ---------------------------------------------------------------------------


def sync_details_with_overview(plot_root: Path, project_id: str) -> dict[str, list[str]]:
    """Ensure services-detail/{id}.json exists for every service in the Overview.

    Services that disappear from the Overview have their Detail files moved
    to ``services-detail/_archive/{id}.json`` — a destructive delete would
    throw away user work on a stray click. Called opportunistically after
    writes to the Overview canvas.

    Returns ``{"created": [...], "archived": [...]}`` for telemetry.
    """
    _ensure_project(plot_root, project_id)
    try:
        overview = read_canvas(plot_root, project_id, "services_overview")
    except FileNotFoundError:
        return {"created": [], "archived": []}
    overview_service_ids = {n.id for n in overview.nodes if n.kind == "service"}
    detail_folder = _project_dir(plot_root, project_id) / _DETAIL_SUBDIR
    existing_details = {p.stem for p in detail_folder.glob("*.json")}

    created: list[str] = []
    for service_id in sorted(overview_service_ids - existing_details):
        src = next(n for n in overview.nodes if n.id == service_id)
        detail = CanvasDoc(
            canvas_id=service_id,
            canvas_kind="service_detail",
            service_ref=service_id,
            nodes=[src.model_copy(update={"parent_id": None, "is_root": False})],
        )
        _write_json(
            _canvas_file(plot_root, project_id, "service_detail", service_id=service_id),
            detail.model_dump(by_alias=True),
        )
        created.append(service_id)

    archive_folder = detail_folder / "_archive"
    archived: list[str] = []
    for service_id in sorted(existing_details - overview_service_ids):
        archive_folder.mkdir(exist_ok=True)
        src_path = detail_folder / f"{service_id}.json"
        dst_path = archive_folder / f"{service_id}.json"
        src_path.replace(dst_path)
        archived.append(service_id)

    return {"created": created, "archived": archived}
