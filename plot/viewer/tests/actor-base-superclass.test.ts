/**
 * Abstract root superclass detection — v0.31.0 (D-2026-05-31-H).
 *
 * OOP framing of the actors canvas: the ROOT of an inheritance tree is
 * an *abstract* superclass. It is the actor that has no actor parent
 * (its only inheritance parent is the project anchor) AND has at least
 * one actor child. Such an actor carries no concrete role/motive/pain —
 * those belong to the concrete subclasses, so the Inspector hides them.
 *
 * "Has children" is NOT the test: an intermediate concrete actor (Bana
 * with Hero/Fans below it) has children yet is NOT abstract, because it
 * has an actor parent.
 */
import { describe, expect, it } from "vitest";
import { isActorBaseSuperclass } from "../src/domain/actorInheritance";
import type { SketchEdge, SketchNode } from "../src/types";

const ANCHOR = "__project_anchor__";

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

/** The anchor is a `project` node, never an actor. */
function anchor(): SketchNode {
  return { ...actor(ANCHOR), kind: "project", label: "Banas" } as unknown as SketchNode;
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

// anchor ← User ← { Operator, Bana ← { Hero, Fans } }
const NODES: SketchNode[] = [
  anchor(),
  actor("user", { label: "User", side: "user" }),
  actor("op", { label: "Operator", side: "operator" }),
  actor("bana", { label: "Bana", side: "user" }),
  actor("hero", { label: "Hero" }),
  actor("fans", { label: "Fans" }),
];
const EDGES: SketchEdge[] = [
  inheritEdge("user", ANCHOR),
  inheritEdge("op", "user"),
  inheritEdge("bana", "user"),
  inheritEdge("hero", "bana"),
  inheritEdge("fans", "bana"),
];

describe("isActorBaseSuperclass (D-2026-05-31-H)", () => {
  it("the tree root (parent = anchor, has actor children) IS the abstract base", () => {
    expect(isActorBaseSuperclass("user", NODES, EDGES)).toBe(true);
  });

  it("an intermediate actor with children but an actor parent is NOT abstract", () => {
    // Bana parents Hero/Fans yet inherits from User → concrete, keeps fields.
    expect(isActorBaseSuperclass("bana", NODES, EDGES)).toBe(false);
  });

  it("a leaf actor is NOT abstract", () => {
    expect(isActorBaseSuperclass("op", NODES, EDGES)).toBe(false);
    expect(isActorBaseSuperclass("hero", NODES, EDGES)).toBe(false);
  });

  it("a lone root with NO actor children is NOT abstract (it is a concrete actor)", () => {
    const nodes = [anchor(), actor("solo", { side: "user" })];
    const edges = [inheritEdge("solo", ANCHOR)];
    expect(isActorBaseSuperclass("solo", nodes, edges)).toBe(false);
  });

  it("a root with no parent edge at all but with children IS abstract", () => {
    const nodes = [actor("root"), actor("kid")];
    const edges = [inheritEdge("kid", "root")];
    expect(isActorBaseSuperclass("root", nodes, edges)).toBe(true);
  });
});
