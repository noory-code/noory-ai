# Plot Roadmap — v0.10

The implementation order for the v0.10 kind redefinition. Each step is
an independent, ship-ready commit (Python green, viewer green, plugin
patch bumped, pushed). Together they realise the design captured in
[`CONCEPTS.md`](CONCEPTS.md).

> Status legend: `[ ]` not started · `[~]` in progress · `[x]` shipped.

## Step 1 — Foundation rename + Mission typed fields  `[ ]`

The smallest contained change, so it can land before anything else.

**Python**
- `CanvasKind` literal: rename `"core"` → `"foundation"`.
- `_ALLOWED_KINDS_BY_CANVAS["core"]` → `_ALLOWED_KINDS_BY_CANVAS["foundation"]`.
- `_core_canvas_rules` → `_foundation_canvas_rules` (function name, error
  messages, comparisons).
- `folder_io._canvas_file` already uses `canvas_kind` directly, so renaming
  flows through the disk path automatically (`.plot/{id}/foundation/canvas.json`).
- `migrate.upgrade_core_canvas_if_needed` — extend the early-version
  upgrader to also rename `core/canvas.json` → `foundation/canvas.json`
  on read (idempotent), so v0.9 disk layouts still open in v0.10.
- `SketchNode` typed fields:
  - `what_we_do: str = ""`
  - `why: str = ""`
  - `direction: str = ""`

**Viewer**
- `CanvasKind` / `CanvasKey` types: `"core"` → `"foundation"`.
- Tab labels and slugs follow.
- Inspector renders the three Mission fields when `kind === "mission"`.

**Tests**
- Update fixtures in `test_canvas_doc.py`, `test_folder_io.py`, etc., to
  the `foundation` kind name.
- Add a test that `mission` nodes round-trip with the typed fields.

**Verification**: `pytest -q`, `ruff`, `mypy`, `tsc --noEmit` clean.

## Step 2 — Core Value + Identity typed fields  `[ ]`

**Python**
- `SketchNode`:
  - `definition: str = ""` (core_value)
  - `description: str = ""` (identity)
  - `do: str = ""` (shared)
  - `dont: str = ""` (shared)

**Viewer**
- Inspector form maps:
  - `core_value` → label · definition · do · dont
  - `identity` → label · description · do · dont

**Tests**: round-trip + Inspector field rendering.

## Step 3 — Reference kinds (mission_ref / value_ref / identity_ref)  `[ ]`

Generalise the existing `actor_ref` symbol pattern to Foundation.

**Python**
- `NodeKind` literal: add `"mission_ref"`, `"value_ref"`, `"identity_ref"`.
- `SketchNode`: add `ref_mission_id`, `ref_value_id`, `ref_identity_id`
  (all `str | None = None`); pre-existing `ref_actor_id` stays.
- `_ALLOWED_KINDS_BY_CANVAS`:
  - `"services"` and `"service_detail"` accept all four ref kinds.
- Validators:
  - Each `*_ref` requires its corresponding `ref_*_id` set.
  - On canvas write, optionally check the referenced master exists in
    the Foundation canvas (warn, don't reject — orphans are useful
    while drafting).

**Viewer**
- Stencil: add Mission ref / Value ref / Identity ref draggables to the
  Services and Service-Detail stencils.
- Each ref kind gets a distinct shape/colour/icon.
- Picker modal (similar to ActorRefPicker) for the master to point at.

**Tests**: validator coverage, picker round-trip.

## Step 4 — Service typed fields (top vs sub)  `[ ]`

**Python**
- `SketchNode`: add service-relevant typed fields.
  - Shared: `what`, `value_created`, `scope`, `do`, `dont`.
  - Sub-only (the model just allows them; Inspector decides surfacing):
    `trigger`, `how`, `outcome`.
- Validator (services canvas): each top-level service has either an
  `identity_ref` or a `value_ref` placed near it (as a sibling node)
  OR a non-empty `value_created` field. Exact gating TBD during impl.

**Viewer**
- Inspector branches by canvas:
  - Service on `services` canvas → top-level field set + required
    Foundation ref hint.
  - Service inside a `service_detail` canvas → sub-service field set,
    all optional.

**Tests**: top vs sub field round-trip, Foundation-ref validator.

## Step 5 — New composition kinds (metric, step)  `[ ]`

**Python**
- `NodeKind`: add `"metric"`, `"step"`.
- `_ALLOWED_KINDS_BY_CANVAS["service_detail"]` includes both.
- `SketchNode` typed fields:
  - `target: str = ""` (metric)
  - `measurement: str = ""` (metric)
  - `order: int | None = None` (step)
  - `outcome: str = ""` — already added in Step 4 for service, shared
    semantically with step.

**Viewer**
- Stencil: add Metric / Step draggables to the Service-Detail stencil.
- Inspector renders kind-specific forms.

**Tests**: round-trip + visual stencil load.

## Step 6 — rule / content typed-field polish  `[ ]`

The composition kinds that already exist gain richer typed fields.

**Python**
- `SketchNode`:
  - `policy: str = ""` (rule)
  - `enforcement: str = ""` (rule)
  - `actor_permissions: dict[str, str] = {}` (rule, keyed by actor id;
    value is e.g. "RUD") — schema TBD when implementing.
  - `format: str = ""` (content)
  - `producer_actor_id: str | None = None` (content)
  - `consumer_actor_id: str | None = None` (content)

**Viewer**
- Inspector forms for `rule` and `content` kinds.
- For permissions, show a small actor × CRUD matrix UI keyed by the
  actor_refs already on the canvas.

**Tests**: round-trip + permission matrix serialisation.

---

## Cross-cutting items (apply to all steps)

- Each step ends with: ruff + mypy + pytest + tsc all green.
- Each step bumps `plugin.json` and adds a `CHANGELOG.md` entry.
- `details.md` per node continues to behave exactly as in v0.9.1 — no
  changes there.
- The watcher and broadcast layers don't need changes; new typed fields
  ride along on existing canvas write paths.

## Out of scope for v0.10

- The "edge utilisation strategy" — keep the existing `action_verb` /
  `value_form` edge metadata as-is; revisit only after the kind
  redefinition is shipped.
- The future task / time-axis layer — Plot keeps room for it (the
  service model doesn't preclude a `delivery_status` typed field
  later) but no work in v0.10.
- Renaming `core_value` to a shorter name — kept as `core_value` per
  user direction in the kind review.
