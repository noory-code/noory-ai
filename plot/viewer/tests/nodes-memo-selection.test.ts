/**
 * v0.37.1 (D-2026-05-31-AD) — the controlled ``nodes`` array (useNodesMemo)
 * must carry ``selected`` from the tracked selection set. Without it React
 * Flow resets selection on every re-render and a node click "선택되고 해제되고".
 */
import { renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useNodesMemo } from "../src/canvases/sketch/useNodesMemo";
import type { CanvasDoc, SketchNode } from "../src/types";

function mkNode(id: string): SketchNode {
  return {
    id,
    label: id,
    x: 0,
    y: 0,
    width: 80,
    height: 36,
    color: "#fff",
    shape: "rectangle",
    icon: null,
    kind: "mission",
    parent_id: null,
    collapsed: false,
    is_root: false,
  } as unknown as SketchNode;
}

function baseArgs(doc: CanvasDoc, selectedIds: Set<string>) {
  return {
    doc,
    childIdsByParent: new Map<string, string[]>(),
    nearestCollapsedAncestor: () => null,
    subtreeSize: () => 0,
    toggleCollapsed: vi.fn(),
    updateNode: vi.fn(),
    orphanActorRefIds: new Set<string>(),
    availableActors: undefined,
    availableMissions: undefined,
    availableValues: undefined,
    availableIdentities: undefined,
    onNodeDrill: undefined,
    projectAnchor: null,
    projectName: null,
    onAnchorChange: undefined,
    setBodyModalNodeId: vi.fn(),
    hideRootServiceNode: false,
    shouldDrill: undefined,
    showFoldButton: true,
    injectAnchor: false,
    selectedIds,
  };
}

describe("useNodesMemo — selection (D-2026-05-31-AD)", () => {
  const doc = { nodes: [mkNode("a"), mkNode("b")], edges: [] } as unknown as CanvasDoc;

  it("marks only the selected node as selected", () => {
    const { result } = renderHook(() => useNodesMemo(baseArgs(doc, new Set(["a"]))));
    const byId = Object.fromEntries(result.current.map((n) => [n.id, n.selected]));
    expect(byId.a).toBe(true);
    expect(byId.b).toBe(false);
  });

  it("marks no node selected when the set is empty", () => {
    const { result } = renderHook(() => useNodesMemo(baseArgs(doc, new Set())));
    expect(result.current.every((n) => n.selected === false)).toBe(true);
  });

  it("reflects a multi-selection", () => {
    const { result } = renderHook(() => useNodesMemo(baseArgs(doc, new Set(["a", "b"]))));
    expect(result.current.every((n) => n.selected === true)).toBe(true);
  });
});
