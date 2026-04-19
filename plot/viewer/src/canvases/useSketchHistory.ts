import { useCallback, useState } from "react";

const LIMIT = 50;

export interface SketchHistory<T> {
  doc: T | null;
  canUndo: boolean;
  canRedo: boolean;
  /** Seed the history with a fresh present (e.g., after loading from server). */
  init: (doc: T) => void;
  /** Record a user-driven change: present → past, new doc → present, clear redo. */
  push: (doc: T) => void;
  /** Swap present without touching the past/future — for remote refreshes. */
  replace: (doc: T) => void;
  /** Returns the new present, or null when undo is not possible. */
  undo: () => T | null;
  /** Returns the new present, or null when redo is not possible. */
  redo: () => T | null;
}

export function useSketchHistory<T>(): SketchHistory<T> {
  const [past, setPast] = useState<T[]>([]);
  const [present, setPresent] = useState<T | null>(null);
  const [future, setFuture] = useState<T[]>([]);

  const init = useCallback((doc: T) => {
    setPast([]);
    setPresent(doc);
    setFuture([]);
  }, []);

  const push = useCallback((doc: T) => {
    setPast((p) => (present === null ? [] : [...p, present].slice(-LIMIT)));
    setPresent(doc);
    setFuture([]);
  }, [present]);

  const replace = useCallback((doc: T) => {
    setPresent(doc);
  }, []);

  const undo = useCallback((): T | null => {
    if (past.length === 0 || present === null) return null;
    const prev = past[past.length - 1];
    setPast(past.slice(0, -1));
    setFuture((f) => [present, ...f].slice(0, LIMIT));
    setPresent(prev);
    return prev;
  }, [past, present]);

  const redo = useCallback((): T | null => {
    if (future.length === 0 || present === null) return null;
    const next = future[0];
    setFuture(future.slice(1));
    setPast((p) => [...p, present].slice(-LIMIT));
    setPresent(next);
    return next;
  }, [past, present, future]);

  return {
    doc: present,
    canUndo: past.length > 0,
    canRedo: future.length > 0,
    init,
    push,
    replace,
    undo,
    redo,
  };
}
