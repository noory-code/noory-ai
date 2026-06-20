import { useCallback, useRef, useState } from "react";
import { getCanvas, putCanvas } from "../api";
import { createEchoGuard, type EchoGuard } from "../lib/echoGuard";
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
  /** Track which feature canvases the server says exist right now. */
  setFeatureDetails: React.Dispatch<React.SetStateAction<string[]>>;
  /** After a successful PUT the sidebar's ``updated`` stamp changes. */
  onListStale: () => void;
  onError: (err: string) => void;
}

export interface UseCanvasPersistApi {
  saveState: SaveState;
  /** Shared with ``useProjectSocket`` so the WS layer can skip self-echoes.
   *  Counts in-flight writes per key with a TTL + error path (D-2026-06-08-A,
   *  step 3) — replaces the leak-prone `Set<CanvasKey>`. */
  echoGuard: React.MutableRefObject<EchoGuard>;
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
    setFeatureDetails,
    onListStale,
    onError,
  } = args;

  const [saveState, setSaveState] = useState<SaveState>("idle");
  const saveTimer = useRef<number | null>(null);
  const savedTimer = useRef<number | null>(null);
  const echoGuard = useRef(createEchoGuard());

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
      setSaveState("saving");
      if (saveTimer.current !== null) window.clearTimeout(saveTimer.current);
      saveTimer.current = window.setTimeout(() => {
        saveTimer.current = null;
        // Expect the server's self-echo for THIS write. Debounce collapses a
        // rapid edit burst into one PUT → one expect → one echo. Expecting at
        // send-time (not schedule-time) avoids counting a debounced-away edit.
        // (D-2026-06-08-A step 3)
        echoGuard.current.expect(key);
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
            // v0.27.14 (D-2026-05-28-I) — surface protected details.
            // The server refused to archive these because they carried
            // user-authored content; warn so the user can intervene.
            const skipped = res.sync.skipped_archive ?? [];
            if (skipped.length > 0) {
              console.warn(
                "[plot] sync skipped archive for services with user-authored detail content; restore the service in the overview or delete the detail explicitly:",
                skipped,
              );
              onErrorRef.current(
                `Detail for ${skipped.length === 1 ? "1 service" : `${skipped.length} services`} preserved (user content present): ${skipped.join(", ")}`,
              );
            }
            // Reconcile Overview ↔ Detail sync the server reports.
            if (res.sync.created.length || res.sync.archived.length) {
              setFeatureDetails((prev) => {
                const s = new Set(prev);
                for (const n of res.sync.created) s.add(n);
                for (const n of res.sync.archived) s.delete(n);
                return Array.from(s).sort();
              });
              if (res.sync.created.length) {
                void (async () => {
                  for (const sid of res.sync.created) {
                    try {
                      const d = await getCanvas(pp, pid, "feature", sid);
                      setCanvasCache((prev) => {
                        const next = new Map(prev);
                        next.set(`feature:${sid}`, d);
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
                    next.delete(`feature:${sid}`);
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
            // No echo will arrive for a failed write — retire its pending slot
            // so a later external change to this key isn't suppressed.
            echoGuard.current.fail(key);
            setSaveState("error");
            onErrorRef.current(err instanceof Error ? err.message : String(err));
          });
      }, DEBOUNCE_MS);
    },
    [setCanvasCache, setFeatureDetails],
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

  return { saveState, echoGuard, applyEdit, undo, redo };
}
