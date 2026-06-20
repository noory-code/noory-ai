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
  shouldDrill?: (n: SketchNode) => boolean;
  /** When true, SELECTING (single-click) a ``shouldDrill`` node opens its
   *  detail tab instead of the right inspector (D-2026-06-15-H). Only the
   *  Services canvas sets this; the Service-Detail canvas keeps actor_ref
   *  drill on DOUBLE-click (jump to the actor master), so a single click there
   *  still opens the node's inspector. */
  selectOpensDrill?: boolean;
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
  shouldDrill,
  selectOpensDrill,
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

  const onNodeClick = useCallback(
    (_evt: unknown, n: Node) => {
      // v0.17.1 (D-2026-05-16-B): synthetic anchor has no Inspector, and
      // clicking it also closes any currently-open Inspector — anchor
      // click reads as a deselect for the user.
      if (n.id === PROJECT_ANCHOR_ID) {
        setInspectorNodeId(null);
        return;
      }
      // D-2026-06-15-H — selecting a drillable service node opens its detail
      // TAB instead of the right inspector (the service's content lives in the
      // detail canvas, not a side panel).
      const node = nodes.find((x) => x.id === n.id);
      if (selectOpensDrill && onNodeDrill && node && shouldDrill?.(node)) {
        setInspectorNodeId(null);
        onNodeDrill(n.id);
        return;
      }
      setInspectorNodeId(n.id);
    },
    [nodes, onNodeDrill, shouldDrill, selectOpensDrill],
  );

  const onNodeDoubleClick = useCallback(
    (_evt: unknown, n: Node) => {
      if (n.id === PROJECT_ANCHOR_ID) return;
      // D-2026-06-15-L — double-click drills ONLY nodes the canvas marks
      // drillable (shouldDrill). A non-drillable node (e.g. actor_ref in
      // FeatureDetail, which no longer sets shouldDrill) must NOT navigate
      // away on a body double-click — the click stays put so its inspector
      // (per-service motivation/pain) remains. The old unconditional call
      // jumped to the actor master and was the bug.
      const node = nodes.find((x) => x.id === n.id);
      if (!node || !shouldDrill?.(node)) return;
      onNodeDrill?.(n.id);
    },
    [nodes, shouldDrill, onNodeDrill],
  );

  const onPaneClick = useCallback(() => setInspectorNodeId(null), []);

  return { inspectorNodeId, setInspectorNodeId, onNodeClick, onNodeDoubleClick, onPaneClick };
}
