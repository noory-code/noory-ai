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
