/**
 * Regression: a drag that ends on a macOS trackpad emits a trailing
 * ``contextmenu`` event AFTER pointerup. React Flow's d3-drag only
 * suppresses ``contextmenu`` WHILE a drag is active, so the trailing event
 * leaks to ``onNodeContextMenu`` / ``onPaneContextMenu`` and the sketch
 * context menu pops up at the release point — the "drag a node, let go, it
 * acts like a right-click" bug (user report 2026-06-15).
 *
 * The fix (D-2026-06-15-N, broadened D-2026-06-16-A): ``useContextMenus``
 * watches the raw pointer gesture at the window level — a ``pointerup`` that
 * moved more than a few px from its ``pointerdown`` is a DRAG, so the next
 * ``contextmenu`` is swallowed. This is kind- and canvas-agnostic (it does
 * NOT depend on React Flow firing ``onNodeDragStop`` per node), so it covers
 * services, categories, groups, and every detail canvas uniformly. A real
 * right-click never moves, so its menu still opens.
 */
import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { MouseEvent as ReactMouseEvent } from "react";
import type { Edge, Node, ReactFlowInstance } from "reactflow";
import { useContextMenus } from "../src/canvases/sketch/useContextMenus";
import type { CanvasDoc } from "../src/types";

function makeArgs() {
  const docRef = {
    current: { canvas_kind: "services", nodes: [], edges: [] } as unknown as CanvasDoc,
  };
  const flowRef = {
    current: {
      screenToFlowPosition: (p: { x: number; y: number }) => p,
    } as unknown as ReactFlowInstance,
  };
  return {
    docRef,
    flowRef,
    onDocChange: vi.fn(),
    clipboard: {
      hasClip: () => false,
      copy: vi.fn(),
      duplicate: vi.fn(),
      paste: vi.fn(),
    } as never,
    handleNodesDelete: vi.fn(),
    handleEdgesDelete: vi.fn(),
    addNodeAt: vi.fn(),
    selectedNodeIds: { current: [] as string[] },
  };
}

function fakeEvent() {
  return {
    preventDefault: vi.fn(),
    clientX: 12,
    clientY: 34,
  } as unknown as ReactMouseEvent;
}

/** Simulate a press at (x,y) then release at (x2,y2) at the window level. */
function gesture(x: number, y: number, x2: number, y2: number) {
  window.dispatchEvent(new MouseEvent("pointerdown", { clientX: x, clientY: y }));
  window.dispatchEvent(new MouseEvent("pointerup", { clientX: x2, clientY: y2 }));
}

const NODE = { id: "n1" } as Node;
const EDGE = { id: "e1" } as Edge;

describe("context-menu drag suppression (D-2026-06-15-N / D-2026-06-16-A)", () => {
  it("opens the node menu on a plain right-click (no preceding drag)", () => {
    const { result } = renderHook(() => useContextMenus(makeArgs()));
    act(() => result.current.openNodeMenu(fakeEvent(), NODE));
    expect(result.current.menu).not.toBeNull();
  });

  it("opens the menu when the press did not move (a click, not a drag)", () => {
    const { result } = renderHook(() => useContextMenus(makeArgs()));
    act(() => gesture(40, 40, 41, 41)); // 1px — below threshold
    act(() => result.current.openNodeMenu(fakeEvent(), NODE));
    expect(result.current.menu).not.toBeNull();
  });

  it("suppresses the trailing contextmenu after a drag gesture (any node kind)", () => {
    const { result } = renderHook(() => useContextMenus(makeArgs()));
    const evt = fakeEvent();
    act(() => gesture(10, 10, 90, 90)); // moved well past threshold
    act(() => result.current.openNodeMenu(evt, NODE));
    expect(evt.preventDefault).toHaveBeenCalled();
    expect(result.current.menu).toBeNull();
  });

  it("suppresses a trailing pane contextmenu after a drag too", () => {
    const { result } = renderHook(() => useContextMenus(makeArgs()));
    act(() => gesture(10, 10, 90, 90));
    act(() => result.current.openPaneMenu(fakeEvent()));
    expect(result.current.menu).toBeNull();
  });

  it("suppresses a trailing edge contextmenu after a drag too", () => {
    const { result } = renderHook(() => useContextMenus(makeArgs()));
    act(() => gesture(10, 10, 90, 90));
    act(() => result.current.openEdgeMenu(fakeEvent(), EDGE));
    expect(result.current.menu).toBeNull();
  });

  it("only swallows ONE contextmenu — a second attempt opens normally", () => {
    const { result } = renderHook(() => useContextMenus(makeArgs()));
    act(() => gesture(10, 10, 90, 90));
    act(() => result.current.openNodeMenu(fakeEvent(), NODE)); // swallowed
    act(() => result.current.openNodeMenu(fakeEvent(), NODE)); // opens
    expect(result.current.menu).not.toBeNull();
  });

  it("a deliberate right-click after a drag opens (its pointerdown disarms)", () => {
    const { result } = renderHook(() => useContextMenus(makeArgs()));
    act(() => gesture(10, 10, 90, 90)); // drag → armed
    // A real right-click fires pointerdown (no movement) before contextmenu,
    // which disarms the one-shot suppression.
    act(() => {
      window.dispatchEvent(new MouseEvent("pointerdown", { clientX: 90, clientY: 90 }));
    });
    act(() => result.current.openNodeMenu(fakeEvent(), NODE));
    expect(result.current.menu).not.toBeNull();
  });
});
