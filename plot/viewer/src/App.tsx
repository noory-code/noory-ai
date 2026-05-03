import { useCallback, useEffect, useMemo, useState } from "react";
import { resolveProjectPath, type SocketStatus } from "./api";
import { SketchCanvas } from "./canvases/SketchCanvas";
import { SketchSidebar } from "./canvases/SketchSidebar";
import { useProjectHistory } from "./canvases/useProjectHistory";
import { useCanvasPersist } from "./hooks/useCanvasPersist";
import { useProject } from "./hooks/useProject";
import { useProjectSocket } from "./hooks/useProjectSocket";
import type { CanvasKey, CanvasKind, SketchNode } from "./types";

type CanvasTab = "foundation" | "actors" | "services";
const CANVAS_TABS: readonly { id: CanvasTab; label: string }[] = [
  { id: "foundation", label: "Foundation" },
  { id: "actors", label: "Actors" },
  { id: "services", label: "Services" },
];

function tabToKind(tab: CanvasTab): CanvasKind {
  if (tab === "foundation") return "foundation";
  if (tab === "actors") return "actors";
  return "services";
}


export function App() {
  const projectPath = useMemo(resolveProjectPath, []);
  const history = useProjectHistory();
  const [error, setError] = useState<string | null>(null);

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

  // ------- project state (extracted to useProject) -------

  const initialActiveId = useMemo(() => {
    const url = new URL(window.location.href);
    return url.searchParams.get("project") ?? url.searchParams.get("sketch");
  }, []);

  const project = useProject({
    projectPath,
    history,
    initialActiveId,
    onActiveIdChange: (id) => {
      syncUrl({ project: id, sketch: null });
    },
    onError: (err) => setError(err),
  });

  const {
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
    create: handleCreate,
    rename: handleRename,
    remove: handleDelete,
    pick: handlePick,
    markSession: handleMarkSession,
    deleteTag: handleDeleteTag,
    dismissToast,
  } = project;

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

  // ------- persist + undo/redo (extracted to useCanvasPersist) -------

  const {
    pendingWrites,
    applyEdit,
    undo: historyUndo,
    redo: historyRedo,
  } = useCanvasPersist({
    projectPath,
    activeId,
    history,
    setCanvasCache,
    setServiceDetails,
    onListStale: () => {
      void loadList();
    },
    onError: (err) => setError(err),
  });

  // ------- WebSocket (extracted to useProjectSocket) -------

  const socketStatus = useProjectSocket({
    projectPath,
    activeId,
    pendingWrites,
    onListStale: () => {
      void loadList();
    },
    onExternalCanvas: (key, fresh) => {
      setCanvasCache((prev) => {
        const next = new Map(prev);
        next.set(key, fresh);
        return next;
      });
    },
    onTagsRefresh: (nextTags) => setTags(nextTags),
    onExternalChange: () => history.clear(),
    onError: (err) => setError(err),
  });

  const handleUndo = useCallback(() => {
    const key = historyUndo();
    if (key) focusCanvas(key);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [historyUndo]);

  const handleRedo = useCallback(() => {
    const key = historyRedo();
    if (key) focusCanvas(key);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [historyRedo]);

  const focusCanvas = useCallback(
    (key: CanvasKey) => {
      if (key === "foundation") {
        setActiveTab("foundation");
        setDetailServiceId(null);
        syncUrl({ canvas: "foundation", detail: null });
      } else if (key === "actors") {
        setActiveTab("actors");
        setDetailServiceId(null);
        syncUrl({ canvas: "actors", detail: null });
      } else if (key === "services") {
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

  const [helpOpen, setHelpOpen] = useState(false);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)) {
        return;
      }
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key === "z" && !e.shiftKey) {
        e.preventDefault();
        handleUndo();
        return;
      }
      if (mod && ((e.key === "z" && e.shiftKey) || e.key === "y")) {
        e.preventDefault();
        handleRedo();
        return;
      }
      // ``?`` without modifiers → toggle help.
      if (!mod && !e.altKey && (e.key === "?" || (e.shiftKey && e.key === "/"))) {
        e.preventDefault();
        setHelpOpen((v) => !v);
        return;
      }
      if (!mod && e.key === "Escape" && helpOpen) {
        e.preventDefault();
        setHelpOpen(false);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleUndo, handleRedo, helpOpen]);

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

  // v0.10 Step 3: foundation canvas feeds the FoundationRefPicker. The
  // three master kinds are filtered separately so each picker shows only
  // the relevant candidates.
  const foundationCanvas = canvasCache.get("foundation");
  const availableMissions: SketchNode[] = useMemo(() => {
    if (!foundationCanvas) return [];
    return foundationCanvas.nodes.filter((n) => n.kind === "mission");
  }, [foundationCanvas]);
  const availableValues: SketchNode[] = useMemo(() => {
    if (!foundationCanvas) return [];
    return foundationCanvas.nodes.filter((n) => n.kind === "core_value");
  }, [foundationCanvas]);
  const availableIdentities: SketchNode[] = useMemo(() => {
    if (!foundationCanvas) return [];
    return foundationCanvas.nodes.filter((n) => n.kind === "identity");
  }, [foundationCanvas]);

  // v0.11.6 — download / upload toolbar buttons removed per user
  // feedback. Save is automatic; the toolbar focuses on undo/redo +
  // layout. Reintroducing JSON import/export should go through a
  // dedicated import/export flow if it returns at all.

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
        onDismissToast={dismissToast}
        migratedToast={migratedToast}
      />
      {helpOpen && <HelpCheatsheet onClose={() => setHelpOpen(false)} />}
      <div className="flex flex-1 overflow-hidden">
        <SketchSidebar
          projects={summaries}
          activeId={activeId}
          stencilCanvas={
            activeTab === "services" && detailServiceId ? "service_detail" : activeTab
          }
          availableActors={availableActors}
          availableMissions={availableMissions}
          availableValues={availableValues}
          availableIdentities={availableIdentities}
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
                  .get("services")
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
                doc={activeCanvas}
                onDocChange={(next) => {
                  applyEdit(activeCanvasKey, activeCanvas, next);
                }}
                onUndo={handleUndo}
                onRedo={handleRedo}
                canUndo={history.canUndo}
                canRedo={history.canRedo}
                projectPath={projectPath ?? ""}
                projectId={activeId}
                availableActors={availableActors}
                availableMissions={availableMissions}
                availableValues={availableValues}
                availableIdentities={availableIdentities}
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

function HelpCheatsheet({ onClose }: { onClose: () => void }) {
  const items: [string, string][] = [
    ["⌘/Ctrl + Z", "Undo (project-wide, auto-switches tab)"],
    ["⌘/Ctrl + Shift + Z", "Redo"],
    ["⌘/Ctrl + Y", "Redo (alt)"],
    ["⌘/Ctrl + C", "Copy selection"],
    ["⌘/Ctrl + V", "Paste"],
    ["⌘/Ctrl + D", "Duplicate selection"],
    ["⌘/Ctrl + A", "Select all"],
    ["Delete / Backspace", "Delete selected nodes"],
    ["Double-click service", "Drill into Service Detail (Overview)"],
    ["Double-click actor_ref", "Jump to Actor canvas target"],
    ["?", "Toggle this help"],
    ["Esc", "Close help"],
  ];
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Keyboard shortcuts"
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40"
      onClick={onClose}
    >
      <div
        className="w-[28rem] max-w-[90vw] overflow-hidden rounded-lg bg-white shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <h2 className="text-sm font-semibold text-slate-900">
            Keyboard shortcuts
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded px-2 text-slate-400 hover:bg-slate-100"
          >
            ✕
          </button>
        </div>
        <dl className="divide-y divide-slate-100 text-xs">
          {items.map(([combo, desc]) => (
            <div key={combo} className="flex items-center gap-3 px-4 py-1.5">
              <dt className="w-36 shrink-0 font-mono text-[11px] text-slate-700">
                {combo}
              </dt>
              <dd className="text-slate-600">{desc}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
}

function truncateMiddle(s: string, max: number): string {
  if (s.length <= max) return s;
  const side = Math.floor((max - 1) / 2);
  return `${s.slice(0, side)}…${s.slice(-side)}`;
}
