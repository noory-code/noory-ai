/**
 * Actor inheritance — computed effective fields — v0.30.4
 * (D-2026-05-31-G).
 *
 * On the actors canvas a sub-actor inherits its parent actor's common
 * fields (motivation / pain / side / body). The relationship is an
 * inheritance edge child→parent (source=subclass, target=superclass).
 * A field resolves to: own non-empty value → nearest ancestor's
 * non-empty value → empty. Override = the child sets its own value.
 * Computed at render; nothing is written (SSOT stays on each node).
 */
import { describe, expect, it } from "vitest";
import { effectiveActorFields } from "../src/domain/actorInheritance";
import type { CanvasDoc, SketchEdge, SketchNode } from "../src/types";

function actor(id: string, over: Partial<Record<string, unknown>> = {}): SketchNode {
  return {
    id,
    label: id,
    x: 0,
    y: 0,
    width: 80,
    height: 36,
    color: "#fff",
    shape: "rounded",
    icon: null,
    collapsed: false,
    is_root: false,
    details_path: null,
    owner: null,
    version: "v1.0",
    kind: "actor",
    motivation: "",
    pain: "",
    side: null,
    body: "",
    ...over,
  } as unknown as SketchNode;
}

function inheritEdge(child: string, parent: string): SketchEdge {
  return {
    id: `e_${child}_${parent}`,
    source: child,
    target: parent,
    sourceHandle: null,
    targetHandle: null,
    label: "",
    style: "solid",
    directed: true,
    relation: "inheritance",
    action_verb: null,
    value_form: [],
  } as SketchEdge;
}

// anchor(project) ← User(base) ← { Op, Bana }
const NODES: SketchNode[] = [
  actor("user", { label: "User", motivation: "be served well", pain: "friction", side: "user" }),
  actor("op", { label: "Operator", side: "operator" }), // inherits motivation/pain from User
  actor("bana", { label: "Bana", motivation: "create + share" }), // overrides motivation
];
const EDGES: SketchEdge[] = [inheritEdge("op", "user"), inheritEdge("bana", "user")];

describe("effectiveActorFields (D-2026-05-31-G)", () => {
  it("a base actor's fields are all own", () => {
    const eff = effectiveActorFields("user", NODES, EDGES);
    expect(eff.motivation).toEqual({ value: "be served well", source: "own" });
    expect(eff.pain.source).toBe("own");
  });

  it("a sub-actor inherits empty fields from its parent", () => {
    const eff = effectiveActorFields("op", NODES, EDGES);
    expect(eff.motivation).toEqual({
      value: "be served well",
      source: "inherited",
      fromId: "user",
      fromLabel: "User",
    });
    expect(eff.pain.value).toBe("friction");
    expect(eff.pain.source).toBe("inherited");
    // own side overrides
    expect(eff.side).toEqual({ value: "operator", source: "own" });
  });

  it("a sub-actor's own non-empty field overrides the inherited one", () => {
    const eff = effectiveActorFields("bana", NODES, EDGES);
    expect(eff.motivation).toEqual({ value: "create + share", source: "own" });
    // pain is empty on Bana → inherited from User
    expect(eff.pain).toEqual({
      value: "friction",
      source: "inherited",
      fromId: "user",
      fromLabel: "User",
    });
  });

  it("empty everywhere → empty own value", () => {
    const lone = effectiveActorFields("x", [actor("x")], []);
    expect(lone.motivation).toEqual({ value: "", source: "own" });
  });

  it("survives an inheritance cycle without infinite loop", () => {
    const cyc = [actor("a"), actor("b", { motivation: "B" })];
    const edges = [inheritEdge("a", "b"), inheritEdge("b", "a")];
    const eff = effectiveActorFields("a", cyc, edges);
    expect(eff.motivation.value).toBe("B");
  });

  it("multiple parents → lexicographically smallest id wins (deterministic)", () => {
    const nodes = [
      actor("child"),
      actor("p2", { motivation: "from p2" }),
      actor("p1", { motivation: "from p1" }),
    ];
    const edges = [inheritEdge("child", "p2"), inheritEdge("child", "p1")];
    const eff = effectiveActorFields("child", nodes, edges);
    expect(eff.motivation).toEqual({
      value: "from p1",
      source: "inherited",
      fromId: "p1",
      fromLabel: "p1",
    });
  });
});

// type-only: CanvasDoc import keeps the wire shape in scope for editors
export type _Doc = CanvasDoc;
