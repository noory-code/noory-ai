# Changelog

All notable changes to Plot are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.3.0] — 2026-04-21

### Added
- **Folder-per-project storage** — `.plot/sketches/{id}/` with one JSON file per canvas (`core.json`, `actors.json`, `services-overview.json`, `services-detail/{service_id}.json`). Writing one canvas no longer touches any other. ([`plot_mcp/folder_io.py`](plot_mcp/folder_io.py))
- **v0.1 → v0.2 migration** — `plot_mcp.migrate.migrate_v01_to_v02` (also exposed as the `migrate_v01_sketches` MCP tool). Idempotent; promotes `mission` / `core_values` / `identity` text fields on the core-root into their own nodes; multi-line core-values split into one node per line. Originals rename to `{id}.json.v01.bak`.
- **Canvas-level MCP tools** — `list_projects`, `get_project`, `create_project_tool`, `delete_project_tool`, `rename_project`, `get_canvas`, `update_canvas`, `list_detail_canvases`, `migrate_v01_sketches`. The legacy sketch tools stay available during the transition.
- **Overview ↔ Detail auto-sync** — writing the `services_overview` via `update_canvas` auto-creates a Detail canvas for any new service and archives (does not delete) the Detail of a removed service.
- **Actor_ref picker UI** — dragging "Actor ref" onto the Services canvas opens a modal listing every actor from the Actor canvas; picking one creates a reference node with `ref_actor_id` and a "→ {label}" prefix.
- Inspector shows a read-only `References` pill for `actor_ref` nodes.

### Changed
- Inspector no longer renders `mission` / `core_values` / `identity` text fields on root nodes — those are first-class node kinds now.

### Notes
- The v0.1 viewer (single-file `SketchDoc` + tab-filter) still works. Switching the HTTP layer and viewer to the new canvas-level API is a follow-up; until then, the new tools and folder layout are opt-in via MCP.

## [0.2.0] — 2026-04-21

### Added
- Multi-canvas split — the sketch is now viewed through three tabs (**Core**, **Actors**, **Services**) so each cognitive layer has its own canvas. The underlying `SketchDoc` stays single-file for v0.2; separate canvas storage arrives in a later release.
- **Core canvas** — drops for Mission, Core Value, Identity, and Identity Facet promote what used to be Inspector text fields into structural child nodes of the Core octagon.
- **Services drill-down** — double-click any non-root service in the Overview to enter its Detail view; a breadcrumb at the top navigates back. `?canvas=services&detail=<id>` makes the view deep-linkable.
- **Canvas-aware stencil** — each tab surfaces only the presets it can accept, and `resolveDropTarget` knows the new core-child / identity-facet parenting rules.
- `CanvasDoc` + `CanvasKind` in `plot_mcp/models.py` with per-canvas-kind validators (core: 1 mission + 1 identity; actors: actor-only; services-overview: top-level only; service-detail: requires service_ref matching canvas_id).
- Expanded `NodeKind`: `mission`, `core_value`, `identity`, `identity_facet`, `actor_ref`. `SketchNode.ref_actor_id` carries the pointer for Actor→Service references.
- 26 new tests in `tests/test_canvas_doc.py`.

### Changed
- `?canvas=` URL param now carries the active tab; refreshing lands back on the same canvas.
- `SketchSidebar.stencilCanvas` prop switches the presets shown in the stencil.

### Notes
- Backward compatible: existing v0.1 `.plot/sketches/{id}.json` files keep loading; legacy untyped nodes default to the Services tab.
- `SketchDoc`'s old `mission` / `core_values` / `identity` text fields on root nodes remain for round-tripping until the v0.1→v0.2 migration script lands.

## [0.1.0] — 2026-04-20

### Added
- Initial release.
- Schema-free sketch store at `.plot/sketches/{id}.json`.
- Starlette HTTP server on port 5190 with 5 endpoints (list / get / create / put / delete) + WebSocket push.
- FastMCP tool surface: `list_sketches`, `get_sketch`, `create_sketch`, `update_sketch`, `delete_sketch`.
- React Flow 11 viewer with full editing: multi-select, copy/paste, undo/redo, auto-layout (dagre), context menu, MiniMap, Controls, resize, color picker, body markdown modal.
- Claude Code plugin manifest + initial skills (`plot-help`, `plot-new-sketch`, `plot-read-sketch`).
