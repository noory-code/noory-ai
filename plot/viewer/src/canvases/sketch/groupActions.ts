/**
 * v0.29.0 (D-2026-05-30-I) — group membership actions (pure).
 *
 * `groupSelected` wraps ≥ 2 selected nodes in a new `group` node placed
 * just above their bounding box, with `member_ids` = the selection.
 * `ungroup` drops the group node (members stay put). Membership is the
 * SSOT on the group, so neither touches the member nodes.
 */
import type { CanvasDoc } from "../../types";
import { Group } from "../../domain";

/** Wrap `memberIds` (≥ 2) in a new group node (id = `newId`). Returns
 *  the doc unchanged if fewer than 2 of the ids exist. */
export function groupSelected(
  doc: CanvasDoc,
  memberIds: string[],
  newId: string,
): CanvasDoc {
  const members = doc.nodes.filter((n) => memberIds.includes(n.id));
  if (members.length < 2) return doc;
  const minX = Math.min(...members.map((m) => m.x));
  const minY = Math.min(...members.map((m) => m.y));
  const maxX = Math.max(...members.map((m) => m.x + m.width));
  const height = 48;
  const groupNode = Group.fromJson({
    id: newId,
    kind: "group",
    label: "",
    x: minX,
    y: minY - height - 24,
    width: Math.max(160, maxX - minX),
    height,
    color: "#f1f5f9",
    shape: "rounded",
    icon: null,
    member_ids: members.map((m) => m.id),
  }).toJson();
  return { ...doc, nodes: [...doc.nodes, groupNode] };
}

/** Remove the group node `groupId`; its members are untouched. */
export function ungroup(doc: CanvasDoc, groupId: string): CanvasDoc {
  return { ...doc, nodes: doc.nodes.filter((n) => n.id !== groupId) };
}
