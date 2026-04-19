export interface SketchNode {
  id: string;
  label: string;
  body: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
}

export interface SketchEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle: string | null;
  targetHandle: string | null;
  label: string;
  style: "solid" | "dashed";
}

export interface SketchDoc {
  id: string;
  name: string;
  created: string;
  updated: string;
  version: number;
  nodes: SketchNode[];
  edges: SketchEdge[];
}

export interface SketchSummary {
  id: string;
  name: string;
  updated: string;
  node_count: number;
  edge_count: number;
}
