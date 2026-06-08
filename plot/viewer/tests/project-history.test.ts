/**
 * useProjectHistory characterization (D-2026-06-08-A, step 7 "regression-first").
 *
 * Undo is the WEAKEST seam for the server-state migration (ARCH_REVIEW): it is a
 * PROJECT-LEVEL UNIFIED stack of full-doc snapshots shared across every canvas —
 * Ctrl+Z on one tab can roll back an edit that landed on another. TanStack
 * Query's per-resource cache does NOT model this, so this test pins the current
 * behaviour before the migration touches it. If a later step regresses undo,
 * these fail.
 */
import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useProjectHistory, type HistoryEntry } from "../src/canvases/useProjectHistory";
import type { CanvasDoc, CanvasKey } from "../src/types";

const doc = (tag: string) => ({ __tag: tag }) as unknown as CanvasDoc;
const entry = (key: CanvasKey, prevTag: string, nextTag: string): HistoryEntry => ({
  canvasKey: key,
  prev: doc(prevTag),
  next: doc(nextTag),
});

describe("useProjectHistory — project-level unified stack (D-2026-06-08-A)", () => {
  it("undo/redo round-trips a single entry", () => {
    const { result } = renderHook(() => useProjectHistory());
    const e = entry("foundation", "f0", "f1");
    act(() => result.current.push(e));
    expect(result.current.canUndo).toBe(true);
    expect(result.current.canRedo).toBe(false);

    let popped: HistoryEntry | null = null;
    act(() => {
      popped = result.current.undo();
    });
    expect(popped).toBe(e);
    expect(result.current.canUndo).toBe(false);
    expect(result.current.canRedo).toBe(true);

    let re: HistoryEntry | null = null;
    act(() => {
      re = result.current.redo();
    });
    expect(re).toBe(e);
    expect(result.current.canRedo).toBe(false);
  });

  it("is ONE timeline across canvases — undo reverts the last edit regardless of tab", () => {
    const { result } = renderHook(() => useProjectHistory());
    const onFoundation = entry("foundation", "f0", "f1");
    const onActors = entry("actors", "a0", "a1");
    act(() => {
      result.current.push(onFoundation);
      result.current.push(onActors); // different canvas, same stack
    });

    // LIFO across canvases: the actors edit reverts first...
    let first: HistoryEntry | null = null;
    act(() => {
      first = result.current.undo();
    });
    expect(first).toBe(onActors);
    // ...then the foundation edit — proving a single project-level timeline.
    let second: HistoryEntry | null = null;
    act(() => {
      second = result.current.undo();
    });
    expect(second).toBe(onFoundation);
  });

  it("push clears the redo frontier", () => {
    const { result } = renderHook(() => useProjectHistory());
    act(() => result.current.push(entry("foundation", "f0", "f1")));
    act(() => {
      result.current.undo();
    });
    expect(result.current.canRedo).toBe(true);
    act(() => result.current.push(entry("actors", "a0", "a1"))); // new edit
    expect(result.current.canRedo).toBe(false); // frontier dropped
  });

  it("clear() / init() resets both stacks (project switch or external change)", () => {
    const { result } = renderHook(() => useProjectHistory());
    act(() => {
      result.current.push(entry("foundation", "f0", "f1"));
      result.current.push(entry("actors", "a0", "a1"));
    });
    act(() => result.current.clear());
    expect(result.current.canUndo).toBe(false);
    expect(result.current.canRedo).toBe(false);
    expect(result.current.undo()).toBe(null);
  });

  it("caps the past at 50 entries (oldest dropped)", () => {
    const { result } = renderHook(() => useProjectHistory());
    act(() => {
      for (let i = 0; i < 55; i++) result.current.push(entry("foundation", `p${i}`, `n${i}`));
    });
    // Drain — at most 50 undos succeed, the 6 oldest were shifted out.
    let count = 0;
    act(() => {
      while (result.current.undo()) count++;
    });
    expect(count).toBe(50);
  });
});
