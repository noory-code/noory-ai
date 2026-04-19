import { renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { useSketchClipboard } from "../src/canvases/useSketchClipboard";
import type { SketchDoc } from "../src/types";

function makeDoc(): SketchDoc {
  return {
    id: "x",
    name: "X",
    created: "2026-04-20",
    updated: "2026-04-20",
    version: 1,
    nodes: [
      { id: "a", label: "A", body: "", x: 0, y: 0, width: 180, height: 80, color: "#fff" },
      { id: "b", label: "B", body: "", x: 100, y: 0, width: 180, height: 80, color: "#fff" },
      { id: "c", label: "C", body: "", x: 200, y: 0, width: 180, height: 80, color: "#fff" },
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
      {
        id: "e2",
        source: "b",
        target: "c",
        sourceHandle: null,
        targetHandle: null,
        label: "",
        style: "solid",
      },
    ],
  };
}

describe("useSketchClipboard", () => {
  it("copy + paste appends new nodes with fresh ids", () => {
    const { result } = renderHook(() => useSketchClipboard());
    const doc = makeDoc();
    result.current.copy(doc, ["a", "b"]);
    const pasted = result.current.paste(doc, { x: 50, y: 50 });
    expect(pasted.nodes).toHaveLength(5); // original 3 + 2 pasted
    const newNodes = pasted.nodes.slice(3);
    expect(newNodes.every((n) => !["a", "b", "c"].includes(n.id))).toBe(true);
    expect(newNodes[0].x).toBe(50);
  });

  it("paste remaps edge source/target to new ids", () => {
    const { result } = renderHook(() => useSketchClipboard());
    const doc = makeDoc();
    result.current.copy(doc, ["a", "b"]);
    const pasted = result.current.paste(doc);
    const newEdges = pasted.edges.filter((e) => e.id !== "e1" && e.id !== "e2");
    expect(newEdges).toHaveLength(1); // e1 (a→b) cloned; e2 (b→c) dropped (c not in selection)
    const newIds = pasted.nodes.slice(3).map((n) => n.id);
    expect(newIds).toContain(newEdges[0].source);
    expect(newIds).toContain(newEdges[0].target);
  });

  it("paste with empty clipboard returns doc unchanged", () => {
    const { result } = renderHook(() => useSketchClipboard());
    const doc = makeDoc();
    const pasted = result.current.paste(doc);
    expect(pasted).toBe(doc);
  });

  it("duplicate clones selected nodes in-place", () => {
    const { result } = renderHook(() => useSketchClipboard());
    const doc = makeDoc();
    const out = result.current.duplicate(doc, ["c"]);
    expect(out.nodes).toHaveLength(4);
    expect(out.nodes[3].label).toBe("C");
    expect(out.nodes[3].id).not.toBe("c");
  });

  it("hasClip reports empty then non-empty", () => {
    const { result } = renderHook(() => useSketchClipboard());
    expect(result.current.hasClip()).toBe(false);
    result.current.copy(makeDoc(), ["a"]);
    expect(result.current.hasClip()).toBe(true);
  });
});
