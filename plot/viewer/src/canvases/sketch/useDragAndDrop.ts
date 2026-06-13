// Stencil → canvas placement orchestration. Owns:
// - ``placePresetAt(preset, clientX, clientY)``: hit-tests the drop
//   point, nudges off siblings, and either creates the node directly or
//   stashes a "pending ref" for the picker modal,
// - the two pending-ref states themselves.
//
// The drag GESTURE is captured by the pointer channel
// (``StencilDragContext``, D-2026-06-13-C) — WKWebView does not fire
// HTML5 ``drop`` — which calls ``placePresetAt`` on pointer release over
// a registered canvas pane. SPEC §Drag-and-drop owns the canonical
// hit-test / nudge / hierarchy-edge / picker rules.
import {
  type Dispatch,
  type MutableRefObject,
  type RefObject,
  type SetStateAction,
  useCallback,
  useRef,
  useState,
} from "react";
import type { ReactFlowInstance } from "reactflow";
import type { SketchNode as DocNode } from "../../types";
import { resolveDropTarget, type StencilCanvas, type StencilPreset } from "../SketchStencil";
import { DEFAULT_HEIGHT, DEFAULT_WIDTH } from "./constants";
import { containerAtFlowPoint, findFreeSpot } from "./overlapNudge";
import { useStencilDropTarget } from "./StencilDragContext";
import type { NodePreset, PendingActorRef, PendingFoundationRef } from "./types";
import { useDialog } from "../../shell/dialog/DialogProvider";

export interface UseDragAndDropArgs {
  nodes: DocNode[];
  /** v0.26.0 (D-2026-05-25-A) — edges needed for parent-child queries
   *  during drop-target sibling calculation. */
  edges: import("../../types").SketchEdge[];
  nodeById: Map<string, DocNode>;
  flowRef: MutableRefObject<ReactFlowInstance | null>;
  addNodeAt: (x: number, y: number, preset?: NodePreset) => void;
  addNestedNodeAt: (args: {
    parentId: string;
    localX: number;
    localY: number;
    preset: NodePreset;
  }) => void;
  /** v0.27.10 (D-2026-05-28-A) — the canvas kind. Used by
   *  ``resolveDropTarget`` to apply ServiceDetail's free-form
   *  composition rule. */
  canvasKind?: StencilCanvas;
}

export interface UseDragAndDropResult {
  /** Attach to the canvas pane element. Registered with the pointer-drag
   *  channel so a stencil released over it places a node here. */
  paneRef: RefObject<HTMLDivElement>;
  pendingActorRef: PendingActorRef | null;
  setPendingActorRef: Dispatch<SetStateAction<PendingActorRef | null>>;
  pendingFoundationRef: PendingFoundationRef | null;
  setPendingFoundationRef: Dispatch<SetStateAction<PendingFoundationRef | null>>;
}

export function useDragAndDrop({
  nodes,
  edges,
  nodeById,
  flowRef,
  addNodeAt,
  addNestedNodeAt,
  canvasKind,
}: UseDragAndDropArgs): UseDragAndDropResult {
  const dialog = useDialog();
  const [pendingActorRef, setPendingActorRef] = useState<PendingActorRef | null>(null);
  const [pendingFoundationRef, setPendingFoundationRef] =
    useState<PendingFoundationRef | null>(null);

  const placePresetAt = useCallback(
    (preset: StencilPreset, clientX: number, clientY: number) => {
      if (!flowRef.current) return;
      const pos = flowRef.current.screenToFlowPosition({
        x: clientX,
        y: clientY,
      });
      const w = preset.width ?? DEFAULT_WIDTH;
      const h = preset.height ?? DEFAULT_HEIGHT;
      const container = containerAtFlowPoint(nodes, nodeById, pos.x, pos.y);
      const resolved = resolveDropTarget(
        preset,
        container ? { id: container.id, kind: container.kind } : null,
        canvasKind,
      );
      if ("error" in resolved) {
        void dialog.alert({ message: resolved.error });
        return;
      }
      // v0.11.5 — preset already carries the master id (common case),
      // skip picker. Picker is reserved for orphan rewire flow.
      const presetHasRefId =
        (preset.kind === "actor_ref" && preset.ref_actor_id) ||
        (preset.kind === "mission_ref" && preset.ref_mission_id) ||
        (preset.kind === "value_ref" && preset.ref_value_id) ||
        (preset.kind === "identity_ref" && preset.ref_identity_id);
      if (preset.kind === "actor_ref" && !presetHasRefId) {
        setPendingActorRef({ mode: "create", preset, pos, resolved });
        return;
      }
      if (
        (preset.kind === "mission_ref" ||
          preset.kind === "value_ref" ||
          preset.kind === "identity_ref") &&
        !presetHasRefId
      ) {
        setPendingFoundationRef({
          mode: "create",
          refKind: preset.kind,
          preset,
          pos,
          resolved,
        });
        return;
      }
      if (resolved.parentId) {
        // v0.26.0 (D-2026-05-25-A) — coordinates are flat (no nested
        // parent-local system anymore). The parent's absolute
        // position is just ``parent.x`` / ``parent.y``.
        const parent = nodeById.get(resolved.parentId)!;
        const rawLocalX = Math.max(8, pos.x - parent.x - w / 2);
        const rawLocalY = Math.max(28, pos.y - parent.y - h / 2);
        // Siblings = nodes that share this parent via a directed edge.
        const siblingIds = new Set(
          edges
            .filter((e) => e.directed && e.source === resolved.parentId)
            .map((e) => e.target),
        );
        const siblings = nodes.filter((n) => siblingIds.has(n.id));
        const spot = findFreeSpot(rawLocalX, rawLocalY, w, h, siblings);
        addNestedNodeAt({
          parentId: resolved.parentId,
          localX: spot.x,
          localY: spot.y,
          preset,
        });
      } else {
        const rawX = pos.x - w / 2;
        const rawY = pos.y - h / 2;
        // Top-level peers = nodes that have no incoming directed edge.
        const childIds = new Set(
          edges.filter((e) => e.directed).map((e) => e.target),
        );
        const siblings = nodes.filter((n) => !childIds.has(n.id));
        const spot = findFreeSpot(rawX, rawY, w, h, siblings);
        addNodeAt(spot.x, spot.y, preset);
      }
    },
    [flowRef, nodes, edges, nodeById, addNodeAt, addNestedNodeAt, canvasKind, dialog],
  );

  // Register the pane with the pointer-drag channel (D-2026-06-13-C). The
  // channel calls ``placePresetAt`` on pointer release over ``paneRef``.
  const paneRef = useRef<HTMLDivElement>(null);
  useStencilDropTarget(paneRef, placePresetAt);

  return {
    paneRef,
    pendingActorRef,
    setPendingActorRef,
    pendingFoundationRef,
    setPendingFoundationRef,
  };
}
