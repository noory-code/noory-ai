import { useMemo } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  type Edge,
  type Node,
} from "reactflow";
import type { Concept, Graph, WorkspaceLens } from "../types";

interface PlanCanvasProps {
  graph: Graph;
  lens: WorkspaceLens;
}

/**
 * Read-only first pass: Concepts as nodes, Concept↔Concept edges as free-label lines.
 * Identity sits at the origin; Concepts spread out in a circle around it.
 * Layout is static for now — real positions come from map-layout.json in a later phase.
 */
export function PlanCanvas({ graph, lens }: PlanCanvasProps) {
  const { nodes, edges } = useMemo(() => buildFlowElements(graph, lens), [graph, lens]);

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable
      >
        <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="#e2e8f0" />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}

function buildFlowElements(graph: Graph, lens: WorkspaceLens): {
  nodes: Node[];
  edges: Edge[];
} {
  const nodes: Node[] = [];
  const edges: Edge[] = [];

  if (graph.identity) {
    nodes.push({
      id: "identity",
      type: "default",
      position: { x: 0, y: 0 },
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
    nodes.push({
      id: `concept:${c.id}`,
      position: { x: Math.cos(angle) * radius, y: Math.sin(angle) * radius },
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
        target: `concept:${c.id}`,
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
