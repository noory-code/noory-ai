// Auto-layout — mindmap-style directional tree.
//
// Per SPEC.md §Auto-layout and DECISIONS.md D-2026-05-10-E:
// - Anchor is the layout root and stays fixed in place.
// - BFS from anchor builds a spanning tree; cycle-closing edges are
//   ignored for placement (they are still drawn elsewhere).
// - Each child is placed in the direction (T/R/B/L) of the parent-side
//   handle of the connecting edge.
// - R/L children stack in a vertical column to the parent's right/left.
// - T/B children stack in a horizontal row above/below the parent.
// - Recursion uses each child's own incoming-edge handle. Direction is
//   absolute (T = absolute up).
// - Sibling spacing tracks subtree extents (Reingold-Tilford-style) so
//   node footprints never overlap. ``padding`` defaults to 32 px.
// - Determinism: ties broken by node id everywhere.
//
// Pure module — no React imports.

import type { SketchEdge, SketchNode } from "../../types";

export type Direction = "T" | "R" | "B" | "L";

const DEFAULT_PADDING = 32;

export interface AutoLayoutAnchor {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface AutoLayoutInput {
  nodes: SketchNode[];
  edges: SketchEdge[];
  anchor: AutoLayoutAnchor;
  padding?: number;
}

export interface AutoLayoutOutput {
  /** New top-left position per non-anchor node id. Anchor is omitted
   *  because auto-layout never moves it. */
  positions: Map<string, { x: number; y: number }>;
}

interface NodeSize {
  width: number;
  height: number;
}

interface NodeCenterPos {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface AdjEntry {
  neighborId: string;
  /** The direction of the neighbor IF the current node is the parent in
   *  the spanning tree. Computed from the parent-side handle. */
  parentSideDir: Direction;
}

interface SubtreeLayout {
  bbox: { minX: number; minY: number; maxX: number; maxY: number };
  /** Center positions, relative to root at (0, 0). */
  positions: Map<string, { x: number; y: number }>;
}

export function computeAutoLayout(input: AutoLayoutInput): AutoLayoutOutput {
  const padding = input.padding ?? DEFAULT_PADDING;
  if (input.nodes.length === 0) return { positions: new Map() };

  const nodeSizes = new Map<string, NodeSize>();
  nodeSizes.set(input.anchor.id, {
    width: input.anchor.width,
    height: input.anchor.height,
  });
  for (const n of input.nodes) {
    nodeSizes.set(n.id, { width: n.width, height: n.height });
  }

  const nodeCenters = new Map<string, NodeCenterPos>();
  nodeCenters.set(input.anchor.id, {
    x: input.anchor.x + input.anchor.width / 2,
    y: input.anchor.y + input.anchor.height / 2,
    width: input.anchor.width,
    height: input.anchor.height,
  });
  for (const n of input.nodes) {
    nodeCenters.set(n.id, {
      x: n.x + n.width / 2,
      y: n.y + n.height / 2,
      width: n.width,
      height: n.height,
    });
  }

  const adj = buildAdjacency(input.edges, nodeCenters);
  const tree = bfsSpanningTree(input.anchor.id, adj);

  const rootSub = layoutSubtree(input.anchor.id, tree, nodeSizes, padding);

  const anchorCx = input.anchor.x + input.anchor.width / 2;
  const anchorCy = input.anchor.y + input.anchor.height / 2;

  const positions = new Map<string, { x: number; y: number }>();
  for (const [id, center] of rootSub.positions) {
    if (id === input.anchor.id) continue;
    const size = nodeSizes.get(id)!;
    positions.set(id, {
      x: anchorCx + center.x - size.width / 2,
      y: anchorCy + center.y - size.height / 2,
    });
  }

  // Isolated nodes — not visited by BFS. Place to anchor's lower-right
  // empty quadrant in id order, in a vertical column.
  const visited = new Set(rootSub.positions.keys());
  const isolated = input.nodes.filter((n) => !visited.has(n.id));
  if (isolated.length > 0) {
    isolated.sort((a, b) => a.id.localeCompare(b.id));
    const startX = anchorCx + rootSub.bbox.maxX + padding * 4;
    let cursorY = anchorCy + rootSub.bbox.maxY + padding * 2;
    for (const n of isolated) {
      positions.set(n.id, { x: startX, y: cursorY });
      cursorY += n.height + padding;
    }
  }

  return { positions };
}

function buildAdjacency(
  edges: SketchEdge[],
  nodeCenters: Map<string, NodeCenterPos>,
): Map<string, AdjEntry[]> {
  const adj = new Map<string, AdjEntry[]>();
  const push = (parentId: string, childId: string, parentHandle: string | null) => {
    if (!adj.has(parentId)) adj.set(parentId, []);
    let dir: Direction;
    if (parentHandle) {
      dir = handleToDirection(parentHandle);
    } else {
      const parentPos = nodeCenters.get(parentId);
      const childPos = nodeCenters.get(childId);
      dir = parentPos && childPos ? inferDirection(parentPos, childPos) : "R";
    }
    adj.get(parentId)!.push({ neighborId: childId, parentSideDir: dir });
  };
  for (const e of edges) {
    push(e.source, e.target, e.sourceHandle);
    push(e.target, e.source, e.targetHandle);
  }
  return adj;
}

function bfsSpanningTree(
  rootId: string,
  adj: Map<string, AdjEntry[]>,
): Map<string, Array<{ childId: string; dir: Direction }>> {
  const tree = new Map<string, Array<{ childId: string; dir: Direction }>>();
  const visited = new Set<string>([rootId]);
  const queue: string[] = [rootId];
  while (queue.length > 0) {
    const cur = queue.shift()!;
    const neighbors = (adj.get(cur) ?? [])
      .slice()
      .sort((a, b) => a.neighborId.localeCompare(b.neighborId));
    for (const n of neighbors) {
      if (visited.has(n.neighborId)) continue;
      visited.add(n.neighborId);
      if (!tree.has(cur)) tree.set(cur, []);
      tree.get(cur)!.push({ childId: n.neighborId, dir: n.parentSideDir });
      queue.push(n.neighborId);
    }
  }
  return tree;
}

function layoutSubtree(
  rootId: string,
  tree: Map<string, Array<{ childId: string; dir: Direction }>>,
  nodeSizes: Map<string, NodeSize>,
  padding: number,
): SubtreeLayout {
  const rootSize = nodeSizes.get(rootId)!;
  const positions = new Map<string, { x: number; y: number }>();
  positions.set(rootId, { x: 0, y: 0 });

  const bbox = {
    minX: -rootSize.width / 2,
    minY: -rootSize.height / 2,
    maxX: rootSize.width / 2,
    maxY: rootSize.height / 2,
  };

  const children = (tree.get(rootId) ?? []).slice();
  children.sort((a, b) => {
    if (a.dir !== b.dir) return a.dir.localeCompare(b.dir);
    return a.childId.localeCompare(b.childId);
  });

  const byDir: Record<Direction, SubtreeLayout[]> = { T: [], R: [], B: [], L: [] };
  for (const c of children) {
    byDir[c.dir].push(layoutSubtree(c.childId, tree, nodeSizes, padding));
  }

  for (const dir of ["T", "R", "B", "L"] as const) {
    const subs = byDir[dir];
    if (subs.length === 0) continue;
    placeInDirection(dir, subs, rootSize, padding, positions, bbox);
  }

  return { bbox, positions };
}

function placeInDirection(
  dir: Direction,
  subs: SubtreeLayout[],
  rootSize: NodeSize,
  padding: number,
  positions: Map<string, { x: number; y: number }>,
  bbox: { minX: number; minY: number; maxX: number; maxY: number },
): void {
  const isVertical = dir === "R" || dir === "L";

  if (isVertical) {
    const heights = subs.map((s) => s.bbox.maxY - s.bbox.minY);
    const totalH = heights.reduce((a, b) => a + b, 0) + (subs.length - 1) * padding;
    let cursorY = -totalH / 2;
    const rootEdgeX = dir === "R" ? rootSize.width / 2 : -rootSize.width / 2;

    for (let i = 0; i < subs.length; i++) {
      const sub = subs[i];
      const subH = heights[i];
      const subCenterY = cursorY + subH / 2;
      const subMidY = (sub.bbox.minY + sub.bbox.maxY) / 2;
      const shiftY = subCenterY - subMidY;
      const shiftX =
        dir === "R" ? rootEdgeX + padding - sub.bbox.minX : rootEdgeX - padding - sub.bbox.maxX;

      for (const [id, pos] of sub.positions) {
        positions.set(id, { x: pos.x + shiftX, y: pos.y + shiftY });
      }
      bbox.minX = Math.min(bbox.minX, sub.bbox.minX + shiftX);
      bbox.maxX = Math.max(bbox.maxX, sub.bbox.maxX + shiftX);
      bbox.minY = Math.min(bbox.minY, sub.bbox.minY + shiftY);
      bbox.maxY = Math.max(bbox.maxY, sub.bbox.maxY + shiftY);
      cursorY += subH + padding;
    }
  } else {
    const widths = subs.map((s) => s.bbox.maxX - s.bbox.minX);
    const totalW = widths.reduce((a, b) => a + b, 0) + (subs.length - 1) * padding;
    let cursorX = -totalW / 2;
    const rootEdgeY = dir === "B" ? rootSize.height / 2 : -rootSize.height / 2;

    for (let i = 0; i < subs.length; i++) {
      const sub = subs[i];
      const subW = widths[i];
      const subCenterX = cursorX + subW / 2;
      const subMidX = (sub.bbox.minX + sub.bbox.maxX) / 2;
      const shiftX = subCenterX - subMidX;
      const shiftY =
        dir === "B" ? rootEdgeY + padding - sub.bbox.minY : rootEdgeY - padding - sub.bbox.maxY;

      for (const [id, pos] of sub.positions) {
        positions.set(id, { x: pos.x + shiftX, y: pos.y + shiftY });
      }
      bbox.minX = Math.min(bbox.minX, sub.bbox.minX + shiftX);
      bbox.maxX = Math.max(bbox.maxX, sub.bbox.maxX + shiftX);
      bbox.minY = Math.min(bbox.minY, sub.bbox.minY + shiftY);
      bbox.maxY = Math.max(bbox.maxY, sub.bbox.maxY + shiftY);
      cursorX += subW + padding;
    }
  }
}

export function handleToDirection(handle: string): Direction {
  const h = handle.toLowerCase();
  if (h.startsWith("t")) return "T";
  if (h.startsWith("r")) return "R";
  if (h.startsWith("b")) return "B";
  if (h.startsWith("l")) return "L";
  return "R";
}

export function inferDirection(
  from: { x: number; y: number },
  to: { x: number; y: number },
): Direction {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  if (Math.abs(dx) > Math.abs(dy)) return dx > 0 ? "R" : "L";
  return dy > 0 ? "B" : "T";
}
