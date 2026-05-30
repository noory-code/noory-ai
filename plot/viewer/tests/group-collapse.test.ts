/**
 * v0.29.0 (D-2026-05-30-I) — group collapse hides members.
 */
import { describe, expect, it } from "vitest";
import { collapsedGroupMemberIds } from "../src/canvases/sketch/groupCollapse";
import type { CanvasDoc, SketchNode } from "../src/types";

function group(id: string, member_ids: string[], collapsed: boolean): SketchNode {
  return {
    id, kind: "group", label: id, x: 0, y: 0, width: 200, height: 120,
    color: "#eee", shape: "rounded", icon: null, collapsed,
    is_root: false, details_path: null, owner: null, version: "v1.0",
    member_ids, body: "",
  } as unknown as SketchNode;
}

function step(id: string): SketchNode {
  return {
    id, kind: "step", label: id, x: 0, y: 0, width: 150, height: 60,
    color: "#fff", shape: "rounded", icon: null, collapsed: false,
    is_root: false, details_path: null, owner: null, version: "v1.0",
    order: null, outcome: "", body: "", polarity: "neutral",
  } as unknown as SketchNode;
}

const nodes = (ns: SketchNode[]): CanvasDoc["nodes"] => ns as unknown as CanvasDoc["nodes"];

describe("collapsedGroupMemberIds (D-2026-05-30-I)", () => {
  it("hides members of a collapsed group", () => {
    const hidden = collapsedGroupMemberIds(nodes([
      group("g1", ["a", "b"], true),
      step("a"), step("b"), step("c"),
    ]));
    expect(hidden.has("a")).toBe(true);
    expect(hidden.has("b")).toBe(true);
    expect(hidden.has("c")).toBe(false);
  });

  it("hides nothing for an expanded group", () => {
    const hidden = collapsedGroupMemberIds(nodes([
      group("g1", ["a", "b"], false),
      step("a"), step("b"),
    ]));
    expect(hidden.size).toBe(0);
  });

  it("unions members across multiple collapsed groups", () => {
    const hidden = collapsedGroupMemberIds(nodes([
      group("g1", ["a"], true),
      group("g2", ["b", "c"], true),
      step("a"), step("b"), step("c"),
    ]));
    expect([...hidden].sort()).toEqual(["a", "b", "c"]);
  });
});
