import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  createProject,
  deleteProject,
  deleteProjectTag,
  getAllCanvases,
  getCanvas,
  getProject,
  listProjects,
  openProjectSocket,
  putCanvas,
  renameProject,
  resolveProjectPath,
  tagProject,
  type SocketStatus,
} from "./api";
import { SketchCanvas } from "./canvases/SketchCanvas";
import { SketchSidebar } from "./canvases/SketchSidebar";
import type { SaveState } from "./canvases/SketchToolbar";
import { useProjectHistory } from "./canvases/useProjectHistory";
import type {
  CanvasDoc,
  CanvasKey,
  CanvasKind,
  ProjectDoc,
  ProjectTag,
  SketchNode,
} from "./types";

type Phase = "loading" | "no-projects" | "ready" | "error";

type CanvasTab = "core" | "actors" | "services";
const CANVAS_TABS: readonly { id: CanvasTab; label: string }[] = [
  { id: "core", label: "Core" },
  { id: "actors", label: "Actors" },
  { id: "services", label: "Services" },
];

function tabToKind(tab: CanvasTab): CanvasKind {
  if (tab === "core") return "core";
  if (tab === "actors") return "actors";
  return "services_overview";
}

function canvasKey(kind: CanvasKind, serviceId?: string | null): CanvasKey {
  if (kind === "service_detail") {
    if (!serviceId) throw new Error("service_detail requires serviceId");
    return `service_detail:${serviceId}`;
  }
  return kind;
}

const DEBOUNCE_MS = 400;

export function App() {
  const projectPath = useMemo(resolveProjectPath, []);
  const [summaries, setSummaries] = useState<ProjectDoc[]>([]);
  const [migratedToast, setMigratedToast] = useState<string[] | null>(null);
  const [tags, setTags] = useState<ProjectTag[]>([]);
  const history = useProjectHistory();

  const [canvasCache, setCanvasCache] = useState<Map<CanvasKey, CanvasDoc>>(
    () => new Map(),
  );
  // Kept in state because persistCanvas updates it when Overview sync
  // creates / archives Detail canvases; the list drives initial cache
  // warm-up and (later) any Detail picker UI.
  const [, setServiceDetails] = useState<string[]>([]);

  const [phase, setPhase] = useState<Phase>("loading");
  const [error, setError] = useState<string | null>(null);
  const [socketStatus, setSocketStatus] = useState<SocketStatus>("connecting");
  const [saveState, setSaveState] = useState<SaveState>("idle");

  const [activeId, setActiveId] = useState<string | null>(() => {
    const url = new URL(window.location.href);
    return url.searchParams.get("project") ?? url.searchParams.get("sketch");
  });
  const [activeTab, setActiveTab] = useState<CanvasTab>(() => {
    const raw = new URL(window.location.href).searchParams.get("canvas");
    return CANVAS_TABS.some((t) => t.id === raw) ? (raw as CanvasTab) : "services";
  });
  const [detailServiceId, setDetailServiceId] = useState<string | null>(() => {
    return new URL(window.location.href).searchParams.get("detail");
  });
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(() => {
    return new URL(window.location.href).searchParams.get("select");
  });

  const saveTimer = useRef<number | null>(null);
  const savedTimer = useRef<number | null>(null);
  // Stays between putCanvas calls; the WebSocket echo ignores our own
  // writes so they don't stomp on in-flight state.
  const pendingWrites = useRef(new Set<CanvasKey>());

  // ------- url sync -------

  const syncUrl = useCallback(
    (updates: Record<string, string | null | undefined>) => {
      const url = new URL(window.location.href);
      for (const [k, v] of Object.entries(updates)) {
        if (v == null || v === "") url.searchParams.delete(k);
        else url.searchParams.set(k, v);
      }
      window.history.replaceState(null, "", url.toString());
    },
    [],
  );

  const selectTab = useCallback(
    (tab: CanvasTab) => {
      setActiveTab(tab);
      setDetailServiceId(null);
      syncUrl({ canvas: tab, detail: null, select: null });
    },
    [syncUrl],
  );

  const drillIntoService = useCallback(
    (serviceId: string) => {
      setActiveTab("services");
      setDetailServiceId(serviceId);
      syncUrl({ canvas: "services", detail: serviceId });
    },
    [syncUrl],
  );

  const backToOverview = useCallback(() => {
    setDetailServiceId(null);
    syncUrl({ detail: null });
  }, [syncUrl]);

  const jumpToActor = useCallback(
    (actorId: string) => {
      setActiveTab("actors");
      setDetailServiceId(null);
      setSelectedNodeId(actorId);
      syncUrl({ canvas: "actors", detail: null, select: actorId });
    },
    [syncUrl],
  );

  const consumeSelection = useCallback(() => {
    setSelectedNodeId(null);
    syncUrl({ select: null });
  }, [syncUrl]);

  // ------- load project list -------

  const loadList = useCallback(async () => {
    if (!projectPath) return null;
    try {
      const { projects, migrated } = await listProjects(projectPath);
      setSummaries(projects);
      if (migrated.length > 0) setMigratedToast(migrated);
      return projects;
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setPhase("error");
      return null;
    }
  }, [projectPath]);

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
        setError(err instanceof Error ? err.message : String(err));
        setPhase("error");
      }
    },
    [projectPath, history],
  );

  // Initial load
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

  // ------- WebSocket -------

  const wsActiveIdRef = useRef<string | null>(activeId);
  wsActiveIdRef.current = activeId;
  const wsSaveStateRef = useRef<SaveState>(saveState);
  wsSaveStateRef.current = saveState;

  useEffect(() => {
    if (!projectPath) return;
    const sock = openProjectSocket(projectPath, {
      onEvent: (msg) => {
        if (msg.event !== "project_changed") return;
        const payload = msg as { project_id?: string; canvas_kind?: CanvasKind; service_id?: string };
        const pid = wsActiveIdRef.current;
        if (!pid) return;
        if (payload.project_id && payload.project_id !== pid) {
          // Different project changed — refresh sidebar only.
          void loadList();
          return;
        }
        // Same project. If this was our own write, skip.
        const key = payload.canvas_kind
          ? canvasKey(payload.canvas_kind, payload.service_id)
          : null;
        if (key && pendingWrites.current.has(key)) {
          pendingWrites.current.delete(key);
          return;
        }
        // External change — clear in-memory history (no stale replay).
        history.clear();
        if (key && projectPath) {
          void (async () => {
            try {
              const fresh = await getCanvas(
                projectPath,
                pid,
                payload.canvas_kind!,
                payload.service_id ?? null,
              );
              setCanvasCache((prev) => {
                const next = new Map(prev);
                next.set(key, fresh);
                return next;
              });
            } catch (err) {
              setError(err instanceof Error ? err.message : String(err));
            }
          })();
        } else {
          // Project-level event — just refresh sidebar + tags.
          void loadList();
          void getProject(projectPath, pid).then((p) => setTags(p.tags));
        }
      },
      onStatus: setSocketStatus,
      onError: (err) => setError(err),
    });
    return () => sock.close();
  }, [projectPath, loadList, history]);

  // ------- persist one canvas (debounced) -------

  const persistCanvas = useCallback(
    (key: CanvasKey, canvas: CanvasDoc) => {
      if (!projectPath || !activeId) return;
      pendingWrites.current.add(key);
      setSaveState("saving");
      if (saveTimer.current !== null) window.clearTimeout(saveTimer.current);
      saveTimer.current = window.setTimeout(() => {
        saveTimer.current = null;
        putCanvas(projectPath, activeId, canvas)
          .then((res) => {
            setSaveState("saved");
            // If the server auto-created / archived Detail canvases, keep
            // our cache + service-detail list in sync.
            if (res.sync.created.length || res.sync.archived.length) {
              setServiceDetails((prev) => {
                const s = new Set(prev);
                for (const n of res.sync.created) s.add(n);
                for (const n of res.sync.archived) s.delete(n);
                return Array.from(s).sort();
              });
              // Fetch any newly-created detail canvases so the cache is ready.
              if (res.sync.created.length && projectPath && activeId) {
                void (async () => {
                  for (const sid of res.sync.created) {
                    try {
                      const d = await getCanvas(
                        projectPath,
                        activeId,
                        "service_detail",
                        sid,
                      );
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
            if (savedTimer.current !== null) window.clearTimeout(savedTimer.current);
            savedTimer.current = window.setTimeout(() => setSaveState("idle"), 1500);
            void loadList();
          })
          .catch((err) => {
            setSaveState("error");
            setError(err instanceof Error ? err.message : String(err));
          });
      }, DEBOUNCE_MS);
    },
    [projectPath, activeId, loadList],
  );

  // ------- canvas edit entry point -------

  const applyEdit = useCallback(
    (key: CanvasKey, prev: CanvasDoc, next: CanvasDoc, opts?: { skipHistory?: boolean }) => {
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
    [history, persistCanvas],
  );

  const handleUndo = useCallback(() => {
    const entry = history.undo();
    if (!entry) return;
    setCanvasCache((cur) => {
      const m = new Map(cur);
      m.set(entry.canvasKey, entry.prev);
      return m;
    });
    persistCanvas(entry.canvasKey, entry.prev);
    // Auto-switch tab to where the reverted edit landed.
    focusCanvas(entry.canvasKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [history, persistCanvas]);

  const handleRedo = useCallback(() => {
    const entry = history.redo();
    if (!entry) return;
    setCanvasCache((cur) => {
      const m = new Map(cur);
      m.set(entry.canvasKey, entry.next);
      return m;
    });
    persistCanvas(entry.canvasKey, entry.next);
    focusCanvas(entry.canvasKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [history, persistCanvas]);

  const focusCanvas = useCallback(
    (key: CanvasKey) => {
      if (key === "core") {
        setActiveTab("core");
        setDetailServiceId(null);
        syncUrl({ canvas: "core", detail: null });
      } else if (key === "actors") {
        setActiveTab("actors");
        setDetailServiceId(null);
        syncUrl({ canvas: "actors", detail: null });
      } else if (key === "services_overview") {
        setActiveTab("services");
        setDetailServiceId(null);
        syncUrl({ canvas: "services", detail: null });
      } else {
        const sid = key.slice("service_detail:".length);
        setActiveTab("services");
        setDetailServiceId(sid);
        syncUrl({ canvas: "services", detail: sid });
      }
    },
    [syncUrl],
  );

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)) {
        return;
      }
      const mod = e.metaKey || e.ctrlKey;
      if (!mod) return;
      if (e.key === "z" && !e.shiftKey) {
        e.preventDefault();
        handleUndo();
      } else if ((e.key === "z" && e.shiftKey) || e.key === "y") {
        e.preventDefault();
        handleRedo();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleUndo, handleRedo]);

  // ------- project CRUD -------

  const handleCreate = useCallback(async () => {
    if (!projectPath) return;
    try {
      const id = `proj-${Date.now().toString(36)}`;
      const created = await createProject(projectPath, id, "Untitled");
      setActiveId(created.id);
      await loadList();
      await openProject(created.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [projectPath, loadList, openProject]);

  const handleRename = useCallback(
    async (id: string, name: string) => {
      if (!projectPath) return;
      try {
        await renameProject(projectPath, id, name);
        await loadList();
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      }
    },
    [projectPath, loadList],
  );

  const handleDelete = useCallback(
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
        setError(err instanceof Error ? err.message : String(err));
      }
    },
    [projectPath, loadList, activeId, openProject],
  );

  const handlePick = useCallback(
    (id: string) => {
      setActiveId(id);
      syncUrl({ project: id, sketch: null });
      void openProject(id);
    },
    [openProject, syncUrl],
  );

  // ------- tag actions -------

  const handleMarkSession = useCallback(async () => {
    if (!projectPath || !activeId) return;
    const name = window.prompt("Session tag name (e.g. 'session-banas-start')");
    if (!name || !name.trim()) return;
    const message = window.prompt("Optional short message", "") || undefined;
    try {
      await tagProject(projectPath, activeId, name.trim(), message);
      const proj = await getProject(projectPath, activeId);
      setTags(proj.tags);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [projectPath, activeId]);

  const handleDeleteTag = useCallback(
    async (name: string) => {
      if (!projectPath || !activeId) return;
      try {
        await deleteProjectTag(projectPath, activeId, name);
        const proj = await getProject(projectPath, activeId);
        setTags(proj.tags);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      }
    },
    [projectPath, activeId],
  );

  // ------- current canvas selection -------

  const activeCanvasKey: CanvasKey = useMemo(() => {
    if (activeTab === "services" && detailServiceId) {
      return `service_detail:${detailServiceId}` as CanvasKey;
    }
    const kind = tabToKind(activeTab);
    return kind as CanvasKey;
  }, [activeTab, detailServiceId]);

  const activeCanvas = canvasCache.get(activeCanvasKey) ?? null;

  // actors canvas provides the orphan check list + picker source
  const actorsCanvas = canvasCache.get("actors");
  const availableActors: SketchNode[] = useMemo(() => {
    if (!actorsCanvas) return [];
    return actorsCanvas.nodes.filter((n) => n.kind === "actor");
  }, [actorsCanvas]);

  // ------- download / upload -------

  const handleDownload = useCallback(() => {
    if (!activeCanvas) return;
    const blob = new Blob([JSON.stringify(activeCanvas, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${activeCanvas.canvas_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [activeCanvas]);

  const handleUpload = useCallback(() => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "application/json,.json";
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file || !activeCanvas) return;
      try {
        const text = await file.text();
        const incoming = JSON.parse(text) as CanvasDoc;
        if (!Array.isArray(incoming.nodes) || !Array.isArray(incoming.edges)) {
          setError("Invalid canvas file");
          return;
        }
        const next: CanvasDoc = {
          ...incoming,
          canvas_id: activeCanvas.canvas_id,
          canvas_kind: activeCanvas.canvas_kind,
          service_ref: activeCanvas.service_ref,
        };
        applyEdit(activeCanvasKey, activeCanvas, next);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      }
    };
    input.click();
  }, [activeCanvas, activeCanvasKey, applyEdit]);

  if (!projectPath) {
    return (
      <div className="flex h-full items-center justify-center p-8 text-center">
        <div>
          <h1 className="mb-2 text-2xl font-semibold">Plot</h1>
          <p className="text-slate-500">
            Add <code>?project_path=/absolute/path/to/project</code> to the URL.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <Header
        projectPath={projectPath}
        error={error}
        socketStatus={socketStatus}
        projectName={summaries.find((p) => p.id === activeId)?.name ?? null}
        onDismissToast={() => setMigratedToast(null)}
        migratedToast={migratedToast}
      />
      <div className="flex flex-1 overflow-hidden">
        <SketchSidebar
          projects={summaries}
          activeId={activeId}
          stencilCanvas={activeTab}
          tags={tags}
          onPick={handlePick}
          onCreate={handleCreate}
          onRename={handleRename}
          onDelete={handleDelete}
          onDeleteTag={handleDeleteTag}
        />
        <main className="flex flex-1 flex-col overflow-hidden">
          {phase === "ready" && (
            <CanvasTabs
              active={activeTab}
              onSelect={selectTab}
              onMarkSession={handleMarkSession}
            />
          )}
          {phase === "ready" && activeTab === "services" && detailServiceId && (
            <ServicesBreadcrumb
              label={
                canvasCache
                  .get("services_overview")
                  ?.nodes.find((n) => n.id === detailServiceId)?.label ??
                detailServiceId
              }
              onBack={backToOverview}
            />
          )}
          <div className="flex-1 overflow-hidden">
            {phase === "loading" && <Loading />}
            {phase === "error" && <ErrorPanel message={error ?? "unknown"} />}
            {phase === "no-projects" && <EmptyState onCreate={handleCreate} />}
            {phase === "ready" && activeCanvas && activeId && (
              <SketchCanvas
                key={`${activeId}:${activeCanvasKey}`}
                doc={asSketchDoc(activeCanvas)}
                onDocChange={(next) => {
                  const canvasNext: CanvasDoc = {
                    ...activeCanvas,
                    nodes: next.nodes,
                    edges: next.edges,
                  };
                  applyEdit(activeCanvasKey, activeCanvas, canvasNext);
                }}
                onUndo={handleUndo}
                onRedo={handleRedo}
                canUndo={history.canUndo}
                canRedo={history.canRedo}
                saveState={saveState}
                onDownload={handleDownload}
                onUpload={handleUpload}
                availableActors={availableActors}
                selectNodeId={selectedNodeId}
                onSelectionConsumed={consumeSelection}
                onNodeDrill={(id) => {
                  const n = activeCanvas.nodes.find((x) => x.id === id);
                  if (!n) return;
                  if (n.kind === "actor_ref" && n.ref_actor_id) {
                    jumpToActor(n.ref_actor_id);
                    return;
                  }
                  if (
                    activeTab === "services" &&
                    !detailServiceId &&
                    n.kind === "service" &&
                    !n.is_root
                  ) {
                    drillIntoService(id);
                  }
                }}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

/**
 * Legacy SketchCanvas expects a ``SketchDoc`` shape. We adapt by
 * synthesising one on the fly — the canvas only reads id/name/version
 * metadata and the nodes/edges arrays.
 */
function asSketchDoc(c: CanvasDoc): import("./types").SketchDoc {
  return {
    id: c.canvas_id,
    name: c.canvas_id,
    created: "",
    updated: "",
    version: 2,
    nodes: c.nodes,
    edges: c.edges,
  };
}

// ---------------------------------------------------------------------------
// Small UI bits
// ---------------------------------------------------------------------------

function CanvasTabs({
  active,
  onSelect,
  onMarkSession,
}: {
  active: CanvasTab;
  onSelect: (tab: CanvasTab) => void;
  onMarkSession: () => void;
}) {
  return (
    <div
      role="tablist"
      aria-label="Canvas"
      className="flex items-center justify-between border-b border-slate-200 bg-white px-3"
    >
      <div className="flex items-center gap-1">
        {CANVAS_TABS.map((tab) => {
          const selected = tab.id === active;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={selected}
              onClick={() => onSelect(tab.id)}
              className={
                selected
                  ? "border-b-2 border-slate-900 px-4 py-2 text-sm font-medium text-slate-900"
                  : "border-b-2 border-transparent px-4 py-2 text-sm text-slate-500 hover:text-slate-800"
              }
            >
              {tab.label}
            </button>
          );
        })}
      </div>
      <button
        type="button"
        onClick={onMarkSession}
        className="rounded border border-slate-300 bg-white px-3 py-1 text-xs text-slate-700 hover:bg-slate-50"
        title="Plant a git tag at the current state of the project"
      >
        Mark session…
      </button>
    </div>
  );
}

function ServicesBreadcrumb({
  label,
  onBack,
}: {
  label: string;
  onBack: () => void;
}) {
  return (
    <div className="flex items-center gap-2 border-b border-slate-200 bg-slate-50 px-4 py-1.5 text-sm">
      <button
        type="button"
        onClick={onBack}
        className="text-slate-500 hover:text-slate-800"
      >
        ← Services
      </button>
      <span className="text-slate-400">›</span>
      <span className="font-medium text-slate-900">{label}</span>
    </div>
  );
}

interface HeaderProps {
  projectPath: string;
  error: string | null;
  socketStatus: SocketStatus;
  projectName: string | null;
  migratedToast: string[] | null;
  onDismissToast: () => void;
}

function Header({
  projectPath,
  error,
  socketStatus,
  projectName,
  migratedToast,
  onDismissToast,
}: HeaderProps) {
  return (
    <header className="flex flex-col border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="flex items-center justify-between px-4 py-2">
        <div className="flex items-center gap-4">
          <span className="text-sm font-semibold tracking-wide">PLOT</span>
          <span className="font-mono text-xs text-slate-500" title={projectPath}>
            {truncateMiddle(projectPath, 48)}
          </span>
          {projectName && (
            <span className="text-sm text-slate-700">· {projectName}</span>
          )}
        </div>
        <div className="flex w-64 items-center justify-end gap-2 text-right text-xs">
          <SocketIndicator status={socketStatus} />
          {error && (
            <span
              className="truncate text-rose-600"
              title={error}
              aria-label="error"
            >
              {error}
            </span>
          )}
        </div>
      </div>
      {migratedToast && migratedToast.length > 0 && (
        <div className="flex items-center justify-between border-t border-emerald-200 bg-emerald-50 px-4 py-1.5 text-xs text-emerald-800">
          <span>
            Migrated {migratedToast.length} v0.1 sketch
            {migratedToast.length === 1 ? "" : "es"} to v0.4 format:
            <code className="ml-1">{migratedToast.join(", ")}</code>
          </span>
          <button
            type="button"
            onClick={onDismissToast}
            className="rounded px-1 text-emerald-700 hover:bg-emerald-100"
          >
            ✕
          </button>
        </div>
      )}
    </header>
  );
}

function SocketIndicator({ status }: { status: SocketStatus }) {
  const label = {
    connecting: "connecting…",
    connected: "live",
    reconnecting: "reconnecting…",
    disconnected: "offline",
  }[status];
  const dot = {
    connecting: "bg-amber-500 animate-pulse",
    connected: "bg-emerald-500",
    reconnecting: "bg-amber-500 animate-pulse",
    disconnected: "bg-slate-400",
  }[status];
  const tone = {
    connecting: "text-amber-700",
    connected: "text-emerald-700",
    reconnecting: "text-amber-700",
    disconnected: "text-slate-600",
  }[status];
  return (
    <span
      className={`inline-flex items-center gap-1 ${tone}`}
      title={`Server: ${label}`}
    >
      <span aria-hidden className={`h-2 w-2 rounded-full ${dot}`} />
      <span>{label}</span>
    </span>
  );
}

function Loading() {
  return (
    <div className="flex h-full items-center justify-center text-slate-500">
      Loading…
    </div>
  );
}

function ErrorPanel({ message }: { message: string }) {
  return (
    <div className="flex h-full items-center justify-center p-8 text-center">
      <div>
        <h1 className="mb-2 text-xl font-semibold text-rose-700">
          Something broke
        </h1>
        <p className="font-mono text-xs text-slate-600">{message}</p>
      </div>
    </div>
  );
}

function EmptyState({ onCreate }: { onCreate: () => void }) {
  return (
    <div className="flex h-full items-center justify-center p-8 text-center">
      <div>
        <h1 className="mb-2 text-2xl font-semibold">No projects yet</h1>
        <p className="mb-6 text-slate-500">
          Create your first Plot project to start mapping.
        </p>
        <button
          type="button"
          onClick={onCreate}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
        >
          New project
        </button>
      </div>
    </div>
  );
}

function truncateMiddle(s: string, max: number): string {
  if (s.length <= max) return s;
  const side = Math.floor((max - 1) / 2);
  return `${s.slice(0, side)}…${s.slice(-side)}`;
}
