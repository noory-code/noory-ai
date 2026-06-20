/**
 * v0.18.0 Phase 3 (D-2026-05-16-E) — publish eligibility helper.
 * v0.24.10 (D-2026-05-19-C) — actor is_root now publishable.
 *
 * Mirror of ``plot_mcp/md_publish.py::can_publish``. Returns ``true``
 * iff the node is publish-eligible (drives both the Inspector
 * button's visibility and the server endpoint's 409 guard).
 *
 * Rules:
 * - ``project`` (anchor): false — mirrors ``ProjectDoc.name`` only.
 * - ``service`` (is_root): false — FeatureDetail mirror of a Services-
 *   canvas master; the master gets published, the mirror follows.
 * - ``actor`` (is_root): true — masters like Bana / Admin / Guest hold
 *   their own typed text and own their own version (D-2026-05-19-C).
 *   Future Phase 5 referent flow layers cross-canvas referent updates
 *   on top of this direct-publish path; no migration needed.
 * - ``*_ref`` kinds (alias nodes): false — publish the referent
 *   instead.
 * - All other kinds: true.
 */
import type { SketchNode } from "./SketchNode";

// actor_ref is the only surviving standalone reference node (mission/value/
// identity refs retired 2026-06-20, D-2026-06-20-G).
const REF_KINDS = new Set<string>(["actor_ref"]);

export function canPublish(node: SketchNode): boolean {
  if (node.kind === "project") return false;
  if (node.is_root && node.kind === "service") return false;
  if (REF_KINDS.has(node.kind)) return false;
  return true;
}
