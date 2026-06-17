# ENTITIES_PLAN — implementing the 2026-06-17 Entities canvas design

> **Status: PLAN (2026-06-17) — DESIGN COMPLETE, NOT YET BUILT.** Build queue for
> the new project-level **Entities** canvas + new `entity` kind, from the
> big-picture review (`D-2026-06-17-I` in [DECISIONS.md](./DECISIONS.md); rows
> 13–20 of [BIG_PICTURE_REVIEW.md](./BIG_PICTURE_REVIEW.md)). **The entity
> discussion is finished** — all five design questions (§B) are resolved
> (`D-2026-06-17-J` + `D-2026-06-17-K`). This file records what is SETTLED (§A +
> §B), then gives the lock-step build order (§C). **Code is currently
> UNCHANGED.** TDD per CLAUDE.md Gate 1.5.

## A. Settled design (`D-2026-06-17-I`)

The frame is pinned (§B is now fully resolved — see below). Settled:

- **New project-level "Entities" canvas**, a 4th singleton sibling of
  `foundation` / `actors` / `services` (NOT parametric like `service_detail`).
  Holds product data objects (글 / 댓글 / 사용자), project-wide managed.
- **Symmetric to Actors** — Actors = *who* acts, Entities = *what* is acted on.
  New kind `entity`.
- **AI-maintained, NOT user-authored.** The AI surfaces entities as a byproduct
  of designing features / services, auto-registers them; the user
  reviews / refines / confirms (NOT silent — `D-2026-06-16-P`). Bottom-up
  creation (during feature work) + top-down management (project registry).
- **Populated last** — a derived surface, the deepest downstream of the design
  flow, not a starting canvas.
- **FORM = conceptual entity map**, not a physical ERD. Entities + rough
  relationships (e.g. 사용자 —쓴다→ 글 —달린다→ 댓글). Pre-normalisation
  abstract entities. **NO** normalisation, FK, cardinality, or field types —
  those are the external AI agent's job, below Plot's altitude. **Plot holds
  `name` + one-line "무엇을 담나" only.**
- **Feature actions reference entities** ("발행 → 글 생성"). The reference flows
  from a feature-canvas action node toward an `entity`.

These items have enough definition to land the canvas shell and the `entity`
kind without inventing anything (§C steps 1–6). The §B answers (now all pinned)
govern the inspector content, dedup, back-reference, and AI-surfacing behaviour.

## B. Design questions — ✅ ALL RESOLVED (D-2026-06-17-J + D-2026-06-17-K)

> **Resolved 2026-06-17.** B1 → `D-2026-06-17-J` (edges governed by definition, AI
> may draw entity relationship edges). B2–B5 → `D-2026-06-17-K`: **B2** dedup = fully
> smart / first-class (strong semantic match; only ambiguous cases ask the user;
> never silent-merge or -duplicate — AI-playbook duty). **B3** back-reference =
> shown, read-only (where the entity is used). **B4** AI-surfacing = in-chat
> proposal during feature design (not auto-scan). **B5** inspector = 이름 + "무엇을
> 담나?" (rough fields, no types/FK) + 어디서 쓰이나 (B3) + 거친 관계. The per-item
> notes below are kept as the original tension log; the answers above govern.

`D-2026-06-17-I` originally left B2–B5 open; `D-2026-06-17-K` (B1 → `D-2026-06-17-J`)
closed them all on 2026-06-17. The per-item notes below keep the original tension
log; the **Resolved** answers govern.

### B1. Relationship-edge ownership — ✅ RESOLVED (D-2026-06-17-J)
- **Resolved 2026-06-17:** the former "all edges user-drawn / never auto-emit"
  rule (`D-2026-05-04-A`) was **removed** by `D-2026-06-17-J`. Edges are now
  governed by their **definition** (`relation` + payload), **not authorship**, and
  the AI **may propose / draw edges on AI-maintained canvases** — exactly this one.
  So **AI-proposed entity relationship edges (사용자 —쓴다→ 글) are allowed**; the
  user can edit / delete any of them.
- **Remaining (small, not blocking):** give the `entities` canvas a branch in
  `edge_semantics.py::classify_edge` + `viewer/src/flow/edgeSemantics.ts::classifyEdge`
  to assign a default `relation` for entity edges; never emit a *meaningless* or
  *silently-uneditable* line (the one harm still banned, D-J). §C step 7 is
  **unblocked.**

### B2. Duplicate recognition strength — ✅ RESOLVED (D-2026-06-17-K)
- **Tension:** the AI should not split 글 / 게시물 / 포스트 into three entities
  for the same concept, but Plot stores only `name` + one-line text — there is
  no schema-level identity key to dedupe on. Too-weak recognition fragments the
  registry; too-strong silently merges genuinely distinct entities.
- **Resolved 2026-06-17:** dedup is **fully smart / first-class.** Before creating
  an entity the AI must **strongly semantic-match** the candidate against the
  existing registry (글 = 게시물 = 포스트 → **one** entity, never duplicated). Only
  genuinely ambiguous cases ask the user ("이거 기존 '글'과 같은가요?"). **Never
  silent-merge, never silent-duplicate.** This is a **1급 duty of the AI chat
  playbook** (ROADMAP 5.10) — not an in-engine guard.
- **Step 8** is unblocked; the merge behaviour lives in the playbook, not in
  engine code.

### B3. Back-reference (entity → which features use it) — ✅ RESOLVED (D-2026-06-17-K)
- **Tension:** a project registry is more useful if selecting an entity shows
  which features reference it — but feature→entity references live in the
  feature canvas, and Plot has no cross-canvas back-index today
  (`useAvailableNodes.ts` reads other canvases forward, not a reverse map).
- **Resolved 2026-06-17:** back-references **are shown, read-only.** Selecting an
  entity shows which features/actions reference it (글 → "글쓰기 · 글편집 ·
  글보기에서 쓰임"). **Derived** (not stored), read-only — core to project-wide
  management.
- **Remaining (implementation wiring, not a design question):** Plot has no
  cross-canvas reverse index today (`useAvailableNodes.ts` reads forward only) —
  the derived back-ref map still needs to be built when step 6's inspector content
  lands.

### B4. AI-surfacing UX (how / when the AI proposes an entity) — ✅ RESOLVED (D-2026-06-17-K)
- **Tension:** the settled design says "AI surfaces entities as a byproduct of
  feature work" — but **Plot has no engine event that fires on a feature
  action.** The only existing seam is the external agent choosing to call MCP
  `update_canvas` after reading selection via `get_viewer_context`. There is no
  push / trigger.
- **Resolved 2026-06-17:** AI-surfacing = **in-chat proposal, not auto-scan.**
  During feature-design chat, when an action handles a "thing," the AI proposes
  the entity ("이건 '글' 엔티티네요 — 등록할까요?") → user confirms → it registers on
  the Entities canvas. **No silent background scan.** Part of the AI chat playbook.
- **Remaining (implementation wiring, not a design question):** there is no engine
  event on a feature action — the in-chat proposal is **agent-initiated** through
  the existing `get_viewer_context` → `update_canvas` seam (the framing string in
  §C step 8), with no push/trigger and no review-queue UI to build.

### B5. Entity inspector content (when an entity is selected) — ✅ RESOLVED (D-2026-06-17-K)
- **Tension:** settled storage is just `name` + one-line "무엇을 담나". The
  inspector must render *something* when selected, and the fuller field set
  depended on B1/B3/B4 being answered.
- **Resolved 2026-06-17:** the entity inspector = **lean, conceptual** — 이름 +
  **"무엇을 담나?"** (one line, rough fields 제목·본문·작성자 — no types/FK) +
  **어디서 쓰이나** (B3 back-ref, read-only) + **거친 관계** (rough relationships to
  other entities). The two writable fields are `name` + the "무엇을 담나" line; the
  back-ref list (B3) and rough-relationship view are read-only.

## C. Build order (smallest-first) — what IS settled

Lands in lock-step per CLAUDE.md Gate 1.5 (Red→Green→Refactor) via the
[`plot-entity-template`](../skills/plot-entity-template/SKILL.md) skill. The
canvas (steps 1–2) and the kind (steps 3–5) are the easy structural class — a
new **singleton** canvas + a new discriminated-union kind. The §B-derived parts
(inspector views in step 6, edges in step 7, AI-surfacing in step 8) are now all
resolved by `D-2026-06-17-J` + `D-2026-06-17-K`; only implementation wiring
remains.

> **PRE-FLIGHT — reconcile the kind-count drift first.** The guards disagree
> today: `plot_mcp/schema_export.py::_ALL_KIND_CLASSES` +
> `tests/test_schema_parity.py::test_all_kinds_covered` count **15**, while
> `viewer/tests/structural-guards.test.tsx` `KIND_DIRS` + `NODE_RENDERERS` count
> **17** (they add `decision` + `group`). Adding `entity` must satisfy **both**
> numbers, so the count bumps must land deliberately on each side. **Do not add
> `entity` on top of a silent disagreement** — name the reconciliation in the
> step-3 test work (the `entity` kind itself only legitimately raises one count
> per side; the pre-existing 15-vs-17 gap is flagged, not silently absorbed).
> This drift is also entangled with the FEATURE-canvas retirements
> (`mission_ref` / `value_ref` / `identity_ref` / `metric` / `content` / `group`
> per `D-2026-06-17-E/G/H`) — see Out of scope; sequence with that work so the
> counts move once, not twice.

### 1. Register the `entities` canvas — server side (`D-2026-06-17-I`)
Every site that enumerates `CanvasKind`. A miss here is **silent** (there is no
"every CanvasKind appears at every site" guard except scope parity):
- `plot_mcp/models_canvas.py` line 31 — `CanvasKind` Literal SSOT: add
  `"entities"`. Update the module docstring (lines 8–16) to name a 5th canvas.
- `plot_mcp/models_canvas.py` lines 38–64 — add `"entities": {"project",
  "entity"}` to `_ALLOWED_KINDS_BY_CANVAS` (anchor + the new kind). Add `entity`
  to other canvases ONLY if they carry entity refs — **blocked-on-open** until
  the feature-action→entity reference is designed (Out of scope: FEATURE canvas).
- `plot_mcp/models_canvas.py` lines 247–252 — `_default_anchors()`: seed the
  `entities` anchor (else no anchor renders).
- `plot_mcp/models_canvas.py` lines 81–222 — add an `_entities_canvas_rules`
  `@model_validator` **only if** entities needs a structural invariant; `services`
  has none post-v0.26, so default to **no validator** (YAGNI) unless a settled
  rule demands one.
- `plot_mcp/endpoints_common.py` lines 19–20 — add `"entities"` to
  `_ALLOWED_CANVAS_KINDS` (the HTTP gate; `_parse_canvas_kind` reads it).
- `plot_mcp/canvas_io.py` line 69 — add `entities` to the anchor-bearing tuple in
  `read_canvas()` (legacy-anchor eviction).
- `plot_mcp/broadcast.py` line 13 — add `"entities"` to `_SINGLETON_CANVAS_KINDS`
  (else `entities/canvas.json` writes never push `project_changed` over WS).
- `plot_mcp/endpoints_projects.py` line 182 — add `"entities"` to the
  `{"foundation","actors","services"}` guard.
- `plot_mcp/endpoints_tags.py` lines 110–112, 152 — add `"entities"` to the
  snapshot/tag singleton map.
- `plot_mcp/node_publish.py` line 68 — add `"entities"` to `fixed_kinds` **only
  if** entity nodes are publishable (decide; default: include for parity).
- `plot_mcp/project_io.py` lines 64–200 — add `_seed_entities_canvas` + a write
  in `create_project`. **Seed EMPTY** (like services) — settled: entities are
  populated last / AI-derived, never hand-authored at create time.
- `.noory/` storage — `storage.py:_canvas_file()` maps singletons to
  `{kind}/canvas.json` automatically → `entities/canvas.json` works with **no
  change**. v0.1 migrators (`migrate_*.py`): **no change** — lazy-seed on read
  (YAGNI; old projects back-fill `entities` on first read).
- `plot_mcp/mcp_tools.py` — `get_canvas`/`update_canvas` accept
  `canvas_kind: CanvasKind`, so they pick up `entities` for free. **But fix the
  stale docstrings** (lines 55, 127–140) + the MCP server `instructions` string
  (search `"services_overview"`) — they still say `core / services_overview` and
  will mislead the agent about the canvas inventory.
- Tests: `update_canvas` accepts an `entities` doc; `_ALLOWED_KINDS_BY_CANVAS`
  rejects a non-`entity`/`project` node on `entities`; `_default_anchors` seeds
  the anchor; a write to `entities/canvas.json` broadcasts `project_changed`.

### 2. Register the `entities` canvas — viewer side (`D-2026-06-17-I`)
- `viewer/src/types.ts` line 112 — TS `CanvasKind` SSOT: add `"entities"`.
- `viewer/src/types.ts` lines 126–131 — `ChatScope` union: add `"entities"`.
- `viewer/src/types.ts` lines 147–151 — `CanvasKey` cache-key union: add
  `"entities"`.
- `viewer/src/shell/CanvasTabs.tsx` lines 18, 21–23 — extend `CanvasTab` +
  the tab-order array. **A 4th tab is a visual-hierarchy decision** (CLAUDE.md
  ux: 1 화면 = 1 Primary CTA) — confirm tab placement/order with the user as the
  one product judgement in this step.
- `viewer/src/App.tsx` lines 37–40 — `tabToKind()` switch: add `entities`.
- `viewer/src/App.tsx` lines 464–469 — render switch: add the `EntitiesCanvas`
  branch. (`activeScope` at line 393 derives from `tabToKind` → free.)
- `viewer/src/hooks/useUrlSync.ts` lines 5, 45, 94–153 — add the
  `?canvas=entities` parse/sync branch.
- `viewer/src/canvases/EntitiesCanvas.tsx` — **NEW** props-only thin wrapper
  (≤150 LOC, mirror `ServicesCanvas.tsx`; behaviour banned here per Gate 2).
  Declare `anchorArrowMode` (per-canvas semantic choice, SPEC line 328 — not a
  default) and `enableAutoLayout` (auto-layout is Foundation-only today;
  default **off** unless a settled layout rule says otherwise).
- `viewer/src/canvases/SketchStencil.tsx` lines 256, 289–352, 388–395 — add the
  `entity` stencil preset + the `entities`-canvas palette case.
- `viewer/src/canvases/inspectors`/`nodes` registries pick up `entity` via the
  directory convention (step 5).
- `viewer/src/lib/canvasKey.ts` — singletons key by kind verbatim → **no
  change**.
- Tests: `test_chat_scope_parity.py` lines 39–42 — add `"entities"` to
  `_EXPECTED_SCOPES` (this cross-repo wire guard **fails the moment** one side
  has `entities` and the other doesn't — land both halves together);
  `structural-guards.test.tsx` lines 92–96 + LOC budgets 168–171 — add
  `EntitiesCanvas` (ceiling 150).

### 3. Add the `entity` kind — server side (`D-2026-06-17-I`)
- New Pydantic model (`plot_mcp/models_kinds.py` or a new `models_entity.py`,
  file <500 LOC): `EntityNode(BaseNodeFields)`, `kind: Literal["entity"]`.
  **Fields = the two settled ones only:** `label` (= `name`) + a one-line typed
  text for "무엇을 담나". **Do NOT add ERD fields** (FK / cardinality / field
  types are below altitude — settled). No relationship fields on the node
  (relationships are edges, gated by B1).
- `plot_mcp/models_union.py` lines 47–90 — add `EntityNode` to the
  `SketchNode = Annotated[Union[…], discriminator="kind"]` + `SketchNodeAdapter`.
- `plot_mcp/models.py` lines 35–128 — re-export `EntityNode`.
- `plot_mcp/schema_export.py` lines 76–92 — add `"entity": EntityNode` to
  `_ALL_KIND_CLASSES` (SSOT for parity + `get_node_schema`).
- Tests: `tests/test_schema_parity.py` auto-iterates → bump
  `test_all_kinds_covered`'s count for the real `entity` add, and **reconcile
  the 15-vs-17 drift here** (pre-flight). `entity` Pydantic field-set ≡ TS
  `EntityJson` field-set.

### 4. Add the `entity` kind — viewer domain class (`D-2026-06-17-I`)
- `viewer/src/domain/Entity.ts` — **NEW** class: `EntityJson extends
  BaseFieldsJson`, `Entity` with private ctor, `static fromJson` (**invariants
  throw `DomainParseError` HERE — the JSON↔domain boundary**), `toJson`, and a
  trailing `registerKindParser("entity", Entity.fromJson)`. Two settled fields
  only.
- `viewer/src/domain/SketchNode.ts` — extend both unions (`SketchNode` +
  `SketchNodeJson`), alphabetical.
- `viewer/src/domain/createBlankNode.ts` — add `case "entity":` (defaults +
  palette colour; cross-check `canvases/sketch/palette.ts`).
- `viewer/src/domain/index.ts` — barrel-export `Entity` + `EntityJson`
  (alphabetical) so the side-effect `registerKindParser` runs on load.
- Tests: `viewer/tests/entity-roundtrip.test.tsx` — add an `entity` case
  (`fromJson(json).toJson() === json`); `no-god-import.test.tsx` —
  per-kind file exists + `EntityJson` exported + `registerKindParser` called.

### 5. Add the `entity` kind — per-kind UI (`D-2026-06-17-I`)
- `viewer/src/canvases/nodes/entity/index.tsx` — **NEW** renderer wrapping
  `BaseNode` (LOC ceiling 100). Render shape per SPEC entity section.
- `viewer/src/canvases/inspectors/entity/index.tsx` — **NEW** inspector in
  `BaseInspector`'s slot (LOC ceiling 250). Per `D-2026-06-17-K` (B5) the
  inspector is **lean, conceptual**: 이름 + **"무엇을 담나?"** (one line, rough
  fields — no types/FK) — both **writable** — plus **어디서 쓰이나** (B3 back-ref,
  read-only) + **거친 관계** (rough relationships, read-only). The two writable
  fields land in step 5; the read-only back-ref + rough-relationship views wire
  in step 6.
- Registries — `canvases/nodes/registry.ts` + `inspectors/registry.ts`
  auto-pick the directory-convention files; verify via vitest
  `-t "NODE_RENDERERS includes entity"`.
- `viewer/src/i18n/locales/{en,ko}.json` — both locales: `kind.entity.label`,
  `kind.entity.description`, `inspector.entity.field.{name,summary}` + `.hint`,
  and `canvas.tabs.entities`. Guarded by `i18n-keys-parity.test.tsx`.
- Tests: `structural-guards.test.tsx` — add `entity` to `KIND_DIRS` + the count
  assertion; add it to `styles-cursor-baseline.test.tsx`'s `KIND_DIRS` (dual
  SSOT — must move in tandem).

### 6. Entity inspector — back-reference + rough-relationship views (B5, B3 resolved, D-2026-06-17-K)
- Built in step 5: `name` + one-line "무엇을 담나", both editable.
- This step adds the two **read-only** views pinned by `D-2026-06-17-K`:
  **어디서 쓰이나** (B3 back-ref — which features/actions reference the entity, e.g.
  글 → "글쓰기 · 글편집 · 글보기에서 쓰임") and **거친 관계** (rough relationships to
  other entities). Both are derived/read-only, not user-authored fields.
- **Remaining (implementation wiring, not a design question):** the B3 back-ref is
  **derived** but Plot has no cross-canvas reverse index today
  (`useAvailableNodes.ts` reads forward only) — the reverse-lookup map must be
  built here.

### 7. Entity relationship edges — unblocked (B1 resolved, D-2026-06-17-J)
- AI **may propose / draw** entity relationship edges (사용자 —쓴다→ 글); the user
  can edit / delete any. The blanket "user-drawn only" rule is gone (D-J).
- Add an `entities` branch to `edge_semantics.py::classify_edge` +
  `viewer/src/flow/edgeSemantics.ts::classifyEdge` to assign a default `relation`
  for entity edges. Keep edges **conceptual** (rough relationship — no
  normalisation / FK / cardinality, per the `D-2026-06-17-I` altitude guard).
  Never emit a *meaningless* or *silently-uneditable* line (D-J).

### 8. AI-surfacing hooks — settled (B2, B4 resolved, D-2026-06-17-K)
Buildable now:
- `plot_mcp/chat_context.py` `SCOPE_FRAMING` dict (lines 27–48) — **add an
  `"entities":` framing string.** This is the SSOT consumed by both delivery
  layers (HTTP chat + MCP `get_viewer_context`). For an AI-maintained canvas,
  this string instructs the agent how to surface/maintain entities (conceptual
  map, pre-normalisation, `name` + one-line only, not below altitude). A missing
  key is silent (empty framing) — so this is required, not optional.
- `plot_mcp/chat_providers/base.py` lines 34–49 — add `"entities"` to the
  `ChatScope` Literal + `_SINGLETON_SCOPES` (`is_valid_scope` gates wire scopes).
- Layer-2 selection preamble (`chat_context.py` lines 63–94) is kind-agnostic —
  an `entity` selection flows through with **no change**.
- The existing mutation seam carries an AI-proposed entity for free: the agent
  reads selection via MCP `get_viewer_context` → calls MCP `update_canvas` on the
  `entities` canvas with new `entity` nodes → `broadcast.py` pushes
  `project_changed`. **No new endpoint** needed.
- Tests: `SCOPE_FRAMING["entities"]` is non-empty; `is_valid_scope("entities")`
  is true; `test_chat_scope_parity.py` green.

Behaviour pinned by `D-2026-06-17-K`, lives in the AI chat playbook (ROADMAP 5.10),
not in engine code:
- **B4 — surfacing = in-chat proposal, not auto-scan.** During feature-design chat
  the AI proposes the entity ("이건 '글' 엔티티네요 — 등록할까요?") → user confirms →
  it registers. **No silent background scan.**
- **B2 — dedup = fully smart / first-class.** The AI strongly semantic-matches a
  candidate against the registry (글 = 게시물 = 포스트 → one entity); only ambiguous
  cases ask the user; never silent-merge / -duplicate.

**Remaining (implementation wiring, not a design question):** Plot has **no engine
event on a "feature action"** — so surfacing is **agent-initiated only** through the
framing string above (`get_viewer_context` → `update_canvas`), with no in-engine
prompt and no review-queue UI. The dedup match is a playbook duty, so there is no
in-engine dedupe guard to build.

## Out of scope (separate, already tracked)

- **FEATURE canvas** (the renamed/repurposed `service_detail`) + feature
  action→entity *reference* wiring — `D-2026-06-17-E/G/H`; its own plan. The
  `entities` allowed-kinds entry for refs (step 1) waits on that.
- **Services-overview rewire** (`feature` node, drill change, service inspector
  5 fields, dropped service fields) — `D-2026-06-17-B/C/D`; separate plan.
- **FEATURE-canvas kind retirements** (`mission_ref` / `value_ref` /
  `identity_ref` / `metric` / `content` / `group`) — `D-2026-06-17-G/H`; their
  count moves entangle with the kind-count reconciliation (pre-flight). Sequence
  so the guard counts move once.
- **Cross-cutting policy** (spans features/services) — PARKED per
  `D-2026-06-17-H`; revisit on concrete need.
- CONCEPTS.md / SPEC.md full refresh for the new canvas inventory — doc-sync
  lands with this work's Gate-4, but the wider multi-canvas CONCEPTS rewrite is
  the broader doc task.

## Done when

The `entities` tab renders a singleton canvas with a project anchor; the
`entity` kind round-trips (`fromJson ∘ toJson` identity) and carries only the two
settled fields; `SCOPE_FRAMING["entities"]` frames the agent; the agent can
surface entities via `update_canvas` and the viewer receives `project_changed`;
the kind-count drift is reconciled so **both** `_ALL_KIND_CLASSES`/parity and
`KIND_DIRS`/`NODE_RENDERERS` agree; and the five §B questions (all resolved by
`D-2026-06-17-J` + `D-2026-06-17-K`) are wired per their pinned answers — entity
inspector back-ref/rough-relationship views (step 6), entity relationship edges
(step 7), and in-chat AI-surfacing (step 8). Migration loss-free (lazy-seed, no
old-project data touched) +
schema parity + chat-scope parity + structural guards + i18n parity + doc-sync
green.
