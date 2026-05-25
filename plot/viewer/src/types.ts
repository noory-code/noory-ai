/**
 * Plot v0.15 viewer wire types.
 *
 * Per-node typed shapes live in ``./domain/`` as per-kind entity
 * classes; ``SketchNode`` itself is the discriminated union of those
 * classes (re-exported below). The legacy god ``SketchNode`` interface
 * — every kind's typed fields collapsed into one shape — was retired
 * in v0.15 Phase 2.10 (D-2026-05-12-B).
 */
export type Shape =
  | "rectangle"
  | "rounded"
  | "circle"
  | "ellipse"
  | "diamond"
  | "hexagon"
  | "octagon";

/**
 * Node kinds. Mirrors ``plot_mcp/models.py::NodeKind`` 1:1.
 *   project         — Foundation-canvas central anchor (circle, auto-seeded,
 *                     cannot be deleted; label mirrors ProjectDoc.name).
 *   mission         — Foundation-canvas child; 0..N. Carries typed fields
 *                     ``what_we_do`` / ``why`` / ``direction``.
 *   core_value      — Foundation-canvas child; 0..N.
 *   identity        — Foundation-canvas child; 0..N peers.
 *   actor           — participant in the value economy (Actor canvas).
 *   actor_ref       — reference to an actor (Service canvases);
 *                     carries ``ref_actor_id``.
 *   category        — top-level grouping on the Services canvas (v0.12).
 *   service         — leaf inside a category.
 *   rule / content  — composition element inside a service (modal only).
 *   metric / step   — composition KPI / procedural step (modal only).
 *   mission_ref / value_ref / identity_ref — Foundation references.
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
  | "mission_ref"
  | "value_ref"
  | "identity_ref"
  | "metric"
  | "step"
  | "category";

/** v0.10 Step 3: the four ref kinds form a uniform family. */
export type RefKind = "actor_ref" | "mission_ref" | "value_ref" | "identity_ref";

/**
 * Plural forms of value that can flow along an edge. See PHILOSOPHY.md (P2).
 */
export type ValueForm =
  | "economic" // 돈, 결제, 수수료
  | "attention" // 관심, 트래픽
  | "social" // 이름, 명성, 관계, 신뢰
  | "cognitive" // 정보, 데이터, 노하우
  | "experience" // 즐거움, 편의, 성취
  | "access" // 기회, 멤버십, 독점성
  | "effort"; // 시간, 창의 노동

// v0.15 Phase 2.10 — discriminated-union ``SketchNode`` lives in
// ``./domain/``. Re-exported here so the dozen+ files that already
// import from ``../types`` keep working.
export type { SketchEntity, SketchNode } from "./domain";

export interface SketchEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle: string | null;
  targetHandle: string | null;
  label: string;
  style: "solid" | "dashed";
  /** v0.26.0 (D-2026-05-25-A) — directed edges carry parent→child
   *  semantics. When True, the renderer draws an arrowhead at the
   *  target end and the fold / hierarchy logic treats source as
   *  parent. New edges default to True; the v0.26 read-time migration
   *  converts pre-v0.26 nodes' ``parent_id`` into directed=True edges. */
  directed: boolean;
  /** v0.2: primary verb (create / pay / deliver / ...). */
  action_verb: string | null;
  /** v0.2: which forms of value flow along this edge. */
  value_form: ValueForm[];
}

// ---------------------------------------------------------------------------
// v0.4 multi-canvas — project folder layout
// ---------------------------------------------------------------------------

export type CanvasKind = "foundation" | "actors" | "services" | "service_detail";

/**
 * Cache key for a loaded canvas inside the viewer. Singleton canvases use
 * just the kind; service-detail uses ``service_detail:{service_id}``.
 */
export type CanvasKey =
  | "foundation"
  | "actors"
  | "services"
  | `service_detail:${string}`;

import type { SketchNode } from "./domain";

export interface CanvasDoc {
  canvas_id: string;
  canvas_kind: CanvasKind;
  service_ref: string | null;
  nodes: SketchNode[];
  edges: SketchEdge[];
}

/**
 * v0.13 Phase 0: per-canvas project anchor placement. The anchor is rendered
 * as a derived node by SketchCanvas (not stored in canvas.json). This is the
 * SSOT for the anchor's position / visual; the canvas no longer carries a
 * ``project`` kind node.
 */
export interface AnchorPlacement {
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  shape: Shape;
}

export interface ProjectDoc {
  id: string;
  name: string;
  created: string;
  updated: string;
  version: number;
  /** v0.13 Phase 0: anchor placements per canvas. Keys are CanvasKind values
   *  (foundation / actors / services). Older project.json may omit; the
   *  viewer applies defaults. */
  anchors?: Partial<Record<CanvasKind, AnchorPlacement>>;
  /** v0.24.13 (D-2026-05-21-B) — blueprint-level semver. Bumped via
   *  ``POST /api/projects/{id}/publish``. Defaults to ``v0.1.0`` for
   *  new projects; older projects without the field get the default
   *  via Pydantic on first read. */
  blueprint_version?: string;
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
