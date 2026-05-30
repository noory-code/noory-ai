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
  // v0.28.1 (D-2026-05-30-D) — source-kind lookup for foundation-
  // injection edge styling. Rebuilt only when the node set changes.
  const kindById = useMemo(() => {
    const m = new Map<string, string>();
    for (const n of doc.nodes) m.set(n.id, n.kind);
    return m;
  }, [doc.nodes]);
  return useMemo(
    () =>
      edgeTransform({
        edges: doc.edges,
        serviceRef: doc.service_ref,
        nearestCollapsedAncestor,
        valueFlowOn,
        hideRootServiceNode,
        nodeKindById: (id) => kindById.get(id),
      }),
    [
      doc.edges,
      doc.service_ref,
      nearestCollapsedAncestor,
      valueFlowOn,
      hideRootServiceNode,
      kindById,
    ],
  );
}
