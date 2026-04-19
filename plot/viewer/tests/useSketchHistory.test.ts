import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { useSketchHistory } from "../src/canvases/useSketchHistory";

describe("useSketchHistory", () => {
  it("starts empty", () => {
    const { result } = renderHook(() => useSketchHistory<string>());
    expect(result.current.doc).toBeNull();
    expect(result.current.canUndo).toBe(false);
    expect(result.current.canRedo).toBe(false);
  });

  it("init sets present", () => {
    const { result } = renderHook(() => useSketchHistory<string>());
    act(() => {
      result.current.init("a");
    });
    expect(result.current.doc).toBe("a");
    expect(result.current.canUndo).toBe(false);
  });

  it("push records history and enables undo", () => {
    const { result } = renderHook(() => useSketchHistory<string>());
    act(() => result.current.init("a"));
    act(() => result.current.push("b"));
    expect(result.current.doc).toBe("b");
    expect(result.current.canUndo).toBe(true);
  });

  it("undo returns to previous value", () => {
    const { result } = renderHook(() => useSketchHistory<string>());
    act(() => result.current.init("a"));
    act(() => result.current.push("b"));
    let undone: string | null = null;
    act(() => {
      undone = result.current.undo();
    });
    expect(undone).toBe("a");
    expect(result.current.doc).toBe("a");
    expect(result.current.canRedo).toBe(true);
  });

  it("redo restores the undone value", () => {
    const { result } = renderHook(() => useSketchHistory<string>());
    act(() => result.current.init("a"));
    act(() => result.current.push("b"));
    act(() => {
      result.current.undo();
    });
    let redone: string | null = null;
    act(() => {
      redone = result.current.redo();
    });
    expect(redone).toBe("b");
    expect(result.current.doc).toBe("b");
  });

  it("push after undo clears redo stack", () => {
    const { result } = renderHook(() => useSketchHistory<string>());
    act(() => result.current.init("a"));
    act(() => result.current.push("b"));
    act(() => {
      result.current.undo();
    });
    act(() => result.current.push("c"));
    expect(result.current.canRedo).toBe(false);
    expect(result.current.doc).toBe("c");
  });

  it("undo on empty past returns null", () => {
    const { result } = renderHook(() => useSketchHistory<string>());
    act(() => result.current.init("a"));
    let undone: string | null = "not null";
    act(() => {
      undone = result.current.undo();
    });
    expect(undone).toBeNull();
    expect(result.current.doc).toBe("a");
  });
});
