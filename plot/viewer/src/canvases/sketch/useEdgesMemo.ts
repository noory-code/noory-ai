// Thin React wrapper around ``edgeTransform``. Uses useMemo for
// referential stability; the pure transform does the work.
//
// v0.15 Phase 3.4 — the doc.canvas_kind read is gone; the
// ``hideRootServiceNode`` decision now flows in from the canvas
// wrapper (ServiceDetailCanvas → true, others → false).
import { useMemo } from "react";
import type { Edge } from "reactflow";
import type { AnchorPlacement, CanvasDoc } from "../../types";
import { edgeTransform, type AnchorArrowMode } from "./edgeTransform";
import { PROJECT_ANCHOR_ID } from "./constants";

export interface UseEdgesMemoArgs {
  doc: CanvasDoc;
  nearestCollapsedAncestor: (id: string) => string | null;
  valueFlowOn: boolean;
  hideRootServiceNode: boolean;
  /** Wrapper-supplied anchor-relative arrow orientation (D-2026-05-31-AA +
   *  D-2026-06-14-C): Foundation/Actors ``"converge"``, Services
   *  ``"diverge"``, ServiceDetail ``"none"``. Replaces a banned
   *  ``doc.canvas_kind`` read in this hook. */
  anchorArrowMode: AnchorArrowMode;
  /** v0.40.0 (D-2026-06-01-E) — the project anchor placement, so edges
   *  can attach to the side facing the other node (the anchor isn't in
   *  doc.nodes). Null on ServiceDetail (no anchor). */
  projectAnchor: AnchorPlacement | null | undefined;
}

export function useEdgesMemo({
  doc,
  nearestCollapsedAncestor,
  valueFlowOn,
  hideRootServiceNode,
  anchorArrowMode,
  projectAnchor,
}: UseEdgesMemoArgs): Edge[] {
  // v0.40.0 (D-2026-06-01-E) — node-centre lookup so each edge attaches
  // to the handle facing the other node (floating removed). The
  // synthetic anchor isn't in doc.nodes, so seed it explicitly.
  const nodeCenters = useMemo(() => {
    const m = new Map<string, { cx: number; cy: number }>();
    for (const n of doc.nodes) {
      m.set(n.id, { cx: n.x + n.width / 2, cy: n.y + n.height / 2 });
    }
    if (projectAnchor) {
      m.set(PROJECT_ANCHOR_ID, {
        cx: projectAnchor.x + projectAnchor.width / 2,
        cy: projectAnchor.y + projectAnchor.height / 2,
      });
    }
    return m;
  }, [doc.nodes, projectAnchor]);
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
        // D-2026-05-31-AA + D-2026-06-14-C — anchor-relative arrow mode is a
        // wrapper-supplied prop (converge / diverge / none), not a
        // doc.canvas_kind read in this hook.
        anchorArrowMode,
        nodeCenters,
      }),
    [
      doc.edges,
      doc.service_ref,
      nearestCollapsedAncestor,
      valueFlowOn,
      hideRootServiceNode,
      anchorArrowMode,
      nodeCenters,
    ],
  );
}
