// Thin React wrapper around ``edgeTransform``. Uses useMemo for
// referential stability; the pure transform does the work.
import { useMemo } from "react";
import type { Edge } from "reactflow";
import type { CanvasDoc } from "../../types";
import { edgeTransform } from "./edgeTransform";

export interface UseEdgesMemoArgs {
  doc: CanvasDoc;
  nearestCollapsedAncestor: (id: string) => string | null;
  valueFlowOn: boolean;
}

export function useEdgesMemo({
  doc,
  nearestCollapsedAncestor,
  valueFlowOn,
}: UseEdgesMemoArgs): Edge[] {
  return useMemo(
    () =>
      edgeTransform({
        edges: doc.edges,
        canvasKind: doc.canvas_kind,
        serviceRef: doc.service_ref,
        nearestCollapsedAncestor,
        valueFlowOn,
      }),
    [doc.edges, doc.canvas_kind, doc.service_ref, nearestCollapsedAncestor, valueFlowOn],
  );
}
