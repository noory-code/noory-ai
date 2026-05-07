// Pure: doc edges → React Flow edges. No React imports, no closures
// captured from a component. Genuinely unit-testable in isolation —
// edges have far fewer dependencies than nodes (no callbacks, just
// data + value-flow toggle), which is why the pure split survives
// here but not in nodeTransform (see D-2026-05-08-B).
import type { Edge } from "reactflow";
import type { CanvasDoc } from "../../types";
import { VALUE_FORM_COLORS } from "../SketchEdgeModal";

export interface EdgeTransformInput {
  edges: CanvasDoc["edges"];
  canvasKind: CanvasDoc["canvas_kind"];
  serviceRef: CanvasDoc["service_ref"];
  /** Walk the parent chain; return the id of the first collapsed
   *  ancestor (not counting ``id`` itself), or null if none. */
  nearestCollapsedAncestor: (id: string) => string | null;
  /** When on, edges are recoloured by their first value_form entry. */
  valueFlowOn: boolean;
}

export function edgeTransform(input: EdgeTransformInput): Edge[] {
  const { edges, canvasKind, serviceRef, nearestCollapsedAncestor, valueFlowOn } = input;
  // v0.12.2 — same hide rule as the nodes transform: drop edges that
  // point at the service-detail modal's hidden service-root.
  const isHiddenRoot = (id: string): boolean =>
    canvasKind === "service_detail" && !!serviceRef && id === serviceRef;
  const out: Edge[] = [];
  for (const e of edges) {
    if (isHiddenRoot(e.source) || isHiddenRoot(e.target)) continue;
    const sAncestor = nearestCollapsedAncestor(e.source);
    const tAncestor = nearestCollapsedAncestor(e.target);
    const src = sAncestor ?? e.source;
    const tgt = tAncestor ?? e.target;
    if (sAncestor && tAncestor && sAncestor === tAncestor) continue;
    if (src === tgt) continue;
    const stroke =
      valueFlowOn && e.value_form && e.value_form.length > 0
        ? VALUE_FORM_COLORS[e.value_form[0]]
        : undefined;
    out.push({
      id: e.id,
      source: src,
      target: tgt,
      sourceHandle: sAncestor ? undefined : e.sourceHandle ?? undefined,
      targetHandle: tAncestor ? undefined : e.targetHandle ?? undefined,
      label: e.label || undefined,
      style: {
        ...(e.style === "dashed" ? { strokeDasharray: "6 4" } : {}),
        ...(stroke ? { stroke, strokeWidth: e.value_form.length } : {}),
      },
    });
  }
  return out;
}
