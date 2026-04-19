import { useMemo } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  type Edge,
  type Node,
} from "reactflow";
import type { SketchDoc } from "../types";
import { SketchNode, type SketchNodeData } from "./SketchNode";

const NODE_TYPES = { sketch: SketchNode } as const;

export interface SketchCanvasProps {
  doc: SketchDoc;
}

/**
 * Read-only React Flow surface. Renders the sketch's nodes and edges with
 * a MiniMap, Controls, and dotted background. Editing and persistence land
 * in commit 3.
 */
export function SketchCanvas({ doc }: SketchCanvasProps) {
  const nodes = useMemo<Node<SketchNodeData>[]>(
    () =>
      doc.nodes.map((n) => ({
        id: n.id,
        type: "sketch",
        position: { x: n.x, y: n.y },
        data: {
          label: n.label,
          body: n.body,
          color: n.color,
          width: n.width,
          height: n.height,
        },
      })),
    [doc.nodes],
  );

  const edges = useMemo<Edge[]>(
    () =>
      doc.edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        sourceHandle: e.sourceHandle ?? undefined,
        targetHandle: e.targetHandle ?? undefined,
        label: e.label || undefined,
        style: e.style === "dashed" ? { strokeDasharray: "6 4" } : undefined,
      })),
    [doc.edges],
  );

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={NODE_TYPES}
      fitView
      fitViewOptions={{ padding: 0.2 }}
      proOptions={{ hideAttribution: false }}
    >
      <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
      <MiniMap zoomable pannable />
      <Controls />
    </ReactFlow>
  );
}
