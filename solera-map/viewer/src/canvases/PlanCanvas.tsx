import { useMemo } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  type Edge,
  type Node,
  type NodeChange,
  applyNodeChanges,
} from "reactflow";
import type { Concept, Graph, Layout, WorkspaceLens } from "../types";

interface PlanCanvasProps {
  graph: Graph;
  lens: WorkspaceLens;
  layout: Layout;
  onLayoutChange: (next: Layout) => void;
}

/**
 * Concept nodes laid out from persisted positions when available, falling back
 * to a ring around the Identity node. Drags write through to `onLayoutChange`
 * which persists to `_views/map-layout.json` server-side.
 */
export function PlanCanvas({ graph, lens, layout, onLayoutChange }: PlanCanvasProps) {
  const { nodes, edges } = useMemo(
    () => buildFlowElements(graph, lens, layout),
    [graph, lens, layout],
  );

  const handleNodesChange = (changes: NodeChange[]) => {
    // ReactFlow drag events include interim positions (type="position", dragging=true)
    // and one final event (dragging=false). Persist only on the final one.
    const positionCommits = changes.filter(
      (c): c is Extract<NodeChange, { type: "position" }> =>
        c.type === "position" && c.dragging === false && c.position !== undefined,
    );
    if (positionCommits.length === 0) return;

    const updated = applyNodeChanges(changes, nodes);
    const nextNodes: Record<string, { x: number; y: number }> = { ...layout.nodes };
    for (const node of updated) {
      nextNodes[node.id] = { x: node.position.x, y: node.position.y };
    }
    onLayoutChange({ ...layout, nodes: nextNodes });
  };

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView={Object.keys(layout.nodes).length === 0}
        fitViewOptions={{ padding: 0.2 }}
        nodesDraggable
        nodesConnectable={false}
        elementsSelectable
        onNodesChange={handleNodesChange}
      >
        <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="#e2e8f0" />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}

function buildFlowElements(
  graph: Graph,
  lens: WorkspaceLens,
  layout: Layout,
): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = [];
  const edges: Edge[] = [];

  const positionOf = (id: string, fallback: { x: number; y: number }) => {
    const stored = layout.nodes[id];
    return stored ? { x: stored.x, y: stored.y } : fallback;
  };

  if (graph.identity) {
    nodes.push({
      id: "identity",
      type: "default",
      position: positionOf("identity", { x: 0, y: 0 }),
      data: { label: "Identity" },
      style: {
        background: "#0f172a",
        color: "white",
        border: "1px solid #0f172a",
        borderRadius: 12,
        padding: 8,
        fontWeight: 600,
      },
    });
  }

  const radius = Math.max(260, graph.concepts.length * 40);
  graph.concepts.forEach((c, i) => {
    const angle = (i / Math.max(graph.concepts.length, 1)) * Math.PI * 2;
    const fallback = { x: Math.cos(angle) * radius, y: Math.sin(angle) * radius };
    const id = `concept:${c.id}`;
    nodes.push({
      id,
      position: positionOf(id, fallback),
      data: { label: renderConceptLabel(c, lens) },
      style: {
        background: conceptBackground(c, lens),
        border: `1px solid ${conceptBorder(c)}`,
        borderRadius: 12,
        padding: "10px 14px",
        minWidth: 160,
        maxWidth: 220,
      },
    });
    if (graph.identity) {
      edges.push({
        id: `identity-${c.id}`,
        source: "identity",
        target: id,
        style: { stroke: "#cbd5e1", strokeDasharray: "3 3" },
      });
    }
  });

  graph.concept_edges.forEach((e) => {
    edges.push({
      id: e.id,
      source: `concept:${e.from}`,
      target: `concept:${e.to}`,
      label: e.label || undefined,
      labelStyle: { fontSize: 11, fill: "#475569" },
      style: { stroke: "#94a3b8" },
    });
  });

  return { nodes, edges };
}

function renderConceptLabel(c: Concept, lens: WorkspaceLens) {
  const sub = lens === "live" ? c.current_shape : c.current_design;
  return (
    <div className="text-left">
      <div className="text-[13px] font-semibold text-ink">{c.name}</div>
      {c.intent && (
        <div className="mt-0.5 text-[11px] italic text-slate-500 line-clamp-2">{c.intent}</div>
      )}
      {sub && (
        <div className="mt-1 text-[11px] text-slate-700 line-clamp-3">{truncate(sub, 120)}</div>
      )}
    </div>
  );
}

function truncate(s: string, max: number): string {
  return s.length <= max ? s : `${s.slice(0, max).trim()}…`;
}

function conceptBackground(c: Concept, lens: WorkspaceLens): string {
  if (c.status === "archived") return "#f1f5f9";
  if (c.status === "deprecated") return "#fef2f2";
  if (lens === "live" && c.current_shape.includes("no Stories")) {
    return "#fffbeb"; // sketched but not yet painted
  }
  return "#ffffff";
}

function conceptBorder(c: Concept): string {
  if (c.status === "archived") return "#cbd5e1";
  if (c.status === "deprecated") return "#fecaca";
  return "#c7d2fe";
}
