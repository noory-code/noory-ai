// Anchor-ward orientation helper — v0.34.4 (D-2026-05-31-R).
//
// On the Foundation + Actors canvases every directed edge must point
// TOWARD the project anchor — Foundation elements (mission / core_value /
// identity) converge to BECOME the service; actors PARTICIPATE in it. The
// arrow therefore points at whichever endpoint is *nearer the anchor*, even
// for edges that don't touch the anchor directly (e.g. the actor
// inheritance tree's child→parent edges point up toward the root).
//
// Pure module (no React) — unit-testable; consumed by both ``edgeTransform``
// (render orientation) and ``handleConnect`` (creation normalization) so the
// same rule applies however an edge is drawn.
import type { CanvasDoc } from "../../types";

/** BFS hop-distance of every node from ``anchorId`` over the edge graph
 *  (treated as undirected). Unreachable nodes are absent from the map. */
export function anchorDistances(
  edges: CanvasDoc["edges"],
  anchorId: string,
): Map<string, number> {
  const adj = new Map<string, string[]>();
  const link = (a: string, b: string) => {
    const arr = adj.get(a);
    if (arr) arr.push(b);
    else adj.set(a, [b]);
  };
  for (const e of edges) {
    link(e.source, e.target);
    link(e.target, e.source);
  }
  const dist = new Map<string, number>([[anchorId, 0]]);
  const queue = [anchorId];
  for (let i = 0; i < queue.length; i++) {
    const cur = queue[i];
    const d = dist.get(cur)!;
    for (const nb of adj.get(cur) ?? []) {
      if (!dist.has(nb)) {
        dist.set(nb, d + 1);
        queue.push(nb);
      }
    }
  }
  return dist;
}

/** True when ``source`` is the anchor-ward endpoint (so the arrow should
 *  point at it). Closer-to-anchor wins; unreachable loses; ties keep order. */
export function sourceIsAnchorWard(
  dist: Map<string, number>,
  source: string,
  target: string,
): boolean {
  const ds = dist.get(source);
  const dt = dist.get(target);
  if (ds === undefined) return false;
  if (dt === undefined) return true;
  return ds < dt;
}
