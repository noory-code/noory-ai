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

  const connectedIds = new Set<string>();
  // v0.26.0 (D-2026-05-25-A) — directed edges are the only source of
  // hierarchy. Undirected edges are still considered "connections"
  // (so dagre can lay them out), but ``parent_id``-implicit edges no
  // longer exist.
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
export interface RadialAnchor {
  x: number;
  y: number;
  width: number;
  height: number;
}

export function radialLayout(
  doc: CanvasDoc,
  options: { anchorId?: string; anchorOverride?: RadialAnchor } = {},
): CanvasDoc {
  const { anchorId = "project", anchorOverride } = options;
  // v0.13: the project anchor lives in ProjectDoc.anchors and is rendered
  // as a synthetic node — it's not in doc.nodes. SketchCanvas passes its
  // current placement via ``anchorOverride`` so radial still has a centre
  // to spread peers around. v0.12 fall-back: look for a kind=project node
  // in doc.nodes (legacy data only).
  const anchor =
    anchorOverride ?? doc.nodes.find((n) => n.id === anchorId);
  if (!anchor) return autoLayout(doc); // fall back if no anchor

  // Anchor centre stays where the user has it.
  const cx = anchor.x + anchor.width / 2;
  const cy = anchor.y + anchor.height / 2;

  // Filter out the anchor *if* it happened to be in doc.nodes (legacy
  // path). For v0.13 anchorOverride, every doc node is a peer.
  const others = anchorOverride
    ? doc.nodes
    : doc.nodes.filter((n) => n.id !== anchorId);
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

  // Spread pairs that are too close in angle so they don't visually
  // overlap on the ring. Minimum separation is the arc length each node
  // needs (largest dim + padding) divided by the ring radius — i.e. the
  // tightest angle that keeps nodes from touching. Walk sorted by angle
  // and nudge any that are tighter; if the chain wraps past 2π, distribute
  // evenly as a fallback so we don't pile everything to one side.
  angled.sort((a, b) => a.theta - b.theta);
  const padding = 24;
  const minSep = Math.min(
    Math.PI / 2,
    (maxOtherDim + padding) / radius,
  );
  for (let i = 1; i < angled.length; i += 1) {
    if (angled[i].theta - angled[i - 1].theta < minSep) {
      angled[i].theta = angled[i - 1].theta + minSep;
    }
  }
  // If the spreading pushed the last node past the first by more than 2π,
  // the user's input was too clustered to spread cleanly — distribute
  // evenly around the full circle starting at the first node's angle.
  const span = angled[angled.length - 1].theta - angled[0].theta;
  if (span > 2 * Math.PI - minSep) {
    const start = angled[0].theta;
    const step = (2 * Math.PI) / angled.length;
    for (let i = 0; i < angled.length; i += 1) {
      angled[i].theta = start + i * step;
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
