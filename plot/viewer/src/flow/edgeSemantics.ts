// Edge semantic taxonomy — the default assigner for the stored
// `SketchEdge.relation` field (v0.30.0, D-2026-05-31-C).
//
// `relation` ("flow" | "injection" | "inheritance") is STORED on the
// edge: it is the one wire SSOT read by both the viewer (fold / layout
// / styling) and the server (`propagation.py` publish MINOR-bump). A
// viewer-only derivation would drift from the server's independent
// directed-edge hierarchy walk (plot-design-red-team A8).
//
// `classifyEdge` only decides the DEFAULT when an edge is drawn or
// migrated; once stored, `edge.relation` is authoritative. The rules
// here are mirrored byte-for-byte in `plot_mcp/edge_semantics.py`; a
// parity test keeps the two truth-tables identical.
//
// Pure module (no React) — Clean Architecture.

export type EdgeRelation = "flow" | "injection" | "inheritance";

/** Essence kinds whose outgoing edges inject essence into the target:
 *  the foundation masters and their consumer-plane refs. `actor_ref`
 *  is deliberately excluded — it is the sequence *subject*, not an
 *  essence overlay (the sequence subject, not a foundation ref). */
// mission_ref / value_ref / identity_ref retired 2026-06-20 (D-2026-06-20-G);
// only the Foundation masters remain essence sources.
export const ESSENCE_SOURCE_KINDS: ReadonlySet<string> = new Set([
  "mission",
  "core_value",
  "identity",
]);

/** Default relation for an edge, from its canvas + source-node kind.
 *  Order matters: actors-canvas edges are always inheritance (single
 *  edge type), then essence sources are injection, else flow. */
export function classifyEdge(
  canvasKind: string,
  sourceKind: string | null | undefined,
): EdgeRelation {
  if (canvasKind === "actors") return "inheritance";
  if (sourceKind && ESSENCE_SOURCE_KINDS.has(sourceKind)) return "injection";
  return "flow";
}
