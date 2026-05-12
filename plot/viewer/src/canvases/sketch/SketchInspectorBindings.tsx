// Wires the inspector panel to the SketchCanvas-side state: which
// node is selected, which prop maps to which canvas mutation, where
// the repick / drill / delete flows route. SC stays a thin shell.
//
// v0.14.27 — calls ``KindInspector`` directly. The legacy
// ``SketchInspector`` (1491 LOC at v0.14.18) was deleted as part of
// the v0.15 structural reset Phase 2.9 once every kind had its own
// per-kind inspector under ``inspectors/{kind}/``.
import { type Dispatch, type MutableRefObject, type SetStateAction } from "react";
import type { Node } from "reactflow";
import type { CanvasDoc, CanvasKind, SketchNode as DocNode } from "../../types";
import { KindInspector } from "../inspectors/KindInspector";
import type { PendingActorRef, PendingFoundationRef } from "./types";

export interface SketchInspectorBindingsProps {
  doc: CanvasDoc;
  docRef: MutableRefObject<CanvasDoc>;
  onDocChange: (next: CanvasDoc) => void;
  inspectorNodeId: string | null;
  setInspectorNodeId: Dispatch<SetStateAction<string | null>>;
  updateNode: (id: string, patch: Partial<DocNode>) => void;
  handleNodesDelete: (deleted: Node[]) => void;
  addCompositionChild: (parentId: string, kind: "rule" | "content") => void;
  setPendingActorRef: Dispatch<SetStateAction<PendingActorRef | null>>;
  setPendingFoundationRef: Dispatch<SetStateAction<PendingFoundationRef | null>>;
  availableActors: DocNode[] | undefined;
  availableMissions: DocNode[] | undefined;
  availableValues: DocNode[] | undefined;
  availableIdentities: DocNode[] | undefined;
  projectPath: string;
  projectId: string;
}

export function SketchInspectorBindings({
  doc,
  docRef,
  onDocChange,
  inspectorNodeId,
  setInspectorNodeId,
  updateNode,
  handleNodesDelete,
  addCompositionChild,
  setPendingActorRef,
  setPendingFoundationRef,
  availableActors,
  availableMissions,
  availableValues,
  availableIdentities,
  projectPath,
  projectId,
}: SketchInspectorBindingsProps) {
  if (!inspectorNodeId) return null;
  const node = doc.nodes.find((n) => n.id === inspectorNodeId) ?? null;
  if (!node) return null;
  return (
    <KindInspector
      node={node}
      allNodes={doc.nodes}
      availableActors={availableActors ?? doc.nodes.filter((n) => n.kind === "actor")}
      availableMissions={availableMissions}
      availableValues={availableValues}
      availableIdentities={availableIdentities}
      projectPath={projectPath}
      projectId={projectId}
      canvasKind={doc.canvas_kind as CanvasKind}
      onRepickActorRef={(nodeId) => setPendingActorRef({ mode: "rewire", nodeId })}
      onRepickFoundationRef={(nodeId) => {
        // v0.11.1 — find the orphan ref's kind and open the picker.
        const target = doc.nodes.find((n) => n.id === nodeId);
        if (
          !target ||
          (target.kind !== "mission_ref" &&
            target.kind !== "value_ref" &&
            target.kind !== "identity_ref")
        ) {
          return;
        }
        setPendingFoundationRef({ mode: "rewire", refKind: target.kind, nodeId });
      }}
      onDeleteNode={(nodeId) => handleNodesDelete([{ id: nodeId } as Node])}
      onPatchNode={(patch) => {
        if (!inspectorNodeId) return;
        updateNode(inspectorNodeId, patch);
      }}
      onAddChild={addCompositionChild}
      onPatchChild={(childId, patch) => updateNode(childId, patch)}
      onRemoveChild={(childId) => {
        const current = docRef.current;
        onDocChange({
          ...current,
          nodes: current.nodes.filter((n) => n.id !== childId),
        });
      }}
      onClose={() => setInspectorNodeId(null)}
    />
  );
}
