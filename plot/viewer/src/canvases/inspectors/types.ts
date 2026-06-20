/**
 * Props the per-kind inspector wrappers consume. A subset of the
 * legacy ``SketchInspectorProps`` — only what every kind body needs.
 *
 * Kind-specific extras (e.g. ActorRef's ``onRepickActorRef``) live on
 * per-kind prop interfaces declared inside each
 * ``inspectors/{kind}/index.tsx`` file.
 */
import type { CanvasKind, SketchEdge, SketchNode } from "../../types";

export interface KindInspectorProps {
  /** Currently selected node (the per-kind component narrows on
   *  ``node.kind`` internally — single line, discriminator flow). */
  node: SketchNode;
  /** All nodes on the canvas, so per-kind inspectors can compute
   *  derived data (e.g. CategoryInspector counts its child services). */
  allNodes: SketchNode[];
  /** v0.26.0 (D-2026-05-25-A) — all edges on the canvas. Used by
   *  per-kind inspectors that count children (parent-child is now
   *  derived from directed edges, not parent_id). */
  allEdges: SketchEdge[];
  /** Patch the selected node's own fields. */
  onPatchNode: (patch: Partial<SketchNode>) => void;
  /** Remove a node entirely (used by ``BaseInspector``'s delete button). */
  onDeleteNode: (nodeId: string) => void;
  /** v0.18.0 Phase 3 (D-2026-05-16-E) — publish the selected node
   *  (used by ``BaseInspector``'s publish button). Optional so the
   *  prop can be elided in tests / shells that don't surface
   *  publish. */
  onPublishNode?: (nodeId: string) => void;
  /** v0.23.x (D-2026-05-17-J) — unpublish (git revert most recent
   *  publish commit). Optional; surfaced only when the node has a
   *  publish to revert. */
  onUnpublishNode?: (nodeId: string) => void;
  /** Close the panel (used by ``BaseInspector``'s close button). */
  onClose: () => void;
  /** D-2026-06-15-O — render the inspector read-only (no editable inputs,
   *  no delete / publish / close / composition affordances). Used by the
   *  ServiceDetail fallback inspector, which shows the subject service's
   *  fields cross-doc without letting the user edit them from the detail
   *  canvas. Default false. */
  readOnly?: boolean;
  /** v0.7: needed for the MD editor's file paths + preview-cache hints. */
  projectPath: string;
  projectId: string;
  canvasKind: CanvasKind;
  /** v0.27.13 (D-2026-05-28-H) — required for the published-versions
   *  fetch on service_detail canvases. The backend's
   *  ``GET .../canvases/service_detail/nodes/.../published`` returns
   *  500 when ``service_id`` is missing (read_canvas raises
   *  ValueError); the Inspector now passes it through so the URL is
   *  always complete. Optional on every other canvas. */
  serviceId?: string;
  /** v0.2 multi-canvas: actors across all canvases. ActorRefInspector
   *  uses this to look up the referenced actor master + detect orphans. */
  availableActors?: SketchNode[];
  /** D-2026-06-17-B — core_value + identity masters for the service
   *  inspector's reference chips (뭘 양보 못 하나 / 어떤 결로). */
  availableValues?: SketchNode[];
  availableIdentities?: SketchNode[];
  /** v0.11 — open ActorRefPicker in rewire mode for an orphan actor_ref. */
  onRepickActorRef?: (nodeId: string) => void;
}
