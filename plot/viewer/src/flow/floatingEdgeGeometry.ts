// Floating-edge geometry — v0.30.3 (D-2026-05-31-F).
//
// "Connect from any side, identically": an edge floats to the point on
// each node's border that faces the other node, instead of attaching to
// a fixed per-side handle. This removes the asymmetric-handle problem
// (a node could only emit from its right/bottom, forcing awkward loops
// when the target sat on its left/top).
//
// `nodeBorderPoint` returns the point on `node`'s rectangle border along
// the line from `node`'s centre toward `target`'s centre — the standard
// React Flow floating-edge intersection formula. Circle nodes (the
// anchor) are approximated by their bounding box, which is visually
// indistinguishable at these radii.
//
// Pure module (no React) — unit-testable; the FloatingEdge component is
// a thin consumer.

export interface NodeRect {
  /** top-left absolute x */
  x: number;
  /** top-left absolute y */
  y: number;
  width: number;
  height: number;
}

/** A node whose border is an ellipse (circle = the w===h case) rather than a
 *  rectangle — the round project anchor + any user circle/ellipse node. */
export type BorderShape = "rect" | "ellipse";

/** True for shapes that should use the ellipse border (v0.34.6). */
export function isEllipseShape(shape: string | null | undefined): boolean {
  return shape === "circle" || shape === "ellipse";
}

/** Point on `node`'s ELLIPSE border facing `target`'s centre — the ray from
 *  the centre toward the target intersected with the ellipse. */
function ellipseBorderPoint(node: NodeRect, target: NodeRect): { x: number; y: number } {
  const w = node.width / 2;
  const h = node.height / 2;
  const cx = node.x + w;
  const cy = node.y + h;
  const ux = target.x + target.width / 2 - cx;
  const uy = target.y + target.height / 2 - cy;
  if (w === 0 || h === 0 || (ux === 0 && uy === 0)) return { x: cx, y: cy };
  const s = 1 / Math.sqrt((ux / w) ** 2 + (uy / h) ** 2);
  return { x: cx + ux * s, y: cy + uy * s };
}

/** Point on `node`'s border facing `target`'s centre. Rectangle by default;
 *  ellipse when `shape === "ellipse"` (v0.34.6 — fixes arrows that floated
 *  off the round anchor because it was approximated by its bounding box). */
export function nodeBorderPoint(
  node: NodeRect,
  target: NodeRect,
  shape: BorderShape = "rect",
): { x: number; y: number } {
  if (shape === "ellipse") return ellipseBorderPoint(node, target);
  const w = node.width / 2;
  const h = node.height / 2;
  const cx = node.x + w;
  const cy = node.y + h;
  const tx = target.x + target.width / 2;
  const ty = target.y + target.height / 2;

  if (w === 0 || h === 0) return { x: cx, y: cy };

  const dx = (tx - cx) / (2 * w);
  const dy = (ty - cy) / (2 * h);
  const xx1 = dx - dy;
  const yy1 = dx + dy;
  const denom = Math.abs(xx1) + Math.abs(yy1);
  if (denom === 0) return { x: cx, y: cy }; // coincident centres

  const a = 1 / denom;
  const xx3 = a * xx1;
  const yy3 = a * yy1;
  return {
    x: w * (xx3 + yy3) + cx,
    y: h * (-xx3 + yy3) + cy,
  };
}

export type BorderSide = "top" | "right" | "bottom" | "left";

/** Which border side a point sits on, relative to `node`'s centre. Used to
 *  aim a bezier control point perpendicular to the side the floating
 *  endpoint exits (v0.34.5). */
export function borderSide(px: number, py: number, node: NodeRect): BorderSide {
  const hw = node.width / 2 || 1;
  const hh = node.height / 2 || 1;
  const dx = (px - (node.x + hw)) / hw;
  const dy = (py - (node.y + hh)) / hh;
  if (Math.abs(dx) >= Math.abs(dy)) return dx >= 0 ? "right" : "left";
  return dy >= 0 ? "bottom" : "top";
}

/** Both border points for an edge between `source` and `target`, each
 *  honoring its own border shape. */
export function floatingEndpoints(
  source: NodeRect,
  target: NodeRect,
  sourceShape: BorderShape = "rect",
  targetShape: BorderShape = "rect",
): { sx: number; sy: number; tx: number; ty: number } {
  const s = nodeBorderPoint(source, target, sourceShape);
  const t = nodeBorderPoint(target, source, targetShape);
  return { sx: s.x, sy: s.y, tx: t.x, ty: t.y };
}
