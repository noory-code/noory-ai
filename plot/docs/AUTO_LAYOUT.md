# Auto-layout — per-canvas criteria (SSOT)

> The single source of truth for *how the `자동 정렬` button arranges each
> canvas*. When code and this doc disagree, fix whichever is wrong and say
> which. Pinned by `viewer/tests/mindmapLayout.test.ts`.

---

## 1. The two things "정렬" actually controls

These are **separate** and must not be confused (the main source of churn
during v0.40.0):

| Concern | Who decides | What it sets |
|---|---|---|
| **Node placement** | `computeMindmapLayout` (+ `actorAnchoredLayout` for ServiceDetail) | each node's `x` / `y` |
| **Edge attachment** | `edgeTransform` (render-time) | which side (`t/r/b/l` handle) each edge end connects to |

Removing floating edges, changing handles, etc. only touch **edge
attachment** — they do not move nodes. The layout algorithm never reads
handles. Fixing "정렬" almost always means deciding which of the two you
mean.

---

## 2. Flow semantics per canvas (the direction of meaning)

Each canvas has a fixed **flow meaning** that fixes arrow direction,
stored on each edge as `edge.relation` (SSOT, read by viewer + server).

| Canvas | Meaning | Arrow direction | `relation` |
|---|---|---|---|
| **Foundation** | **수렴 (convergence)** — elements compose into the essence | element → BANAS (into anchor) | `injection` for essence refs, else `flow` |
| **Actors** | **상속 (inheritance)** — parent passes down to child | parent → child | `inheritance` |
| **Services** | **발산 (divergence)** — the essence decomposes into services | BANAS → category → service | `flow` |
| **ServiceDetail** | **시퀀스 (sequence)** — actor walks the step graph | actor → step → … | `flow` |

Pinned 2026-06-01 (D-2026-06-01-D): Services flipped from element→anchor
to anchor→element (divergence). Foundation stays convergence; Actors stays
inheritance.

---

## 3. Placement algorithm (`computeMindmapLayout`)

All primary canvases use a **4-direction (上下左右) tidy tree**.
Decision 2026-06-01 (D-2026-06-01-F): keep the 4-direction shape (not a
single left→right tree, not a circle).

### Arm assignment — ONE rule, no per-kind special-casing
- The hub = the project anchor (Foundation / Actors / Services) or the
  hidden root-service (ServiceDetail).
- BFS spanning tree from the hub (cycle-safe, id-sorted → deterministic).
- Each top-level branch goes to the arm matching **its current side** of
  the hub (direction of its centre from the hub centre, dominant axis
  wins). The user groups by WHERE they place nodes — drag mission up,
  core_value left, identity right and re-layout keeps them there.
- A brand-new node sitting exactly on the hub has no usable side; those
  spread across the emptiest arms by subtree **leaf-count** so a fresh
  graph still fans out instead of stacking on one axis.
- **No per-kind rule.** An earlier "one arm per kind" version was rejected
  ("또 카테고리별로 정렬 규칙을 만들어뒀구만요") — the single
  position-respecting rule already groups when the user groups by
  placement.

### Within an arm
- A tidy tree growing **away** from the hub. R/L grow horizontally
  (children stack vertically); U/D grow vertically (children stack
  horizontally). Each subtree owns a disjoint cross-axis **band**
  (band = Σ child cross-extents); the parent centres on its children →
  no overlap, parent reads as the group head.
- Cross-arm collision: each axis starts **just beyond** the perpendicular
  axis's spread, kept tight (`rankGap` 44, `crossGap` 16) so the first
  ring sits close to the hub → short edges, four disjoint regions around
  the centre box holding the hub.

### Guarantees (pinned by `viewer/tests/mindmapLayout.test.ts`)
1. no two nodes overlap;
2. every child sits beyond its parent (outward, no back-cross);
3. top-level children spread across ≥3 directions (not one pile);
4. branches stay on the side the user placed them (mission↑ / values← /
   identities→ when grouped there);
5. deterministic.

### ServiceDetail exception
When a doc has a user-side `actor_ref` wired to an entry step (the
"subject edge"), `actorAnchoredLayout` runs **first** (dagre layered,
direction from the subject edge `LR/RL/TB/BT`, actor anchored, steps
ranked, injection overlays anchored beside their target). Only when no
subject edge claims the doc does the mindmap path run.

### Wiring (`useAutoLayout.trigger`, priority order)
1. user-side actor subject edge → `actorAnchoredLayout`
2. anchor present → `computeMindmapLayout(hub = anchor)`
3. else operator-side / any actor_ref subject edge → `actorAnchoredLayout`
4. else → `handleAwareLayout` (dagre LR fallback)

The trigger is **manual** (the `자동 정렬` button). Decision 2026-06-01:
no always-on auto-layout (user cancelled it). Positions land via the
normal `onDocChange` → one `Cmd+Z` undoes them; positions only, no other
field touched.

---

## 4. Tuning constants (`computeMindmapLayout`)
| Const | Default | Meaning |
|---|---|---|
| `rankGap` | 44 px | gap between depth ranks along the growth axis |
| `crossGap` | 16 px | gap between sibling subtrees on the cross axis |

Kept tight so the first ring hugs the hub (user: "거리를 왜 이렇게 멀리").

---

## 5. Edge attachment side (`edgeTransform`)

Floating edges were removed in v0.40.0 (D-2026-06-01-E). Each non-self-
loop edge attaches to the handle on the side of each node **facing the
other node** (computed from node centres passed via `useEdgesMemo`; the
synthetic anchor is **not** in `doc.nodes`, so it is seeded from
`projectAnchor`). `BaseNode`'s four handles are all `type="source"` with
ids `t/r/b/l`; `ConnectionMode.Loose` lets them receive, so the same ids
serve both ends. This gives clean routing from any direction (the
"uniform from any side" goal floating had) without floating, fixing the
arrow-tangle floating papered over.

---

## 6. History (why it looks the way it does)
- v0.34.8 radial depth-rings → rejected ("원이 아니라 트리").
- v0.39.0 Reingold-Tilford position-inferred tree → split one parent's
  children across 4 sides, cross-branch crowding near the anchor.
- v0.40.0 `computeMindmapLayout` 4-direction tidy tree (this doc).
  - per-kind arm grouping tried, then removed (single position rule).
  - floating edges (D-2026-05-31-F) removed (D-2026-06-01-E).
