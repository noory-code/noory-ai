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
from plot_mcp.models import (
    ActorNode,
    ActorRefNode,
    CanvasDoc,
    CanvasKind,
    CategoryNode,
    CoreValueNode,
    IdentityNode,
    MissionNode,
    ProjectDoc,
)

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
    # v0.13 Phase 0 — project anchor moved to ``ProjectDoc.anchors``. If an
    # old canvas still carries a ``project`` kind node, evict it: copy its
    # position/visual to ProjectDoc.anchors[canvas] and remove from nodes.
    if canvas_kind in ("foundation", "actors", "services"):
        raw = _evict_legacy_project_anchor(plot_root, project_id, canvas_kind, raw)
    # v0.17 Phase 1 (D-2026-05-16-A) — JSON is the single SSOT for
    # Foundation typed-text fields. On first read of any pre-v0.17
    # project, absorb the typed H2 sections + post-``---`` body from
    # ``foundation/{kind}-{slug}.md`` into the JSON node, clear
    # ``details_path``, and quarantine the source MD file to
    # ``foundation/_legacy/``. Subsequent reads are no-ops (the
    # original path no longer exists).
    if canvas_kind == "foundation":
        raw = _absorb_md_typed_text_into_json(plot_root, project_id, raw)
    # v0.11.5 — services canvas no longer accepts Foundation refs (they
    # moved to service_detail). Drop any stale ones from older projects so
    # the canvas validates on open. Same idempotent pattern.
    if canvas_kind == "services":
        raw = _drop_disallowed_services_kinds(plot_root, project_id, raw)
        # v0.12 — wrap orphan top-level services in a default category so
        # the new "service must be nested in a category" validator passes.
        raw = _wrap_legacy_services_in_default_category(plot_root, project_id, raw)
    return CanvasDoc.model_validate(raw)


def _wrap_legacy_services_in_default_category(
    plot_root: Path,
    project_id: str,
    raw: dict[str, Any],
) -> dict[str, Any]:
    """v0.12 migration helper: any service nodes on the services canvas
    without a parent_id are legacy top-level services. Wrap them under a
    seeded default category so v0.12's "service must be nested" validator
    accepts them. Idempotent — only acts when orphan top-level services
    are detected.
    """
    nodes: list[dict[str, Any]] = list(raw.get("nodes") or [])
    orphans = [n for n in nodes if n.get("kind") == "service" and not n.get("parent_id")]
    if not orphans:
        return raw
    has_default = any(
        n.get("kind") == "category" and n.get("id") == "default-category" for n in nodes
    )
    rebuilt: list[dict[str, Any]] = []
    if not has_default:
        rebuilt.append(
            {
                **CategoryNode(
                    id="default-category",
                    label="Services",
                    theme="Migrated services",
                    x=-200,
                    y=-50,
                    width=200,
                    height=100,
                    color="#e2e8f0",
                    shape="rounded",
                ).model_dump(by_alias=True),
            }
        )
    for n in nodes:
        if n.get("kind") == "service" and not n.get("parent_id"):
            rebuilt.append({**n, "parent_id": "default-category"})
        else:
            rebuilt.append(n)
    raw = {**raw, "nodes": rebuilt}
    _write_json(_canvas_file(plot_root, project_id, "services"), raw)
    return raw


def _drop_disallowed_services_kinds(
    plot_root: Path,
    project_id: str,
    raw: dict[str, Any],
) -> dict[str, Any]:
    """v0.11.5 migration helper: silently drop ``mission_ref`` / ``value_ref``
    / ``identity_ref`` (and any other now-disallowed kinds) from the services
    top view. They live in ``service_detail`` from v0.11.5 onwards.
    Idempotent.

    v0.12 update: read the live ``_ALLOWED_KINDS_BY_CANVAS`` so future
    additions to the services-canvas allow-list don't trigger spurious
    drops here.
    """
    from plot_mcp.models import _ALLOWED_KINDS_BY_CANVAS

    nodes: list[dict[str, Any]] = list(raw.get("nodes") or [])
    allowed = _ALLOWED_KINDS_BY_CANVAS["services"]
    kept = [n for n in nodes if n.get("kind") in allowed or n.get("kind") is None]
    if len(kept) == len(nodes):
        return raw
    raw = {**raw, "nodes": kept}
    _write_json(_canvas_file(plot_root, project_id, "services"), raw)
    return raw


def _foundation_md_path(
    plot_root: Path, project_id: str, kind: str, node_id: str, label: str
) -> Path:
    """v0.13 Phase 3+6: per-node Markdown file path for a Foundation node.

    Layout: ``foundation/{kind}-{slugified-label}.md`` directly under the
    canvas folder (no per-node subfolder). The node's ``id`` is the
    stable identity; the slug derives from ``label`` and is regenerated
    on rename. We pin uniqueness by also embedding the kind so two
    differently-kinded nodes with the same label don't collide.
    """
    from plot_mcp.slug import slugify

    base_slug = slugify(label) if label.strip() else node_id
    return _project_dir(plot_root, project_id) / "foundation" / f"{kind}-{base_slug}.md"


def _legacy_md_dir(plot_root: Path, project_id: str) -> Path:
    return _project_dir(plot_root, project_id) / "foundation" / "_legacy"


def _absorb_md_typed_text_into_json(
    plot_root: Path, project_id: str, raw: dict[str, Any]
) -> dict[str, Any]:
    """v0.17 Phase 1 one-shot read-side migrator (D-2026-05-16-A).

    For each Foundation node of a typed-text kind (mission / core_value /
    identity), absorb the H2 typed sections + post-``---`` free prose
    from ``foundation/{kind}-{slug}.md`` into the JSON node (typed fields
    + new ``body`` field, all as MD-formatted strings), clear
    ``details_path`` to ``None``, and quarantine the source MD file to
    ``foundation/_legacy/{kind}-{slug}.md``.

    Conflict policy (4 scenarios):
      - JSON empty,   MD populated → MD wins; absorb.
      - JSON populated, MD missing → no-op for fields (JSON already SSoT).
      - Both populated              → JSON wins (latest); MD still quarantined.
      - Both empty                  → no-op.

    Idempotent: once the original MD path is gone, subsequent reads see
    no source file and skip. The ``_legacy/`` quarantine is never read.
    """
    from plot_mcp.md_template import parse_md_template
    from plot_mcp.models import FOUNDATION_MD_FIELDS, FOUNDATION_TYPED_TEXT_FIELDS

    nodes: list[dict[str, Any]] = list(raw.get("nodes") or [])
    changed = False
    new_nodes: list[dict[str, Any]] = []
    for n in nodes:
        kind = n.get("kind")
        if not isinstance(kind, str) or not FOUNDATION_MD_FIELDS.get(kind):
            new_nodes.append(n)
            continue
        md_path = _foundation_md_path(plot_root, project_id, kind, n["id"], n.get("label", ""))
        # No source MD → no field absorption + no quarantine move. But
        # Foundation typed-text kinds carry no ``details_path`` in v0.17+
        # (invariant per D-2026-05-16-A: JSON is SSOT for these kinds;
        # the viewer's MD-editor surface is gone). Clear unconditionally
        # if set; idempotent when already cleared.
        if not md_path.exists():
            if n.get("details_path") is not None:
                cleaned = {**n, "details_path": None}
                changed = True
                new_nodes.append(cleaned)
                continue
            new_nodes.append(n)
            continue
        parsed = parse_md_template(md_path.read_text(encoding="utf-8"), kind)
        merged = {**n}
        # Typed H2 fields: JSON value wins when present, else absorb MD.
        for field in FOUNDATION_TYPED_TEXT_FIELDS.get(kind, []):
            json_val = str(merged.get(field) or "")
            md_val = parsed.typed_fields.get(field, "")
            if not json_val.strip() and md_val.strip():
                merged[field] = md_val
        # body ← MD's post-``---`` free prose (same conflict policy).
        json_body = str(merged.get("body") or "")
        if not json_body.strip() and parsed.free_prose.strip():
            merged["body"] = parsed.free_prose
        # Foundation typed-text kinds carry no details_path in v0.17+.
        merged["details_path"] = None
        # Quarantine the source MD file. ``Path.rename`` is atomic within
        # the same filesystem; if the destination already exists (e.g.
        # duplicate slug across nodes), append the node-id short suffix
        # and try once more; if still colliding, leave the source in
        # place and continue (no data loss, just deferred cleanup).
        legacy_dir = _legacy_md_dir(plot_root, project_id)
        legacy_dir.mkdir(parents=True, exist_ok=True)
        dest = legacy_dir / md_path.name
        if dest.exists():
            short_id = str(n.get("id", ""))[:8] or "x"
            dest = legacy_dir / f"{md_path.stem}-{short_id}.md"
        if dest.exists():
            # Two collisions — give up moving (rare; leave on disk).
            new_nodes.append(merged)
            changed = True
            continue
        md_path.rename(dest)
        new_nodes.append(merged)
        changed = True
    if changed:
        raw = {**raw, "nodes": new_nodes}
        _write_json(_canvas_file(plot_root, project_id, "foundation"), raw)
    return raw


def collect_foundation_md_warnings(
    plot_root: Path, project_id: str, canvas: CanvasDoc
) -> dict[str, list[str]]:
    """v0.17 Phase 1 (D-2026-05-16-A): JSON is the sole SSOT for
    Foundation typed-text fields. The pre-v0.17 MD-template parser
    warnings are no longer surfaced because there are no MD files left
    at the canonical path after ``_absorb_md_typed_text_into_json``
    runs. Kept as a stable callable so the API response shape stays
    backward-compatible; Phase 6 will drop the call site entirely.
    """
    return {}


def _evict_legacy_project_anchor(
    plot_root: Path,
    project_id: str,
    canvas_kind: CanvasKind,
    raw: dict[str, Any],
) -> dict[str, Any]:
    """v0.13 Phase 0 migration helper: project anchor is now in
    ``ProjectDoc.anchors``. If an old canvas .json still carries a
    ``project`` kind node, copy its position/visual into ProjectDoc.anchors
    and remove the node. Idempotent — does nothing once cleaned up.
    """
    from plot_mcp.models import AnchorPlacement

    nodes: list[dict[str, Any]] = list(raw.get("nodes") or [])
    legacy_anchors = [n for n in nodes if n.get("kind") == "project"]
    if not legacy_anchors:
        # Defensive: an earlier eviction (without the edge cleanup that
        # landed in v0.13.0) may have left orphan edges referencing the
        # removed project node. Strip them now if any are still pointing
        # at a vanished id.
        #
        # v0.16.38 (D-2026-05-13-N) — the synthetic project anchor
        # ``PROJECT_ANCHOR_ID`` is a valid edge endpoint per
        # D-2026-05-04-B SPEC mandate even though it doesn't live in
        # ``nodes``. Whitelist it here so user-drawn anchor edges
        # aren't strip-and-rewritten on every read (which triggered
        # the watcher → broadcast → refetch loop reported by the
        # user on 2026-05-13 as *"새로고침을 하다보면 캔버스에 노드들이
        # 사라지는 이슈"*).
        from plot_mcp.models import PROJECT_ANCHOR_ID

        node_ids = {n.get("id") for n in nodes} | {PROJECT_ANCHOR_ID}
        edges: list[dict[str, Any]] = list(raw.get("edges") or [])
        kept_edges = [
            e for e in edges if e.get("source") in node_ids and e.get("target") in node_ids
        ]
        if len(kept_edges) != len(edges):
            raw = {**raw, "edges": kept_edges}
            _write_json(_canvas_file(plot_root, project_id, canvas_kind), raw)
        return raw
    try:
        proj = read_project(plot_root, project_id)
    except FileNotFoundError:
        # No project doc → can't migrate; just drop the node so the canvas
        # validates. Position is unrecoverable but defaults are sensible.
        kept = [n for n in nodes if n.get("kind") != "project"]
        raw = {**raw, "nodes": kept}
        _write_json(_canvas_file(plot_root, project_id, canvas_kind), raw)
        return raw
    legacy = legacy_anchors[0]
    anchor = AnchorPlacement(
        x=float(legacy.get("x", -75.0)),
        y=float(legacy.get("y", -75.0)),
        width=float(legacy.get("width", 150.0)),
        height=float(legacy.get("height", 150.0)),
        color=str(legacy.get("color", "#fef3c7")),
        shape=legacy.get("shape", "circle"),
    )
    new_anchors = {**proj.anchors, canvas_kind: anchor}
    proj = proj.model_copy(update={"anchors": new_anchors})
    write_project(plot_root, proj)
    evicted_ids = {n.get("id") for n in legacy_anchors}
    kept = [n for n in nodes if n.get("kind") != "project"]
    # v0.13 Phase 0: also drop any edges that referenced the evicted project
    # node — otherwise CanvasDoc validator fails with "edges reference
    # unknown nodes".
    all_edges: list[dict[str, Any]] = list(raw.get("edges") or [])
    kept_edges = [
        e
        for e in all_edges
        if e.get("source") not in evicted_ids and e.get("target") not in evicted_ids
    ]
    raw = {**raw, "nodes": kept, "edges": kept_edges}
    _write_json(_canvas_file(plot_root, project_id, canvas_kind), raw)
    return raw


def write_canvas(plot_root: Path, project_id: str, canvas: CanvasDoc) -> None:
    _ensure_project(plot_root, project_id)
    service_id = canvas.service_ref if canvas.canvas_kind == "service_detail" else None
    path = _canvas_file(plot_root, project_id, canvas.canvas_kind, service_id)
    raw = canvas.model_dump(by_alias=True)
    # v0.17 Phase 1 (D-2026-05-16-A) — JSON is the sole SSOT for
    # Foundation typed-text fields. The v0.13 ``_split_foundation_typed_
    # text_to_md`` write-side helper is gone; Pydantic now serialises
    # every field (typed + body) into the JSON output directly.
    _write_json(path, raw)
    try:
        meta = read_project(plot_root, project_id)
    except FileNotFoundError:
        return
    # v0.13 Phase 0: project label SSOT is ProjectDoc.name; no longer derived
    # from a per-canvas project node (the node is gone). Renames go through
    # ``rename_project`` directly. We just bump updated below.
    write_project(plot_root, meta)


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
            if child.is_dir() and child.name != "_archive" and (child / "detail.json").is_file():
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
                ActorRefNode(
                    id=f"{service_id}-operator-ref",
                    label="→ Operator",
                    ref_actor_id="operator",
                    side="operator",
                    color="#bae6fd",
                    shape="ellipse",
                    width=140,
                    height=70,
                ),
                ActorRefNode(
                    id=f"{service_id}-user-ref",
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
