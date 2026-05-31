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
  // v0.30.1 (D-2026-05-31-D) — injection styling now reads the stored
  // ``edge.relation`` SSOT inside edgeTransform, so the source-kind
  // lookup map (v0.28.1) is no longer needed here.
  return useMemo(
    () =>
      edgeTransform({
        edges: doc.edges,
        serviceRef: doc.service_ref,
        nearestCollapsedAncestor,
        valueFlowOn,
        hideRootServiceNode,
        // v0.34.4 (D-2026-05-31-R) — Foundation + Actors converge on the
        // anchor (elements compose into the service; actors participate).
        constrainArrowToAnchor:
          doc.canvas_kind === "foundation" || doc.canvas_kind === "actors",
      }),
    [
      doc.edges,
      doc.service_ref,
      doc.canvas_kind,
      nearestCollapsedAncestor,
      valueFlowOn,
      hideRootServiceNode,
    ],
  );
}
