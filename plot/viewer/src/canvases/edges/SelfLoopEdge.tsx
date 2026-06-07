/**
 * SelfLoopEdge — custom React Flow edge for self-loops (source === target).
 *
 * Per PRODUCT_SPEC §"서비스 간 연결 = 유저저니" (D-2026-05-12-M):
 *   "셀프 피드백 루프 표현 가능 (서비스 A → 서비스 A)."
 *
 * React Flow's default edge draws a zero-length line for self-loops
 * (or a chord through the node body when source / target handles
 * differ on the same node). Neither is readable. This component
 * draws a cubic Bezier arc that bulges away from the node so the
 * loop is visually unambiguous and click-able for select / delete.
 *
 * Wired in ``edges/registry.ts`` → ``SketchCanvas.tsx`` ``edgeTypes``.
 * ``edgeTransform.ts`` assigns ``type: "selfLoop"`` when the source
 * doc edge has ``source === target`` and neither side resolves to a
 * different collapsed ancestor.
 */
import { BaseEdge, EdgeLabelRenderer, type EdgeProps } from "reactflow";

/** How far the arc bulges away from the source / target line. */
const ARC_BULGE = 100;

function selfLoopPath(
  sourceX: number,
  sourceY: number,
  targetX: number,
  targetY: number,
): { path: string; labelX: number; labelY: number } {
  // Always arc *above* the source / target line so the loop is visible
  // even when source === target (same handle). The two Bezier control
  // points sit ``ARC_BULGE`` above each endpoint with a horizontal
  // spread that guarantees a non-degenerate curve.
  const c1x = sourceX + ARC_BULGE;
  const c1y = sourceY - ARC_BULGE;
  const c2x = targetX - ARC_BULGE;
  const c2y = targetY - ARC_BULGE;
  const path = `M ${sourceX},${sourceY} C ${c1x},${c1y} ${c2x},${c2y} ${targetX},${targetY}`;
  // Label sits at the curve's apex (t=0.5 of the Bezier).
  const labelX = (sourceX + c1x + c2x + targetX) / 4;
  const labelY = (sourceY + c1y + c2y + targetY) / 4;
  return { path, labelX, labelY };
}

export function SelfLoopEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  markerEnd,
  style,
  label,
  selected,
}: EdgeProps): JSX.Element {
  const { path, labelX, labelY } = selfLoopPath(sourceX, sourceY, targetX, targetY);
  const strokeStyle: React.CSSProperties = {
    ...style,
    strokeWidth:
      typeof style?.strokeWidth === "number" ? style.strokeWidth : selected ? 2 : 1.5,
  };
  return (
    <>
      <BaseEdge
        id={id}
        path={path}
        markerEnd={markerEnd}
        style={strokeStyle}
      />
      {label && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: "absolute",
              transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
              pointerEvents: "all",
              fontSize: 10,
            }}
            className="rounded bg-surface/90 px-1 text-fg shadow-sm"
          >
            {String(label)}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}

// Exported for unit tests — the math is the worth-protecting part.
export { selfLoopPath };
