// Bridge between the pure ``autoLayout`` algorithm and the React /
// React-Flow side: reads the current ``CanvasDoc`` + ``AnchorPlacement``
// off refs / props, computes new positions via ``computeAutoLayout``,
// then dispatches a single ``onDocChange`` so the result lands in the
// regular history stack (one ``Cmd+Z`` reverses it). Per
// SPEC.md §Auto-layout and DECISIONS.md D-2026-05-10-E.
//
// Hub selection mirrors useRadialLayout (D-2026-05-26-A):
//   - If ``projectAnchor`` is set (Foundation / Actors / Services), use
//     the synthetic anchor as the layout root (PROJECT_ANCHOR_ID).
//   - Otherwise (ServiceDetail), pick the canvas's root-service node
//     (kind === "service" && is_root === true). It is hidden from the
//     viewport via ``hideRootServiceNode`` but still exists in
//     ``doc.nodes`` and provides a stable layout origin.

import { useCallback, type MutableRefObject } from "react";
import { useReactFlow } from "reactflow";
import type { AnchorPlacement, CanvasDoc } from "../../types";
import { computeAutoLayout, type AutoLayoutAnchor } from "./autoLayout";
import { handleAwareLayout } from "../../flow/handleAwareLayout";
import { PROJECT_ANCHOR_ID } from "./constants";

export interface UseAutoLayoutInput {
  docRef: MutableRefObject<CanvasDoc>;
  onDocChange: (next: CanvasDoc) => void;
  projectAnchor: AnchorPlacement | null | undefined;
}

function pickAnchor(
  doc: CanvasDoc,
  projectAnchor: AnchorPlacement | null | undefined,
): AutoLayoutAnchor | null {
  if (projectAnchor) {
    return {
      id: PROJECT_ANCHOR_ID,
      x: projectAnchor.x,
      y: projectAnchor.y,
      width: projectAnchor.width,
      height: projectAnchor.height,
    };
  }
  const root = doc.nodes.find(
    (n) => n.kind === "service" && n.is_root === true,
  );
  if (root) {
    return {
      id: root.id,
      x: root.x,
      y: root.y,
      width: root.width,
      height: root.height,
    };
  }
  return null;
}

function fitNext(rf: ReturnType<typeof useReactFlow>): void {
  // v0.27.6 (D-2026-05-26-J) — after layout mutates positions, the
  // user's viewport stays put — typically meaning the newly laid-out
  // graph lands off-screen ("정렬 누르니까 다 사라짐"). Frame the
  // new layout in the next tick so the user always sees the result
  // they triggered. ``setTimeout(0)`` lets the onDocChange render
  // commit + RF measure pass complete before fitView runs.
  setTimeout(() => rf.fitView({ padding: 0.2, duration: 250 }), 0);
}

export function useAutoLayout({ docRef, onDocChange, projectAnchor }: UseAutoLayoutInput) {
  const rf = useReactFlow();
  return useCallback(() => {
    const doc = docRef.current;
    if (doc.nodes.length === 0) return;
    const anchor = pickAnchor(doc, projectAnchor);
    if (anchor) {
      const { positions } = computeAutoLayout({
        nodes: doc.nodes,
        edges: doc.edges,
        anchor,
      });
      if (positions.size > 0) {
        const nextNodes = doc.nodes.map((n) => {
          const p = positions.get(n.id);
          if (!p) return n;
          return { ...n, x: p.x, y: p.y };
        });
        onDocChange({ ...doc, nodes: nextNodes });
        fitNext(rf);
        return;
      }
    }
    // v0.27.12 (D-2026-05-28-G) — Fallback: mindmap BFS yielded no
    // positions (or there is no anchor at all). Typical case:
    // ServiceDetail's hidden root-service per D-2026-05-28-B is the
    // anchor but is intentionally disconnected from every edge, so
    // BFS can't reach any node. Run a handle-aware dagre layered
    // layout so ``⊞`` produces a visible re-arrangement that follows
    // edge handles instead of being a no-op.
    const fallback = handleAwareLayout(doc);
    const moved = fallback.nodes.some((nn, i) => {
      const prev = doc.nodes[i];
      return prev && (prev.x !== nn.x || prev.y !== nn.y);
    });
    if (!moved) return;
    onDocChange(fallback);
    fitNext(rf);
  }, [docRef, onDocChange, projectAnchor, rf]);
}
