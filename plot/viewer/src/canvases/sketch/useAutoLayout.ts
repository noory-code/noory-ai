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
import { type AutoLayoutAnchor } from "./autoLayout";
import { computeMindmapLayout } from "./mindmapLayout";
import {
  actorAnchoredLayout,
  setSubjectDirection,
  type AnchorDirection,
} from "../../flow/actorAnchoredLayout";
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

export interface AutoLayoutHandle {
  /** Default ⊞ auto-layout (anchor / actor-anchored / dagre fallback). */
  trigger: () => void;
  /** v0.28.3 (D-2026-05-30-F) — set the subject edge's direction
   *  (LR / TB) then re-run the actor-anchored layout, in one undoable
   *  change. No-op when the doc has no subject edge. */
  layoutInDirection: (direction: AnchorDirection) => void;
}

export function useAutoLayout({
  docRef,
  onDocChange,
  projectAnchor,
}: UseAutoLayoutInput): AutoLayoutHandle {
  const rf = useReactFlow();
  const trigger = useCallback(() => {
    const doc = docRef.current;
    if (doc.nodes.length === 0) return;
    // v0.27.16 (D-2026-05-28-J) — Actor-anchored layout takes
    // *priority* on docs that have a user-side actor_ref wired to
    // an entry step (the "subject edge"). The mindmap BFS path
    // below uses the hidden root_service as its anchor for
    // ServiceDetail; that anchor is disconnected, so BFS yields
    // only the root_service itself and dumps every other node —
    // including the user actor — into the isolated-nodes grid.
    // That sweeps the actor away from its placed position, which
    // is exactly the bug the user flagged on 2026-05-28
    // (*"이렇게 정렬이 되면 사람이 알아보겠어요???"*).
    const hasUserSubjectEdge = doc.nodes.some(
      (n) =>
        n.kind === "actor_ref" &&
        (n as unknown as { side?: string }).side === "user" &&
        doc.edges.some((e) => e.source === n.id),
    );
    if (hasUserSubjectEdge) {
      const next = actorAnchoredLayout(doc);
      const moved = next.nodes.some((nn, i) => {
        const prev = doc.nodes[i];
        return prev && (prev.x !== nn.x || prev.y !== nn.y);
      });
      if (moved) {
        onDocChange(next);
        fitNext(rf);
        return;
      }
    }
    const anchor = pickAnchor(doc, projectAnchor);
    if (anchor) {
      // v0.40.0 — MINDMAP radial tree. The v0.39.0 Reingold-Tilford tree
      // inferred T/R/B/L direction from current positions, which split one
      // parent's children across four sides and let cross-branch edges
      // crowd near the anchor. The mindmap layout gives each subtree a
      // disjoint angular wedge (sized by leaf-count) and nests children
      // inside the parent's wedge on the outward side, so every branch
      // reads as ONE group beside its parent with no node overlap and no
      // cross-branch edge crossing. User criteria 2026-06-01.
      const { positions } = computeMindmapLayout({
        nodes: doc.nodes,
        edges: doc.edges,
        hub: anchor,
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
    // v0.27.16 — Same actor-anchored layout but the doc has no
    // user-side actor_ref. Try an operator-side one (or any
    // actor_ref + subject edge) before falling back to dagre.
    const actorAnchored = actorAnchoredLayout(doc);
    const actorAnchoredMoved = actorAnchored.nodes.some((nn, i) => {
      const prev = doc.nodes[i];
      return prev && (prev.x !== nn.x || prev.y !== nn.y);
    });
    if (actorAnchoredMoved) {
      onDocChange(actorAnchored);
      fitNext(rf);
      return;
    }
    // v0.27.12 (D-2026-05-28-G) — Final fallback: no anchor, no
    // actor_ref subject edge. Run a handle-aware dagre layered
    // layout so ``⊞`` produces a visible re-arrangement.
    const fallback = handleAwareLayout(doc);
    const moved = fallback.nodes.some((nn, i) => {
      const prev = doc.nodes[i];
      return prev && (prev.x !== nn.x || prev.y !== nn.y);
    });
    if (!moved) return;
    onDocChange(fallback);
    fitNext(rf);
  }, [docRef, onDocChange, projectAnchor, rf]);

  const layoutInDirection = useCallback(
    (direction: AnchorDirection) => {
      const doc = docRef.current;
      if (doc.nodes.length === 0) return;
      // Set the subject-edge handle for the chosen direction, then lay
      // the step graph out along it — one undoable onDocChange carrying
      // both the handle flip and the new positions.
      const laid = actorAnchoredLayout(setSubjectDirection(doc, direction));
      if (laid === doc) return; // no subject edge → nothing to do
      onDocChange(laid);
      fitNext(rf);
    },
    [docRef, onDocChange, rf],
  );

  return { trigger, layoutInDirection };
}
