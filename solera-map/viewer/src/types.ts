// Wire types that mirror `solera_map.graph` (by_alias JSON output).

export type ConceptStatus = "active" | "deprecated" | "archived";
export type MilestoneStatus = "proposed" | "agreed" | "in-progress" | "released";
export type WorkStatus = "pending" | "in_progress" | "complete" | "on_hold" | "cancelled";

export interface Concept {
  id: string;
  name: string;
  status: ConceptStatus;
  intent: string;
  current_design: string;
  current_shape: string;
  horizon: string | null;
  parent: string | null;
}

export interface ConceptEdge {
  id: string;
  from: string; // aliased from from_id
  to: string; // aliased from to_id
  label: string;
  created: string | null;
}

export interface Story {
  id: string;
  name: string;
  story_type: string;
  status: WorkStatus;
  contributes_to: string[];
  belongs_to: string | null;
}

export interface ActionItem {
  story_id: string;
  id: string;
  name: string;
  status: WorkStatus;
  depends_on: string[];
}

export interface Milestone {
  id: string;
  name: string;
  status: MilestoneStatus;
  scope: string[];
}

export interface Identity {
  mission: string | null;
  vision: string | null;
  values: string | null;
  goals: string | null;
  tone_and_manner: string | null;
  extras: Record<string, string>;
}

export interface Release {
  tag: string;
  milestone_id: string | null;
  released_at: string | null;
}

export interface Graph {
  identity: Identity | null;
  concepts: Concept[];
  concept_edges: ConceptEdge[];
  milestones: Milestone[];
  stories: Story[];
  action_items: ActionItem[];
  releases: Release[];
}

export type WorkspaceLens = "plan" | "build" | "live";

export type BranchSide = "left" | "right";

export interface NodeLayout {
  // Persisted drag position. When omitted, the canvas uses auto-layout.
  x?: number;
  y?: number;
  collapsed?: boolean;
  // Only meaningful for top-level Concepts on the Plan canvas. Decides which
  // side of the Identity root this branch and its subtree extends toward.
  side?: BranchSide;
}

export interface Layout {
  nodes: Record<string, NodeLayout>;
}
