/**
 * Services-canvas wrapper. v0.15 Phase 3.4 — fold on, anchor on.
 * Drill rewire (D-2026-06-17-D): the **feature** is the sole drill target —
 * selecting a service shows its inspector (no drill); clicking a feature drills
 * into its detail (what is wire-named ``service_detail`` until the canvas-string
 * rename). Supersedes the service-as-drill-target predicate.
 */
import { SketchCanvas, type SketchCanvasProps } from "./SketchCanvas";
import type { SketchNode } from "../types";

export function shouldDrillFeature(n: SketchNode): boolean {
  return n.kind === "feature";
}

export function ServicesCanvas(props: SketchCanvasProps) {
  return (
    <SketchCanvas
      {...props}
      hideRootServiceNode={false}
      shouldDrill={shouldDrillFeature}
      selectOpensDrill={true}
      showFoldButton={true}
      injectAnchor={true}
      anchorArrowMode="diverge"
      layoutAlgo="tree"
    />
  );
}
