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

  const nodeIds = new Set(doc.nodes.map((n) => n.id));
  const connectedIds = new Set<string>();
  // Explicit edges.
  for (const e of doc.edges) {
    connectedIds.add(e.source);
    connectedIds.add(e.target);
  }
  // ``parent_id`` acts as an implicit decomposition edge, so Core /
  // Actors / Services-detail canvases — which rarely have explicit edges
  // between the new node kinds — still get arranged.
  for (const n of doc.nodes) {
    if (n.parent_id && nodeIds.has(n.parent_id)) {
      connectedIds.add(n.id);
      connectedIds.add(n.parent_id);
    }
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
  for (const n of doc.nodes) {
    if (n.parent_id && g.hasNode(n.parent_id) && g.hasNode(n.id)) {
      g.setEdge(n.parent_id, n.id);
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
