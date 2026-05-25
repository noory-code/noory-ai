// Pure helpers for the v0.26 directed-edge hierarchy model.
//
// v0.26.0 (D-2026-05-25-A) — parent-child relationships are derived
// from ``SketchEdge.directed === true`` rather than the (removed)
// ``parent_id`` field. The helpers here are tiny + side-effect-free
// so any consumer (Inspector lists, drag-and-drop, node sort,
// overlap detection, …) can express "the parent of X" or "the
// children of X" without bringing the BFS / Map plumbing along.
//
// Determinism: when a node has multiple incoming directed edges
// (multi-parent), ``parentIdOf`` picks the lexicographically
// smallest source id — matches the propagation walk's tie-break
// (plot_mcp/propagation.py::_pick_parent).
//
// No React imports — these helpers live in component callbacks +
// memoised hooks alike.

import type { SketchEdge } from "../../types";

/** Return the (deterministic) parent id of ``nodeId``: the source of
 *  the lexicographically smallest incoming directed edge, or null if
 *  none. */
export function parentIdOf(
  edges: SketchEdge[],
  nodeId: string,
): string | null {
  let pick: string | null = null;
  for (const e of edges) {
    if (!e.directed) continue;
    if (e.target !== nodeId) continue;
    if (pick === null || e.source < pick) pick = e.source;
  }
  return pick;
}

/** Return all parent ids of ``nodeId`` (every source of an incoming
 *  directed edge), sorted ascending for determinism. */
export function parentIdsOf(
  edges: SketchEdge[],
  nodeId: string,
): string[] {
  const out: string[] = [];
  for (const e of edges) {
    if (!e.directed) continue;
    if (e.target !== nodeId) continue;
    out.push(e.source);
  }
  return out.sort();
}

/** Return all direct child ids of ``parentId`` (every target of an
 *  outgoing directed edge from ``parentId``), sorted ascending. */
export function childIdsOf(
  edges: SketchEdge[],
  parentId: string,
): string[] {
  const out: string[] = [];
  for (const e of edges) {
    if (!e.directed) continue;
    if (e.source !== parentId) continue;
    out.push(e.target);
  }
  return out.sort();
}

/** True iff ``nodeId`` has any incoming directed edge. */
export function hasParent(edges: SketchEdge[], nodeId: string): boolean {
  return parentIdOf(edges, nodeId) !== null;
}
