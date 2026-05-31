import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  type BlueprintBump,
  createProject,
  deleteProject,
  deleteProjectTag,
  discoverWorkspace,
  getAllCanvases,
  getProject,
  publishNode,
  publishProject,
  unpublishNode,
  renameProject,
  tagProject,
} from "../api";
import { joinWorkspaceDir } from "../lib/projectPath";
import { useDialog } from "../shell/dialog/DialogProvider";
import type { ProjectHistoryApi } from "../canvases/useProjectHistory";
import type {
  CanvasDoc,
  CanvasKey,
  ProjectDoc,
  ProjectTag,
} from "../types";

export type ProjectPhase = "loading" | "no-projects" | "ready" | "error";

export interface UseProjectArgs {
  /** Workspace ROOT (the launch ``?project_path=``). Per-project I/O uses
   *  the effective path = root + the project's dir (D-2026-05-31-M). */
  workspaceRoot: string | null;
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
  /** Effective ``project_path`` for the active project (root + its dir),
   *  or the workspace root when no project is active. Per-project consumers
   *  (persist / socket / canvas) thread this. */
  activeProjectPath: string | null;
  /** The active project's dir relative to the workspace root ("." = root). */
  dirForId: (id: string) => string;
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
  /** Add a project in ``targetDir`` (relative to the workspace root; "." =
   *  root). If that dir already holds a project, land in the most-recent one
   *  instead of creating a duplicate (D-2026-05-31-N). */
  create: (targetDir: string) => Promise<void>;
  rename: (id: string, name: string) => Promise<void>;
  remove: (id: string) => Promise<void>;
  pick: (id: string) => void;
  markSession: () => Promise<void>;
  /** v0.24.13 (D-2026-05-21-B) — bump project blueprint semver +
   *  create a git tag at the new version name. */
  publishBlueprint: (bump: BlueprintBump) => Promise<void>;
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
  const { workspaceRoot, history, onActiveIdChange, initialActiveId, onError } = args;
  const { t } = useTranslation();
  const dialog = useDialog();

  const [summaries, setSummaries] = useState<ProjectDoc[]>([]);
  // ``dirMap`` (state) drives reactive render (sidebar labels +
  // ``activeProjectPath`` memo). ``dirMapRef`` mirrors it synchronously so
  // imperative actions that run right after ``loadList`` (e.g. the initial
  // open) read the freshest dir before the state re-render lands.
  const [dirMap, setDirMap] = useState<Map<string, string>>(() => new Map());
  const dirMapRef = useRef<Map<string, string>>(new Map());
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

  // A project's dir relative to the workspace root ("." = root-level).
  // Reads state so the sidebar re-renders when discovery updates it.
  const dirForId = useCallback((id: string) => dirMap.get(id) ?? ".", [dirMap]);

  // Effective server ``project_path`` for a given project = root + its dir.
  // Reads the ref (synchronous) so an action firing immediately after
  // ``loadList`` uses the freshest dir, not the pre-render empty map.
  const pathFor = useCallback(
    (id: string): string | null =>
      workspaceRoot == null
        ? null
        : joinWorkspaceDir(workspaceRoot, dirMapRef.current.get(id) ?? "."),
    [workspaceRoot],
  );

  const activeProjectPath = useMemo(
    () => (activeId ? pathFor(activeId) : workspaceRoot),
    [activeId, pathFor, workspaceRoot],
  );

  const loadList = useCallback(async (): Promise<ProjectDoc[] | null> => {
    if (!workspaceRoot) return null;
    try {
      const { projects, migrated } = await discoverWorkspace(workspaceRoot);
      const map = new Map(projects.map((d) => [d.project.id, d.dir]));
      dirMapRef.current = map;
      setSummaries(projects.map((d) => d.project));
      setDirMap(map);
      if (migrated.length > 0) setMigratedToast(migrated);
      return projects.map((d) => d.project);
    } catch (err) {
      onError(err instanceof Error ? err.message : String(err));
      setPhase("error");
      return null;
    }
  }, [workspaceRoot, onError]);

  const openProject = useCallback(
    async (projectId: string) => {
      const path = pathFor(projectId);
      if (!path) return;
      try {
        const proj = await getProject(path, projectId);
        setServiceDetails(proj.service_details);
        setTags(proj.tags);
        const cache = await getAllCanvases(path, projectId, proj.service_details);
        setCanvasCache(cache);
        history.init();
        setPhase("ready");
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
        setPhase("error");
      }
    },
    [pathFor, history, onError],
  );

  // Initial list + open.
  useEffect(() => {
    if (!workspaceRoot) return;
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
  }, [workspaceRoot]);

  const create = useCallback(
    async (targetDir: string) => {
      if (!workspaceRoot) return;
      // Land in an existing project if the chosen dir already has one
      // (summaries are newest-first, so the first match is most-recent).
      const existing = summaries.find(
        (p) => (dirMapRef.current.get(p.id) ?? ".") === targetDir,
      );
      if (existing) {
        setActiveId(existing.id);
        void openProject(existing.id);
        return;
      }
      try {
        const id = `proj-${Date.now().toString(36)}`;
        const targetPath = joinWorkspaceDir(workspaceRoot, targetDir);
        const created = await createProject(targetPath, id, "Untitled");
        setActiveId(created.id);
        await loadList(); // rebuilds dirMapRef incl. created.id → targetDir
        await openProject(created.id);
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [workspaceRoot, summaries, loadList, openProject, onError, setActiveId],
  );

  const rename = useCallback(
    async (id: string, name: string) => {
      const path = pathFor(id);
      if (!path) return;
      try {
        await renameProject(path, id, name);
        await loadList();
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [pathFor, loadList, onError],
  );

  const remove = useCallback(
    async (id: string) => {
      const path = pathFor(id);
      if (!path) return;
      try {
        await deleteProject(path, id);
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
    [pathFor, loadList, openProject, activeId, onError, setActiveId],
  );

  const pick = useCallback(
    (id: string) => {
      setActiveId(id);
      void openProject(id);
    },
    [openProject, setActiveId],
  );

  const publishBlueprint = useCallback(
    async (bump: BlueprintBump) => {
      const path = activeId ? pathFor(activeId) : null;
      if (!path || !activeId) return;
      try {
        await publishProject(path, activeId, bump);
        // Refresh summaries (blueprint_version) and tags.
        const proj = await getProject(path, activeId);
        setSummaries((prev) =>
          prev.map((p) =>
            p.id === activeId
              ? { ...p, blueprint_version: proj.blueprint_version }
              : p,
          ),
        );
        setTags(proj.tags);
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [pathFor, activeId, onError],
  );

  const markSession = useCallback(async () => {
    const path = activeId ? pathFor(activeId) : null;
    if (!path || !activeId) return;
    const name = await dialog.prompt({ message: t("snapshot.tagNamePrompt") });
    if (!name || !name.trim()) return;
    const message =
      (await dialog.prompt({ message: t("snapshot.tagMessagePrompt"), defaultValue: "" })) ||
      undefined;
    try {
      await tagProject(path, activeId, name.trim(), message);
      const proj = await getProject(path, activeId);
      setTags(proj.tags);
    } catch (err) {
      onError(err instanceof Error ? err.message : String(err));
    }
  }, [pathFor, activeId, onError, dialog, t]);

  const publishNodeAction = useCallback(
    async (canvasKey: CanvasKey, nodeId: string) => {
      const path = activeId ? pathFor(activeId) : null;
      if (!path || !activeId) return;
      const [canvasKind, serviceId] = canvasKey.split(":") as [string, string?];
      try {
        await publishNode(path, activeId, canvasKind, nodeId, serviceId);
        // Re-read the canvas via the existing all-canvases fetch so the
        // Inspector reflects the bumped version + the new MD file on
        // disk is visible to subsequent reads.
        const proj = await getProject(path, activeId);
        const refreshed = await getAllCanvases(path, activeId, proj.service_details);
        setCanvasCache(refreshed);
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [pathFor, activeId, onError],
  );

  // v0.23.x (D-2026-05-17-J) — unpublish action mirrors publishNodeAction
  // (same refresh flow).
  const unpublishNodeAction = useCallback(
    async (canvasKey: CanvasKey, nodeId: string) => {
      const path = activeId ? pathFor(activeId) : null;
      if (!path || !activeId) return;
      const [canvasKind, serviceId] = canvasKey.split(":") as [string, string?];
      try {
        await unpublishNode(path, activeId, canvasKind, nodeId, serviceId);
        const proj = await getProject(path, activeId);
        const refreshed = await getAllCanvases(path, activeId, proj.service_details);
        setCanvasCache(refreshed);
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [pathFor, activeId, onError],
  );

  const deleteTag = useCallback(
    async (name: string) => {
      const path = activeId ? pathFor(activeId) : null;
      if (!path || !activeId) return;
      try {
        await deleteProjectTag(path, activeId, name);
        const proj = await getProject(path, activeId);
        setTags(proj.tags);
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [pathFor, activeId, onError],
  );

  const dismissToast = useCallback(() => setMigratedToast(null), []);

  const replaceSummary = useCallback((next: ProjectDoc) => {
    setSummaries((prev) => prev.map((p) => (p.id === next.id ? next : p)));
  }, []);

  return {
    summaries,
    activeId,
    activeProjectPath,
    dirForId,
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
    publishBlueprint,
    publishNodeAction,
    unpublishNodeAction,
    deleteTag,
    dismissToast,
    replaceSummary,
  };
}
