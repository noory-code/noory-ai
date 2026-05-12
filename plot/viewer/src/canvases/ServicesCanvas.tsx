/**
 * Services-canvas wrapper. v0.15 Phase 3.3. Pure pass-through (see
 * ``FoundationCanvas`` doc — Phase 3.4 absorbs canvas-kind-specific
 * behaviour, Phase 3.5 wires NODE_RENDERERS).
 */
import { SketchCanvas, type SketchCanvasProps } from "./SketchCanvas";

export function ServicesCanvas(props: SketchCanvasProps) {
  return <SketchCanvas {...props} />;
}
