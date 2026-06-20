// Pure: doc edges → React Flow edges. No React imports, no closures
// captured from a component. Genuinely unit-testable in isolation —
// edges have far fewer dependencies than nodes (no callbacks, just
// data + value-flow toggle), which is why the pure split survives
// here but not in nodeTransform (see D-2026-05-08-B).
//
// v0.15 Phase 3.4 — the canvas_kind switch moved out to the
// ``hideRootServiceNode`` wrapper-supplied flag. FeatureDetailCanvas
// passes true (and supplies serviceRef); other wrappers pass false.
import { MarkerType, type Edge } from "reactflow";
import type { CanvasDoc } from "../../types";
import { VALUE_FORM_COLORS } from "../SketchEdgeModal";
import { anchorDistances, sourceIsAnchorWard } from "./anchorDistance";
import { PROJECT_ANCHOR_ID } from "./constants";

/** Anchor-relative arrow orientation mode (D-2026-06-14-C). */
export type AnchorArrowMode = "converge" | "diverge" | "none";

/** Invisible click band around each edge path so thin edges are easy to
 *  select (D-2026-06-14-C). React Flow's default is 20; widen it. */
export const EDGE_INTERACTION_WIDTH = 28;

export interface EdgeTransformInput {
  edges: CanvasDoc["edges"];
  serviceRef: CanvasDoc["feature_ref"];
  /** Walk the parent chain; return the id of the first collapsed
   *  ancestor (not counting ``id`` itself), or null if none. */
  nearestCollapsedAncestor: (id: string) => string | null;
  /** When on, edges are recoloured by their first value_form entry. */
  valueFlowOn: boolean;
  /** v0.15 Phase 3.4 — drop edges that touch the hidden service-root
   *  (true on FeatureDetailCanvas; false elsewhere). */
  hideRootServiceNode: boolean;
  /** Anchor-relative arrow orientation (D-2026-05-31-R + D-2026-06-14-C):
   *  - ``"converge"`` — Foundation + Actors: force every directed edge's
   *    arrowhead toward the anchor-ward endpoint (elements compose into /
   *    participate in the service).
   *  - ``"diverge"`` — Services: force the arrowhead AWAY from the anchor
   *    (anchor → category → service flows outward), regardless of how the
   *    edge was drawn.
   *  - ``"none"`` — leave the drawn direction (FeatureDetail, no anchor). */
  anchorArrowMode: AnchorArrowMode;
  /** v0.40.0 (D-2026-06-01-E) — render-time handle picker. Maps each
   *  node id (incl. the synthetic project anchor, which is NOT in
   *  doc.nodes) to its centre. When present, a non-self-loop edge
   *  attaches to the handle on the side of each node that FACES the
   *  other node, so the edge reads clean from any direction (floating
   *  edges removed). Omit → handles read from the stored edge (unit
   *  tests, and any caller without geometry). */
  nodeCenters?: Map<string, { cx: number; cy: number }>;
}

/** The side of `from` that faces `to`; dominant axis wins. */
function facingSide(
  from: { cx: number; cy: number },
  to: { cx: number; cy: number },
): "t" | "r" | "b" | "l" {
  const dx = to.cx - from.cx;
  const dy = to.cy - from.cy;
  if (Math.abs(dx) >= Math.abs(dy)) return dx >= 0 ? "r" : "l";
  return dy >= 0 ? "b" : "t";
}

// v0.28.1 (D-2026-05-30-D) — an injection edge ("this essence fires
// here") renders animated violet. v0.30.1 (D-2026-05-31-D) — detected
// from the stored ``relation`` SSOT, not a source-kind lookup.
const INJECTION_STROKE = "#8b5cf6"; // violet-500

/** Resolve {sourceHandle, targetHandle} for one rendered edge.
 *
 * v0.41.0 (D-2026-06-01-H) — STORED handles win. The handle each edge end
 * is pinned to (``edge.sourceHandle`` / ``edge.targetHandle``) is the SSOT
 * for where the line attaches; auto-layout reads the same field to decide
 * the node's arm. A stored handle survives only if its endpoint hasn't
 * folded into a collapsed ancestor. When an end has NO stored handle (e.g.
 * a legacy floating-era edge nulled to None), fall back to the geometric
 * facing side so the line still attaches cleanly. */
function resolveHandles(
  rfSource: string,
  rfTarget: string,
  isRealSelfLoop: boolean,
  sAncestor: string | null,
  tAncestor: string | null,
  e: CanvasDoc["edges"][number],
  nodeCenters?: Map<string, { cx: number; cy: number }>,
): { sourceHandle: string | undefined; targetHandle: string | undefined } {
  const storedSource = sAncestor ? undefined : e.sourceHandle ?? undefined;
  const storedTarget = tAncestor ? undefined : e.targetHandle ?? undefined;
  // Geometric fallback only for ends with no stored handle.
  let facingSource: string | undefined;
  let facingTarget: string | undefined;
  if (!isRealSelfLoop && nodeCenters) {
    const s = nodeCenters.get(rfSource);
    const t = nodeCenters.get(rfTarget);
    if (s && t) {
      // All BaseNode handles are type="source" with ids t/r/b/l;
      // ConnectionMode.Loose lets them receive, so the same ids serve
      // both ends.
      facingSource = facingSide(s, t);
      facingTarget = facingSide(t, s);
    }
  }
  return {
    sourceHandle: storedSource ?? facingSource,
    targetHandle: storedTarget ?? facingTarget,
  };
}

export function edgeTransform(input: EdgeTransformInput): Edge[] {
  const {
    edges,
    serviceRef,
    nearestCollapsedAncestor,
    valueFlowOn,
    hideRootServiceNode,
    anchorArrowMode,
    nodeCenters,
  } = input;
  const isHiddenRoot = (id: string): boolean =>
    hideRootServiceNode && !!serviceRef && id === serviceRef;
  // v0.34.4 (D-2026-05-31-R) + D-2026-06-14-C — anchor-relative orientation
  // map. Computed once over the raw edge graph when any anchor mode is on.
  const dist =
    anchorArrowMode !== "none"
      ? anchorDistances(edges, PROJECT_ANCHOR_ID)
      : null;
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
    // v0.34.4 (D-2026-05-31-R) + D-2026-06-14-C — orient the rendered arrow
    // relative to the anchor. Swap the RF source/target (visual only; the doc
    // edge stays the SSOT) so ``markerEnd`` lands on the wanted end:
    //   converge → arrowhead at the anchor-ward endpoint
    //   diverge  → arrowhead at the non-anchor (outward) endpoint
    let rfSource = src;
    let rfTarget = tgt;
    if (dist && e.directed && !isRealSelfLoop) {
      const shouldSwap =
        anchorArrowMode === "converge"
          ? sourceIsAnchorWard(dist, src, tgt) // arrowhead → anchor
          : sourceIsAnchorWard(dist, tgt, src); // diverge: arrowhead → away
      if (shouldSwap) {
        rfSource = tgt;
        rfTarget = src;
      }
    }
    // v0.30.1 (D-2026-05-31-D) — injection read from the stored
    // ``relation`` SSOT (was re-derived from the source kind in
    // v0.28.1). Works on every canvas (foundation essence→anchor
    // included) and stays correct through collapse.
    const isInjection = e.relation === "injection";
    const stroke = isInjection
      ? INJECTION_STROKE
      : valueFlowOn && e.value_form && e.value_form.length > 0
        ? VALUE_FORM_COLORS[e.value_form[0]]
        : undefined;
    out.push({
      id: e.id,
      source: rfSource,
      target: rfTarget,
      // D-2026-06-14-C — wider invisible hit band so thin edges are easy to
      // click/select (RF default 20).
      interactionWidth: EDGE_INTERACTION_WIDTH,
      // v0.40.0 (D-2026-06-01-E) — floating edges removed. When node
      // centres are supplied, attach each end to the handle on the side
      // facing the other node (clean routing from any direction); else
      // fall back to the stored handles. Self-loops always keep stored
      // handles (the arc anchors on them); handles drop when the
      // endpoint folds into a collapsed ancestor.
      ...resolveHandles(rfSource, rfTarget, isRealSelfLoop, sAncestor, tAncestor, e, nodeCenters),
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
          ? // dash period 10 (5 on + 5 off) matches RF's animated
            // stroke-dashoffset cycle (10) so the marching dashes loop
            // seamlessly instead of stuttering (v0.30.3).
            { stroke: INJECTION_STROKE, strokeDasharray: "5 5", strokeWidth: 1.5 }
          : stroke
            ? { stroke, strokeWidth: e.value_form.length }
            : {}),
      },
    });
  }
  return out;
}
