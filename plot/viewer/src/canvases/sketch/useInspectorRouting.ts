// Inspector routing: tracks which node (if any) is currently selected
// for the right-side Inspector panel, plus the React Flow click
// callbacks that open / close it. The synthetic project anchor is
// excluded from Inspector routing — clicking it does nothing
// (anchor data flows via onAnchorChange, not onDocChange) and
// double-clicking does NOT trigger drill.
//
// Also handles the ``selectNodeId`` prop dispatch: when the App
// arrives with a target id (e.g. jumping from actor_ref to its
// Actor canvas target), the effect picks it up once, fits the
// viewport, and tells the App via onSelectionConsumed.
import {
  type MutableRefObject,
  type Dispatch,
  type SetStateAction,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import type { Node, ReactFlowInstance } from "reactflow";
import type { SketchNode } from "../../types";
import { PROJECT_ANCHOR_ID } from "./constants";

export interface UseInspectorRoutingArgs {
  nodes: SketchNode[];
  flowRef: MutableRefObject<ReactFlowInstance | null>;
  selectNodeId: string | null | undefined;
  onSelectionConsumed: (() => void) | undefined;
  onNodeDrill: ((nodeId: string) => void) | undefined;
}

export interface UseInspectorRoutingResult {
  inspectorNodeId: string | null;
  setInspectorNodeId: Dispatch<SetStateAction<string | null>>;
  onNodeClick: (_evt: unknown, n: Node) => void;
  onNodeDoubleClick: (_evt: unknown, n: Node) => void;
  onPaneClick: () => void;
}

export function useInspectorRouting({
  nodes,
  flowRef,
  selectNodeId,
  onSelectionConsumed,
  onNodeDrill,
}: UseInspectorRoutingArgs): UseInspectorRoutingResult {
  const [inspectorNodeId, setInspectorNodeId] = useState<string | null>(null);

  // v0.2 multi-canvas: honour ``selectNodeId`` arrival (e.g., jumping
  // from an actor_ref on Services to its target on Actors). Runs once
  // per distinct incoming id; afterwards the App clears its URL param.
  const lastAppliedSelectRef = useRef<string | null>(null);
  useEffect(() => {
    if (!selectNodeId) return;
    if (lastAppliedSelectRef.current === selectNodeId) return;
    if (!nodes.some((n) => n.id === selectNodeId)) return;
    setInspectorNodeId(selectNodeId);
    lastAppliedSelectRef.current = selectNodeId;
    const inst = flowRef.current;
    if (inst) inst.fitView({ nodes: [{ id: selectNodeId }], padding: 0.5, duration: 300 });
    onSelectionConsumed?.();
  }, [selectNodeId, nodes, onSelectionConsumed, flowRef]);

  const onNodeClick = useCallback((_evt: unknown, n: Node) => {
    // v0.13 Phase 0: synthetic anchor is read-only — no Inspector.
    if (n.id === PROJECT_ANCHOR_ID) return;
    setInspectorNodeId(n.id);
  }, []);

  const onNodeDoubleClick = useCallback(
    (_evt: unknown, n: Node) => {
      if (n.id === PROJECT_ANCHOR_ID) return;
      onNodeDrill?.(n.id);
    },
    [onNodeDrill],
  );

  const onPaneClick = useCallback(() => setInspectorNodeId(null), []);

  return { inspectorNodeId, setInspectorNodeId, onNodeClick, onNodeDoubleClick, onPaneClick };
}
