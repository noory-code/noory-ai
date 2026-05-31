/**
 * FloatingEdge — v0.30.3 (D-2026-05-31-F).
 *
 * Attaches the edge to the point on each node's border that faces the
 * other node, instead of a fixed per-side handle. This makes the
 * connection read identically from any side — the asymmetric 4-handle
 * model (emit only right/bottom, receive only top/left) used to force
 * awkward loops when the target sat on a node's left/top.
 *
 * Reads live node geometry from the React Flow store (v11
 * ``nodeInternals``) and recomputes the path on every position change.
 * The ``markerEnd`` (arrowhead), ``style`` (injection violet /
 * value-flow recolour / dashed) and ``animated`` flag are passed in by
 * ``edgeTransform`` exactly as for default edges, so all styling is
 * preserved. Self-loops keep their own ``SelfLoopEdge``.
 *
 * Wired in ``edges/registry.ts`` → ``SketchCanvas`` ``edgeTypes``.
 */
import {
  BaseEdge,
  getBezierPath,
  Position,
  useStore,
  type EdgeProps,
  type ReactFlowState,
} from "reactflow";
import {
  borderSide,
  floatingEndpoints,
  type BorderSide,
  type NodeRect,
} from "../../flow/floatingEdgeGeometry";

const TO_POSITION: Record<BorderSide, Position> = {
  top: Position.Top,
  right: Position.Right,
  bottom: Position.Bottom,
  left: Position.Left,
};

function rectOf(node: {
  positionAbsolute?: { x: number; y: number };
  position: { x: number; y: number };
  width?: number | null;
  height?: number | null;
}): NodeRect {
  const pos = node.positionAbsolute ?? node.position;
  return {
    x: pos.x,
    y: pos.y,
    width: node.width ?? 0,
    height: node.height ?? 0,
  };
}

export function FloatingEdge({ id, source, target, markerEnd, style }: EdgeProps) {
  const sourceNode = useStore((s: ReactFlowState) => s.nodeInternals.get(source));
  const targetNode = useStore((s: ReactFlowState) => s.nodeInternals.get(target));

  if (!sourceNode || !targetNode) return null;

  const sRect = rectOf(sourceNode);
  const tRect = rectOf(targetNode);
  const { sx, sy, tx, ty } = floatingEndpoints(sRect, tRect);
  // v0.34.5 — curved (bezier) instead of straight; control points leave
  // each node perpendicular to the border side the endpoint floats to.
  const [path] = getBezierPath({
    sourceX: sx,
    sourceY: sy,
    sourcePosition: TO_POSITION[borderSide(sx, sy, sRect)],
    targetX: tx,
    targetY: ty,
    targetPosition: TO_POSITION[borderSide(tx, ty, tRect)],
  });

  return <BaseEdge id={id} path={path} markerEnd={markerEnd} style={style} />;
}
