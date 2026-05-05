# Changelog

All notable changes to Plot are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.13.2] — 2026-05-05

### Added — **Foundation SPEC + decision log**
- ``plot/docs/SPEC.md`` — first canonical behaviour spec (Foundation
  canvas only). Codifies anchor / edges / auto-layout / ⚠ badge /
  hover / Inspector / viewport behaviour with explicit user approval.
- ``plot/docs/DECISIONS.md`` — append-only UX / behaviour decision
  log. Today's seven decisions are logged with status (accepted /
  rejected / pending). Future UI changes must add an entry here
  before / alongside the code change.
- Reason: prior to this release, behavioural decisions lived only in
  code comments (not agreed) or in session memory (didn't survive).
  Cross-session work didn't accumulate. The two new files are the
  fix.

### Changed — **Foundation canvas: smaller, agreed-upon polish**
- **Anchor visually distinct from Service circles.** The project
  anchor now wears a slate-600 outline + offset + slate-300 inner
  ring so it reads as "this is the project itself, not a peer", even
  when it appears on Actors / Services where same-coloured Service
  circles also exist. (Decision D-2026-05-04-C.)
- **⚠ MD-warning badge contrast.** Was amber-100 fill on amber-100 /
  amber-50 cards — nearly invisible. Now white fill, amber-700
  glyph, amber-500 ring + shadow; legible on every Foundation card
  colour. (Decision D-2026-05-04-F.)
- **Quieter hover.** Connection handles stay hidden at rest; fade to
  opacity 0.55 while the cursor is on the node body; only become
  fully opaque + scaled on direct handle hover. The previous "all
  four handles pop the moment the cursor approaches" felt noisy.
  (Decision D-2026-05-04-E.)
- **Defensive viewport sizing.** Outermost shell uses ``h-screen
  min-h-screen``; ``html, body, #root`` add ``min-height: 100dvh``
  fallback. Belt-and-braces against cascading quirks so the canvas
  always reaches the bottom of the window. (Decision D-2026-05-04-G,
  approval pending user confirmation.)

### Removed — **Auto-layout button + auto-edges (rolled back same day)**
- **"Auto layout" button gone** from the canvas toolbar and the pane
  context menu. ``handleAutoLayout`` callback and ``autoLayout`` /
  ``radialLayout`` imports dropped from ``SketchCanvas``. Layout is
  fully manual — node positions encode user intent and shouldn't be
  silently rewritten. (Decision D-2026-05-04-D.)
- **Synthetic anchor → child auto-edges removed** before reaching a
  release. Briefly added during this session as dashed slate-400
  lines connecting the anchor to Mission / CoreValue / Identity, but
  the user rejected the approach: edges that the user can't edit or
  delete break the "every line on the canvas is mine to control"
  expectation. All edges on Foundation are user-drawn. (Decision
  D-2026-05-04-A.)
- **Anchor handle suppression rolled back.** Briefly hid the anchor's
  four React Flow handles on the assumption that "synthetic =
  read-only" (a stale code comment, not an agreed decision). Handles
  restored — the user may draw edges from / to the anchor like any
  other node. (Decision D-2026-05-04-B.)

## [0.13.1] — 2026-05-04

### Fixed — **Radial auto-layout under v0.13's derived project anchor**
- ``radialLayout`` was still looking for the project node inside
  ``doc.nodes`` (legacy v0.12 path). v0.13 moved the anchor out to
  ``ProjectDoc.anchors``; the lookup returned nothing on Foundation /
  Actors and silently fell back to dagre LR, collapsing the canvas
  into a horizontal row.
- New ``options.anchorOverride`` parameter; SketchCanvas passes the
  derived anchor in. Legacy in-doc.nodes lookup preserved as a
  fallback.

### Fixed — **Peer overlap on radial rings**
- The "minimum angular separation" between adjacent peers was a fixed
  15°. With node widths > 120 px on a 220 px ring, two peers could
  end up visibly overlapping. Now derives the gap from
  ``(maxNodeDim + 24px padding) / radius`` so it scales with actual
  footprint. Caps at π/2.
- If the spread chain wraps past 2π (user's nodes were so clustered
  that respecting angles couldn't yield separation), fall back to
  even distribution around the full circle.

## [0.13.0] — 2026-05-04

A foundational rework of how a project's data is laid out on disk —
**graph in JSON, typed content in Markdown, schema in its own folder**.
Foundation canvas is the v1 surface; Actors / Services / Service
Detail keep the v0.12 layout for now and join the new model in v0.14+.

### BREAKING — file layout

The first time Plot reads a v0.12 project, it migrates Foundation in
place:

  .plot/{project}/
    project.json                 ← + new ``anchors`` field
    schema/                      ← ✨ NEW (auto-generated, git-tracked)
      _meta.json                 schema_version=1, plot_version, kinds
      project.json               JSON Schema for project node entry
      mission.json               + core_value.json, identity.json
      mission.md.template        + core_value.md.template, identity.md.template
    foundation/
      canvas.json                ← graph only (no project node, no typed text)
      mission-mission.md         ← ✨ per-node typed text + free prose
      core_value-{slug}.md
      identity-voice.md
    actors/canvas.json           ← v0.12 layout, project node evicted
    services/                    ← v0.12 layout, project node evicted

### Phase 0 — Project SSOT
- New ``ProjectDoc.anchors: dict[CanvasKind, AnchorPlacement]``. Each
  AnchorPlacement carries x/y/w/h/color/shape for the project anchor
  on a given canvas. Default-seeded; old projects fall back cleanly.
- Per-canvas seeds (foundation/actors/services) no longer create a
  ``project`` kind node — the anchor is no longer canvas data.
- Eviction migrator on canvas read: legacy ``project`` node →
  ``ProjectDoc.anchors[canvas]`` + node removed + orphan edges stripped.
- Frontend: SketchCanvas injects a synthetic project anchor (id
  ``__project_anchor__``) derived from ProjectDoc.anchors. Drag /
  resize routes through a new ``PATCH /api/projects/{id}/anchors/{canvas}``;
  the canvas .json never carries a project node again.
- ``ProjectDoc.version`` bumped 2 → 3.

### Phase 1 — Pydantic discriminated union (Foundation)
- ``BaseNodeFields`` carries the 13 graph fields. Per-kind subclasses
  ``ProjectNode`` / ``MissionNode`` / ``CoreValueNode`` /
  ``IdentityNode`` declare a ``Literal`` discriminator on ``kind`` and
  their own typed-text fields. ``FoundationNode = Annotated[Union[...],
  Field(discriminator="kind")]``.
- The legacy god ``SketchNode`` stays in place — Foundation just gains
  type-safer per-kind constructors.

### Phase 2 — Schema auto-export
- New module ``schema_export.py``. ``create_project`` writes
  ``.plot/{project}/schema/`` with one JSON Schema per kind (graph
  fields only) plus per-kind MD templates. Idempotent.

### Phase 3 — Markdown template I/O
- New module ``md_template.py``. ``parse_md_template`` is **lenient**
  (missing sections → empty + warning, unknown headings preserved in
  warnings, case-insensitive headings, HTML comments stripped, free
  prose below the ``---`` rule preserved verbatim).
  ``render_md_template`` is **strict** (canonical section order per
  kind, free prose round-trips).
- 18 round-trip + lenient + strict tests.

### Phase 6 — Migration v0.12 → v0.13 (Foundation)
- ``_evict_typed_text_to_md`` runs on first foundation read: per-kind
  typed text in canvas.json → ``foundation/{kind}-{slug}.md`` template
  (preserving any existing free prose), then stripped from JSON.
- ``_merge_md_typed_text_into_nodes`` re-attaches typed text from the
  canonical MD path into the in-memory node so Inspector / API
  continue to see populated fields.
- ``_split_foundation_typed_text_to_md`` runs on every foundation
  write so Inspector edits land in MD, not back in canvas.json.

### Phase 4 — File watcher
- Watcher recognises ``foundation/*.md`` (any .md directly under
  ``foundation/``) as v0.13 per-node templates. External Obsidian /
  VS Code edits trigger ``project_changed`` with ``canvas_kind:
  "foundation"`` so any open viewer reloads.

### Phase 5 — TypeScript Foundation discriminated union
- ``BaseFoundationNode`` + ``MissionFoundationNode`` /
  ``CoreValueFoundationNode`` / ``IdentityFoundationNode`` /
  ``ProjectFoundationNode`` per-kind types.
  ``FoundationNode = ...`` discriminated on ``kind``. Ready for
  Foundation-aware code paths to narrow safely.

### Phase 7 — Resilience UX
- New helper ``collect_foundation_md_warnings`` runs alongside
  canvas read; ``canvas_get_endpoint`` injects per-node
  ``_md_warnings`` into the response without polluting the model.
- Frontend: ``SketchNode`` shows a yellow ⚠ badge when warnings
  present. Inspector displays the warning list with a hint pointing
  at the file the user should fix.

### Compatibility
- v0.12 projects auto-migrate on first read. Eviction is idempotent:
  re-running on v0.13 data is a no-op. The legacy v0.7
  ``{slug}/details.md`` per-node folders are left in place for
  backward compatibility but no longer used by Foundation reads;
  ``details_path`` may continue to point at them for the user's
  reference.
- 182 tests pass (164 prior + 18 new for md_template).

## [0.12.6] — 2026-05-03

Code-level audit cleared the v0.10/v0.11 residue still leaking into
the v0.12 Services surfaces.

### Changed — **`is_root` UI no longer applies to service**
- Inspector still surfaced a "Mark as Service Root" checkbox and a
  "Service Root" header for any parentless service. v0.12 made
  `service` a category leaf — there is no service-root concept any
  more. The toggle and the header branch now apply only to `actor`.
  The `is_root` field stays on the data model (still meaningful for
  actor); only the service UI path is removed.

### Changed — **Service Detail modal shows the parent category**
- The header used to read just "SERVICE DETAIL — Login". Inside the
  modal users had no way to see which category the service belonged
  to; drill context was lost. Header now reads
  "SERVICE DETAIL  {Category} › {Service}", with the category label
  derived from the service's `parent_id` lookup against the cached
  Services canvas.

### Added — **Soft warning on empty categories**
- A `category` with zero child services is structurally legal but
  semantically noise (categories exist to group services). Inspector
  now surfaces an amber hint inside `CategoryFields` when child
  count = 0, suggesting the user either drop a service in or delete
  the category. Not a hard validator — autosave-friendly.

### Changed — **Stale "sub-service" wording removed**
- Comments and JSDoc across `types.ts`, `SketchStencil.tsx`, and
  `SketchCanvas.tsx` still described the v0.10/v0.11 sub-service
  decomposition. Updated to v0.12 phrasing
  ("category → service leaf"; "service detail = modal").

### Changed — **Auto-layout button tooltip drops "(dagre LR)"**
- v0.12.4 made auto-layout dispatch by canvas (radial for
  Foundation/Actors, dagre for Services/Detail), so the literal
  "(dagre LR)" tooltip was a lie on half the canvases. Tooltip is
  now just "Auto layout".

## [0.12.5] — 2026-05-03

### Fixed — **Radial auto-layout preserves the user's angle**
- v0.12.4's radial placed peers around the project in `doc.nodes`
  declaration order (top → clockwise), so a node the user had
  dragged to the right could end up on the left after auto-layout.
  The placement felt arbitrary because it ignored where the user
  put things.
- New behaviour: each peer keeps its **current angle** from the
  project anchor; auto-layout only normalises distance (snap onto
  the same ring) and nudges any pair that would sit within 15° of
  each other so they don't visually overlap. If the user dragged
  Identity to the right, it stays on the right.

## [0.12.4] — 2026-05-03

Three corrections from continued usage.

### Changed — **Auto-layout dispatches by canvas shape**
- `dagre LR` lays a graph out as a left→right tree, which only fits
  the canvases that *are* trees (Services, Service Detail). On
  Foundation and Actors — both "project anchor at the centre, peers
  around it" — it collapsed everything into a single horizontal row
  and broke the radial mental model.
- New `radialLayout` keeps the `project` anchor where it sits and
  spreads the other connected nodes on a circle around it (top-down
  start, equal angular steps, ring sized to the largest peer node).
  `SketchCanvas.handleAutoLayout` dispatches by `canvas_kind` —
  Foundation / Actors radial; Services / Service Detail stay dagre.

### Changed — **Label alignment: category left, service centre**
- v0.12.2 left-aligned service titles to read them as "headers", but
  in v0.12 the actual *header* role belongs to `category` (the
  container). Service nodes are leaves and read better centred like
  every other kind. So the conditional flips: only `category` uses
  `justify-start`; everything else (including `service`) stays
  centred.

### Changed — **Collapse button: lose the circle, grow the arrow**
- The 32×32 white-circle-with-shadow control read as a UI chrome
  blob detached from the label. Replaced with a borderless inline
  arrow at `text-xl` (`▸` / `▾`) that hugs the label, hover
  darkens. Same hit area, much less visual noise.

## [0.12.3] — 2026-05-03

Docs only — sync `CONCEPTS.md` to v0.12 reality.

### Changed — **CONCEPTS.md**
- Canvas table: Services row now `project / category / service`;
  Service Detail row drops `service (sub via parent_id)` (sub-service
  was eliminated in v0.12) and is labelled "(modal, per-service)".
- `service` kind: the "Top-level service" / "Sub-service" sub-sections
  are merged into a single v0.12 service definition with one typed
  field block (`target_side`, `what`, `value_created`, `scope`,
  `trigger`, `how`, `outcome`, `do`, `dont`).
- Design principles: the validator floor for the Services canvas is
  rewritten — `service` must sit under a `category`, no nested
  categories. The v0.11.2 "≥ 1 Foundation anchor on the Services
  canvas" rule is removed (anchors now live inside the per-service
  modal, not on the top view).
- Stylistic phrasings updated from "Service Detail canvas" to
  "Service Detail modal" wherever the old surface was named.

## [0.12.2] — 2026-05-03

Visual polish on the v0.12 surfaces, driven by direct usage feedback.

### Changed — **Collapse button is a clear circle, not a tiny chevron**
- The fold/unfold control on container nodes (categories on the
  Services canvas, sub-actor parents on Actors) was a 24×24 square
  with no border that visually disappeared. Now 32×32, `rounded-full`,
  white background with a slate border and shadow. Same arrow glyph,
  much higher discoverability.

### Changed — **Service titles align left**
- Service node labels were centered like every other kind. With the
  v0.12 service-as-leaf model the label reads better as a header,
  so service nodes now `justify-start`. Other kinds still center.

### Fixed — **Service-detail modal hides the redundant root node**
- The modal's inner canvas seeded a copy of the service itself as a
  visible node, even though the modal header already names it
  ("SERVICE DETAIL — Login"). The modal now filters the root
  (matched by `doc.service_ref === node.id`) from both the nodes
  and edges memos, so refs and composition read against an empty
  background.

## [0.12.1] — 2026-05-03

Two decisive bugs from the v0.12.0 cleanup pass.

### Fixed — **Service double-click now opens the detail modal**
- The intended v0.12 gesture (double-click a service → modal overlay)
  silently failed: `SketchNode`'s inner `dblclick` handler called
  `e.stopPropagation()` and opened the generic Edit Node modal,
  shadowing React Flow's `onNodeDoubleClick → onNodeDrill`. The
  `ServiceDetailModal` was unreachable via the documented gesture.
- `SketchNodeData` now carries an optional `onDrill`. `SketchCanvas`
  wires it for kinds where drill is the intended dblclick gesture
  (services-canvas service → detail modal; service_detail actor_ref →
  jump to actor master). `SketchNode` prefers `onDrill` over
  `onOpenBody` when both could fire, so the Edit Node modal stops
  hijacking drill-eligible nodes.

### Changed — **Inspector says "Service", not "Sub-service"**
- v0.12 eliminated sub-service, but `SketchInspector.ServiceFields`
  still branched on `isTopLevel` and rendered "Sub-service" as the
  section header for any service with a `parent_id` (i.e. all
  services on the v0.12 services canvas, plus the service_detail
  root). Header is now always "Service".
- The dead "top-level vs sub" branch is gone: every service surfaces
  the same six typed fields (`what` / `value_created` / `scope` /
  `trigger` / `how` / `outcome`) plus Do/Don't, matching v0.12's
  "service is one kind" model.

## [0.12.0] — 2026-05-03

A larger refactor — the **Service vs Category split**. v0.10.3's
choice to keep top-level service and sub-service in a single `service`
kind never matched the user's mental model: top-level was always a
*grouping* (Admin / App / Backend), and the actual unit of value
production+exchange was the sub-service. v0.12 splits them.

### Added — **`category` kind**
- New top-level kind on the Services canvas. Categories are pure
  containers — they don't carry actor_refs, foundation refs, or any
  composition. Services nest inside them.
- One typed field: `theme` (one-line common thread).
- Stencil: a Category preset (top-level) and a Service preset that
  drops *inside* a category container.
- Validator: services on the Services canvas must have a category
  parent; categories must be top-level (no nested categories).

### Changed — **Service is now a leaf**
- The "service hierarchy depth = unlimited" rule from v0.10.3 is
  retired. A service has no sub-service. The Services canvas reads
  exactly two levels: `category → service`.
- All the previous sub-service typed fields (`value_created` /
  `trigger` / `how` / `outcome` / `do` / `dont`) and the v0.11.4
  `target_side` field stay on `service` exactly as before.

### Changed — **Service detail is now a modal overlay**
- Double-clicking a service no longer swaps the main canvas. The
  Services canvas stays mounted; the detail content opens in a
  modal overlay (Esc / backdrop click closes).
- The on-disk `service_detail/{id}/detail.json` file structure is
  unchanged. The change is purely UI — modal instead of canvas-swap.
- The drill-in breadcrumb is removed.

### Migration
- v0.1 → v0.2 split now seeds a single default `Category` ("Services",
  with `theme = "Migrated services"`) and parents the migrated
  top-level services under it.
- On read of the Services canvas, any orphan top-level services left
  by v0.11.x projects are silently re-parented under a seeded
  `default-category`. Idempotent.

### Notes
- 164 Python tests passing. Test fixtures updated to wrap services
  in a category. ruff / mypy / tsc all clean.
- `category` brings the kind count from 14 to 15.
- The "user can keep building deep service hierarchies" claim from
  v0.11.4 is rescinded for v0.12 — that's no longer the model. Depth
  in the picture maxes at category → service.

## [0.11.6] — 2026-05-03

Three small UX fixes from continued use.

### Removed — **Toolbar Download / Upload / save-state indicator**
- Save is automatic and silent already; the persistent indicator was
  noise. Errors still surface via the App-level error toast.
- `SketchToolbar` now only carries Undo / Redo / Auto layout.
- `SketchCanvasProps` no longer takes `saveState` / `onDownload` /
  `onUpload`; App.tsx drops `handleDownload` / `handleUpload`. JSON
  import/export, if it ever returns, will be a dedicated flow.

### Changed — **Top-level service default size shrinks**
- Was 300×200, now 180×100. Users still resize after drop; the
  smaller default keeps the Services canvas tidy when many top-level
  services are added (the previous size felt overscale next to the
  project anchor).

### Notes
- This release is viewer-only. Python schema unchanged.
- Pairs naturally with the user's flow after v0.11.5: drop a top-
  level service, drill in, and use the per-master stencil for refs.

## [0.11.5] — 2026-05-03

Two paired user-experience changes triggered by hands-on use.

### Changed — **Services top view only carries Project + Services**
- `_ALLOWED_KINDS_BY_CANVAS["services"]` is now `{"service", "project"}`
  (was `{"service", "project"} | _FOUNDATION_REFS`).
- All Foundation references (`mission_ref` / `value_ref` /
  `identity_ref`), participant references (`actor_ref`), and
  composition kinds (`metric` / `step`) are **service-detail-only**
  from now on. Sub-service decomposition already lives there, so the
  whole "rich detail" lives in one place.
- The v0.11.2 anchor hard validator on the Services canvas is dropped
  along with this change. Alignment ownership now lives inside each
  Service-Detail canvas.
- Migrator: read of an older Services canvas silently drops any
  Foundation ref nodes (idempotent) so existing projects open clean.

### Changed — **Stencil generates one draggable per master**
- The Service-Detail stencil no longer shows a generic "Mission ref"
  preset. Instead it renders **one draggable per master**, labelled
  with that master's real label and tinted with its colour. Ten
  missions on the Foundation canvas → ten mission entries on the
  Service-Detail stencil. Same for `value_ref`, `identity_ref`, and
  `actor_ref`.
- Drops are now **direct**: the preset already carries the target
  master id, so the picker no longer opens for the create flow. The
  picker is reserved for the Inspector's rewire button on orphans.
- `StencilCanvas` type gains a `service_detail` value; `App.tsx`
  passes `"service_detail"` whenever the user is drilled into a
  service detail (was always `"services"` before).

### Notes
- 162 Python tests passing. Existing fixtures padded to match the
  new allowed-kinds set.
- The Inspector's existing actor_ref / foundation_ref orphan UX
  (Re-pick / Delete) still works — the rewire flow keeps the picker.
- "Product as a kind" remains rejected from the v0.11.4 discussion.

## [0.11.4] — 2026-05-03

First user-experience-driven patch on the v0.11 model. Two paired
changes triggered by hands-on use:

- "Where's the project? Each canvas feels like it floats on its own."
  → Project anchor visible on every primary canvas.
- "Operator-facing services and user-facing services need to read
  differently at a glance."
  → New `target_side` typed field on `service`, mirror of `actor.side`.

### Added — **Project anchor on Actors / Services canvases**
- `_ALLOWED_KINDS_BY_CANVAS` admits `project` on Actors and Services
  in addition to Foundation.
- New `_seed_project_anchor()` factory; `_seed_actors_canvas()` and
  the new `_seed_services_canvas()` both seed it at the centre.
- `rename_project()` now propagates the rename to Actors / Services
  copies in addition to Foundation. All three labels stay in sync.
- `read_canvas` quietly backfills the anchor for projects created
  before v0.11.4 (idempotent).

### Added — **`service.target_side` typed field**
- `SketchNode.target_side: Literal["operator", "user", "both"] | None
  = None`. Mirror of `actor.side`.
- Inspector ServiceFields gains a Target side selector
  (운영자측 / 사용자측 / 둘 다 / 미지정).
- Canvas tints the service body by `target_side`:
  - `operator` → blue (`#dbeafe`)
  - `user` → red (`#fee2e2`)
  - `both` → violet (`#ede9fe`)
- No new kind. The two-axis classification (actor side ↔ service
  target_side) keeps the model's mental shape consistent.

### Notes
- Tests: 162 passing. Two existing fixtures updated for the new
  Actors / Services seeds.
- "Product" is intentionally **not** a new kind — operator-facing
  services and user-facing services are distinct service instances
  with different `target_side`, not a separate kind. This decision
  was confirmed during the discussion (see plan file).
- Users can keep building deep service hierarchies (sub-sub-service
  is fine — depth stays unlimited).

## [0.11.3] — 2026-04-30

Closes the v0.11 release line. Phase D (Mode 2 time-axis layer
compatibility) was verified without code changes — every Phase A/B/C
decision extends non-destructively when the time-axis kinds (Task,
schedule, etc.) are eventually added. The infrastructure layer joins
Mode 2 as already documented in IDENTITY.md.

### Changed — `docs/ROADMAP.md`
- Reorganised to cover both v0.10 and v0.11 release lines with a
  per-phase ship table for v0.11.

### Notes — what's next
- v0.11 model is now intentionally stable. The next round is
  **user-experience polish** — known follow-ups (e.g. node click
  going to label-edit instead of opening the Inspector) and anything
  surfaced by hands-on use of the new actor/service model.
- Mode 2 (time-axis task layer) waits until that polish round
  generates concrete requirements.
- No code or schema changes in this release.

## [0.11.2] — 2026-04-30

Phase C of v0.11. Two long-standing soft rules graduate to hard
validators, and `actor_ref` joins the typed-field family with a
per-actor-per-service value-flow pair.

### Added — **`actor_ref` typed fields (Phase C3)**
- `SketchNode.gives: str = ""` — what this actor gives to the service.
- `SketchNode.receives: str = ""` — what this actor receives back.
- Inspector renders an "Value flow" form on `actor_ref` selection
  with the two fields side by side. Both optional.
- Rationale: PHILOSOPHY.md P6 ("arrows carry action + value") in its
  weakened form. The flow lives on the ref node rather than on an
  explicit edge, so the value economy is captured per-pair without
  forcing the user to draw and label dozens of arrows.
- `service.value_created` (aggregate) and `actor_ref.gives` /
  `receives` (per-pair) are deliberately orthogonal.

### Changed — **Top-level service Foundation anchor is now a hard
validator (Phase C2)**
- A `services` canvas containing at least one top-level service must
  also contain at least one Foundation reference (`mission_ref` /
  `value_ref` / `identity_ref`). An empty services canvas is fine.
- The same rule was already in IDENTITY.md and CONCEPTS.md as docs;
  this release wires it into Pydantic.
- Mapping is **canvas-level, not per-service**: the visual layout
  (which anchor sits next to which service) carries the 1:1 nuance.
  This keeps the model schema free of new fields and matches the
  existing `mission_ref` placement pattern from v0.10.2.
- Migrator: legacy v0.1 sketches whose split overview canvas had no
  anchor get a single `mission_ref → "mission"` seeded automatically
  so the canvas validates after open. Idempotent.

### Notes
- Tests: 162 passing. New test `test_overview_services_without_anchor_rejected`
  asserts the new floor; existing fixtures padded with anchors.
- Phase D (time-axis compatibility + v0.11 vs v0.12+ scoping) remains
  the last v0.11 step.

## [0.11.1] — 2026-04-30

Phase B of v0.11. The `actor_ref` orphan UX (re-pick, delete) now
extends to all four ref kinds, and ref labels stay in sync with their
masters automatically.

### Added — **Foundation ref orphan UX**
- `mission_ref` / `value_ref` / `identity_ref` Inspector blocks now
  show a **Re-pick…** + **Delete** button pair when the master is
  missing from the Foundation canvas. Mirrors the existing
  `actor_ref` orphan UI.
- `FoundationRefPicker` already supported a `rewire` mode (since
  v0.10.2); this release wires it through `SketchCanvas` so the
  Inspector's Re-pick button opens the picker and the user-selected
  master replaces the orphan's `ref_*_id`.

### Added — **Ref label auto-sync**
- The displayed label for any ref kind (`actor_ref`, `mission_ref`,
  `value_ref`, `identity_ref`) is now **derived from the master at
  render time** — `→ {master.label}`. The stored label remains as a
  fallback for the orphan case (master missing).
- This means: rename the master `Mission` to `우리의 사명`, and every
  `mission_ref` on every canvas updates instantly with no propagation
  step. No more stale denormalised labels.

### Notes
- Implementation: the label transform happens in `SketchCanvas`'s
  React Flow node mapping (`useMemo`), via lookups against the
  `availableActors` / `availableMissions` / `availableValues` /
  `availableIdentities` props the App already passes through. No
  backend / migration change needed.
- Phase C (Service field polish) and Phase D (time-axis
  compatibility) remain.

## [0.11.0] — 2026-04-28

The Actor model promised by v0.10.6 / v0.10.7 lands as code. Phase A
of the v0.11 redefinition (A1–A5) is fully implemented; B/C/D follow
in later releases.

### Added — **Actor typed fields**
- `SketchNode.motivation: str = ""` — why this actor participates.
- `SketchNode.pain: str = ""` — frictions / frustrations they face.
- `SketchNode.side: Literal["operator", "user"] | None = None` —
  flat category; partitions actors by which side of the value
  exchange they occupy. Set on every actor; mirrored onto every
  `actor_ref` so service-detail canvases can validate operator/user
  mixes without cross-canvas lookups.
- Inspector renders an `Actor` form (Side selector + Motivation +
  Pain textareas) when `kind === "actor"`.

### Changed — **Hard validators**
- `actors` canvas now requires **≥ 2 actor classes**.
  IDENTITY.md baseline: a project without two sides can't host value
  exchange. New projects seed two placeholders (Operator + User) so
  this floor is satisfied out of the box.
- `service_detail` canvas now requires **≥ 2 `actor_ref` nodes**.
  Auto-creation paths (`sync_details_with_overview`, the v0.10
  migrator) seed two stub refs (operator + user) for every new or
  migrated detail canvas.

### Added — **Project + migration seeding**
- `_seed_actors_canvas()` (folder_io.py) seeds two actor classes
  ("Operator" + "User", with `side` set) on project creation.
- Migration path (`_backfill_actor_sides` + `_ensure_minimum_actors`
  + `_detail_actor_ref_seeds`) heals legacy v0.10.x projects on open:
  defaults missing `side` to `"user"`, pads under-populated actors
  canvases, and seeds operator/user actor_refs for any service_detail
  that doesn't already have them. Idempotent.

### Changed — **`docs/CONCEPTS.md` actor section**
- Adds the "two orthogonal mechanisms" subsection (`side` flat
  category + `parent_id` is-a tree) — the central insight from Phase
  A3 of the discussion.
- Documents the v0.11 typed fields (`motivation`, `pain`) and notes
  the deliberate exclusion of Do/Don't and permissions from the
  actor.

### Notes
- Phase A discussion log lives at
  `~/.claude/plans/ancient-pondering-petal.md`.
- Phase B (actor_ref Symbol justification + orphan UX), Phase C
  (Service field polish), and Phase D (time-axis compatibility) are
  the remaining v0.11.x work.
- This release re-asserts every IDENTITY.md floor as Pydantic
  validation, not just doc text. Existing projects migrate cleanly;
  no data loss is expected.

## [0.10.7] — 2026-04-28

Docs-only patch capturing the load-bearing Actor / Service decisions
made in v0.11 Phase A1 + A2 planning. The code changes (validators,
seed actors) ship later as v0.11.0; this release is the philosophy
front-load so the docs are accurate before any model moves.

### Added — `IDENTITY.md` "Actor & Service — the Core Philosophy" section
- **Actor definition**: a *class of people* who participate in the
  project's value economy. Class, not individual; people only — APIs,
  systems, bots, and infrastructure are out of scope until Mode 2.
- **Service definition**: a *playground* where stakeholders **produce
  and exchange** value (the dual phrasing is deliberate — services
  produce new value through actor participation, not just route
  pre-existing value).
- **Service minimum baseline**: every service must include **≥ 2**
  participating `actor_ref` nodes — non-negotiable.
- **Operator-explicit rule**: the operator/developer must always be
  one of those `actor_ref`s. The reasoning is moderation: services
  are playgrounds, freedom needs alignment-keepers, and *which*
  operator owns alignment for *which* service must be visible —
  exactly Plot's stated purpose.
- A "Why these are philosophy, not just rules" subsection explains
  that loosening any of these floors changes the product, not just
  the schema.

### Changed — `CONCEPTS.md`
- `actor` kind: redefined as "a class of people," with the people-only
  scope and the project-level `≥ 2` floor stated. Previous "person /
  system / organisation" wording retired.
- `service` kind: re-introduced with the playground metaphor,
  "produce + exchange" phrasing, and a new explicit subsection
  documenting the service minimum baseline (≥ 2 actor_refs, explicit
  operator).
- "Design principles" #2 ("templates rich, requirements minimal") now
  enumerates the current set of hard floors and cross-references
  IDENTITY.md.

### Notes
- This is **not** a behaviour change. The validators and the seed
  actors (User / Operator placeholders) land in v0.11.0 once the rest
  of Phase A — A3 (sub-actor semantics), A4 (typed fields), A5
  (naming) — and Phase B / C / D are decided. Doing docs first means
  the model changes can be evaluated against a stable spec.
- Plan-file framework with the running discussion log lives at
  `~/.claude/plans/ancient-pondering-petal.md`.

## [0.10.6] — 2026-04-28

Docs-only patch ahead of v0.11. Captures Plot's product identity in
permanent storage so future sessions (human or AI) can ground their
decisions in what Plot actually is — and is not.

### Added — **`docs/IDENTITY.md`**
- New canonical document stating what Plot is (a strategic operations
  design + alignment tool) and what it is not (a simple mindmap or
  brainstorming tool).
- The four use purposes: concrete service planning, direction alignment,
  position in the big picture, relationship visualisation.
- The two modes — today's picture mode and the future time-axis task
  mode — and the implication that v0.11+ models must survive the
  transition.
- Korean original quote from the user (2026-04-28) preserved so the
  source intent is auditable.

### Changed — `docs/CONCEPTS.md`
- Header now points to `IDENTITY.md` first. CONCEPTS remains the
  technical reference (kinds, canvases, fields); IDENTITY is the
  "why and for whom" check applied before any new concept lands.

### Notes
- This release contains no code changes. It exists to fix a gap caught
  during v0.11 planning: the user-stated identity from 2026-04-28 was
  living only in the in-progress plan file, which is volatile across
  sessions.

## [0.10.5] — 2026-04-28

Step 6 of the v0.10 kind-redefinition program — and the **final** step.
The two pre-existing composition kinds (`rule`, `content`) gain typed
fields so the Inspector can drive them as deterministically as the
kinds added earlier in v0.10.

### Added — **`rule` typed fields**
- `SketchNode.policy: str = ""` — the rule statement.
- `SketchNode.enforcement: str = ""` — how it's enforced.
- `SketchNode.actor_permissions: dict[str, str] = {}` — actor-id →
  permission-string map. Free-form value; suggested vocabulary is
  C/R/U/D shorthand (`"RUD"`, `"CRUD"`, etc.).

### Added — **`content` typed fields**
- `SketchNode.format: str = ""` — artifact shape (JSON, MD, image, …).
- `SketchNode.producer_actor_id: str | None = None` — actor master id
  that creates the content.
- `SketchNode.consumer_actor_id: str | None = None` — actor master id
  that consumes it.

### Added — **Expandable Inspector rows**
- The `CompositionList` rows for Rules and Contents are now expandable
  via a chevron toggle. Collapsed: just the label input. Expanded:
  the kind-specific typed form.
- Rule form includes a **permission editor**: a dropdown of actor
  masters not yet assigned + a per-row permission text input + a
  remove button.
- Content form includes producer/consumer **actor pickers** populated
  from the same `availableActors` list the Inspector already uses.

### Notes
- `actor_permissions` is keyed by actor master id (matching the
  `actor_ref` semantic from Step 3); the editor surfaces the actor's
  label for readability.
- The permission string is intentionally free-form for v0.10. A future
  release may switch to a richer schema (e.g. `{create, read, update,
  delete}` booleans) once the convention settles.
- This release closes out the v0.10 kind-redefinition program: every
  kind now has a clear semantic purpose, typed fields where the
  domain has separable facets, and Inspector rendering. The next
  release line can focus on edge utilisation or the time-axis layer.

## [0.10.4] — 2026-04-28

Step 5 of the v0.10 kind-redefinition program. Two new composition
kinds for the Service-Detail canvas — explicit success indicators
(metrics) and ordered procedural flow (steps).

### Added — **`metric` kind**
- New node kind admitted only on the **service_detail** canvas, with
  the same parent-must-be-a-service rule that already governs
  `rule` / `content`.
- Typed fields:
  - `target: str = ""` — goal value or threshold (e.g. `>99%`).
  - `measurement: str = ""` — how the metric is measured.
- Stencil entry on the Services-tab stencil under "Composition"
  (drop on a Service container).

### Added — **`step` kind**
- New node kind admitted only on the **service_detail** canvas, same
  parent constraint as the other composition kinds.
- Typed fields:
  - `order: int | None = None` — ordinal position in the sequence;
    `None` leaves the step unordered (e.g. parallel branches).
  - `outcome: str = ""` — observable end state. Shared with `service`
    (declared once on the model in v0.10 Step 4).
- Stencil entry on the Services-tab stencil under "Composition".

### Changed — **`_COMPOSITION_KINDS`**
- Now `{rule, content, metric, step}`. Inside a `service_detail`
  canvas all four kinds must have a service parent.

### Notes
- `metric` and `step` are canvas-first composition (visible on the
  Service-Detail canvas), unlike `rule` / `content` which remain
  Inspector-only `+ Add` items. The model accepts both kinds in either
  position; the editorial choice is a UI policy.
- Inspector forms render the typed fields per-kind. Drop validator
  rejects metric/step placed at top level with the standard
  "Drop inside a Service container" message.

## [0.10.3] — 2026-04-28

Step 4 of the v0.10 kind-redefinition program. Service nodes gain typed
fields differentiated by canvas — top-level services (the strategic
view) and sub-services (the operational view) get different forms while
sharing one model.

### Added — **Service typed fields**
- `SketchNode` gains six optional `str` fields (default `""`):
  - Top-level focus: `what`, `value_created`, `scope`.
  - Sub-service focus: `value_created`, `trigger`, `how`, `outcome`.
  - The shared Do/Don't pair from Step 2 (`do`, `dont`) is reused.
- One model carries all six on every service node; the **Inspector**
  surfaces them per branch:
  - `kind === "service"` on the **services** canvas with no parent →
    Label · What · Value created · Scope · Do · Don't.
  - `kind === "service"` on a **service_detail** canvas →
    Label · Value created · Trigger · How · Outcome · Do · Don't.

### Notes — **No hard validator gating**
- The ROADMAP suggested gating top-level services on either a
  Foundation ref or non-empty `value_created`. Per the v0.10 design
  philosophy ("rich fields, minimal required"), this is **not** a
  hard validator: writes succeed regardless. The Inspector's typed
  form makes the missing fields visible without blocking drafting.
- Round-trip and per-branch tests added in `tests/test_canvas_doc.py`.

## [0.10.2] — 2026-04-28

Step 3 of the v0.10 kind-redefinition program. Generalises the existing
`actor_ref` Symbol/Component pattern to the three Foundation masters
(Mission / Core Value / Identity), so a Service can declare which
Foundation commitment it answers to without leaving its canvas.

### Added — **Foundation reference kinds**
- New node kinds: `mission_ref`, `value_ref`, `identity_ref`. Together
  with the pre-existing `actor_ref` they form a uniform four-member
  family of "instance points at master" symbols.
- New `SketchNode` fields: `ref_mission_id`, `ref_value_id`,
  `ref_identity_id` (each `str | None = None`). Validator rule: every
  `*_ref` kind requires its corresponding `ref_*_id` to be set.
- `_ALLOWED_KINDS_BY_CANVAS`: the three new ref kinds are admitted on
  the **Services** overview canvas and on **Service-Detail** canvases.
  They stay forbidden on Foundation (would be a self-loop) and on
  Actors (out of place there).

### Added — **Stencil presets + picker UI**
- New stencil entries on the Services-side stencil: Mission ref, Value
  ref, Identity ref (under a "Foundation refs" section). Each gets a
  distinct hue and Lucide icon (flag / star / heart) so the canvas reads
  at a glance.
- New `FoundationRefPicker` modal — drop a ref onto the canvas, the
  picker lists candidates pulled from the Foundation canvas (Mission /
  Core Value / Identity, depending on the kind dropped). Clicking one
  spawns the ref node with the right `ref_*_id` set and a `→ {label}`
  display label.
- `App` derives the three master lists (`availableMissions`,
  `availableValues`, `availableIdentities`) from the Foundation canvas
  cache and passes them down to the canvas/inspector.

### Added — **Inspector ref display**
- The Inspector shows a "References — {kind}" block for each ref node,
  listing the resolved master label or a "⚠ master not found" warning
  when the target doesn't exist (orphan).

### Notes
- The orphan re-pick UX from `actor_ref` is **not** generalised in this
  step — for now users can drop a fresh ref preset and delete the
  broken one. Re-pick is on the list for a follow-up patch.
- The validator does not (yet) cross-check that `ref_mission_id` etc.
  point at an actual master in the project's Foundation canvas: writes
  succeed even with stale ids so drafting stays cheap; the Inspector's
  orphan warning surfaces the issue interactively.

## [0.10.1] — 2026-04-28

Step 2 of the v0.10 kind-redefinition program (see
[`docs/ROADMAP.md`](docs/ROADMAP.md)). Re-introduces typed fields on
the remaining two Foundation kinds, with the AI-first **Do / Don't**
pair shared between them.

### Added — **Core Value typed fields**
- `SketchNode.definition` (`str`, default `""`) — what the value means.
- Inspector renders a typed form when `kind === "core_value"`:
  Label · Definition · Do · Don't.

### Added — **Identity typed fields**
- `SketchNode.description` (`str`, default `""`) — how the aspect is
  expressed (Voice / Energy / Speech style / …).
- Inspector renders a typed form when `kind === "identity"`:
  Label · Description · Do · Don't.

### Added — **Shared Do / Don't pair**
- `SketchNode.do`, `SketchNode.dont` (`str`, default `""`). Both fields
  exist on every node so the schema stays uniform; only the Inspector
  forms for `core_value` and `identity` surface them today. Future kinds
  (Mission, Service) may opt in without a schema migration.

### Notes
- All four new fields are optional and default to `""` — none of them
  introduce a validator that could reject a legacy canvas. Mirroring
  v0.10 Step 1's principle: "rich fields, minimal required".
- Long-form prose still belongs in `details.md` per node. Typed fields
  are for short, structured facets that an LLM (or human reader) can
  consume deterministically.

## [0.10.0] — 2026-04-28

This release kicks off the v0.10 kind-redefinition program (see
[`docs/CONCEPTS.md`](docs/CONCEPTS.md) and [`docs/ROADMAP.md`](docs/ROADMAP.md)).
Step 1 ships the rename of the identity canvas and the first AI-first typed
fields on `mission`. Subsequent steps will re-introduce typed fields on the
remaining kinds where the domain has clearly distinct facets.

### Changed — **`core` canvas → `foundation` canvas**
- Canvas kind/id rename: `"core"` → `"foundation"`. The folder is now
  `.plot/{project_id}/foundation/canvas.json`. Existing v0.5–v0.9 projects
  are migrated transparently on open: the `core/` directory is renamed to
  `foundation/` and the `canvas_kind` field is rewritten. Legacy alias
  `migrate.upgrade_core_canvas_if_needed` still works.
  ([`plot_mcp/folder_io.py`](plot_mcp/folder_io.py),
   [`plot_mcp/migrate.py`](plot_mcp/migrate.py),
   [`plot_mcp/models.py`](plot_mcp/models.py))
- Viewer tab label is now **Foundation** (not Core); `CanvasKind` /
  `CanvasKey` types match. Default folder slug is `foundation/…`.
  ([`viewer/src/types.ts`](viewer/src/types.ts),
   [`viewer/src/App.tsx`](viewer/src/App.tsx),
   [`viewer/src/lib/slug.ts`](viewer/src/lib/slug.ts))

### Added — **Mission typed fields** (AI-first)
- `SketchNode.what_we_do`, `SketchNode.why`, `SketchNode.direction` (all `str`,
  default `""`). These three facets are stored directly on the `mission` node
  in `canvas.json` — Plot is the sole editor. Long-form prose still lives in
  `details.md`. Other kinds also carry the fields as empty strings; only the
  Inspector for `kind === "mission"` exposes a typed form.
  ([`plot_mcp/models.py`](plot_mcp/models.py),
   [`viewer/src/types.ts`](viewer/src/types.ts),
   [`viewer/src/canvases/SketchInspector.tsx`](viewer/src/canvases/SketchInspector.tsx))

### Added — **Concept docs**
- [`docs/CONCEPTS.md`](docs/CONCEPTS.md) — the full glossary
  (4 canvases × 13 kinds + design principles). SSOT for human and AI tooling.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — six-step v0.10 implementation
  plan. Step 1 is this release.

### Notes
- Mission is **0..N** (was effectively 1..N). Validator unchanged; the doc
  surface now matches what the model already allowed since v0.5.
- Foundation rename is backward-compatible at the file-system layer — opening
  a v0.9 project rewrites it in place to the new layout.

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
