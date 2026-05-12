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
}
