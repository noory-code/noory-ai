/**
 * Actors-canvas wrapper. v0.15 Phase 3.4 — fold on, no drill, anchor on.
 */
import { SketchCanvas, type SketchCanvasProps } from "./SketchCanvas";

export function ActorsCanvas(props: SketchCanvasProps) {
  return (
    <SketchCanvas
      {...props}
      hideRootServiceNode={false}
      shouldDrill={undefined}
      showFoldButton={true}
    />
  );
}
