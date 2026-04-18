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
import type { Concept, Graph, Identity, Layout, WorkspaceLens } from "../types";

export const IDENTITY_NODE_ID = "identity";

export interface SelectedNode {
  kind: "identity" | "concept";
  id: string;
}

interface PlanCanvasProps {
  graph: Graph;
  lens: WorkspaceLens;
  layout: Layout;
  onLayoutChange: (next: Layout) => void;
  onSelect: (selection: SelectedNode | null) => void;
  selection: SelectedNode | null;
}

const ROOT_SPACING_X = 320;
const CHILD_SPACING_X = 240;
const LEVEL_SPACING_Y = 180;

/**
 * Tree rooted at the Identity node. Top-level Concepts (parent === null) attach
 * to Identity. Deeper Concepts attach to their parent Concept. Clicking any
 * node lifts the selection to App so the SidePanel can render the details.
 */
export function PlanCanvas({
  graph,
  lens,
  layout,
  onLayoutChange,
  onSelect,
  selection,
}: PlanCanvasProps) {
  const { nodes, edges } = useMemo(
    () => buildFlowElements(graph, lens, layout, selection),
    [graph, lens, layout, selection],
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
        onNodeClick={(_evt, node) => {
          if (node.id === IDENTITY_NODE_ID) {
            onSelect({ kind: "identity", id: IDENTITY_NODE_ID });
          } else if (node.id.startsWith("concept:")) {
            onSelect({ kind: "concept", id: node.id.slice("concept:".length) });
          }
        }}
        onPaneClick={() => onSelect(null)}
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
  selection: SelectedNode | null,
): { nodes: Node[]; edges: Edge[] } {
  const byId = new Map(graph.concepts.map((c) => [c.id, c] as const));
  const childrenByParent = new Map<string | null, Concept[]>();
  for (const c of graph.concepts) {
    const key = c.parent && byId.has(c.parent) ? c.parent : null;
    if (!childrenByParent.has(key)) childrenByParent.set(key, []);
    childrenByParent.get(key)!.push(c);
  }

  const autoPositions = new Map<string, { x: number; y: number }>();

  // Identity is the synthetic root. All top-level Concepts (parent=null) hang
  // under it.
  const hasIdentity = graph.identity !== null;
  const topLevels = childrenByParent.get(null) ?? [];

  if (hasIdentity) {
    const totalWidth = subtreeWidth(topLevels, childrenByParent);
    autoPositions.set(IDENTITY_NODE_ID, { x: totalWidth / 2, y: 0 });
    let cursor = 0;
    for (const concept of topLevels) {
      const w = subtreeWidthFor(concept, childrenByParent);
      layoutSubtree(concept, childrenByParent, autoPositions, cursor + w / 2, 1);
      cursor += w;
    }
  } else {
    // Fallback: Concepts arranged as forest from y=0.
    let cursor = 0;
    for (const concept of topLevels) {
      const w = subtreeWidthFor(concept, childrenByParent);
      layoutSubtree(concept, childrenByParent, autoPositions, cursor + w / 2, 0);
      cursor += w + ROOT_SPACING_X;
    }
  }

  const nodes: Node[] = [];
  const positionOf = (id: string, fallback: { x: number; y: number }) => {
    const stored = layout.nodes[id];
    return stored ? { x: stored.x, y: stored.y } : fallback;
  };

  if (hasIdentity && graph.identity) {
    const isSelected = selection?.kind === "identity";
    nodes.push({
      id: IDENTITY_NODE_ID,
      position: positionOf(IDENTITY_NODE_ID, autoPositions.get(IDENTITY_NODE_ID) ?? { x: 0, y: 0 }),
      data: { label: <IdentityLabel identity={graph.identity} /> },
      style: {
        background: "#0f172a",
        color: "white",
        border: `${isSelected ? 3 : 2}px solid ${isSelected ? "#fbbf24" : "#0f172a"}`,
        borderRadius: 16,
        padding: "14px 22px",
        minWidth: 200,
        maxWidth: 280,
        cursor: "pointer",
      },
    });
  }

  for (const concept of graph.concepts) {
    const id = `concept:${concept.id}`;
    const isRoot = !concept.parent || !byId.has(concept.parent);
    const isSelected = selection?.kind === "concept" && selection.id === concept.id;
    const fallback = autoPositions.get(concept.id) ?? { x: 0, y: LEVEL_SPACING_Y };
    nodes.push({
      id,
      position: positionOf(id, fallback),
      data: { label: renderConceptLabel(concept, lens, isRoot) },
      style: {
        background: conceptBackground(concept, lens),
        border: `${isSelected ? 3 : isRoot ? 2 : 1}px solid ${
          isSelected ? "#6366f1" : conceptBorder(concept, isRoot)
        }`,
        borderRadius: 12,
        padding: isRoot ? "12px 16px" : "8px 12px",
        minWidth: isRoot ? 200 : 170,
        maxWidth: 240,
        cursor: "pointer",
      },
    });
  }

  const edges: Edge[] = [];
  // Identity → top-level Concept (containment)
  if (hasIdentity) {
    for (const top of topLevels) {
      edges.push({
        id: `identity-${top.id}`,
        source: IDENTITY_NODE_ID,
        target: `concept:${top.id}`,
        style: { stroke: "#cbd5e1", strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#cbd5e1" },
      });
    }
  }
  // Parent Concept → child Concept (containment)
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
  // Free-label cross edges
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

function subtreeWidthFor(concept: Concept, childrenBy: Map<string | null, Concept[]>): number {
  const kids = childrenBy.get(concept.id) ?? [];
  if (kids.length === 0) return CHILD_SPACING_X;
  return kids.reduce((acc, k) => acc + subtreeWidthFor(k, childrenBy), 0);
}

function subtreeWidth(concepts: Concept[], childrenBy: Map<string | null, Concept[]>): number {
  if (concepts.length === 0) return CHILD_SPACING_X;
  return concepts.reduce((acc, c) => acc + subtreeWidthFor(c, childrenBy), 0);
}

function layoutSubtree(
  concept: Concept,
  childrenBy: Map<string | null, Concept[]>,
  out: Map<string, { x: number; y: number }>,
  centerX: number,
  depth: number,
): void {
  out.set(concept.id, { x: centerX, y: depth * LEVEL_SPACING_Y });
  const kids = childrenBy.get(concept.id) ?? [];
  if (kids.length === 0) return;
  const totalWidth = kids.reduce((acc, k) => acc + subtreeWidthFor(k, childrenBy), 0);
  let cursor = centerX - totalWidth / 2;
  for (const kid of kids) {
    const w = subtreeWidthFor(kid, childrenBy);
    layoutSubtree(kid, childrenBy, out, cursor + w / 2, depth + 1);
    cursor += w;
  }
}

function IdentityLabel({ identity }: { identity: Identity }) {
  const firstSentence = extractFirstSentence(identity.mission ?? identity.vision ?? "");
  return (
    <div className="text-left">
      <div className="text-[10px] font-semibold uppercase tracking-widest text-amber-300">
        identity
      </div>
      <div className="mt-0.5 text-[14px] font-bold">BANAS</div>
      {firstSentence && (
        <div className="mt-1 text-[11px] leading-tight text-slate-300 line-clamp-3">
          {firstSentence}
        </div>
      )}
    </div>
  );
}

function extractFirstSentence(text: string): string {
  // Skip markdown headers and pull the first meaningful line.
  for (const raw of text.split("\n")) {
    const trimmed = raw.trim();
    if (!trimmed) continue;
    if (trimmed.startsWith("#")) continue;
    if (trimmed.startsWith("<!--")) continue;
    return trimmed.replace(/^>\s*/, "").replace(/\*\*/g, "").replace(/<!--.*?-->/g, "").trim();
  }
  return "";
}

function renderConceptLabel(c: Concept, lens: WorkspaceLens, isRoot: boolean) {
  const sub = lens === "live" ? c.current_shape : c.current_design;
  return (
    <div className="text-left">
      <div className={`font-semibold text-ink ${isRoot ? "text-[14px]" : "text-[12px]"}`}>
        {c.name}
      </div>
      {c.intent && (
        <div className="mt-0.5 text-[11px] italic text-slate-500 line-clamp-2">{c.intent}</div>
      )}
      {sub && !sub.includes("no Stories") && (
        <div className="mt-1 text-[11px] text-slate-700 line-clamp-2">{truncate(sub, 90)}</div>
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
