/**
 * Anchor-radial initial placement for Foundation kinds (v0.16.11).
 *
 * Per the canonical Plot spec (D-2026-05-12-N), the user explicitly said:
 *
 *   "프로젝트 노드 놓고(앵커) 그 주변에 미션, 코어밸류, 아이덴티티
 *    붙이면 되요. 뭐가 먼저고 말고는 없습니다."
 *
 * = Project (anchor) sits in the centre; Mission / CoreValue / Identity
 * attach *around* it. No narrative order. The visual is "essence's three
 * aspects, all radiating from the project."
 *
 * This module is a pure helper: given the kind to create and the count
 * of existing Foundation nodes already present, return the canvas-space
 * top-left ``{x, y}`` where the new node should land.
 *
 * Only fires for new-node creation on the Foundation canvas; users can
 * drag the node anywhere afterward (positional hint, not constraint).
 * Does *not* emit edges — D-2026-05-04-A (no auto-edges) is preserved.
 */

export const FOUNDATION_RADIAL_KINDS = ["mission", "core_value", "identity"] as const;
export type FoundationRadialKind = (typeof FOUNDATION_RADIAL_KINDS)[number];

/** Canonical anchor centre in canvas coordinates. Matches
 *  ``App.tsx::resolveProjectAnchor`` default: anchor box at
 *  ``(-75, -75)`` size ``150×150`` → centre at (0, 0). */
const ANCHOR_CENTER = { x: 0, y: 0 } as const;

/** Distance from anchor centre to each radial slot. */
const RADIUS = 320;

/** Base angle per kind in clock-face degrees (12 o'clock = 0°,
 *  clockwise). The three angles are 120° apart for visual balance.
 *  No semantic ordering — the user is explicit that "뭐가 먼저고
 *  말고는 없습니다." */
const DEFAULT_ANGLES: Record<FoundationRadialKind, number> = {
  mission: 270,    //  9 o'clock — left of anchor
  core_value: 30,  //  1 o'clock — upper-right of anchor
  identity: 150,   //  5 o'clock — lower-right of anchor
};

/** Offset added per *additional* node of the same kind already on the
 *  canvas. Prevents 2nd / 3rd Mission from stacking on top of the 1st. */
const SAME_KIND_OFFSET_DEG = 30;

export interface ExistingFoundationCounts {
  mission: number;
  core_value: number;
  identity: number;
}

/** Convert clock-face degrees (12 = 0°, clockwise) → canvas x/y on a
 *  circle of radius ``RADIUS`` around ``ANCHOR_CENTER``. */
function slotForDegrees(degrees: number): { x: number; y: number } {
  const rad = (degrees * Math.PI) / 180;
  return {
    x: ANCHOR_CENTER.x + RADIUS * Math.sin(rad),
    y: ANCHOR_CENTER.y - RADIUS * Math.cos(rad),
  };
}

/** Centre of the radial slot for a new node of the given kind, given
 *  how many of each kind are already on the canvas. */
export function anchorRadialSlot(
  kind: FoundationRadialKind,
  existing: ExistingFoundationCounts,
): { x: number; y: number } {
  const baseDeg = DEFAULT_ANGLES[kind];
  const angleDeg = baseDeg + existing[kind] * SAME_KIND_OFFSET_DEG;
  return slotForDegrees(angleDeg);
}

/** Top-left position for a node of the given kind so its *centre*
 *  lands on the radial slot. Defaults match the per-kind blank-node
 *  factory (``DEFAULT_WIDTH`` 180, ``DEFAULT_HEIGHT`` 80). */
export function anchorRadialPosition(
  kind: FoundationRadialKind,
  existing: ExistingFoundationCounts,
  width = 180,
  height = 80,
): { x: number; y: number } {
  const centre = anchorRadialSlot(kind, existing);
  return { x: centre.x - width / 2, y: centre.y - height / 2 };
}

/** True when the kind is one of the three radial Foundation kinds. */
export function isFoundationRadialKind(kind: string): kind is FoundationRadialKind {
  return (FOUNDATION_RADIAL_KINDS as readonly string[]).includes(kind);
}

/** Count how many of each radial kind already live on the canvas.
 *  Caller (``useNodeCreation``) feeds the current ``doc.nodes``. */
export function countFoundationKinds(
  nodes: ReadonlyArray<{ kind: string }>,
): ExistingFoundationCounts {
  const counts: ExistingFoundationCounts = { mission: 0, core_value: 0, identity: 0 };
  for (const n of nodes) {
    if (isFoundationRadialKind(n.kind)) counts[n.kind] += 1;
  }
  return counts;
}
