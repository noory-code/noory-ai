// Semantic-aware fold hierarchy — v0.30.1 (D-2026-05-31-D).
//
// Collapse/fold derives parent→child from the edge's stored
// ``relation`` (the SSOT from edgeSemantics), not just ``directed``:
//   - flow        → source = parent, target = child (sequence / tree).
//   - inheritance → target = parent, source = child (INVERTED — the
//                   arrow points child→superclass on the actors canvas,
//                   but collapsing the *superclass* must hide its
//                   subclasses).
//   - injection   → null — an essence overlay doesn't contain its
//                   target, so it never participates in fold.
// Undirected edges (``directed === false``) define no hierarchy.
//
// Pure module (no React) — consumed by useCollapsedTree + useNodesMemo
// so the two never disagree on what counts as a parent edge.
import type { SketchEdge } from "../types";

export interface FoldEndpoints {
  parent: string;
  child: string;
}

export function foldEndpoints(edge: SketchEdge): FoldEndpoints | null {
  if (!edge.directed) return null;
  if (edge.relation === "injection") return null;
  if (edge.relation === "inheritance") {
    return { parent: edge.target, child: edge.source };
  }
  // flow (or a pre-v0.30 edge with no relation)
  return { parent: edge.source, child: edge.target };
}
