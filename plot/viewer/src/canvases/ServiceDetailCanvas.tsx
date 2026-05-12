/**
 * ServiceDetail-canvas wrapper. v0.15 Phase 3.3. Pure pass-through.
 *
 * Mounted inside ``ServiceDetailModal`` when the user drills into a
 * service from the Services overview. Phase 3.4 absorbs the
 * service-detail-specific behaviour (anchor injection, edge filter
 * for service-ref edges); Phase 3.5 wires NODE_RENDERERS so this
 * wrapper supplies a service-detail-only ``nodeTypes`` map (omits
 * Foundation kinds, includes composition + actor_ref + 3 foundation
 * refs).
 */
import { SketchCanvas, type SketchCanvasProps } from "./SketchCanvas";

export function ServiceDetailCanvas(props: SketchCanvasProps) {
  return <SketchCanvas {...props} />;
}
