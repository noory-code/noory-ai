/**
 * Actors-canvas wrapper. v0.15 Phase 3.2. Pass-through (see
 * ``FoundationCanvas`` doc — same pattern, same upgrade path).
 */
import { SketchCanvas, type SketchCanvasProps } from "./SketchCanvas";

export function ActorsCanvas(props: SketchCanvasProps) {
  return <SketchCanvas {...props} />;
}
