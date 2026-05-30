// D-2026-05-28-J (auto-layout responsibility) + D-2026-05-28-G follow-up.
//
// Actor-anchored layered layout for ServiceDetail canvases:
//
//   - The user-side actor_ref is the anchor. Its position is preserved.
//   - The "subject edge" (actor → entry step) tells us which direction
//     the user wants: ``sourceHandle = "r"`` → LR, ``"l"`` → RL,
//     ``"b"`` → TB, ``"t"`` → BT.
//   - The step graph is laid out by dagre using that rankdir.
//   - Every step is then translated so the entry sits one rank away
//     from the actor in the chosen direction. The actor itself is
//     never moved.
//   - Nodes with no incident step edges (orphan refs, the hidden
//     root-service, the operator-side actor_ref placeholder if any)
//     keep their existing positions.
//
// Replaces ``handleAwareLayout`` for ServiceDetail's typical user-
// authored interaction graphs. ``handleAwareLayout`` (dagre LR over
// every connected node) swept the anchor along with everything else;
// the user flagged that as unreadable on 2026-05-28
// (*"이렇게 정렬이 되면 사람이 알아보겠어요???"*).

import dagre from "dagre";
import type { CanvasDoc, SketchNode } from "../types";

// v0.28.3 (D-2026-05-30-G) — gap (centre-to-centre) from an injection
// node to its target, in the targetHandle direction.
const INJECTION_GAP = 160;

export type AnchorDirection = "LR" | "RL" | "TB" | "BT";

interface Anchor {
  actor: SketchNode;
  entry: SketchNode;
  direction: AnchorDirection;
}

function directionFromHandle(handle: string | null | undefined): AnchorDirection {
  if (!handle) return "LR";
  const h = handle.toLowerCase();
  if (h.startsWith("r")) return "LR";
  if (h.startsWith("l")) return "RL";
  if (h.startsWith("b")) return "TB";
  if (h.startsWith("t")) return "BT";
  return "LR";
}

/** The anchor actor_ref = the user-side one, else any actor_ref.
 *  Single source of truth for "whose first outgoing edge is the
 *  subject edge", shared by ``detectAnchor`` (layout) and
 *  ``setSubjectDirection`` (the direction-switch buttons). */
function detectAnchorActor(doc: CanvasDoc): SketchNode | null {
  const userActor = doc.nodes.find(
    (n) =>
      n.kind === "actor_ref" &&
      (n as unknown as { side?: string }).side === "user",
  );
  return userActor ?? doc.nodes.find((n) => n.kind === "actor_ref") ?? null;
}

/** v0.28.3 (D-2026-05-30-F) — id of the subject edge (actor → entry),
 *  or null. The direction-switch buttons flip this edge's handles. */
export function detectSubjectEdgeId(doc: CanvasDoc): string | null {
  const actor = detectAnchorActor(doc);
  if (!actor) return null;
  return doc.edges.find((e) => e.source === actor.id)?.id ?? null;
}

function detectAnchor(doc: CanvasDoc): Anchor | null {
  const anyActor = detectAnchorActor(doc);
  if (!anyActor) return null;
  // First edge whose source is the anchor actor is the "subject edge".
  const subjectEdge = doc.edges.find((e) => e.source === anyActor.id);
  if (!subjectEdge) return null;
  const entry = doc.nodes.find((n) => n.id === subjectEdge.target);
  if (!entry) return null;
  return {
    actor: anyActor,
    entry,
    direction: directionFromHandle(subjectEdge.sourceHandle),
  };
}

// v0.28.3 (D-2026-05-30-F) — handle pair per direction (source, target).
const DIRECTION_HANDLES: Record<AnchorDirection, [string, string]> = {
  LR: ["r", "l"],
  RL: ["l", "r"],
  TB: ["b", "t"],
  BT: ["t", "b"],
};

/** Set the subject edge's handles so the actor-anchored layout lays
 *  the step graph out in ``direction``. Returns the doc unchanged when
 *  there is no subject edge. Direction stays the SSOT in the handle —
 *  a later ``⊞`` re-uses it. */
export function setSubjectDirection(doc: CanvasDoc, direction: AnchorDirection): CanvasDoc {
  const eid = detectSubjectEdgeId(doc);
  if (!eid) return doc;
  const [sourceHandle, targetHandle] = DIRECTION_HANDLES[direction];
  return {
    ...doc,
    edges: doc.edges.map((e) =>
      e.id === eid ? { ...e, sourceHandle, targetHandle } : e,
    ),
  };
}

/** Per-direction separation between the actor and the entry step.
 *  ``actorEntryGap`` is centre-to-centre, in pixels. */
const ACTOR_ENTRY_GAP = 220;

export function actorAnchoredLayout(doc: CanvasDoc): CanvasDoc {
  const anchor = detectAnchor(doc);
  if (!anchor) return doc;
  const { actor, entry, direction } = anchor;

  const g = new dagre.graphlib.Graph();
  g.setGraph({
    rankdir: direction,
    nodesep: 60,
    ranksep: 120,
    marginx: 20,
    marginy: 20,
  });
  g.setDefaultEdgeLabel(() => ({}));

  // v0.28.3 (D-2026-05-30-G) — layout anchor priority: actor (1) > step
  // / decision (2) > injection overlay (3). Injection edges are a
  // 2nd-layer essence overlay, NOT part of the user-interaction
  // sequence — so they are excluded from the dagre step rank and their
  // source nodes are anchored beside their target by the targetHandle
  // (below). v0.30.1 (D-2026-05-31-D) — read from the stored
  // ``relation`` SSOT (was a source-kind lookup in v0.28.3).
  const isInjectionEdge = (e: CanvasDoc["edges"][number]): boolean =>
    e.relation === "injection";
  const injectionEdges = doc.edges.filter(isInjectionEdge);

  // Step-graph = every node connected by a sequence edge: not from the
  // anchor actor (those are subject edges) and not an injection edge.
  // The anchor itself is never sent to dagre — its position is preserved.
  const stepEdges = doc.edges.filter((e) => e.source !== actor.id && !isInjectionEdge(e));
  const stepConnectedIds = new Set<string>();
  for (const e of stepEdges) {
    stepConnectedIds.add(e.source);
    stepConnectedIds.add(e.target);
  }

  // Always include the entry — even if it has no outgoing step edges
  // (a one-step service is still a service). Otherwise dagre returns
  // an empty layout and we'd have nothing to translate.
  g.setNode(entry.id, { width: entry.width, height: entry.height });
  for (const n of doc.nodes) {
    if (n.id === actor.id) continue;
    if (n.id === entry.id) continue;
    if (!stepConnectedIds.has(n.id)) continue;
    g.setNode(n.id, { width: n.width, height: n.height });
  }
  for (const e of stepEdges) {
    if (!g.hasNode(e.source) || !g.hasNode(e.target)) continue;
    g.setEdge(e.source, e.target);
  }
  dagre.layout(g);

  const entryDagre = g.node(entry.id);
  if (!entryDagre) return doc;

  // Translate everything so the entry sits at actor + gap in the
  // chosen direction.
  const actorCenterX = actor.x + actor.width / 2;
  const actorCenterY = actor.y + actor.height / 2;
  let targetEntryCenterX = actorCenterX;
  let targetEntryCenterY = actorCenterY;
  if (direction === "LR") targetEntryCenterX = actorCenterX + ACTOR_ENTRY_GAP;
  else if (direction === "RL") targetEntryCenterX = actorCenterX - ACTOR_ENTRY_GAP;
  else if (direction === "TB") targetEntryCenterY = actorCenterY + ACTOR_ENTRY_GAP;
  else if (direction === "BT") targetEntryCenterY = actorCenterY - ACTOR_ENTRY_GAP;

  const dx = targetEntryCenterX - entryDagre.x;
  const dy = targetEntryCenterY - entryDagre.y;

  // Tier 1-2: final top-left positions for the dagre-placed step nodes.
  const placedFinal = new Map<string, { x: number; y: number }>();
  for (const n of doc.nodes) {
    if (n.id === actor.id) continue;
    const placed = g.node(n.id);
    if (!placed) continue;
    placedFinal.set(n.id, { x: placed.x + dx - n.width / 2, y: placed.y + dy - n.height / 2 });
  }

  // Final CENTRE of a target node (actor anchor / dagre-placed step /
  // untouched orphan), used to anchor injection nodes beside it.
  const targetCenter = (id: string): { cx: number; cy: number } | null => {
    if (id === actor.id) return { cx: actorCenterX, cy: actorCenterY };
    const p = placedFinal.get(id);
    const node = doc.nodes.find((n) => n.id === id);
    if (!node) return null;
    if (p) return { cx: p.x + node.width / 2, cy: p.y + node.height / 2 };
    return { cx: node.x + node.width / 2, cy: node.y + node.height / 2 };
  };

  // Tier 3: anchor each injection-source node beside its target on the
  // side the edge's targetHandle dictates (t → above, b → below,
  // l → left, r → right). First injection edge per source wins.
  for (const e of injectionEdges) {
    const src = doc.nodes.find((n) => n.id === e.source);
    if (!src || placedFinal.has(src.id)) continue;
    const tc = targetCenter(e.target);
    if (!tc) continue;
    let cx = tc.cx;
    let cy = tc.cy;
    const th = (e.targetHandle ?? "").toLowerCase();
    if (th.startsWith("t")) cy = tc.cy - INJECTION_GAP;
    else if (th.startsWith("b")) cy = tc.cy + INJECTION_GAP;
    else if (th.startsWith("l")) cx = tc.cx - INJECTION_GAP;
    else if (th.startsWith("r")) cx = tc.cx + INJECTION_GAP;
    else cy = tc.cy - INJECTION_GAP; // default: above
    placedFinal.set(src.id, { x: cx - src.width / 2, y: cy - src.height / 2 });
  }

  return {
    ...doc,
    nodes: doc.nodes.map((n) => {
      const p = placedFinal.get(n.id);
      return p ? { ...n, x: p.x, y: p.y } : n;
    }),
  };
}
