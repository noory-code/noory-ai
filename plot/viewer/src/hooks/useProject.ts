import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
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

/** The active project's canvases + its metadata — one TanStack Query entry
 *  per [path, id] (D-2026-06-08-A, step 6). */
interface CanvasesData {
  canvases: Map<CanvasKey, CanvasDoc>;
  /** Full project read (includes ``tags`` + ``service_details``, which the
   *  ``ProjectDoc`` summary type omits). */
  project: Awaited<ReturnType<typeof getProject>>;
}

const EMPTY_CANVAS_CACHE: Map<CanvasKey, CanvasDoc> = new Map();

function canvasesQueryKey(path: string | null, id: string | null) {
  return ["canvases", path, id] as const;
}

/**
 * Owns everything project-scoped: the sidebar list, the currently open
 * project's metadata, the canvas cache, the tag list, and the actions
 * that mutate any of them.
 *
 * v0.51 (D-2026-06-08-A, step 6): the canvas cache now lives in a TanStack
 * Query (``["canvases", path, id]``) instead of ``useState`` — above the
 * ``api.ts`` engine seam, so a future in-process engine swaps the transport
 * with no cache-layer change. ``setCanvasCache`` is preserved as a setter
 * backed by ``queryClient.setQueryData`` so every mutation call site
 * (useCanvasPersist edits / undo / redo, useProjectSocket external changes,
 * publish/unpublish) is unchanged. The WebSocket still drives external-change
 * refresh, so the query is ``staleTime: Infinity`` (no background refetch).
 *
 * The hook does NOT touch the URL — the App wires ``onActiveIdChange`` to
 * ``?project=`` so the concern stays at the view layer.
 */
export function useProject(args: UseProjectArgs): UseProjectApi {
  const { workspaceRoot, history, onActiveIdChange, initialActiveId, onError } = args;
  const { t } = useTranslation();
  const dialog = useDialog();
  const queryClient = useQueryClient();

  const [summaries, setSummaries] = useState<ProjectDoc[]>([]);
  // ``dirMap`` (state) drives reactive render (sidebar labels +
  // ``activeProjectPath`` memo). ``dirMapRef`` mirrors it synchronously so
  // imperative actions that run right after ``loadList`` (e.g. the initial
  // open) read the freshest dir before the state re-render lands.
  const [dirMap, setDirMap] = useState<Map<string, string>>(() => new Map());
  const dirMapRef = useRef<Map<string, string>>(new Map());
  const [migratedToast, setMigratedToast] = useState<string[] | null>(null);
  const [tags, setTags] = useState<ProjectTag[]>([]);
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

  // --- canvas cache as a TanStack Query (step 6) ------------------------
  // Keyed on the effective path + id; switching project changes the key and
  // loads that project's canvases. The query fetches the project metadata
  // (for service_details) + all canvases together.
  const canvasesQuery = useQuery<CanvasesData>({
    queryKey: canvasesQueryKey(activeProjectPath, activeId),
    enabled: !!activeProjectPath && !!activeId,
    staleTime: Infinity,
    queryFn: async () => {
      const path = activeProjectPath as string;
      const id = activeId as string;
      const project = await getProject(path, id);
      const canvases = await getAllCanvases(path, id, project.service_details);
      return { canvases, project };
    },
  });
  const canvasCache = canvasesQuery.data?.canvases ?? EMPTY_CANVAS_CACHE;

  // Mutation seam: every edit / undo / WS-refresh / publish writes through
  // here. Backed by the query cache so the same ``setCanvasCache`` API the
  // other hooks already use keeps working unchanged.
  const activeProjectPathRef = useRef(activeProjectPath);
  activeProjectPathRef.current = activeProjectPath;
  const activeIdRef = useRef(activeId);
  activeIdRef.current = activeId;
  const setCanvasCache = useCallback<
    React.Dispatch<React.SetStateAction<Map<CanvasKey, CanvasDoc>>>
  >(
    (updater) => {
      queryClient.setQueryData<CanvasesData>(
        canvasesQueryKey(activeProjectPathRef.current, activeIdRef.current),
        (prev) => {
          if (!prev) return prev; // nothing loaded yet — ignore stray writes
          const next =
            typeof updater === "function"
              ? (updater as (m: Map<CanvasKey, CanvasDoc>) => Map<CanvasKey, CanvasDoc>)(
                  prev.canvases,
                )
              : updater;
          return { ...prev, canvases: next };
        },
      );
    },
    [queryClient],
  );

  // Sync the open project's metadata + reset undo ONLY when the project
  // identity changes (a switch / fresh load) — not on every canvas edit
  // (those keep the same project, so optimistic setTags / setServiceDetails
  // are not clobbered). Mirrors the old ``openProject`` side effects.
  const syncedProjectRef = useRef<string | null>(null);
  useEffect(() => {
    const data = canvasesQuery.data;
    if (data && syncedProjectRef.current !== data.project.id) {
      syncedProjectRef.current = data.project.id;
      setTags(data.project.tags);
      setServiceDetails(data.project.service_details);
      history.init();
    }
  }, [canvasesQuery.data, history]);

  // Derive phase from the list + the canvas query (replaces the imperative
  // setPhase calls scattered through the old openProject flow).
  useEffect(() => {
    if (!workspaceRoot) {
      setPhase("loading");
      return;
    }
    if (canvasesQuery.isError) {
      setPhase("error");
      return;
    }
    if (activeId && canvasesQuery.isSuccess) {
      setPhase("ready");
      return;
    }
    if (activeId) {
      setPhase("loading");
    }
  }, [workspaceRoot, activeId, canvasesQuery.isError, canvasesQuery.isSuccess]);

  // Surface a fetch error through the App's error channel too.
  useEffect(() => {
    if (canvasesQuery.error) {
      const e = canvasesQuery.error;
      onError(e instanceof Error ? e.message : String(e));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canvasesQuery.error]);

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

  // Opening a project now just makes it active — the canvas query fetches
  // (and the metadata-sync effect resets tags / undo) when the key changes.
  const openProject = useCallback(
    async (projectId: string) => {
      if (!pathFor(projectId)) return;
      setActiveId(projectId);
    },
    [pathFor, setActiveId],
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
        return;
      }
      // v0.36.0 (D-2026-05-31-Y) — ask for the project name instead of
      // silently creating "Untitled". Cancelling the prompt aborts creation.
      const name = await dialog.prompt({
        message: t("sidebar.newProjectNamePrompt"),
        placeholder: t("sidebar.newProjectNamePlaceholder"),
      });
      if (name === null) return;
      try {
        const id = `proj-${Date.now().toString(36)}`;
        const targetPath = joinWorkspaceDir(workspaceRoot, targetDir);
        const created = await createProject(targetPath, id, name.trim() || "Untitled");
        await loadList(); // rebuilds dirMapRef incl. created.id → targetDir
        setActiveId(created.id);
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [workspaceRoot, summaries, loadList, onError, setActiveId, dialog, t],
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
          }
        }
      } catch (err) {
        onError(err instanceof Error ? err.message : String(err));
      }
    },
    [pathFor, loadList, activeId, onError, setActiveId],
  );

  const pick = useCallback(
    (id: string) => {
      setActiveId(id);
    },
    [setActiveId],
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
    [pathFor, activeId, onError, setCanvasCache],
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
    [pathFor, activeId, onError, setCanvasCache],
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
