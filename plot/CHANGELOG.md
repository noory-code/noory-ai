# Changelog

All notable changes to Plot are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.9.1] — 2026-04-28

### Removed
- **Typed fields on `SketchNode`** (`tagline`, `audience`, `method`, `goal`, `summary`, `criteria`). For most kinds the typed `summary` was just a worse copy of `label`. The viewer's `TypedFieldsForm` and the per-kind `TYPED_FIELDS` map go with them. Long-form structure (Tagline / Audience / Method / Goal sections) now lives wherever the user wants it inside `details.md`.
- **`details.md` legacy text bridge from v0.1 migration** — the old core-root `mission` / `identity` text used to land in `tagline` / `summary`. With those fields gone the text is dropped on migration. The structural mission / identity nodes still get created so the user can paste the text into the new node's `details.md` if they care. (Practically nobody ever ran v0.1 → v0.9 on real data.)
- **`leftover bodySections.ts` viewer file** — finally tracked the deletion that should have ridden along with v0.9.0.

### Notes
- Inspector layout per node is now: **Label** input + per-node **`details.md` editor** (or "Create details" button). That's it. No middle tier.
- On-canvas node preview is just the label — the body block is hidden when `data.body` is empty (which it always is now).
- `details.md` is still SSOT for prose; external editors (Obsidian, VS Code) can still edit it freely with watcher-driven sync.

## [0.9.0] — 2026-04-26

### Changed — **typed JSON fields + per-node `details.md`** (no more sync conflicts)
- **JSON and MD now hold different data.** Typed short fields live on the node in `canvas.json` and are written/read only by Plot; long prose lives in a per-node `details.md` and Plot reads/writes that file just like any other editor (Obsidian, VS Code) can. Same content is never duplicated, so the sync question that haunted v0.7 / v0.8 disappears entirely. ([`plot_mcp/models.py`](plot_mcp/models.py))
- **`SketchNode` typed fields**: `tagline`, `audience`, `method`, `goal`, `summary`, `criteria`. All optional; Inspector renders kind-specific subsets (Mission → Tagline/Audience/Method/Goal, CoreValue → Summary/Criteria, Identity / Project → Summary).
- **`SketchNode.body` is gone.** Its preview-cache role is moot (typed fields are direct), and its long-form-edit role moves to `details.md`. v0.1 migration drops legacy `mission` text into `tagline`, `identity` text into `summary`.
- **`SketchNode.folder_path` → `SketchNode.details_path`.** Same path-traversal validator, clearer name (it points at the node's `details.md`, not a generic folder).
- **Inspector**: dropped the H3-section `KindTemplate` and the `ConnectToFolderButton` flow. Replaced with `TypedFieldsForm` (binds directly to typed fields) + `DetailsSection` (opens `MDFileEditor` if `details_path` is set, otherwise shows "Create details"). ([`viewer/src/canvases/SketchInspector.tsx`](viewer/src/canvases/SketchInspector.tsx))
- **External MD editing is now safe.** The watcher tracks `details.md` files too — edits in Obsidian, VS Code, or any other editor raise a `project_changed` event and the open viewer reloads. There's nothing to drift because the JSON has no mirror of the MD content. ([`plot_mcp/watcher.py`](plot_mcp/watcher.py), [`plot_mcp/broadcast.py`](plot_mcp/broadcast.py))
- **On-canvas node preview** now picks from typed fields directly: Mission shows `tagline` (falling back to `summary`); everything else shows `summary`. No more H3 parsing on the client.

### Removed
- `plot_mcp/body_sections.py`, `viewer/src/lib/bodySections.ts`, `tests/test_body_sections_py.py` — no callers.
- `_sync_node_body_cache_on_md_write` and the `preview` field on `PUT /api/files` — typed fields are direct, no cache to sync.
- `ConnectToFolderButton`, `KindTemplate`, `REFERENCES_FIELD`, `TEMPLATES` (Inspector).
- `body` field on `SketchNode` (Python and TypeScript).
- Long-form textarea in `SketchBodyModal` (visual properties only now).

### Notes
- **No automatic migration from v0.8.** User confirmed no production data; v0.9 is a clean break.
- `details.md` is intentionally never parsed by Plot. Use whatever Markdown layout you like — `# Heading`, tables, Mermaid blocks, etc.

## [0.8.0] — 2026-04-23

### Changed — **breaking disk-layout refactor**
- **`.plot/` is wrapper-less and canvas-grouped.** Every project now owns a single folder under `.plot/` containing one subfolder per canvas kind; each canvas folder holds its structure (`canvas.json`) alongside its nodes' content folders. The former sibling `workspace/` tree is gone — long-form content lives inside the project's own folder.
  ```
  .plot/{project_id}/
    project.json
    core/
      canvas.json
      {slug}/index.md
    actors/
      canvas.json
      {slug}/index.md
    services/
      canvas.json                 ← top-view
      {service_id}/
        index.md
        detail.json               ← per-service drill-down
  ```
  - `.plot/sketches/` intermediate removed.
  - `core.json` / `actors.json` / `services-overview.json` → `{canvas}/canvas.json`.
  - `services-detail/{sid}.json` → `services/{sid}/detail.json` (co-located with the service's `index.md`).
- **`CanvasKind` literal `services_overview` → `services`.** Tab label is already "Services" — the canvas key now matches.
- **`/api/files`, `/api/folders` are project-scoped.** `project_id` is required; `path` is relative to `.plot/{project_id}/`. Client can no longer accidentally address another project's tree via `..`.
- **`folderSlug` drops the `workspace/` prefix.** Returns `{canvas}/{kind}-{label}` on both server (`plot_mcp/slug.py`) and client (`viewer/src/lib/slug.ts`).
- **`sync_details_with_overview`** archives a service's whole folder (including `index.md`) to `services/_archive/{sid}/` when it disappears from the top-view — the previous `.json`-only archive would have orphaned any long-form notes.

### Removed
- `workspace/` wrapper folder (everything moved inside `.plot/{project_id}/`).
- `services-detail/` dedicated folder.
- `.plot/sketches/` intermediate directory for new projects (legacy v0.1 migration still reads from it when it exists).

### Notes
- **No automatic migration from v0.7.** The user confirmed no production data — BANAS is a dev-only artifact. Opening an old v0.7 project in v0.8 will look empty; re-create or run a manual port.
- v0.1 → v0.4 auto-migration path still works and lands new projects in the v0.8 layout.

## [0.7.1] — 2026-04-23

### Added
- **Inspector width toggle** (`⇤` / `⇥`). Narrow stays at 320px; wide expands to `min(720px, 60vw)`. Choice persists in `localStorage` so the next node opens at the user's preferred size. ([`viewer/src/canvases/SketchInspector.tsx`](viewer/src/canvases/SketchInspector.tsx))
- **MDPreview component + Edit / Split / Preview tabs in the MD editor.** Rendered view is powered by `react-markdown` + `remark-gfm` (tables, task lists) plus a custom code renderer that pipes `` ```mermaid `` blocks through `mermaid.render`. Diagrams appear inline; parse errors fall back to the raw source instead of crashing the Inspector. Split mode pairs well with the wide Inspector for drafting diagrams next to the source. ([`viewer/src/edit/MDPreview.tsx`](viewer/src/edit/MDPreview.tsx), [`viewer/src/edit/MDFileEditor.tsx`](viewer/src/edit/MDFileEditor.tsx))

## [0.7.0] — 2026-04-23

### Added
- **Folder-backed node content — Inspector becomes an MD editor.** Click a node with a `folder_path`, the right panel turns into a full Markdown editor for that folder's `index.md`. Free-form text, structured ### H3 sections, wiki links — all round-trip to disk via a 600 ms debounced save. Mirrors the Claude-skill pattern the user asked for ("each node = folder, each folder has an `index.md`"). ([`viewer/src/edit/MDFileEditor.tsx`](viewer/src/edit/MDFileEditor.tsx))
- **`SketchNode.folder_path` field.** Optional relative path (under `project_path`) that binds a node to a folder on disk. When set, `body` holds only a short summary cache for the canvas preview; the long-form lives in the MD file. Validator rejects absolute paths, `..` segments, and blanks. ([`plot_mcp/models.py`](plot_mcp/models.py))
- **`/api/files` and `/api/folders` endpoints.** `GET /api/files`, `PUT /api/files`, `POST /api/folders`. Path-traversal, absolute paths, and symlink-escapes are all rejected; writes go through a tmp-rename so readers never see half a file. Folder POST uniquifies on collision (`-2`, `-3`, …). ([`plot_mcp/file_io.py`](plot_mcp/file_io.py), [`plot_mcp/api_endpoints.py`](plot_mcp/api_endpoints.py))
- **Server-side preview cache sync.** `PUT /api/files` with `project_id` + `node_id` query hints parses the saved `index.md`, picks the `### Tagline` (Mission) or `### Summary` (everything else), and mirrors it into the node's `body`. The on-canvas preview stays current without a separate fetch per node.
- **"Connect to folder" button in Inspector.** Legacy body-backed nodes (BANAS and everything shipped before 0.7) can opt into the folder model one click at a time: the button asks the server for a fresh folder based on `kind + label`, seeds `index.md` with whatever `body` already had, and attaches `folder_path`. No big-bang migration. ([`viewer/src/canvases/SketchInspector.tsx`](viewer/src/canvases/SketchInspector.tsx))
- **Shared slug convention.** `plot_mcp/slug.py` + `viewer/src/lib/slug.ts` compute the same default folder path — `workspace/{canvas}/{kind}-{label-slug}/` — so the client doesn't need a round-trip just to guess a name. Korean and CJK characters are preserved; server uniquifies on collision.

### Notes
- BANAS (and any pre-0.7 project) keeps working exactly as before until the user presses "Connect to folder" on a node. Migration is opt-in, not automatic.
- `index.md` is free-form. Use whatever headings you like — `### Tagline` and `### Summary` are the only ones the canvas preview reads.

## [0.6.0] — 2026-04-22

### Added
- **Markdown body rendering.** `SketchNode` now renders its body through `react-markdown`, so Inspector template fields (`### Tagline`, `### Summary`, …) appear as small uppercase section labels inside the node, and bold / italic / lists / links stay readable. Left-aligned body text reads naturally once multiple sections are stacked; the label keeps its centred treatment. ([`viewer/src/canvases/SketchNode.tsx`](viewer/src/canvases/SketchNode.tsx))
- **References field in Inspector templates.** Mission / Core Value / Identity / Project each pick up a `References` field for wiki-style links (e.g. `[[workspace/identity/mission.md]]`) pointing at long-form narrative docs. Plot stays the structural SSOT; MD files stay the narrative SSOT — no auto-sync. ([`viewer/src/canvases/SketchInspector.tsx`](viewer/src/canvases/SketchInspector.tsx))

## [0.5.1] — 2026-04-22

### Fixed
- **Legacy Core children no longer trap inside the Project anchor.** Pre-v0.5 projects (like BANAS) stored Mission / Identity nested under a `core`-kind octagon. The v0.5 upgrade now un-parents every node whose `parent_id` pointed at a legacy core anchor, so after opening the pillars land as peers around the small circular Project — not inside it. ([`plot_mcp/migrate.py`](plot_mcp/migrate.py))

### Changed
- **Top-left kind tag on Core nodes.** Mission / Core Value / Identity / Project nodes carry a small uppercase "MISSION" / "CORE VALUE" / … label in the top-left so the kind is legible at a glance, before opening the Inspector. ([`viewer/src/canvases/SketchNode.tsx`](viewer/src/canvases/SketchNode.tsx))
- **Star icon retired from Core kinds.** Mission / Core Value / Identity / Project no longer seed with a `star` icon (every Core kind had the same star, so it couldn't tell them apart). The new kind tag carries the identity signal. Legacy disk files carrying `icon: "star"` on Core kinds get cleaned up on the next open.
- **Fold button shifted to 24×24** (was 16×16) so it's no longer easy to miss. The Core canvas suppresses it entirely — Core is a peer layout, fold has no meaning there. Other canvases (actors / services) keep it.

## [0.5.0] — 2026-04-22

### Added
- **Project anchor on the Core canvas.** Every project now carries a central, circular **Project** node — auto-seeded on create / on the first open of a legacy project, protected from deletion (keyboard Delete, right-click Delete, Inspector Delete all refuse to touch it), and label-synced with `ProjectDoc.name` in both directions. Rename from the sidebar updates the node; editing the node label renames the project (the server reconciles on `PUT /canvases/core`). ([`plot_mcp/folder_io.py`](plot_mcp/folder_io.py), [`plot_mcp/migrate.py`](plot_mcp/migrate.py), [`viewer/src/canvases/SketchCanvas.tsx`](viewer/src/canvases/SketchCanvas.tsx))
- **Multi-Mission and multi-Identity on the Core canvas.** Mission is now 1..N (was exactly 1); Identity is now 1..N peers (was 1 + N Facet children). Each Identity node represents one aspect (Voice / Energy / Speech style / Visual tone / …) — drag the preset for every aspect you need. ([`plot_mcp/models.py`](plot_mcp/models.py))
- **Kind-aware Inspector templates.** Selecting a Mission / Core Value / Identity / Project node now surfaces the right fields instead of a bare Description textarea:
  - Mission → Tagline, Audience, Method, Goal, Story
  - Core Value → Summary, Decision criteria
  - Identity → Summary, Details
  - Project → Summary
  Fields persist as `### H3` Markdown sections inside `SketchNode.body` — no schema change, unknown sections and free-form notes round-trip untouched. ([`viewer/src/canvases/SketchInspector.tsx`](viewer/src/canvases/SketchInspector.tsx), [`viewer/src/lib/bodySections.ts`](viewer/src/lib/bodySections.ts))
- **Automatic v0.4 → v0.5 Core-canvas migration.** Opening a project with legacy `core`-kind octagons or `identity_facet` children heals itself lazily — the `read_canvas` path calls `upgrade_core_canvas_if_needed`, which rewrites kinds in-place and persists the result. No manual step. ([`plot_mcp/migrate.py`](plot_mcp/migrate.py))

### Changed
- **`NodeKind` shrinks.** Removed `core` (was the legacy octagon anchor) and `identity_facet` (absorbed into `identity`). Added `project`. Disk files carrying the retired kinds are rewritten on open.
- **`_core_canvas_rules`** relaxes Mission / Identity from "exactly 1" to "≥ 1" and adds "exactly 1 Project, top-level".
- **Stencil copy.** Mission / Core values / Identity sections now read "add as many as you need". Identity adds a hint listing example aspects. Identity Facet preset disappears.

### Fixed
- Right-click context menus no longer show their items with text pre-highlighted. The residual text selection the browser leaves behind on right-click is now suppressed with `select-none` + a `mousedown` preventDefault on the menu container. ([`viewer/src/canvases/SketchContextMenu.tsx`](viewer/src/canvases/SketchContextMenu.tsx))
- The Inspector no longer shows an empty "Select a node to see details" placeholder — it renders `null` when nothing is selected, reclaiming canvas width.

## [0.4.1] — 2026-04-21

### Added
- **Drop-overlap nudge.** Dragging a preset onto a spot already occupied by a sibling node no longer buries the new node behind the old one — the drop position slides diagonally by 32px until it finds a free slot (max 24 tries). Works for both top-level drops and container-nested drops. ([`viewer/src/canvases/SketchCanvas.tsx`](viewer/src/canvases/SketchCanvas.tsx))
- **Keyboard cheatsheet.** Press `?` anywhere to toggle a modal listing every shortcut; `Esc` or click-outside closes it. ([`viewer/src/App.tsx`](viewer/src/App.tsx))
- **Inspector delete button.** Every non-root, non-core node gets a `✕ delete` button in the Inspector header (with a confirmation prompt). The actor_ref orphan banner still has its own Delete button.
- **Inspector color swatch.** Small square next to the kind label shows the node's current fill colour at a glance.
- **Auto-layout now arranges Core / Actors / Detail canvases.** `autoLayout` treats `parent_id` relationships as implicit dagre edges, so the toolbar "Auto layout" button finally does something useful on canvases whose semantic links live in the hierarchy rather than in explicit edges. ([`viewer/src/flow/autoLayout.ts`](viewer/src/flow/autoLayout.ts))

### Fixed
- Tab-switch fit-view is now reliable: the canvas key includes the active canvas, so React Flow remounts and its `fitView` runs fresh on every tab change.

## [0.4.0] — 2026-04-21

### Added
- **Full viewer / HTTP cutover to the v0.2 folder layout.** New REST surface: `GET/POST /api/projects`, `GET/PATCH/DELETE /api/projects/{id}`, `GET/PUT /api/projects/{id}/canvases/{kind}[?service_id=]`. The viewer now loads one canvas at a time — no more in-memory tab-filtering. ([`plot_mcp/api_endpoints.py`](plot_mcp/api_endpoints.py), [`plot/viewer/src/api.ts`](viewer/src/api.ts))
- **Per-project git repo for session bookmarks.** Each project folder gets its own `.git/` at creation time, but editing never auto-commits. The user plants named tags at meaningful moments via the new **Mark session…** button or the `tag_project` MCP tool. `GET/POST /api/projects/{id}/tags` + `DELETE .../tags/{name}` expose the tag surface. ([`plot_mcp/git_store.py`](plot_mcp/git_store.py))
- **Project-level unified undo/redo.** New `useProjectHistory` hook holds one in-memory stack per loaded project with `{canvasKey, prev, next}` entries — `Ctrl+Z`/`Ctrl+Z+Shift`/`Ctrl+Y` rewinds any canvas's last edit and auto-switches tabs to where the change landed. 50-entry cap, cleared on project switch or external WebSocket write. ([`viewer/src/canvases/useProjectHistory.ts`](viewer/src/canvases/useProjectHistory.ts))
- WebSocket event shape: `sketch_changed` → **`project_changed`** with `{project_id, canvas_kind?, service_id?}` so the viewer only reloads the affected canvas.
- Sidebar has a **Session tags** collapsible panel listing the project's `git tag` entries with a hover × to delete (commit stays reachable via reflog).
- Silent v0.1 → v0.2 auto-migration on the first `GET /api/projects` call; banner toast reports what was migrated.
- New MCP tools: `tag_project`, `list_project_tags`, `delete_project_tag`. Canvas-level tools from v0.3 (`list_projects`, `get_project`, `get_canvas`, `update_canvas`, etc.) stay.

### Changed
- Sidebar "Sketches" → "Projects", "+ New sketch" → "+ New project". Summary's `node_count`/`edge_count` columns are dropped (canvases are loaded lazily now).
- `create_project` (Python + MCP) calls `git_store.ensure_repo` on the new folder.
- `plot_mcp/sketches.py` is now an internal module; only `migrate.py` imports it.

### Removed (breaking)
- `/api/sketches/*` REST endpoints — any external script that hit them needs to move to `/api/projects/*`.
- v0.1 MCP tool wrappers (`list_sketches_tool`, `get_sketch`, `create_sketch_tool`, `update_sketch`, `delete_sketch_tool`). Use the canvas-level equivalents.
- `useSketchHistory` viewer hook.

### Notes
- **Nested git repo.** `.plot/sketches/{id}/.git/` sits inside whatever project directory you're pointing Plot at. git naturally stops at inner `.git/` boundaries, so the parent repo sees `.plot/` as untracked. Recommended: add `.plot/` to your project's top-level `.gitignore`.
- Identity configured per-repo as `user.name=Plot`, `user.email=plot@noory-ai.local` so Plot commits don't inherit your global git identity.
- Undo/redo is in-memory only; tags are the durable history mechanism.

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
