// Pure helpers for ``handleNodesChange``. The handler stays in the
// SC shell (React Flow's onNodesChange must dispatch atomically per
// the coupling map), but the change-collection and node-update
// passes are pure and worth lifting.
import type { NodeChange } from "reactflow";
import type { CanvasDoc } from "../../types";

export interface NodeChangeMaps {
  posById: Map<string, { x: number; y: number }>;
  dimById: Map<string, { width: number; height: number }>;
}

/**
 * Bucket a stream of NodeChange events into (id → newPos) and
 * (id → newDim) maps. ``dimensions`` events fire continuously
 * during a NodeResizer drag — we only keep ones where ``resizing``
 * is true so React Flow's own post-mount measurements don't
 * clobber user-set sizes.
 */
export function collectNodeChanges(changes: NodeChange[]): NodeChangeMaps {
  const posById = new Map<string, { x: number; y: number }>();
  const dimById = new Map<string, { width: number; height: number }>();
  for (const c of changes) {
    if (c.type === "position" && c.position) posById.set(c.id, c.position);
    if (
      c.type === "dimensions" &&
      c.resizing &&
      c.dimensions &&
      c.dimensions.width > 0 &&
      c.dimensions.height > 0
    ) {
      dimById.set(c.id, c.dimensions);
    }
  }
  return { posById, dimById };
}

/**
 * Apply pos/dim maps to a doc's nodes, returning a new doc. Nodes
 * absent from both maps are returned unchanged. Anchor entries
 * must be peeled off (via ``applyAnchorChange``) before this call
 * — anchor mutations route through ``onAnchorChange``, never
 * ``onDocChange``.
 */
export function applyNodeChangesToDoc(
  current: CanvasDoc,
  posById: Map<string, { x: number; y: number }>,
  dimById: Map<string, { width: number; height: number }>,
): CanvasDoc {
  return {
    ...current,
    nodes: current.nodes.map((n) => {
      const p = posById.get(n.id);
      const d = dimById.get(n.id);
      if (!p && !d) return n;
      return {
        ...n,
        ...(p ?? {}),
        ...(d ? { width: d.width, height: d.height } : {}),
      };
    }),
  };
}
