import dagre from "dagre";
import type { SketchDoc } from "../types";

export type LayoutDirection = "LR" | "TB" | "RL" | "BT";

/**
 * Return a new doc where node x/y have been arranged by dagre.
 *
 * Orphan nodes (no edges) remain in their original positions so that users
 * can still auto-arrange a partial graph without losing off-tree notes.
 */
export function autoLayout(doc: SketchDoc, direction: LayoutDirection = "LR"): SketchDoc {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: direction, nodesep: 40, ranksep: 100, marginx: 20, marginy: 20 });
  g.setDefaultEdgeLabel(() => ({}));

  const connectedIds = new Set<string>();
  for (const e of doc.edges) {
    connectedIds.add(e.source);
    connectedIds.add(e.target);
  }

  for (const n of doc.nodes) {
    if (!connectedIds.has(n.id)) continue;
    g.setNode(n.id, { width: n.width, height: n.height });
  }
  for (const e of doc.edges) {
    if (g.hasNode(e.source) && g.hasNode(e.target)) {
      g.setEdge(e.source, e.target);
    }
  }

  dagre.layout(g);

  return {
    ...doc,
    nodes: doc.nodes.map((n) => {
      if (!connectedIds.has(n.id)) return n;
      const placed = g.node(n.id);
      if (!placed) return n;
      return { ...n, x: placed.x - n.width / 2, y: placed.y - n.height / 2 };
    }),
  };
}
