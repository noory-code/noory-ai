# CURSOR — canvas-wide cursor behaviour SSOT

> **Audience:** anyone touching `viewer/src/styles.css`,
> `viewer/src/canvases/SketchNode.tsx`, `viewer/src/edit/EditableText.tsx`,
> or any new interactive node element.
>
> **Pairs with:**
> - [`SPEC.md` §Cursor states](./SPEC.md#cursor-states-canvas-wide-ssot-applies-to-every-canvas) — short table form.
> - [`DECISIONS.md` D-2026-05-10-C](./DECISIONS.md) — reset rationale.
> - [`../CLAUDE.md`](../CLAUDE.md) — pre-edit gates and anti-patterns.

---

## TL;DR

| Where | Cursor |
|---|---|
| Anywhere on the canvas (pane or node) — idle hover | **`grab`** 🖐 |
| Anywhere on the canvas — actively dragging | **`grabbing`** ✊ |
| Connection handle (4 dots on every node) — hover | **`crosshair`** ✛ |
| Edge (connection line) — hover | **`pointer`** ☝ |
| Resize control (sides / corners on selected node) | **`ew/ns/nwse/nesw-resize`** ↔ ↕ ⤡ ⤢ |

That's the entire spec. Everything below explains why this is the
shape, what we tried before, and what an editor must do to deviate.

---

## The mental model

React Flow ships a uniform model that we adopted in v0.13.6:

> **Anything draggable shows `grab`.**
> Active drag shows `grabbing`.
> Drawing a connection shows `crosshair`.
> Clicking-to-select an edge shows `pointer`.
> Resizing shows the directional resize cursor.

Both `.react-flow__pane` and `.react-flow__node` declare
`cursor: grab`, so the cursor never changes when the mouse crosses
between empty canvas and a node — by construction there is nothing
to flicker.

This is the standard React Flow contract that ships in every other
React Flow product. Adopting it instead of inventing our own buys
us:

- **One known state** to reason from. Vendor CSS is the SSOT.
- **No flicker by construction.** Adjacent regions agree.
- **Predictable affordances** for users who've used any other
  React Flow product.

---

## The full table (with selectors)

Sourced from `node_modules/reactflow/dist/style.css` and
`node_modules/@reactflow/node-resizer/dist/style.css`. We do not
override these.

| Region | Selector | State | Cursor |
|---|---|---|---|
| Empty canvas | `.react-flow__pane` | idle | `grab` |
| Empty canvas | `.react-flow__pane.dragging` | actively panning | `grabbing` |
| Node body | `.react-flow__node` | idle hover | `grab` |
| Node body | `.react-flow__node.dragging` | actively dragging | `grabbing` |
| Multi-selection rect | `.react-flow__nodesselection-rect` | hover | `grab` |
| Connection handle | `.react-flow__handle.connectionindicator` | hover, connectable | `crosshair` |
| Edge | `.react-flow__edge` | hover | `pointer` |
| Edge updater | `.react-flow__edgeupdater` | hover end-point | `move` |
| Resize side L/R | `.react-flow__resize-control.left/right` | hover | `ew-resize` |
| Resize side T/B | `.react-flow__resize-control.top/bottom` | hover | `ns-resize` |
| Resize corner ↘ | `.react-flow__resize-control.top.left` / `.bottom.right` | hover | `nwse-resize` |
| Resize corner ↙ | `.react-flow__resize-control.bottom.left` / `.top.right` | hover | `nesw-resize` |
| Inspector / Toolbar / context menu | per element | hover | per element (Tailwind / browser defaults) |

---

## The two rules we add — Tailwind preflight cancellation

`styles.css` contains exactly two cursor-related rules:

```css
/* (1) RF v11 sets role="button" on .react-flow__node itself for
       accessibility. Restore RF's intended grab. */
.react-flow__node[role="button"] {
  cursor: grab;
}
.react-flow__node[role="button"].dragging {
  cursor: grabbing;
}

/* (2) Inside a node, force descendants to inherit the node's cursor
       so EditableText label + fold button don't flip to pointer. */
.react-flow__node *:not(.react-flow__handle):not(.react-flow__resize-control) {
  cursor: inherit;
}
```

### Why this exists

Tailwind preflight (loaded via `@tailwind base;`) ships these rules
in every Tailwind-using project:

```css
button, [role="button"] { cursor: pointer; }
:disabled { cursor: default; }
```

Three elements in our canvas match these selectors:

- **`.react-flow__node` itself** — RF v11 sets `role="button"` on every
  node element for accessibility. Tailwind preflight matches it
  directly. Without rule (1), the node element shows `cursor: pointer`,
  and (because cursor inherits) every descendant inside the node shows
  `cursor: pointer` too.
- **The fold button** (`<button>`) on container nodes.
- **The EditableText label span** which carries `role="button"` for
  keyboard accessibility.

Without the cancellation rules, the cursor flips between `grab` (RF
default on the pane) and `pointer` (Tailwind preflight on the node)
as the mouse crosses the node-pane boundary. That is the exact
flicker the v0.13.3 → v0.13.6 work tried to fix six times — and
finally identified in v0.13.10 via Playwright DOM-probe diagnostics.

Rule (1) restores `grab` on the node element. Rule (2) makes every
descendant inherit from the node — except the React Flow
infrastructure (handles and resize controls), which keeps its
semantic cursor.

### Why this isn't "just another override"

The override stack we removed in v0.13.6 changed RF's own defaults
(node = `pointer` instead of `grab`, handles hidden until selected,
custom handle colours, etc.). The cancellation rule does not change
RF — it cancels a *Tailwind* rule that was breaking RF's
inheritance chain inside our canvas. The RF mental model remains
intact; we just stop Tailwind from contradicting it.

### Why we don't simply remove `role="button"` from the label

EditableText is also used outside the canvas (e.g. Inspector
fields). In those contexts `role="button"` is the right semantic
for screen readers — the span IS a button. Removing the role to
fix the canvas would degrade accessibility everywhere else. The
narrower fix lives in canvas-scoped CSS.

---

## Anti-patterns (do not do these)

| Anti-pattern | Why it bit us before |
|---|---|
| **Override `.react-flow__node { cursor: pointer }`** to make nodes feel "clickable" | v0.13.3-v0.13.5. Created a `pointer ↔ grab` boundary at every node edge and a `pointer ↔ crosshair` boundary at every handle, then we fixed those boundaries with five more rules, and so on. |
| **Hide handles until selected** then re-style them with custom colours / sizes | v0.13.4-v0.13.5. Two cycles of "큰 검지 / 작은 검지" flicker came from animating the appearance and the indicator scale. |
| **Force `cursor: default` on the pane** to suppress flicker while disabling pan | v0.13.4. Made the canvas read as inert when it was actually pannable, then we re-enabled pan and the override stayed inconsistent until v0.13.6 removed both. |
| **Decorate a node with `outline` / `outline-offset` / `ring` / outset `box-shadow`** | v0.13.5. Visual extent paints outside the click target; clicks on the visible decoration land on the pane below. Border instead. |
| **Add a fresh cursor rule for a new symptom** without reading this doc first | The override stack itself is the regression engine — every unaudited rule paid for the next round of bug reports. |

---

## How to deviate (if a future requirement demands it)

The reset is a *baseline*, not a *moratorium*. Deviation is allowed
when there's a real user need; it just needs an audit trail.

### Workflow

1. Open a fresh `D-YYYY-MM-DD-X` entry in
   [`DECISIONS.md`](./DECISIONS.md). Record the user's words and
   what cursor state must change.
2. Get explicit user approval on the decision *before* writing CSS.
3. Add the rule to `styles.css` with a comment naming the decision
   id, e.g.:
   ```css
   /* Per D-2026-06-15-A — handles only when selected so canvases
      with many nodes don't look like a measles outbreak. */
   .react-flow__node:not(.selected) .react-flow__handle {
     opacity: 0;
   }
   ```
4. Update [SPEC.md §Cursor states](./SPEC.md#cursor-states-canvas-wide-ssot-applies-to-every-canvas)
   table to reflect the new state.
5. Update this file's "Full table" section.
6. Add a regression test to
   `viewer/tests/SketchCanvas.regression.test.tsx` that fails if the
   rule is removed.

### Forbidden shortcuts

- Adding a CSS rule "to see if it helps" without a decision id.
- Editing `node_modules/reactflow/dist/style.css` directly.
- Wrapping React Flow elements in another DOM layer to isolate
  cursor — RF expects its own DOM tree to remain unwrapped for
  hit-testing and connection routing.

---

## How to verify the cursor state in the browser

Drop this into DevTools console at any canvas URL:

```js
const seen = new Map();
document.body.addEventListener('mousemove', (e) => {
  const el = document.elementFromPoint(e.clientX, e.clientY);
  if (!el) return;
  const cur = getComputedStyle(el).cursor;
  if (!seen.has(cur)) {
    seen.set(cur, {
      tag: el.tagName,
      cls: String(el.className).slice(0, 80),
      id: el.id,
    });
  }
});
window.dumpCursors = () => console.table(
  Array.from(seen, ([c, m]) => ({ cursor: c, ...m })),
);
console.log('Move the mouse around, then run: dumpCursors()');
```

Expected output after moving across an empty pane and a node body
(no handles, no resize controls):

```
┌─────────┬──────┬──────────────────┬────┐
│ cursor  │ tag  │ cls              │ id │
├─────────┼──────┼──────────────────┼────┤
│ grab    │ DIV  │ react-flow__...  │    │
└─────────┴──────┴──────────────────┴────┘
```

If `pointer` appears with a tag in the node descendants (a button,
a `[role="button"]` span, etc.), the Tailwind preflight cancellation
rule is missing or has been broken. Check `styles.css` first.

---

## Change history

- **v0.13.10 (2026-05-10)** — added cancellation rule for
  `.react-flow__node[role="button"]` itself (RF v11 a11y attribute
  was the root cursor-flicker source all along). Identified via
  Playwright DOM probe. See D-2026-05-10-F.
- **v0.13.6 (2026-05-10)** — full reset to RF defaults + Tailwind
  preflight cancellation on descendants. See D-2026-05-10-C.
- **v0.13.3-v0.13.5** — six-round override stack (now removed). See
  D-2026-05-04-E, D-2026-05-08-C, D-2026-05-08-E, D-2026-05-08-F,
  D-2026-05-08-G, D-2026-05-10-A.
