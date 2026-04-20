export type Shape =
  | "rectangle"
  | "rounded"
  | "circle"
  | "ellipse"
  | "diamond"
  | "hexagon"
  | "octagon";

/**
 * v0.2 node kinds. See PHILOSOPHY.md (P5, P11).
 *   core    — the single project-identity root (holds mission + core values
 *             + identity for the whole sketch).
 *   actor   — participant; may carry ``is_root=true`` to mark actor-tree centre.
 *   service — value hub; may carry ``is_root=true`` to mark service-tree centre.
 *   rule    — composition element inside a service (data-only, shown in Inspector).
 *   content — composition element inside a service (data-only, shown in Inspector).
 * Sub-service / sub-actor are not separate kinds — they're service/actor
 * with a non-null parent_id (hierarchical decomposition).
 */
export type NodeKind = "core" | "actor" | "service" | "rule" | "content";

/**
 * Plural forms of value that can flow along an edge. See PHILOSOPHY.md (P2).
 */
export type ValueForm =
  | "economic"    // 돈, 결제, 수수료
  | "attention"   // 관심, 트래픽
  | "social"      // 이름, 명성, 관계, 신뢰
  | "cognitive"   // 정보, 데이터, 노하우
  | "experience"  // 즐거움, 편의, 성취
  | "access"      // 기회, 멤버십, 독점성
  | "effort";     // 시간, 창의 노동

export interface SketchNode {
  id: string;
  label: string;
  body: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  shape: Shape;
  /** Lucide icon name (e.g. "user", "star") or null for no icon. */
  icon: string | null;
  /** v0.2: typed kind. ``null`` = legacy / untyped. */
  kind: NodeKind | null;
  /** v0.2: nested parent node id, or null for top-level. */
  parent_id: string | null;
  /** v0.2: container fold state. ``false`` = expanded. */
  collapsed: boolean;
  /** v0.2: mark this actor/service as the root of its tree (at most one per kind). */
  is_root: boolean;
  /** v0.2: populated for core / actor-root / service-root only. */
  mission: string;
  core_values: string;
  identity: string;
}

export interface SketchEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle: string | null;
  targetHandle: string | null;
  label: string;
  style: "solid" | "dashed";
  /** v0.2: primary verb (create / pay / deliver / ...). */
  action_verb: string | null;
  /** v0.2: which forms of value flow along this edge. */
  value_form: ValueForm[];
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
