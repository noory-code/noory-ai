import type { CanvasKey, CanvasKind } from "../types";

/**
 * Derive a cache / history key for a canvas. Singleton canvases use their
 * kind verbatim; ``service_detail`` serialises the service id it drills
 * into so each detail canvas has its own slot.
 */
export function canvasKey(kind: CanvasKind, serviceId?: string | null): CanvasKey {
  if (kind === "service_detail") {
    if (!serviceId) throw new Error("service_detail requires serviceId");
    return `service_detail:${serviceId}`;
  }
  return kind;
}
