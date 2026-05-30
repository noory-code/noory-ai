/**
 * v0.28.3 (D-2026-05-30-F) — auto-layout direction switch.
 *
 * `setSubjectDirection(doc, dir)` flips the subject edge's handles so
 * the actor-anchored layout lays the step graph out LR or TB. The
 * subject edge is identified by the SAME `detectSubjectEdgeId` the
 * layout uses.
 */
import { describe, expect, it } from "vitest";
import {
  detectSubjectEdgeId,
  setSubjectDirection,
} from "../src/flow/actorAnchoredLayout";
import type { CanvasDoc, SketchEdge, SketchNode } from "../src/types";

function node(id: string, kind: SketchNode["kind"], extra: Record<string, unknown> = {}): SketchNode {
  return {
    id,
    kind,
    label: id,
    x: 0,
    y: 0,
    width: 120,
    height: 60,
    color: "#fff",
    shape: "rectangle",
    icon: null,
    collapsed: false,
    is_root: false,
    details_path: null,
    owner: null,
    version: "v0.0",
    ...extra,
  } as unknown as SketchNode;
}

function edge(id: string, source: string, target: string, over: Partial<SketchEdge> = {}): SketchEdge {
  return {
    id,
    source,
    target,
    sourceHandle: "r",
    targetHandle: "l",
    label: "",
    style: "solid",
    directed: true,
    action_verb: null,
    value_form: [],
    ...over,
  };
}

function doc(): CanvasDoc {
  return {
    id: "d",
    name: "d",
    canvas_kind: "service_detail",
    service_ref: null,
    nodes: [
      node("bana", "actor_ref", { side: "user" }),
      node("entry", "step"),
      node("s2", "step"),
    ],
    edges: [edge("subj", "bana", "entry"), edge("seq", "entry", "s2")],
  } as unknown as CanvasDoc;
}

describe("detectSubjectEdgeId (D-2026-05-30-F)", () => {
  it("finds the first edge whose source is the user-side actor_ref", () => {
    expect(detectSubjectEdgeId(doc())).toBe("subj");
  });
  it("returns null when there is no actor_ref", () => {
    const d = doc();
    d.nodes = d.nodes.filter((n) => n.kind !== "actor_ref");
    expect(detectSubjectEdgeId(d)).toBeNull();
  });
});

describe("setSubjectDirection (D-2026-05-30-F)", () => {
  it("LR sets subject handles r → l", () => {
    const out = setSubjectDirection(doc(), "LR");
    const subj = out.edges.find((e) => e.id === "subj")!;
    expect([subj.sourceHandle, subj.targetHandle]).toEqual(["r", "l"]);
  });
  it("TB sets subject handles b → t", () => {
    const out = setSubjectDirection(doc(), "TB");
    const subj = out.edges.find((e) => e.id === "subj")!;
    expect([subj.sourceHandle, subj.targetHandle]).toEqual(["b", "t"]);
  });
  it("leaves non-subject edges untouched", () => {
    const out = setSubjectDirection(doc(), "TB");
    const seq = out.edges.find((e) => e.id === "seq")!;
    expect([seq.sourceHandle, seq.targetHandle]).toEqual(["r", "l"]);
  });
  it("returns the doc unchanged when there is no subject edge", () => {
    const d = doc();
    d.nodes = d.nodes.filter((n) => n.kind !== "actor_ref");
    expect(setSubjectDirection(d, "TB")).toBe(d);
  });
});
