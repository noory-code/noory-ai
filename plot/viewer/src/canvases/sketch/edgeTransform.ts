// Pure: doc edges → React Flow edges. No React imports, no closures
// captured from a component. Genuinely unit-testable in isolation —
// edges have far fewer dependencies than nodes (no callbacks, just
// data + value-flow toggle), which is why the pure split survives
// here but not in nodeTransform (see D-2026-05-08-B).
//
// v0.15 Phase 3.4 — the canvas_kind switch moved out to the
// ``hideRootServiceNode`` wrapper-supplied flag. ServiceDetailCanvas
// passes true (and supplies serviceRef); other wrappers pass false.
import { MarkerType, type Edge } from "reactflow";
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
  /** v0.28.1 (D-2026-05-30-D) — source-kind lookup for foundation-
   *  injection styling. An edge whose source is a foundation ref
   *  (mission_ref / value_ref / identity_ref) renders as an animated
   *  violet "injection" edge. Optional — when omitted, no edge is
   *  styled as injection (back-compat for non-ServiceDetail canvases). */
  nodeKindById?: (id: string) => string | undefined;
}

// v0.28.1 (D-2026-05-30-D) — foundation refs whose outgoing edges read
// as "this essence fires here". ``actor_ref`` is excluded: the
// user-side actor_ref → entry subject edge is the sequence anchor, not
// an injection.
const FOUNDATION_REF_KINDS = new Set<string>(["mission_ref", "value_ref", "identity_ref"]);
const INJECTION_STROKE = "#8b5cf6"; // violet-500

export function edgeTransform(input: EdgeTransformInput): Edge[] {
  const {
    edges,
    serviceRef,
    nearestCollapsedAncestor,
    valueFlowOn,
    hideRootServiceNode,
    nodeKindById,
  } = input;
  const isHiddenRoot = (id: string): boolean =>
    hideRootServiceNode && !!serviceRef && id === serviceRef;
  const out: Edge[] = [];
  for (const e of edges) {
    if (isHiddenRoot(e.source) || isHiddenRoot(e.target)) continue;
    const sAncestor = nearestCollapsedAncestor(e.source);
    const tAncestor = nearestCollapsedAncestor(e.target);
    const src = sAncestor ?? e.source;
    const tgt = tAncestor ?? e.target;
    // Collapsed-ancestor collapse: both endpoints fold into the same
    // collapsed parent → edge is invisible inside that subtree, drop.
    if (sAncestor && tAncestor && sAncestor === tAncestor) continue;
    // ``src === tgt`` after collapse logic. Two cases:
    //   (a) Original ``e.source === e.target`` (user-drawn self-loop)
    //       → render as a self-loop arc per D-2026-05-12-M.
    //   (b) ``e.source !== e.target`` but exactly one side collapsed
    //       into the same id as the other → cross-subtree edge that
    //       now looks like a self-loop on the collapsed parent; drop.
    const isRealSelfLoop = e.source === e.target;
    if (src === tgt && !isRealSelfLoop) continue;
    // v0.28.1 (D-2026-05-30-D) — injection edge: source is a foundation
    // ref. Computed from the original (pre-collapse) source so a
    // collapsed-into-parent edge doesn't lose the signal.
    const isInjection = nodeKindById
      ? FOUNDATION_REF_KINDS.has(nodeKindById(e.source) ?? "")
      : false;
    const stroke = isInjection
      ? INJECTION_STROKE
      : valueFlowOn && e.value_form && e.value_form.length > 0
        ? VALUE_FORM_COLORS[e.value_form[0]]
        : undefined;
    out.push({
      id: e.id,
      source: src,
      target: tgt,
      sourceHandle: sAncestor ? undefined : e.sourceHandle ?? undefined,
      targetHandle: tAncestor ? undefined : e.targetHandle ?? undefined,
      label: e.label || undefined,
      // Self-loops route through SelfLoopEdge (curved arc); regular
      // edges keep React Flow's default Bezier path.
      ...(isRealSelfLoop ? { type: "selfLoop" } : {}),
      // v0.28.1 (D-2026-05-30-D) — injection edges animate (marching
      // dashes flow source → target = the foundation flowing into the
      // flow node).
      ...(isInjection ? { animated: true } : {}),
      // v0.26.0 (D-2026-05-25-A) — directed edges render an arrowhead
      // at the target end. Undirected edges (``directed === false``)
      // render unadorned. The arrow colour matches the resolved stroke
      // so value-flow recolouring stays consistent.
      ...(e.directed
        ? {
            markerEnd: {
              type: MarkerType.ArrowClosed,
              width: 18,
              height: 18,
              color: stroke ?? "#64748b",
            },
          }
        : {}),
      style: {
        ...(e.style === "dashed" ? { strokeDasharray: "6 4" } : {}),
        // Injection: violet dashed stroke. Otherwise value-flow recolour.
        ...(isInjection
          ? { stroke: INJECTION_STROKE, strokeDasharray: "4 4", strokeWidth: 1.5 }
          : stroke
            ? { stroke, strokeWidth: e.value_form.length }
            : {}),
      },
    });
  }
  return out;
}
