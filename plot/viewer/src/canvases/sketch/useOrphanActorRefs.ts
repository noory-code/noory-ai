// Detect actor_ref nodes whose target actor is missing — either never
// existed, or was just deleted on the Actors canvas. The orphans are
// visualised with a red-tinted fill and a "⚠ " label prefix downstream
// (see nodeTransform when Step 5 extracts it). Pure data — no React
// Flow concerns here.
import { useMemo } from "react";
import type { SketchNode } from "../../types";

export function useOrphanActorRefs(
  nodes: SketchNode[],
  availableActors: SketchNode[] | undefined,
): Set<string> {
  return useMemo(() => {
    const pool = availableActors ?? nodes;
    const validActorIds = new Set(
      pool.filter((n) => n.kind === "actor").map((n) => n.id),
    );
    const orphans = new Set<string>();
    for (const n of nodes) {
      if (n.kind !== "actor_ref") continue;
      if (!n.ref_actor_id || !validActorIds.has(n.ref_actor_id)) {
        orphans.add(n.id);
      }
    }
    return orphans;
  }, [nodes, availableActors]);
}
