// Mindmap auto-layout — four-direction tidy tree (上下左右). Pure
// geometry, no React imports.
//
// v0.40.0: replaces the radial / depth-ring layouts. The user rejected
// every circular layout ("원이 아니라", "마인드 노드 참고") — real
// mindmap tools (MindNode, XMind) lay branches out as horizontal /
// vertical TIDY TREES, never a sunburst. The user then asked for all
// four directions at once ("상하좌우로 합시다"):
//
//                     s ─ child
//                     │
//          branch ── cat   cat ── branch
//                 \   │   /
//      branch ── cat ─ HUB ─ cat ── branch
//                 /   │   \
//          branch ── cat   cat ── branch
//                     │
//                     s ─ child
//
// The hub sits at the centre. Its direct children (the top-level
// branches) are split across R / L / U / D, balanced by subtree
// leaf-count. Each branch grows AWAY from the hub as a tidy tree:
//   - R / L branches grow horizontally; children stack vertically.
//   - U / D branches grow vertically;   children stack horizontally.
// Each subtree owns a disjoint "band" on the cross axis (band size =
// Σ leaf cross-extents), and the parent is centred on its children →
// no overlap within a direction, parent reads as the group's head.
//
// Cross-direction overlap (the +-corner problem) is removed by starting
// each axis's branches BEYOND the perpendicular axis's cross-spread:
// R/L start at x ≥ (U/D x-spread) + gap, U/D start at y ≥ (R/L y-spread)
// + gap. The four arms therefore occupy four disjoint regions around an
// empty centre box that holds the hub. No node overlap, no edge crossing
// — proven by construction; pinned by mindmapLayout.test.ts.

import type { SketchEdge, SketchNode } from "../../types";

export interface MindmapLayoutHub {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface MindmapLayoutInput {
  nodes: SketchNode[];
  edges: SketchEdge[];
  hub: MindmapLayoutHub;
  /** Perpendicular gap between sibling subtrees (px). */
  crossGap?: number;
  /** Gap between successive depths along the growth axis (px). */
  rankGap?: number;
}

export interface MindmapLayoutOutput {
  positions: Map<string, { x: number; y: number }>;
}

type Dir = "R" | "L" | "U" | "D";
const DIR_ORDER: Dir[] = ["R", "D", "L", "U"]; // round-robin + tie-break order
const DEFAULT_CROSS_GAP = 16;
const DEFAULT_RANK_GAP = 44;

interface BucketResult {
  /** Local along-axis centre per node id (≥0, grows away from hub). */
  along: Map<string, number>;
  /** Local cross-axis centre per node id (centred on 0). */
  cross: Map<string, number>;
  /** max(|cross| + crossExtent/2) over the bucket — its perpendicular reach. */
  crossHalf: number;
  ids: string[];
}

export function computeMindmapLayout(input: MindmapLayoutInput): MindmapLayoutOutput {
  const { nodes, edges, hub } = input;
  const crossGap = input.crossGap ?? DEFAULT_CROSS_GAP;
  const rankGap = input.rankGap ?? DEFAULT_RANK_GAP;

  const positions = new Map<string, { x: number; y: number }>();
  const size = new Map<string, { w: number; h: number }>();
  const nodeById = new Map<string, SketchNode>();
  for (const n of nodes) {
    size.set(n.id, { w: n.width ?? 160, h: n.height ?? 80 });
    nodeById.set(n.id, n);
  }

  const hubCx = hub.x + hub.width / 2;
  const hubCy = hub.y + hub.height / 2;
  positions.set(hub.id, { x: hub.x, y: hub.y });

  // Undirected adjacency.
  const adj = new Map<string, string[]>();
  for (const e of edges) {
    if (!adj.has(e.source)) adj.set(e.source, []);
    if (!adj.has(e.target)) adj.set(e.target, []);
    adj.get(e.source)!.push(e.target);
    adj.get(e.target)!.push(e.source);
  }

  // Spanning tree from hub (BFS, first-visit wins). Children sorted by id.
  const children = new Map<string, string[]>();
  const depth = new Map<string, number>();
  const visited = new Set<string>([hub.id]);
  depth.set(hub.id, 0);
  const queue: string[] = [hub.id];
  while (queue.length > 0) {
    const cur = queue.shift()!;
    const kids: string[] = [];
    for (const nb of (adj.get(cur) ?? []).slice().sort()) {
      if (!visited.has(nb)) {
        visited.add(nb);
        depth.set(nb, depth.get(cur)! + 1);
        kids.push(nb);
        queue.push(nb);
      }
    }
    children.set(cur, kids);
  }

  // Subtree leaf-count (leaf = 1).
  const leafCount = new Map<string, number>();
  const countLeaves = (id: string): number => {
    const kids = children.get(id) ?? [];
    if (kids.length === 0) {
      leafCount.set(id, 1);
      return 1;
    }
    let s = 0;
    for (const k of kids) s += countLeaves(k);
    leafCount.set(id, s);
    return s;
  };
  countLeaves(hub.id);

  const tops = (children.get(hub.id) ?? []).slice();

  // Assign each top-level branch to one of the four arms (D-2026-06-01-F).
  //
  // ONE rule for every canvas: respect the node's CURRENT side. The arm is
  // the direction of the node's centre from the hub centre (dominant axis
  // wins). No per-kind special-casing — the user groups by WHERE they put
  // nodes (mission up, core_value left, identity right → they stay there).
  // Re-layout only tidies spacing within each arm; it never teleports a
  // branch to a different side. A brand-new node sitting exactly on the hub
  // has no usable side → those spread across the emptiest arms by subtree
  // leaf-count so a fresh graph still fans out instead of stacking.
  const buckets: Record<Dir, string[]> = { R: [], L: [], U: [], D: [] };

  // Horizontal bias (D-2026-06-01-G): a node counts as left/right whenever
  // it is meaningfully to one side, even if it sits higher/lower. Without
  // this, a tall column the user dragged to the right (every node at the
  // same +x but spanning a big y-range) mis-classifies its top nodes as
  // "up" and bottom as "down" — the column scatters across three arms
  // ("내가 오른쪽을 다 넘겼는데 왜 다시 상하로 돌아오냐"). A node is U/D
  // only when it is clearly more vertical than horizontal (|dy| > k·|dx|);
  // otherwise it goes L/R by the sign of dx. Mindmaps read horizontally,
  // so the bias favours columns over rows.
  const VERTICAL_BIAS = 3;
  const dirFromCurrent = (id: string): Dir | null => {
    const n = nodeById.get(id);
    if (!n) return null;
    const dx = n.x + (n.width ?? 160) / 2 - hubCx;
    const dy = n.y + (n.height ?? 80) / 2 - hubCy;
    if (dx === 0 && dy === 0) return null;
    // vertical only when clearly steeper than the bias; else horizontal.
    if (Math.abs(dy) > Math.abs(dx) * VERTICAL_BIAS) return dy >= 0 ? "D" : "U";
    return dx >= 0 ? "R" : "L";
  };
  const load: Record<Dir, number> = { R: 0, L: 0, U: 0, D: 0 };
  const unpositioned: string[] = [];
  for (const t of tops) {
    const d = dirFromCurrent(t);
    if (d) {
      buckets[d].push(t);
      load[d] += leafCount.get(t) ?? 1;
    } else {
      unpositioned.push(t);
    }
  }
  unpositioned.sort((a, b) => (leafCount.get(b)! - leafCount.get(a)!) || a.localeCompare(b));
  for (const t of unpositioned) {
    let best: Dir = DIR_ORDER[0];
    for (const d of DIR_ORDER) if (load[d] < load[best]) best = d;
    buckets[best].push(t);
    load[best] += leafCount.get(t)!;
  }
  for (const d of DIR_ORDER) buckets[d].sort();

  // --- lay out one direction's branches into local (along, cross) ---
  const layoutBucket = (roots: string[], dir: Dir): BucketResult => {
    const horizontal = dir === "R" || dir === "L";
    const alongExt = (id: string) => (horizontal ? size.get(id)!.w : size.get(id)!.h);
    const crossExt = (id: string) => (horizontal ? size.get(id)!.h : size.get(id)!.w);

    // collect bucket nodes (the root subtrees) + per-depth max along-extent
    const ids: string[] = [];
    const maxAlongAtDepth = new Map<number, number>();
    const walk = (id: string) => {
      ids.push(id);
      const d = depth.get(id)!;
      maxAlongAtDepth.set(d, Math.max(maxAlongAtDepth.get(d) ?? 0, alongExt(id)));
      for (const k of children.get(id) ?? []) walk(k);
    };
    for (const r of roots) walk(r);
    if (ids.length === 0) return { along: new Map(), cross: new Map(), crossHalf: 0, ids };

    // along centre per depth: depth1 inner edge at 0, then +rankGap per rank
    const depthsAsc = [...maxAlongAtDepth.keys()].sort((a, b) => a - b);
    const alongCenterByDepth = new Map<number, number>();
    let acc = 0;
    for (const d of depthsAsc) {
      const ext = maxAlongAtDepth.get(d)!;
      alongCenterByDepth.set(d, acc + ext / 2);
      acc += ext + rankGap;
    }
    const along = new Map<string, number>();
    for (const id of ids) along.set(id, alongCenterByDepth.get(depth.get(id)!)!);

    // cross via disjoint band allocation across the root subtrees
    const band = new Map<string, number>();
    const computeBand = (id: string): number => {
      const kids = children.get(id) ?? [];
      const b =
        kids.length === 0
          ? crossExt(id) + crossGap
          : kids.reduce((s, k) => s + computeBand(k), 0);
      band.set(id, b);
      return b;
    };
    let total = 0;
    for (const r of roots) total += computeBand(r);

    const cross = new Map<string, number>();
    const place = (id: string, start: number): void => {
      const kids = children.get(id) ?? [];
      if (kids.length === 0) {
        cross.set(id, start + band.get(id)! / 2);
        return;
      }
      let c = start;
      for (const k of kids) {
        place(k, c);
        c += band.get(k)!;
      }
      cross.set(id, (cross.get(kids[0])! + cross.get(kids[kids.length - 1])!) / 2);
    };
    let cursor = -total / 2;
    for (const r of roots) {
      place(r, cursor);
      cursor += band.get(r)!;
    }

    let crossHalf = 0;
    for (const id of ids) {
      crossHalf = Math.max(crossHalf, Math.abs(cross.get(id)!) + crossExt(id) / 2);
    }
    return { along, cross, crossHalf, ids };
  };

  const res: Record<Dir, BucketResult> = {
    R: layoutBucket(buckets.R, "R"),
    L: layoutBucket(buckets.L, "L"),
    U: layoutBucket(buckets.U, "U"),
    D: layoutBucket(buckets.D, "D"),
  };

  // Start each axis just beyond the perpendicular axis's cross-spread so
  // the four arms don't collide near the centre — kept tight (no extra
  // padding) so the first ring sits close to the hub. The first column is
  // already short because each arm only holds the branches the user put on
  // that side, so it stays within its quadrant without pushing it far out.
  const crossHalfRL = Math.max(res.R.crossHalf, res.L.crossHalf); // R/L column Y-spread
  const crossHalfUD = Math.max(res.U.crossHalf, res.D.crossHalf); // U/D row X-spread
  // Start each axis JUST beyond the perpendicular axis's spread so the four
  // arms don't collide near the centre — kept tight (no own-cross-half
  // term) so the first ring hugs the hub and edges stay SHORT (user: "왜
  // 이렇게 연결선이 길어"). A tall column may let its top/bottom nodes
  // splay slightly past the diagonal; short edges win that trade-off. Arm
  // ASSIGNMENT still respects the user's side via the horizontal bias
  // above, so the column stays one group.
  const startX = Math.max(hub.width / 2 + rankGap, crossHalfUD + rankGap);
  const startY = Math.max(hub.height / 2 + rankGap, crossHalfRL + rankGap);

  const apply = (r: BucketResult, dir: Dir): void => {
    for (const id of r.ids) {
      const a = r.along.get(id)!;
      const c = r.cross.get(id)!;
      const s = size.get(id)!;
      let cx: number;
      let cy: number;
      if (dir === "R") {
        cx = hubCx + startX + a;
        cy = hubCy + c;
      } else if (dir === "L") {
        cx = hubCx - startX - a;
        cy = hubCy + c;
      } else if (dir === "D") {
        cx = hubCx + c;
        cy = hubCy + startY + a;
      } else {
        cx = hubCx + c;
        cy = hubCy - startY - a;
      }
      positions.set(id, { x: cx - s.w / 2, y: cy - s.h / 2 });
    }
  };
  apply(res.R, "R");
  apply(res.L, "L");
  apply(res.U, "U");
  apply(res.D, "D");

  // Orphans (unreachable from hub) — grid below everything.
  const orphans = nodes.filter((n) => n.id !== hub.id && !depth.has(n.id));
  if (orphans.length > 0) {
    let maxY = hubCy;
    for (const p of positions.values()) maxY = Math.max(maxY, p.y);
    let x = hubCx - (orphans.length * 200) / 2;
    const y = maxY + 160;
    for (const o of orphans) {
      const s = size.get(o.id)!;
      positions.set(o.id, { x, y });
      x += s.w + 60;
    }
  }

  return { positions };
}
