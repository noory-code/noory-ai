# FEATURE_CANVAS_PLAN — implementing the 2026-06-17 Feature-canvas redesign

> **Status: PLAN (2026-06-17).** Converts the current Service-Detail canvas into
> the **FEATURE** canvas — an actor-anchored behaviour flowchart at action
> altitude — per `D-2026-06-17-E` / `D-2026-06-17-G` / `D-2026-06-17-H`
> ([DECISIONS.md](./DECISIONS.md)). Concept SSOT = those three entries +
> [BIG_PICTURE_REVIEW.md](./BIG_PICTURE_REVIEW.md) rows 18–20.
> **Code is currently UNCHANGED** — `service_detail` canvas exists and already
> renders the actor-anchored layout; this file is the implementation queue.
> TDD per CLAUDE.md Gate 1.5. **Sibling:** the drill-rewire + `feature` kind +
> service-inspector rewrite live in [`SERVICES_PLAN.md`](./SERVICES_PLAN.md);
> this file owns only the FEATURE canvas (the drill *target*).

## Reconcile-first blocker (do before any kind add/retire)

The kind count is **already drifted across guards** and any kind change here
fights it:

- `plot_mcp/schema_export.py::_ALL_KIND_CLASSES` + `tests/test_schema_parity.py`
  (`test_all_kinds_covered`, asserts `len(...) == 15`) + `tests/test_schema_export.py`
  (`test_export_writes_all_15_kind_schemas`) count **15** — they exclude
  `decision` and `group`.
- `viewer/tests/structural-guards.test.tsx` `KIND_DIRS` (lines 54–72) +
  `NODE_RENDERERS` ("exactly the 17 kinds", line 226) +
  `viewer/tests/styles-cursor-baseline.test.tsx` `KIND_DIRS` count **17** —
  they include `decision` and `group`.

This plan **removes** `group` (D-H) and **adds** `note` (D-F). After the work the
viewer set is 16 (17 − group + note) and the server set is 15 (15 + note − metric
− content; refs stay server-side until the retire steps land). **Do not invent a
single magic number** — each guard's count is recomputed per step below. Land
step 0 first so the two sides stop disagreeing on `decision`/`group` before the
churn starts.

### 0. Reconcile decision/group across the parity SSOTs (no `D-` needed — drift fix)
- Decide consciously whether `decision`/`group` belong in `_ALL_KIND_CLASSES`.
  `decision` is **KEPT** (D-H node inventory) so it must gain a Pydantic class +
  parity coverage; `group` is **RETIRED** (D-H) so it leaves the viewer set in
  step 6. After this plan both sides should agree.
- Tests (Red first): `tests/test_schema_parity.py` count assertion + the viewer
  `NODE_RENDERERS`/`KIND_DIRS` count assertions are edited **together** in each
  step that changes the kind set; never edit one number without the other.

## Already correct (no change)

- The `service_detail` canvas already renders the **actor-anchored layout**
  (`models_canvas.py::_service_detail_actor_refs_minimum`, line 201; SPEC.md
  §"Actor-anchored layout" D-2026-05-28-J). D-G confirms this layout *is* the
  feature flowchart's frame. **Keep the layout; rename the surface.**
- `step` (행동), `decision` (분기), flow **edges**, `rule`, `actor_ref` already
  live in `_ALLOWED_KINDS_BY_CANVAS["service_detail"]` (`models_canvas.py`
  lines 53–63). **Keep all five.** Per `D-2026-06-17-H`.
- `rule` stays a **per-feature operational constraint** (password ≥ N chars) —
  `domain/Rule.ts` + `models_*.py::RuleNode` unchanged. Per `D-2026-06-17-E`;
  no schema edit, only a CONCEPTS wording sync (step 8).

## Per-change scope (every kind add/retire lands in lock-step)

A kind change is never one file. The `plot-entity-template` walk
(`noory-ai/.claude/skills/plot-entity-template/SKILL.md`) is mandatory; retiring
is its reverse. Each add/retire touches **all** of:

- viewer domain class `viewer/src/domain/{Kind}.ts` (+ `registerKindParser`)
- both unions in `viewer/src/domain/SketchNode.ts`, the `NodeKind` union in
  `viewer/src/types.ts`, the factory branch in `viewer/src/domain/createBlankNode.ts`,
  the barrel `viewer/src/domain/index.ts`
- server Pydantic model in `plot_mcp/models_*.py` + the `NodeKind` Literal in
  `plot_mcp/models_kinds.py` + the union in `plot_mcp/models_union.py` +
  `plot_mcp/models.py` re-export + `plot_mcp/schema_export.py::_ALL_KIND_CLASSES`
- per-kind renderer `viewer/src/canvases/nodes/{kind}/index.tsx` (≤100 LOC) +
  inspector `viewer/src/canvases/inspectors/{kind}/index.tsx` (≤250 LOC); both
  auto-picked by `nodes/registry.ts` + `inspectors/registry.ts`
- `viewer/src/i18n/locales/{en,ko}.json` (`kind.{kind}.*` + inspector field keys)
- the canvas gate `_ALLOWED_KINDS_BY_CANVAS` in `plot_mcp/models_canvas.py`
- guards: `KIND_DIRS` in **both** `viewer/tests/structural-guards.test.tsx` **and**
  `viewer/tests/styles-cursor-baseline.test.tsx` (dual SSOT), the count assertions,
  `tests/test_schema_parity.py`, `tests/test_schema_export.py`,
  `viewer/tests/entity-roundtrip.test.tsx`, `viewer/tests/i18n-keys-parity.test.tsx`,
  `tests/test_module_size.py` (500-LOC cap)

**Procedure:** TDD (Red→Green→Refactor, CLAUDE.md Gate 1.5).

## Build order (smallest-first)

### 1. NEW `note` kind — edgeless, canvas-global, AI-framing-injected (`D-2026-06-17-F`)
- Add the kind via the full `plot-entity-template` walk (all files in
  Per-change scope above). `domain/Note.ts`: `NoteJson extends BaseFieldsJson`,
  private ctor, `static fromJson` (the JSON↔domain boundary; invariants throw
  `DomainParseError` here), `toJson`, trailing `registerKindParser("note", Note.fromJson)`.
  Fields = `label` + `body` only (the ambient memo text); no refs, no targets.
- Server: `NoteNode` Pydantic model, `kind: Literal["note"]`; add to
  `_ALL_KIND_CLASSES` (15 → 16 server-side, **temporarily** — drops back when
  metric/content retire in step 5) and bump `test_schema_parity` +
  `test_schema_export` counts in tandem.
- **Allowed-canvas gate:** add `"note"` to `_ALLOWED_KINDS_BY_CANVAS["service_detail"]`
  in `plot_mcp/models_canvas.py` (lines 53–63). FEATURE canvas only for now
  (extensible later — YAGNI, per D-F).
- **Edgeless invariant (net-new logic — this is the load-bearing part):**
  - Viewer reject: guard in `viewer/src/canvases/sketch/useFlowHandlers.ts::handleConnect`
    (line 61) — reject the connection when source **or** target kind is `note`.
    There is no source/target-kind edge validator today; `handleConnect` accepts
    any pair and `classifyEdge` only sets `relation`, so the block belongs here,
    **not** in `flow/edgeSemantics.ts::classifyEdge`.
  - Server reject: a `note` endpoint must fail `CanvasDoc` validation. Add a
    `@model_validator` (sibling to `_edges_reference_nodes`, `models_canvas.py`
    line 89) that raises if any edge's source/target resolves to a `note` node.
    Mirror the viewer rule so a hand-edited / MCP-written doc can't smuggle one in.
- **AI-framing injection:** the note text is injected into the per-canvas AI
  framing. The framing assembly is `plot_mcp/chat_context.py` (shared by in-app
  + MCP paths; SPEC.md line 131, D-2026-06-15-C `_SCOPE_FRAMING`). Add: when the
  `service_detail`/feature scope framing is assembled, append the canvas's `note`
  bodies as ambient context. **This is server-side framing, not a node edge** —
  keep it out of the canvas graph.
- Stencil: add a `NOTE` preset to `STENCIL_PRESETS` (`viewer/src/canvases/SketchStencil.tsx`,
  ~line 256) + a section in the `service_detail` branch (lines 464–538) so the
  user can place one. No drop-onto-edge target (`resolveDropTarget`, lines 287–334).
- **Tests (Red first):**
  - `entity-roundtrip`: `note` `fromJson∘toJson` identity.
  - edgeless invariant: `handleConnect` rejects a connection whose endpoint is a
    `note` (viewer); `CanvasDoc` raises on a `note`-referencing edge (`tests/test_*`).
    Pin the invariant as a **structural guard** too, not just a behaviour test —
    "note never gains an edge" is the spec's hard line.
  - AI-framing: `chat_context` includes the note body in the assembled
    `service_detail` framing (server test).
  - schema parity + i18n parity + structural-guards count bump (16 viewer / 16
    server **transiently** before step 5).
- **Loss-free note:** none — net-new kind, no migration.

### 2. RETIRE `mission_ref` from the FEATURE canvas (`D-2026-06-17-H`)
- D-H: refs moved to the **service inspector chips** (D-2026-06-17-B,
  `SERVICES_PLAN.md`); the feature *inherits* them, so duplicating on the canvas
  is redundant. The feature canvas was their **only** home → full retirement of
  the kind, confirmed by D-H spec-impact ("likely retired entirely").
- Remove from **all**: `viewer/src/domain/MissionRef.ts`, both unions in
  `SketchNode.ts`, `NodeKind` in `types.ts`, `createBlankNode.ts` case, the barrel;
  `viewer/src/canvases/nodes/mission_ref/` + `inspectors/mission_ref/`; both
  registries; `KIND_DIRS` in `structural-guards.test.tsx` **and**
  `styles-cursor-baseline.test.tsx` + the count assertion; `kind.mission_ref.*`
  + field keys in `en.json` + `ko.json`; server `models_actors.py::MissionRefNode`
  (line 90), `_ALL_KIND_CLASSES`, the union, the `NodeKind` Literal,
  `test_schema_parity`/`test_schema_export` counts.
- Remove from the gate: drop `mission_ref` from `_FOUNDATION_REFS`
  (`models_canvas.py` line 36) — but note `_FOUNDATION_REFS` is also admitted on
  the `services` canvas historically; **confirm** whether the chips-rewrite
  (`SERVICES_PLAN.md`) has already removed refs from `services` before deleting
  the set, else scope this to the `service_detail` entry only and leave the set.
- Stencil: prune `MISSION_REF` (`SketchStencil.tsx` line 138) +
  `missionRefPresetFor` (line 580) from the `service_detail` branch.
- Shared ref machinery: `mission_ref` participates in `injection`-edge
  classification — audit `ESSENCE_SOURCE_KINDS` in
  `viewer/src/flow/edgeSemantics.ts` (line 23) + `plot_mcp/edge_semantics.py`
  (line 28); remove `mission_ref` only (value_ref/identity_ref handled in step 3).
- **Tests (Red first):** `registry-completeness` no longer expects
  `mission_ref`; the count drops; `entity-roundtrip` no longer iterates it;
  schema parity green. A guard asserting the per-kind dirs are **absent**
  (mirror of `GOD_FILES_ABSENT`) prevents accidental re-creation.

### 3. RETIRE `value_ref` and `identity_ref` from the FEATURE canvas (`D-2026-06-17-H`)
- Same reverse-walk as step 2, ×2, for `value_ref` (`models_actors.py` line 107,
  `domain/ValueRef.ts`, `nodes/value_ref/`, `inspectors/value_ref/`,
  `VALUE_REF`/`valueRefPresetFor` at `SketchStencil.tsx` lines 151/596) and
  `identity_ref` (`models_actors.py` line 123, `domain/IdentityRef.ts`,
  `nodes/identity_ref/`, `inspectors/identity_ref/`, lines 163/612).
- With all three refs gone, retire the now-orphaned shared ref UI:
  `inspectors/shared/FoundationRefBlock.tsx`, `FoundationRefPicker.tsx`,
  `canvases/sketch/useOrphanActorRefs.ts` — **only if** no surviving kind imports
  them. **`actor_ref` is KEPT** and may share `FoundationRefPicker`/orphan logic;
  grep importers before deleting any shared file, retire only the dead ones.
- Finish the `ESSENCE_SOURCE_KINDS` prune in both `edgeSemantics` files (line 23 /
  line 28) — after this step the three foundation refs are gone from the
  injection-edge set.
- Drop `_FOUNDATION_REFS` (`models_canvas.py` line 36) and its union into
  `_ALLOWED_KINDS_BY_CANVAS["service_detail"]` (line 63), pending the step-2 caveat
  about the `services` canvas usage.
- **Tests:** counts drop by 2 (both viewer + server in tandem); parity + roundtrip
  + i18n parity green; absent-dir guards added.

### 4. RETIRE `metric` from the FEATURE canvas (`D-2026-06-17-H`)
- D-H: "not needed." Its only canvas home is `service_detail`. Full retirement.
- Reverse-walk: `viewer/src/domain/Metric.ts`, `nodes/metric/`,
  `inspectors/metric/`, unions, `types.ts`, factory, barrel, both `KIND_DIRS` +
  count, i18n `kind.metric.*`; server `models_composition.py::MetricNode`,
  `_ALL_KIND_CLASSES`, union, Literal, parity/export counts.
- Stencil: prune the `SERVICE_COMPOSITION` "Value"-relabelled metric preset
  (`SketchStencil.tsx` line 189 + line 479).
- **Tests:** counts drop; parity/roundtrip green; absent-dir guard.

### 5. RETIRE `content` from the FEATURE canvas (`D-2026-06-17-H`)
- D-H: implementation artifacts = **below action-altitude** = the AI agent's job;
  user-facing artifacts are implied by the producing action or carried by the flow
  edge. Full retirement (its only home was Service-Detail, inspector-only).
- Reverse-walk: `viewer/src/domain/Content.ts`, `nodes/content/`,
  `inspectors/content/`, unions, `types.ts`, factory, barrel, both `KIND_DIRS` +
  count, i18n; server `models_composition.py::ContentNode`, `_ALL_KIND_CLASSES`,
  union, Literal, parity/export counts.
- `content` is **inspector-only** (rendered via `inspectors/service/CompositionList.tsx`,
  not the canvas stencil) — remove its row there; confirm `CompositionList`
  survives for any other consumer or retire it.
- **Tests:** counts drop; parity/roundtrip green; absent-dir guard. After this
  step + steps 2–4 the **server `_ALL_KIND_CLASSES` lands back at 15** (16 from
  the note add, −metric −content, and the three refs were never in the
  decision/group gap) — recompute and pin the exact number; do not assume.

### 6. RETIRE `group` from the FEATURE canvas (`D-2026-06-17-H`)
- D-H: its chunking role is now the **feature** level; folding a busy flow is a
  **view affordance, not a node kind**. `group` is in the viewer 17-set but **not**
  in the server `_ALL_KIND_CLASSES` 15-set (the live drift) — so its retirement is
  **viewer-side only** plus the gate.
- Remove: `viewer/src/domain/Group.ts`, `nodes/group/`, `inspectors/group/`,
  unions, `types.ts`, factory, barrel, both `KIND_DIRS` + the count (17 → down),
  i18n `kind.group.*`. **No server `_ALL_KIND_CLASSES` change** (absent already) —
  but remove `"group"` from `_ALLOWED_KINDS_BY_CANVAS["service_detail"]`
  (`models_canvas.py` line 60) and from `models_union.py` / `models_kinds.py` if a
  `GroupNode` discriminant exists there. **This is exactly the drift step 0
  flagged — reconcile here so both sides end consistent.**
- **Folding-as-view follow-up (out of scope, tracked):** the "fold a busy flow"
  affordance that replaces `group` is a **view** feature, not this plan — file in
  ROADMAP, do not build a node kind for it.
- **Tests:** viewer count drops; `NODE_RENDERERS` assertion updated; `decision`
  stays (kept). Re-run `test_schema_parity` — viewer and server kind lists must
  now be reconcilable (see Done-when).

### 7. Altitude guard — enforce action-level, no implementation logic (`D-2026-06-17-G`)
- D-G altitude line: the flow shows **user actions → branches → results**; it must
  **not** descend into storage/queries/rendering (the AI agent's job, outside Plot).
- This is primarily a **doc + framing** guard, not a schema field — there is no
  "implementation node" kind to ban (the retires above already removed `content`/
  `metric`). Encode the altitude rule in the per-canvas AI framing
  (`plot_mcp/chat_context.py` `_SCOPE_FRAMING` feature/execution entry): the
  framing instructs the AI to keep proposals at action altitude and defer
  implementation. SPEC.md line 131 is the framing SSOT.
- **Tests:** a server test asserting the feature/`service_detail` framing string
  carries the action-altitude instruction (pin the wording so a future edit can't
  silently drop it).
- **No "no service→service edge" rule here** — that belongs to the Services
  overview (`SERVICES_PLAN.md`, D-2026-06-17-D), not the feature canvas.

### 8. Doc-sync — CONCEPTS.md + SPEC.md feature-canvas slice
- **CONCEPTS.md:** add the `note` kind row (edgeless invariant, canvas-global,
  AI-framing injection); update the `rule` row to "per-feature operational
  constraint" wording (D-E); **delete** the rows for `mission_ref` / `value_ref` /
  `identity_ref` / `metric` / `content` / `group`. Bump the kind-count header to
  the reconciled number.
- **SPEC.md:** rename the Service-Detail canvas slice to the **FEATURE** canvas;
  state node inventory = `step` / `decision` / flow edges / `note` / `rule` /
  `actor_ref`; record the altitude guard (D-G) and the edgeless-note invariant
  (D-F). Cross-link the drill rewire to `SERVICES_PLAN.md` (the `feature` node is
  the drill target — owned there, referenced here).
- **Naming note (open, defer to SERVICES_PLAN.md):** whether the *canvas-kind*
  string `service_detail` is renamed to `feature` (server `CanvasKind` Literal,
  `models_canvas.py` line 31; viewer wrapper `ServiceDetailCanvas.tsx`; `App.tsx`
  selector ~line 438; `useUrlSync.ts` `?detail=` param) is a **canvas rename**, not
  a kind change — it is a product decision gated out of the entity skill. The
  drill-target repoint (service→feature) and any canvas-kind rename live in
  `SERVICES_PLAN.md`; **this file keeps the wire string `service_detail` until that
  plan renames it**, to avoid a half-renamed two-repo churn. Flag at hand-off.

## Out of scope (separate, already tracked)

- The **drill rewire** (selecting a service = inspector-only; clicking a `feature`
  node drills into this canvas), the **NEW `feature` kind**, and the **service
  5-field inspector rewrite** → [`SERVICES_PLAN.md`](./SERVICES_PLAN.md)
  (`D-2026-06-17-B/C/D`). This file is the drill *target* only.
- The **Entities** canvas + `entity` kind (`D-2026-06-17-I`) — discussion **not
  finished**, several OPEN questions; separate plan, populated last. Not here.
- The **fold-a-busy-flow view affordance** that replaces `group`'s chunking role
  (D-H) — a view feature → ROADMAP, not a node kind.
- **Cross-cutting policy** (a constraint spanning multiple features/services) —
  **PARKED** per `D-2026-06-17-E` (YAGNI; revisit on a concrete need). `rule` stays
  per-feature only.
- Canvas-kind string rename `service_detail`→`feature` + the App/url/wrapper
  repoint → `SERVICES_PLAN.md` (canvas rename, product-gated).

## Done when

The FEATURE canvas (renamed/repurposed Service-Detail) holds exactly
`step` / `decision` / flow edges / `note` / `rule` / `actor_ref`; `note` is a new
kind that is **edgeless** (rejected in both `handleConnect` and the `CanvasDoc`
validator), canvas-global, and injected into the per-canvas AI framing;
`mission_ref` / `value_ref` / `identity_ref` / `metric` / `content` / `group` are
retired in lock-step (each with its absent-dir guard); the kind-count drift across
`schema_export`/`test_schema_parity` (server) and `KIND_DIRS`/`NODE_RENDERERS`
(viewer, both SSOTs) is **reconciled to one agreed number**; the altitude guard is
pinned in the framing; CONCEPTS/SPEC feature-canvas slice is current. Every
retirement is loss-free for surviving data; schema parity + structural guards +
i18n parity + roundtrip + doc-sync green.
