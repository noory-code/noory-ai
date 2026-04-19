import { describe, expect, it } from "vitest";
import { autoLayout } from "../src/flow/autoLayout";
import type { SketchDoc } from "../src/types";

function makeDoc(overrides: Partial<SketchDoc> = {}): SketchDoc {
  return {
    id: "x",
    name: "X",
    created: "2026-04-20",
    updated: "2026-04-20",
    version: 1,
    nodes: [],
    edges: [],
    ...overrides,
  };
}

describe("autoLayout", () => {
  it("arranges connected nodes in LR order", () => {
    const doc = makeDoc({
      nodes: [
        { id: "a", label: "A", body: "", x: 999, y: 999, width: 180, height: 80, color: "#fff" },
        { id: "b", label: "B", body: "", x: 999, y: 999, width: 180, height: 80, color: "#fff" },
      ],
      edges: [
        {
          id: "e1",
          source: "a",
          target: "b",
          sourceHandle: null,
          targetHandle: null,
          label: "",
          style: "solid",
        },
      ],
    });
    const laid = autoLayout(doc);
    const a = laid.nodes.find((n) => n.id === "a")!;
    const b = laid.nodes.find((n) => n.id === "b")!;
    expect(a.x).toBeLessThan(b.x); // LR → source left of target
  });

  it("leaves orphan nodes untouched", () => {
    const doc = makeDoc({
      nodes: [
        { id: "orphan", label: "O", body: "", x: 500, y: 500, width: 180, height: 80, color: "#fff" },
      ],
    });
    const laid = autoLayout(doc);
    expect(laid.nodes[0].x).toBe(500);
    expect(laid.nodes[0].y).toBe(500);
  });
});
