/**
 * Entities-canvas wrapper (D-2026-06-17-I). A project-level singleton sibling
 * of Foundation / Actors / Services holding the product data objects the
 * services act on (글 / 댓글 / 사용자). Props-only thin shell — behaviour lives
 * in SketchCanvas / its hooks (Gate 2).
 *
 * Mirrors ServicesCanvas's anchor + fold, minus drill: an entity is NOT a
 * drill target (it has no sub-canvas — its data lives in its inspector
 * ``summary`` + its relationship edges). ``enableAutoLayout`` stays OFF
 * (auto-layout is Foundation-only, SPEC §Auto-layout). ``anchorArrowMode``
 * mirrors services (``"diverge"``).
 */
import { SketchCanvas, type SketchCanvasProps } from "./SketchCanvas";

export function EntitiesCanvas(props: SketchCanvasProps) {
  return (
    <SketchCanvas
      {...props}
      hideRootServiceNode={false}
      showFoldButton={true}
      injectAnchor={true}
      anchorArrowMode="diverge"
      layoutAlgo="tree"
    />
  );
}
