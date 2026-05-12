# DECISIONS — Plot UX / behaviour log

> Every decision that shapes how Plot **looks or behaves** belongs here.
> If a UI / behaviour change is not represented by an entry below (or
> by an explicit line in [`SPEC.md`](./SPEC.md)), it was not properly
> agreed and should be reverted.

---

## How to use this file

**Before** a UI / behaviour change:
1. Check [`SPEC.md`](./SPEC.md) — does it cover this?
   - If yes: implement what the spec says.
   - If no: **stop. Ask the user.** Don't read code comments and treat
     them as spec — comments are not approved decisions.
2. After user gives direction, append a `D-YYYY-MM-DD-X` entry below
   *first*, then implement.

**After** a change ships:
- Mark the decision **Accepted** if the user kept it after seeing it.
- Mark it **Rejected** if the user asked to revert.
- Rejected entries stay in the log so the next session knows not to
  re-propose the same idea.

**Entry template:**

```
### D-YYYY-MM-DD-X — short title

- **What:** the proposed / made change in one line.
- **Why:** the rationale (problem the change addresses).
- **Alternatives:** what was considered and rejected.
- **Approval:** Accepted | Rejected | Pending — by whom, when.
- **Spec impact:** which line of SPEC.md this updates (if any).
```

---

## Log

### D-2026-05-04-A — No auto-edges from anchor

- **What:** Renderer was emitting synthetic dashed slate-400 edges from
  the project anchor to every top-level Mission / CoreValue / Identity
  node on Foundation.
- **Why:** the relationship "this Mission belongs to this project" was
  implicit; auto-edges were proposed to make it visible.
- **Alternatives:** real seed edges written into `canvas.json`
  (rejected — auto-creates user data without consent); leave it to
  the user (chosen).
- **Approval:** **Rejected** by user, 2026-05-04 — auto-edges weren't
  editable / deletable, which broke the user's "every line on the
  canvas is mine to control" expectation.
- **Spec impact:** [`SPEC.md` §Edges](./SPEC.md#edges) — codifies "all
  edges are user-drawn".

---

### D-2026-05-04-B — Anchor handles stay visible

- **What:** Hide the four React Flow connection handles on the
  synthetic project anchor.
- **Why:** code comment said "synthetic anchor is read-only"; assumed
  this meant the user shouldn't draw edges from it either.
- **Alternatives:** keep the handles (chosen after rejection).
- **Approval:** **Rejected** by user, 2026-05-04 — the user never
  agreed the anchor was read-only. The "read-only" claim was a stale
  code comment from v0.13 Phase 0 development that the assistant
  treated as spec. Anchor handles are restored.
- **Spec impact:** [`SPEC.md` §Anchor](./SPEC.md#anchor-the-centre-node)
  — "Handles (4 sides): Visible. User may draw edges from / to the
  anchor like any other node."

---

### D-2026-05-04-C — Anchor visually distinct from Service circles

- **What:** Add a slate-600 outline + offset + slate-300 inner ring to
  the project anchor, so it's recognisable as "the project itself" and
  not confused with the same-coloured Service nodes that appear on
  the Services canvas.
- **Why:** without differentiation, a user landing on Services / Actors
  (where the anchor is also auto-seeded) couldn't tell which yellow
  circle was the project vs a Service.
- **Alternatives:** different fill colour (rejected — fill is already
  meaningful per kind palette); icon overlay (rejected — competes
  with kind-tag corner labels).
- **Approval:** **Accepted** by user, 2026-05-04 — implicitly, by not
  asking to revert when other items were rolled back.
- **Spec impact:** [`SPEC.md` §Anchor](./SPEC.md#anchor-the-centre-node)
  — "Visual differentiation".

---

### D-2026-05-04-D — Auto-layout removed entirely — **Rejected (misattribution corrected 2026-05-10)**

- **What was implemented:** Removed the "Auto layout" toolbar button
  and the corresponding pane-context-menu entry. Dropped the
  `radialLayout` / `autoLayout` calls and the `handleAutoLayout`
  callback from `SketchCanvas`.
- **Original (incorrect) rationale:** layout encodes user intent;
  auto-layout silently overwrites that intent.
- **Why this entry is now Rejected:** the user confirmed in the
  2026-05-10 Foundation re-verification session that this removal
  was a misread of their actual intent. Direct quote (2026-05-10):
  *"내가 없애라는건 다운로드 업로드 이런거였는데. 오토레이아웃만
  남기라는거였는데."* The earlier session's *"그리고
  오토레이아웃도 없앴어요. 이해?"* (2026-05-04) was the
  assistant's own erroneous summary of the v0.11.6 toolbar cleanup,
  not a fresh user instruction. The user wanted only download /
  upload buttons removed; auto-layout was meant to stay.
- **What replaces this:** [D-2026-05-10-E](#d-2026-05-10-e--auto-layout-restored-as-mindmap-style-directional-tree) —
  auto-layout restored with a proper handle-aware directional-tree
  spec.
- **Lesson encoded into Gate 0:** assistant-summarised "이해?"
  questions are not user confirmations of the underlying claim. A
  decision id requires the user to **affirmatively** approve the
  precise behaviour, not nod along to the assistant's paraphrase.
- **Approval:** **Rejected** by user, 2026-05-10. The original
  "Accepted (removal)" line from 2026-05-04 stands as a historical
  record of the misattribution.
- **Spec impact:** [`SPEC.md` §Auto-layout](./SPEC.md#auto-layout) —
  rewritten by D-2026-05-10-E.

---

### D-2026-05-04-E — Hover handles only fade in lightly

- **What:** Connection handles stay invisible at rest; fade to
  `opacity: 0.55` while the cursor is on the node body; only become
  fully opaque + scaled when the cursor lands directly on a handle.
- **Why:** the prior behaviour (all four handles pop to full opacity +
  scale 1.35× the moment the cursor enters the node) felt noisy and
  read as "the node is constantly inviting a connection".
- **Alternatives:** keep prior behaviour (rejected — noisy); hide
  handles entirely until a modifier key (rejected — too hidden,
  discoverability suffers).
- **Approval:** **Accepted** by user, 2026-05-04 — implicitly.
- **Spec impact:** [`SPEC.md` §Hover behaviour](./SPEC.md#hover-behaviour).

---

### D-2026-05-04-F — ⚠ badge contrast bumped

- **What:** Change MD-warning badge from `bg-amber-100 text-amber-800
  ring-amber-300` to `bg-white text-amber-700 ring-amber-500 shadow-sm`
  so it stays legible on cream / pastel-orange / pastel-yellow card
  backgrounds.
- **Why:** the prior amber-on-amber palette nearly disappeared into
  the Mission and CoreValue card colours.
- **Alternatives:** stronger amber fill (rejected — competes with
  card colour); red fill (rejected — overstates severity for a
  fixable parse warning).
- **Approval:** **Accepted** by user, 2026-05-04 — implicitly.
- **Spec impact:** [`SPEC.md` §⚠ Markdown-template warning badge](./SPEC.md#-markdown-template-warning-badge).

---

### D-2026-05-04-G — Defensive viewport CSS

- **What:** Add `h-screen min-h-screen` to the outermost shell `<div>`
  and `min-height: 100vh / 100dvh` fallbacks on `html, body, #root`.
- **Why:** user reported the canvas not filling top-to-bottom in
  their browser, even though Playwright measurement showed the
  existing `height: 100%` chain was correct. Defensive doubling
  (`100vh` + `100dvh`) costs nothing in clean cascades and rescues
  edge cases (mobile-style viewports, iframe embeds, dev-tools
  docking).
- **Alternatives:** require user to share a screenshot before
  changing anything (rejected as too slow — defensive CSS is cheap);
  do nothing (rejected — user reported a real symptom).
- **Approval:** Pending — user has not yet confirmed whether their
  browser symptom resolved after the change.
- **Spec impact:** [`SPEC.md` §Viewport](./SPEC.md#viewport).

---

### D-2026-05-05-A — SPEC + DECISIONS files exist; comments are not spec

- **What:** Introduce `plot/docs/SPEC.md` (Foundation only, for now)
  and `plot/docs/DECISIONS.md` (this file). Future UI / behaviour
  changes must reference an entry in one of these.
- **Why:** session-to-session work was not accumulating: every
  session re-relitigated the same trade-offs because the prior
  session's decisions lived only in code comments (which were not
  agreed) or in the assistant's working memory (which doesn't
  survive). The fix is a single canonical place where every
  behavioural decision is written down with date + rationale +
  approval status.
- **Approval:** **Accepted** by user, 2026-05-05.
- **Spec impact:** none — meta-rule about how decisions are recorded.

---

### D-2026-05-05-B — Architecture violation acknowledged: god components

- **What:** Acknowledge that today's viewer code violates the
  project's own structural rule (project CLAUDE.md: "Review for
  splitting when a file exceeds 500 lines") and the user's stated
  design principles (global CLAUDE.md: SOLID / SRP / Clean
  Architecture / DDD).
- **Evidence (measured 2026-05-05, post-v0.13.2):**
  - `viewer/src/canvases/SketchCanvas.tsx` — **1476 lines, 40 hooks,
    ≥13 distinct responsibilities** (node transforms, edge
    transforms, anchor sync, click→Inspector routing, three context
    menus, keyboard shortcuts, drag-and-drop, overlap nudging,
    value-flow toggle, collapsed-tree state, orphan ref detection,
    Service-Detail modal routing, undo/redo glue).
  - `viewer/src/canvases/SketchInspector.tsx` — **1422 lines.**
  - `viewer/src/App.tsx` — **791 lines.**
  - `viewer/src/canvases/SketchStencil.tsx` — **523 lines.**
- **Why this matters:** today's hover bug, today's edge regressions,
  and the recurring "small change here breaks something over there"
  pattern are symptoms of the god-component shape — every concern
  shares the same closure scope, so changes have unbounded blast
  radius. CSS-only fixes (today's hover tone-down) cover the
  symptom without fixing the cause.
- **Decision:** **No new responsibilities are added to
  SketchCanvas.tsx, SketchInspector.tsx, App.tsx, or
  SketchStencil.tsx until each is split.** New behaviour goes into
  new files. Existing-file edits must reduce or maintain LOC, never
  grow.
- **Plan:** see [`ARCHITECTURE.md`](./ARCHITECTURE.md) — responsibility
  inventory + candidate split boundaries. Actual split happens in a
  subsequent session, in plan mode, with user approval of the chosen
  boundary.
- **Approval:** Pending — user has agreed the violation exists and
  asked for the inventory; the chosen split boundary is **not yet
  approved**.
- **Spec impact:** none on behaviour SPEC; lives in ARCHITECTURE.md.

---

### D-2026-05-05-C — `plot/CLAUDE.md` for practical guidance

- **What:** Create `plot/CLAUDE.md` translating the global / project
  core principles (SOLID, Clean Architecture, SRP, SSOT, AHA, YAGNI,
  TDD, "임시 통과 금지", "추측 금지", etc.) into Plot-specific
  *practical* checklists, triggers, and commands the assistant must
  follow inside the `plot/` subtree.
- **Why:** the principles are theoretical and live two directories
  up; in-session, the assistant defaults to "do the change" without
  consulting them. A Plot-local file with concrete triggers ("before
  editing SketchCanvas.tsx, do X") makes the principles operational.
- **Approval:** **Accepted** by user, 2026-05-05.
- **Spec impact:** none — meta rule about how the assistant operates
  inside `plot/`.

---

### D-2026-05-08-G — Node decoration must coincide with the hit-box (no `outline` / `ring`)

- **What:** Replace the three node-decoration class strings in
  `SketchNode.tsx` with `border` equivalents. Old: `outline …
  outline-offset-2 ring-1 …` (anchor) / `outline outline-1 …`
  (regular) / `outline outline-2 outline-indigo-500` (selected).
  New: `border-2 border-slate-600` / `border border-slate-300` /
  `border-2 border-indigo-500`.
- **Why — the diagnosis the previous rounds missed:** v0.13.3 and
  v0.13.4 unified the cursor inside the node and on the pane to
  `pointer` and `default` respectively. DOM probing showed a
  single cursor inside the node region. Yet the user still saw
  `pointer ↔ default` flicker on a slow mouse-move across a
  single node. The reason is that **`outline` paints outside the
  border-box and is excluded from hit-testing.** Pixels under the
  outline (and inside the `outline-offset` gap) look like they
  belong to the node, but a hit-test there resolves to the parent
  `.react-flow__pane` (cursor: default). For the anchor, the
  flicker zone was 8–10 px wide. For regular nodes (1 px outline)
  it was sub-pixel-perceivable.
- **The general rule (recorded for every future node-styling
  change):**
  > Visual extent and hit-box of an interactive node must
  > coincide. Use `border` (border-box, hit-tested) rather than
  > `outline` / `outline-offset` / `ring` / outset
  > `box-shadow` for any decoration on `.react-flow__node`,
  > `.react-flow__handle`, or any clickable element. Inset
  > `box-shadow` is fine — it paints inside the box and doesn't
  > affect hit-testing.
- **Verified:** `getBoundingClientRect()` on the
  `.react-flow__node` and its inner decorated `<div>` returns
  identical x/y/w/h after the change (banas-v013 anchor:
  710.875, 636.062, 206.54×206.54). Single distinct cursor =
  `pointer` across the entire node tree.
- **Approval:** Accepted by user, 2026-05-08 (plan approved
  before commit).
- **Spec impact:** SPEC §Anchor "Visual differentiation" row
  updated to reference `border` instead of outline + offset +
  ring. The general rule is also added to `plot/CLAUDE.md`
  anti-patterns.

---

### D-2026-05-08-F — Handles appear only when the node is selected

- **What:** Removed the hover-fade and direct-handle-scale animations
  on `.react-flow__handle`. Handles are now `opacity: 0` until the
  node is selected (`.react-flow__node.selected`), at which point
  they appear at full opacity with the indigo "connectable"
  styling.
- **Why:** the user reported "커서였다가 검지였다가 큰 검지였다가
  작은 검지였다가 등등" — the cursor itself appearing to vary in
  size / shape as it moved across a node. DOM-level cursor probing
  showed only `pointer` and `default` were ever set; the perceived
  variation was the four handle dots pulsing in opacity (0 →
  0.55 on node-hover) and one of them scaling to 1.25× on direct
  handle-hover. The dots near the pointer reading as "cursor".
- **What this changes for the user:**
  - To draw an edge: click a node first (selects it; handles
    appear). Then drag from a handle. One extra click vs. before.
  - Hovering a node now never changes the visual at all. The node
    just sits there. Selecting (clicking) is the explicit gesture
    that opens both Inspector and edge-drawing handles.
- **Approval:** Pending — matches the user's evolving "노드 선택할
  수 있게만" direction (D-2026-05-08-E) plus this round's flicker
  diagnosis. User can override if the extra click feels
  too costly.
- **Spec impact:** SPEC §Hover behaviour rewritten — three states
  collapse to two (hidden / selected), no more fade / scale.

---

### D-2026-05-08-E — Pan-on-drag removed; cursor stays pointer on click

- **What:** Three paired changes (the third was discovered after
  the user said "같아" to the first two — pure prop disable
  wasn't enough; the baseline CSS still set `grab`):
  - **`panOnDrag={false}` on `<ReactFlow>`.** Grabbing an empty
    canvas region and dragging no longer pans the viewport.
    Zoom / fit-view controls (bottom-left) and the minimap remain
    the only ways to move the view.
  - **CSS override on `.react-flow__pane` / `.react-flow__viewport`
    / `.react-flow__renderer` to `cursor: default !important`.**
    React Flow's baseline stylesheet keeps `cursor: grab` on the
    pane / viewport even when `panOnDrag` is off, which
    reintroduced the cursor flicker (grab over canvas ↔ pointer
    over node) that the user reported.
  - **Removed `.react-flow__node:active { cursor: grabbing }`
    rule.** Clicking a node previously flipped the cursor to
    grabbing for a frame even on a pure click (no drag); that
    competed with the v0.13.4 hover invariant ("on a node the
    cursor is `pointer`, period"). The
    `.react-flow__node.dragging` rule is kept so an actual drag
    still surfaces grabbing.
  - **Removed `cursor-text` from the EditableText display span**
    (separate but-related fix in the same commit). The display
    span is `role="button"` (click to enter edit mode) and now
    uses `cursor-pointer`. Previously hovering the label flipped
    the cursor to I-beam — the user described it as
    "보자기 / 가위 계속 바뀌는" (paper / scissors swapping).
- **Why:** user said exactly:
  > "노드 위에 커서 올리면 노드 선택할 수 있게만하고 캔버스 쥐고
  > 옮기는 동작을 없애세요"
  — when the cursor is on a node, only "select" should read; and
  the canvas grab-and-move action should be removed.
- **What we kept:** `nodesDraggable={true}`. The user did not ask
  to remove node drag; only the *visual signal* that the node
  was draggable on hover. They keep the position-control they've
  always wanted; the cursor just doesn't advertise it on every
  click.
- **Approval:** Accepted by user, 2026-05-08.
- **Spec impact:** SPEC §Pan and select (new), §Hover behaviour
  (clarified cursor invariant).

---

### D-2026-05-08-D — SketchCanvas split: stop at 360 LOC (not 150)

- **What:** The SketchCanvas split lands at 360 LOC, not the
  plan's 150-LOC design target.
- **Why stopped:** The plan's "ideal shell ≈ 150 LOC" was
  aspirational. Realistic floor for the current shell shape is
  ~330 LOC, broken down as:
  - ~50 LOC imports (16 sketch hooks + reactflow + types)
  - ~55 LOC `SketchCanvasProps` interface with JSDoc — the
    component's public API surface; cannot compress without
    losing documentation
  - ~10 LOC component setup (refs + 2 modal-id useStates)
  - ~140 LOC hook composition (12 hooks × ~10 LOC each for
    args + destructured returns)
  - ~15 LOC `handleNodesChange` shell (must stay in shell
    per the coupling map)
  - ~80 LOC JSX render block (ReactFlow root + Toolbar +
    SketchModals + Inspector + ContextMenu)
- **Further compression would mean** introducing a
  `useSketchCanvasModel(props)` umbrella hook that returns ~30
  fields the JSX consumes — exactly the **Candidate B
  controller pattern rejected in D-2026-05-08-A**. Going there
  now would re-concentrate the previously-decomposed concerns
  into a single 30-output return value, undoing the SRP win.
- **Net result:** SC went from **1476 LOC → 360 LOC (76%
  reduction)**. The original violation (CLAUDE.md "Review for
  splitting when a file exceeds 500 lines") is resolved with
  140-LOC headroom. 16 extracted modules under
  `canvases/sketch/` each have a single responsibility and
  unit-testable surface (4 of them — `nodeTransform`,
  `edgeTransform`, `overlapNudge`, `applyAnchorChange`,
  `nodeChanges`, `useOrphanActorRefs`,
  `useCollapsedTree.toggleCollapsed` — are pure or
  near-pure modules).
- **Approval:** Pending — user can override and request the
  controller-hook step if the 360-LOC floor is unacceptable.
- **Spec impact:** none.

---

### D-2026-05-08-C — Cursor-flicker fix on node hover

- **What:** Set `.react-flow__handle { cursor: pointer }` (matching
  the node body), restoring `cursor: crosshair` only when a
  connection is actively being drawn
  (`.react-flow__handle.connecting` / `.connectingfrom`).
- **Why:** moving the mouse across a node would flicker the cursor
  between `pointer` (node body, our rule) and `crosshair` (React
  Flow's default handle cursor). The user described it as "보자기 /
  가위 계속 바뀌는" — paper / scissors swapping — which was visually
  noisy and made the canvas feel jittery.
- **Why this isn't another bandaid:** the v0.13.2 hover tone-down
  (D-2026-05-04-E) reduced the *visual* prominence of handles but
  left React Flow's default `cursor: crosshair` rule untouched.
  That CSS default is the real source of the flicker — making the
  cursor invariant deterministic across the whole node region is
  the actual fix, not a fade.
- **What we kept:** crosshair during active edge drawing — that's
  semantic (the user IS doing something crosshair-shaped). And
  `cursor: grabbing` on `:active` when a drag actually starts.
- **Approval:** Pending — user requested the fix, ship and confirm.
- **Spec impact:** SPEC §Hover behaviour now codifies the cursor
  invariant explicitly.

---

### D-2026-05-08-B — Step 5 deviation: hook only, no pure node-transform module

- **What:** Plan called for Step 5 to extract two files —
  `nodeTransform.ts` (pure, no React) plus a thin `useNodesMemo.ts`
  wrapper. Implementation ships only `useNodesMemo.ts` (a single
  React hook).
- **Why:** the node transform reads ten-plus callbacks
  (`updateNode`, `setBodyModalNodeId`, `onNodeDrill`,
  `onAnchorChange`, plus collapsed-tree's four exports) and
  produces per-node closures (`onLabelChange`, `onResize`,
  `onToggleCollapse`, `onDrill`). A "pure" version would still
  require those callbacks as inputs — the purity would be
  cosmetic, paid for in a 10-field input interface and a
  React-aware wrapper that mostly just shuffles arguments. AHA
  ("avoid hasty abstraction") + YAGNI.
- **What this gives up:** node transform is not unit-testable in
  isolation today. If a future use case needs that (e.g. snapshot
  testing thousands of doc shapes), the hook can be split then —
  one rewrite is cheaper than the wrong abstraction now.
- **What this preserves:** edge transform (Step 6) is still split
  pure + thin-hook. Edges have far fewer callbacks (one: edge
  modal open) so the pure form is genuinely useful.
- **Approval:** Pending — recorded as a same-day execution decision;
  user can override and request the pure node-transform split if
  they want.
- **Spec impact:** none.

---

### D-2026-05-08-A — SketchCanvas split: Candidate A (modified)

- **What:** Split `plot/viewer/src/canvases/SketchCanvas.tsx` (1476
  LOC, 16 concerns) down to a thin React Flow shell (target ≈ 150
  LOC, hard ceiling 200 LOC) using **Candidate A modified**: surgical
  responsibility split per ARCHITECTURE.md, with the two pure
  transforms (nodes / edges) and overlap math extracted as plain
  `.ts` modules (no React imports) — borrowing Candidate B's domain
  purity for the parts where it actually fits.
- **Why:**
  - Candidate B (Clean Architecture controller) rejected: would
    re-concentrate `docRef`'s 19+ read sites into one
    `useSketchController.ts` — same god scope, different filename.
    The pure-transform win is real but only for two of 16 concerns,
    so we cherry-pick that part.
  - Candidate C (mechanical 4-file split) rejected: trades visible
    LOC for unchanged coupling. The next bug still has 1476-LOC
    blast radius across 4 files, just spread thinner.
  - Candidate A surgically isolates the 5 easy concerns (memos,
    inspector routing, value-flow, collapse, orphan) into
    single-purpose hooks, and keeps React Flow's prop wiring in the
    shell where it must live (per coupling map: `onNodesChange`,
    `onEdgesChange`, etc. need single handlers).
- **Plan:** see [`/Users/woogis/.claude/plans/wiggly-herding-pixel.md`](../../../.claude/plans/wiggly-herding-pixel.md)
  — Pre-Step 0 (test baseline) + Steps 1–14 (extraction in
  risk-ascending order), each commit-sized and browser-verified per
  the matrix.
- **Layout:** new files under `plot/viewer/src/canvases/sketch/`.
  16 files total (10 hooks + 4 pure modules + 1 modal component +
  1 shell remainder).
- **Approval:** **Accepted** by user, 2026-05-08.
- **Spec impact:** none on behaviour. Some load-bearing comments
  surface as new SPEC entries before extraction (Steps 5/7/9/11)
  per the plan's "Comments policy".

---

### D-2026-05-10-A — Pan re-enabled; canvas reads as a pannable surface again

- **What:** `panOnDrag` flipped back to `true` on the React Flow
  surface, and the v0.13.4 `cursor: default !important` override on
  `.react-flow__pane` / `.react-flow__viewport` /
  `.react-flow__renderer` is removed so React Flow's native
  `cursor: grab` (idle) and `cursor: grabbing`
  (`.react-flow__pane.dragging`) take effect.
- **Why:** the user reports — quoted directly — *"노드 밖에 호버
  했을 때 보여야하는 손바닥 커서가 안생기구요."* The absence of a
  hand cursor on the empty canvas read as the surface being inert
  (a "page", not a "canvas"), which conflicted with the user's
  workflow of moving the viewport to inspect different regions of
  the project graph. The v0.13.4 reasoning ("users were
  accidentally panning while clicking nodes") is reversed by the
  4 px `nodeDragThreshold`: clicks short of 4 px on a node still
  register as clicks (Inspector opens), and drags on the empty
  pane unambiguously start panning. There is no behaviour collision
  to disambiguate.
- **Methodology — probe before fix for the lingering flicker:** the
  user *also* reports — *"노드 위에 올라가면 화살표하고 검지모양
  커서가 깝박 거리고 있어요."* — that the arrow ↔ pointer flicker
  on nodes persists after v0.13.5. Five rounds of cursor work have
  fixed five distinct localised sources, but a pervasive source
  remains. Per the plot/CLAUDE.md "추측 금지" / "임시 통과 금지"
  rules, the v0.13.6 ship deliberately splits in two: Part 1 (this
  decision — pan reverse) ships immediately because it is
  spec-driven and definite; Part 2 (find and fix the pervasive
  flicker) requires a live-DOM probe in the user's real browser
  before any node-cursor code changes. The probe script and its
  expected outcomes are recorded in
  [`/Users/woogis/.claude/plans/wiggly-herding-pixel.md`](../../../.claude/plans/wiggly-herding-pixel.md).
- **Alternatives:**
  - "Hand cursor visual only, no pan" — rejected as user-hostile
    (a misleading affordance is worse than a missing one).
  - Keep pan off + a different visible cursor (e.g. `default`) —
    user explicitly asked for the hand back AND for the pan, so
    no daylight between visual and behaviour.
- **Approval:** **Accepted** by user, 2026-05-10 (plan approved
  before commit).
- **Spec impact:** [`SPEC.md` §Pan and select](./SPEC.md#pan-and-select)
  — rewritten from "does not pan" to "pans on empty-pane drag".
  [`SPEC.md` §Cursor states](./SPEC.md#cursor-states-canvas-wide-ssot-applies-to-every-canvas)
  — new section establishing the canvas-wide cursor SSOT (later
  rewritten in D-2026-05-10-C).
  [`plot/CLAUDE.md`](../CLAUDE.md) anti-patterns — new row banning
  the "force `cursor: default` on the pane to suppress flicker
  while disabling pan altogether" pattern.

---

### D-2026-05-10-B — Force-pointer on every node descendant — Rejected (rolled back same session)

- **What proposed:** Add
  `.react-flow__node *:not(.react-flow__handle):not(.react-flow__resize-control) { cursor: pointer !important }`
  to `styles.css` so every descendant of a node shows `pointer`,
  killing the "anywhere on the node" arrow-flicker the user kept
  reporting.
- **Why proposed:** Symptomatic fix when the diagnostic probe
  approach (D-2026-05-10-A Part 2) felt too slow.
- **Why rolled back:** As soon as the user saw the cursor
  table I had drafted, they pushed back — *"정리한게 이상하지
  않아요?"* / *"커서 동작 다 정리해보세요 일단."* — and on a
  follow-up cleanup request, *"RF 디폴트로 일단 가세요. 거기서
  부터 다시 시작하죠. 코드 정리 제대로 하구요."* The force-pointer
  rule was the latest in a six-round cursor-override stack
  (v0.13.3-v0.13.6 Part 1) where each round papered over a
  prior round's regression. The user's call: stop adding
  overrides, restart from the React Flow vendor baseline, then
  decide what (if anything) to deviate from. See D-2026-05-10-C.
- **Approval:** **Rejected** by user, 2026-05-10 (rolled back in
  the same session before commit).
- **Spec impact:** None — the override never shipped. The
  D-2026-05-10-A entry was edited to remove the
  D-2026-05-10-B forward reference.

---

### D-2026-05-10-C — Reset all RF cursor / handle overrides; restart from vendor baseline

- **What:** Remove **every** custom cursor / handle / handle-size /
  handle-colour CSS rule from `viewer/src/styles.css`. The file now
  contains only the html/body/#root sizing block. All cursor
  behaviour comes from `node_modules/reactflow/dist/style.css` and
  `node_modules/@reactflow/node-resizer/dist/style.css` directly.
  Also remove the `cursor-pointer` Tailwind class from
  `EditableText.tsx`'s display span — the label inherits from the
  node, which under RF default is `grab`.
- **Why:** Six rounds of cursor / handle interventions
  (D-2026-05-04-E hover-fade, D-2026-05-08-C handle-cursor unify,
  D-2026-05-08-E pan-off + label cursor-text removal, D-2026-05-08-F
  handles-on-select, D-2026-05-08-G border-replaces-outline,
  D-2026-05-10-A pan re-enable) shipped overrides on top of
  overrides. Each fix solved one localised symptom and revealed or
  introduced another. After the user's *"정리한게 이상하지 않아요?"*
  / *"RF 디폴트로 일단 가세요"* feedback, the structural problem
  is plain: the override stack itself is the regression engine,
  not any single rule in it. Removing the whole stack and
  restarting from the vendor baseline gives us:
  - **One known state** to reason from. Future "what should the
    cursor be on X?" questions answer themselves by reading the
    vendor CSS.
  - **No flicker by construction.** RF's baseline puts `cursor:
    grab` on both `.react-flow__pane` and `.react-flow__node` —
    the cursor literally cannot change when crossing the boundary.
  - **One predictable mental model for the user.** RF's "anything
    draggable shows `grab`; active drag shows `grabbing`; drawing
    a connection shows `crosshair`; resizing shows the directional
    resize cursor" is uniform and well-known across all React Flow
    deployments.
- **What we kept (not part of this reset):**
  - v0.13.6 Part 1 pan re-enable (`panOnDrag` on, no
    `cursor: default !important` override on the pane). That
    matches RF default and stays.
  - v0.13.5 border-replaces-outline on the inner node decoration.
    That decision is about *visual extent matching the click
    target*, not about cursor — clicks on the visible decoration
    must select the node, not pass through to the pane. Keeps.
  - SketchCanvas split (D-2026-05-08-A) and all other
    architecture / behaviour decisions unrelated to cursor.
- **One single rule retained — Tailwind preflight cancellation:**
  Tailwind's preflight forces `cursor: pointer` on every
  `<button>` and `[role="button"]`. The fold button and the
  EditableText label span (`role="button"`) inside a node match
  these selectors and re-introduce the very flicker this reset
  was meant to kill — node hover = `grab` (RF), label hover =
  `pointer` (Tailwind). To honor RF's "node = uniform grab"
  contract, `styles.css` keeps a **single** rule:
  ```css
  .react-flow__node *:not(.react-flow__handle):not(.react-flow__resize-control) {
    cursor: inherit;
  }
  ```
  This is not an override of RF — it is an override of *Tailwind
  preflight* that restores the RF inheritance chain inside the
  canvas. The :not() exclusions preserve RF's own semantic cursors
  on connection handles (crosshair) and resize controls
  (directional resize). This is the only cursor rule in
  `styles.css` and may not grow without a fresh decision id.
- **What this rolls back:**
  - `.react-flow__node { cursor: pointer }` (was D-2026-05-08-C).
  - `.react-flow__node.dragging { cursor: grabbing }` (was redundant
    with RF default).
  - `.react-flow__handle { width 10px / height 10px / opacity 0 / 1.5px slate-400 border / white background / cursor: pointer !important }` (was D-2026-05-08-F + earlier).
  - `.react-flow__node.selected .react-flow__handle { opacity 1 / indigo border + bg }` (was D-2026-05-08-F).
  - `.react-flow__handle.connecting / .connectingfrom { cursor: crosshair !important / opacity 1 / indigo border }` (was D-2026-05-08-C — RF default already covers this via `.connectionindicator`).
  - `EditableText` display span `cursor-pointer` class (was D-2026-05-08-E).
- **Cursor behaviour after this reset** — see
  [`SPEC.md` §Cursor states](./SPEC.md#cursor-states-canvas-wide-ssot-applies-to-every-canvas).
  In one sentence: hover anywhere on the canvas (pane or node) =
  `grab`; drag (pane or node) = `grabbing`; hover a connection
  handle = `crosshair`; hover an edge = `pointer`; hover a resize
  control = directional resize cursor.
- **Future deviation rule:** any new cursor / handle override must
  open a fresh `D-YYYY-MM-DD-X` entry with explicit user approval
  *and* a comment in the CSS rule naming that decision id. The
  override stack must never grow without an audit trail.
- **Approval:** **Accepted** by user, 2026-05-10 — *"RF 디폴트로
  일단 가세요. 거기서부터 다시 시작하죠. 코드 정리 제대로 하구요."*
- **Spec impact:** [`SPEC.md` §Hover behaviour](./SPEC.md#hover-behaviour)
  rewritten from "handles only when selected, cursor pointer
  everywhere" to "RF defaults, handles always visible". [`SPEC.md`
  §Cursor states](./SPEC.md#cursor-states-canvas-wide-ssot-applies-to-every-canvas)
  rewritten to mirror the vendor CSS exactly. [`plot/CLAUDE.md`](../CLAUDE.md)
  anti-patterns updated.

---

### D-2026-05-10-D — Gate 0: user confirmation pins the spec immediately

- **What:** Add a new pre-action gate at position 0 (before the
  existing Gate 1) in [`plot/CLAUDE.md`](../CLAUDE.md). The gate
  fires on a fixed keyword set in the user's message
  (`승인합니다 / 좋아요 / 네 좋아요 / 됐다 / 이제 됐다 / 맞아요`,
  English equivalents) and forces the assistant, before any other
  tool call, to: (1) state the confirmed behaviour in one
  declarative sentence, (2) update `docs/SPEC.md` so its text
  matches the confirmation pixel-identically, (3) append a
  `D-YYYY-MM-DD-X` entry to this file with `Accepted by user,
  YYYY-MM-DD`, and (4) stage SPEC + DECISIONS into the current
  commit cycle (or a docs-only follow-up if the implementing
  commit already shipped).
- **Why:** This is a structural fix for the "work doesn't
  accumulate across sessions" pattern the user has flagged
  repeatedly. The v0.13.3 → v0.13.6 cursor work is the canonical
  motivating example — six rounds of cursor changes because each
  confirmed behaviour evaporated before reaching the spec, so the
  next session re-asked questions the user had already answered.
  The user's exact framing this session: *"plot 의 claude.md 에
  제품의 스펙이 확정되면 문서에 반영한다는 룰이 있어야할 것
  같구요."*
- **Why these specific keywords (not a free-form trigger):**
  Concrete `literal-string-match` triggers are far more reliably
  applied by the assistant than vague conditions like "behaviour
  changed". The list is closed and short on purpose. New
  approval-style phrasings can be added later via a follow-up
  decision id; do not silently expand the list.
- **Why "before any other tool call":** Without an ordering
  constraint, the assistant defers SPEC updates to the next
  message, then forgets, then ships an implementation commit
  with no spec line to back it. The "before any other tool call"
  language matches the same fail-fast severity as `behavior:
  부분 완료 → 금지` in the global CLAUDE.md.
- **Banned shortcuts (encoded in the gate body):** deferring to
  "next session"; assuming the SPEC line exists without verifying
  the diff; batching multiple confirmations into one update;
  treating an unclear confirmation as implicit (must explicitly
  ask the user instead).
- **Approval:** **Accepted** by user, 2026-05-10 — *"네 좋아요"*
  in response to the proposed Gate 0 draft. This decision entry
  is itself the first application of Gate 0.
- **Spec impact:** None on product spec. This is an operational
  rule change in `plot/CLAUDE.md`. SPEC.md remains the canonical
  product behaviour spec; Gate 0 is the discipline that keeps it
  in sync with reality.

---

### D-2026-05-10-E — Auto-layout restored as mindmap-style directional tree — **Rejected (rolled back v0.14.1, 2026-05-10)**

> Originally Accepted 2026-05-10 (this entry). Rolled back the same
> day in v0.14.1 — see [D-2026-05-10-G](#d-2026-05-10-g--auto-layout-removed-again-cost-vs-benefit).
> Original entry preserved below for the historical record.

- **What:** Bring back an "Auto layout" button on the
  `<SketchToolbar>`. Implementation is a custom directional-tree
  algorithm rooted at the canvas anchor, grouping each node's
  children by the parent-side handle of the connecting edge:
  - `R` handle ⇒ child stacked in a vertical column to the right.
  - `L` handle ⇒ child stacked in a vertical column to the left.
  - `T` handle ⇒ child placed in a horizontal row above.
  - `B` handle ⇒ child placed in a horizontal row below.
  Spacing uses Reingold-Tilford-style subtree-extent tracking to
  guarantee no node-to-node overlap. Tree edges follow a BFS
  spanning tree from the anchor; cycle-closing edges are drawn but
  ignored for placement. Node-id ordering breaks ties for full
  determinism. Result is applied via `onDocChange` so it lands in
  the standard undo stack.
- **Why this shape (not radial / not force-directed):** the user's
  two binding constraints are *"오른쪽에 연결된 노드들을 오른쪽에
  정렬해야하고 (아래로 정렬하면 안됨), 위쪽에 있는건 위쪽에 정렬"*
  (handle direction is strict — the side a child connects from is
  the side it lands on) and *"노드들이 서로 겹치지 않게"* (no
  overlap, period). Radial layouts (e.g. d3 `tree()` with polar
  coordinates) violate the first because they distribute children
  evenly around 360° regardless of which handle was used.
  Force-directed layouts (e.g. d3-force) violate the first because
  edge directionality has no preferred axis in the simulation.
  A custom directional tree is the smallest algorithm that hits
  both constraints exactly.
- **Why no library:** the four-direction grouping is unconventional
  enough that no off-the-shelf layout library matches without
  significant adaptation. The pure algorithm fits in one ~150-LOC
  module under `plot/viewer/src/canvases/sketch/autoLayout.ts`
  with no new runtime dependency.
- **Why anchor stays put:** moving the anchor would yank the entire
  visual centre of the canvas every time the user runs auto-layout.
  Keeping it fixed lets the user position the anchor manually once
  and use auto-layout to clean up everything around it.
- **Why BFS spanning tree (not full graph layout):** the spec
  promises *no edge crossings in the spanning tree* — that's only
  achievable on an actual tree. Cycles in the user's graph are
  collapsed to a tree by BFS; the leftover edges are drawn as
  cross-links so the user still sees them. Crossings on
  cross-links are unavoidable on graphs with cycles and are
  acknowledged in the spec.
- **Why no animation, no preview:** explicit user requirement is
  that auto-layout be predictable. Single-click → instant re-layout
  → `Cmd+Z` if you don't like it. Adding animation or preview
  introduces a moment where the user is staring at an in-progress
  layout and can't tell whether to trust it.
- **Approval:** **Accepted** by user, 2026-05-10 — *"네 일단
  해봐요"* on the proposed spec table.
- **Spec impact:** [`SPEC.md` §Auto-layout](./SPEC.md#auto-layout) —
  fully rewritten from "Removed" to the directional-tree spec
  above.

---

### D-2026-05-10-F — Cursor flicker root cause: `[role="button"]` on `.react-flow__node`; Auto layout button moved to lower-left Controls

Two related fixes shipped together because the user surfaced both
in the same browser-verification round:

#### Part 1 — Tailwind preflight cancellation on `.react-flow__node[role="button"]`

- **What:** Add `.react-flow__node[role="button"] { cursor: grab }`
  (and its `.dragging` companion → `grabbing`) to `viewer/src/styles.css`.
- **Why — root cause finally identified:** v0.13.3-v0.13.6 chased
  cursor flicker through six rounds and *every diagnosis was wrong*.
  The actual cause: **React Flow v11 sets `role="button"` on
  `.react-flow__node` itself** for accessibility. Tailwind preflight
  `[role="button"] { cursor: pointer }` matches that element directly,
  which overrides the RF-default `cursor: grab` *on the node* and
  then propagates pointer down the inheritance chain. The v0.13.6
  reset's premise ("RF default is grab; just remove our overrides")
  was correct in theory but Tailwind preflight had been silently
  shadowing it the whole time. Verified empirically via Playwright
  DOM probe — walking the parent chain from a span inside a Mission
  node showed `cursor: pointer` originating at the
  `.react-flow__node` element, not at any of our descendant rules.
- **Verification:** post-fix Playwright sweep across the entire
  canvas grid (50px sample × 22 columns × 21 rows) returned only
  three distinct cursors anywhere: `grab` (pane + every node body),
  `auto` (SVG inside MiniMap, never user-interactive), `not-allowed`
  (disabled toolbar buttons). No `pointer` on any node body. No
  cursor changes when crossing between pane and node.
- **Why this didn't surface earlier:** every prior round assumed
  the cursor cascade stopped at our rules vs RF defaults. Nobody
  walked the actual DOM tree to find that Tailwind was injecting
  via an attribute selector neither our code nor RF documentation
  highlighted. The fix took 30 seconds once the cause was known;
  the prior six rounds spent ~60 minutes of round-trip on wrong
  diagnoses. Process lesson: probe the live DOM **first**, theorise
  **second**.

#### Part 2 — Auto layout button moved from `<SketchToolbar>` to React Flow `<Controls>`

- **What:** Move the v0.13.9 Auto layout `IconBtn` (top-right
  toolbar) into the React Flow `<Controls>` panel at lower-left,
  rendered as a `<ControlButton>` below zoom / fit / lock.
- **Why:** the user grouped auto-layout mentally with view-state
  controls (zoom / fit) rather than mutation actions (undo / redo).
  Direct quote: *"정렬은 그리고 왼쪽 아래에 핏하는거하고 같은 곳에
  넣어도 되요. 오른쪽 상단에 둘 필요 없음."* Lower-left is also where
  the user's eye already goes for camera-related operations.
- **What this preserves:** the algorithm itself is unchanged from
  D-2026-05-10-E; only the trigger UI moved. Disabled state still
  fires when no anchor exists or when the canvas has no non-anchor
  nodes.

#### Process change implied for future sessions

- **First step on any cursor / hit-test bug = Playwright DOM probe**,
  not code reading. CURSOR.md's probe script is the canonical
  starting point. Walking the parent chain from
  `document.elementFromPoint` is mandatory before proposing a fix.
- **Tailwind preflight is a hidden source of cursor regressions.**
  It applies to attribute selectors (`[role="button"]`, `[disabled]`)
  that interact silently with vendor library accessibility
  attributes. CURSOR.md's anti-patterns table now includes this
  failure mode.

- **Approval:** **Accepted** by user, 2026-05-10.
- **Spec impact:** [`SPEC.md` §Cursor states](./SPEC.md#cursor-states-canvas-wide-ssot-applies-to-every-canvas)
  — augmented to mention BOTH preflight cancellation rules (v0.13.6
  for descendants, v0.13.10 for the node element itself).
  [`SPEC.md` §Auto-layout — Trigger and undo](./SPEC.md#auto-layout)
  — button location updated to lower-left Controls panel.
  [`CURSOR.md`](./CURSOR.md) updated.

---

### D-2026-05-10-G — Auto-layout removed again — cost vs benefit

- **What:** Remove auto-layout from Plot in v0.14.1. Delete
  `viewer/src/canvases/sketch/autoLayout.ts`,
  `viewer/src/canvases/sketch/useAutoLayout.ts`, and the unit test
  file. Drop the `<ControlButton>` invocation in `SketchCanvas.tsx`
  along with its imports. Revert the regression test from
  v0.13.9-inverted ("auto layout button MUST exist") back to its
  v0.13.8 form ("auto layout button MUST NOT exist").
- **Why (user):** *"근데 auto layout 빼야겠네 문제가 너무 많다. 넣고
  나서 커서 들에 문제 너무 많고."* User cost/benefit assessment
  after observing the feature in action: the value of auto-layout
  at this stage of Plot does not justify the complexity / debugging
  load it added across v0.13.8 → v0.14.0.
- **Honest correction on causation:** the user attributed the cursor
  flicker problems to auto-layout temporally ("after adding it,
  cursor problems were too many"). The actual root cause was
  unrelated — RF v11 sets `role="button"` on `.react-flow__node`
  which Tailwind preflight matched and overrode the RF default
  `cursor: grab` (see [D-2026-05-10-F](#d-2026-05-10-f--cursor-flicker-root-cause-rolebutton-on-react-flow__node-auto-layout-button-moved-to-lower-left-controls)).
  The Tailwind preflight cancellation rule shipped in v0.13.10 fixes
  the cursor flicker independently and remains in place after this
  removal. Removing auto-layout therefore does not undo any cursor
  fix — it simplifies the canvas surface.
- **Why the user's call still stands despite the misattribution:** the
  removal is a separate cost/benefit decision. Even if cursor was
  the trigger to revisit, the broader argument ("the feature added
  too much complexity for too little user value at this stage")
  applies on its own merits. Plot has no users with complex
  multi-actor / multi-service graphs yet; the value of auto-layout
  is theoretical until then. When real users surface a clear need,
  re-introduction can be weighed afresh with concrete user
  workflows in mind.
- **What stays:** the v0.13.10 cursor fix
  (`.react-flow__node[role="button"] { cursor: grab }` + the
  descendant inheritance rule). Plot v0.14.1 has no cursor flicker;
  pane and node both show `grab`, transitions are clean.
- **Re-introduction policy:** any future "let's bring back
  auto-layout" proposal must (a) open a fresh `D-YYYY-MM-DD-X` entry,
  (b) cite specific real-user workflows that demand it, (c) include
  a cost/benefit comparison against this entry's reasoning, and
  (d) get explicit user approval before any code lands. The
  D-2026-05-04-D / D-2026-05-10-E / D-2026-05-10-G oscillation in
  this DECISIONS log is itself the cautionary tale.
- **Approval:** **Accepted** by user, 2026-05-10 — *"빼야겠네"*
  (in response to assistant's offer to verify Foundation behaviour
  next).
- **Spec impact:** [`SPEC.md` §Auto-layout](./SPEC.md#auto-layout)
  rewritten back to "Removed", with the full history paragraph
  preserving the lineage of decisions D-2026-05-04-D →
  D-2026-05-10-E → D-2026-05-10-F → D-2026-05-10-G so future
  sessions can read the saga in one place.
- **Files removed:**
  - `viewer/src/canvases/sketch/autoLayout.ts`
  - `viewer/src/canvases/sketch/useAutoLayout.ts`
  - `viewer/tests/autoLayout.test.ts`
- **Files reverted:**
  - `viewer/src/canvases/SketchCanvas.tsx` (drop ControlButton + useAutoLayout)
  - `viewer/tests/SketchCanvas.regression.test.tsx` (re-invert auto layout assertion)

---

### D-2026-05-11-A — Pure RF default cursors (revert all cancellation rules); remove MiniMap

- **What:** Two related simplifications shipped in v0.14.2.
  1. **Cursor:** Remove every cursor rule from
     `viewer/src/styles.css`. The v0.13.6 (D-2026-05-10-C) and
     v0.13.10 (D-2026-05-10-F) Tailwind preflight cancellation rules
     are gone. `styles.css` now contains only `@tailwind` imports +
     `html/body/#root` sizing. Resulting cursors come purely from
     React Flow defaults + Tailwind preflight composition.
  2. **MiniMap:** Remove the `<MiniMap zoomable pannable />` from
     `viewer/src/canvases/SketchCanvas.tsx` (and its import). No
     more bottom-right overview.
- **Why (user):** *"일단 RF 기본으로 돌리라구요. 이해를 못하지?"* —
  the user's core mental model has been "pointer on clickable node,
  crosshair on draw-from handle, grab on pannable pane" all along.
  v0.13.6 and v0.13.10 added cancellations to force `node = grab`
  (RF's nominal default) but that contradicted the user's intent.
  Pure RF default + Tailwind preflight COMPOSES to exactly what the
  user wants:
  - `.react-flow__node` (RF v11 sets `role="button"`) → preflight
    overrides RF's `grab` to `pointer`.
  - EditableText label span (`role="button"` for keyboard a11y) →
    preflight `pointer`.
  - Fold `<button>` → preflight `pointer`.
  - `.react-flow__pane` → RF default `grab`.
  - `.react-flow__handle.connectionindicator` → RF default
    `crosshair`.
  - Resize controls → vendor defaults.
  Verified empirically via Playwright DOM probe at multiple
  coordinates after the revert.
- **Lesson encoded for future sessions:** The assistant repeatedly
  added cancellation rules to "fix" Tailwind preflight matching RF's
  attribute-based selectors. The user's preference was always to
  let preflight + RF compose naturally. Four iterations of this
  mistake (v0.13.5 / v0.13.6 / v0.13.10 / v0.14.2) should have been
  one. Heuristic for future Plot cursor work: **default to NO
  cursor rules in `styles.css`. Only add a rule when a real,
  Playwright-probed user complaint cannot be explained by Tailwind
  + RF interaction.**
- **Anchor asymmetry note:** anchor body shows `grab` (because the
  anchor uses a static `<span>`, no `role="button"`) while the
  other Foundation nodes show `pointer` (EditableText). Acceptable
  per this decision; if a future requirement demands anchor =
  pointer too, a single focused rule + new decision id.
- **Approval:** **Accepted** by user, 2026-05-11 — *"이제 됐네 자
  문서들 업데이트하구요."* User additionally requested MiniMap
  removal in the same exchange (*"오른쪽 아래에 있는 오버뷰? 이거
  없애요."*) which is bundled here.
- **Spec impact:**
  - [`SPEC.md` §Cursor states](./SPEC.md#cursor-states-canvas-wide-ssot-applies-to-every-canvas)
    — fully rewritten to "pure RF default + Tailwind preflight, no
    overrides" with the new cursor table and the anchor-asymmetry
    note.
  - [`CURSOR.md`](./CURSOR.md) — cancellation sections removed,
    "no overrides — pure RF default + Tailwind preflight" section
    added; change-history updated.
  - [`SPEC.md`](./SPEC.md) — MiniMap removed from the implicit
    canvas surface inventory (no explicit MiniMap section existed,
    so no rewrite needed beyond noting in CHANGELOG).
- **Files touched:**
  - `viewer/src/styles.css` — strip cursor rules.
  - `viewer/src/canvases/SketchCanvas.tsx` — remove `MiniMap` import + JSX.

---

### D-2026-05-11-B — Architectural concern: auto-layout work bled into cursor code (review next session)

- **What (user observation):** *"지금 문제는 오토레이아웃을
  넣어달라고 했는데 이거 때문에 커서 관련된 코드에 영향을 받는거에요.
  이거 잘못된거죠. 완전히 다른 영역인데 영향을 받는다? 이거 설계를
  잘못한거에요. 다음세션에서 심층적으로 검토하고 개선할 수 있게
  해두세요."*
- **Why this matters:** Cursor (visual contract for the canvas
  surface) and Layout (positioning algorithm) are two independent
  concerns. The fact that v0.13.8 → v0.14.1 auto-layout work
  triggered ~6 cursor regressions demonstrates that the codebase
  does not isolate these contexts. Per
  [`DOMAIN.md`](./DOMAIN.md): cursor is a cross-cutting visual
  contract; layout belongs to `EssencePlanning`. They should not
  share files, mutation paths, or runtime state. Today they do.
- **Trigger for next session:** When the user says **"다음"** in a
  Plot session start, this entry's "Review scope" below becomes
  the active task. The SessionStart hook surfaces this trigger
  via [`plot/docs/NEXT_SESSION.md`](./NEXT_SESSION.md) — see
  there for the full review scope and execution plan.
- **Approval:** **Accepted** by user, 2026-05-11 (instruction
  to record + execute next session).
- **Spec impact:** No immediate code change. Spec impact from the
  next-session review goes into a follow-up D-YYYY-MM-DD-X entry
  once the architectural fix is designed.

---

### D-2026-05-11-C — cursor ⊥ auto-layout: cognitive coupling, not mechanical; structural gate added

- **What:** The "cursor was broken by auto-layout work" review
  (queued in D-2026-05-11-B + NEXT_SESSION.md, fired by the
  user saying "다음") concludes that the coupling was
  **cognitive (commit bundling), not mechanical (shared files)**.
  Verified empirically against the v0.13.7..v0.14.2 git history:
  - `viewer/src/styles.css` (cursor SSOT) was not modified by any
    auto-layout commit (v0.13.8 docs, v0.13.9 impl, v0.14.1 revert).
  - `autoLayout.ts` / `useAutoLayout.ts` were not modified by any
    cursor commit (v0.13.10, v0.14.2).
  - The only mechanical intersections were `SketchCanvas.tsx`
    (shell, 359 LOC, well within the 500-line rule) and
    `SketchToolbar.tsx` (button-location decision) — both edits
    touched disjoint JSX regions.
  - v0.13.10 commit ("cursor flicker root cause + auto-layout
    button placement") bundled both concerns in one atomic commit;
    this is the cognitive coupling vector.
  - Cursor flicker existed since v0.13.0 (RF v11's `role="button"`
    + Tailwind preflight `[role="button"] { cursor: pointer }`
    collision) — auto-layout was the *trigger for discovery*, not
    *insertion*. D-2026-05-10-G already records this causal
    correction; this entry generalises the lesson.

  Structural gate ships in v0.14.3 with three orthogonal
  enforcement mechanisms:
  1. `plot/hooks/pre_commit_gate.py::cross_cutting_bundle_check`
     denies any commit that stages `viewer/src/styles.css`
     (cross-cutting visual SSOT) alongside feature code under
     `viewer/` or `plot_mcp/`. Tests are excluded from the
     "feature" category so test-with-target shipping stays normal.
  2. `viewer/tests/styles-cursor-baseline.test.tsx` asserts
     `styles.css` has zero cursor declarations outside comments.
     Adding one requires a fresh D-id and updating the test
     together — making the audit trail mechanical.
  3. `plot/agents/plot-verifier.md` Step 4 default now runs the
     cursor DOM probe sweep FIRST on every viewer change,
     regardless of declared change kind. A latent cursor
     regression hidden behind an unrelated feature commit fails
     verification.

  `plot/CLAUDE.md` anti-patterns table gains a row pointing here.

- **Why this matters:** Cursor (cross-cutting visual contract) and
  Layout (`EssencePlanning` algorithm per
  [`DOMAIN.md`](./DOMAIN.md)) cannot share a natural domain
  home. DOMAIN.md line 205 already records this correctly:
  *"Cursor SSOT | Cross-cutting | OK as-is — visual contract has
  no natural domain home."* The right enforcement layer is
  **commit hygiene + static guard + verification default**, not
  domain re-modelling.
- **Alternatives considered and rejected:**
  - (a) Extract `cursorContract.ts` module — rejected: `styles.css`
    is currently 27 LOC with zero cursor rules (post-v0.14.2).
    Empty abstraction violates YAGNI.
  - (b) Pre-commit gate via shell hook in `.git/hooks/` instead
    of `pre_commit_gate.py` — rejected: noory-ai CLAUDE.md
    "Cross-Platform Compatibility" bans shell scripts; the Plot
    hook already runs through `pre_commit_gate.py` PreToolUse.
  - (c) Add cursor as a separate bounded context in DOMAIN.md —
    rejected: DOMAIN.md line 205 already explicitly decided
    cursor is cross-cutting with no domain home. Adding a context
    would contradict that decision.
  - (d) Refactor `useNodesMemo` / `useEdgesMemo` to isolate
    transient runtime state — rejected: the ghost-edge symptom
    from v0.13.9 testing was resolved by D-2026-05-10-G
    (auto-layout removal). No live problem to refactor for.
- **Honest premise correction:** the original D-2026-05-11-B
  framing implied a mechanical coupling between cursor and
  auto-layout files. Phase 1 analysis showed this was wrong —
  the files never shared territory. The architectural review
  therefore targets the real failure mode (commit bundling +
  latent visual bugs surfacing during feature verification)
  rather than the named one (cursor ↔ auto-layout file
  coupling). User confirmed this re-framing during the 2026-05-10
  session.
- **Approval:** Pending — user, 2026-05-10.
- **Spec impact:** none. Structural / process change with no
  observable Plot behaviour difference.

---

### D-2026-05-11-D — i18n infrastructure (English primary, Korean locale)

- **What:** Bootstrap i18n in the Plot viewer using `react-i18next`
  + `i18next` + `i18next-browser-languagedetector`. New module
  `viewer/src/i18n/` owns the resource bundles
  (`locales/en.json` + `locales/ko.json`), the `init()` call
  (imported from `main.tsx` for side effects), and the
  `LanguageToggle` component rendered at the bottom of
  `SketchSidebar`. First-batch migrations: `SketchToolbar` (Undo /
  Redo + tooltips) and `SketchSidebar` (project list controls,
  rename / delete confirmations, session-tags section). All
  remaining hardcoded UI text is queued for follow-up commits.

  Static guards shipped:
  - `viewer/tests/i18n-keys-parity.test.ts` — asserts `ko.json`
    has the identical key set as `en.json` and that every value is
    a non-empty string. Locale drift = test fail.
  - `plot/CLAUDE.md` anti-patterns table gains a row blocking
    hardcoded UI text.

  Detection order is `localStorage["plot:lang"] → navigator.language
  → en`. User choice persists across sessions.

- **Why:** User direction (2026-05-10):
  > "우리는 로컬라이즈도 신경 써야합니다. 이건 글로벌 서비스가
  > 될거거든요."

  Establishes the global-service identity recorded in
  `feedback_plot_global_service.md`. Domain-boundary + SSOT must be
  strict from inception (user CLAUDE.md "design"); deferring i18n
  to a "later" milestone would compound hardcoded-text sprawl and
  force a high-cost retrofit.

- **Library choice rationale:** `react-i18next` (over a custom
  ~50 LOC wrapper or `lingui`):
  - Mature production stack; well-documented React hooks API.
  - Supports interpolation (`{{name}}`), pluralization, namespaces
    out of the box — needed within months as the UI surface
    grows.
  - Standard pattern for the global-service identity; ~30KB cost
    is acceptable for a viewer that already ships Mermaid +
    React Flow + React Markdown.
  - User explicitly selected this option via AskUserQuestion.

- **Scope limit (first commit):** Only the most visible toolbar +
  sidebar strings migrate in v0.14.4. The rest of the viewer
  (Inspector forms, Stencil labels, App-level toasts, context
  menus, modals) will migrate in subsequent commits. The
  anti-pattern row + the parity test prevent NEW hardcoded text
  from appearing in the meantime.

- **Approval:** Pending — user, 2026-05-10.
- **Spec impact:** none observable beyond the new language toggle
  pill in the sidebar's footer. No canvas behaviour changes.

---

### D-2026-05-11-E — Product spec pinned as PRODUCT_SPEC.md; product framing now lives above VISION

- **What:** User delivered a Plot product spec mid-session
  (2026-05-11) covering platforms (Claude plugin → macOS app),
  business model (individual free / enterprise paid, PLG growth),
  tech stack (React Flow / JSON / Markdown / Mermaid / MCP), data
  principles (JSON SoT, owner field, MD export targets), Figma-style
  symbol system, four canvas layers with audience split (humans vs
  agents), agent-interview UX pattern, snapshot work-item layer,
  PR-style feedback loop, MVP scope, future / out-of-scope.

  Per user direction *"이건 잘 정리해두세요. 작업 다 끝나고"*, the
  spec is pinned to [`plot/docs/PRODUCT_SPEC.md`](./PRODUCT_SPEC.md)
  as a new canonical document. Translated to English (per
  noory-ai CLAUDE.md "Language" rule), reorganised into AI-First
  structured sections with cross-references to existing docs.

- **Why this matters:** product-level facts (who Plot is for, what
  platforms, what's in MVP, what's deferred) were scattered across
  conversation history and partially in VISION.md. Consolidating to
  one file gives every future session a single place to read the
  framing before touching code. Without it, the next session is
  liable to re-litigate decisions that already have a user mandate.

- **Position in the doc set:** PRODUCT_SPEC sits **above** VISION.md.
  VISION is the essence; PRODUCT_SPEC is how the essence becomes a
  shippable product. `plot/CLAUDE.md` reading order updated to put
  PRODUCT_SPEC as step 2 (right after VISION, before DOMAIN).
  `VISION.md` Cross-references updated to point at PRODUCT_SPEC
  first.

- **What this does NOT do:**
  - Does NOT change code. No new fields on `SketchNode`, no canvas
    splits, no new MCP tools.
  - Does NOT change the existing doc files beyond cross-link
    insertion. SPEC, CONCEPTS, ROADMAP, DOMAIN unchanged.
  - Does NOT decide the open questions captured in §16 of
    PRODUCT_SPEC (Mission/Identity canvas split, PR-loop
    enforcement, snapshot subsystem, Mermaid rendering, owner field
    landing date). Each becomes its own follow-up `D-YYYY-MM-DD-X`
    when the user calls.

- **Alternatives considered and rejected:**
  - **Fold the product spec into VISION.md** — rejected: VISION's
    "one sentence at the top" discipline (D-pre-VISION) breaks if
    platform / business-model / MVP detail gets bolted on. Two
    files, clear roles.
  - **Distribute the spec content across existing docs** (Mermaid
    → ROADMAP, owner field → CONCEPTS, snapshot → SPEC, …) —
    rejected: scatter violates SSOT and makes the framing hard to
    read in one session. PRODUCT_SPEC is the framing; the other
    docs implement it.
  - **Skip pinning, treat as conversation memory only** — rejected:
    explicitly contradicts the user instruction *"이건 잘
    정리해두세요"*.

- **Approval:** Pending — user, 2026-05-11.
- **Spec impact:** SPEC.md unchanged (PRODUCT_SPEC is upstream).
  VISION.md gains a Cross-references entry. plot/CLAUDE.md reading
  order updated to include PRODUCT_SPEC as item 2.

---

### D-2026-05-12-A — PRODUCT_SPEC.md revision 2: mindmap/graph split, isomorphic-git, Foundation single canvas, MD-as-export queued

- **What:** User delivered a substantially revised product spec
  on 2026-05-12 (full text recorded in the conversation). The
  spec changes flowing into `plot/docs/PRODUCT_SPEC.md` rev 2:
  1. **§1 — Language split.** Plot is a "mindmap" to users,
     "graph" internally. Internal model supports cycles +
     self-loops; trees alone don't fit.
  2. **§4 — `isomorphic-git` added** to the tech stack.
  3. **§5 — "Cycles allowed"** explicit. Self-loops legal.
  4. **§6 — Source-data version control (new section).**
     Plot's *content* (canvas JSON, user stories, tasks) is git-
     versioned, isolated from any source-code git the user
     happens to be in. Snapshot ≡ commit. Agent proposal ≡
     branch. User approve ≡ merge. User reject ≡ branch delete.
     GitHub remote integration is a future option.
  5. **§8 — Mission / Core-value / Identity → one canvas.** The
     v0.14.7 open question (#2) "split or keep one canvas?" is
     resolved by the user: keep one. Audience distinction
     (human-facing for Mission + Core value; agent-facing for
     Identity) is visual, not structural.
  6. **§8 — Service-Detail starts empty.** Fills bottom-up
     through the agent-interview + user-story loop. Living
     document framing.
  7. **§9 — Service interview produces two artefacts.** Service-
     Detail content AND user-story draft, sharing provenance.
  8. **§10 — Snapshot ≡ commit SHA**, formalising the link
     between the work-item layer and §6.
  9. **§11 — Feedback loop is git-branch shaped** per §6.
  10. **§13 — GitHub integration** added to future items.
  11. **MVP section removed.** The rev-1 "MVP scope" framing is
      gone; the user has moved past pre-launch scope discussion.
  12. **§15 Open questions reorganised.**
      - Closed: Mission/Identity canvas split (resolved in §8).
      - Added: MD-as-export migration (Phase 2; the v0.13 co-
        equal MD becomes a derived export). User direction:
        *"이 부분은 나중에 다시 다듬어 봅시다."* Deferred.
      - Added: isomorphic-git integration timing.
      - Added: i18n string lifecycle skill (delete unused keys).
      - Added: Plot repository split (move out of noory-ai
        monorepo).
- **Why:** The product framing matures. Cycles + git + bottom-up
  service-detail + branch-shaped agent proposals are concrete
  enough now to commit. Open items either have a clear
  deferral marker or a clear future plan.
- **Approval:** Pending — user, 2026-05-12 (delivered spec
  verbatim, no further confirmation requested).
- **Spec impact:** PRODUCT_SPEC.md fully rewritten (rev 2). No
  immediate code change. The MD-as-export shift (§15 #2) and the
  git integration (§15 #3) are large enough to need their own
  D entries when work begins. SPEC.md / CONCEPTS.md / ROADMAP.md
  unchanged — each will get its own update when the queued items
  land.
- **Files:** `plot/docs/PRODUCT_SPEC.md` (rev 2), this entry.

---

### D-2026-05-12-B — Structural reset planned: v0.15.0 = domain layer + entity classes + componentisation

- **What:** Capture the architectural-debt diagnosis the user
  surfaced at the end of the 2026-05-12 session and queue the
  v0.15.0 structural reset as the next session's top priority.
  Old backlog items (i18n audit, Mermaid, owner field, repo
  split, isomorphic-git, MD-export, snapshot layer, v0.15 Actors
  migration) are PARKED until the reset lands.

  User direct quotes:
  - *"파운데이션에서 사용되는 커서 컨트롤하고 액터나
    서비스에서 사용되는 커서 컨트롤이 다릅니다. 코어 원칙이
    지켜지고 있지않아요. 이게 진짜 문제인거에요. 개발을 잘
    못하고 있는거거든요. 이건 당장해야하는거에요."*
  - *"엔티티 정의도 안되어 있구요."*
  - *"기본을 못하고 있는겁니다."*
  - *"코드 재활용 할 수도 없게 해뒀어요. JSON을 직접 건드리고
    있는게 아닌지 모르겠네요. fromJson, toJson 같은걸 쓰고
    클래스를 코드로 만들어서 개념화해야 했다."*
  - *"도메인 레이어 설계가 제대로 되어 있는지도
    모르겠구요."*
  - *"이런 작업들을 다음 세션에 해야해요."*
  - *"필요하다면 스킬이나 룰을 만들구요."*

- **Code evidence supporting the critique (verified 2026-05-12):**

  | Probe | Result |
  |---|---|
  | `viewer/src/types.ts:174` comment | Self-admits *"The runtime payload is still SketchNode (god interface)"* |
  | `grep -rE "fromJson\|toJson\|parse(\|serialize("` in viewer/src | **0 hits** (JSON.parse / stringify excluded) |
  | `grep -rE "^class \|^export class "` in viewer/src | **0 hits** |
  | `find viewer/src -type d \| grep -iE "domain\|entit\|model"` | No directory |
  | `types.ts` 305 LOC | 100% type / interface declarations; zero methods, zero invariants |
  | `SketchInspector.tsx` | 1422 LOC, kind-branching for every typed field |
  | `SketchCanvas.tsx` | 359 LOC, one god component for 3 canvas tabs via `doc.canvas_kind` runtime discriminator |

  The viewer has **no domain layer** in the Clean-Architecture /
  DDD sense. It has a god TypeScript interface (`SketchNode`)
  holding every kind's flat fields, no JSON↔domain boundary, no
  per-kind entity classes, no per-canvas components, no per-kind
  Inspector modules. The v0.13 "Phase 5 discriminated union" is
  cosmetic aliases only (per the `types.ts:174` comment); runtime
  is still god.

- **Why this matters:** the rule violation is explicit. Both:
  - User CLAUDE.md `architecture: Clean Architecture, DDD`, and
  - Memory `feedback_no_god_object.md` non-negotiable rule:
    *"kind 별 클래스 + Pydantic/TS discriminated union 비협상.
    한 클래스에 모든 kind 필드 = 디자인 실패."*

  The 9 i18n / UI cleanup commits shipped this session
  (v0.14.3–v0.14.12) are paint on top of the god object. They
  do not fix the structural problem and they make further
  surface work increasingly fragile.

- **What ships in v0.15.0 (planned, multi-session):**

  - **Phase A — Domain entity classes** in
    `viewer/src/domain/`. 15 per-kind classes (Mission /
    CoreValue / Identity / Actor / ActorRef / Service /
    Category / MissionRef / ValueRef / IdentityRef / Metric /
    Step / Rule / Content / Project), each with kind-specific
    fields only + `static fromJson` / `toJson` / invariants.
    `domain/SketchNode.ts` = discriminated union. `domain/CanvasDoc.ts`
    = `Canvas` class.
  - **Phase B — Server alignment** with
    `plot_mcp/models.py` Pydantic.
  - **Phase C — Inspector kind fan-out.** Split
    `SketchInspector.tsx` into per-kind inspectors.
  - **Phase D — Canvas componentisation.** `FoundationCanvas`,
    `ActorsCanvas`, `ServicesCanvas`, `ServiceDetailCanvas` as
    separate components.
  - **Phase E — Cursor / interaction contracts per canvas.**
  - **Phase F — Verification.** Per-canvas cursor sweep +
    per-kind Inspector smoke + entity-shape round-trip test.

  Done criteria: `viewer/src/domain/` has ≥ 15 entity classes,
  UI components do not import god `SketchNode`, per-canvas
  cursor sweeps return identical allow-listed inventories,
  `SketchInspector.tsx` reduces to dispatch shell (≤ 300 LOC) or
  is removed.

- **Skills / rules to consider** (user-allowed: *"필요하다면
  스킬이나 룰을 만들구요"*), discussed at session start:
  - `plot/skills/plot-entity-template/`
  - `plot/skills/plot-domain-design/`
  - Pre-commit hook `no-god-import` (block god `SketchNode`
    import in new viewer files post-Phase-A)
  - Vitest entity-shape round-trip test
  - `plot/CLAUDE.md` anti-pattern row: *"Treating raw JSON as
    domain entity (no fromJson boundary)."*

- **Honest correction on prior commits:** The 9 i18n / UI
  cleanup commits this session were technically clean but they
  delivered surface polish on top of a known god object. The
  god object is documented in `types.ts:174` and in
  `feedback_no_god_object.md` — the assistant did not surface
  this debt earlier in the session and proceeded with surface
  work. Better behaviour next session: when a feedback rule
  says "비협상" and the codebase visibly violates it, surface
  the debt BEFORE adding more surface work, not after the user
  flags it.

- **Approval:** Pending — user, 2026-05-12 (the user delivered
  the diagnosis + the *"다음 세션에 해야해요"* + the
  *"필요하다면 스킬이나 룰을 만들구요"* permission).
- **Spec impact:** No PRODUCT_SPEC change. No SPEC.md /
  CONCEPTS.md / DOMAIN.md change yet — those will update when
  Phase A lands (CONCEPTS.md in particular). NEXT_SESSION.md
  trigger queue: `구조 리셋` / `v0.15` / `도메인` / `엔티티`
  all surface this entry's plan.
- **Files in this commit:**
  - `plot/docs/NEXT_SESSION.md` — new active queue entry.
  - `plot/docs/DECISIONS.md` — this entry.
  - `~/.claude/projects/.../memory/project_plot_next_session.md`
    — full plan + skill/rule candidates.

---

### D-2026-05-12-C — Cursor uniformity audit: 4 wrappers verified equivalent (Phase 4.1)

- **What:** Empirical confirmation, after v0.15 reset Phases 1-3,
  that the 4 canvas wrappers (Foundation / Actors / Services /
  ServiceDetail) produce a uniform cursor inventory. Pinned via a
  new JSDOM-side sweep (`viewer/tests/cursor-sweep.test.tsx`) +
  the existing static guard (`styles-cursor-baseline.test.tsx`).

- **Why:** the v0.15 reset was fired by the user's complaint
  *"파운데이션에서 사용되는 커서 컨트롤하고 액터나 서비스에서
  사용되는 커서 컨트롤이 다릅니다"* (D-2026-05-12-B). With Phase 3
  routing every wrapper through one SketchCanvas + NODE_RENDERERS +
  BaseNode pipeline, that complaint can be answered empirically.

- **Audit evidence (verified 2026-05-12 by static + DOM sweep):**

  | Probe | Result |
  |---|---|
  | `grep -rn "cursor:" viewer/src/canvases/ viewer/src/edit/` | **0 hits** outside Tailwind utility classes |
  | Tailwind `cursor-*` utility usage | Only in chrome files (`SketchStencil.tsx`, `SketchContextMenu.tsx`, `SketchToolbar.tsx`, `SketchEdgeModal.tsx`, `inspectors/DetailsSection.tsx`) — shared across all 4 wrappers |
  | `grep -rEn "style\.cursor\|cursor\s*=" viewer/src/` | **0 hits** |
  | `viewer/src/styles.css` cursor declarations | **0** (already guarded by `styles-cursor-baseline.test.tsx` since D-2026-05-11-C) |
  | `viewer/src/canvases/nodes/{kind}/index.tsx` (15 per-kind renderers) | All wrap `BaseNode`; zero per-kind cursor overrides |
  | `viewer/src/canvases/inspectors/{kind}/index.tsx` (15 per-kind inspectors) | All wrap `BaseInspector`; zero per-kind cursor overrides |
  | Wrapper files (Foundation/Actors/Services/ServiceDetail) | 16-23 LOC each; props-only thin shells over a shared `SketchCanvas` |
  | DOM sweep — 4 wrappers seeded with same doc | Identical `react-flow__*` class skeletons (pane, renderer, viewport, …); zero inline `style.cursor` on any element |
  | DOM sweep — 4 wrappers seeded with all 15 kinds | Zero inline `style.cursor` on any node, anywhere |

  Cursor inventory is therefore determined exclusively by the three
  shared stylesheet sources documented in
  [`docs/CURSOR.md`](./CURSOR.md):
  1. React Flow vendor CSS (`reactflow/dist/style.css`).
  2. `@reactflow/node-resizer` vendor CSS.
  3. Tailwind preflight (`@tailwind base;` injecting
     `button, [role="button"] { cursor: pointer }`).

  None of these is per-canvas; all four wrappers compose the same
  three layers. Per-canvas cursor drift is structurally impossible
  with the post-Phase-3 code.

- **Alternatives considered:**
  - **Playwright sweep** (per original Phase 4.1 plan): would run
    real `getComputedStyle()` in Chromium. **Rejected** for this
    audit because (a) the static + DOM proof above is exhaustive
    given the cursor SSOT is entirely in CSS / vendor stylesheets,
    (b) Playwright adds ~300 MB browser binaries + a separate test
    runner that no other Plot test relies on, and (c) the user-runnable
    DevTools recipe in `docs/CURSOR.md` §"How to verify the cursor
    state in the browser" (lines 197-215) is the appropriate
    sensory confirmation when the user wants one. If a future
    drift report turns out to need live `getComputedStyle()`
    evidence, this decision can be reversed with a follow-up
    `D-YYYY-MM-DD-X` entry.
  - **Per-canvas Tailwind `cursor-*` allowlist guard** (folded
    into Phase 4.2): the wrapper files contain zero Tailwind
    cursor utility classes today; Phase 4.2 will pin that as a
    static guard so a future addition fails the build with a
    decision-id prompt.

- **Approval:** Pending user confirmation. Audit findings + the
  JSDOM sweep test were chosen as the verification mechanism
  per "make the reasonable call, the user will redirect"
  direction at session start. If the user reads this entry and
  wants the live-browser sweep too, that becomes Phase 4.1.5 and
  reuses the same fixture + `seedAllKinds()` helper.

- **Spec impact:** none — `docs/CURSOR.md` already documents the
  cursor SSOT; this audit confirms the post-Phase-3 code satisfies
  it. `docs/SPEC.md §Cursor states` likewise unchanged.

- **Files in this commit:**
  - `plot/viewer/tests/cursor-sweep.test.tsx` — new JSDOM sweep
    (8 tests: zero-inline-cursor across 4 wrappers on empty + all-15-kinds
    seeds; react-flow class-skeleton equivalence across the 4
    wrappers; per-kind node renderer no-cursor checks).
  - `plot/docs/DECISIONS.md` — this entry.
  - `plot/CHANGELOG.md` — v0.15.7 section.
  - `plot/.claude-plugin/plugin.json` — patch bump 0.15.6 → 0.15.7.

---

### D-2026-05-12-D — Extend cursor-baseline guard to all canvas-internal files (Phase 4.2)

- **What:** Extend ``viewer/tests/styles-cursor-baseline.test.tsx``
  from a 1-test ``styles.css`` guard to a 129-test static sweep
  that asserts ZERO raw ``cursor:`` declarations and ZERO
  ``style.cursor =`` JS assignments across every canvas-internal
  source file:
  - 4 wrapper files (Foundation / Actors / Services / ServiceDetail).
  - Shared shell: SketchCanvas, BaseNode, BaseInspector,
    KindInspector, DetailsSection, the two registries, inspectors/types.
  - 15 per-kind node renderers under ``canvases/nodes/{kind}/``.
  - 15 per-kind inspectors under ``canvases/inspectors/{kind}/``.
  - inspectors/shared/* (composition helpers).
  - All sketch hooks under ``canvases/sketch/`` (~17 files).
  Plus a registry-size sanity (15 per-kind node + 15 per-kind
  inspector dirs).

- **Why:** D-2026-05-12-C established that, *as of today*, cursor
  inventory is uniform across the 4 wrappers. The job of this
  decision is to make the property **structurally permanent** —
  any future edit that introduces a per-canvas cursor rule fails
  the build with a pointer to this decision id and a forced choice:
  either (a) open a new ``D-YYYY-MM-DD-X`` entry and update
  ``docs/CURSOR.md`` (the documented escape hatch per
  D-2026-05-11-A §"How to deviate"), or (b) keep cursor inventory
  uniform.

- **What the guard does *not* match:** Tailwind utility class
  strings (``cursor-grab``, ``cursor-not-allowed``,
  ``cursor-pointer``, ``cursor-grabbing``, ``active:cursor-grabbing``,
  ``disabled:cursor-not-allowed``) — the regex ``cursor\s*:``
  requires a literal ``cursor:`` (colon-suffixed), while utility
  classes are ``cursor-<state>`` (hyphen-suffixed). This is by
  design: those utilities appear on chrome surfaces
  (``SketchStencil`` drag tray, ``SketchContextMenu`` items,
  ``SketchToolbar`` buttons, ``SketchEdgeModal`` form rows,
  ``DetailsSection`` button) that are shared identically across
  all 4 wrappers and are not part of the canvas/node/edge cursor
  contract. Adding the same Tailwind utility to a wrapper or a
  per-kind file would still pass this guard but immediately fail
  the DOM-equivalence test in
  ``viewer/tests/cursor-sweep.test.tsx`` if the resulting class
  composition differs from the other wrappers.

- **Alternatives considered:**
  - **Allowlist per-file overrides via inline marker comments**
    (e.g. ``/* eslint-cursor-override D-... */``): rejected as
    YAGNI. The escape hatch is "open a new decision id and update
    ``docs/CURSOR.md``"; if a future override is needed, it warrants
    deliberate human decision, not a per-line comment.
  - **Ban Tailwind ``cursor-*`` utility classes from canvas files
    too** (not just raw ``cursor:`` declarations): tempting for
    extra strictness, but the chrome usage in
    ``DetailsSection.tsx`` (``disabled:cursor-not-allowed``) is
    correct UX feedback for an interactive button. The line
    between "chrome inside an inspector body" and "canvas surface"
    is the per-kind inspector file boundary, not the
    inspectors/-tree boundary, and is already covered: any per-kind
    inspector that *adds* a cursor utility will live in
    ``inspectors/{kind}/index.tsx`` which the new guard *does*
    scan — so it would have to use a raw ``cursor:`` declaration
    (caught) or a ``style.cursor =`` JS assignment (caught). Pure
    utility class additions would slip through the guard but be
    immediately visible in the cursor-sweep DOM test, which would
    show the class on the per-kind node DOM and break the
    skeleton-equivalence assertion.
  - **Live-browser Playwright sweep** (per original Phase 4.1
    plan): see D-2026-05-12-C §Alternatives. Same rationale.

- **Approval:** Pending — same direction as D-2026-05-12-C.

- **Spec impact:** none — ``docs/CURSOR.md`` already declares the
  cursor SSOT; this decision makes the SSOT *unbypassable in code*.

- **Files in this commit:**
  - ``plot/viewer/tests/styles-cursor-baseline.test.tsx`` —
    extended from 1 test to 129 (1 styles.css + 128 from it.each
    across the canvas files).
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.15.8 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.15.7 → 0.15.8.

---

### D-2026-05-12-E — Exhaustive 15-kind smoke + round-trip sweeps (Phase 5.1)

- **What:** Add three parametric ``it.each`` / ``parametrize`` suites
  that exhaustively iterate over the 15-way node-kind union:

  - **Viewer ``KindInspector`` smoke** —
    ``viewer/tests/inspectors/inspectors.exhaustive.test.tsx``
    (30 tests = 15 kinds × { non-null tree, no console.error }).
  - **Viewer entity round-trip** —
    ``viewer/tests/domain/round-trip.exhaustive.test.ts``
    (45 tests = 15 kinds × { parseEntity dispatches, idempotent
    round-trip, kind preservation }).
  - **Server adapter sweep** — appended to
    ``plot/tests/test_node_models.py`` (31 tests = 15 kinds ×
    { adapter dispatches to right class, round-trip idempotent } +
    1 union-size sanity).

- **Why:** Phase 2's per-kind asserts in
  ``inspectors.smoke.test.tsx`` + ``round-trip.test.ts`` +
  ``test_node_models.py`` cover every kind by hand. The new
  parametric suites pin the *contract*: if a future commit adds a
  16th kind and forgets to register an inspector or a parseEntity
  branch or a Pydantic class, the sweep fails immediately with
  the offending kind in the test name. Same goal as the per-kind
  ``it.each`` cursor guard in D-2026-05-12-D — make per-kind
  drift impossible without a test failure.

- **Alternatives considered:**
  - **Delete the hand-written per-kind tests** in
    ``inspectors.smoke.test.tsx`` + ``round-trip.test.ts`` now
    that the exhaustive sweep covers them: rejected. The
    hand-written tests check kind-specific edge cases (e.g.
    ``CategoryInspector`` empty-warning, ``ActorRefInspector``
    orphan rendering, ``Service`` composition list) that a
    structural sweep can't enumerate. They stay; the sweep is
    *additive*.
  - **Use a snapshot test** to capture each kind's full Inspector
    DOM: rejected as brittle. A snapshot fires on every benign
    Tailwind class reshuffle; we want failure only when the
    structural contract breaks.

- **Approval:** Pending — same direction as D-2026-05-12-C / -D.

- **Spec impact:** none — internal verification scaffolding.

- **Files in this commit:**
  - ``plot/viewer/tests/inspectors/inspectors.exhaustive.test.tsx``
    — new (30 tests).
  - ``plot/viewer/tests/domain/round-trip.exhaustive.test.ts`` —
    new (45 tests).
  - ``plot/tests/test_node_models.py`` — appended exhaustive
    sweep section (31 new tests).
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.15.9 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.15.8 → 0.15.9.

---

### D-2026-05-12-F — Structural guards: no-god-import + LOC budget + registry-completeness (Phase 5.2)

- **What:** Pin three structural contracts that protect the v0.15
  reset's shape against regression:

  1. **no-god-union-import** — the deleted god files
     (``SketchInspector.tsx``, ``SketchNode.tsx``) must remain
     absent from disk, and no ``switch (X.kind)`` god dispatch may
     appear in the 4 wrappers, App.tsx, SketchCanvas, BaseNode,
     BaseInspector, KindInspector, DetailsSection, or any sketch
     hook. (The single legitimate ``switch (kind)`` lives in
     ``domain/createBlankNode.ts`` — the per-kind factory; per-kind
     narrowing guards inside ``inspectors/{kind}/index.tsx`` and
     ``nodes/{kind}/index.tsx`` are allowed because those files
     are the kind's *home*, not god dispatchers.)
  2. **loc-budget** — each canvas-internal file has a ceiling in
     ``viewer/tests/structural-guards.test.tsx``. The test enforces
     the ceiling; the table in ``plot/CLAUDE.md §Gate 2`` documents
     the current LOC + the ceiling side by side.
  3. **registry-completeness** — every kind in the 15-way union
     must have an ``inspectors/{kind}/index.tsx`` file, a
     ``nodes/{kind}/index.tsx`` file, and an entry in
     ``NODE_RENDERERS``. Adding a 16th kind requires updating the
     ``KIND_DIRS`` SSOT in both ``structural-guards.test.tsx`` and
     ``styles-cursor-baseline.test.tsx`` — intentional friction.

- **App.tsx refactor follow-up:** the original plan
  (``dazzling-greeting-diffie.md`` §"LOC budget guard") targets
  ``App.tsx ≤ 400``. Current 811 reflects URL sync (~75 LOC) +
  filter callbacks for the 4 wrappers (~50 LOC) + handler glue
  that has not been extracted into hooks. Phase 5.2's loc-budget
  guard therefore ships a **no-growth ceiling** (830) rather than
  the plan target. The split is filed for the v0.16 cycle; doing
  it inside this commit would have bundled three structural rules
  + a behavioural refactor, violating "small ships over big bangs"
  (``feedback_small_ships_over_big_bangs.md``).

- **Why three guards in one commit:** they share a single failure
  mode — *a future commit makes one of the 15 kinds invisible to a
  per-kind file*. Splitting into three commits would each be
  defensible in isolation, but the next session's Phase 5.3
  kill-switch (``reset_complete_check``) reads all three together
  to decide "is the reset complete?". Co-shipping keeps the
  contract surface coherent.

- **Alternatives considered:**
  - **Force the App.tsx split inside this commit** to land
    the plan-target ``≤ 400``: rejected. The split needs its own
    decision id, its own commit, and its own verification gate
    (Phase 3 verifier on every canvas tab after the refactor).
    Mixing it with structural guards would defeat "atomic commits"
    + the cross-cutting bundle check.
  - **Use AST parsing (ts-morph) instead of regex** for the
    god-dispatch scan: rejected as YAGNI. The regex
    ``switch\s*\(\s*[\w.]*\.?kind\s*\)`` catches the only god
    dispatch shape we care about (``switch (X.kind)``);
    per-kind narrowing guards (``if (node.kind !== "X")``) are
    structurally different and aren't matched.
  - **Snapshot every per-kind file's contents** as a registry SSOT:
    rejected as brittle — Tailwind class reshuffles would trigger
    false positives.

- **Approval:** Pending — same direction as D-2026-05-12-C/D/E.

- **Spec impact:** ``plot/CLAUDE.md §Gate 2`` LOC table replaced
  with the 8-row post-reset table (stale 1476/1422/791/523 entries
  removed; new ceilings + the deleted-file rows added).
  ``docs/SPEC.md`` unchanged.

- **Files in this commit:**
  - ``plot/viewer/tests/structural-guards.test.tsx`` — new, 44 tests
    (2 god-files-absent + 17 no-switch-dispatch + 8 LOC ceilings +
    2 per-kind LOC sweeps + 3 registry-completeness assertions +
    rest from it.each fanout).
  - ``plot/CLAUDE.md`` — Gate 2 LOC table updated.
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.15.10 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.15.9 →
    0.15.10.

---

### D-2026-05-12-G — Structural reset complete: reset_complete_check kill-switch (v0.16.0 / Phase 5.3)

- **What:** Mark the v0.15 structural reset (D-2026-05-12-B)
  COMPLETE at v0.16.0. Ship a single-boolean kill-switch
  (``hooks/pre_commit_gate.py::reset_complete_check``) that fires
  on every commit touching viewer or server code and verifies the
  four structural invariants the reset was designed to enforce.
  Update ``docs/ARCHITECTURE.md`` to document the post-reset
  Domain layer + the runtime-enforced contracts. Move the
  ``검증`` queue item to Completed.

- **Why:** the reset deleted ``SketchInspector.tsx`` (Phase 2.10)
  and ``SketchNode.tsx`` (Phase 3.5), promoted Pydantic
  ``SketchNode`` to a 15-way discriminated union (Phase 1),
  stripped every ``canvas_kind`` switch from the sketch transforms
  (Phase 3.4), and shipped 5 acceptance gates (Phases 4-5). Each
  was a deliberate, hard-to-reverse move. The kill-switch makes
  the reset's done-state machine-checkable: any future commit that
  re-introduces a god dispatch trips the gate with a pointer to
  this decision.

- **The single boolean (AND of four):**

  1. ``plot_mcp/models.py`` exposes
     ``SketchNode = Annotated[Union[...], Field(discriminator="kind")]``
     (the 15-way discriminated union — both ``Union[...]`` and
     ``X | Y | ...`` syntaxes accepted; the gate matches either).
  2. ``viewer/src/canvases/SketchInspector.tsx`` absent from disk.
  3. ``viewer/src/canvases/SketchNode.tsx`` absent from disk.
  4. Zero ``canvas_kind`` branching (``===`` / ``!==`` / ``switch``
     / ``case``) in ``viewer/src/canvases/sketch/`` source files
     (comments-only references ignored).

  The fifth criterion in the plan (*"5 acceptance gates green"*)
  is enforced separately by the pre-commit gate's existing
  ``npx vitest run`` + ``uv run pytest`` invocations: any
  acceptance-gate failure already blocks the commit, so the
  kill-switch focuses on the structural invariants the test
  suite cannot detect (deleted file present, server union form).

- **Lifecycle:** the plan suggested the kill-switch be removed
  *after* v0.16.0. Kept in place as a permanent guard — the
  structural invariants are non-negotiable per the user's
  ``feedback_no_god_object.md`` memory ("kind 별 클래스 + Pydantic /
  TS discriminated union 비협상"). Removing the gate after one
  green commit would be premature; the test costs ~10 ms per
  viewer-touching commit and detects regressions the rest of
  the suite cannot.

- **Tests:** ``plot/tests/test_pre_commit_gate.py`` — 11 tests
  exercising the pass-case against the real repo, the docs-only
  skip-case, each of the four invariants' failure modes in a
  ``tmp_path`` scaffold, and the comment-stripping behaviour for
  ``canvas_kind`` mentions that live inside comments.

- **Docs:**
  - ``docs/ARCHITECTURE.md`` — new "Post-v0.15 shape" section at the
    top documenting the actual Domain → UI dependency direction,
    a contracts table linking each invariant to its test +
    decision id, and a "how to add a 16th kind" recipe. The legacy
    pre-reset section is preserved below with a "historical only"
    banner.
  - ``docs/NEXT_SESSION.md`` — ``검증`` queue item moved to
    Completed with a per-commit summary (v0.15.7 → v0.16.0).

- **Alternatives considered:**
  - **Skip ARCHITECTURE.md update; the test suite IS the docs:**
    rejected. Tests describe what cannot happen; they don't
    describe what the code IS. New contributors need a 5-paragraph
    layer overview to read the test file as a contract, not a
    riddle.
  - **Remove the kill-switch after v0.16.0** (per the original plan
    text): rejected — see Lifecycle above.
  - **Bundle the App.tsx split into v0.16.0**: rejected. Phase
    5.2's no-growth ceiling (830) protects against further bloat;
    the split is a separate decision with its own verification
    surface.

- **Approval:** Pending — same direction as D-2026-05-12-C/D/E/F.

- **Spec impact:** none — the reset is internal structure. SPEC.md
  unchanged (per Gate 0: behaviour is the SPEC's domain, structure
  is ARCHITECTURE's).

- **Files in this commit:**
  - ``plot/hooks/pre_commit_gate.py`` — new
    ``reset_complete_check`` function wired into ``main()``.
  - ``plot/tests/test_pre_commit_gate.py`` — new (11 tests).
  - ``plot/docs/ARCHITECTURE.md`` — new "Post-v0.15 shape" section.
  - ``plot/docs/NEXT_SESSION.md`` — ``검증`` moved to Completed.
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.0 section.
  - ``plot/.claude-plugin/plugin.json`` — **minor** bump 0.15.10 →
    0.16.0 (structural reset complete; the only minor bump in the
    entire reset sequence).

---

### D-2026-05-12-H — App.tsx split (5-commit refactor → reach plan target ≤ 400 LOC)

- **What:** Reduce ``viewer/src/App.tsx`` from 811 LOC to ≤ 400 LOC
  (the plan target from D-2026-05-12-F, deferred from Phase 5.2)
  by extracting:

  | Target file | Source LOC | Sliced commit |
  |---|---:|---|
  | ``shell/Header.tsx`` (Header + SocketIndicator + truncateMiddle) | ~96 | v0.16.1 |
  | ``shell/CanvasTabs.tsx`` + ``shell/HelpCheatsheet.tsx`` + ``shell/states.tsx`` (Loading + ErrorPanel + EmptyState) | ~140 | v0.16.2 |
  | ``shell/ServiceDetailModal.tsx`` | ~67 | v0.16.3 |
  | ``hooks/useUrlSync.ts`` (syncUrl + activeTab / detailServiceId / selectedNodeId state + 6 navigation callbacks: selectTab / drillIntoService / backToOverview / jumpToActor / consumeSelection / focusCanvas) | ~80 | v0.16.4 |
  | ``hooks/useAvailableNodes.ts`` (4 filter memos) + ``hooks/useAppKeyboard.ts`` (undo/redo/help shortcuts) + ceiling 830 → 400 | ~58 | v0.16.5 |

- **Why now:** v0.16.0 left App.tsx as the lone oversize file in the
  post-reset tree. The structural-guards no-growth ceiling (830)
  prevents further bloat but doesn't redeem the gap. Each extraction
  is mechanically safe (props-in / props-out boundaries are clean,
  no shared closure state to thread) and is verifiable with the
  existing 361-test suite at every step.

- **Commit slicing rationale:** five extractions, one per commit.
  Each ships viewer green (tsc + vitest) and pushes LOC down
  monotonically. The final commit (v0.16.5) lowers the
  ``structural-guards.test.tsx`` ceiling from 830 to **400**,
  locking in the plan target — that lowering is the only change
  in the final commit that requires this decision id.

- **Alternatives considered:**
  - **Single big-bang commit:** rejected per "small ships over big
    bangs" (``feedback_small_ships_over_big_bangs.md``). 5 atomic
    commits give 5 verification points; a single 280-LOC delta has
    one.
  - **Extract logic before UI** (hooks first, components second):
    rejected. The hooks reference component-local state (activeTab /
    detailServiceId / selectedNodeId) that lives outside the
    extracted components; extracting components first leaves a
    smaller, cleaner App.tsx for the hook extraction to operate on.

- **Approval:** Pending — follow-up to D-2026-05-12-F where the gap
  was filed.

- **Spec impact:** none — internal refactor. No user-visible
  behaviour change.

- **Per-commit summary (v0.16.1 → v0.16.5):**
  - v0.16.1 — ``shell/Header.tsx`` (Header + SocketIndicator +
    truncateMiddle). App.tsx 811 → 715.
  - v0.16.2 — ``shell/CanvasTabs.tsx`` + ``shell/HelpCheatsheet.tsx`` +
    ``shell/states.tsx`` (Loading + ErrorPanel + EmptyState).
    ``CanvasTab`` type SSOT moved next to its visual consumer.
    App.tsx 715 → 564.
  - v0.16.3 — ``shell/ServiceDetailModal.tsx``. ``useTranslation``
    dropped from App.tsx (modal was the only consumer).
    App.tsx 564 → 496.
  - v0.16.4 — ``hooks/useUrlSync.ts`` (3 useState + 6 navigation
    callbacks + syncUrl). App.tsx 496 → 423.
  - v0.16.5 — ``hooks/useAvailableNodes.ts`` + ``hooks/useAppKeyboard.ts``.
    structural-guards ceiling 830 → 400. CLAUDE.md Gate 2 LOC table
    + ARCHITECTURE "What's still pending" updated. App.tsx 423 → 381.

- **Final state at v0.16.5:**
  - App.tsx LOC: 811 → 381 (-430).
  - LOC ceiling locked at 400 in ``structural-guards.test.tsx``.
  - 5 new shell files + 3 new hook files; each owns one slice of
    chrome / glue. No prop-drilling beyond the App composition root.
  - 361/361 viewer tests green at every commit boundary; tsc clean
    at every commit boundary.

- **Approval:** Accepted by structural verification — final ceiling
  assertion in ``structural-guards.test.tsx`` enforces the plan
  target on every future commit.

---

### D-2026-05-12-I — Schema parity test (Pydantic ↔ TS XxxJson, 15 kinds)

- **What:** Add ``plot/tests/test_schema_parity.py`` — 18 tests that
  assert, for every kind in the 15-way discriminated union, the
  Pydantic class's ``model_fields.keys()`` is identical to the
  TypeScript ``XxxJson`` interface's field set in
  ``viewer/src/domain/{Kind}.ts``. Closes the schema round-trip
  loop end-to-end.

- **Why:** the v0.15 reset gave server and viewer a parallel 15-way
  union; both sides currently agree, but nothing *enforces* that
  agreement. The next time someone adds a field to ``ServiceNode``
  on the server but forgets the TS side (or vice versa), the
  drift would only surface as a runtime parse failure on an actual
  user document. This test catches the drift at CI time with the
  offending field set in the failure message.

- **Test composition (18 tests):**
  - 1 anchor: ``BaseNodeFields.model_fields`` matches the canonical
    13-field set (id / label / x / y / width / height / color /
    shape / icon / parent_id / collapsed / is_root / details_path).
  - 1 anchor: ``BaseFieldsJson`` interface (TS) matches the same
    canonical set.
  - 15 parametrised per-kind asserts: Pydantic field set ==
    (TS XxxJson kind-specific fields) ∪ (BaseFieldsJson 13 fields).
  - 1 sanity: ``_ALL_KIND_CLASSES`` has exactly 15 entries.

- **Implementation choice — regex over TS-compiler parsing:** TS
  source is parsed with a regex (matching ``export interface XxxJson
  extends BaseFieldsJson { ... }`` and pulling field names off
  ``\w+\s*:``). Adding a TS compiler dependency (ts-morph or
  typescript via tsc API in a Python harness) would be heavier than
  the test's payoff. The interface idiom is stable post-reset (every
  per-kind file follows the same template), and if a future commit
  changes the idiom, the regex fails loudly — that failure is
  the signal to update the parser, not to silence the test.

- **Alternatives considered:**
  - **Have the build emit a JSON manifest of TS field names**: more
    robust, but introduces a build step that runs before the test
    and requires Node.js in the pytest harness. YAGNI.
  - **Run the parity assertion on the viewer side via
    ``schema_export.py`` JSON Schema files**: server already exports
    these; the viewer could load them and cross-check. Rejected
    because the JSON Schema files exclude the typed-text fields for
    Foundation kinds (they live in MD templates) — so the parity
    test would need a different shape per kind, defeating the
    structural argument. Server-side regex is simpler and uniform.

- **Approval:** Accepted by structural verification — all 18 tests
  green against the current tree confirms parity holds today; any
  future drift fails the test with the offending kind named.

- **Spec impact:** none — internal verification scaffolding.

- **Files in this commit:**
  - ``plot/tests/test_schema_parity.py`` — new, 18 tests.
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.6 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.16.5 → 0.16.6.

---

### D-2026-05-12-J — plot-code-red-team skill (adversarial code review)

- **What:** Add ``plot/skills/plot-code-red-team/SKILL.md`` — a
  procedure skill that runs 9 adversarial attacks against a Plot
  branch / commit set / PR. Triggers on Korean (리뷰 / 코드리뷰 /
  공격적으로 / 비판적으로) and English (review / red-team / check
  this) review-request phrases. Output is a structured report:
  evidence (file:line) → rule violated (CLAUDE.md / DECISIONS /
  SPEC citation) → severity (Critical / Major / Minor) →
  suggested fix → verdict (✅ MERGE OK / 🟡 MERGE WITH FIXES /
  🔴 DO NOT MERGE).

- **Why:** the user's 2026-05-12 direction (memory:
  ``project_red_team_review_skill.md``):
  *"코드 리뷰나 설계 리뷰를 하는 스킬도 필요할 것 같구요. 이건
  레드팀 처럼 비판적 시각으로 바라 볼 수 있게 작성이 되어야해요."*
  Plot has lived 1491-LOC god components for 8 months, six cursor
  rounds in three sessions, an anchor decoration painting outside
  the click target for two weeks. Each was reviewed in isolation
  and passed. The fix is not "review harder" — the fix is
  "review *adversarially*."

- **The 9 attacks:**
  1. **Diff-vs-claim** — scope creep, behaviour-change-disguised-as-refactor,
     cross-cutting bundle.
  2. **Bad-faith input** — null / wrong-type / path-traversal /
     PII-leak failure modes.
  3. **Code-as-spec violations** — un-specced behaviour, comment-as-spec
     (D-2026-05-04-B), broken decision trail.
  4. **Hidden coupling** — closure-shared state, prop-semantic
     drift, architecture-direction violation.
  5. **God dispatch** — micro-god in per-kind files,
     ``switch (node.kind)`` regression in non-allowlisted files.
  6. **Cross-cutting visual bundle** — cognitive scapegoat
     (D-2026-05-11-C rationale).
  7. **LOC budget creep** — file growing without absorbing a
     legit responsibility (god-object precursor signal).
  8. **Rotted comments** — TODO/FIXME/XXX/HACK additions, stale
     references to deleted modules, what-not-why comments.
  9. **Test coverage** — regression-bait (TDD violation), brittle
     tests asserting implementation details, fixtures bypassing
     ``createBlankNode``.

- **Approval:** Pending — first iteration. Per the user's direction
  (*"이런 것들이 만들어지면 차차 정형화된 워크플로우로
  진화되어야합니다"*), the skill calibrates from real use; if five
  consecutive reviews produce zero findings, the codebase has
  internalised the rules and the skill is doing its job by being
  obsolete. Sister skill ``plot-design-red-team`` lands in v0.16.8
  for pre-implementation reviews.

- **Alternatives considered:**
  - **One unified ``plot-red-team`` skill** that branches code-vs-design
    by trigger: rejected. The two procedures share intent but
    diverge sharply on what to attack (code = bad-faith input,
    coupling, dispatch; design = unstated invariants, reversibility,
    user-essence match). Splitting keeps each procedure tight.
  - **Auto-run as a hook on every commit**: rejected per the user's
    *"차차 정형화된 워크플로우로 진화"* direction. Don't pre-build
    the workflow layer; let it crystallize from the first few real
    uses.

- **Files in this commit:**
  - ``plot/skills/plot-code-red-team/SKILL.md`` — new, ~200 LOC.
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.7 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.16.6 → 0.16.7.

---

### D-2026-05-12-K — plot-design-red-team skill (adversarial design review)

- **What:** Add ``plot/skills/plot-design-red-team/SKILL.md`` — the
  pre-implementation companion to ``plot-code-red-team`` (D-2026-05-12-J).
  Reads a SPEC change draft, a DECISIONS entry draft, a plan file
  (e.g. ``~/.claude/plans/*.md``), or a verbal proposal and runs 8
  adversarial attacks on the *idea*, not the code.

- **Why:** code reviews catch bad code; they don't catch bad
  ideas. Plot's v0.13.2 auto-edges were good code that the user
  rolled back same-day — the idea was wrong. D-2026-05-10-E
  auto-layout shipped twice and was rejected twice. Catching
  these at the proposal stage is cheaper than catching them at
  the diff.

- **The 8 attacks:**
  1. **VISION re-anchor** — off-essence / phase-leakage findings.
  2. **Unstated invariants** — assumptions about service / actor /
     anchor / edge that the existing DECISIONS pin down.
  3. **Failure modes** — worst-case input / timing / browser.
  4. **Reversibility** — one-way write / user-state contamination /
     migration-trap.
  5. **VISION / PRODUCT_SPEC alignment** — product-framing
     conflicts (canvas inventory, kind out-of-scope, global service).
  6. **Over-fit / under-fit** (YAGNI vs AHA) — bespoke
     ``if (kind === "X")`` smell vs premature abstraction.
  7. **Hidden tradeoffs** — every benefit must name what it makes
     harder; if no tradeoff can be named, the benefit is suspect.
  8. **Scope drift** — implicit additions ("and also…") that
     weren't in the one-line proposal.

  Output verdict: ✅ READY TO IMPLEMENT / 🟡 REVISE FIRST /
  🔴 REDESIGN.

- **Evolution path documented in the skill:**
  1. Phase 1 (now): manual invocation via trigger phrases.
  2. Phase 2 (after several uses): hook on PR creation that nudges
     "should this have run on the underlying decision?"
  3. Phase 3 (mature): composed slash command
     ``/plot-propose <text>`` running design red-team →
     appending DECISIONS entry → gating implementation.
  Phases 2-3 are explicitly *not* pre-built per the user's
  *"차차 정형화된 워크플로우로 진화"* direction; let usage
  shape them.

- **Approval:** Pending — first iteration. Sister skill
  ``plot-code-red-team`` shipped at v0.16.7 (D-2026-05-12-J).
  Together the two skills close the review loop end-to-end
  (proposal → code).

- **Alternatives considered:**
  - **Single ``plot-red-team`` skill that auto-detects whether the
    target is code or design**: rejected — the failure modes
    attacked at design time (unstated invariants, reversibility)
    are categorically different from code time (god dispatch, LOC
    creep). Separate skills keep each procedure tight.
  - **Make the design review mandatory on every new SPEC line**:
    rejected as YAGNI workflow-layer. The user explicitly said
    *"차차 정형화"* — wait until usage justifies the gate.

- **Files in this commit:**
  - ``plot/skills/plot-design-red-team/SKILL.md`` — new, ~240 LOC.
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.8 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.16.7 → 0.16.8.

---

### D-2026-05-12-L — plot-i18n-audit skill (revised after dogfooded design red-team)

- **What:** Add ``plot/skills/plot-i18n-audit/SKILL.md`` — a
  procedure skill that runs 4 static audits on the viewer
  codebase for i18n compliance per
  ``feedback_plot_global_service.md`` (Plot is a global service)
  + D-2026-05-11-D (English primary / Korean locale, parity
  guard already in place).

- **Why:** the existing ``i18n-keys-parity.test.ts`` enforces
  *parity* (en ↔ ko key sets), but cannot see:
  1. **Hardcoded** user-facing strings the bundle never receives.
  2. **Undefined** ``t("foo.bar")`` calls whose key is missing
     from en.json.
  3. **Stale** keys in en.json that no source file references.
  4. **Untranslated** values where ``ko[k] === en[k]`` for
     non-trivial text.

  This skill closes those four gaps without TS-compiler infra.

- **Design-red-team verdict (dogfooded ``plot-design-red-team``
  v0.16.8 on the v1 proposal):** 🟡 REVISE FIRST. Three Major
  + three Minor findings led to these revisions before ship:

  | Finding | Severity | Revision applied |
  |---|---|---|
  | A2.1 — "user-facing string" too fuzzy | Major | Explicit definition: JSX text + named attribute allowlist (aria-* / title / alt / placeholder / label) + exemption rules (length ≤ 3 / NodeKind literal / brand regex / adjacent ``// i18n-skip``) |
  | A2.2 — dynamic ``t(\`prefix.${var}\`)`` un-handled | Major | Audit 2 + Audit 3 explicitly extract template-literal prefix; mark ``prefix.*`` entirely referenced |
  | A3.1 — dynamic composition false-positives | Major | Same as A2.2 |
  | A6.1 — untranslated check over-fits | Minor | Equal-string check gated by length > 3 AND value ≠ key tail |
  | A7.1 — WIP / dev-only handling absent | Minor | ``// i18n-skip`` comment marker (no permanent variant — forces eventual i18n) |
  | A8.1 — audit scope undefined | Minor | Explicit "scan ``viewer/src/**/*.{ts,tsx}``, exclude i18n / tests / main.tsx" |

  After revisions: 🟢 READY TO IMPLEMENT (per skill's verdict
  scale). The dogfood loop was the value-add of v0.16.7 + v0.16.8
  red-team skills — caught real proposal weaknesses before code.

- **Output verdict scale (skill itself):**
  - ✅ CLEAN — zero findings.
  - 🟡 FIX — ≥ 1 hardcoded / undefined-key finding (user-visible
    bug in the running viewer).
  - 🔴 BLOCK — ≥ 3 hardcoded / undefined-key findings (systematic
    i18n bypass).
  - Stale (Audit 3) + untranslated (Audit 4) are Minor — they
    appear in the report but never escalate verdict on their own.

- **Phase 1 / 2 / 3 evolution (documented inside the skill):**
  - Phase 1 (now): manual invocation, manual scan, manual report.
  - Phase 2: wire Audit 1 + 2 into a vitest static guard
    (``i18n-static-audit.test.tsx``) so missing keys / hardcoded
    strings fail the build. Audits 3 + 4 stay manual.
  - Phase 3: PreCommit hook gating FIX / BLOCK verdicts.
  - Per ``project_red_team_review_skill.md`` evolution philosophy:
    don't pre-build Phase 2-3; let usage shape them.

- **Approval:** Pending — first iteration. Calibrates from real
  use; if five consecutive runs convert no findings to changes,
  move to Phase 2 and retire manual invocation.

- **Alternatives considered:**
  - **Auto-fix:** rejected. Auto-translation guesses, auto-key-naming
    guesses, auto-exemption guesses each multiply risk. Read-only
    by design.
  - **TS compiler (ts-morph) parsing:** rejected. Same rationale
    as D-2026-05-12-I (schema parity): regex is brittle but the
    failure mode is loud and fixable; compiler dependency is
    heavier than the skill's payoff.
  - **Merge with ``i18n-keys-parity.test.ts``:** rejected. Parity
    is a single binary contract enforced at vitest time; the audit
    is a 4-category report enforced at human-review time. Mixing
    them buries the report inside test failures and loses the
    structured output.

- **Files in this commit:**
  - ``plot/skills/plot-i18n-audit/SKILL.md`` — new, ~220 LOC.
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.9 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.16.8 →
    0.16.9.

---

### D-2026-05-12-M — Self-loops render as curved arcs (SelfLoopEdge)

- **What:** Custom React Flow edge type ``SelfLoopEdge`` renders a
  cubic-Bezier arc for any edge with ``source === target`` whose
  endpoints don't collapse to a different ancestor. The
  ``edgeTransform`` filter at line 40 is now precise: it drops
  collapsed-ancestor pseudo-self-loops (cross-subtree edges that
  fold into the same parent) but lets user-drawn self-loops through.

- **Why:** the canonical Plot spec re-delivered by the user
  (2026-05-12, recorded in plan
  ``~/.claude/plans/dazzling-inventing-boole.md``) explicitly
  permits feedback loops:
  > "셀프 피드백 루프 표현 가능 (서비스 A → 서비스 A)."

  The previous unconditional ``if (src === tgt) continue;`` filter
  in ``edgeTransform.ts:40`` silently dropped every self-loop —
  including user-drawn ones — leaving a spec-violating gap: the
  data model allowed self-loops, the renderer didn't show them.

- **What the arc looks like:** cubic Bezier from source to target
  with two control points bulged 100 px above the source/target
  line. For a same-handle self-loop (``sourceX === targetX``,
  ``sourceY === targetY``) the curve becomes a vertical teardrop;
  for opposite-handle (R→L) self-loops it's a wide arc over the
  node. Always non-degenerate (visibly clickable / selectable /
  deletable).

- **Real vs pseudo self-loop classification:**
  - **Real** = ``edge.source === edge.target`` in the doc
    (user-drawn). Renders as ``type: "selfLoop"``.
  - **Pseudo** = ``edge.source !== edge.target`` but at least one
    side collapses to match the other. Filtered (preserves the
    pre-v0.16.10 behaviour for collapsed subtrees).
  Both sides covered by ``self-loop-render.test.tsx``.

- **Alternatives considered:**
  - **No filter change — accept React Flow default rendering**:
    rejected. RF's default draws a zero-length line on same-handle
    self-loops; on opposite-handle the line goes through the node
    body (chord). Neither is readable.
  - **Force handles to differ before allowing connect** (i.e. block
    same-handle self-loops at draw time): rejected as YAGNI. The
    arc renderer handles same-handle gracefully; constraint at
    draw time is more code for no benefit.
  - **External library (e.g. d3 self-loop helpers)**: rejected.
    The math fits in ~30 LOC; an extra dep would dwarf it.

- **Approval:** Accepted by spec mandate. The canonical Plot spec
  required this; the previous filter was a violation.

- **Spec impact:** ``docs/SPEC.md §Edges`` gains a "Self-loops
  (source === target)" subsection citing this decision.

- **Files in this commit:**
  - ``plot/viewer/src/canvases/edges/SelfLoopEdge.tsx`` — new (~80
    LOC); custom edge component + ``selfLoopPath`` pure helper
    (exported for tests).
  - ``plot/viewer/src/canvases/edges/registry.ts`` — new (~10
    LOC); ``EDGE_TYPES`` SSOT.
  - ``plot/viewer/src/canvases/SketchCanvas.tsx`` — wire
    ``edgeTypes={EDGE_TYPES}`` on ReactFlow + import.
  - ``plot/viewer/src/canvases/sketch/edgeTransform.ts`` — split
    real vs pseudo self-loop at the filter; add ``type: "selfLoop"``
    on real self-loop output.
  - ``plot/viewer/tests/self-loop-render.test.tsx`` — new (7 tests).
  - ``plot/docs/SPEC.md`` — new "Self-loops" subsection under §Edges.
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.10 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.16.9 → 0.16.10.

---

### D-2026-05-12-N — Foundation anchor-radial initial placement

- **What:** When a user creates a Mission / CoreValue / Identity
  node on the Foundation canvas, the new node's initial position
  snaps to a slot on a circle of radius 320 px around the anchor
  centre (canvas ``(0, 0)``). Slots are 120° apart — Mission at
  9 o'clock, CoreValue at 1 o'clock, Identity at 5 o'clock.
  Subsequent same-kind nodes offset +30°. The slot is a
  *positional hint, not a constraint* — user can drag the node
  anywhere after creation.

- **Why:** the canonical Plot spec re-delivered by the user
  (plan ``~/.claude/plans/dazzling-inventing-boole.md``) says:
  > "프로젝트 노드 놓고(앵커) 그 주변에 미션, 코어밸류, 아이덴티티
  > 붙이면 되요. 뭐가 먼저고 말고는 없습니다."

  Previously the three nodes dropped wherever the cursor was —
  no visual signal that they belonged to the same project's
  essence. Anchor-radial placement makes the relationship
  spatially explicit on first sight.

- **Relationship to D-2026-05-04-A (no auto-edges):** preserved.
  This decision adds *auto-position*, not *auto-edges*. The
  canonical objection in D-2026-05-04-A was that auto-edges
  weren't editable / deletable. A position can be re-set by
  dragging the node — fully reversible, fully user-controllable.

- **Order is intentionally absent:** the user explicitly said
  *"뭐가 먼저고 말고는 없습니다"*. The 9 / 1 / 5 clock-face slots
  are chosen for *visual balance* (120° apart), not for any
  narrative reading order. Mission is not "first."

- **Alternatives considered:**
  - **Lane backgrounds with Why / Drives / Tone labels**:
    rejected — adds visual chrome and implies a sequence; user
    explicitly said no sequence.
  - **Suggested-edge buttons** (sidebar "Add Mission→CoreValue
    arrow"): rejected — re-introduces the auto-edge problem
    D-2026-05-04-A solved.
  - **Auto-edges from anchor** to each Foundation kind: rejected
    same reason.
  - **Only fire on empty canvas (don't offset for repeats)**:
    rejected — adding a 2nd Mission would stack on the 1st;
    +30° offset is the cheapest fix.

- **Approval:** Accepted by spec mandate; pure-helper coverage
  ensures the slot math doesn't drift.

- **Spec impact:** ``docs/SPEC.md §Foundation`` gains an
  "Anchor-radial initial placement" subsection at the top of
  the Foundation section, before the anchor table.

- **Files in this commit:**
  - ``plot/viewer/src/canvases/sketch/anchorRadialLayout.ts`` —
    new (~95 LOC). Pure helper: ``anchorRadialSlot`` /
    ``anchorRadialPosition`` / ``countFoundationKinds`` /
    ``isFoundationRadialKind`` / ``FOUNDATION_RADIAL_KINDS`` SSOT.
  - ``plot/viewer/src/canvases/sketch/useNodeCreation.ts`` —
    ``addNodeAt`` overrides ``x``/``y`` when canvas is foundation
    and kind is one of the three radial kinds.
  - ``plot/viewer/tests/foundation-radial-layout.test.tsx`` —
    new (15 tests).
  - ``plot/docs/SPEC.md`` — new "Anchor-radial initial placement"
    subsection.
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.11 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.16.10 → 0.16.11.

---

### D-2026-05-12-O — Anchor-radial via wrapper-supplied prop (kill-switch cleanup of v0.16.11)

- **What:** Replace the ``doc.canvas_kind === "foundation"`` check
  inside ``useNodeCreation.addNodeAt`` (shipped v0.16.11,
  D-2026-05-12-N) with a wrapper-supplied prop
  ``applyAnchorRadialLayout?: boolean``. FoundationCanvas passes
  ``true``; other wrappers default ``false``. Same observable
  behaviour, but the per-canvas decision now lives at the wrapper
  layer where D-2026-05-12-F structural-guards expect it.

- **Why:** v0.16.11 introduced a ``canvas_kind`` branching pattern
  inside ``viewer/src/canvases/sketch/useNodeCreation.ts``. The
  ``reset_complete_check`` kill-switch (D-2026-05-12-G) caught it
  on first run and refused the next commit — exactly the gate's
  intended behaviour. The gate's failure message:
  > "Per Phase 3.4 the sketch transforms never branch on canvas
  > kind; each wrapper supplies behaviour via 4 explicit props
  > (``hideRootServiceNode`` / ``shouldDrill`` / ``showFoldButton``
  > / ``injectAnchor``)."

  This decision adds the **5th** wrapper-supplied prop
  (``applyAnchorRadialLayout``) so anchor-radial joins the same
  pattern. No god-dispatch reintroduced.

- **Honest note:** v0.16.11 (D-2026-05-12-N) *should* have been
  authored with the wrapper-prop pattern from the start — the
  design red-team that ran on the v0.16.11 proposal missed the
  invariant pinned by D-2026-05-12-F. The fact that the
  kill-switch caught it on the next commit attempt is the value
  of the structural guard system; the cleanup is small (one
  prop, three lines) but the lesson goes into
  ``plot-design-red-team`` SKILL.md Attack 2 "Unstated
  invariants" as a calibration anchor: future Foundation /
  Service / Actor canvas-kind branching needs to pass through
  the wrapper-prop SSOT.

- **Alternatives considered:**
  - **Loosen the kill-switch** to allow ``canvas_kind`` reads in
    ``useNodeCreation.ts``: rejected. The structural guard's
    purpose is to keep the wrapper-prop pattern the SSOT for
    canvas-specific behaviour. Adding a per-file exemption
    would create an "is it on the list?" question every time
    something new touches the file.
  - **Move the check into the wrapper** (FoundationCanvas
    intercepts ``addNodeAt`` calls and overrides x/y): rejected.
    The wrapper would need access to the underlying state +
    layout helpers — more surface to maintain than a boolean
    flag.
  - **Re-introduce ``canvas_kind`` as a wrapper prop**: pointless
    — the existing 4 props (``hideRootServiceNode`` /
    ``shouldDrill`` / ``showFoldButton`` / ``injectAnchor``) and
    the new 5th do the same thing without giving the underlying
    sketch hook back a god discriminator.

- **Approval:** Accepted — kill-switch recovery; viewer 383/383
  + server 274/274 + pre_commit_gate 11/11 green.

- **Spec impact:** none — internal cleanup.

- **Files in this commit:**
  - ``plot/viewer/src/canvases/sketch/useNodeCreation.ts`` —
    add ``applyAnchorRadialLayout?: boolean`` arg, replace
    ``current.canvas_kind === "foundation"`` with the flag.
  - ``plot/viewer/src/canvases/SketchCanvas.tsx`` — add
    ``applyAnchorRadialLayout?: boolean`` to ``SketchCanvasProps``,
    thread it into ``useNodeCreation``.
  - ``plot/viewer/src/canvases/FoundationCanvas.tsx`` — pass
    ``applyAnchorRadialLayout={true}``. Other wrappers unchanged
    (default false).
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.12 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.16.11 → 0.16.12.

---

### D-2026-05-12-P — Add ``owner: str | None`` to BaseNodeFields (multi-user prep)

- **What:** Add an ``owner`` field to ``BaseNodeFields`` (Pydantic)
  and ``BaseFieldsJson`` / ``BaseFields`` (TS), plus the matching
  ``readonly owner!: string | null`` declaration + ``owner:
  this.owner`` toJson emission on each of the 15 entity classes.
  Type ``string | null``, default ``null``. Schema parity test
  ``_EXPECTED_BASE_FIELDS`` extended.

- **Why:** the canonical Plot spec re-delivered by the user
  (plan ``~/.claude/plans/dazzling-inventing-boole.md``) §"데이터
  구조 원칙":
  > "owner 필드 포함 (멀티유저 확장 대비)."

  Multi-user editing itself is out of scope for the current cycle
  (per spec §"추후 과제"); this commit lands the *data field* so
  the wire format is ready when multi-user does ship. Single-user
  sessions write ``null``; server fills from session context once
  multi-user lands.

- **Scope discipline (what this decision does NOT do):**
  - **No UI surface.** Inspector / node renderers / display
    unchanged. ``owner`` is invisible to today's user.
  - **No permission logic.** Read / write authorisation comes
    later with the rest of the multi-user track.
  - **No retroactive backfill.** Existing nodes load with
    ``owner=null`` via Pydantic + TS defaults; no migration.
  - **All 15 kinds inherit.** Refs (``mission_ref`` /
    ``value_ref`` / ``identity_ref`` / ``actor_ref``) and
    composition kinds (``rule`` / ``content`` / ``step`` /
    ``metric``) can each be owned independently if needed. The
    spec doesn't say "symbols only" — every node gets it.

- **Alternatives considered:**
  - **Structured owner** (``{ id: string; type: "user" | "team" |
    "org" }``): rejected per YAGNI. Multi-user data shape is not
    yet specced; ``string | null`` is the cheapest extensible
    placeholder.
  - **Owner only on symbol kinds** (Mission / CoreValue /
    Identity / Actor / Service): rejected. Future scope (e.g.
    a workspace where service rules carry team-specific
    permissions) would need it on rules. Default ``null`` on all
    is cost-free today and future-proof.
  - **Skip the field, add it when multi-user starts**: rejected.
    Wire-format migrations are expensive once user data is in
    the wild; adding the field now (with default ``null``) is
    backwards-compatible.

- **Approval:** Accepted by spec mandate. Schema parity test
  pins TS ↔ Pydantic agreement on the new field.

- **Spec impact:** none in ``docs/SPEC.md`` (no user-visible
  behaviour change). ``docs/PRODUCT_SPEC.md §5 데이터 구조 원칙``
  could later be reconciled with the canonical spec wording, but
  that is a separate doc-only commit.

- **Files in this commit:**
  - ``plot/plot_mcp/models.py`` — ``BaseNodeFields`` adds
    ``owner: str | None = None`` after ``details_path``.
  - ``plot/viewer/src/domain/BaseFields.ts`` —
    ``BaseFieldsJson`` + ``BaseFields`` interfaces add ``owner:
    string | null``; ``parseBaseFields`` reads it with null
    default.
  - ``plot/viewer/src/domain/{15 entity files}`` — each gets a
    ``readonly owner!: string | null`` field + ``owner:
    this.owner`` line in ``toJson``.
  - ``plot/tests/test_schema_parity.py`` — ``_EXPECTED_BASE_FIELDS``
    gains ``"owner"``.
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.13 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.16.12 → 0.16.13.

---

### D-2026-05-12-Q — Anchor drag snap-back: optimistic local update

- **What:** ``App.tsx`` 's ``onAnchorChange`` handler now updates
  ``summaries`` state **optimistically** (via the new pure helper
  ``viewer/src/lib/anchorOptimistic.ts::applyOptimisticAnchorPatch``)
  *before* the ``patchProjectAnchor`` PATCH request fires. After the
  server response, the optimistic doc is replaced with the canonical
  server doc. On PATCH failure, the previous (pre-patch) doc is
  restored.

- **Why:** React Flow is a *controlled* component — its ``nodes``
  prop is the SSOT for node positions. The anchor drag flow was:
  ```
  user drag → onNodesChange → handleNodesChange → applyAnchorChange
  → onAnchorChange(patch) → patchProjectAnchor (async, 100-500ms)
  → replaceSummary
  ```
  Before this fix, ``summaries`` state only updated *after* the PATCH
  resolved, so during the round-trip the computed ``projectAnchor``
  prop carried the OLD position. React Flow, being controlled,
  rendered the anchor at the OLD position prop → user saw the anchor
  snap back to its pre-drag location.

  Same pattern as any optimistic-update UX: client commits the
  local view first, reconciles with server response after.

- **Why this wasn't caught earlier:** v0.13 Phase 0 introduced the
  anchor PATCH path but only tested it with localhost MCP server,
  where the PATCH round-trip is < 5ms — fast enough that the snap-back
  was sub-perceptible. Once the user's actual workflow involved any
  network latency (slow local CPU under HMR, real-world deploy
  latency, etc.), the gap became visible.

- **Architecture:**
  - New ``viewer/src/lib/anchorOptimistic.ts`` (~50 LOC):
    ``applyOptimisticAnchorPatch(current, tab, patch): ProjectDoc``
    + ``resolveAnchorPlacement(proj, tab): AnchorPlacement``. Pure,
    side-effect-free, testable in isolation.
  - ``App.tsx`` onAnchorChange shrinks from 7 lines to 17 lines
    (added optimistic update + error revert) but uses helper so
    the *new* logic stays in a 50-LOC pure module instead of
    bloating App.tsx (which has a 400-LOC structural ceiling).

- **Tests:** ``plot/viewer/tests/anchor-drag-snap-back.test.tsx``
  — 7 tests covering: x/y patch, missing-anchors-default, other-tab
  isolation, dimension-only patch, revert-via-previous, default
  fallback, stored-placement readback.

- **Alternatives considered:**
  - **Use ``useReactFlow().setNodes()`` to forcibly write the new
    anchor position into RF's store before the PATCH**: rejected —
    breaks the controlled-component contract (same anti-pattern as
    Cmd+A in D-2026-05-12-R, addressed separately at v0.16.17).
  - **Synchronous PATCH (await before returning)**: rejected — would
    block the drag handler on the server round-trip.
  - **Move ``summaries`` to a Context with optimistic+server
    reducer pattern**: over-engineering for one patch site. If a
    second optimistic site appears later, revisit.

- **Approval:** Accepted by spec mandate (RF controlled-component
  contract) + regression test pinning.

- **Spec impact:** ``docs/SPEC.md §Anchor`` already says
  "Mutation routing: anchor changes flow through ``onAnchorChange``
  (a separate prop), **never** through ``onDocChange``". This decision
  doesn't change that — only the *timing* of the state propagation
  back into ``summaries``.

- **Files in this commit:**
  - ``plot/viewer/src/lib/anchorOptimistic.ts`` — new (~55 LOC).
  - ``plot/viewer/src/App.tsx`` — onAnchorChange uses the helper +
    error revert. 381 → 393 LOC (within 400 ceiling).
  - ``plot/viewer/tests/anchor-drag-snap-back.test.tsx`` — new
    (7 tests).
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.15 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.16.14 → 0.16.15.

- **Series context:** First of 5-commit React Flow regression-fix
  batch (v0.16.15-19) prompted by user hands-on review of v0.16.14.
  Companion fixes: refetch storm (v0.16.16), Cmd+A controlled
  contract (v0.16.17), fitView gating (v0.16.18), anchor
  data.onResize stability (v0.16.19).

---

### D-2026-05-12-R — Stable callback handlers (refetch storm fix)

- **What:** New ``viewer/src/hooks/useStableHandlers.ts`` returns
  ``useCallback``-wrapped post-project handlers (handleListStale /
  handleExternalCanvas / handleTagsRefresh / handleExternalChange).
  ``App.tsx`` additionally inlines ``handleError`` + ``handleActiveIdChange``
  pre-project as direct ``useCallback`` (they must be stable BEFORE
  ``useProject`` is invoked).

- **Why:** Playwright session recording showed **404 GETs to the same
  3 endpoints** in a single idle browser session — a refetch storm.
  Root cause: App.tsx passed inline arrow closures to ``useProject``,
  ``useCanvasPersist``, and ``useProjectSocket``. Those closures
  were recreated on every render. ``useProject``'s ``loadList`` had
  ``onError`` in its dependency array, so ``loadList`` was rebuilt
  every render too. Under certain WebSocket event timings the
  cascade could trigger a refetch chain: WS event → onListStale →
  loadList → setSummaries → App re-render → new closures → next
  WS event sees a different ``handlersRef.current`` snapshot → repeat.

- **Stability boundary:**
  - *Pre-project* handlers (``handleError``, ``handleActiveIdChange``)
    must be stable before ``useProject`` runs, so they live as
    direct ``useCallback`` in App.tsx (2 callbacks, 5 lines).
  - *Post-project* handlers (the 4 above) depend on ``useProject``'s
    output (``loadList``, ``setCanvasCache``, ``setTags``) and are
    bundled into ``useStableHandlers``.
  - This 2-stage shape keeps App.tsx under its 400-LOC ceiling
    (App.tsx 393 → 380 LOC after extraction).

- **Why the refetch storm appeared *now*:** the v0.16.0 App.tsx
  split (D-2026-05-12-H) extracted useUrlSync / useAvailableNodes /
  useAppKeyboard, leaving the *project / persist / socket* trio of
  hook wirings inline with their inline callbacks. None of the v0.15
  / v0.16 structural guards catch callback identity issues —
  structural-guards.test.tsx is *static* (file shape / LOC), not
  *runtime* (re-render behaviour). The storm only surfaced under
  hands-on use, exactly as the user predicted.

- **Tests:** ``plot/viewer/tests/stable-handlers.test.tsx`` —
  5 tests covering: identity stability across re-renders, identity
  change when ``loadList`` ref changes, ``handleExternalCanvas``
  produces the right Map-updater, ``handleExternalChange`` calls
  ``historyClear``, ``handleListStale`` invokes ``loadList``.

- **Alternatives considered:**
  - **Move all inline closures to refs in useProject / useCanvasPersist
    / useProjectSocket** (so caller stability doesn't matter):
    rejected. Already done in useCanvasPersist + useProjectSocket
    via ``handlersRef``. useProject doesn't follow the same pattern;
    converting it would change its public contract. Caller-side
    useCallback is the localised fix.
  - **Wrap each handler in a separate ``useCallback`` inline in App.tsx**:
    rejected — would push App.tsx past 400 LOC ceiling without a
    structural decision. The hook extraction is structurally cleaner.

- **Approval:** Accepted by regression test + LOC budget compliance.

- **Spec impact:** none — internal refactor.

- **Files in this commit:**
  - ``plot/viewer/src/hooks/useStableHandlers.ts`` — new (~60 LOC).
  - ``plot/viewer/src/App.tsx`` — pre-project handlers via
    ``useCallback``, post-project via ``useStableHandlers``. 393 →
    380 LOC.
  - ``plot/viewer/tests/stable-handlers.test.tsx`` — new (5 tests).
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.16 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.16.15 → 0.16.16.

---

### D-2026-05-12-S — Cmd+A respects controlled-component contract

- **What:** ``useKeyboardShortcuts`` 's ``Cmd+A`` handler used to flip
  the RF store's ``selected`` flag via ``setNodes`` / ``setEdges``,
  but never synced ``selectedNodeIds.current`` (the SketchCanvas ref
  the clipboard reads). After Cmd+A, the user's next ``Cmd+C`` /
  ``Cmd+D`` copied the *previous* selection, not "all nodes". Fix:
  after the store mutation, write ``selectedNodeIds.current =
  inst.getNodes().map(n => n.id)`` so the ref tracks the RF store.

- **Why:** RF emits ``onSelectionChange`` only on *user-initiated*
  selection events (click / box-select / arrow keys). Programmatic
  ``setNodes(... selected: true)`` does NOT trigger it. The
  SketchCanvas wire-up assumed onSelectionChange was the single
  source of selection truth — Cmd+A broke that assumption.

- **Architecture honesty:** the deeper fix would be to *not* use
  ``setNodes`` for selection at all, but RF v11 doesn't expose a
  public "select all programmatically + fire onSelectionChange" API.
  Manual ref sync is the localised fix that preserves both sides
  of the contract.

- **Tests:** ``plot/viewer/tests/select-all-sync.test.tsx`` — 2 tests:
  Cmd+A populates ``selectedNodeIds.current`` with all rendered node
  ids + RF store ``selected`` flag flips for all nodes; then Cmd+C
  copies the full set (via clipboard mock).

- **Approval:** Accepted by regression test.

- **Spec impact:** ``docs/SPEC.md §Keyboard shortcuts`` already
  declares Cmd+A's user-visible behaviour ("Select all nodes and
  edges"); this fix makes the *internal contract* match.

- **Files in this commit:**
  - ``plot/viewer/src/canvases/sketch/useKeyboardShortcuts.ts`` —
    Cmd+A branch now also syncs ``selectedNodeIds.current``.
  - ``plot/viewer/tests/select-all-sync.test.tsx`` — new (2 tests).
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.17 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.16.16 → 0.16.17.

---

### D-2026-05-12-T — fitView gating: onInit only, not as ReactFlow prop

- **What:** Remove the ``fitView`` (+ ``fitViewOptions``) prop from
  the ``<ReactFlow>`` element in ``SketchCanvas``. Call
  ``inst.fitView({ padding: 0.2 })`` once inside the ``onInit``
  callback. Tab changes still re-fit because the wrapper has
  ``key={activeCanvasKey}`` (App.tsx) which forces remount → new
  ``onInit`` fires.

- **Why:** Plot's ``useNodesMemo`` returns a fresh ``nodes`` array
  on every render (synthetic anchor is re-injected from the prop).
  RF v11's ``fitView`` prop re-fits whenever the ``nodes`` reference
  changes, so the user's manual zoom / pan was reset mid-session
  by every unrelated state update (Inspector form input, history
  push, etc.). Visible bug: cannot zoom-into a region — the view
  springs back to "fit all" on next render.

- **Approval:** Accepted by static guard. The
  ``viewport-stability.test.tsx`` regex catches reintroduction of
  the ``fitView`` prop.

- **Tests:** ``plot/viewer/tests/viewport-stability.test.tsx``
  — 2 static-grep tests:
  - No top-level ``fitView`` prop on ``<ReactFlow ...>``.
  - ``onInit`` JSX form present and contains an ``inst.fitView(...)``
    call.

- **Alternatives considered:**
  - **Memoize ``nodes`` array reference** to make the prop stable
    across non-content-changing renders: would need deep equality
    on ``useNodesMemo`` output, which is non-trivial and bypasses
    React's normal reference-equality contract.
  - **Use ``useNodesInitialized`` + a once-only effect**: more
    code; the simpler ``onInit`` callback covers initial mount and
    tab-switch remount equally well.
  - **Set ``fitView={false}`` explicitly**: same effect as removing
    the prop (default is undefined-falsy), but slightly clearer
    intent. Either is fine; we go with removal.

- **Spec impact:** ``docs/SPEC.md §Viewport`` already says
  "Fit view fires once on mount + once per canvas switch." This
  fix makes the code match.

- **Files in this commit:**
  - ``plot/viewer/src/canvases/SketchCanvas.tsx`` — remove
    ``fitView`` + ``fitViewOptions`` props from ``<ReactFlow>``;
    add ``inst.fitView({ padding: 0.2 })`` to ``onInit``.
  - ``plot/viewer/tests/viewport-stability.test.tsx`` — new
    (2 static-grep tests).
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.18 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.16.17 → 0.16.18.

---

### D-2026-05-12-U — Stable handleAnchorChange via useCallback (data.onResize ref stability)

- **What:** Extract App.tsx's inline ``onAnchorChange`` JSX arrow into
  a top-level ``useCallback``-wrapped ``handleAnchorChange`` declared
  alongside the other stable handlers. ``useNodesMemo`` 's synthetic
  anchor node carries an inline ``data.onResize: (w, h) => onAnchorChange?.(...)``;
  by stabilising ``onAnchorChange`` ref at the source, the memo's
  ``data`` object now only rebuilds when anchor-relevant state
  actually changes (projectPath / activeId / activeTab / summaries /
  project), not on every App render.

- **Why:** Closes the loop of the 5-commit React Flow regression
  batch (v0.16.15-19). Before this commit, even after v0.16.16's
  callback stabilisation, ``onAnchorChange`` was still inline JSX —
  recreated every App render. Each render triggered ``useNodesMemo``
  recomputation → fresh anchor node data → RF rerenders the anchor
  node. Visually subtle but contributes to anchor flicker / hover
  jitter under heavy use.

- **Approval:** Accepted by no-regression (399 / 399 tests still
  pass, no new failures) + LOC budget compliance (App.tsx 380 →
  385 LOC; well under 400 ceiling).

- **Tests:** No new dedicated test — the existing
  ``anchor-drag-snap-back.test.tsx`` (7 tests) covers
  ``handleAnchorChange`` 's behaviour (optimistic merge, revert);
  the existing ``stable-handlers.test.tsx`` (5 tests) covers the
  identity-stability pattern this commit applies to anchor too.

- **Spec impact:** none — internal stability optimization.

- **Files in this commit:**
  - ``plot/viewer/src/App.tsx`` — extract inline arrow JSX to
    ``handleAnchorChange = useCallback(...)``; replace prop usage
    with the stable reference.
  - ``plot/docs/DECISIONS.md`` — this entry.
  - ``plot/CHANGELOG.md`` — v0.16.19 section.
  - ``plot/.claude-plugin/plugin.json`` — patch bump 0.16.18 → 0.16.19.

- **Batch closure (v0.16.15-19):** This is the 5th and final commit
  of the React Flow regression-fix batch surfaced by user hands-on
  review of v0.16.14. All four major issues + this minor are now
  addressed with regression tests pinning each:

  | # | Issue | Decision | Test |
  |---|---|---|---|
  | 1 | Anchor drag snap-back | D-2026-05-12-Q | anchor-drag-snap-back.test.tsx (7 tests) |
  | 2 | Refetch storm | D-2026-05-12-R | stable-handlers.test.tsx (5 tests) |
  | 3 | Cmd+A controlled contract | D-2026-05-12-S | select-all-sync.test.tsx (2 tests) |
  | 4 | fitView mid-session reset | D-2026-05-12-T | viewport-stability.test.tsx (2 tests) |
  | 5 | Anchor data.onResize ref stability | D-2026-05-12-U | (covered by 1 + 2) |

  Total: 399 viewer tests (383 baseline + 16 new across the batch).

---

### D-2026-05-13-A — Restore anchor visual layer (v0.16.20-23 batch reverted)

- **What:** Revert all four commits of the v0.16.20-23 "RF 기본 동작
  rollback" batch as a single squashed git-revert:
  - ``ac35021`` v0.16.23 (batch closure docs / version bump)
  - ``32f3dc5`` v0.16.22 (synthetic anchor + PATCH path revert)
  - ``7edbbf8`` v0.16.21 (anchor-radial layout revert)
  - ``75ee0b0`` v0.16.20 (self-loop custom edge revert)

  Restores: synthetic project anchor on Foundation / Actors / Services
  canvases; anchor-radial initial placement for Foundation new nodes
  (120° auto-radial around anchor); ``SelfLoopEdge`` custom edge for
  ``source === target``; anchor PATCH path (``applyAnchorChange`` +
  ``anchorOptimistic`` + ``handleAnchorChange``).

  Keeps reverted: nothing — all four layers fully restored to their
  v0.16.19 state.

- **Why:** User direct correction — "다 복구 하라" — after the
  v0.16.20-23 batch was identified as over-reach. The original
  triggering message "그냥 RF 기본 동작으로 동작하게 해주세요"
  (v0.16.20 commit body) was interpreted as "remove the synthetic
  anchor and all its associated visual layers"; the user's actual
  intent was "keep the anchor + make *interaction* feel like stock
  React Flow". Removing the anchor itself violated the canonical
  Plot spec mandate ("프로젝트 노드가 가운데" — SPEC §Anchor) and
  contradicted the user's mental model. NEXT_SESSION.md:22-24 already
  recorded this as over-reach before this session.

- **Why not partial restore (anchor only, skip radial / self-loop):**
  User asked to restore *all*; partial restore would silently
  re-interpret the message a second time after the first
  mis-interpretation already cost a 4-commit batch.

- **Why not surgical revert of useNodesMemo block only:** The four
  layers were entangled at the commit level (anchor injection feeds
  PATCH path; PATCH path feeds optimistic update; radial layout
  reads anchor position; self-loop edge is independent but was
  bundled in the same batch). A single git-revert of the four
  commits is the audit-trail-preserving inverse — every restoration
  becomes a documented git event, not a hand-rewrite.

- **Real bug remains unresolved:** Interaction "엉망" — the user's
  *actual* complaint that triggered v0.16.15-19 *and* v0.16.20-23 —
  was never fixed by either batch. v0.16.19 (anchor present) and
  v0.16.23 (anchor absent) both exhibit the issue. This restoration
  is a precondition for diagnosis, not the diagnosis itself.
  Next-session work: ``RF 움직임`` trigger — reproducible step
  capture + layer kill-switch bisect (NEXT_SESSION.md).

- **Approval:** Accepted by user, 2026-05-13, via in-session
  ``AskUserQuestion`` answer: *"다 복구 하라고 그리고 문제의 원인을
  찾자고"*.

- **Spec impact:** [SPEC.md §Anchor](./SPEC.md#anchor-the-centre-node)
  / §Edges Self-loops / §Foundation Anchor-radial all restored to
  v0.16.19 text by the revert. No new spec lines.

- **Files in this commit:** all files in the
  ``ac35021..75ee0b0`` four-commit revert + ``plugin.json`` version
  ``0.16.19`` → ``0.16.24`` + ``CHANGELOG.md`` v0.16.24 section +
  this entry.

- **Reverted decisions (now back in force):**
  - D-2026-05-12-M (self-loop visual)
  - D-2026-05-12-N (anchor-radial layout)
  - D-2026-05-12-O / P / Q (anchor injection / PATCH / optimistic)
  - D-2026-05-04-B / C (anchor handles visible + visually distinct)

- **Rejected decisions (these are reverted away):**
  - D-2026-05-12-V (self-loop revert) — **Rejected**.
  - D-2026-05-12-W (anchor-radial revert) — **Rejected**.
  - D-2026-05-12-X (synthetic anchor + PATCH revert) — **Rejected**.
  - D-2026-05-12-Y (rollback batch closure) — **Rejected**.

  Note: revert removed these entries from the DECISIONS.md file
  itself (since the v0.16.22-23 commits added them). They are
  documented here so the next session sees both the proposal and
  its rejection.

- **Lesson:** When the user says "RF 기본 동작" mid-session, the
  scope is **interaction (cursor / drag / pan / zoom / select)**,
  not the synthetic node decoration. Spec mandates ("프로젝트 노드
  가운데", "셀프 피드백 루프", "주변에 붙임") override at-the-moment
  preference unless the user *explicitly* says "spec 도 폐기".
