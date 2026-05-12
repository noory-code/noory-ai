/**
 * Foundation-canvas wrapper. v0.15 Phase 3.4 — supplies the
 * canvas-kind-specific behaviour (no fold, no drill, anchor on)
 * via wrapper-supplied props instead of having SketchCanvas read
 * ``doc.canvas_kind``.
 *
 * Phase 3.5 will wire NODE_RENDERERS so this wrapper supplies a
 * Foundation-only ``nodeTypes`` map.
 */
import { SketchCanvas, type SketchCanvasProps } from "./SketchCanvas";

export function FoundationCanvas(props: SketchCanvasProps) {
  return (
    <SketchCanvas
      {...props}
      hideRootServiceNode={false}
      shouldDrill={undefined}
      showFoldButton={false}
      injectAnchor={true}
      applyAnchorRadialLayout={true}
    />
  );
}
