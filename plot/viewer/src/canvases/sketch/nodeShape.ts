// Node shape policy — shape encodes producer-vs-reference.
//
// v0.29.3 (D-2026-05-31-B): 원본/master kinds render as a rounded
// rectangle (네모 — soft corners, user 2026-05-31 "좀 둥그스럼하게");
// symbol-reference (`*_ref`) kinds render as a circle (동그라미). The
// shape distinguishes the *original* from the symbol pointer that
// stands in for it on a consumer canvas. Supersedes D-2026-05-28-D
// (which made every Symbol kind a circle).
//
// Pure module (no React) so it is unit-testable and the BaseNode
// renderer stays a thin consumer — mirrors `polarityTint`.
import type { Shape } from "../../types";

/** Original / producer-plane kinds — the real node on its home
 *  canvas. Rendered as a rounded rectangle (soft corners). */
export const MASTER_KINDS = new Set<string>([
  "mission",
  "core_value",
  "identity",
  "actor",
]);

/** Symbol-reference kinds — a pointer that stands in for a master on
 *  a consumer canvas. Rendered as a circle. */
export const REFERENCE_KINDS = new Set<string>([
  "actor_ref",
  "mission_ref",
  "value_ref",
  "identity_ref",
]);

/** Resolve the rendered shape for a node from its kind + stored shape.
 *  Master kinds force a rounded rectangle (soft corners), reference
 *  kinds force circle, `decision` forces diamond (the shape is the
 *  semantic, D-2026-05-30-C). `project` (synthetic anchor) and every
 *  other kind honour the stored shape. */
export function effectiveShape(
  kind: string | null | undefined,
  storedShape: Shape,
): Shape {
  if (kind && MASTER_KINDS.has(kind)) return "rounded";
  if (kind && REFERENCE_KINDS.has(kind)) return "circle";
  if (kind === "decision") return "diamond";
  return storedShape;
}
