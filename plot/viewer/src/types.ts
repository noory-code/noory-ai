export type Shape =
  | "rectangle"
  | "rounded"
  | "circle"
  | "ellipse"
  | "diamond"
  | "hexagon"
  | "octagon";

/**
 * Node kinds. See docs/CONCEPTS.md and plot_mcp/models.py.
 *   project         — Foundation-canvas central anchor (circle, auto-seeded,
 *                     cannot be deleted; label mirrors ProjectDoc.name).
 *   mission         — Foundation-canvas child; 0..N. Carries typed fields
 *                     ``what_we_do`` / ``why`` / ``direction``.
 *   core_value      — Foundation-canvas child; 0..N.
 *   identity        — Foundation-canvas child; 0..N peers. Each represents
 *                     an aspect (Voice / Energy / Speech style / …).
 *   actor           — participant in the value economy (Actor canvas).
 *   actor_ref       — reference to an actor (Service canvases);
 *                     carries ``ref_actor_id`` pointing at the Actor canvas.
 *   service         — value hub (Overview / Detail / sub-service).
 *   rule / content  — composition element inside a service (Detail only).
 * Sub-service / sub-actor are not separate kinds — they're service/actor
 * with a non-null parent_id (hierarchical decomposition).
 *
 * Deprecated kinds ("core" anchor, "identity_facet" child) are rewritten
 * server-side by ``migrate.upgrade_foundation_canvas_if_needed`` on open.
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
  | "content"
  // v0.10 Step 3: Foundation symbol refs (master/instance pattern). Masters
  // live on the Foundation canvas; instances on Services / Service-Detail.
  | "mission_ref"
  | "value_ref"
  | "identity_ref"
  // v0.10 Step 5: composition kinds inside service_detail.
  //   metric — KPI / SLA / success rate
  //   step   — ordered procedural step
  | "metric"
  | "step";

/** v0.10 Step 3: the four ref kinds form a uniform family. */
export type RefKind = "actor_ref" | "mission_ref" | "value_ref" | "identity_ref";

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
  /** v0.10: typed fields for ``mission`` kind. Default empty for other kinds.
   *  what_we_do = current-tense daily activity; why = reason for being;
   *  direction = positioning (space, not time). See docs/CONCEPTS.md. */
  what_we_do: string;
  why: string;
  direction: string;
  /** v0.10 Step 2: typed fields for ``core_value`` (definition + do/dont)
   *  and ``identity`` (description + do/dont). Other kinds default to "".
   *  do/dont follow the AI-first principle in docs/CONCEPTS.md. */
  definition: string;
  description: string;
  do: string;
  dont: string;
  /** v0.10 Step 4: service typed fields. Top-level service surfaces
   *  what / value_created / scope; sub-service surfaces value_created /
   *  trigger / how / outcome. Both share do / dont. Inspector branches
   *  by canvas kind + parent_id. */
  what: string;
  value_created: string;
  scope: string;
  trigger: string;
  how: string;
  outcome: string;
  /** v0.10 Step 5: metric kind — target value + how it's measured. */
  target: string;
  measurement: string;
  /** v0.10 Step 5: step kind — ordinal in the procedural sequence,
   *  ``null`` = unordered (e.g. parallel branches). */
  order: number | null;
  /** v0.10 Step 6: rule kind — policy text, enforcement mechanism,
   *  and an actor-id → permission-string map (e.g. {"user": "RUD"}). */
  policy: string;
  enforcement: string;
  actor_permissions: Record<string, string>;
  /** v0.10 Step 6: content kind — artifact format + producer/consumer
   *  actor master ids (null = unset). */
  format: string;
  producer_actor_id: string | null;
  consumer_actor_id: string | null;
  /** v0.2 multi-canvas: set when kind === "actor_ref", points at Actor canvas node id. */
  ref_actor_id: string | null;
  /** v0.10 Step 3: Foundation refs. Set when kind === "*_ref"; null otherwise. */
  ref_mission_id: string | null;
  ref_value_id: string | null;
  ref_identity_id: string | null;
  /** v0.9.1: project-relative path to this node's long-form ``details.md``
   *  (resolved server-side under ``.plot/{project_id}/``). ``null`` =
   *  no MD yet; Inspector offers a "Create details" button. */
  details_path?: string | null;
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
  | "foundation"
  | "actors"
  | "services"
  | "service_detail";

/**
 * Cache key for a loaded canvas inside the viewer. Singleton canvases use
 * just the kind; service-detail uses ``service_detail:{service_id}``.
 */
export type CanvasKey =
  | "foundation"
  | "actors"
  | "services"
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
