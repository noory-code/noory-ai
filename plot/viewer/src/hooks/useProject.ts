import { useCallback, useEffect, useState } from "react";
import {
  createProject,
  deleteProject,
  deleteProjectTag,
  getAllCanvases,
  getProject,
  listProjects,
  publishNode,
  unpublishNode,
  renameProject,
  tagProject,
} from "../api";
import type { ProjectHistoryApi } from "../canvases/useProjectHistory";
import type {
  CanvasDoc,
  CanvasKey,
  ProjectDoc,
  ProjectTag,
} from "../types";

export type ProjectPhase = "loading" | "no-projects" | "ready" | "error";

export interface UseProjectArgs {
  projectPath: string | null;
  history: ProjectHistoryApi;
  /** URL state is owned by the App; the hook hands it the chosen id
   *  whenever the open project changes so the shell can sync ``?project=``. */
  onActiveIdChange: (id: string | null) => void;
  /** Initial ``activeId`` read from the URL on mount. */
  initialActiveId?: string | null;
  onError: (err: string) => void;
}

export interface UseProjectApi {
  // state
  summaries: ProjectDoc[];
  activeId: string | null;
  canvasCache: Map<CanvasKey, CanvasDoc>;
  tags: ProjectTag[];
  migratedToast: string[] | null;
  phase: ProjectPhase;
  // setters — other hooks write through these
  setCanvasCache: React.Dispatch<
    React.SetStateAction<Map<CanvasKey, CanvasDoc>>
  >;
  setServiceDetails: React.Dispatch<React.SetStateAction<string[]>>;
  setTags: React.Dispatch<React.SetStateAction<ProjectTag[]>>;
  // actions
  loadList: () => Promise<ProjectDoc[] | null>;
  openProject: (id: string) => Promise<void>;
  create: () => Promise<void>;
  rename: (id: string, name: string) => Promise<void>;
  remove: (id: string) => Promise<void>;
  pick: (id: string) => void;
  markSession: () => Promise<void>;
  /** v0.18.0 Phase 3 (D-2026-05-16-E) — publish a node. Re-reads the
   *  canvas after the server-side bump so the Inspector reflects the
   *  new version on next paint. */
  publishNodeAction: (
    canvasKey: CanvasKey,
    nodeId: string,
  ) => Promise<void>;
  /** v0.23.x (D-2026-05-17-J) — unpublish via git revert. */
  unpublishNodeAction: (
    canvasKey: CanvasKey,
    nodeId: string,
  ) => Promise<void>;
  deleteTag: (name: string) => Promise<void>;
  dismissToast: () => void;
  /** v0.13 Phase 0: replace one summary in place (used by anchor PATCH). */
  replaceSummary: (next: ProjectDoc) => void;
}

/**
 * Owns everything project-scoped: the sidebar list, the currently open
 * project's metadata, the canvas cache, the tag list, and the actions
 * that mutate any of them.
 *
 * The hook does NOT touch the URL — the App wires ``onActiveIdChange``
 * to ``?project=`` so the concern stays at the view layer.
 */
export function useProject(args: UseProjectArgs): UseProjectApi {
  const { projectPath, history, onActiveIdChange, initialActiveId, onError } = args;

  const [summaries, setSummaries] = useState<ProjectDoc[]>([]);
  const [migratedToast, setMigratedToast] = useState<string[] | null>(null);
  const [tags, setTags] = useState<ProjectTag[]>([]);
  const [canvasCache, setCanvasCache] = useState<Map<CanvasKey, CanvasDoc>>(
    () => new Map(),
  );
  const [, setServiceDetails] = useState<string[]>([]);
  const [activeId, _setActiveId] = useState<string | null>(initialActiveId ?? null);
  const [phase, setPhase] = useState<ProjectPhase>("loading");

  const setActiveId = useCallback(
    (id: string | null) => {
      _setActiveId(id);
      onActiveIdChange(id);
    },
    [onActiveIdChange],
  );

  const loadList = useCallback(async (): Promise<ProjectDoc[] | null> => {
    if (!projectPath) return null;
    try {
      const { projects, migrated } = await listProjects(projectPath);
      setSummaries(projects);
      if (migrated.length > 0) setMigratedToast(migrated);
      return projects;
    } catch (err) {
      onError(err instanceof Error ? err.message : String(err));
      setPhase("error");
      return null;
    }
  }, [projectPath, onError]);

  const openProject = useCallback(
    async (projectId: string) => {
      if (!projectPath) return;
      try {
        const proj = await getProject(projectPath, projectId);
        setServiceDetails(proj.service_details);
        setTags(proj.tags);
        const cache = await getAllCanvases(
          projectPath,
          projectId,
          proj.service_details,
        );
        setCanvasCache(cache);
        history.init();
        setPhase("ready");
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
        setPhase("error");
      }
    },
    [projectPath, history, onError],
  );

  // Initial list + open.
  useEffect(() => {
    if (!projectPath) return;
    void (async () => {
      const list = await loadList();
      if (!list || list.length === 0) {
        setPhase("no-projects");
        return;
      }
      const chosen =
        (activeId && list.find((p) => p.id === activeId)?.id) ?? list[0].id;
      setActiveId(chosen);
      void openProject(chosen);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectPath]);

  const create = useCallback(async () => {
    if (!projectPath) return;
    try {
      const id = `proj-${Date.now().toString(36)}`;
      const created = await createProject(projectPath, id, "Untitled");
      setActiveId(created.id);
      await loadList();
      await openProject(created.id);
    } catch (err) {
      onError(err instanceof Error ? err.message : String(err));
    }
  }, [projectPath, loadList, openProject, onError, setActiveId]);

  const rename = useCallback(
    async (id: string, name: string) => {
      if (!projectPath) return;
      try {
        await renameProject(projectPath, id, name);
        await loadList();
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [projectPath, loadList, onError],
  );

  const remove = useCallback(
    async (id: string) => {
      if (!projectPath) return;
      try {
        await deleteProject(projectPath, id);
        const list = (await loadList()) ?? [];
        if (activeId === id) {
          if (list.length === 0) {
            setPhase("no-projects");
            setActiveId(null);
          } else {
            setActiveId(list[0].id);
            void openProject(list[0].id);
          }
        }
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [projectPath, loadList, openProject, activeId, onError, setActiveId],
  );

  const pick = useCallback(
    (id: string) => {
      setActiveId(id);
      void openProject(id);
    },
    [openProject, setActiveId],
  );

  const markSession = useCallback(async () => {
    if (!projectPath || !activeId) return;
    const name = window.prompt("Session tag name (e.g. 'session-banas-start')");
    if (!name || !name.trim()) return;
    const message = window.prompt("Optional short message", "") || undefined;
    try {
      await tagProject(projectPath, activeId, name.trim(), message);
      const proj = await getProject(projectPath, activeId);
      setTags(proj.tags);
    } catch (err) {
      onError(err instanceof Error ? err.message : String(err));
    }
  }, [projectPath, activeId, onError]);

  const publishNodeAction = useCallback(
    async (canvasKey: CanvasKey, nodeId: string) => {
      if (!projectPath || !activeId) return;
      const [canvasKind, serviceId] = canvasKey.split(":") as [string, string?];
      try {
        await publishNode(projectPath, activeId, canvasKind, nodeId, serviceId);
        // Re-read the canvas via the existing all-canvases fetch so the
        // Inspector reflects the bumped version + the new MD file on
        // disk is visible to subsequent reads.
        const proj = await getProject(projectPath, activeId);
        const refreshed = await getAllCanvases(
          projectPath,
          activeId,
          proj.service_details,
        );
        setCanvasCache(refreshed);
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [projectPath, activeId, onError],
  );

  // v0.23.x (D-2026-05-17-J) — unpublish action mirrors publishNodeAction
  // (same refresh flow).
  const unpublishNodeAction = useCallback(
    async (canvasKey: CanvasKey, nodeId: string) => {
      if (!projectPath || !activeId) return;
      const [canvasKind, serviceId] = canvasKey.split(":") as [string, string?];
      try {
        await unpublishNode(projectPath, activeId, canvasKind, nodeId, serviceId);
        const proj = await getProject(projectPath, activeId);
        const refreshed = await getAllCanvases(
          projectPath,
          activeId,
          proj.service_details,
        );
        setCanvasCache(refreshed);
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [projectPath, activeId, onError],
  );

  const deleteTag = useCallback(
    async (name: string) => {
      if (!projectPath || !activeId) return;
      try {
        await deleteProjectTag(projectPath, activeId, name);
        const proj = await getProject(projectPath, activeId);
        setTags(proj.tags);
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [projectPath, activeId, onError],
  );

  const dismissToast = useCallback(() => setMigratedToast(null), []);

  const replaceSummary = useCallback((next: ProjectDoc) => {
    setSummaries((prev) => prev.map((p) => (p.id === next.id ? next : p)));
  }, []);

  return {
    summaries,
    activeId,
    canvasCache,
    tags,
    migratedToast,
    phase,
    setCanvasCache,
    setServiceDetails,
    setTags,
    loadList,
    openProject,
    create,
    rename,
    remove,
    pick,
    markSession,
    publishNodeAction,
    unpublishNodeAction,
    deleteTag,
    dismissToast,
    replaceSummary,
  };
}
