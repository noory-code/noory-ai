/**
 * Derive the four cross-canvas "available master" lists from the
 * project's canvas cache:
 *
 *   - ``availableActors``    ← Actors canvas, kind="actor"
 *   - ``availableMissions``  ← Foundation canvas, kind="mission"
 *   - ``availableValues``    ← Foundation canvas, kind="core_value"
 *   - ``availableIdentities``← Foundation canvas, kind="identity"
 *
 * Wired through to every canvas wrapper so picker / orphan-detection
 * code doesn't have to read across the canvas boundary itself.
 *
 * Extracted from ``App.tsx`` (v0.16.5).
 */
import { useMemo } from "react";
import type { CanvasDoc, CanvasKey, SketchNode } from "../types";

export interface AvailableNodes {
  availableActors: SketchNode[];
  availableMissions: SketchNode[];
  availableValues: SketchNode[];
  availableIdentities: SketchNode[];
}

export function useAvailableNodes(canvasCache: Map<CanvasKey, CanvasDoc>): AvailableNodes {
  const actorsCanvas = canvasCache.get("actors");
  const foundationCanvas = canvasCache.get("foundation");

  const availableActors = useMemo<SketchNode[]>(() => {
    if (!actorsCanvas) return [];
    return actorsCanvas.nodes.filter((n) => n.kind === "actor");
  }, [actorsCanvas]);

  const availableMissions = useMemo<SketchNode[]>(() => {
    if (!foundationCanvas) return [];
    return foundationCanvas.nodes.filter((n) => n.kind === "mission");
  }, [foundationCanvas]);

  const availableValues = useMemo<SketchNode[]>(() => {
    if (!foundationCanvas) return [];
    return foundationCanvas.nodes.filter((n) => n.kind === "core_value");
  }, [foundationCanvas]);

  const availableIdentities = useMemo<SketchNode[]>(() => {
    if (!foundationCanvas) return [];
    return foundationCanvas.nodes.filter((n) => n.kind === "identity");
  }, [foundationCanvas]);

  return { availableActors, availableMissions, availableValues, availableIdentities };
}
