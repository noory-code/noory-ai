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

### D-2026-05-04-D — Auto-layout removed entirely

- **What:** Remove the "Auto layout" toolbar button and the
  corresponding pane-context-menu entry. Drop the `radialLayout` /
  `autoLayout` calls and the `handleAutoLayout` callback from
  `SketchCanvas`.
- **Why:** layout encodes user intent (where things sit relative to
  each other reflects how the user thinks about them). Auto-layout
  silently overwrites that intent.
- **Alternatives:** keep auto-layout but require confirmation
  (rejected — adds friction without solving the intent-overwrite
  problem); restrict to specific canvas kinds (rejected — same issue
  on every kind).
- **Approval:** **Accepted (removal)** by user, 2026-05-04.
- **Spec impact:** [`SPEC.md` §Auto-layout](./SPEC.md#auto-layout) —
  codifies "removed; layout is fully manual".

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
