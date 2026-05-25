// Renders the four modal / picker blocks the canvas can show:
// - SketchBodyModal — long-form node body editor (double-click node body).
// - SketchEdgeModal — edge label / dashed / value-form editor (double-click edge).
// - FoundationRefPicker — picker for unbound mission/value/identity ref drops.
// - ActorRefPicker — picker for unbound actor_ref drops or rewire flow.
//
// All four are conditional on their respective state. Inspector is
// not bundled here — it lives one level up in SC because its
// width-toggle persistence and selection lifecycle are owned by the
// shell.
import {
  type Dispatch,
  type MutableRefObject,
  type SetStateAction,
} from "react";
import { type Edge, type Node } from "reactflow";
import type { CanvasDoc, SketchNode as DocNode } from "../../types";
import { ActorRefPicker } from "../ActorRefPicker";
import {
  FoundationRefPicker,
  type FoundationRefMasterKind,
  masterKindForRef,
  refIdFieldForKind,
} from "../FoundationRefPicker";
import { SketchBodyModal } from "../SketchBodyModal";
import { SketchEdgeModal } from "../SketchEdgeModal";
import { DEFAULT_HEIGHT, DEFAULT_WIDTH } from "./constants";
import type { NodePreset, PendingActorRef, PendingFoundationRef } from "./types";

export interface SketchModalsProps {
  doc: CanvasDoc;
  docRef: MutableRefObject<CanvasDoc>;
  onDocChange: (next: CanvasDoc) => void;
  nodeById: Map<string, DocNode>;
  updateNode: (id: string, patch: Partial<DocNode>) => void;
  handleNodesDelete: (deleted: Node[]) => void;
  handleEdgesDelete: (deleted: Edge[]) => void;
  addNodeAt: (x: number, y: number, preset?: NodePreset) => void;
  addNestedNodeAt: (args: {
    parentId: string;
    localX: number;
    localY: number;
    preset: NodePreset;
  }) => void;
  bodyModalNodeId: string | null;
  setBodyModalNodeId: Dispatch<SetStateAction<string | null>>;
  edgeModalId: string | null;
  setEdgeModalId: Dispatch<SetStateAction<string | null>>;
  pendingFoundationRef: PendingFoundationRef | null;
  setPendingFoundationRef: Dispatch<SetStateAction<PendingFoundationRef | null>>;
  pendingActorRef: PendingActorRef | null;
  setPendingActorRef: Dispatch<SetStateAction<PendingActorRef | null>>;
  availableActors: DocNode[] | undefined;
  availableMissions: DocNode[] | undefined;
  availableValues: DocNode[] | undefined;
  availableIdentities: DocNode[] | undefined;
}

/** Compute the absolute position of ``parent`` by walking its
 *  ancestor chain. Pulled out of the inline picker callbacks where
 *  it appeared twice. */
function parentAbsolute(
  parent: DocNode,
  _nodeById: Map<string, DocNode>,
): { x: number; y: number } {
  // v0.26.0 (D-2026-05-25-A) — coordinates are flat (no parent-local
  // system anymore). A node's "absolute" position is just its own
  // ``x`` / ``y``. The ``nodeById`` arg stays on the signature for
  // call-site compatibility but is unused.
  return { x: parent.x, y: parent.y };
}

export function SketchModals({
  doc,
  docRef,
  onDocChange,
  nodeById,
  updateNode,
  handleNodesDelete,
  handleEdgesDelete,
  addNodeAt,
  addNestedNodeAt,
  bodyModalNodeId,
  setBodyModalNodeId,
  edgeModalId,
  setEdgeModalId,
  pendingFoundationRef,
  setPendingFoundationRef,
  pendingActorRef,
  setPendingActorRef,
  availableActors,
  availableMissions,
  availableValues,
  availableIdentities,
}: SketchModalsProps) {
  return (
    <>
      {bodyModalNodeId &&
        (() => {
          const target = doc.nodes.find((n) => n.id === bodyModalNodeId);
          if (!target) return null;
          return (
            <SketchBodyModal
              node={target}
              onCommit={(patch) => updateNode(target.id, patch)}
              onClose={() => setBodyModalNodeId(null)}
              onDelete={() => handleNodesDelete([{ id: target.id } as Node])}
            />
          );
        })()}
      {edgeModalId &&
        (() => {
          const target = doc.edges.find((e) => e.id === edgeModalId);
          if (!target) return null;
          return (
            <SketchEdgeModal
              edge={target}
              onCommit={(patch) => {
                const current = docRef.current;
                onDocChange({
                  ...current,
                  edges: current.edges.map((e) =>
                    e.id === target.id ? { ...e, ...patch } : e,
                  ),
                });
              }}
              onClose={() => setEdgeModalId(null)}
              onDelete={() => handleEdgesDelete([{ id: target.id } as Edge])}
            />
          );
        })()}
      {pendingFoundationRef &&
        (() => {
          const masterKind: FoundationRefMasterKind | null = masterKindForRef(
            pendingFoundationRef.refKind,
          );
          if (!masterKind) return null;
          const masters =
            masterKind === "mission"
              ? availableMissions ?? []
              : masterKind === "core_value"
                ? availableValues ?? []
                : availableIdentities ?? [];
          const idField = refIdFieldForKind(pendingFoundationRef.refKind);
          if (!idField) return null;
          return (
            <FoundationRefPicker
              masterKind={masterKind}
              masters={masters}
              mode={pendingFoundationRef.mode}
              onCancel={() => setPendingFoundationRef(null)}
              onPick={(master) => {
                if (pendingFoundationRef.mode === "rewire") {
                  updateNode(pendingFoundationRef.nodeId, {
                    [idField]: master.id,
                    label: `→ ${master.label || master.id}`,
                  } as Partial<DocNode>);
                  setPendingFoundationRef(null);
                  return;
                }
                const { preset, pos, resolved } = pendingFoundationRef;
                const w = preset.width ?? DEFAULT_WIDTH;
                const h = preset.height ?? DEFAULT_HEIGHT;
                const resolvedPreset: NodePreset = {
                  ...preset,
                  label: `→ ${master.label || master.id}`,
                  [idField]: master.id,
                };
                if (resolved.parentId) {
                  const parent = nodeById.get(resolved.parentId)!;
                  const { x: ax, y: ay } = parentAbsolute(parent, nodeById);
                  addNestedNodeAt({
                    parentId: resolved.parentId,
                    localX: Math.max(8, pos.x - ax - w / 2),
                    localY: Math.max(28, pos.y - ay - h / 2),
                    preset: resolvedPreset,
                  });
                } else {
                  addNodeAt(pos.x - w / 2, pos.y - h / 2, resolvedPreset);
                }
                setPendingFoundationRef(null);
              }}
            />
          );
        })()}
      {pendingActorRef && (
        <ActorRefPicker
          nodes={availableActors ?? doc.nodes}
          mode={pendingActorRef.mode}
          onCancel={() => setPendingActorRef(null)}
          onPick={(actor) => {
            if (pendingActorRef.mode === "rewire") {
              updateNode(pendingActorRef.nodeId, {
                ref_actor_id: actor.id,
                label: `→ ${actor.label || actor.id}`,
              });
              setPendingActorRef(null);
              return;
            }
            const { preset, pos, resolved } = pendingActorRef;
            const w = preset.width ?? DEFAULT_WIDTH;
            const h = preset.height ?? DEFAULT_HEIGHT;
            const resolvedPreset: NodePreset = {
              ...preset,
              label: `→ ${actor.label || actor.id}`,
              ref_actor_id: actor.id,
            };
            if (resolved.parentId) {
              const parent = nodeById.get(resolved.parentId)!;
              const { x: ax, y: ay } = parentAbsolute(parent, nodeById);
              addNestedNodeAt({
                parentId: resolved.parentId,
                localX: Math.max(8, pos.x - ax - w / 2),
                localY: Math.max(28, pos.y - ay - h / 2),
                preset: resolvedPreset,
              });
            } else {
              addNodeAt(pos.x - w / 2, pos.y - h / 2, resolvedPreset);
            }
            setPendingActorRef(null);
          }}
        />
      )}
    </>
  );
}
