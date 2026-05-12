/**
 * Services-canvas wrapper. v0.15 Phase 3.4 — fold on, drill on
 * non-root service nodes (per v0.12.1), anchor on.
 */
import { SketchCanvas, type SketchCanvasProps } from "./SketchCanvas";
import type { SketchNode } from "../types";

function shouldDrillService(n: SketchNode): boolean {
  return n.kind === "service" && !n.is_root;
}

export function ServicesCanvas(props: SketchCanvasProps) {
  return (
    <SketchCanvas
      {...props}
      hideRootServiceNode={false}
      shouldDrill={shouldDrillService}
      showFoldButton={true}
    />
  );
}
