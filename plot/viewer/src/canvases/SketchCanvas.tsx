import { useCallback, useMemo, useRef } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  ReactFlowProvider,
  applyEdgeChanges,
  applyNodeChanges,
  type Connection,
  type Edge,
  type EdgeChange,
  type Node,
  type NodeChange,
  type ReactFlowInstance,
} from "reactflow";
import type { SketchDoc, SketchEdge, SketchNode as DocNode } from "../types";
import { SketchNode, type SketchNodeData } from "./SketchNode";
import { SketchToolbar, type SaveState } from "./SketchToolbar";

const NODE_TYPES = { sketch: SketchNode } as const;

const DEFAULT_WIDTH = 180;
const DEFAULT_HEIGHT = 80;
const DEFAULT_COLOR = "#ffffff";

export interface SketchCanvasProps {
  doc: SketchDoc;
  onDocChange: (next: SketchDoc) => void;
  saveState: SaveState;
  onDownload: () => void;
  onUpload: () => void;
}

export function SketchCanvas(props: SketchCanvasProps) {
  return (
    <ReactFlowProvider>
      <SketchCanvasInner {...props} />
    </ReactFlowProvider>
  );
}

function SketchCanvasInner({
  doc,
  onDocChange,
  saveState,
  onDownload,
  onUpload,
}: SketchCanvasProps) {
  const docRef = useRef<SketchDoc>(doc);
  docRef.current = doc;
  const flowRef = useRef<ReactFlowInstance | null>(null);

  const updateNodeLabel = useCallback(
    (nodeId: string, label: string) => {
      const current = docRef.current;
      onDocChange({
        ...current,
        nodes: current.nodes.map((n) => (n.id === nodeId ? { ...n, label } : n)),
      });
    },
    [onDocChange],
  );

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
          onLabelChange: (next: string) => updateNodeLabel(n.id, next),
        },
      })),
    [doc.nodes, updateNodeLabel],
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

  // Apply React Flow's cheap changes (selection, dimensions, drag-in-progress)
  // to a local derived copy and propagate meaningful mutations (position,
  // add, remove) to the parent. Position updates commit only on drag stop
  // below — intermediate drag frames stay local to React Flow.
  const handleNodesChange = useCallback(
    (changes: NodeChange[]) => {
      const positionCommits = changes.filter(
        (c) => c.type === "position" && c.dragging === false && c.position,
      );
      if (positionCommits.length === 0) return;
      const posById = new Map<string, { x: number; y: number }>();
      for (const c of positionCommits) {
        if (c.type === "position" && c.position) {
          posById.set(c.id, c.position);
        }
      }
      const current = docRef.current;
      onDocChange({
        ...current,
        nodes: current.nodes.map((n) =>
          posById.has(n.id) ? { ...n, ...posById.get(n.id)! } : n,
        ),
      });
    },
    [onDocChange],
  );

  // React Flow's onEdgesChange fires for selection + remove. We only care
  // about remove here (delete-key triggers onEdgesDelete separately, but
  // this path keeps the local Edge array consistent regardless).
  const handleEdgesChange = useCallback((_changes: EdgeChange[]) => {
    // No-op — deletions are handled via onEdgesDelete.
    // Selection is internal to React Flow.
  }, []);

  const handleConnect = useCallback(
    (connection: Connection) => {
      if (!connection.source || !connection.target) return;
      const current = docRef.current;
      const newEdge: SketchEdge = {
        id: `e_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`,
        source: connection.source,
        target: connection.target,
        sourceHandle: connection.sourceHandle ?? null,
        targetHandle: connection.targetHandle ?? null,
        label: "",
        style: "solid",
      };
      onDocChange({ ...current, edges: [...current.edges, newEdge] });
    },
    [onDocChange],
  );

  const handleNodesDelete = useCallback(
    (deleted: Node[]) => {
      const ids = new Set(deleted.map((n) => n.id));
      const current = docRef.current;
      onDocChange({
        ...current,
        nodes: current.nodes.filter((n) => !ids.has(n.id)),
        edges: current.edges.filter(
          (e) => !ids.has(e.source) && !ids.has(e.target),
        ),
      });
    },
    [onDocChange],
  );

  const handleEdgesDelete = useCallback(
    (deleted: Edge[]) => {
      const ids = new Set(deleted.map((e) => e.id));
      const current = docRef.current;
      onDocChange({
        ...current,
        edges: current.edges.filter((e) => !ids.has(e.id)),
      });
    },
    [onDocChange],
  );

  const addNodeAt = useCallback(
    (x: number, y: number) => {
      const id = `n_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
      const newNode: DocNode = {
        id,
        label: "",
        body: "",
        x,
        y,
        width: DEFAULT_WIDTH,
        height: DEFAULT_HEIGHT,
        color: DEFAULT_COLOR,
      };
      const current = docRef.current;
      onDocChange({ ...current, nodes: [...current.nodes, newNode] });
    },
    [onDocChange],
  );

  const handlePaneDoubleClick = useCallback(
    (event: React.MouseEvent) => {
      if (!flowRef.current) return;
      // Only fire on the pane itself, not on child elements.
      const target = event.target as HTMLElement;
      if (!target.classList.contains("react-flow__pane")) return;
      const pos = flowRef.current.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });
      addNodeAt(pos.x - DEFAULT_WIDTH / 2, pos.y - DEFAULT_HEIGHT / 2);
    },
    [addNodeAt],
  );

  const handleToolbarAdd = useCallback(() => {
    // Place new node near the viewport centre.
    if (!flowRef.current) return;
    const vp = flowRef.current.getViewport();
    const { innerWidth, innerHeight } = window;
    const centreScreen = { x: innerWidth / 2, y: innerHeight / 2 };
    const centre = flowRef.current.screenToFlowPosition(centreScreen);
    addNodeAt(centre.x - DEFAULT_WIDTH / 2, centre.y - DEFAULT_HEIGHT / 2 + vp.y * 0);
  }, [addNodeAt]);

  return (
    <div className="relative h-full w-full" onDoubleClick={handlePaneDoubleClick}>
      <SketchToolbar
        saveState={saveState}
        onAddNode={handleToolbarAdd}
        onDownload={onDownload}
        onUpload={onUpload}
      />
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={NODE_TYPES}
        nodesConnectable
        nodesDraggable
        elementsSelectable
        deleteKeyCode={["Delete", "Backspace"]}
        onNodesChange={handleNodesChange}
        onEdgesChange={handleEdgesChange}
        onConnect={handleConnect}
        onNodesDelete={handleNodesDelete}
        onEdgesDelete={handleEdgesDelete}
        onInit={(inst) => {
          flowRef.current = inst;
        }}
        fitView
        fitViewOptions={{ padding: 0.2 }}
      >
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
        <MiniMap zoomable pannable />
        <Controls />
      </ReactFlow>
    </div>
  );
}

// Re-exports for tests that want to exercise the pure helpers without
// mounting the canvas.
export { applyEdgeChanges, applyNodeChanges };
