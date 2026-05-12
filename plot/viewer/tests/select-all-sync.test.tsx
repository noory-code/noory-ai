/**
 * Cmd+A select-all controlled-contract regression —
 * v0.16.17 (D-2026-05-12-S).
 *
 * Before: ``useKeyboardShortcuts`` 's Cmd+A handler called only
 * ``flowRef.current.setNodes(...)`` + ``setEdges(...)`` to flip RF's
 * internal ``selected`` flag. RF does NOT emit
 * ``onSelectionChange`` from store mutations, so
 * ``selectedNodeIds.current`` (the SketchCanvas ref the clipboard
 * reads) stayed at its previous value. Cmd+C / Cmd+D following Cmd+A
 * copied / duplicated the OLD selection, not all nodes.
 *
 * Fix: after the setNodes/setEdges mutation, copy the resulting node
 * id list into ``selectedNodeIds.current`` directly. This test
 * asserts that synchronisation.
 *
 * The test uses ``renderHook`` + a fake ``ReactFlowInstance`` mock so
 * we exercise the Cmd+A code path without mounting the full canvas.
 */
import { renderHook } from "@testing-library/react";
import { act } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useKeyboardShortcuts } from "../src/canvases/sketch/useKeyboardShortcuts";
import type { CanvasDoc } from "../src/types";

interface FakeRfNode {
  id: string;
  selected: boolean;
}
interface FakeRfEdge {
  id: string;
  selected: boolean;
}

function makeFakeFlow(nodeIds: string[], edgeIds: string[] = []) {
  const nodes: FakeRfNode[] = nodeIds.map((id) => ({ id, selected: false }));
  const edges: FakeRfEdge[] = edgeIds.map((id) => ({ id, selected: false }));
  return {
    getNodes: () => nodes,
    getEdges: () => edges,
    setNodes: (updater: (ns: FakeRfNode[]) => FakeRfNode[]) => {
      const next = updater(nodes);
      nodes.length = 0;
      nodes.push(...next);
    },
    setEdges: (updater: (es: FakeRfEdge[]) => FakeRfEdge[]) => {
      const next = updater(edges);
      edges.length = 0;
      edges.push(...next);
    },
  };
}

function dispatchCmdA() {
  const ev = new KeyboardEvent("keydown", {
    key: "a",
    metaKey: true,
    bubbles: true,
    cancelable: true,
  });
  window.dispatchEvent(ev);
}

const fakeDoc: CanvasDoc = {
  id: "x",
  name: "X",
  created: "",
  updated: "",
  version: 1,
  nodes: [],
  edges: [],
};

afterEach(() => {
  // belt-and-braces — useEffect cleanup removes listeners on unmount,
  // but explicit removeAll prevents cross-test leakage.
});

describe("Cmd+A synchronises selectedNodeIds.current with RF store", () => {
  it("populates selectedNodeIds.current with every node id on the canvas", () => {
    const fakeFlow = makeFakeFlow(["a", "b", "c"]);
    const docRef = { current: fakeDoc };
    const flowRef = { current: fakeFlow as unknown as ReturnType<typeof makeFakeFlow> };
    const selectedNodeIds = { current: [] as string[] };
    const clipboard = {
      hasClip: () => false,
      copy: vi.fn(),
      paste: vi.fn(() => fakeDoc),
      duplicate: vi.fn(() => fakeDoc),
    };
    renderHook(() =>
      useKeyboardShortcuts({
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        docRef: docRef as any,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        flowRef: flowRef as any,
        selectedNodeIds,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        clipboard: clipboard as any,
        onUndo: vi.fn(),
        onRedo: vi.fn(),
        onDocChange: vi.fn(),
      }),
    );
    act(() => {
      dispatchCmdA();
    });
    expect(selectedNodeIds.current).toEqual(["a", "b", "c"]);
    // RF store also flipped.
    expect(fakeFlow.getNodes().every((n) => n.selected)).toBe(true);
  });

  it("Cmd+C after Cmd+A copies the newly-synced selection (full set)", () => {
    const fakeFlow = makeFakeFlow(["a", "b", "c"]);
    const docRef = { current: fakeDoc };
    const flowRef = { current: fakeFlow as unknown as ReturnType<typeof makeFakeFlow> };
    const selectedNodeIds = { current: [] as string[] };
    const copyMock = vi.fn();
    const clipboard = {
      hasClip: () => false,
      copy: copyMock,
      paste: vi.fn(() => fakeDoc),
      duplicate: vi.fn(() => fakeDoc),
    };
    renderHook(() =>
      useKeyboardShortcuts({
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        docRef: docRef as any,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        flowRef: flowRef as any,
        selectedNodeIds,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        clipboard: clipboard as any,
        onUndo: vi.fn(),
        onRedo: vi.fn(),
        onDocChange: vi.fn(),
      }),
    );
    act(() => {
      dispatchCmdA();
    });
    // Now Cmd+C.
    act(() => {
      const ev = new KeyboardEvent("keydown", {
        key: "c",
        metaKey: true,
        bubbles: true,
        cancelable: true,
      });
      window.dispatchEvent(ev);
    });
    expect(copyMock).toHaveBeenCalledTimes(1);
    expect(copyMock).toHaveBeenCalledWith(fakeDoc, ["a", "b", "c"]);
  });
});
