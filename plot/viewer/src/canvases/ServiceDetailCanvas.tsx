/**
 * ServiceDetail-canvas wrapper. v0.15 Phase 3.4 — drops the
 * redundant root-service node, drills on actor_ref (jump to master),
 * suppresses the synthetic anchor (modal already names the service).
 */
import { SketchCanvas, type SketchCanvasProps } from "./SketchCanvas";
import type { SketchNode } from "../types";

function shouldDrillActorRef(n: SketchNode): boolean {
  return n.kind === "actor_ref";
}

export function ServiceDetailCanvas(props: SketchCanvasProps) {
  return (
    <SketchCanvas
      {...props}
      hideRootServiceNode={true}
      shouldDrill={shouldDrillActorRef}
      showFoldButton={true}
      injectAnchor={false}
      layoutAlgo="tree"
    />
  );
}
