/**
 * Stable post-project callback handlers — v0.16.16 (D-2026-05-12-R).
 *
 * App.tsx wires ``useCanvasPersist`` + ``useProjectSocket`` with
 * callbacks that depend on ``useProject`` 's output (``loadList``,
 * ``setCanvasCache``, ``setTags``). Before this hook, those callbacks
 * were inline arrow functions recreated every render. The downstream
 * hooks defensively stored them in refs, but the cascade of identity
 * changes still rebuilt ``loadList`` / ``persistCanvas`` etc., which
 * under specific WS event timings caused a refetch storm.
 *
 * This hook returns a stable bundle of callbacks via ``useCallback``,
 * so the downstream hooks' dependency arrays stay stable across
 * App renders.
 *
 * Note: ``onError`` and ``onActiveIdChange`` for ``useProject`` itself
 * are NOT in here — those are needed BEFORE useProject is called,
 * so App.tsx inlines them via direct ``useCallback`` near the top.
 */
import { useCallback } from "react";
import type { CanvasDoc, CanvasKey, ProjectTag } from "../types";

export interface PostProjectHandlerDeps {
  setCanvasCache: React.Dispatch<
    React.SetStateAction<Map<CanvasKey, CanvasDoc>>
  >;
  setTags: React.Dispatch<React.SetStateAction<ProjectTag[]>>;
  loadList: () => Promise<unknown>;
  historyClear: () => void;
}

export interface PostProjectHandlers {
  handleListStale: () => void;
  handleExternalCanvas: (key: CanvasKey, fresh: CanvasDoc) => void;
  handleTagsRefresh: (nextTags: ProjectTag[]) => void;
  handleExternalChange: () => void;
}

export function useStableHandlers(
  deps: PostProjectHandlerDeps,
): PostProjectHandlers {
  const { setCanvasCache, setTags, loadList, historyClear } = deps;
  const handleListStale = useCallback(() => {
    void loadList();
  }, [loadList]);
  const handleExternalCanvas = useCallback(
    (key: CanvasKey, fresh: CanvasDoc) => {
      setCanvasCache((prev) => {
        const next = new Map(prev);
        next.set(key, fresh);
        return next;
      });
    },
    [setCanvasCache],
  );
  const handleTagsRefresh = useCallback(
    (nextTags: ProjectTag[]) => setTags(nextTags),
    [setTags],
  );
  const handleExternalChange = useCallback(
    () => historyClear(),
    [historyClear],
  );
  return {
    handleListStale,
    handleExternalCanvas,
    handleTagsRefresh,
    handleExternalChange,
  };
}
