"""Folder-based project store for Plot — facade (D-2026-06-10-D).

The 1413-line god-module was split along its own section headers into
focused modules; this file re-exports every name (public AND the private
helpers that tests/endpoints import) so no import site changes:

    storage.py            — path layout + atomic JSON read/write
    canvas_migrations.py  — read-path healing (lazy migrations, MD absorb,
                            legacy anchor eviction)
    canvas_io.py          — read_canvas / write_canvas / list_feature_details
    project_io.py         — ProjectDoc read/write, seeds, create/rename/delete
    detail_sync.py        — feature ↔ services-overview sync
    node_publish.py       — per-node publish/unpublish (dirty detection,
                            version bumps, git snapshots)

Disk layout (unchanged)
-----------------------

    .plot/{project_id}/
        project.json                     — ProjectDoc
        foundation/canvas.json           — CanvasDoc (canvas_kind = "foundation")
        actors/canvas.json
        services/canvas.json             — top-view (canvas_kind = "services")
        services/{service_id}/detail.json— CanvasDoc (canvas_kind = "feature")

`tests/test_module_size.py` pins every module (and this facade) under the
monorepo 500-line rule so the god module cannot re-grow.
"""

from __future__ import annotations

from plot_mcp.canvas_io import (
    list_feature_details as list_feature_details,
)
from plot_mcp.canvas_io import (
    read_canvas as read_canvas,
)
from plot_mcp.canvas_io import (
    write_canvas as write_canvas,
)
from plot_mcp.canvas_migrations import (
    _LEGACY_PUBLISHED_FILENAME_RE as _LEGACY_PUBLISHED_FILENAME_RE,
)
from plot_mcp.canvas_migrations import (
    _absorb_md_typed_text_into_json as _absorb_md_typed_text_into_json,
)
from plot_mcp.canvas_migrations import (
    _drop_disallowed_services_kinds as _drop_disallowed_services_kinds,
)
from plot_mcp.canvas_migrations import (
    _evict_legacy_project_anchor as _evict_legacy_project_anchor,
)
from plot_mcp.canvas_migrations import (
    _foundation_md_path as _foundation_md_path,
)
from plot_mcp.canvas_migrations import (
    _legacy_md_dir as _legacy_md_dir,
)
from plot_mcp.canvas_migrations import (
    _migrate_actor_isroot_to_false as _migrate_actor_isroot_to_false,
)
from plot_mcp.canvas_migrations import (
    _migrate_assign_edge_relation as _migrate_assign_edge_relation,
)
from plot_mcp.canvas_migrations import (
    _migrate_parent_id_to_directed_edges as _migrate_parent_id_to_directed_edges,
)
from plot_mcp.canvas_migrations import (
    _migrate_published_flat_to_kind_slug as _migrate_published_flat_to_kind_slug,
)
from plot_mcp.canvas_migrations import (
    _migrate_published_slug_to_id as _migrate_published_slug_to_id,
)
from plot_mcp.canvas_migrations import (
    collect_foundation_md_warnings as collect_foundation_md_warnings,
)
from plot_mcp.detail_sync import (
    _detail_has_user_authored_content as _detail_has_user_authored_content,
)
from plot_mcp.detail_sync import (
    sync_details_with_overview as sync_details_with_overview,
)
from plot_mcp.node_publish import (
    _DIRTY_NON_CONTENT_FIELDS as _DIRTY_NON_CONTENT_FIELDS,
)
from plot_mcp.node_publish import (
    _DIRTY_VISUAL_FIELDS as _DIRTY_VISUAL_FIELDS,
)
from plot_mcp.node_publish import (
    PublishNotEligibleError as PublishNotEligibleError,
)
from plot_mcp.node_publish import (
    UnpublishNotEligibleError as UnpublishNotEligibleError,
)
from plot_mcp.node_publish import (
    _bump_node_version_in_canvas as _bump_node_version_in_canvas,
)
from plot_mcp.node_publish import (
    _dirty_snapshot as _dirty_snapshot,
)
from plot_mcp.node_publish import (
    _incident_edges as _incident_edges,
)
from plot_mcp.node_publish import (
    _load_all_canvases as _load_all_canvases,
)
from plot_mcp.node_publish import (
    _patch_node_in_canvas as _patch_node_in_canvas,
)
from plot_mcp.node_publish import (
    is_node_dirty as is_node_dirty,
)
from plot_mcp.node_publish import (
    publish_node as publish_node,
)
from plot_mcp.node_publish import (
    unpublish_node as unpublish_node,
)
from plot_mcp.project_io import (
    _seed_actors_canvas as _seed_actors_canvas,
)
from plot_mcp.project_io import (
    _seed_foundation_canvas as _seed_foundation_canvas,
)
from plot_mcp.project_io import (
    _seed_services_canvas as _seed_services_canvas,
)
from plot_mcp.project_io import (
    create_project as create_project,
)
from plot_mcp.project_io import (
    delete_project as delete_project,
)
from plot_mcp.project_io import (
    rename_project as rename_project,
)
from plot_mcp.storage import (
    _canvas_file as _canvas_file,
)
from plot_mcp.storage import (
    _ensure_project as _ensure_project,
)
from plot_mcp.storage import (
    _project_dir as _project_dir,
)
from plot_mcp.storage import (
    _project_file as _project_file,
)
from plot_mcp.storage import (
    _read_json as _read_json,
)
from plot_mcp.storage import (
    _write_json as _write_json,
)
from plot_mcp.storage import (
    read_project as read_project,
)
from plot_mcp.storage import (
    write_project as write_project,
)
