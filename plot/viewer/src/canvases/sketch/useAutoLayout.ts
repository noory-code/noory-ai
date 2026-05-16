// Bridge between the pure ``autoLayout`` algorithm and the React /
// React-Flow side: reads the current ``CanvasDoc`` + ``AnchorPlacement``
// off refs / props, computes new positions via ``computeAutoLayout``,
// then dispatches a single ``onDocChange`` so the result lands in the
// regular history stack (one ``Cmd+Z`` reverses it). Per
// SPEC.md §Auto-layout and DECISIONS.md D-2026-05-10-E.

import { useCallback, type MutableRefObject } from "react";
import type { AnchorPlacement, CanvasDoc } from "../../types";
import { computeAutoLayout } from "./autoLayout";
import { PROJECT_ANCHOR_ID } from "./constants";

export interface UseAutoLayoutInput {
  docRef: MutableRefObject<CanvasDoc>;
  onDocChange: (next: CanvasDoc) => void;
  projectAnchor: AnchorPlacement | null | undefined;
}

export function useAutoLayout({ docRef, onDocChange, projectAnchor }: UseAutoLayoutInput) {
  return useCallback(() => {
    if (!projectAnchor) return;
    const doc = docRef.current;
    if (doc.nodes.length === 0) return;
    const { positions } = computeAutoLayout({
      nodes: doc.nodes,
      edges: doc.edges,
      anchor: {
        id: PROJECT_ANCHOR_ID,
        x: projectAnchor.x,
        y: projectAnchor.y,
        width: projectAnchor.width,
        height: projectAnchor.height,
      },
    });
    if (positions.size === 0) return;
    const nextNodes = doc.nodes.map((n) => {
      const p = positions.get(n.id);
      if (!p) return n;
      return { ...n, x: p.x, y: p.y };
    });
    onDocChange({ ...doc, nodes: nextNodes });
  }, [docRef, onDocChange, projectAnchor]);
}
