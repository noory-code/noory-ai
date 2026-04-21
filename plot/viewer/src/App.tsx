import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  createSketch,
  deleteSketch,
  getSketch,
  listSketches,
  openSketchSocket,
  putSketch,
  resolveProjectPath,
  type SocketStatus,
} from "./api";
import { SketchCanvas } from "./canvases/SketchCanvas";
import { SketchSidebar } from "./canvases/SketchSidebar";
import type { SaveState } from "./canvases/SketchToolbar";
import { useSketchHistory } from "./canvases/useSketchHistory";
import type { SketchDoc, SketchNode, SketchSummary } from "./types";

type Phase = "loading" | "no-sketches" | "ready" | "error";

// v0.2 multi-canvas (2026-04-21): canvas-kind tabs above the ReactFlow area.
// Each tab shows only the nodes/edges belonging to it; edits merge back
// with the hidden nodes from the other tabs before persisting.
type CanvasTab = "core" | "actors" | "services";
const CANVAS_TABS: readonly { id: CanvasTab; label: string }[] = [
  { id: "core", label: "Core" },
  { id: "actors", label: "Actors" },
  { id: "services", label: "Services" },
];

const CORE_KINDS = new Set(["core", "mission", "core_value", "identity", "identity_facet"]);
const SERVICE_KINDS = new Set(["service", "rule", "content", "actor_ref"]);

function classifyNodeTab(node: SketchNode, nodesById: Map<string, SketchNode>): CanvasTab {
  // Walk up the parent chain, stopping at is_root or at top. The ancestor's
  // own kind decides which tab the whole subtree belongs to.
  let cur: SketchNode = node;
  while (cur.parent_id && !cur.is_root) {
    const parent = nodesById.get(cur.parent_id);
    if (!parent) break;
    cur = parent;
  }
  if (cur.kind === "actor") return "actors";
  if (cur.kind === "service") return "services";
  if (cur.kind && CORE_KINDS.has(cur.kind)) return "core";
  if (cur.kind && SERVICE_KINDS.has(cur.kind)) return "services";
  // Legacy v0.1 untyped nodes land on Services (the default workspace).
  return "services";
}

function filterDocForTab(doc: SketchDoc, tab: CanvasTab): SketchDoc {
  const byId = new Map(doc.nodes.map((n) => [n.id, n] as const));
  const visibleNodes = doc.nodes.filter((n) => classifyNodeTab(n, byId) === tab);
  const visibleIds = new Set(visibleNodes.map((n) => n.id));
  // Edges that span tabs (e.g., v0.1 core-root → actor-root decomposition)
  // are dropped from the view — they only made sense in the single-canvas world.
  const visibleEdges = doc.edges.filter(
    (e) => visibleIds.has(e.source) && visibleIds.has(e.target),
  );
  return { ...doc, nodes: visibleNodes, edges: visibleEdges };
}

function mergeTabEdit(prev: SketchDoc, next: SketchDoc, tab: CanvasTab): SketchDoc {
  const byId = new Map(prev.nodes.map((n) => [n.id, n] as const));
  const hiddenNodes = prev.nodes.filter((n) => classifyNodeTab(n, byId) !== tab);
  const hiddenNodeIds = new Set(hiddenNodes.map((n) => n.id));
  const hiddenEdges = prev.edges.filter(
    (e) => hiddenNodeIds.has(e.source) || hiddenNodeIds.has(e.target),
  );
  return {
    ...next,
    nodes: [...hiddenNodes, ...next.nodes],
    edges: [...hiddenEdges, ...next.edges],
  };
}

const DEBOUNCE_MS = 400;

export function App() {
  const projectPath = useMemo(resolveProjectPath, []);
  const [summaries, setSummaries] = useState<SketchSummary[]>([]);
  const history = useSketchHistory<SketchDoc>();
  const doc = history.doc;
  const [phase, setPhase] = useState<Phase>("loading");
  const [error, setError] = useState<string | null>(null);
  const [socketStatus, setSocketStatus] = useState<SocketStatus>("connecting");
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [activeId, setActiveId] = useState<string | null>(() => {
    const url = new URL(window.location.href);
    return url.searchParams.get("sketch");
  });
  const [activeTab, setActiveTab] = useState<CanvasTab>(() => {
    const url = new URL(window.location.href);
    const raw = url.searchParams.get("canvas");
    return CANVAS_TABS.some((t) => t.id === raw) ? (raw as CanvasTab) : "services";
  });

  const selectTab = useCallback((tab: CanvasTab) => {
    setActiveTab(tab);
    const url = new URL(window.location.href);
    url.searchParams.set("canvas", tab);
    window.history.replaceState(null, "", url.toString());
  }, []);

  const saveTimer = useRef<number | null>(null);
  const savedTimer = useRef<number | null>(null);
  // Track doc ids we wrote ourselves so the WebSocket event for our own
  // save doesn't trigger a needless reload that wipes in-flight edits.
  const lastWriteSignature = useRef<string | null>(null);

  const loadList = useCallback(async (): Promise<SketchSummary[] | null> => {
    if (!projectPath) return null;
    try {
      const list = await listSketches(projectPath);
      setSummaries(list);
      return list;
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setPhase("error");
      return null;
    }
  }, [projectPath]);

  const loadDoc = useCallback(
    async (id: string) => {
      if (!projectPath) return;
      try {
        const d = await getSketch(projectPath, id);
        history.init(d);
        setPhase("ready");
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
        setPhase("error");
      }
    },
    [projectPath, history],
  );

  const persist = useCallback(
    (next: SketchDoc) => {
      if (!projectPath) return;
      if (saveTimer.current !== null) window.clearTimeout(saveTimer.current);
      setSaveState("saving");
      saveTimer.current = window.setTimeout(() => {
        saveTimer.current = null;
        lastWriteSignature.current = `${next.id}@${Date.now()}`;
        putSketch(projectPath, next)
          .then(() => {
            setSaveState("saved");
            if (savedTimer.current !== null) window.clearTimeout(savedTimer.current);
            savedTimer.current = window.setTimeout(() => setSaveState("idle"), 1500);
          })
          .catch((err) => {
            setSaveState("error");
            setError(err instanceof Error ? err.message : String(err));
          });
      }, DEBOUNCE_MS);
    },
    [projectPath],
  );

  const setDoc = useCallback(
    (next: SketchDoc) => {
      history.push(next);
      persist(next);
    },
    [history, persist],
  );

  const handleUndo = useCallback(() => {
    const next = history.undo();
    if (next) persist(next);
  }, [history, persist]);

  const handleRedo = useCallback(() => {
    const next = history.redo();
    if (next) persist(next);
  }, [history, persist]);

  // Initial load
  useEffect(() => {
    if (!projectPath) return;
    void (async () => {
      const list = await loadList();
      if (!list || list.length === 0) {
        setPhase("no-sketches");
        return;
      }
      const chosen =
        (activeId && list.find((s) => s.id === activeId)?.id) ?? list[0].id;
      setActiveId(chosen);
      void loadDoc(chosen);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectPath]);

  // WebSocket — funnel every volatile dep through refs so the subscription
  // persists across unrelated re-renders. The effect only runs when the
  // project itself changes.
  const wsActiveIdRef = useRef<string | null>(activeId);
  wsActiveIdRef.current = activeId;
  const wsSaveStateRef = useRef<SaveState>(saveState);
  wsSaveStateRef.current = saveState;
  const wsLoadListRef = useRef(loadList);
  wsLoadListRef.current = loadList;
  const wsLoadDocRef = useRef(loadDoc);
  wsLoadDocRef.current = loadDoc;
  useEffect(() => {
    if (!projectPath) return;
    const sock = openSketchSocket(projectPath, {
      onEvent: (msg) => {
        if (msg.event === "sketch_changed") {
          void wsLoadListRef.current();
          const id = wsActiveIdRef.current;
          if (id && wsSaveStateRef.current !== "saving") {
            void wsLoadDocRef.current(id);
          }
        }
      },
      onStatus: setSocketStatus,
      onError: (err) => setError(err),
    });
    return () => sock.close();
  }, [projectPath]);

  const handleCreate = useCallback(async () => {
    if (!projectPath) return;
    try {
      const id = `sketch-${Date.now().toString(36)}`;
      const newDoc = await createSketch(projectPath, id, "Untitled");
      setActiveId(newDoc.id);
      history.init(newDoc);
      setPhase("ready");
      await loadList();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [projectPath, loadList, history]);

  const handleRename = useCallback(
    async (id: string, name: string) => {
      if (!projectPath) return;
      try {
        // Fetch current, rewrite name, PUT back.
        const current = await getSketch(projectPath, id);
        await putSketch(projectPath, { ...current, name });
        await loadList();
        if (activeId === id) {
          history.replace({ ...(history.doc ?? current), name });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      }
    },
    [projectPath, loadList, activeId, history],
  );

  const handleDelete = useCallback(
    async (id: string) => {
      if (!projectPath) return;
      try {
        await deleteSketch(projectPath, id);
        const list = (await loadList()) ?? [];
        if (activeId === id) {
          if (list.length === 0) {
            setPhase("no-sketches");
            setActiveId(null);
          } else {
            setActiveId(list[0].id);
            void loadDoc(list[0].id);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      }
    },
    [projectPath, loadList, loadDoc, activeId],
  );

  const handleDownload = useCallback(() => {
    if (!doc) return;
    const blob = new Blob([JSON.stringify(doc, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${doc.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [doc]);

  const handleUpload = useCallback(() => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "application/json,.json";
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) return;
      try {
        const text = await file.text();
        const incoming = JSON.parse(text) as SketchDoc;
        if (!incoming.id || !Array.isArray(incoming.nodes) || !Array.isArray(incoming.edges)) {
          setError("Invalid sketch file");
          return;
        }
        // Replace the active sketch's contents; keep the id.
        if (!doc) return;
        setDoc({ ...incoming, id: doc.id });
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      }
    };
    input.click();
  }, [doc, setDoc]);

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
        sketchName={doc?.name ?? null}
      />
      <div className="flex flex-1 overflow-hidden">
        <SketchSidebar
          sketches={summaries}
          activeId={activeId}
          stencilCanvas={activeTab}
          onPick={(id) => {
            setActiveId(id);
            void loadDoc(id);
          }}
          onCreate={handleCreate}
          onRename={handleRename}
          onDelete={handleDelete}
        />
        <main className="flex flex-1 flex-col overflow-hidden">
          {phase === "ready" && doc && (
            <CanvasTabs active={activeTab} onSelect={selectTab} />
          )}
          <div className="flex-1 overflow-hidden">
            {phase === "loading" && <Loading />}
            {phase === "error" && <ErrorPanel message={error ?? "unknown"} />}
            {phase === "no-sketches" && <EmptyState onCreate={handleCreate} />}
            {phase === "ready" && doc && (
              <SketchCanvas
                key={`${doc.id}:${activeTab}`}
                doc={filterDocForTab(doc, activeTab)}
                onDocChange={(next) => setDoc(mergeTabEdit(doc, next, activeTab))}
                onUndo={handleUndo}
                onRedo={handleRedo}
                canUndo={history.canUndo}
                canRedo={history.canRedo}
                saveState={saveState}
                onDownload={handleDownload}
                onUpload={handleUpload}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

interface HeaderProps {
  projectPath: string;
  error: string | null;
  socketStatus: SocketStatus;
  sketchName: string | null;
}

function Header({ projectPath, error, socketStatus, sketchName }: HeaderProps) {
  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white/80 px-4 py-2 backdrop-blur">
      <div className="flex items-center gap-4">
        <span className="text-sm font-semibold tracking-wide">PLOT</span>
        <span className="font-mono text-xs text-slate-500" title={projectPath}>
          {truncateMiddle(projectPath, 48)}
        </span>
        {sketchName && <span className="text-sm text-slate-700">· {sketchName}</span>}
      </div>
      <div className="flex w-64 items-center justify-end gap-2 text-right text-xs">
        <SocketIndicator status={socketStatus} />
        {error && (
          <span className="truncate text-rose-600" title={error} aria-label="error">
            {error}
          </span>
        )}
      </div>
    </header>
  );
}

function CanvasTabs({
  active,
  onSelect,
}: {
  active: CanvasTab;
  onSelect: (tab: CanvasTab) => void;
}) {
  return (
    <div
      role="tablist"
      aria-label="Canvas"
      className="flex items-center gap-1 border-b border-slate-200 bg-white px-3"
    >
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
    <span className={`inline-flex items-center gap-1 ${tone}`} title={`Server: ${label}`}>
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
        <h1 className="mb-2 text-xl font-semibold text-rose-700">Something broke</h1>
        <p className="font-mono text-xs text-slate-600">{message}</p>
      </div>
    </div>
  );
}

function EmptyState({ onCreate }: { onCreate: () => void }) {
  return (
    <div className="flex h-full items-center justify-center p-8 text-center">
      <div>
        <h1 className="mb-2 text-2xl font-semibold">No sketches yet</h1>
        <p className="mb-6 text-slate-500">Create your first canvas to start mapping.</p>
        <button
          type="button"
          onClick={onCreate}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
        >
          New sketch
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
