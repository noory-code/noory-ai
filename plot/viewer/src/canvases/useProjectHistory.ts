import { useCallback, useRef, useState } from "react";
import type { CanvasDoc, CanvasKey } from "../types";

/**
 * Project-level unified undo/redo stack (v0.4).
 *
 * Each entry records one canvas mutation:
 *
 *   { canvasKey, prev, next }
 *
 * Undo rewinds to ``prev``; redo re-applies ``next``. Entries from every
 * canvas share a single timeline, so Ctrl+Z on the Services tab can roll
 * back a Mission edit on the Core tab — the tab auto-switches to where
 * the reverted change landed.
 *
 * The stack is in-memory only: cleared on ``init`` (project switch) and
 * on ``replace`` (external change arrived via WebSocket). Persistent
 * history lives separately in the project's git repo, via user-named
 * session tags.
 */

export interface HistoryEntry {
  canvasKey: CanvasKey;
  prev: CanvasDoc;
  next: CanvasDoc;
}

export interface ProjectHistoryApi {
  /** Record a mutation. Clears any redo frontier. */
  push(entry: HistoryEntry): void;
  /** Rewind one step. Returns ``{canvasKey, snapshot: prev}`` to apply. */
  undo(): HistoryEntry | null;
  /** Replay the most recently undone step. */
  redo(): HistoryEntry | null;
  /** Full reset (e.g., project switch). */
  init(): void;
  /** Drop history without an init (e.g., external WebSocket change). */
  clear(): void;
  canUndo: boolean;
  canRedo: boolean;
}

const LIMIT = 50;

export function useProjectHistory(): ProjectHistoryApi {
  const past = useRef<HistoryEntry[]>([]);
  const future = useRef<HistoryEntry[]>([]);
  // Re-render trigger — the refs above hold the authoritative data, but
  // React needs a state bump so canUndo / canRedo flip.
  const [, setBump] = useState(0);
  const bump = useCallback(() => setBump((n) => n + 1), []);

  const push = useCallback(
    (entry: HistoryEntry) => {
      past.current.push(entry);
      if (past.current.length > LIMIT) past.current.shift();
      future.current.length = 0;
      bump();
    },
    [bump],
  );

  const undo = useCallback((): HistoryEntry | null => {
    const entry = past.current.pop();
    if (!entry) return null;
    future.current.push(entry);
    bump();
    return entry;
  }, [bump]);

  const redo = useCallback((): HistoryEntry | null => {
    const entry = future.current.pop();
    if (!entry) return null;
    past.current.push(entry);
    bump();
    return entry;
  }, [bump]);

  const clear = useCallback(() => {
    past.current.length = 0;
    future.current.length = 0;
    bump();
  }, [bump]);

  return {
    push,
    undo,
    redo,
    init: clear,
    clear,
    get canUndo() {
      return past.current.length > 0;
    },
    get canRedo() {
      return future.current.length > 0;
    },
  };
}
