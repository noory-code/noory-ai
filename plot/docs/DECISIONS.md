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
