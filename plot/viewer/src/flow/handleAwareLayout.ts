// D-2026-05-28-G — Handle-aware dagre layered layout.
//
// Built for FeatureDetail's "no hub" reconstruction graph (where the
// root-service node is hidden + disconnected per D-2026-05-28-B, so the
// mindmap BFS algorithm in ``canvases/sketch/autoLayout.ts`` has no
// entry point). Wraps dagre with a single twist: for every edge whose
// ``sourceHandle`` indicates the source connects from its LEFT or TOP
// side (i.e. the target is supposed to sit on the source's L/T), we
// swap source and target in dagre's input. dagre's ``rankdir: "LR"``
// then places the swapped target on the left / above as intended, so
// the user's "right handle = on the right" mental model is honoured.
//
// Limitations (honest):
// - dagre is a DAG layout. Cycles are broken by dagre's internal
//   feedback-arc-set pass; one edge of every cycle is silently
//   reversed for layout. Visual ordering on cycles may not match
//   handles exactly. Plot's FeatureDetail graphs are typically
//   actor → interaction → actor pairs (small cycles); the result
//   is still readable but not always pixel-perfect.
// - Orphan nodes (no incident edges) keep their original positions.
//   This matches the pre-existing flow/autoLayout.ts behaviour.

import dagre from "dagre";
import type { CanvasDoc } from "../types";

export type LayeredDirection = "LR" | "TB" | "RL" | "BT";

function isLeftOrTop(handle: string | null | undefined): boolean {
  if (!handle) return false;
  const h = handle.toLowerCase();
  return h.startsWith("l") || h.startsWith("t");
}

export interface HandleAwareLayoutOptions {
  /** Dagre rankdir for the final layout. Defaults to "LR" — matches
   *  Plot's typical actor → interaction → actor flow. */
  direction?: LayeredDirection;
  /** Padding between nodes on the same rank. Default 50. */
  nodesep?: number;
  /** Padding between ranks (e.g. between actor column and interaction
   *  column on an LR layout). Default 100. */
  ranksep?: number;
}

/**
 * Compute a new ``CanvasDoc`` with x/y arranged by dagre, swapping
 * edge direction in the input whenever ``sourceHandle`` faces L or T.
 *
 * Pure — no React imports. Caller threads the result through
 * ``onDocChange`` so the layout lands on the regular undo history.
 */
export function handleAwareLayout(
  doc: CanvasDoc,
  opts: HandleAwareLayoutOptions = {},
): CanvasDoc {
  const { direction = "LR", nodesep = 50, ranksep = 100 } = opts;
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: direction, nodesep, ranksep, marginx: 20, marginy: 20 });
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
    if (!g.hasNode(e.source) || !g.hasNode(e.target)) continue;
    // Swap when the source handle faces L/T so dagre's LR/TB output
    // matches the user's "right handle → right side" expectation.
    if (isLeftOrTop(e.sourceHandle)) {
      g.setEdge(e.target, e.source);
    } else {
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
