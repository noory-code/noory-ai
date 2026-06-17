# SERVICES_PLAN — implementing the 2026-06-17 Services-overview redesign

> **Status: PLAN (2026-06-17).** Build order for the Services *overview* canvas
> changes pinned in the big-picture review: service inspector → 5 question-titled
> fields with 3 multi-select reference pickers (`D-2026-06-17-B`), a new `feature`
> node nested under a service + drill rewire (`D-2026-06-17-D`), `category`
> dumb-down (`D-2026-06-17-D`), and dropping the service→service edge affordance
> (`D-2026-06-17-C`) ([DECISIONS.md](./DECISIONS.md)). Concept SSOT =
> [BIG_PICTURE_REVIEW.md](./BIG_PICTURE_REVIEW.md) rows 13-20. **Code is currently
> UNCHANGED** — decisions live in docs only; this file is the implementation queue.
> The **Feature canvas** (renamed `service_detail`) and **Entities** get their own
> plan files (`D-2026-06-17-E/G/H` → FEATURE_PLAN; `D-2026-06-17-I` → ENTITY_PLAN).
> TDD per CLAUDE.md Gate 1.5.

## Goal

Turn the Services overview into the pinned shape: a service node carries a 5-field
question-titled inspector (2 typed-text + 3 multi-select reference chips) instead
of the 11 legacy text fields; a new `feature` node nests under a service and is the
**only** node that drills (selecting a service shows its inspector, never drills);
`category` becomes a low-friction visual grouping with a minimal inspector; and the
canvas no longer offers a service→service edge. Every field move is **loss-free**.

## Blocking pre-flight — reconcile the 15/17 kind-count drift FIRST (`D-2026-06-17-D`)

The guards already disagree before this plan adds a kind. `schema_export._ALL_KIND_CLASSES`
+ `tests/test_schema_parity.py` `test_all_kinds_covered` (L169) hardcode **15**
(no `decision`/`group`); `viewer/tests/structural-guards.test.tsx` `KIND_DIRS`
(L54-72) + `NODE_RENDERERS` (the "exactly the 17 kinds" assert) hardcode **17**
(adding `decision` + `group`). `decision`/`group` exist viewer-side with per-kind
dirs but have no Pydantic class in `_ALL_KIND_CLASSES`.

- **Decision needed before any kind add:** does `feature` raise the count to 16/18,
  or do we first land `decision`/`group` server-side (15→17) so both guards count
  the same set? Adding `feature` to only one side fails one guard immediately.
- This is a **product/architecture decision** — open a `D-2026-06-17-*` entry that
  states the chosen reconciliation, then proceed. Do **not** silently bump one
  number. (Out of scope to *resolve* `decision`/`group` parity here; in scope to
  **not build on top of the drift unconsciously**.)

## Per-change scope (lands in lock-step)

Every kind change touches all of these together (schema parity is enforced):

- viewer domain class `viewer/src/domain/{Kind}.ts` (field set + `fromJson` migration)
- both unions in `viewer/src/domain/SketchNode.ts` + `NodeKind` in `viewer/src/types.ts`
- `viewer/src/domain/createBlankNode.ts` factory `case`
- server pydantic model in `plot_mcp/models_actors.py` + union `plot_mcp/models_union.py`
  + `NodeKind` Literal `plot_mcp/models_kinds.py` + `_ALL_KIND_CLASSES` `plot_mcp/schema_export.py`
- per-canvas allowed-kind gate `plot_mcp/models_canvas.py::_ALLOWED_KINDS_BY_CANVAS`
- per-kind renderer `viewer/src/canvases/nodes/{kind}/index.tsx` + inspector
  `viewer/src/canvases/inspectors/{kind}/index.tsx` + both registries
- i18n keys en/ko for every renamed/added field/label/placeholder
- tests: `entity-roundtrip`, inspector behaviour, schema parity (count bump),
  structural guards (`KIND_DIRS` ×2 + count assert)

**Procedure:** TDD (Red→Green→Refactor, CLAUDE.md Gate 1.5) via the
`plot-entity-template` / `plot-feature-tdd` skills. Files stay <500 LOC
(`tests/test_module_size.py`); per-kind node ≤100, inspector ≤250.

## Build order (smallest-first)

### 1. Drop the service→service edge affordance (`D-2026-06-17-C`)
- There is **no current source/target-kind edge validator** — `handleConnect`
  (`viewer/src/canvases/sketch/useFlowHandlers.ts` L61-111) accepts any pair and
  only sets `relation` via `classifyEdge`. So "no service→service edge" is
  **net-new reject logic**, not a tweak.
- Add a guard in `handleConnect`: after direction normalization, reject (early
  return, no edge appended) when on the `services` canvas both endpoints resolve to
  `kind === "service"`. Mirror server-side in
  `plot_mcp/models_canvas.py::CanvasDoc` (a `@model_validator` alongside
  `_edges_reference_nodes`, L89) so a hand-edited file can't smuggle one in.
- Remove any "user journey" edge wording from PRODUCT_SPEC §7 (doc-sync, step 7).
- **Smallest-first rationale:** it touches no kind, so it lands before the count
  reconciliation and the `feature` add.
- Tests (Red first): dragging service→service on the `services` canvas produces
  **no** new edge (viewer); a `CanvasDoc` with a service→service edge fails
  validation (server); a service→`feature` or category→service edge still succeeds
  (don't over-block).

### 2. Category dumb-down — minimal inspector (`D-2026-06-17-D`)
- `category` already is the lightest service-overview node (`theme` + `body`,
  `plot_mcp/models_actors.py::CategoryNode` L80-87,
  `viewer/src/canvases/inspectors/category/index.tsx`). The decision = "visual
  grouping only, low-friction, minimal inspector" — confirm the current inspector
  is already minimal and trim if `theme`+`body`+empty-warning still feels heavy.
- **No schema change** unless we drop a field. If `theme` survives, this is an
  inspector-copy + intent edit only (re-anchor the hint to "visual grouping, dumb").
  If we drop `body`, that is a kind field change → fold loss-free into `theme` on
  read, and it joins the lock-step + parity count run.
- Keep the empty-category warning (UX feedback) — it earns its place.
- Tests: inspector renders the minimal field set; if a field is dropped, roundtrip
  + loss-free migration; structural guard that `category` stays in `KIND_DIRS`.

### 3. (Conditional) reconcile kind count to a single number (pre-flight outcome)
- Land whatever the pre-flight `D-` entry decided (e.g. add `decision`/`group` to
  `_ALL_KIND_CLASSES` + bump `test_schema_parity` 15→17, OR explicitly pin the
  asymmetry as intentional). This step exists so step 4 lands against **one**
  consistent count.
- Tests: `test_all_kinds_covered` and the structural-guards count assert agree.

### 4. NEW `feature` kind + node + inspector, nested under a service (`D-2026-06-17-D`)
Full `plot-entity-template` lock-step walk (an **entity**, has its own id/node):
- **viewer domain:** `viewer/src/domain/Feature.ts` — `FeatureJson extends
  BaseFieldsJson`, `class Feature` (private ctor, `fromJson` throwing
  `DomainParseError` at the boundary, `toJson`, trailing
  `registerKindParser("feature", …)`). Field: `proposed` (one-line
  "무엇을 할 수 있나?"). The read-only flow preview is **derived** from the feature's
  detail canvas, not a stored field — keep it OUT of `FeatureJson` (OPEN-but-leaning:
  preview is a view affordance; confirm before adding any stored field).
- **viewer unions/factory:** add `"feature"` to `SketchNode`/`SketchNodeJson`
  (`SketchNode.ts`, alphabetical), `NodeKind` (`types.ts`), barrel
  (`domain/index.ts`), and a `case "feature":` in `createBlankNode.ts` (palette
  colour cross-checked in `canvases/sketch/palette.ts`).
- **server:** `FeatureNode(BaseNodeFields)` in `plot_mcp/models_actors.py` (sibling
  to `ServiceNode`; if it pushes the file >500 LOC, new module per
  `test_module_size.py`); register in `models_union.py`, `NodeKind` Literal in
  `models_kinds.py`, `_ALL_KIND_CLASSES` in `schema_export.py`. Field-set MUST equal
  `FeatureJson` or parity fails.
- **allowed-canvas gate:** add `"feature"` to `_ALLOWED_KINDS_BY_CANVAS["services"]`
  in `plot_mcp/models_canvas.py` (L52). "Nested under a service" = a directed edge
  service→feature (the same child mechanism `category`→`service` uses; not
  `parent_id`, which was removed D-2026-05-25-A). Confirm whether a `@model_validator`
  should require a feature's parent edge to originate from a `service` (lean: yes,
  symmetric to `_service_detail_actor_refs_minimum`).
- **UI:** `viewer/src/canvases/nodes/feature/index.tsx` (wraps `BaseNode`, ≤100 LOC)
  + `viewer/src/canvases/inspectors/feature/index.tsx` (≤250 LOC) rendering the
  `proposed` one-liner + the read-only flow preview (preview marked OPEN/not
  finalized in the decision — render a placeholder if the preview source isn't wired
  yet, don't fake content). Register in `nodes/registry.ts` + `inspectors/registry.ts`.
- **i18n:** `kind.feature.{label,description}` + `inspector.feature.field.proposed`
  (+ `.hint`) in BOTH `viewer/src/i18n/locales/en.json` and `ko.json` (the existing
  `inspector.field.*` block is L237-272; follow the existing flat shape unless the
  per-kind `inspector.{kind}.field.*` convention from the skill is adopted — match
  whatever the neighbouring kinds use to avoid `i18n-keys-parity` drift).
- **guards:** add `"feature"` to `KIND_DIRS` in BOTH
  `viewer/tests/structural-guards.test.tsx` (L54-72) **and**
  `viewer/tests/styles-cursor-baseline.test.tsx`; bump the "exactly the N kinds"
  assertion; bump the parity count from step 3's number.
- Tests (Red first): `entity-roundtrip` `feature` case (`fromJson∘toJson` identity);
  `feature` renders + appears in `NODE_RENDERERS`; server rejects `feature` on
  non-`services` canvases; service→feature child edge validates.

### 5. Drill rewire — service = inspector-only, feature = drill target (`D-2026-06-17-D`)
Supersedes the service-as-detail drill (D-2026-05-28-B + the drill portion of
D-2026-06-15-H). The routing brain
(`viewer/src/canvases/sketch/useInspectorRouting.ts`) is **parameterised** — no
change there; only the wrapper predicates + the App drill condition move:
- `viewer/src/canvases/ServicesCanvas.tsx`: change `shouldDrillService`
  (L8-10, currently `n.kind === "service" && !n.is_root`) to target
  `n.kind === "feature"`. Keep `selectOpensDrill={true}` so a single click on a
  feature drills; with the predicate retargeted, a service single-click now falls
  through to `setInspectorNodeId` (inspector-only) automatically.
- `viewer/src/App.tsx` `onMainNodeDrill` (L298-316): change the condition
  `activeTab === "services" && n.kind === "service" && !n.is_root → drillIntoService`
  to `n.kind === "feature"`. The `actor_ref → jumpToActor` branch (L303) stays.
- `viewer/src/hooks/useUrlSync.ts`: owns `detailServiceId`/`drillIntoService`/
  `?detail=<id>`. The drill *target id* is now a feature id, not a service id —
  rename/repoint (`detailFeatureId`?) so the `?detail=` param + dynamic detail tab
  point at the feature whose detail canvas opens. Coordinate with FEATURE_PLAN
  (the detail canvas is the renamed `service_detail`).
- `viewer/src/shell/CanvasTabs.tsx` `detailLabel`: now labels the feature's detail
  tab, not the service's. Copy/i18n update.
- **Server detail seeding** (`plot_mcp/detail_sync.py::sync_details_with_overview`
  L31): today seeds one detail canvas **per service**. If detail canvases are now
  **per feature**, the seeding key changes — flag as a FEATURE_PLAN dependency, do
  NOT silently rewire here (it crosses the canvas boundary owned by that plan).
- Tests (Red first): single-click a `service` on the Services canvas → inspector
  opens, NO drill (`drillIntoService` not called); single-click a `feature` → drill
  fires; double-click a `service` → no navigation; `actor_ref` double-click still
  jumps to actor.

### 6. Service inspector → 5 question-titled fields + delete the 9 legacy fields (`D-2026-06-17-B`)
Two typed-text fields stay/rename; three become multi-select reference chips; nine
fields are deleted. **Loss-free migration** for the renamed text; **no migration
needed** for the deleted text (it was authored content the user is dropping — but
fold non-empty deleted values into `body` on read so nothing silently vanishes,
unless a `D-` entry explicitly approves discarding them).

**Field map (`Service`):**
- KEEP+RENAME `problem` → titled **"왜 필요한가?"** (the gap/need). Field key can
  stay `problem` (rename is label-only) to minimise schema churn — confirm.
- KEEP+RENAME `value_created` → titled **"뭐가 좋아지나?"**. Key stays `value_created`.
- DELETE entirely: `target_side`, `what`, `scope`, `trigger`, `how`, `outcome`,
  `do`, `dont`, `body`. (Note: `body` deletion removes the fold-target — decide the
  loss-free sink for deleted content BEFORE removing `body`; options: keep `body` as
  a hidden migration sink, or pin discard in the `D-` entry. Do not drop `body`
  without resolving this.)

**The 3 multi-select reference pickers** ("누가 참여하나?" = actor refs;
"뭘 양보 못 하나?" = core_value refs; "어떤 결로 다가가나?" = identity refs) — these
are **references, not Service text fields**. Plot's existing model is "refs are
separate `*_ref` nodes on the canvas" (`actor_ref` / `value_ref` / `identity_ref`),
(the former "all edges user-drawn / never auto-emit" constraint was **removed** by
`D-2026-06-17-J` — edges are governed by their **definition**, not authorship, so a
chip *may* emit a ref edge). The remaining choice is purely a **modelling** one:
- **Option A (refs stay nodes):** the inspector multi-select spawns/links
  `actor_ref`/`value_ref`/`identity_ref` nodes wired to the service by a user-
  confirmed edge. Reuses `FoundationRefPicker.tsx` (single-pick today, L35/L80 —
  **needs multi-select rewrite**: checkbox + `Set` state), `ActorRefPicker.tsx`,
  `FoundationRefBlock.tsx`, `useAvailableNodes.ts` (feeds
  `availableActors/Missions/Values/Identities`). The chip **may emit the ref edge
  directly** (allowed since `D-2026-06-17-J`); the user can still edit / delete it,
  and the edge carries a defined `relation`.
- **Option B (refs become arrays on Service):** add `ref_actor_ids: string[]` /
  `ref_value_ids` / `ref_identity_ids` to `ServiceJson` + `ServiceNode`. Then
  schema-parity must accept array fields (today every per-kind field is a scalar —
  verify `_ts_kind_fields` / `test_per_kind_field_parity` handle `string[]`), and
  the "refs are nodes" model forks (chips on service vs ref nodes elsewhere).
- **This is a domain decision, not a file edit.** Run `plot-domain-design` and pin
  the choice in a `D-2026-06-17-*` entry BEFORE writing code. The survey flagged
  this conflict; do not invent the answer.

**Files (once A/B is pinned):**
- `viewer/src/domain/Service.ts`: delete the 9 fields from `ServiceJson`, class
  props, ctor params, `fromJson` reads, `toJson` keys; keep `problem` +
  `value_created`; add the ref array fields **iff Option B**. `Service.fromJson`
  carries the loss-free migration for any folded content. Drop the now-unused
  `readTargetSide` helper.
- `plot_mcp/models_actors.py::ServiceNode` (L57-77): delete the same 9 fields; add
  ref arrays iff Option B. Must stay field-set-identical to `ServiceJson`.
- `viewer/src/canvases/inspectors/service/index.tsx`: rewrite `ServiceFields`
  (L84-168) + `ServiceFieldsReadonly` (L173-213) to the 5 question-titled fields;
  remove the `DoDontFields` + `BodyField` imports (L15-16) + the `target_side`
  `<select>` (L99-121); remove deleted-field rows from the read-only summary
  (L184-194). The `CompositionList` rules/contents panels (L48-71) belong to the
  FEATURE canvas now — confirm with FEATURE_PLAN whether they leave the service
  inspector here.
- Shared `DoDontFields.tsx` / `BodyField.tsx`: they drop out of the **service**
  inspector but are shared — audit other consumers (`rule`/`content`) before
  deleting the shared files; if still used, leave them.
- i18n: in `en.json`+`ko.json`, the field **titles ARE the AI interview questions**
  — the 5 question strings (`inspector.field.problem`/`valueCreated` relabeled +
  3 new ref-picker headings) must read as natural questions, not nouns. Delete keys
  for `targetSide`/`what`/`scope`/`trigger`/`how`/`outcome`/`do`/`dont` (en L241-247,
  L266-267) **only if no other kind uses them** (e.g. `polarity`/`do`/`dont` may be
  shared — grep first). `i18n-keys-parity.test.tsx` gates en/ko drift.
- `viewer/src/canvases/nodes/service/index.tsx`: no change (renders label/chrome only).
- Tests (Red first): `Service.fromJson` of a legacy 11-field node loses no content
  (deleted text folded or discard-pinned); roundtrip identity on the new field set;
  inspector renders exactly 5 question-titled fields; multi-select picker adds N
  refs (per the A/B choice); schema parity green on the new `ServiceNode` field set.

### 7. Doc-sync (CONCEPTS / SPEC / PRODUCT_SPEC — Services-overview slice)
- `docs/CONCEPTS.md`: update the `service` row (5-field inspector, refs model per
  A/B); add the `feature` kind row (purpose, bounded context, canvas = services,
  typed field `proposed`, drill target, edge legality); trim `category` row to
  "visual grouping, minimal".
- `docs/SPEC.md` Services section: service = inspector-only (no drill); feature =
  drillable; no service→service edge; category = dumb grouping.
- `docs/PRODUCT_SPEC.md §7`: remove the "user journey" service→service edges
  (`D-2026-06-17-C`); note the canvas inventory unchanged (overview stays
  `services`).
- Leave Feature-canvas + Entity concepts to FEATURE_PLAN / ENTITY_PLAN (don't
  duplicate — SSOT).

### 8. Gate-4 bookkeeping
- Bump `plot/.claude-plugin/plugin.json` `version` (minor — new `feature` kind +
  inspector redesign) from `0.86.0`.
- `plot/CHANGELOG.md`: **Added** (`feature` kind, 5-question service inspector,
  multi-select ref pickers); **Changed** (service drill → inspector-only, category
  dumb-down); **Removed** (9 legacy service fields, service→service edge).
- `docs/DECISIONS.md`: the design `D-2026-06-17-B/C/D` already exist; add
  implementation/`D-` entries for the pre-flight count reconciliation and the
  service-ref A/B modelling choice (What/Why/Alternatives/Approval/Spec impact).

## Out of scope (separate, already tracked)

- **Feature canvas** (renamed/repurposed `service_detail`) node inventory
  keep/retire (`mission_ref`/`value_ref`/`identity_ref`/`metric`/`content`/`group`),
  `rule` semantics, `note` kind, altitude guard → **FEATURE_PLAN**
  (`D-2026-06-17-E/F/G/H`).
- **Entities** canvas + `entity` kind + AI-surfacing UX (`D-2026-06-17-I`, discussion
  NOT finished, 5 OPEN questions) → **ENTITY_PLAN**.
- AI interview-question wiring (titles double as questions, but the prompt/MCP plumbing) → ROADMAP 5.7.
- Resolving the `decision`/`group` server-side parity gap beyond the pre-flight
  count reconciliation needed to land `feature`.

## Risks / dependencies

- **Ordering:** step 1 (edge) → step 2 (category) → step 3 (count reconcile) →
  step 4 (feature kind) → step 5 (drill rewire) → step 6 (service inspector). Steps
  5 and 6 both touch the service↔feature boundary; land 4 before 5, 5 before 6 so
  the inspector rewrite sees the final drill model.
- **Cross-plan coupling:** detail-canvas seeding (`detail_sync.py`) and the
  `CompositionList` rules/contents panels straddle this plan and FEATURE_PLAN —
  named here, owned there. Do not rewire them in this plan without a FEATURE_PLAN
  handshake (Gate: 부분 완료 금지 — if a change needs both, name both).
- **15/17 drift:** building `feature` on top of an unreconciled count fails one
  guard on first commit. Pre-flight is blocking, not optional.
- **Refs-as-chips modelling (A nodes+edges vs B arrays):** the edge-rule blocker is
  **gone** (`D-2026-06-17-J` — a chip may emit a ref edge). Remaining choice = A
  (refs stay `*_ref` nodes; chip emits/links an editable edge) vs B (ref-id arrays
  on Service; needs array-field parity). Pin via `D-` before code.
- **Loss-free deletion of `body`:** `body` is the conventional fold sink; deleting
  it removes the sink for the other 8 deleted fields. Resolve the sink (keep `body`
  hidden, or pin discard) before removing it.

## Done when

The Services overview renders services with a 5-question inspector (2 typed +
3 multi-select reference chips, per the pinned A/B model) and no legacy 9 fields;
a `feature` node nests under a service and is the sole drill target while selecting
a service opens its inspector only; `category` is a minimal visual grouping; no
service→service edge can be drawn or hand-loaded; every field move is loss-free; the
kind count is reconciled to one number across `schema_export`/`test_schema_parity`
and `structural-guards`/`styles-cursor-baseline`; and migration loss-free + schema
parity + structural guards + i18n parity + doc-sync are all green.
