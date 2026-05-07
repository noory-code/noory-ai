// Collapsed-tree state machinery: a parent → children map, a node →
// node lookup, the "nearest collapsed ancestor" walk, and the
// toggleCollapsed mutation. SC consumes all five outputs (the lookup
// is also used by drag/drop and keyboard, hence kept here as the
// single source rather than rebuilt elsewhere).
import { type MutableRefObject, useCallback, useMemo } from "react";
import type { CanvasDoc, SketchNode } from "../../types";

export interface UseCollapsedTreeResult {
  /** Parent-id → list of direct child ids. Built once per ``nodes``. */
  childIdsByParent: Map<string, string[]>;
  /** Node-id → node lookup. Built once per ``nodes``. */
  nodeById: Map<string, SketchNode>;
  /** Walk the parent chain; return the id of the first collapsed
   *  ancestor (not counting ``nodeId`` itself), or null if none. */
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
  docRef: MutableRefObject<CanvasDoc>,
  onDocChange: (next: CanvasDoc) => void,
): UseCollapsedTreeResult {
  const childIdsByParent = useMemo(() => {
    const map = new Map<string, string[]>();
    for (const n of nodes) {
      if (n.parent_id) {
        const arr = map.get(n.parent_id) ?? [];
        arr.push(n.id);
        map.set(n.parent_id, arr);
      }
    }
    return map;
  }, [nodes]);

  const nodeById = useMemo(() => {
    const m = new Map<string, SketchNode>();
    for (const n of nodes) m.set(n.id, n);
    return m;
  }, [nodes]);

  const nearestCollapsedAncestor = useCallback(
    (nodeId: string): string | null => {
      let current = nodeById.get(nodeId);
      while (current?.parent_id) {
        const parent = nodeById.get(current.parent_id);
        if (parent && parent.collapsed) return parent.id;
        current = parent;
      }
      return null;
    },
    [nodeById],
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
      const direct = childIdsByParent.get(nodeId) ?? [];
      let total = direct.length;
      for (const c of direct) total += subtreeSize(c);
      return total;
    },
    [childIdsByParent],
  );

  return { childIdsByParent, nodeById, nearestCollapsedAncestor, toggleCollapsed, subtreeSize };
}
