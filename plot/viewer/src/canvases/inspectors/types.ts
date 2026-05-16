/**
 * Props the per-kind inspector wrappers consume. A subset of the
 * legacy ``SketchInspectorProps`` — only what every kind body needs.
 *
 * Kind-specific extras (e.g. Service's ``onAddChild`` /
 * ``availableActors`` for the composition list, ActorRef's
 * ``onRepickActorRef``) live on per-kind prop interfaces declared
 * inside each ``inspectors/{kind}/index.tsx`` file.
 */
import type { CanvasKind, SketchNode } from "../../types";

export interface KindInspectorProps {
  /** Currently selected node (the per-kind component narrows on
   *  ``node.kind`` internally — single line, discriminator flow). */
  node: SketchNode;
  /** All nodes on the canvas, so per-kind inspectors can compute
   *  derived data (e.g. CategoryInspector counts its child services). */
  allNodes: SketchNode[];
  /** Patch the selected node's own fields. */
  onPatchNode: (patch: Partial<SketchNode>) => void;
  /** Remove a node entirely (used by ``BaseInspector``'s delete button). */
  onDeleteNode: (nodeId: string) => void;
  /** v0.18.0 Phase 3 (D-2026-05-16-E) — publish the selected node
   *  (used by ``BaseInspector``'s publish button). Optional so the
   *  prop can be elided in tests / shells that don't surface
   *  publish. */
  onPublishNode?: (nodeId: string) => void;
  /** Close the panel (used by ``BaseInspector``'s close button). */
  onClose: () => void;
  /** v0.7: needed for the MD editor's file paths + preview-cache hints. */
  projectPath: string;
  projectId: string;
  canvasKind: CanvasKind;
  /** v0.2 multi-canvas: actors across all canvases. ActorRefInspector
   *  uses this to look up the referenced actor master + detect orphans. */
  availableActors?: SketchNode[];
  /** v0.10 Step 3: foundation masters used by the *_ref inspectors to
   *  display the referenced master's label + detect orphans. */
  availableMissions?: SketchNode[];
  availableValues?: SketchNode[];
  availableIdentities?: SketchNode[];
  /** v0.11 — open ActorRefPicker in rewire mode for an orphan actor_ref. */
  onRepickActorRef?: (nodeId: string) => void;
  /** v0.11.1 — open FoundationRefPicker in rewire mode for an orphan
   *  mission_ref / value_ref / identity_ref. */
  onRepickFoundationRef?: (nodeId: string) => void;
  /** v0.10 Step 6: ServiceInspector composition list — create a rule
   *  or content child under the parent service. */
  onAddChild?: (parentId: string, kind: "rule" | "content") => void;
  /** v0.10 Step 6: edit a composition child (rule / content) in place. */
  onPatchChild?: (childId: string, patch: Partial<SketchNode>) => void;
  /** v0.10 Step 6: remove a composition child. */
  onRemoveChild?: (childId: string) => void;
}
