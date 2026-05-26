/**
 * ServiceDetail-canvas wrapper.
 *
 * v0.15 Phase 3.4 (initial): hid the root-service node + suppressed
 * the synthetic anchor on the grounds that the modal header already
 * named the service.
 *
 * v0.27.3 (D-2026-05-26-G): the canvas's *subject* is the service —
 * "이 서비스를 상세하게 설계하는 캔버스". The root-service is now
 * **visible** at the centre of the canvas (analogous to Foundation /
 * Actors' anchor); it acts as the BFS root for the tree
 * auto-layout, so user-authored interaction nodes can attach to it
 * and fan out. The modal header still carries the navigation
 * breadcrumb; the canvas's root-service node carries the design
 * subject. Two distinct surfaces, not a duplication.
 *
 * Drill on actor_ref still jumps to the actor master.
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
      hideRootServiceNode={false}
      shouldDrill={shouldDrillActorRef}
      showFoldButton={true}
      injectAnchor={false}
      layoutAlgo="tree"
    />
  );
}
