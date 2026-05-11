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
}
