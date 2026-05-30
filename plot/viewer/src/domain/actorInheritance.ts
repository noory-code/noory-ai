// Actor inheritance — computed effective fields (v0.30.4,
// D-2026-05-31-G).
//
// On the actors canvas a sub-actor inherits its parent actor's common
// fields. The relationship is an inheritance edge child→parent
// (source = subclass, target = superclass). A field resolves to:
//   own non-empty value  →  nearest ancestor's non-empty value  →  empty.
// Override = the child sets its own non-empty value. Computed at render
// — nothing is written, so each node's stored value stays the SSOT
// (Plot is a cognition tool, not a data engine: the inheritance is a
// derived view, not duplicated storage).
//
// The parent walk uses the same inheritance semantic + lexicographic
// tie-break as the fold (foldHierarchy) and server propagation, so all
// three agree on the actor tree.
//
// Pure module (no React) — Clean Architecture; the inspector consumes it.
import type { SketchEdge, SketchNode } from "../types";

export type FieldSource = "own" | "inherited";

export interface EffectiveField {
  /** Resolved value ("" when empty everywhere; for ``side`` the empty
   *  case is also ""). */
  value: string;
  source: FieldSource;
  /** Set when source === "inherited": the ancestor it came from. */
  fromId?: string;
  fromLabel?: string;
}

export interface EffectiveActorFields {
  motivation: EffectiveField;
  pain: EffectiveField;
  body: EffectiveField;
  side: EffectiveField;
}

/** Inheritable actor fields. ``side`` is operator|user|null; the rest
 *  are Markdown strings. */
const INHERITABLE_FIELDS = ["motivation", "pain", "body", "side"] as const;

function fieldValue(node: SketchNode, field: string): string {
  const raw = (node as unknown as Record<string, unknown>)[field];
  if (raw == null) return "";
  return typeof raw === "string" ? raw : String(raw);
}

/** child id → parent ids, from inheritance edges (child = source,
 *  parent = target). */
function buildInheritanceParents(edges: SketchEdge[]): Map<string, string[]> {
  const map = new Map<string, string[]>();
  for (const e of edges) {
    if (e.relation !== "inheritance" || !e.directed) continue;
    const arr = map.get(e.source) ?? [];
    arr.push(e.target);
    map.set(e.source, arr);
  }
  return map;
}

/** Ancestor ids from nearest to root, deterministic (lexicographically
 *  smallest parent at each step), cycle-guarded. */
function ancestorChain(startId: string, parents: Map<string, string[]>): string[] {
  const chain: string[] = [];
  const visited = new Set<string>([startId]);
  let cur = startId;
  for (;;) {
    const candidates = (parents.get(cur) ?? []).filter((p) => !visited.has(p));
    if (candidates.length === 0) break;
    const next = [...candidates].sort()[0];
    visited.add(next);
    chain.push(next);
    cur = next;
  }
  return chain;
}

export function effectiveActorFields(
  actorId: string,
  nodes: SketchNode[],
  edges: SketchEdge[],
): EffectiveActorFields {
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const self = byId.get(actorId);
  const chain = ancestorChain(actorId, buildInheritanceParents(edges));

  const resolve = (field: string): EffectiveField => {
    const own = self ? fieldValue(self, field) : "";
    if (own !== "") return { value: own, source: "own" };
    for (const aid of chain) {
      const ancestor = byId.get(aid);
      if (!ancestor) continue;
      const v = fieldValue(ancestor, field);
      if (v !== "") {
        return { value: v, source: "inherited", fromId: aid, fromLabel: ancestor.label };
      }
    }
    return { value: "", source: "own" };
  };

  return {
    motivation: resolve("motivation"),
    pain: resolve("pain"),
    body: resolve("body"),
    side: resolve("side"),
  } satisfies Record<(typeof INHERITABLE_FIELDS)[number], EffectiveField>;
}
