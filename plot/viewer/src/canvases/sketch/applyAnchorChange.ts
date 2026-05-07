// Detect and consume anchor changes from a NodeChange-collected pair
// of maps. Returns the patch to forward to ``onAnchorChange``, or
// null if the change set didn't touch the anchor.
//
// Mutates the input maps (deletes the anchor entries) so the caller
// falls through to the regular-node path with the anchor already
// peeled off. Mid-drag is hot — copying the maps would be wasteful.
//
// SPEC §Anchor "Mutation routing": anchor changes flow through
// onAnchorChange (NOT onDocChange). This helper enforces that split.
import type { AnchorPlacement } from "../../types";
import { PROJECT_ANCHOR_ID } from "./constants";

export function applyAnchorChange(
  posById: Map<string, { x: number; y: number }>,
  dimById: Map<string, { width: number; height: number }>,
): Partial<AnchorPlacement> | null {
  const pos = posById.get(PROJECT_ANCHOR_ID);
  const dim = dimById.get(PROJECT_ANCHOR_ID);
  if (!pos && !dim) return null;
  const patch: Partial<AnchorPlacement> = {};
  if (pos) {
    patch.x = pos.x;
    patch.y = pos.y;
  }
  if (dim) {
    patch.width = dim.width;
    patch.height = dim.height;
  }
  posById.delete(PROJECT_ANCHOR_ID);
  dimById.delete(PROJECT_ANCHOR_ID);
  return patch;
}
