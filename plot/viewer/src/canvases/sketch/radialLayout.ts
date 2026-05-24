// Radial auto-layout — hub-and-spoke pattern.
//
// Per SPEC.md §Auto-layout and DECISIONS.md D-2026-05-24-B:
// - A single hub node is the layout origin (anchor for Services; the
//   hidden root-service for ServiceDetail). The hub itself is never
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
}

export interface RadialLayoutOutput {
  /** New top-left position per non-hub node id. Hub is omitted because
   *  radial layout never moves it. */
  positions: Map<string, { x: number; y: number }>;
}

const DEFAULT_RING_GAP = 40;

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
  const ringByNode = new Map<string, number>();
  ringByNode.set(hub.id, 0);
  const queue: string[] = [hub.id];
  while (queue.length > 0) {
    const cur = queue.shift()!;
    const curRing = ringByNode.get(cur)!;
    const neighbours = [...(adj.get(cur) ?? [])].sort();
    for (const nb of neighbours) {
      if (ringByNode.has(nb)) continue;
      ringByNode.set(nb, curRing + 1);
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

  const positions = new Map<string, { x: number; y: number }>();
  const sortedRings = [...ringMembers.keys()].sort((a, b) => a - b);
  let cumulativeRadius = 0;
  for (const k of sortedRings) {
    const ids = ringMembers.get(k)!;
    const ringSpan = Math.max(
      ...ids.map((id) => {
        const s = sizeById.get(id)!;
        return Math.max(s.w, s.h);
      }),
    );
    if (k === 1) {
      const hubSpan = Math.max(hub.width, hub.height);
      cumulativeRadius = hubSpan / 2 + ringSpan / 2 + ringGap;
    } else {
      cumulativeRadius += ringSpan + ringGap;
    }
    const count = ids.length;
    const angleStep = (2 * Math.PI) / count;
    const angleStart = -Math.PI / 2;
    for (let i = 0; i < count; i++) {
      const id = ids[i];
      const angle = angleStart + i * angleStep;
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
