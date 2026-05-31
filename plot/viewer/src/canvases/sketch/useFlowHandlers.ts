// Small React Flow event-handler bundle: handleConnect (new edge),
// handleNodesDelete (with anchor + legacy project-kind protection),
// handleEdgesDelete, handleEdgesChange (no-op stub React Flow still
// requires), handleSelectionChange (selection ref sync), and
// handlePaneDoubleClick (add node where the user double-clicked).
//
// handleNodesChange does NOT live here — it must remain in SC's
// shell because mid-drag freshness against ``docRef.current`` is
// load-bearing per the coupling map. Splitting it would break drag
// persistence.
import { type MutableRefObject, useCallback } from "react";
import type {
  Connection,
  Edge,
  EdgeChange,
  Node,
  OnSelectionChangeParams,
  ReactFlowInstance,
} from "reactflow";
import type { CanvasDoc, SketchEdge } from "../../types";
import { classifyEdge } from "../../flow/edgeSemantics";
import { anchorDistances, sourceIsAnchorWard } from "./anchorDistance";
import { DEFAULT_HEIGHT, DEFAULT_WIDTH, PROJECT_ANCHOR_ID } from "./constants";
import type { NodePreset } from "./types";

export interface UseFlowHandlersArgs {
  docRef: MutableRefObject<CanvasDoc>;
  flowRef: MutableRefObject<ReactFlowInstance | null>;
  selectedNodeIds: MutableRefObject<string[]>;
  onDocChange: (next: CanvasDoc) => void;
  addNodeAt: (x: number, y: number, preset?: NodePreset) => void;
}

export interface UseFlowHandlersResult {
  handleConnect: (connection: Connection) => void;
  handleEdgesChange: (changes: EdgeChange[]) => void;
  handleNodesDelete: (deleted: Node[]) => void;
  handleEdgesDelete: (deleted: Edge[]) => void;
  handlePaneDoubleClick: (event: React.MouseEvent) => void;
  handleSelectionChange: (sel: OnSelectionChangeParams) => void;
}

function freshEdgeId(): string {
  return `e_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
}

export function useFlowHandlers({
  docRef,
  flowRef,
  selectedNodeIds,
  onDocChange,
  addNodeAt,
}: UseFlowHandlersArgs): UseFlowHandlersResult {
  const handleConnect = useCallback(
    (connection: Connection) => {
      if (!connection.source || !connection.target) return;
      const current = docRef.current;
      // v0.34.4 (D-2026-05-31-R) — Foundation + Actors: normalize the new
      // edge so it points at the anchor-ward endpoint, however the user
      // dragged it (which side/handle they started from no longer matters).
      let source = connection.source;
      let target = connection.target;
      let sourceHandle = connection.sourceHandle ?? null;
      let targetHandle = connection.targetHandle ?? null;
      if (current.canvas_kind === "foundation" || current.canvas_kind === "actors") {
        const dist = anchorDistances(current.edges, PROJECT_ANCHOR_ID);
        if (sourceIsAnchorWard(dist, source, target)) {
          [source, target] = [target, source];
          [sourceHandle, targetHandle] = [targetHandle, sourceHandle];
        }
      }
      // v0.30.0 (D-2026-05-31-C) — default-assign the stored edge
      // semantic from the canvas + (post-normalization) source-node kind.
      const sourceKind = current.nodes.find((n) => n.id === source)?.kind;
      const newEdge: SketchEdge = {
        id: freshEdgeId(),
        source,
        target,
        sourceHandle,
        targetHandle,
        label: "",
        style: "solid",
        // v0.26.0 (D-2026-05-25-A) — default to directed so the
        // drag direction (source = handle the user pressed first;
        // target = handle the user released on) becomes from→to
        // for fold / parent-child purposes. User can toggle via
        // edge right-click menu.
        directed: true,
        relation: classifyEdge(current.canvas_kind, sourceKind),
        action_verb: null,
        value_form: [],
      };
      onDocChange({ ...current, edges: [...current.edges, newEdge] });
    },
    [docRef, onDocChange],
  );

  const handleEdgesChange = useCallback((_changes: EdgeChange[]) => {
    // Selection and removal handled elsewhere; React Flow still
    // requires the prop to be present so the change pipeline runs.
  }, []);

  const handleNodesDelete = useCallback(
    (deleted: Node[]) => {
      const current = docRef.current;
      // SPEC §Anchor: anchor cannot be deleted. Legacy project-kind
      // nodes (pre-eviction-migration data) are protected too.
      const protectedIds = new Set(
        current.nodes.filter((n) => n.kind === "project").map((n) => n.id),
      );
      protectedIds.add(PROJECT_ANCHOR_ID);
      const ids = new Set(
        deleted.map((n) => n.id).filter((id) => !protectedIds.has(id)),
      );
      if (ids.size === 0) return;
      onDocChange({
        ...current,
        nodes: current.nodes.filter((n) => !ids.has(n.id)),
        edges: current.edges.filter(
          (e) => !ids.has(e.source) && !ids.has(e.target),
        ),
      });
    },
    [docRef, onDocChange],
  );

  const handleEdgesDelete = useCallback(
    (deleted: Edge[]) => {
      const ids = new Set(deleted.map((e) => e.id));
      const current = docRef.current;
      onDocChange({
        ...current,
        edges: current.edges.filter((e) => !ids.has(e.id)),
      });
    },
    [docRef, onDocChange],
  );

  const handlePaneDoubleClick = useCallback(
    (event: React.MouseEvent) => {
      if (!flowRef.current) return;
      const target = event.target as HTMLElement;
      if (!target.classList.contains("react-flow__pane")) return;
      const pos = flowRef.current.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });
      addNodeAt(pos.x - DEFAULT_WIDTH / 2, pos.y - DEFAULT_HEIGHT / 2);
    },
    [flowRef, addNodeAt],
  );

  const handleSelectionChange = useCallback(
    (sel: OnSelectionChangeParams) => {
      selectedNodeIds.current = sel.nodes.map((n) => n.id);
    },
    [selectedNodeIds],
  );

  return {
    handleConnect,
    handleEdgesChange,
    handleNodesDelete,
    handleEdgesDelete,
    handlePaneDoubleClick,
    handleSelectionChange,
  };
}
