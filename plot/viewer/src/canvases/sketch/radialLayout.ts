// Radial auto-layout — hub-and-spoke pattern.
//
// Per SPEC.md §Auto-layout and DECISIONS.md D-2026-05-24-B:
// - A single hub node is the layout origin (anchor for Services; the
//   hidden root-service for FeatureDetail). The hub itself is never
//   moved.
// - BFS from the hub via undirected edges assigns a ring level to every
//   reachable node (hub = 0, immediate neighbours = 1, …).
// - Within a ring, members are sorted by id for determinism and spaced
//   at equal angles starting from the top (-π/2). A ring with N members
//   uses 2π / N per slot.
// - Ring k radius accumulates: ring 1 = hub_half + ring1_span_half +
//   gap; subsequent rings add ring_k_span + gap. Span = the longest
//   node dimension in that ring.
// - Orphan nodes (not reachable from hub) drop into a grid below the
//   last ring — same fallback shape autoLayout.ts uses for disconnected
//   subtrees.
// - Determinism: id-sort everywhere. Same input → same output.
//
// Pure module — no React imports.

import type { SketchEdge, SketchNode } from "../../types";

export interface RadialLayoutHub {
  id: string;
  /** Top-left x. */
  x: number;
  /** Top-left y. */
  y: number;
  width: number;
  height: number;
}

export interface RadialLayoutInput {
  /** All nodes on the canvas. The hub may or may not appear here (the
   *  synthetic project anchor lives outside ``doc.nodes`` but a hidden
   *  root-service does live inside it). */
  nodes: SketchNode[];
  edges: SketchEdge[];
  hub: RadialLayoutHub;
  /** Gap (px) between adjacent rings and between orphan grid cells.
   *  Defaults to 40 — chosen so an 80×36 default node has roughly its
   *  own width again between siblings on the inner ring. */
  ringGap?: number;
  /** v0.34.8 (D-2026-05-31-V) — angle source.
   *  - ``"distribute"`` (default): ring 1 members equal-spaced on the
   *    full circle from -π/2; ring k>=2 fans around its parent's angle.
   *    Used by Services / FeatureDetail (``"radial"`` layout button).
   *  - ``"preserve"``: each reachable node keeps the angle it CURRENTLY
   *    has from the hub centre; only its distance is normalised to its
   *    BFS depth ring. This is the floating-canvas (Foundation + Actors)
   *    auto-layout — it preserves the side the user placed each node on
   *    (no swap) while guaranteeing a deeper node sits farther out (no
   *    edge crossing). See SPEC.md §Auto-layout. */
  angleMode?: "distribute" | "preserve";
}

export interface RadialLayoutOutput {
  /** New top-left position per non-hub node id. Hub is omitted because
   *  radial layout never moves it. */
  positions: Map<string, { x: number; y: number }>;
}

const DEFAULT_RING_GAP = 40;

/** v0.37.2 (D-2026-06-01-A) — enforce a minimum angular gap between the
 *  nodes on one ring so none overlap at ``radius``. ``minArc`` is the
 *  required centre-to-centre arc length (≈ node span + gap); the gap in
 *  radians is ``minArc / radius``. Nodes keep their relative order (sorted
 *  by current angle, ties by id); the fan is recentred on the cluster's
 *  middle node so the side the user placed them on is preserved. If the
 *  ring can't fit even around the full circle, falls back to even spacing.
 *  Mutates ``angleByNode`` in place. */
function spreadRingAngles(
  ids: string[],
  angleByNode: Map<string, number>,
  radius: number,
  minArc: number,
): void {
  if (ids.length <= 1 || radius <= 0) return;
  const minGap = minArc / radius;
  const sorted = ids
    .slice()
    .sort((a, b) => angleByNode.get(a)! - angleByNode.get(b)! || a.localeCompare(b));
  const n = sorted.length;
  const mid = Math.floor((n - 1) / 2);
  const origMidAngle = angleByNode.get(sorted[mid])!;

  if (n * minGap >= 2 * Math.PI) {
    const step = (2 * Math.PI) / n;
    sorted.forEach((id, i) => angleByNode.set(id, origMidAngle + (i - mid) * step));
    return;
  }
  // Forward pass: push each node to at least minGap past its predecessor.
  for (let i = 1; i < n; i++) {
    const prev = angleByNode.get(sorted[i - 1])!;
    const cur = angleByNode.get(sorted[i])!;
    if (cur - prev < minGap) angleByNode.set(sorted[i], prev + minGap);
  }
  // Recentre so the middle node returns to (about) its original angle —
  // keeps the fan on the side the user placed the cluster.
  const shift = origMidAngle - angleByNode.get(sorted[mid])!;
  for (const id of sorted) angleByNode.set(id, angleByNode.get(id)! + shift);
}

export function computeRadialLayout(input: RadialLayoutInput): RadialLayoutOutput {
  const ringGap = input.ringGap ?? DEFAULT_RING_GAP;
  const { hub, nodes, edges } = input;

  const hubCx = hub.x + hub.width / 2;
  const hubCy = hub.y + hub.height / 2;

  // Undirected adjacency. Edge endpoints are node ids; the hub id may
  // or may not be referenced.
  const adj = new Map<string, Set<string>>();
  const addEdge = (a: string, b: string) => {
    if (!adj.has(a)) adj.set(a, new Set());
    adj.get(a)!.add(b);
  };
  for (const e of edges) {
    addEdge(e.source, e.target);
    addEdge(e.target, e.source);
  }

  // BFS from the hub. Nodes unreachable from the hub stay out of
  // ``ringByNode`` and land in the orphan grid below.
  // v0.26.3 (D-2026-05-25-D) — also record each node's BFS parent so
  // ring k>=2 members can fan around their parent's angle instead of
  // all collapsing onto -π/2 (top).
  const ringByNode = new Map<string, number>();
  const parentOf = new Map<string, string>();
  ringByNode.set(hub.id, 0);
  const queue: string[] = [hub.id];
  while (queue.length > 0) {
    const cur = queue.shift()!;
    const curRing = ringByNode.get(cur)!;
    const neighbours = [...(adj.get(cur) ?? [])].sort();
    for (const nb of neighbours) {
      if (ringByNode.has(nb)) continue;
      ringByNode.set(nb, curRing + 1);
      parentOf.set(nb, cur);
      queue.push(nb);
    }
  }

  // Group reachable nodes (skip hub itself) by ring level.
  const ringMembers = new Map<number, string[]>();
  for (const n of nodes) {
    if (n.id === hub.id) continue;
    const k = ringByNode.get(n.id);
    if (k === undefined) continue;
    if (!ringMembers.has(k)) ringMembers.set(k, []);
    ringMembers.get(k)!.push(n.id);
  }
  for (const ids of ringMembers.values()) ids.sort();

  // Size lookup. The hub may be a synthetic node not in ``nodes``, so
  // seed it explicitly.
  const sizeById = new Map<string, { w: number; h: number }>();
  for (const n of nodes) sizeById.set(n.id, { w: n.width, h: n.height });
  sizeById.set(hub.id, { w: hub.width, h: hub.height });

  // v0.26.3 (D-2026-05-25-D) — two-pass placement:
  //   pass 1 → assign each node an angle (ring 1 equal-distributed on
  //            the full circle; ring k>=2 fans around its parent's
  //            angle so a chain of length-1 spokes follows a single
  //            radial line rather than all collapsing onto the top).
  //   pass 2 → ring-by-ring radius accumulation + final positions.
  const positions = new Map<string, { x: number; y: number }>();
  const sortedRings = [...ringMembers.keys()].sort((a, b) => a - b);

  const angleMode = input.angleMode ?? "distribute";

  // v0.34.8 (D-2026-05-31-V) — "preserve" mode: each reachable node
  // keeps the angle it currently has from the hub centre. Distance is
  // still normalised below to the BFS depth ring. A node sitting exactly
  // on the hub centre (degenerate) falls back to -π/2 (top) so the result
  // stays deterministic.
  const angleByNode = new Map<string, number>();
  if (angleMode === "preserve") {
    const centerById = new Map<string, { x: number; y: number }>();
    for (const n of nodes) {
      centerById.set(n.id, { x: n.x + n.width / 2, y: n.y + n.height / 2 });
    }
    for (const k of sortedRings) {
      for (const id of ringMembers.get(k)!) {
        const c = centerById.get(id);
        const dx = c ? c.x - hubCx : 0;
        const dy = c ? c.y - hubCy : 0;
        angleByNode.set(id, dx === 0 && dy === 0 ? -Math.PI / 2 : Math.atan2(dy, dx));
      }
    }
  } else {
    for (const k of sortedRings) {
      const ids = ringMembers.get(k)!;
      if (k === 1) {
        const count = ids.length;
        const angleStep = (2 * Math.PI) / count;
        const angleStart = -Math.PI / 2;
        ids.forEach((id, i) => {
          angleByNode.set(id, angleStart + i * angleStep);
        });
        continue;
      }
      // Ring k>=2: group by parent + fan around parent's angle.
      const byParent = new Map<string, string[]>();
      for (const id of ids) {
        const p = parentOf.get(id) ?? hub.id;
        const arr = byParent.get(p) ?? [];
        arr.push(id);
        byParent.set(p, arr);
      }
      for (const [parentId, children] of byParent) {
        children.sort();
        const parentAngle = angleByNode.get(parentId) ?? -Math.PI / 2;
        // Fan narrows as the tree deepens — π/(k+1) gives π/3, π/4, π/5
        // for rings 2, 3, 4. Reads as a tree spreading outward without
        // siblings from different parents colliding.
        const fanWidth = Math.PI / (k + 1);
        if (children.length === 1) {
          angleByNode.set(children[0], parentAngle);
        } else {
          const step = fanWidth / (children.length - 1);
          const start = parentAngle - fanWidth / 2;
          children.forEach((id, i) => {
            angleByNode.set(id, start + i * step);
          });
        }
      }
    }
  }

  let cumulativeRadius = 0;
  for (const k of sortedRings) {
    const ids = ringMembers.get(k)!;
    const ringSpan = Math.max(
      ...ids.map((id) => {
        const s = sizeById.get(id)!;
        return Math.max(s.w, s.h);
      }),
    );
    const minArc = ringSpan + ringGap;
    if (k === 1) {
      const hubSpan = Math.max(hub.width, hub.height);
      cumulativeRadius = hubSpan / 2 + ringSpan / 2 + ringGap;
    } else {
      cumulativeRadius += ringSpan + ringGap;
    }
    // v0.37.2 (D-2026-06-01-A) — collision avoidance, two parts:
    // (1) the ring must be big enough for all its nodes to fit around the
    //     circle without overlap — circumference (2π·r) ≥ count · node-arc.
    //     Without this, a small inner ring can't hold many wide nodes even
    //     when evenly spread (BANAS Services: 7 wide categories on ring 1).
    // (2) fan apart nodes whose angles sit closer than one node-span + gap.
    //     Preserve mode stacks nodes the user placed in a column onto the
    //     same slot ("정렬하면 노드들이 다 겹쳐요"); spreadRingAngles unrolls
    //     them, keeping relative order + recentred on the cluster's middle.
    const requiredRadius = (ids.length * minArc) / (2 * Math.PI);
    cumulativeRadius = Math.max(cumulativeRadius, requiredRadius);
    spreadRingAngles(ids, angleByNode, cumulativeRadius, minArc);
    for (const id of ids) {
      const angle = angleByNode.get(id)!;
      const cx = hubCx + cumulativeRadius * Math.cos(angle);
      const cy = hubCy + cumulativeRadius * Math.sin(angle);
      const s = sizeById.get(id)!;
      positions.set(id, { x: cx - s.w / 2, y: cy - s.h / 2 });
    }
  }

  // Orphans: not reachable from hub. Grid below the outermost ring.
  const orphans = nodes
    .filter((n) => n.id !== hub.id && !ringByNode.has(n.id))
    .map((n) => n.id)
    .sort();
  if (orphans.length > 0) {
    const cellW =
      Math.max(...orphans.map((id) => sizeById.get(id)!.w)) + ringGap;
    const cellH =
      Math.max(...orphans.map((id) => sizeById.get(id)!.h)) + ringGap;
    const cols = Math.max(1, Math.ceil(Math.sqrt(orphans.length)));
    const baseY =
      hubCy + (cumulativeRadius || hub.height / 2) + ringGap * 2;
    const baseX = hubCx - (cols * cellW) / 2;
    orphans.forEach((id, i) => {
      const r = Math.floor(i / cols);
      const c = i % cols;
      const s = sizeById.get(id)!;
      positions.set(id, {
        x: baseX + c * cellW + cellW / 2 - s.w / 2,
        y: baseY + r * cellH + cellH / 2 - s.h / 2,
      });
    });
  }

  return { positions };
}
