/**
 * v0.24.14 (D-2026-05-21-C) — read-only "view at git tag" snapshot mode.
 *
 * When ``viewingTag`` is set, the app renders ``snapshotCache`` (= the
 * project state at that tag, fetched via the ``/at-tag/{tag}`` endpoint)
 * instead of the live cache. Edits are blocked at the App boundary;
 * this hook owns only the snapshot state machine + entry/exit actions.
 */
import { useCallback, useState } from "react";
import { getProjectAtTag } from "../api";
import type { CanvasDoc, CanvasKey } from "../types";

export interface UseSnapshotViewApi {
  /** Non-null when in snapshot mode; the user-visible tag name. */
  viewingTag: string | null;
  /** Canvas data at the viewed tag. Empty when not viewing. */
  snapshotCache: Map<CanvasKey, CanvasDoc>;
  enterTagView: (tag: string) => Promise<void>;
  exitTagView: () => void;
}

export function useSnapshotView(
  projectPath: string | null,
  activeId: string | null,
  onError: (msg: string) => void,
): UseSnapshotViewApi {
  const [viewingTag, setViewingTag] = useState<string | null>(null);
  const [snapshotCache, setSnapshotCache] = useState<Map<CanvasKey, CanvasDoc>>(
    () => new Map(),
  );

  const enterTagView = useCallback(
    async (tag: string) => {
      if (!projectPath || !activeId) return;
      try {
        const resp = await getProjectAtTag(projectPath, activeId, tag);
        const next = new Map<CanvasKey, CanvasDoc>();
        for (const [key, doc] of Object.entries(resp.canvases)) {
          next.set(key as CanvasKey, doc);
        }
        setSnapshotCache(next);
        setViewingTag(tag);
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [projectPath, activeId, onError],
  );

  const exitTagView = useCallback(() => {
    setViewingTag(null);
    setSnapshotCache(new Map());
  }, []);

  return { viewingTag, snapshotCache, enterTagView, exitTagView };
}
