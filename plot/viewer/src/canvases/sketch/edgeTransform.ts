// Pure: doc edges → React Flow edges. No React imports, no closures
// captured from a component. Genuinely unit-testable in isolation —
// edges have far fewer dependencies than nodes (no callbacks, just
// data + value-flow toggle), which is why the pure split survives
// here but not in nodeTransform (see D-2026-05-08-B).
//
// v0.15 Phase 3.4 — the canvas_kind switch moved out to the
// ``hideRootServiceNode`` wrapper-supplied flag. ServiceDetailCanvas
// passes true (and supplies serviceRef); other wrappers pass false.
import type { Edge } from "reactflow";
import type { CanvasDoc } from "../../types";
import { VALUE_FORM_COLORS } from "../SketchEdgeModal";

export interface EdgeTransformInput {
  edges: CanvasDoc["edges"];
  serviceRef: CanvasDoc["service_ref"];
  /** Walk the parent chain; return the id of the first collapsed
   *  ancestor (not counting ``id`` itself), or null if none. */
  nearestCollapsedAncestor: (id: string) => string | null;
  /** When on, edges are recoloured by their first value_form entry. */
  valueFlowOn: boolean;
  /** v0.15 Phase 3.4 — drop edges that touch the hidden service-root
   *  (true on ServiceDetailCanvas; false elsewhere). */
  hideRootServiceNode: boolean;
}

export function edgeTransform(input: EdgeTransformInput): Edge[] {
  const { edges, serviceRef, nearestCollapsedAncestor, valueFlowOn, hideRootServiceNode } =
    input;
  const isHiddenRoot = (id: string): boolean =>
    hideRootServiceNode && !!serviceRef && id === serviceRef;
  const out: Edge[] = [];
  for (const e of edges) {
    if (isHiddenRoot(e.source) || isHiddenRoot(e.target)) continue;
    const sAncestor = nearestCollapsedAncestor(e.source);
    const tAncestor = nearestCollapsedAncestor(e.target);
    const src = sAncestor ?? e.source;
    const tgt = tAncestor ?? e.target;
    // v0.16.20 (D-2026-05-12-V) — revert v0.16.10 self-loop split.
    // RF default: ``src === tgt`` produces a zero-length / chord
    // line; we drop it instead of rendering an unreadable artifact.
    // The received spec mandate (self-loop visible) is deferred per
    // user "RF 기본 동작" request.
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
