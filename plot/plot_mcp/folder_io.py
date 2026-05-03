"""Folder-based project store for Plot v0.10 (wrapper-less, canvas-grouped).

Disk layout
-----------

    .plot/{project_id}/
        project.json                     — ProjectDoc
        foundation/
            canvas.json                  — CanvasDoc (canvas_kind = "foundation")
            {node-slug}/details.md       — node long-form (opt-in per node)
        actors/
            canvas.json
            {node-slug}/details.md
        services/
            canvas.json                  — top-view (canvas_kind = "services")
            {service_id}/
                details.md               — Service node long-form
                detail.json              — CanvasDoc (canvas_kind = "service_detail")

Every canvas lives in its own file (``canvas.json`` for singletons,
``detail.json`` for service detail) so a write to one canvas never
touches another. Thin wrapper: no caching, atomic replace only.

v0.10 renamed the ``core/`` folder to ``foundation/`` to match the
underlying concept (Foundation = the project's identity). Pre-v0.10
disk layouts are healed lazily on read — see
``migrate.upgrade_foundation_canvas_if_needed``.
"""

from __future__ import annotations

import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, cast

from plot_mcp.git_store import ensure_repo
from plot_mcp.models import CanvasDoc, CanvasKind, ProjectDoc, SketchNode

# v0.8 layout: every canvas — singleton or detail — lives in a folder
# named after the canvas (or the owning service, for details), and its
# structure is always called ``canvas.json`` (or ``detail.json`` for
# service_detail). No more per-canvas filename convention to memorise.


# ---------------------------------------------------------------------------
# path helpers
# ---------------------------------------------------------------------------


def _project_dir(plot_root: Path, project_id: str) -> Path:
    return plot_root / project_id


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
        return folder / "services" / service_id / "detail.json"
    return folder / canvas_kind / "canvas.json"


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
    if canvas_kind == "foundation":
        # Heal Foundation canvases written under pre-v0.10 schemas (legacy
        # ``core`` canvas folder + ``core``/``identity_facet`` node kinds +
        # missing Project anchor) before Pydantic sees the raw dict.
        # Imported here to keep migrate.py optional on the hot path for
        # non-foundation kinds.
        from plot_mcp.migrate import upgrade_foundation_canvas_if_needed

        upgrade_foundation_canvas_if_needed(plot_root, project_id)
    path = _canvas_file(plot_root, project_id, canvas_kind, service_id)
    raw = _read_json(path)
    # v0.11.4 — actors / services canvases now carry a project anchor copy
    # (label-synced from foundation). Backfill on read for projects created
    # before v0.11.4 so the new validators / UX find the anchor present.
    if canvas_kind in ("actors", "services"):
        raw = _backfill_project_anchor(plot_root, project_id, canvas_kind, raw)
    # v0.11.5 — services canvas no longer accepts Foundation refs (they
    # moved to service_detail). Drop any stale ones from older projects so
    # the canvas validates on open. Same idempotent pattern as the anchor
    # backfill above.
    if canvas_kind == "services":
        raw = _drop_disallowed_services_kinds(plot_root, project_id, raw)
    return CanvasDoc.model_validate(raw)


def _drop_disallowed_services_kinds(
    plot_root: Path,
    project_id: str,
    raw: dict[str, Any],
) -> dict[str, Any]:
    """v0.11.5 migration helper: silently drop ``mission_ref`` / ``value_ref``
    / ``identity_ref`` (and any other now-disallowed kinds) from the services
    top view. They live in ``service_detail`` from v0.11.5 onwards.
    Idempotent.
    """
    nodes: list[dict[str, Any]] = list(raw.get("nodes") or [])
    allowed = {"service", "project"}
    kept = [n for n in nodes if n.get("kind") in allowed or n.get("kind") is None]
    if len(kept) == len(nodes):
        return raw
    raw = {**raw, "nodes": kept}
    _write_json(_canvas_file(plot_root, project_id, "services"), raw)
    return raw


def _backfill_project_anchor(
    plot_root: Path,
    project_id: str,
    canvas_kind: CanvasKind,
    raw: dict[str, Any],
) -> dict[str, Any]:
    """v0.11.4 migration helper: ensure actors / services canvases carry
    a project anchor node. Idempotent. Reads ProjectDoc.name for the
    label so the anchor is consistent with the Foundation copy.
    """
    nodes: list[dict[str, Any]] = list(raw.get("nodes") or [])
    if any((n.get("kind") == "project") for n in nodes):
        return raw
    try:
        proj = read_project(plot_root, project_id)
    except FileNotFoundError:
        return raw
    anchor = _seed_project_anchor(proj.name).model_dump(by_alias=True)
    raw = {**raw, "nodes": [anchor, *nodes]}
    # Persist so subsequent reads skip the backfill.
    _write_json(_canvas_file(plot_root, project_id, canvas_kind), raw)
    return raw


def write_canvas(plot_root: Path, project_id: str, canvas: CanvasDoc) -> None:
    _ensure_project(plot_root, project_id)
    service_id = canvas.service_ref if canvas.canvas_kind == "service_detail" else None
    path = _canvas_file(plot_root, project_id, canvas.canvas_kind, service_id)
    _write_json(path, canvas.model_dump(by_alias=True))
    try:
        meta = read_project(plot_root, project_id)
    except FileNotFoundError:
        return
    # Foundation canvas has the Project anchor whose label mirrors
    # ProjectDoc.name. Writes to the canvas are the authoritative source of
    # the rename — pull any drift back into the ProjectDoc so the sidebar /
    # MCP stay in sync.
    if canvas.canvas_kind == "foundation":
        project_node = next((n for n in canvas.nodes if n.kind == "project"), None)
        if project_node is not None:
            new_label = project_node.label.strip()
            if new_label and new_label != meta.name:
                meta = meta.model_copy(update={"name": new_label})
    # bump project.updated whenever a canvas changes
    write_project(plot_root, meta)


def rename_project(plot_root: Path, project_id: str, new_name: str) -> ProjectDoc:
    """Update ``ProjectDoc.name`` and sync the Foundation canvas Project
    anchor's label in one shot. Returns the refreshed ProjectDoc.

    Both sides stay in sync: the anchor label in
    ``foundation/canvas.json`` always equals ``project.json``'s ``name``.
    """
    proj = read_project(plot_root, project_id)
    renamed = proj.model_copy(update={"name": new_name})
    _write_json(_project_file(plot_root, project_id), renamed.model_dump())

    # Update the Project anchor label in the Foundation canvas (no-op if
    # the canvas hasn't been upgraded yet — the upgrade hook on
    # read_canvas heals it on the next open).
    try:
        foundation = read_canvas(plot_root, project_id, "foundation")
    except FileNotFoundError:
        write_project(plot_root, renamed)
        return read_project(plot_root, project_id)

    project_node = next((n for n in foundation.nodes if n.kind == "project"), None)
    if project_node is not None and project_node.label != new_name:
        updated_nodes = [
            n.model_copy(update={"label": new_name}) if n.id == project_node.id else n
            for n in foundation.nodes
        ]
        synced = foundation.model_copy(update={"nodes": updated_nodes})
        # Write directly without recursing through write_canvas (which
        # would read back our just-renamed ProjectDoc and no-op the
        # sync check).
        _write_json(
            _canvas_file(plot_root, project_id, "foundation"),
            synced.model_dump(by_alias=True),
        )

    # v0.11.4 — propagate the rename to the project anchors on the actors
    # and services canvases too. Each carries a copy of the project node;
    # all three copies' labels must match ProjectDoc.name.
    for canvas_kind in ("actors", "services"):
        try:
            other = read_canvas(plot_root, project_id, canvas_kind)
        except FileNotFoundError:
            continue
        anchor = next((n for n in other.nodes if n.kind == "project"), None)
        if anchor is not None and anchor.label != new_name:
            updated = [
                n.model_copy(update={"label": new_name}) if n.id == anchor.id else n
                for n in other.nodes
            ]
            _write_json(
                _canvas_file(plot_root, project_id, canvas_kind),
                other.model_copy(update={"nodes": updated}).model_dump(by_alias=True),
            )

    write_project(plot_root, renamed)
    return read_project(plot_root, project_id)


def list_service_details(plot_root: Path, project_id: str) -> list[str]:
    """Return the service ids for which a Detail canvas exists.
    v0.8 layout: each service lives at ``services/{sid}/`` and its detail
    canvas is the sibling ``detail.json`` alongside ``index.md``. Folders
    without a ``detail.json`` (e.g. a service connected to a folder but
    whose detail was archived) are skipped."""
    _ensure_project(plot_root, project_id)
    services_folder = _project_dir(plot_root, project_id) / "services"
    if not services_folder.is_dir():
        return []
    return sorted(
        sid.name
        for sid in services_folder.iterdir()
        if sid.is_dir() and (sid / "detail.json").is_file()
    )


# ---------------------------------------------------------------------------
# create / delete
# ---------------------------------------------------------------------------


def _seed_foundation_canvas(project_name: str) -> CanvasDoc:
    """Minimum valid Foundation canvas — central Project anchor (circle,
    auto-seeded, cannot be deleted) surrounded by Mission / Core Value /
    Identity pillars.

    The Project node's label mirrors ``ProjectDoc.name``; editing either
    side keeps both in sync via ``rename_project`` /
    ``sync_project_name_from_canvas``.
    """
    return CanvasDoc(
        canvas_id="foundation",
        canvas_kind="foundation",
        nodes=[
            SketchNode(
                id="project",
                kind="project",
                label=project_name,
                x=-75,
                y=-75,
                width=150,
                height=150,
                color="#fef3c7",
                shape="circle",
            ),
            SketchNode(
                id="mission",
                kind="mission",
                label="Mission",
                x=-360,
                y=-45,
                width=200,
                height=90,
                color="#fef3c7",
                shape="rounded",
            ),
            SketchNode(
                id="core-value-1",
                kind="core_value",
                label="Core value",
                x=-90,
                y=-260,
                width=180,
                height=80,
                color="#fde68a",
                shape="rounded",
            ),
            SketchNode(
                id="identity",
                kind="identity",
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


def _seed_project_anchor(project_name: str) -> SketchNode:
    """v0.11.4 — project anchor node, identical instance reused across
    every primary canvas (foundation / actors / services). Label mirrors
    ProjectDoc.name on every canvas; renames propagate through
    ``rename_project``.
    """
    return SketchNode(
        id="project",
        kind="project",
        label=project_name,
        x=-75,
        y=-75,
        width=150,
        height=150,
        color="#fef3c7",
        shape="circle",
    )


def _seed_actors_canvas(project_name: str) -> CanvasDoc:
    """v0.11 — actors canvas seeds with two placeholder classes ("Operator"
    and "User") to satisfy the IDENTITY.md "≥ 2 actor classes" minimum.

    v0.11.4 — also seeds a project anchor at the centre so the canvas
    reads as "actors spread out from the project."
    """
    return CanvasDoc(
        canvas_id="actors",
        canvas_kind="actors",
        nodes=[
            _seed_project_anchor(project_name),
            SketchNode(
                id="operator",
                kind="actor",
                label="Operator",
                side="operator",
                x=-260,
                y=-50,
                width=140,
                height=80,
                color="#bae6fd",
                shape="rounded",
            ),
            SketchNode(
                id="user",
                kind="actor",
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


def _seed_services_canvas(project_name: str) -> CanvasDoc:
    """v0.11.4 — services canvas seeds with the project anchor only.
    Top-level services + Foundation refs are added by the user as the
    architecture takes shape.
    """
    return CanvasDoc(
        canvas_id="services",
        canvas_kind="services",
        nodes=[_seed_project_anchor(project_name)],
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
    # Initialise the project's per-folder git repo now so that
    # ``tag_snapshot`` works later without any extra wiring. The repo
    # stays empty until the user plants a tag.
    ensure_repo(folder)

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
    """Ensure ``services/{sid}/detail.json`` exists for every service in the
    top-view ``services`` canvas.

    Services that disappear from the top view have their whole folder moved
    to ``services/_archive/{sid}/`` — a destructive delete would throw away
    user work (``index.md``, attachments) on a stray click. Called
    opportunistically after writes to the services canvas.

    Returns ``{"created": [...], "archived": [...]}`` for telemetry.
    """
    _ensure_project(plot_root, project_id)
    try:
        overview = read_canvas(plot_root, project_id, "services")
    except FileNotFoundError:
        return {"created": [], "archived": []}
    overview_service_ids = {n.id for n in overview.nodes if n.kind == "service"}
    services_folder = _project_dir(plot_root, project_id) / "services"
    services_folder.mkdir(exist_ok=True)
    # Existing service folders: every immediate subdir that isn't ``_archive``
    # and has its own ``detail.json``.
    existing_details: set[str] = set()
    if services_folder.is_dir():
        for child in services_folder.iterdir():
            if (
                child.is_dir()
                and child.name != "_archive"
                and (child / "detail.json").is_file()
            ):
                existing_details.add(child.name)

    created: list[str] = []
    for service_id in sorted(overview_service_ids - existing_details):
        src = next(n for n in overview.nodes if n.id == service_id)
        detail = CanvasDoc(
            canvas_id=service_id,
            canvas_kind="service_detail",
            service_ref=service_id,
            # v0.11 — every service_detail needs ≥ 2 actor_refs (operator +
            # user) per IDENTITY.md. Auto-seed two stub refs that point at
            # the project's seeded actors. Users can re-pick via the
            # picker, or add more refs as the design develops.
            nodes=[
                src.model_copy(update={"parent_id": None, "is_root": False}),
                SketchNode(
                    id=f"{service_id}-operator-ref",
                    kind="actor_ref",
                    label="→ Operator",
                    ref_actor_id="operator",
                    side="operator",
                    color="#bae6fd",
                    shape="ellipse",
                    width=140,
                    height=70,
                ),
                SketchNode(
                    id=f"{service_id}-user-ref",
                    kind="actor_ref",
                    label="→ User",
                    ref_actor_id="user",
                    side="user",
                    color="#fecaca",
                    shape="ellipse",
                    width=140,
                    height=70,
                ),
            ],
        )
        _write_json(
            _canvas_file(plot_root, project_id, "service_detail", service_id=service_id),
            detail.model_dump(by_alias=True),
        )
        created.append(service_id)

    archive_folder = services_folder / "_archive"
    archived: list[str] = []
    for service_id in sorted(existing_details - overview_service_ids):
        archive_folder.mkdir(exist_ok=True)
        src_path = services_folder / service_id
        dst_path = archive_folder / service_id
        # If the archive already has a folder with the same id (rare — same
        # service created, archived, and recreated), rename with a suffix.
        if dst_path.exists():
            n = 2
            while (archive_folder / f"{service_id}-{n}").exists():
                n += 1
            dst_path = archive_folder / f"{service_id}-{n}"
        src_path.replace(dst_path)
        archived.append(service_id)

    return {"created": created, "archived": archived}
