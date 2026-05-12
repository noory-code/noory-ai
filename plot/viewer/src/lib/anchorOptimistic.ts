/**
 * Optimistic anchor update — v0.16.15 (D-2026-05-12-Q).
 *
 * React Flow is a *controlled* component: its ``nodes`` prop is the
 * SSOT for node positions. When the user drags the synthetic project
 * anchor, ``onNodesChange`` fires with a position delta → the App's
 * ``onAnchorChange`` handler PATCHes the server. The server PATCH
 * round-trip takes 100-500ms, and *during that window* the
 * ``summaries`` state still carries the OLD anchor placement, so the
 * computed ``projectAnchor`` prop is OLD, so RF renders the anchor
 * at the OLD position → user sees the anchor snap back to where it
 * was before the drag.
 *
 * Fix: update local state OPTIMISTICALLY before the PATCH fires.
 * After the PATCH resolves, replace with the server-canonical doc.
 * On PATCH failure, revert to the previous doc.
 *
 * This helper is the pure shape of that merge; ``App.tsx``
 * onAnchorChange wraps the network round-trip around it.
 */
import type { AnchorPlacement, CanvasKind, ProjectDoc } from "../types";

/** Default anchor placement (mirrors ``App.tsx::resolveProjectAnchor`` fallback). */
const DEFAULT_ANCHOR: AnchorPlacement = {
  x: -75,
  y: -75,
  width: 150,
  height: 150,
  color: "#fef3c7",
  shape: "circle",
};

/** Resolve the anchor placement for a tab, falling back to default
 *  when the project doesn't have one yet. */
export function resolveAnchorPlacement(
  proj: ProjectDoc | undefined,
  tab: CanvasKind,
): AnchorPlacement {
  if (!proj) return DEFAULT_ANCHOR;
  const fromDoc = proj.anchors?.[tab as keyof typeof proj.anchors];
  return fromDoc ?? DEFAULT_ANCHOR;
}

/** Build a project doc with the anchor patch optimistically applied. */
export function applyOptimisticAnchorPatch(
  current: ProjectDoc,
  tab: CanvasKind,
  patch: Partial<AnchorPlacement>,
): ProjectDoc {
  const baseAnchor = resolveAnchorPlacement(current, tab);
  return {
    ...current,
    anchors: {
      ...(current.anchors ?? {}),
      [tab]: { ...baseAnchor, ...patch },
    },
  };
}
