// Bridge between the pure ``radialLayout`` algorithm and the React /
// React-Flow side. Mirrors ``useAutoLayout`` 1:1 so the wrapper / button
// surface stays uniform between the two algorithms. Per SPEC.md
// §Auto-layout and DECISIONS.md D-2026-05-24-B.
//
// Hub selection:
//   - If ``projectAnchor`` is set (Services canvas), use the synthetic
//     anchor as the hub (PROJECT_ANCHOR_ID).
//   - Otherwise (ServiceDetail), pick the canvas's root-service node
//     (kind === "service" && is_root === true). It is hidden from the
//     viewport via ``hideRootServiceNode`` but still exists in
//     ``doc.nodes`` and provides a stable layout origin.

import { useCallback, type MutableRefObject } from "react";
import type { AnchorPlacement, CanvasDoc } from "../../types";
import { computeRadialLayout, type RadialLayoutHub } from "./radialLayout";
import { PROJECT_ANCHOR_ID } from "./constants";

export interface UseRadialLayoutInput {
  docRef: MutableRefObject<CanvasDoc>;
  onDocChange: (next: CanvasDoc) => void;
  projectAnchor: AnchorPlacement | null | undefined;
}

function pickHub(
  doc: CanvasDoc,
  anchor: AnchorPlacement | null | undefined,
): RadialLayoutHub | null {
  if (anchor) {
    return {
      id: PROJECT_ANCHOR_ID,
      x: anchor.x,
      y: anchor.y,
      width: anchor.width,
      height: anchor.height,
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

export function useRadialLayout({
  docRef,
  onDocChange,
  projectAnchor,
}: UseRadialLayoutInput) {
  return useCallback(() => {
    const doc = docRef.current;
    if (doc.nodes.length === 0) return;
    const hub = pickHub(doc, projectAnchor);
    if (!hub) return;
    const { positions } = computeRadialLayout({
      nodes: doc.nodes,
      edges: doc.edges,
      hub,
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
