// D-2026-05-28-J (auto-layout responsibility) + D-2026-05-28-G follow-up.
//
// Actor-anchored layout: when a ServiceDetail canvas has a user-side
// ``actor_ref`` wired to an entry step (the "subject edge"), the layout
// algorithm must:
//
//   1. preserve the actor's existing position (it's the user-placed
//      anchor),
//   2. infer the spatial direction (LR / RL / TB / BT) from the
//      subject edge's ``sourceHandle``,
//   3. lay the step graph out from the entry in that direction,
//   4. translate the whole step graph so the entry lands one rank
//      away from the actor (= actor stays, steps follow).
//
// v0.27.12's ``handleAwareLayout`` (dagre LR fallback) swept the actor
// along with every other node — user 2026-05-28: *"이렇게 정렬이 되면
// 사람이 알아보겠어요???"*. This module is the replacement.
import { describe, it, expect } from "vitest";
import { actorAnchoredLayout } from "../src/flow/actorAnchoredLayout";
import type { CanvasDoc, SketchNode, SketchEdge } from "../src/types";

function actor(id: string, x: number, y: number): SketchNode {
  return {
    id, label: `actor:${id}`,
    x, y, width: 130, height: 130,
    color: "#fce7f3", shape: "circle", icon: "user",
    collapsed: false, is_root: false, details_path: null,
    owner: null, version: "v1.0", _publish_baseline: null,
    kind: "actor_ref", ref_actor_id: "master", side: "user",
    gives: "", receives: "",
  } as unknown as SketchNode;
}

function step(id: string, x = 0, y = 0): SketchNode {
  return {
    id, label: `step:${id}`,
    x, y, width: 180, height: 70,
    color: "#fef3c7", shape: "rounded", icon: null,
    collapsed: false, is_root: false, details_path: null,
    owner: null, version: "v1.0", _publish_baseline: null,
    kind: "step", order: null, outcome: "", body: "",
  } as unknown as SketchNode;
}

function edge(
  source: string,
  target: string,
  sourceHandle: string = "r",
  targetHandle: string = "l",
  label: string = "",
  relation: SketchEdge["relation"] = "flow",
): SketchEdge {
  return {
    id: `e_${source}_${target}`,
    source, target, sourceHandle, targetHandle,
    label, style: "solid", directed: true,
    relation,
    action_verb: null, value_form: [],
  };
}

function valueRef(id: string, x: number, y: number): SketchNode {
  return {
    id, label: `value:${id}`,
    x, y, width: 120, height: 60,
    color: "#ede9fe", shape: "circle", icon: "star",
    collapsed: false, is_root: false, details_path: null,
    owner: null, version: "v1.0", _publish_baseline: null,
    kind: "value_ref", ref_value_id: "core",
  } as unknown as SketchNode;
}

function doc(nodes: SketchNode[], edges: SketchEdge[]): CanvasDoc {
  return {
    canvas_id: "test", canvas_kind: "service_detail",
    service_ref: null, nodes, edges,
  } as CanvasDoc;
}

describe("actorAnchoredLayout (D-2026-05-28-J)", () => {
  it("preserves the user actor's position and lays steps to the right (LR)", () => {
    const d = doc(
      [actor("U", -800, 0), step("entry", 999, 999), step("s2", 999, 999)],
      [edge("U", "entry", "r", "l"), edge("entry", "s2", "r", "l")],
    );
    const out = actorAnchoredLayout(d);
    const U = out.nodes.find((n) => n.id === "U")!;
    const entry = out.nodes.find((n) => n.id === "entry")!;
    const s2 = out.nodes.find((n) => n.id === "s2")!;
    // Actor anchor preserved.
    expect(U.x, "actor x preserved").toBe(-800);
    expect(U.y, "actor y preserved").toBe(0);
    // Steps land to the right of the actor.
    expect(entry.x, "entry should sit right of the actor").toBeGreaterThan(U.x);
    expect(s2.x, "s2 should sit right of entry").toBeGreaterThan(entry.x);
  });

  it("places entry one ~rank to the right of the actor when handle is 'r'", () => {
    const d = doc(
      [actor("U", 0, 0), step("entry", 999, 999)],
      [edge("U", "entry", "r", "l")],
    );
    const out = actorAnchoredLayout(d);
    const U = out.nodes.find((n) => n.id === "U")!;
    const entry = out.nodes.find((n) => n.id === "entry")!;
    // Actor centre and entry centre should be roughly on the same y baseline.
    const Ucy = U.y + U.height / 2;
    const Ecy = entry.y + entry.height / 2;
    expect(Math.abs(Ecy - Ucy), "entry and actor on same horizontal line").toBeLessThan(80);
    // Entry should be a reasonable distance to the right (≥ 100 px).
    const Ucx = U.x + U.width / 2;
    const Ecx = entry.x + entry.width / 2;
    expect(Ecx - Ucx, "entry right of actor by ≥ 100").toBeGreaterThanOrEqual(100);
  });

  it("uses TB direction when subject edge sourceHandle is 'b'", () => {
    const d = doc(
      [actor("U", 0, -300), step("entry", 999, 999), step("s2", 999, 999)],
      [edge("U", "entry", "b", "t"), edge("entry", "s2", "b", "t")],
    );
    const out = actorAnchoredLayout(d);
    const U = out.nodes.find((n) => n.id === "U")!;
    const entry = out.nodes.find((n) => n.id === "entry")!;
    expect(U.y, "actor y preserved").toBe(-300);
    expect(entry.y, "entry should sit below the actor").toBeGreaterThan(U.y);
  });

  it("handles a branch + join graph: result lands after every branch", () => {
    const d = doc(
      [
        actor("U", -500, 0),
        step("entry", 0, 0), step("decision", 0, 0),
        step("a1", 0, 0), step("b1", 0, 0), step("c1", 0, 0),
        step("result", 0, 0),
      ],
      [
        edge("U", "entry"),
        edge("entry", "decision"),
        edge("decision", "a1", "r", "l", "branch"),
        edge("decision", "b1", "r", "l", "branch"),
        edge("decision", "c1", "r", "l", "branch"),
        edge("a1", "result", "r", "l", "join"),
        edge("b1", "result", "r", "l", "join"),
        edge("c1", "result", "r", "l", "join"),
      ],
    );
    const out = actorAnchoredLayout(d);
    const U = out.nodes.find((n) => n.id === "U")!;
    const decision = out.nodes.find((n) => n.id === "decision")!;
    const a1 = out.nodes.find((n) => n.id === "a1")!;
    const b1 = out.nodes.find((n) => n.id === "b1")!;
    const c1 = out.nodes.find((n) => n.id === "c1")!;
    const result = out.nodes.find((n) => n.id === "result")!;
    // Actor anchor preserved.
    expect(U.x).toBe(-500);
    // Decision right of actor.
    expect(decision.x).toBeGreaterThan(U.x);
    // Branches share the same column to the right of the decision.
    expect(a1.x).toBeGreaterThan(decision.x);
    expect(b1.x).toBeGreaterThan(decision.x);
    expect(c1.x).toBeGreaterThan(decision.x);
    // Result lands to the right of every branch.
    expect(result.x, "result right of a1").toBeGreaterThan(a1.x);
    expect(result.x, "result right of b1").toBeGreaterThan(b1.x);
    expect(result.x, "result right of c1").toBeGreaterThan(c1.x);
  });

  it("leaves orphan nodes (no edges) untouched", () => {
    const d = doc(
      [
        actor("U", -500, 0),
        step("entry", 0, 0),
        step("orphan", 1234, 5678),
      ],
      [edge("U", "entry")],
    );
    const out = actorAnchoredLayout(d);
    const orphan = out.nodes.find((n) => n.id === "orphan")!;
    expect(orphan.x, "orphan x preserved").toBe(1234);
    expect(orphan.y, "orphan y preserved").toBe(5678);
  });

  it("returns the doc unchanged when there is no user-side actor", () => {
    const d = doc([step("s1", 100, 200)], []);
    const out = actorAnchoredLayout(d);
    expect(out.nodes[0].x).toBe(100);
    expect(out.nodes[0].y).toBe(200);
  });

  it("anchors an injection node (foundation ref) by its targetHandle, not in the step rank (D-2026-05-30-G)", () => {
    const d = doc(
      [actor("U", -500, 0), step("entry", 0, 0), step("s2", 0, 0), valueRef("hum", 9999, 9999)],
      [
        edge("U", "entry", "r", "l"),
        edge("entry", "s2", "r", "l"),
        edge("hum", "entry", "b", "t", "", "injection"), // injection: 유머 bottom → entry top
      ],
    );
    const out = actorAnchoredLayout(d);
    const entry = out.nodes.find((n) => n.id === "entry")!;
    const s2 = out.nodes.find((n) => n.id === "s2")!;
    const hum = out.nodes.find((n) => n.id === "hum")!;
    const entryCx = entry.x + entry.width / 2;
    const humCx = hum.x + hum.width / 2;
    // Anchored ABOVE entry (targetHandle "t"): centred on entry's column, above it.
    expect(Math.abs(humCx - entryCx), "injection centred on target column").toBeLessThan(60);
    expect(hum.y + hum.height, "injection sits above the target").toBeLessThanOrEqual(entry.y + 5);
    // The step sequence is unaffected — s2 still ranks to the right of entry.
    expect(s2.x, "entry → s2 sequence intact").toBeGreaterThan(entry.x);
  });
});
