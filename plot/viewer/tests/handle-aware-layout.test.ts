// D-2026-05-28-G — handle-aware layered layout for ServiceDetail.
//
// User report 2026-05-28: *"정렬은 연결관계에 따라서 오른쪽에 붙어있으면
// 오른쪽으로 정렬해야하는데 오른쪽에 붙어있는걸 왼쪽에 정렬하고 이러니까
// 문제죠"*. The pre-existing ``useAutoLayout`` mindmap BFS algorithm
// requires an *anchor with at least one edge* — on the ServiceDetail
// canvas the anchor is the hidden root-service node (D-2026-05-28-B)
// which is intentionally disconnected, so BFS yields zero positions and
// ``⊞`` is a no-op. This file pins the contract for the new
// ``handleAwareLayout`` function that handles the disconnected-anchor
// case via a dagre LR pass, swapping source/target in dagre's input
// whenever the edge's ``sourceHandle`` points L or T so the layered
// result matches the user's "right handle = on the right" mental model.
import { describe, it, expect } from "vitest";
import { handleAwareLayout } from "../src/flow/handleAwareLayout";
import type { CanvasDoc, SketchNode, SketchEdge } from "../src/types";

function n(id: string, x = 0, y = 0): SketchNode {
  return {
    id,
    label: id,
    x,
    y,
    width: 100,
    height: 60,
    color: "#fff",
    shape: "rectangle",
    icon: null,
    collapsed: false,
    is_root: false,
    details_path: null,
    owner: null,
    version: "v1.0",
    _publish_baseline: null,
    kind: "step",
    order: null,
    outcome: "",
    body: "",
  } as SketchNode;
}

function e(
  source: string,
  target: string,
  sourceHandle: string | null = "r",
  targetHandle: string | null = "l",
): SketchEdge {
  return {
    id: `e_${source}_${target}`,
    source,
    target,
    sourceHandle,
    targetHandle,
    label: "",
    style: "solid",
    directed: true,
    action_verb: null,
    value_form: [],
  };
}

function doc(nodes: SketchNode[], edges: SketchEdge[]): CanvasDoc {
  return {
    canvas_id: "test",
    canvas_kind: "service_detail",
    service_ref: null,
    nodes,
    edges,
  } as CanvasDoc;
}

describe("handleAwareLayout (D-2026-05-28-G)", () => {
  it("places target to the right of source when sourceHandle='r'", () => {
    const d = doc([n("A"), n("B")], [e("A", "B", "r", "l")]);
    const next = handleAwareLayout(d);
    const A = next.nodes.find((x) => x.id === "A")!;
    const B = next.nodes.find((x) => x.id === "B")!;
    expect(B.x, "B (sourceHandle r) must be to the right of A").toBeGreaterThan(A.x);
  });

  it("places target to the LEFT of source when sourceHandle='l' (swap)", () => {
    const d = doc([n("A"), n("B")], [e("A", "B", "l", "r")]);
    const next = handleAwareLayout(d);
    const A = next.nodes.find((x) => x.id === "A")!;
    const B = next.nodes.find((x) => x.id === "B")!;
    expect(B.x, "B (sourceHandle l) must be to the left of A").toBeLessThan(A.x);
  });

  it("packs an LR chain into three distinct columns", () => {
    const d = doc(
      [n("A"), n("B"), n("C")],
      [e("A", "B", "r", "l"), e("B", "C", "r", "l")],
    );
    const next = handleAwareLayout(d);
    const A = next.nodes.find((x) => x.id === "A")!;
    const B = next.nodes.find((x) => x.id === "B")!;
    const C = next.nodes.find((x) => x.id === "C")!;
    expect(A.x).toBeLessThan(B.x);
    expect(B.x).toBeLessThan(C.x);
  });

  it("preserves the original position of nodes that have no edges (orphans)", () => {
    const d = doc(
      [n("A", 0, 0), n("B", 200, 0), n("C", -999, -999)],
      [e("A", "B", "r", "l")],
    );
    const next = handleAwareLayout(d);
    const C = next.nodes.find((x) => x.id === "C")!;
    expect(C.x).toBe(-999);
    expect(C.y).toBe(-999);
  });

  it("never returns an empty positions Map for a connected pair", () => {
    const d = doc([n("A"), n("B")], [e("A", "B", "r", "l")]);
    const next = handleAwareLayout(d);
    const A = next.nodes.find((x) => x.id === "A")!;
    const B = next.nodes.find((x) => x.id === "B")!;
    // After layout at least one of the two should have moved off (0, 0).
    expect(A.x !== 0 || A.y !== 0 || B.x !== 0 || B.y !== 0).toBe(true);
  });

  it("works on the user's ServiceDetail reconstruction shape (8-node sample)", () => {
    // Hero → 모임 → Fan, Hero → 콘텐츠 → Fan, plus 가치 + 핵심가치 fan-out
    const nodes = [
      n("hero"), n("fan"),
      n("meet"), n("publish"),
      n("v_taste"), n("v_expertise"),
      n("cv_empathy"), n("mission"),
    ];
    const edges = [
      e("hero", "meet"), e("meet", "fan"),
      e("hero", "publish"), e("publish", "fan"),
      e("meet", "v_taste"),
      e("publish", "v_expertise"),
      e("meet", "cv_empathy"),
      e("cv_empathy", "mission"),
    ];
    const next = handleAwareLayout(doc(nodes, edges));
    const hero = next.nodes.find((x) => x.id === "hero")!;
    const meet = next.nodes.find((x) => x.id === "meet")!;
    const fan = next.nodes.find((x) => x.id === "fan")!;
    const cv = next.nodes.find((x) => x.id === "cv_empathy")!;
    const mission = next.nodes.find((x) => x.id === "mission")!;
    // LR ranking: hero < meet < fan
    expect(hero.x).toBeLessThan(meet.x);
    expect(meet.x).toBeLessThan(fan.x);
    // cv → mission also LR
    expect(cv.x).toBeLessThan(mission.x);
  });
});
