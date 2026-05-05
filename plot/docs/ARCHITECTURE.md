# ARCHITECTURE — current shape + split plan

> **Purpose:** make the structural state of the Plot viewer explicit
> so the next architectural change isn't a guess. Pairs with
> [`SPEC.md`](./SPEC.md) (behaviour) and
> [`DECISIONS.md`](./DECISIONS.md) (history).
>
> **Scope today:** viewer (`plot/viewer/src/`). The MCP server
> (`plot/plot_mcp/`) already follows the noory-ai monorepo's Tool/Core
> separation and is not the bottleneck.

---

## Current shape

### File sizes

Measured 2026-05-05, post-v0.13.2:

| File | LOC | 500-line rule |
|---|---:|---|
| `viewer/src/canvases/SketchCanvas.tsx` | **1476** | Violated |
| `viewer/src/canvases/SketchInspector.tsx` | **1422** | Violated |
| `viewer/src/App.tsx` | **791** | Violated |
| `viewer/src/canvases/SketchStencil.tsx` | **523** | Violated |
| `viewer/src/canvases/SketchEdgeModal.tsx` | 255 | OK |
| `viewer/src/canvases/SketchNode.tsx` | 241 | OK |
| `viewer/src/canvases/SketchBodyModal.tsx` | 228 | OK |
| `viewer/src/canvases/SketchSidebar.tsx` | 212 | OK |
| `viewer/src/canvases/FoundationRefPicker.tsx` | 133 | OK |

Project rule (`noory-ai/CLAUDE.md`): *"Review for splitting when a
file exceeds 500 lines."* Four files violate; one of them (1476 lines)
is **3× the threshold**.

### `SketchCanvas.tsx` — responsibility inventory

The component carries 13+ distinct concerns in a single closure
scope. Each row below names a concern and the lines it lives on
(approximate, file is large and mutates):

| # | Concern | Anchor lines |
|---:|---|---|
| 1 | **Document → React Flow node transform** | `nodes` `useMemo` ~line 313–479 |
| 2 | **Document → React Flow edge transform** | `edges` `useMemo` ~line 481–517 |
| 3 | **Synthetic project anchor injection** | inside the `nodes` memo, ~line 436–465 |
| 4 | **Anchor drag/resize routing** | `handleNodesChange` ~line 521–577 |
| 5 | **Node click → Inspector + collapse + drill-down** | `inspectorNodeId` state + `onNodeClick` prop |
| 6 | **Three context menus** (pane / node / edge) | `menu` state + `openPaneMenu` / `openNodeMenu` / `openEdgeMenu` |
| 7 | **Keyboard shortcuts** (Cmd+Z / copy / paste / Delete) | `useEffect` ~line 939 |
| 8 | **Drag-and-drop creation** (stencil → canvas) | `handleDragOver` / `handleDrop` ~line 991–1175 |
| 9 | **Overlap nudging** (`slideOff`, `findFreeSpot`) | bottom of file |
| 10 | **Value-flow toggle** + edge re-colour | `valueFlowOn` state + `VALUE_FORM_COLORS` |
| 11 | **Collapsed-tree state** (`childIdsByParent`, `nearestCollapsedAncestor`, `subtreeSize`) | memos ~line 255–311 |
| 12 | **Orphan actor_ref detection + visual override** | `orphanActorRefIds` memo + node-fill override ~line 340 |
| 13 | **Service-Detail modal routing** | `onNodeDrill` prop + double-click handler |
| 14 | **Edge edit modal** | `edgeModalId` state + render block |
| 15 | **Body edit modal** | `bodyModalNodeId` state |
| 16 | **Foundation-ref picker** | `pendingActorRef` state + render block |

Side effects of the entanglement:

- A change to (8) drag-drop can mis-trigger (4) anchor drag because
  both feed `handleNodesChange`.
- (1) and (3) share the same memo, so anchor-injection bugs surface
  as node-render bugs.
- (10) value-flow recolour and (12) orphan visual override compete
  for the same `style` field.
- React Flow's d3-zoom event handling and (5)/(6)'s click handling
  interact through React Flow internals — today's "hover handles
  feel jittery" symptom likely lives in this seam.

### `SketchInspector.tsx` — responsibility inventory

1422 lines is too coarse to break down here in this first pass; the
high-level concerns are: header bar, MD-warning banner, label edit,
typed-field forms (per kind: actor / mission / core_value / identity /
service / actor_ref / mission_ref / value_ref / identity_ref / metric
/ step / rule / content), MD template editor with edit/split/preview,
delete, width toggle. **Per-kind form rendering is the bulk** — split
candidate is obvious (see below).

### `App.tsx` — responsibility inventory

App-level: routing (project / canvas), summary loading, project CRUD,
WebSocket plumbing, error toast, header, sidebar wrapper. 791 lines
is bloated mainly because routing + data loading + UI shell all live
together.

### `SketchStencil.tsx` — responsibility inventory

523 lines is bloated mainly because every kind's stencil entry is
hand-rolled in one file. Split candidate is obvious.

---

## Candidate split boundaries

Three candidates for `SketchCanvas.tsx`. Each has different trade-offs;
**user picks in plan mode in a subsequent session.** No code is moved
until the choice is approved and an entry is appended to
[`DECISIONS.md`](./DECISIONS.md).

### Candidate A — by responsibility (one file per concern)

```
canvases/sketch/
  SketchCanvas.tsx            // shell + ReactFlow root only (~150 LOC)
  useNodesMemo.ts             // (1) + (3) + (12) — node transform incl. anchor + orphan style
  useEdgesMemo.ts             // (2) + (10) — edge transform incl. value-flow recolour
  useAnchorSync.ts            // (4) — anchor drag/resize routing
  useCollapsedTree.ts         // (11)
  useContextMenus.ts          // (6) — pane/node/edge menus
  useKeyboardShortcuts.ts     // (7)
  useDragAndDrop.ts           // (8) + (9) — drop + overlap nudging
  useInspectorRouting.ts      // (5) + (13) — click → Inspector / drill-down
  modals/
    SketchEdgeModal.tsx       // (14, already its own file, just move)
    SketchBodyModal.tsx       // (15, already its own file, just move)
    FoundationRefPicker.tsx   // (16, already its own file, just move)
```

- **Pro:** clean SRP; each hook is single-purpose; unit-testable in
  isolation.
- **Con:** lots of small files; potential prop-drilling through the
  shell if hooks don't compose cleanly; React Flow's onNodeClick /
  onEdgeClick / onNodesChange need a single handler each, so the
  "split" is partly cosmetic — the shell still wires hook outputs to
  React Flow props.
- **Risk:** medium — many edits, each small. Easy to lose
  closure-shared state by accident (e.g. `docRef` ref shared between
  nodes-change + drop + keyboard).

### Candidate B — by domain layer (Clean Architecture)

```
canvases/sketch/
  ui/
    SketchCanvas.tsx          // React Flow shell + JSX
    SketchToolbar.tsx
  domain/
    nodeTransform.ts          // pure: doc.nodes -> rf nodes (no React)
    edgeTransform.ts          // pure: doc.edges -> rf edges (no React)
    overlapNudge.ts           // pure: collision math
    collapsedTree.ts          // pure: parent_id graph queries
  app/
    useSketchController.ts    // composes domain + UI; the only React-aware glue
```

- **Pro:** matches global CLAUDE.md "architecture: Clean Architecture,
  DDD"; pure domain functions are trivially unit-testable; UI thinness.
- **Con:** higher upfront cost; requires extracting state machines
  cleanly; React Flow's mutation-y APIs (drag mid-frame node updates)
  resist purity.
- **Risk:** high if rushed; low if done with discipline.

### Candidate C — minimal pragmatic split (just bring under 500 LOC)

```
canvases/
  SketchCanvas.tsx            // node/edge memos + ReactFlow JSX (~450 LOC)
  SketchCanvas.handlers.ts    // every useCallback handler (~400 LOC)
  SketchCanvas.dragdrop.ts    // drag/drop + overlap nudging (~300 LOC)
  SketchCanvas.menus.ts       // three context menus (~250 LOC)
```

- **Pro:** small move; under-500 mechanical fix; minimum behaviour-risk.
- **Con:** doesn't fix the underlying coupling — concerns still share
  closure scope through props passed back and forth.
- **Risk:** low.

### Candidate split for `SketchInspector.tsx`

Independent of which SketchCanvas option is picked:

```
canvases/inspector/
  SketchInspector.tsx               // shell + header + width toggle (~150 LOC)
  fields/
    LabelField.tsx
    MissionFields.tsx
    CoreValueFields.tsx
    IdentityFields.tsx
    ActorFields.tsx
    ServiceFields.tsx
    RefFields.tsx                   // actor_ref / mission_ref / value_ref / identity_ref
    MetricFields.tsx
    StepFields.tsx
    RuleFields.tsx
    ContentFields.tsx
  MdTemplateEditor.tsx              // foundation MD edit/split/preview pane
```

- Per-kind field components are independent of each other and of the
  Inspector shell; this split has near-zero risk.

---

## Risk register

| Risk | Mitigation |
|---|---|
| Splitting breaks React Flow's d3-zoom / drag handling | Keep the React Flow root mount in one file; only extract pure transforms and event-emit hooks. Verify drag + click after every move via the browser, not only via tests. |
| `docRef` and other refs shared across handlers lose freshness | Pass the ref into each extracted hook explicitly; do not rebuild new refs. |
| Undo/redo (`useSketchHistory` upstream) breaks because state-shape changes | Keep `doc` shape unchanged; only re-organise where mutations are dispatched. |
| Anchor sync regresses (anchor drag stops persisting) | Keep `handleNodesChange` as a single React Flow handler; it can dispatch internally to extracted hooks. |
| Tests miss the regressions because the existing two smoke tests are broken | Fix the two pre-existing smoke-test failures (localStorage in JSDOM + missing `useSketchHistory` import) **before** starting any split. |

---

## Migration order (when the split happens)

In strict dependency order — never do step N before N-1 is green:

1. **Fix the broken smoke tests** so we have a baseline. (Pre-existing
   localStorage / import failures.)
2. **Add a "render Foundation with N children + auto-edges = 0"
   regression test.** Today's session would have flagged the
   auto-edge addition immediately.
3. **Split `SketchInspector.tsx` per-kind first** (lowest risk; wins
   under-500 quickly; no React Flow interaction).
4. **Split `SketchStencil.tsx`** (also low risk).
5. **Pick a SketchCanvas candidate** (A / B / C) — that is the
   step requiring plan mode + user approval.
6. **Execute SketchCanvas split** in small commits, one extracted
   hook per commit, browser-verified each time.
7. **Touch `App.tsx` last** — it ties everything together.

---

## What this file is NOT

- Not behaviour spec — that's [`SPEC.md`](./SPEC.md).
- Not a decision — the split-boundary choice happens in plan mode in
  a later session and is recorded in [`DECISIONS.md`](./DECISIONS.md)
  as `D-YYYY-MM-DD-X` once approved.
- Not a refactor PR — no code is moved by this file's existence.
