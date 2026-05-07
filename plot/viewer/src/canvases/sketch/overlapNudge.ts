// Pure spatial helpers for drag/drop. No React imports — usable from
// any module, unit-testable in isolation.
import type { SketchNode as DocNode } from "../../types";

/** Walk the parent chain to compute a node's absolute position. */
function absolutePos(
  n: DocNode,
  nodeById: Map<string, DocNode>,
): { x: number; y: number } {
  let ax = n.x;
  let ay = n.y;
  let cur: DocNode | undefined = n;
  while (cur?.parent_id) {
    const parent = nodeById.get(cur.parent_id);
    if (!parent) break;
    ax += parent.x;
    ay += parent.y;
    cur = parent;
  }
  return { x: ax, y: ay };
}

/**
 * Hit-test: first node (in reverse doc order so top-rendered wins)
 * whose absolute bounding box contains the given flow point. SPEC
 * §Drag-and-drop "Hit-test order": last-drawn first so nested
 * containers can win over their (earlier-rendered) parents.
 */
export function containerAtFlowPoint(
  nodes: DocNode[],
  nodeById: Map<string, DocNode>,
  x: number,
  y: number,
): DocNode | null {
  for (let i = nodes.length - 1; i >= 0; i--) {
    const n = nodes[i];
    const { x: ax, y: ay } = absolutePos(n, nodeById);
    if (x >= ax && x <= ax + n.width && y >= ay && y <= ay + n.height) {
      return n;
    }
  }
  return null;
}

/**
 * Slide a rectangle off siblings it overlaps. Walks diagonally by
 * ``OFFSET_STEP`` px up to ``MAX_STEPS`` tries. Caller passes the list
 * of existing node rects in the same coordinate space — nested drops
 * use parent-local coords, free drops use absolute coords.
 */
export function findFreeSpot(
  baseX: number,
  baseY: number,
  w: number,
  h: number,
  siblings: { x: number; y: number; width: number; height: number }[],
): { x: number; y: number } {
  const OFFSET_STEP = 32;
  const MAX_STEPS = 24;
  const overlaps = (
    a: [number, number, number, number],
    b: [number, number, number, number],
  ): boolean =>
    !(a[2] <= b[0] || b[2] <= a[0] || a[3] <= b[1] || b[3] <= a[1]);
  let x = baseX;
  let y = baseY;
  for (let i = 0; i < MAX_STEPS; i++) {
    const mine: [number, number, number, number] = [x, y, x + w, y + h];
    const collision = siblings.some((s) =>
      overlaps(mine, [s.x, s.y, s.x + s.width, s.y + s.height]),
    );
    if (!collision) return { x, y };
    x += OFFSET_STEP;
    y += OFFSET_STEP;
  }
  return { x, y }; // gave up — place at final nudged position
}
