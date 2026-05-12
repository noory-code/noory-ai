// Thin React wrapper around ``edgeTransform``. Uses useMemo for
// referential stability; the pure transform does the work.
//
// v0.15 Phase 3.4 — the doc.canvas_kind read is gone; the
// ``hideRootServiceNode`` decision now flows in from the canvas
// wrapper (ServiceDetailCanvas → true, others → false).
import { useMemo } from "react";
import type { Edge } from "reactflow";
import type { CanvasDoc } from "../../types";
import { edgeTransform } from "./edgeTransform";

export interface UseEdgesMemoArgs {
  doc: CanvasDoc;
  nearestCollapsedAncestor: (id: string) => string | null;
  valueFlowOn: boolean;
  hideRootServiceNode: boolean;
}

export function useEdgesMemo({
  doc,
  nearestCollapsedAncestor,
  valueFlowOn,
  hideRootServiceNode,
}: UseEdgesMemoArgs): Edge[] {
  return useMemo(
    () =>
      edgeTransform({
        edges: doc.edges,
        serviceRef: doc.service_ref,
        nearestCollapsedAncestor,
        valueFlowOn,
        hideRootServiceNode,
      }),
    [
      doc.edges,
      doc.service_ref,
      nearestCollapsedAncestor,
      valueFlowOn,
      hideRootServiceNode,
    ],
  );
}
