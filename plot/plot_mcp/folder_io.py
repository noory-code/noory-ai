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
    # v0.13 Phase 3+6 — for foundation, extract per-kind typed text out of
    # canvas.json into ``foundation/{kind}-{slug}.md`` heading-section
    # templates and (on read) merge them back into the in-memory node so
    # the rest of the pipeline still sees a populated CanvasDoc.
    if canvas_kind == "foundation":
        raw = _evict_typed_text_to_md(plot_root, project_id, raw)
        raw = _merge_md_typed_text_into_nodes(plot_root, project_id, raw)
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


def _evict_typed_text_to_md(
    plot_root: Path, project_id: str, raw: dict[str, Any]
) -> dict[str, Any]:
    """v0.13 Phase 3+6 migration helper: extract typed-text fields out of
    Foundation node entries in canvas.json into per-node MD templates.
    Idempotent — re-running with already-clean canvas.json + present MD
    files is a no-op.

    Strategy:
      For each node of kind in (mission/core_value/identity):
        1. Compute the MD file path (kind-slug.md under foundation/).
        2. If the canvas.json node still carries any typed-text values,
           render an MD template merging those into the file (preserving
           any existing free-prose body if the file already exists).
        3. Strip the typed-text fields from the canvas.json node.
        4. Set ``details_path`` to the new MD path so the viewer can
           link the two surfaces.
    """
    from plot_mcp.md_template import parse_md_template, render_md_template
    from plot_mcp.models import FOUNDATION_TYPED_TEXT_FIELDS

    nodes: list[dict[str, Any]] = list(raw.get("nodes") or [])
    changed = False
    new_nodes: list[dict[str, Any]] = []
    for n in nodes:
        kind = n.get("kind")
        if not isinstance(kind, str):
            new_nodes.append(n)
            continue
        typed_field_names = FOUNDATION_TYPED_TEXT_FIELDS.get(kind, [])
        if not typed_field_names:
            new_nodes.append(n)
            continue
        # Collect any non-empty typed text from canvas.json.
        existing_typed = {field: (n.get(field) or "") for field in typed_field_names}
        has_inline = any(v.strip() for v in existing_typed.values())
        # If there's no typed text inline AND no typed-text-keys at all,
        # the node is already cleaned. Don't touch details_path or MD.
        keys_present = any(field in n for field in typed_field_names)
        if not has_inline and not keys_present:
            new_nodes.append(n)
            continue
        md_path = _foundation_md_path(plot_root, project_id, kind, n["id"], n.get("label", ""))
        # Preserve existing free prose if the MD file already exists.
        existing_prose = ""
        existing_md_typed: dict[str, str] = {}
        if md_path.exists():
            parsed = parse_md_template(md_path.read_text(encoding="utf-8"), kind)
            existing_prose = parsed.free_prose
            existing_md_typed = parsed.typed_fields
        # Merge: canvas.json typed text wins on conflict (legacy data),
        # but we don't blow away non-empty MD content if the canvas value
        # is blank.
        merged = dict(existing_md_typed)
        for field, val in existing_typed.items():
            if val.strip() or field not in merged:
                merged[field] = val
        # Always strip the typed-text keys from the canvas.json node.
        cleaned = {k: v for k, v in n.items() if k not in typed_field_names}
        # Set details_path to the project-relative MD path only when not
        # already pointing at a real file (preserves user-set custom paths).
        rel_md = md_path.relative_to(_project_dir(plot_root, project_id))
        new_details = str(rel_md).replace("\\", "/")
        existing_details = cleaned.get("details_path")
        if not existing_details:
            cleaned["details_path"] = new_details
        if has_inline or not md_path.exists():
            md_path.parent.mkdir(parents=True, exist_ok=True)
            md_path.write_text(
                render_md_template(kind, n.get("label", ""), merged, existing_prose),
                encoding="utf-8",
            )
        # Compare each field individually to detect actual change.
        if cleaned != n:
            changed = True
        new_nodes.append(cleaned)
    if changed:
        raw = {**raw, "nodes": new_nodes}
        _write_json(_canvas_file(plot_root, project_id, "foundation"), raw)
    return raw


def _merge_md_typed_text_into_nodes(
    plot_root: Path, project_id: str, raw: dict[str, Any]
) -> dict[str, Any]:
    """v0.13 Phase 3+6: after eviction, re-attach typed-text fields to the
    in-memory nodes by reading the per-kind MD template at the canonical
    ``foundation/{kind}-{slug}.md`` path. Pure transform; no writes.

    ``details_path`` is intentionally NOT used here — it may still point
    at a legacy v0.7 ``{slug}/details.md`` (free-prose-only) location that
    has nothing to do with v0.13 typed-text storage. The canonical path
    derives from kind + label, matching what ``_evict_typed_text_to_md``
    writes.
    """
    from plot_mcp.md_template import parse_md_template
    from plot_mcp.models import FOUNDATION_TYPED_TEXT_FIELDS

    nodes: list[dict[str, Any]] = list(raw.get("nodes") or [])
    new_nodes: list[dict[str, Any]] = []
    for n in nodes:
        kind = n.get("kind")
        if not isinstance(kind, str):
            new_nodes.append(n)
            continue
        typed_field_names = FOUNDATION_TYPED_TEXT_FIELDS.get(kind, [])
        if not typed_field_names:
            new_nodes.append(n)
            continue
        md_path = _foundation_md_path(plot_root, project_id, kind, n["id"], n.get("label", ""))
        if not md_path.exists():
            new_nodes.append(n)
            continue
        parsed = parse_md_template(md_path.read_text(encoding="utf-8"), kind)
        merged = {**n}
        for field in typed_field_names:
            merged[field] = parsed.typed_fields.get(field, "")
        new_nodes.append(merged)
    return {**raw, "nodes": new_nodes}


def collect_foundation_md_warnings(
    plot_root: Path, project_id: str, canvas: CanvasDoc
) -> dict[str, list[str]]:
    """v0.13 Phase 7: scan each Foundation node's MD template and return
    ``{node_id: [warning_strings...]}`` for any node whose parser raised
    warnings. Empty mapping when everything is clean. Doesn't mutate the
    canvas. Called by ``canvas_get_endpoint`` to enrich the API response
    out-of-band so the model stays clean."""
    if canvas.canvas_kind != "foundation":
        return {}
    from plot_mcp.md_template import parse_md_template
    from plot_mcp.models import FOUNDATION_TYPED_TEXT_FIELDS

    out: dict[str, list[str]] = {}
    for n in canvas.nodes:
        kind = n.kind
        if not kind or not FOUNDATION_TYPED_TEXT_FIELDS.get(kind):
            continue
        md_path = _foundation_md_path(plot_root, project_id, kind, n.id, n.label)
        if not md_path.exists():
            continue
        parsed = parse_md_template(md_path.read_text(encoding="utf-8"), kind)
        if parsed.warnings:
            out[n.id] = parsed.warnings
    return out


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
        node_ids = {n.get("id") for n in nodes}
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
    # v0.13 Phase 3+6: split foundation typed text out of the JSON entry
    # into per-node MD templates. The JSON keeps only graph fields.
    if canvas.canvas_kind == "foundation":
        raw = _split_foundation_typed_text_to_md(plot_root, project_id, raw)
    _write_json(path, raw)
    try:
        meta = read_project(plot_root, project_id)
    except FileNotFoundError:
        return
    # v0.13 Phase 0: project label SSOT is ProjectDoc.name; no longer derived
    # from a per-canvas project node (the node is gone). Renames go through
    # ``rename_project`` directly. We just bump updated below.
    write_project(plot_root, meta)


def _split_foundation_typed_text_to_md(
    plot_root: Path, project_id: str, raw: dict[str, Any]
) -> dict[str, Any]:
    """v0.13 Phase 3+6: on foundation write, render any typed text on each
    kind node into the canonical ``foundation/{kind}-{slug}.md`` template
    (preserving any existing free prose) and strip the typed-text fields
    from the JSON entry."""
    from plot_mcp.md_template import parse_md_template, render_md_template
    from plot_mcp.models import FOUNDATION_TYPED_TEXT_FIELDS

    nodes: list[dict[str, Any]] = list(raw.get("nodes") or [])
    new_nodes: list[dict[str, Any]] = []
    for n in nodes:
        kind = n.get("kind")
        if not isinstance(kind, str):
            new_nodes.append(n)
            continue
        typed_field_names = FOUNDATION_TYPED_TEXT_FIELDS.get(kind, [])
        if not typed_field_names:
            new_nodes.append(n)
            continue
        # Pull current typed text out of the JSON entry; defaults to "".
        typed = {field: (n.get(field) or "") for field in typed_field_names}
        md_path = _foundation_md_path(plot_root, project_id, kind, n["id"], n.get("label", ""))
        # Preserve free prose if a prior MD file exists.
        existing_prose = ""
        if md_path.exists():
            existing_prose = parse_md_template(md_path.read_text(encoding="utf-8"), kind).free_prose
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(
            render_md_template(kind, n.get("label", ""), typed, existing_prose),
            encoding="utf-8",
        )
        # Strip typed-text fields from the JSON entry; ensure details_path.
        cleaned = {k: v for k, v in n.items() if k not in typed_field_names}
        if not cleaned.get("details_path"):
            rel_md = md_path.relative_to(_project_dir(plot_root, project_id))
            cleaned["details_path"] = str(rel_md).replace("\\", "/")
        new_nodes.append(cleaned)
    return {**raw, "nodes": new_nodes}


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
    from plot_mcp.schema_export import export_foundation_schemas

    export_foundation_schemas(plot_root, project_id)
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
