import { useCallback, useRef, useState } from "react";
import { getCanvas, putCanvas } from "../api";
import type { SaveState } from "../canvases/SketchToolbar";
import type { ProjectHistoryApi } from "../canvases/useProjectHistory";
import type { CanvasDoc, CanvasKey } from "../types";

const DEBOUNCE_MS = 400;

export interface UseCanvasPersistArgs {
  projectPath: string | null;
  activeId: string | null;
  /** Owned by ``useProjectHistory``; passed in so undo/redo push/pop from
   *  the same stack the App binds to ``SketchCanvas``. */
  history: ProjectHistoryApi;
  /** Mutate the cache in-place with the new canvas. */
  setCanvasCache: React.Dispatch<
    React.SetStateAction<Map<CanvasKey, CanvasDoc>>
  >;
  /** Track which service-detail canvases the server says exist right now. */
  setServiceDetails: React.Dispatch<React.SetStateAction<string[]>>;
  /** After a successful PUT the sidebar's ``updated`` stamp changes. */
  onListStale: () => void;
  onError: (err: string) => void;
}

export interface UseCanvasPersistApi {
  saveState: SaveState;
  /** Shared with ``useProjectSocket`` so the WS layer can skip self-echoes. */
  pendingWrites: React.MutableRefObject<Set<CanvasKey>>;
  /** Apply a user edit: cache update + history push + debounced PUT. */
  applyEdit: (
    key: CanvasKey,
    prev: CanvasDoc,
    next: CanvasDoc,
    opts?: { skipHistory?: boolean },
  ) => void;
  /** Pop history top. Returns the key that changed so the caller can focus
   *  the matching tab. ``null`` if the stack was empty. */
  undo: () => CanvasKey | null;
  redo: () => CanvasKey | null;
}

export function useCanvasPersist(args: UseCanvasPersistArgs): UseCanvasPersistApi {
  const {
    projectPath,
    activeId,
    history,
    setCanvasCache,
    setServiceDetails,
    onListStale,
    onError,
  } = args;

  const [saveState, setSaveState] = useState<SaveState>("idle");
  const saveTimer = useRef<number | null>(null);
  const savedTimer = useRef<number | null>(null);
  const pendingWrites = useRef(new Set<CanvasKey>());

  // Refs so persist doesn't force a re-render when args mutate.
  const projectPathRef = useRef(projectPath);
  projectPathRef.current = projectPath;
  const activeIdRef = useRef(activeId);
  activeIdRef.current = activeId;
  const onListStaleRef = useRef(onListStale);
  onListStaleRef.current = onListStale;
  const onErrorRef = useRef(onError);
  onErrorRef.current = onError;

  const persistCanvas = useCallback(
    (key: CanvasKey, canvas: CanvasDoc) => {
      const pp = projectPathRef.current;
      const pid = activeIdRef.current;
      if (!pp || !pid) return;
      pendingWrites.current.add(key);
      setSaveState("saving");
      if (saveTimer.current !== null) window.clearTimeout(saveTimer.current);
      saveTimer.current = window.setTimeout(() => {
        saveTimer.current = null;
        putCanvas(pp, pid, canvas)
          .then((res) => {
            setSaveState("saved");
            // v0.24.12 (D-2026-05-21-A) — refresh per-node ``_dirty``
            // from PUT response. Pre-v0.24.12 the response was a bare
            // canvas without ``_dirty`` decoration, so the Inspector's
            // publish button gate stayed stale until a full GET (e.g.
            // page reload). Merge only ``_dirty`` so any user edit that
            // arrived after the PUT was sent stays intact (the next
            // PUT cycle will refresh ``_dirty`` for that edit too).
            const dirtyByNodeId = new Map<string, boolean>();
            for (const n of res.canvas.nodes) {
              const d = (n as { _dirty?: boolean })._dirty;
              if (typeof d === "boolean") dirtyByNodeId.set(n.id, d);
            }
            if (dirtyByNodeId.size > 0) {
              setCanvasCache((cur) => {
                const cached = cur.get(key);
                if (!cached) return cur;
                const m = new Map(cur);
                m.set(key, {
                  ...cached,
                  nodes: cached.nodes.map((n) => {
                    const d = dirtyByNodeId.get(n.id);
                    return d === undefined
                      ? n
                      : ({ ...n, _dirty: d } as typeof n);
                  }),
                });
                return m;
              });
            }
            // Reconcile Overview ↔ Detail sync the server reports.
            if (res.sync.created.length || res.sync.archived.length) {
              setServiceDetails((prev) => {
                const s = new Set(prev);
                for (const n of res.sync.created) s.add(n);
                for (const n of res.sync.archived) s.delete(n);
                return Array.from(s).sort();
              });
              if (res.sync.created.length) {
                void (async () => {
                  for (const sid of res.sync.created) {
                    try {
                      const d = await getCanvas(pp, pid, "service_detail", sid);
                      setCanvasCache((prev) => {
                        const next = new Map(prev);
                        next.set(`service_detail:${sid}`, d);
                        return next;
                      });
                    } catch {
                      // best-effort; next open will fetch.
                    }
                  }
                })();
              }
              if (res.sync.archived.length) {
                setCanvasCache((prev) => {
                  const next = new Map(prev);
                  for (const sid of res.sync.archived) {
                    next.delete(`service_detail:${sid}`);
                  }
                  return next;
                });
              }
            }
            if (savedTimer.current !== null)
              window.clearTimeout(savedTimer.current);
            savedTimer.current = window.setTimeout(
              () => setSaveState("idle"),
              1500,
            );
            onListStaleRef.current();
          })
          .catch((err) => {
            setSaveState("error");
            onErrorRef.current(err instanceof Error ? err.message : String(err));
          });
      }, DEBOUNCE_MS);
    },
    [setCanvasCache, setServiceDetails],
  );

  const applyEdit = useCallback(
    (
      key: CanvasKey,
      prev: CanvasDoc,
      next: CanvasDoc,
      opts?: { skipHistory?: boolean },
    ) => {
      setCanvasCache((cur) => {
        const m = new Map(cur);
        m.set(key, next);
        return m;
      });
      if (!opts?.skipHistory) {
        history.push({ canvasKey: key, prev, next });
      }
      persistCanvas(key, next);
    },
    [history, persistCanvas, setCanvasCache],
  );

  const undo = useCallback((): CanvasKey | null => {
    const entry = history.undo();
    if (!entry) return null;
    setCanvasCache((cur) => {
      const m = new Map(cur);
      m.set(entry.canvasKey, entry.prev);
      return m;
    });
    persistCanvas(entry.canvasKey, entry.prev);
    return entry.canvasKey;
  }, [history, persistCanvas, setCanvasCache]);

  const redo = useCallback((): CanvasKey | null => {
    const entry = history.redo();
    if (!entry) return null;
    setCanvasCache((cur) => {
      const m = new Map(cur);
      m.set(entry.canvasKey, entry.next);
      return m;
    });
    persistCanvas(entry.canvasKey, entry.next);
    return entry.canvasKey;
  }, [history, persistCanvas, setCanvasCache]);

  return { saveState, pendingWrites, applyEdit, undo, redo };
}
