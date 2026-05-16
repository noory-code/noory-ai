/**
 * v0.18.0 Phase 3 (D-2026-05-16-E) — publish eligibility helper.
 *
 * Mirror of ``plot_mcp/md_publish.py::can_publish``. Returns ``true``
 * iff the node is publish-eligible (drives both the Inspector
 * button's visibility and the server endpoint's 409 guard).
 *
 * Rules:
 * - ``project`` (anchor): false — mirrors ``ProjectDoc.name`` only.
 * - ``is_root`` nodes: false — cross-canvas anchors; will publish
 *   via the referent flow once Phase 5 lands.
 * - ``*_ref`` kinds (alias nodes): false — publish the referent
 *   instead.
 * - All other 10 kinds: true.
 */
import type { SketchNode } from "./SketchNode";

const REF_KINDS = new Set<string>([
  "actor_ref",
  "mission_ref",
  "value_ref",
  "identity_ref",
]);

export function canPublish(node: SketchNode): boolean {
  if (node.kind === "project") return false;
  if (node.is_root) return false;
  if (REF_KINDS.has(node.kind)) return false;
  return true;
}
