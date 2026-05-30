/**
 * v0.29.0 (D-2026-05-30-I) — group collapse.
 *
 * Membership is the SSOT on the `group` node (`member_ids`). A node is
 * hidden when it belongs to a collapsed group. Pure + keyed on
 * `member_ids` (not edges, unlike the directed-edge
 * `nearestCollapsedAncestor`).
 */
import type { CanvasDoc } from "../../types";

/** Ids of nodes that should be hidden because they belong to a
 *  collapsed `group`. */
export function collapsedGroupMemberIds(nodes: CanvasDoc["nodes"]): Set<string> {
  const hidden = new Set<string>();
  for (const n of nodes) {
    if (n.kind === "group" && n.collapsed) {
      for (const mid of n.member_ids) hidden.add(mid);
    }
  }
  return hidden;
}
