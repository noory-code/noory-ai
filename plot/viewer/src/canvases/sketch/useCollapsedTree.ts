// Collapsed-tree state machinery: a parent → children map, a node →
// node lookup, the "nearest collapsed ancestor" walk, and the
// toggleCollapsed mutation. SC consumes all five outputs (the lookup
// is also used by drag/drop and keyboard, hence kept here as the
// single source rather than rebuilt elsewhere).
//
// v0.26.0 (D-2026-05-25-A) — parent-child relationships are now
// derived from *directed edges* (``SketchEdge.directed === true``)
// rather than the (removed) ``parent_id`` field. The hook's
// signature gains an ``edges`` argument; the in-memory shape of the
// outputs is unchanged so consumers keep working.
import { type MutableRefObject, useCallback, useMemo } from "react";
import { foldEndpoints } from "../../flow/foldHierarchy";
import type { CanvasDoc, SketchEdge, SketchNode } from "../../types";

export interface UseCollapsedTreeResult {
  /** Parent-id → list of direct child ids. Built once per
   *  ``(nodes, edges)``. A node is a child of another iff there is a
   *  directed edge from parent → child. */
  childIdsByParent: Map<string, string[]>;
  /** Child-id → list of parent ids (every source of an incoming
   *  directed edge). Used by ``nearestCollapsedAncestor`` to walk
   *  upward without rebuilding the inverse map per call. */
  parentIdsByChild: Map<string, string[]>;
  /** Node-id → node lookup. Built once per ``nodes``. */
  nodeById: Map<string, SketchNode>;
  /** Walk the parent chain; return the id of the first collapsed
   *  ancestor (not counting ``nodeId`` itself), or null if none.
   *  When a node has multiple parents (multi-incoming directed
   *  edges), the walk fans out — the first collapsed ancestor on
   *  any path is returned. */
  nearestCollapsedAncestor: (nodeId: string) => string | null;
  /** Flip the ``collapsed`` flag on the given node and persist via
   *  ``onDocChange``. Reads ``docRef.current`` so it stays fresh
   *  across mid-drag updates. */
  toggleCollapsed: (nodeId: string) => void;
  /** Recursive descendant count — shown on the collapsed badge so the
   *  user sees how much is hidden. */
  subtreeSize: (nodeId: string) => number;
}

export function useCollapsedTree(
  nodes: SketchNode[],
  edges: SketchEdge[],
  docRef: MutableRefObject<CanvasDoc>,
  onDocChange: (next: CanvasDoc) => void,
): UseCollapsedTreeResult {
  const childIdsByParent = useMemo(() => {
    const map = new Map<string, string[]>();
    for (const e of edges) {
      // v0.30.1 (D-2026-05-31-D) — parent/child per the edge's stored
      // ``relation`` (flow source=parent, inheritance target=parent,
      // injection excluded), not raw ``directed``.
      const ep = foldEndpoints(e);
      if (!ep) continue;
      const arr = map.get(ep.parent) ?? [];
      arr.push(ep.child);
      map.set(ep.parent, arr);
    }
    return map;
  }, [edges]);

  const parentIdsByChild = useMemo(() => {
    const map = new Map<string, string[]>();
    for (const e of edges) {
      const ep = foldEndpoints(e);
      if (!ep) continue;
      const arr = map.get(ep.child) ?? [];
      arr.push(ep.parent);
      map.set(ep.child, arr);
    }
    return map;
  }, [edges]);

  const nodeById = useMemo(() => {
    const m = new Map<string, SketchNode>();
    for (const n of nodes) m.set(n.id, n);
    return m;
  }, [nodes]);

  const nearestCollapsedAncestor = useCallback(
    (nodeId: string): string | null => {
      // BFS upward across all parent paths. The visited set guards
      // any directed-edge cycle.
      const visited = new Set<string>([nodeId]);
      const queue = [...(parentIdsByChild.get(nodeId) ?? [])];
      while (queue.length > 0) {
        const cur = queue.shift()!;
        if (visited.has(cur)) continue;
        visited.add(cur);
        const node = nodeById.get(cur);
        if (node?.collapsed) return cur;
        for (const p of parentIdsByChild.get(cur) ?? []) {
          if (!visited.has(p)) queue.push(p);
        }
      }
      return null;
    },
    [nodeById, parentIdsByChild],
  );

  const toggleCollapsed = useCallback(
    (nodeId: string) => {
      const current = docRef.current;
      onDocChange({
        ...current,
        nodes: current.nodes.map((n) =>
          n.id === nodeId ? { ...n, collapsed: !n.collapsed } : n,
        ),
      });
    },
    [docRef, onDocChange],
  );

  const subtreeSize = useCallback(
    (nodeId: string): number => {
      // BFS descendant count with a visited guard (cycles possible
      // once edges define hierarchy).
      const visited = new Set<string>([nodeId]);
      const queue = [...(childIdsByParent.get(nodeId) ?? [])];
      let total = 0;
      while (queue.length > 0) {
        const cur = queue.shift()!;
        if (visited.has(cur)) continue;
        visited.add(cur);
        total += 1;
        for (const c of childIdsByParent.get(cur) ?? []) {
          if (!visited.has(c)) queue.push(c);
        }
      }
      return total;
    },
    [childIdsByParent],
  );

  return {
    childIdsByParent,
    parentIdsByChild,
    nodeById,
    nearestCollapsedAncestor,
    toggleCollapsed,
    subtreeSize,
  };
}
