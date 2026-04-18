import { useMemo } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MarkerType,
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

const ROOT_SPACING_X = 520;
const CHILD_SPACING_X = 260;
const LEVEL_SPACING_Y = 180;

/**
 * Tree layout by `concept.parent` with persisted overrides.
 *
 * - Concepts with `parent === null` are top-level surfaces, placed left→right.
 * - Children fan out below their parent, left→right, with depth stepping y.
 * - Parent→child edges are solid; cross-tree `concept_graph` edges are dashed.
 * - Identity no longer appears on the canvas — its mission is a page banner.
 */
export function PlanCanvas({ graph, lens, layout, onLayoutChange }: PlanCanvasProps) {
  const { nodes, edges } = useMemo(
    () => buildFlowElements(graph, lens, layout),
    [graph, lens, layout],
  );

  const handleNodesChange = (changes: NodeChange[]) => {
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
    <div className="flex h-full w-full flex-col">
      {graph.identity?.mission && <MissionBanner mission={graph.identity.mission} />}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView={Object.keys(layout.nodes).length === 0}
          fitViewOptions={{ padding: 0.15 }}
          nodesDraggable
          nodesConnectable={false}
          elementsSelectable
          onNodesChange={handleNodesChange}
        >
          <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="#e2e8f0" />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
    </div>
  );
}

function MissionBanner({ mission }: { mission: string }) {
  const first = mission.split("\n").find((l) => l.trim().length > 0) ?? "";
  const cleaned = first.replace(/^#+\s*/, "").replace(/^>\s*/, "");
  return (
    <div className="border-b border-slate-200 bg-white/70 px-4 py-1 text-[11px] text-slate-500">
      <span className="font-semibold uppercase tracking-wider text-slate-400">mission</span>
      <span className="ml-2">{truncate(cleaned, 180)}</span>
    </div>
  );
}

function buildFlowElements(
  graph: Graph,
  lens: WorkspaceLens,
  layout: Layout,
): { nodes: Node[]; edges: Edge[] } {
  const byId = new Map(graph.concepts.map((c) => [c.id, c] as const));
  const childrenOf = groupChildren(graph.concepts);
  const roots = graph.concepts.filter((c) => !c.parent || !byId.has(c.parent));

  // Compute auto-layout positions for a fresh canvas. Every node gets a
  // deterministic (x, y); the persisted layout overrides per-node.
  const autoPositions = new Map<string, { x: number; y: number }>();
  let cursorX = 0;
  for (const root of roots) {
    const width = subtreeWidth(root.id, childrenOf);
    layoutSubtree(root.id, childrenOf, autoPositions, cursorX + width / 2, 0);
    cursorX += width + ROOT_SPACING_X;
  }

  const nodes: Node[] = [];
  for (const concept of graph.concepts) {
    const id = `concept:${concept.id}`;
    const fallback = autoPositions.get(concept.id) ?? { x: 0, y: 0 };
    const stored = layout.nodes[id];
    const isRoot = !concept.parent || !byId.has(concept.parent);
    nodes.push({
      id,
      position: stored ? { x: stored.x, y: stored.y } : fallback,
      data: { label: renderConceptLabel(concept, lens, isRoot) },
      style: {
        background: conceptBackground(concept, lens),
        border: `${isRoot ? 2 : 1}px solid ${conceptBorder(concept, isRoot)}`,
        borderRadius: 12,
        padding: isRoot ? "14px 18px" : "10px 14px",
        minWidth: isRoot ? 220 : 180,
        maxWidth: 260,
      },
    });
  }

  const edges: Edge[] = [];
  // Structural containment edges (parent → child).
  for (const concept of graph.concepts) {
    if (!concept.parent || !byId.has(concept.parent)) continue;
    edges.push({
      id: `parent-${concept.id}`,
      source: `concept:${concept.parent}`,
      target: `concept:${concept.id}`,
      style: { stroke: "#cbd5e1", strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: "#cbd5e1" },
    });
  }
  // User-authored free-label edges.
  for (const e of graph.concept_edges) {
    edges.push({
      id: e.id,
      source: `concept:${e.from}`,
      target: `concept:${e.to}`,
      label: e.label || undefined,
      labelStyle: { fontSize: 11, fill: "#475569" },
      style: { stroke: "#94a3b8", strokeDasharray: "4 3" },
    });
  }

  return { nodes, edges };
}

function groupChildren(concepts: Concept[]): Map<string, Concept[]> {
  const out = new Map<string, Concept[]>();
  for (const c of concepts) {
    if (!c.parent) continue;
    if (!out.has(c.parent)) out.set(c.parent, []);
    out.get(c.parent)!.push(c);
  }
  return out;
}

function subtreeWidth(id: string, childrenOf: Map<string, Concept[]>): number {
  const kids = childrenOf.get(id) ?? [];
  if (kids.length === 0) return CHILD_SPACING_X;
  return kids.reduce((acc, k) => acc + subtreeWidth(k.id, childrenOf), 0);
}

function layoutSubtree(
  id: string,
  childrenOf: Map<string, Concept[]>,
  out: Map<string, { x: number; y: number }>,
  centerX: number,
  depth: number,
): void {
  out.set(id, { x: centerX, y: depth * LEVEL_SPACING_Y });
  const kids = childrenOf.get(id) ?? [];
  if (kids.length === 0) return;
  const totalWidth = kids.reduce((acc, k) => acc + subtreeWidth(k.id, childrenOf), 0);
  let cursor = centerX - totalWidth / 2;
  for (const kid of kids) {
    const w = subtreeWidth(kid.id, childrenOf);
    layoutSubtree(kid.id, childrenOf, out, cursor + w / 2, depth + 1);
    cursor += w;
  }
}

function renderConceptLabel(c: Concept, lens: WorkspaceLens, isRoot: boolean) {
  const sub = lens === "live" ? c.current_shape : c.current_design;
  return (
    <div className="text-left">
      <div className={`font-semibold text-ink ${isRoot ? "text-[15px]" : "text-[12px]"}`}>
        {c.name}
      </div>
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
  if (lens === "live" && c.current_shape.includes("no Stories")) return "#fffbeb";
  return "#ffffff";
}

function conceptBorder(c: Concept, isRoot: boolean): string {
  if (c.status === "archived") return "#cbd5e1";
  if (c.status === "deprecated") return "#fecaca";
  return isRoot ? "#6366f1" : "#c7d2fe";
}
