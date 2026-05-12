/**
 * Foundation-canvas wrapper. v0.15 Phase 3.2.
 *
 * Pure pass-through to ``SketchCanvas`` for now — Phase 3.4 absorbs
 * the canvas-kind-specific behaviour (showFold=false, anchor injection,
 * filter rules) that currently lives in ``useNodesMemo.ts`` /
 * ``useEdgesMemo.ts`` and routes them through wrapper-supplied props
 * instead. Phase 3.5 wires ``NODE_RENDERERS`` so this wrapper supplies
 * a Foundation-only ``nodeTypes`` map.
 *
 * The wrapper exists now (vs. straight SketchCanvas calls) so the
 * call-site routing in App.tsx is named — clicking the Foundation tab
 * mounts ``<FoundationCanvas>``, not ``<SketchCanvas doc.kind=...>``.
 */
import { SketchCanvas, type SketchCanvasProps } from "./SketchCanvas";

export function FoundationCanvas(props: SketchCanvasProps) {
  return <SketchCanvas {...props} />;
}
