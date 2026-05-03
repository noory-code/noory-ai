import dagre from "dagre";
import type { CanvasDoc } from "../types";

export type LayoutDirection = "LR" | "TB" | "RL" | "BT";

/**
 * Return a new doc where node x/y have been arranged by dagre.
 *
 * Orphan nodes (no edges) remain in their original positions so that users
 * can still auto-arrange a partial graph without losing off-tree notes.
 */
export function autoLayout(doc: CanvasDoc, direction: LayoutDirection = "LR"): CanvasDoc {
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

/**
 * v0.12.4 — radial tidy for canvases that aren't trees. The project anchor
 * stays put; every other node keeps the **angle** it currently has relative
 * to the anchor, and is moved onto a common ring at that angle. So if the
 * user dragged Identity to the left and Core Value to the right, those
 * sides are preserved — auto-layout only normalises the distance and
 * removes overlap.
 *
 * v0.12.5 correction: previous version placed nodes in `doc.nodes` order
 * around the ring (top → clockwise), which felt arbitrary. The user's
 * expectation is "tidy where I put it," not "redo from scratch."
 *
 * Use for Foundation and Actors (project + peers) where dagre LR's layered
 * left-to-right output collapses the radial mental model into a horizontal
 * row.
 */
export function radialLayout(doc: CanvasDoc, anchorId = "project"): CanvasDoc {
  const anchor = doc.nodes.find((n) => n.id === anchorId);
  if (!anchor) return autoLayout(doc); // fall back if no anchor

  // Anchor centre stays where the user has it.
  const cx = anchor.x + anchor.width / 2;
  const cy = anchor.y + anchor.height / 2;

  const others = doc.nodes.filter((n) => n.id !== anchorId);
  if (others.length === 0) return doc;

  const maxOtherDim = others.reduce(
    (m, n) => Math.max(m, n.width, n.height),
    0,
  );
  const anchorReach = Math.max(anchor.width, anchor.height) / 2;
  const radius = Math.max(220, anchorReach + maxOtherDim / 2 + 80);

  // Compute each node's current angle from the anchor; if the node sits
  // exactly on top of the anchor (atan2(0, 0) = 0 → 3 o'clock), drift it
  // by index so colocated seeds spread out instead of stacking.
  const angled = others.map((n, i) => {
    const ncx = n.x + n.width / 2;
    const ncy = n.y + n.height / 2;
    const dx = ncx - cx;
    const dy = ncy - cy;
    let theta: number;
    if (dx === 0 && dy === 0) {
      theta = -Math.PI / 2 + (i * 2 * Math.PI) / others.length;
    } else {
      theta = Math.atan2(dy, dx);
    }
    return { node: n, theta };
  });

  // Spread any pair that ends up too close in angle (< ~15°) so they don't
  // visually overlap on the ring. Sort by angle, walk through, nudge.
  angled.sort((a, b) => a.theta - b.theta);
  const minSep = (15 * Math.PI) / 180;
  for (let i = 1; i < angled.length; i += 1) {
    if (angled[i].theta - angled[i - 1].theta < minSep) {
      angled[i].theta = angled[i - 1].theta + minSep;
    }
  }

  const placedById = new Map<string, { x: number; y: number }>();
  for (const { node, theta } of angled) {
    const x = cx + radius * Math.cos(theta) - node.width / 2;
    const y = cy + radius * Math.sin(theta) - node.height / 2;
    placedById.set(node.id, { x, y });
  }

  return {
    ...doc,
    nodes: doc.nodes.map((node) => {
      const p = placedById.get(node.id);
      return p ? { ...node, x: p.x, y: p.y } : node;
    }),
  };
}
