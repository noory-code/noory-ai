"""Canvas read/write + service-detail listing.

Split out of the folder_io god-module (D-2026-06-10-D). folder_io.py re-exports
everything, so import sites and tests are unchanged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import ValidationError

from plot_mcp.canvas_migrations import (  # noqa: F401
    _LEGACY_PUBLISHED_FILENAME_RE,
    _absorb_md_typed_text_into_json,
    _drop_disallowed_services_kinds,
    _evict_legacy_project_anchor,
    _foundation_md_path,
    _legacy_md_dir,
    _migrate_actor_isroot_to_false,
    _migrate_assign_edge_relation,
    _migrate_parent_id_to_directed_edges,
    _migrate_published_flat_to_kind_slug,
    _migrate_published_slug_to_id,
    collect_foundation_md_warnings,
)
from plot_mcp.models import (
    CanvasDoc,
    CanvasKind,
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
    # v0.24.11 (D-2026-05-19-D) — actor.is_root semantic deprecated; reset
    # any pre-v0.24.11 ``is_root=true`` on actor nodes to False on first
    # read. Service.is_root is preserved (still meaningful as the
    # ServiceDetail anchor marker). See [[project_plot_symbol_concept]].
    if canvas_kind == "actors":
        raw = _migrate_actor_isroot_to_false(raw)
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
    # v0.26.0 (D-2026-05-25-A) — convert pre-v0.26 ``parent_id`` field
    # to a directed edge from parent → child. Idempotent. Persists
    # back to disk on first read so the file format settles into the
    # new model without needing a write-side trigger.
    raw = _migrate_parent_id_to_directed_edges(plot_root, project_id, canvas_kind, service_id, raw)
    # v0.30.0 (D-2026-05-31-C) — assign the stored ``relation`` semantic
    # to any pre-v0.30 edge that lacks it, via classify_edge(canvas,
    # source-node kind). Idempotent; persists on first read.
    raw = _migrate_assign_edge_relation(plot_root, project_id, canvas_kind, service_id, raw)
    # v0.23.0 (D-2026-05-17-I) — migrate legacy flat published MD layout
    # (<canvas>/published/<kind>-<slug>-v<X>.md) to the kind/slug/version.md
    # hierarchy. Idempotent.
    canvas_dir = _canvas_file(plot_root, project_id, canvas_kind, service_id).parent
    _migrate_published_flat_to_kind_slug(canvas_dir)
    # v0.24.3 (D-2026-05-18-A) — migrate slug-folder layout to id-folder.
    # Reads node id↔label from the raw canvas so we can compute the
    # old slug folder name and rename it to the node id.
    _migrate_published_slug_to_id(canvas_dir, raw)
    return CanvasDoc.model_validate(raw)


# v0.23.0 (D-2026-05-17-I) — published MD layout migration.
# Pre-v0.23.0 layout was flat: ``<canvas>/published/<kind>-<slug>-vN.M.md``.
# v0.23.0+ layout groups by kind + slug: ``<canvas>/published/<kind>/<slug>/vN.M.md``.
# Same data, better navigation: all versions of a logical document live in
# one folder, and that folder is grouped under its kind.
def write_canvas(plot_root: Path, project_id: str, canvas: CanvasDoc) -> None:
    _ensure_project(plot_root, project_id)
    service_id = canvas.service_ref if canvas.canvas_kind == "service_detail" else None
    path = _canvas_file(plot_root, project_id, canvas.canvas_kind, service_id)
    # v0.22.0 (D-2026-05-17-H) — preserve server-managed
    # ``_publish_baseline`` across PUTs. The client doesn't round-trip
    # this field (it's a server-managed dirty baseline), so a PUT from
    # the viewer would otherwise clobber it back to ``None`` and reset
    # every clean node to dirty. Read the existing on-disk canvas and
    # carry any non-None baseline forward for nodes whose incoming
    # baseline is ``None``.
    existing_baselines: dict[str, dict[str, Any]] = {}
    if path.is_file():
        try:
            existing_raw = _read_json(path)
            existing = CanvasDoc.model_validate(existing_raw)
            existing_baselines = {
                n.id: n.publish_baseline for n in existing.nodes if n.publish_baseline is not None
            }
        except (FileNotFoundError, ValueError, ValidationError):
            existing_baselines = {}
    if existing_baselines:
        preserved = [
            n.model_copy(update={"publish_baseline": existing_baselines[n.id]})
            if (n.publish_baseline is None and n.id in existing_baselines)
            else n
            for n in canvas.nodes
        ]
        canvas = canvas.model_copy(update={"nodes": preserved})
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


