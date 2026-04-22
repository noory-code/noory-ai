export type Shape =
  | "rectangle"
  | "rounded"
  | "circle"
  | "ellipse"
  | "diamond"
  | "hexagon"
  | "octagon";

/**
 * Node kinds. See PHILOSOPHY.md (P5, P11) and plot_mcp/models.py.
 *   project         — Core-canvas central anchor (circle, auto-seeded, cannot
 *                     be deleted; label mirrors ProjectDoc.name).
 *   mission         — Core-canvas child; 1..N per Core canvas.
 *   core_value      — Core-canvas child; 0..N.
 *   identity        — Core-canvas child; 1..N peers. Each represents an
 *                     aspect (Voice / Energy / Speech style / …).
 *                     v0.5 absorbed the former identity_facet kind.
 *   actor           — participant in the value economy (Actor canvas).
 *   actor_ref       — reference to an actor (Service canvases);
 *                     carries ``ref_actor_id`` pointing at the Actor canvas.
 *   service         — value hub (Overview / Detail / sub-service).
 *   rule / content  — composition element inside a service (Detail only).
 * Sub-service / sub-actor are not separate kinds — they're service/actor
 * with a non-null parent_id (hierarchical decomposition).
 *
 * Deprecated kinds ("core" anchor, "identity_facet" child) are rewritten
 * server-side by ``migrate.upgrade_core_canvas_if_needed`` on open.
 */
export type NodeKind =
  | "project"
  | "mission"
  | "core_value"
  | "identity"
  | "actor"
  | "actor_ref"
  | "service"
  | "rule"
  | "content";

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
  /** v0.2 multi-canvas: set when kind === "actor_ref", points at Actor canvas node id. */
  ref_actor_id: string | null;
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

// ---------------------------------------------------------------------------
// v0.4 multi-canvas — project folder layout
// ---------------------------------------------------------------------------

export type CanvasKind =
  | "core"
  | "actors"
  | "services_overview"
  | "service_detail";

/**
 * Cache key for a loaded canvas inside the viewer. Singleton canvases use
 * just the kind; service-detail uses ``service_detail:{service_id}``.
 */
export type CanvasKey =
  | "core"
  | "actors"
  | "services_overview"
  | `service_detail:${string}`;

export interface CanvasDoc {
  canvas_id: string;
  canvas_kind: CanvasKind;
  service_ref: string | null;
  nodes: SketchNode[];
  edges: SketchEdge[];
}

export interface ProjectDoc {
  id: string;
  name: string;
  created: string;
  updated: string;
  version: number;
}

export interface ProjectTag {
  name: string;
  sha: string;
  ts: string;
  message: string;
}

export interface ProjectChangedPayload {
  project_id?: string;
  canvas_kind?: CanvasKind;
  service_id?: string;
}

export type SocketEvent =
  | ({ event: "project_changed" } & ProjectChangedPayload)
  | { event: string };
