import type { CanvasKey, CanvasKind } from "../types";

/**
 * Derive a cache / history key for a canvas. Singleton canvases use their
 * kind verbatim; ``feature`` serialises the service id it drills
 * into so each detail canvas has its own slot.
 */
export function canvasKey(kind: CanvasKind, serviceId?: string | null): CanvasKey {
  if (kind === "feature") {
    if (!serviceId) throw new Error("feature requires serviceId");
    return `feature:${serviceId}`;
  }
  return kind;
}
