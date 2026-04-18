import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchGraph, openGraphSocket, resolveProjectPath } from "./api";
import { PlanCanvas } from "./canvases/PlanCanvas";
import type { Graph, WorkspaceLens } from "./types";

export function App() {
  const projectPath = useMemo(resolveProjectPath, []);
  const [graph, setGraph] = useState<Graph | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lens, setLens] = useState<WorkspaceLens>("plan");

  const reload = useCallback(async () => {
    if (!projectPath) return;
    try {
      setGraph(await fetchGraph(projectPath));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [projectPath]);

  useEffect(() => {
    void reload();
  }, [reload]);

  useEffect(() => {
    if (!projectPath) return;
    const sock = openGraphSocket(
      projectPath,
      (msg) => {
        if (msg.event === "graph_changed") void reload();
      },
      (err) => setError(err),
    );
    return () => sock.close();
  }, [projectPath, reload]);

  if (!projectPath) {
    return (
      <div className="flex h-full items-center justify-center p-8 text-center">
        <div>
          <h1 className="mb-2 text-2xl font-semibold">Solera Map</h1>
          <p className="text-slate-500">
            Add <code>?project_path=/absolute/path/to/project</code> to the URL.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <Header lens={lens} onLensChange={setLens} projectPath={projectPath} error={error} />
      <main className="flex-1">
        {graph ? (
          <PlanCanvas graph={graph} lens={lens} />
        ) : (
          <div className="flex h-full items-center justify-center text-slate-400">
            loading…
          </div>
        )}
      </main>
    </div>
  );
}

interface HeaderProps {
  lens: WorkspaceLens;
  onLensChange: (lens: WorkspaceLens) => void;
  projectPath: string;
  error: string | null;
}

function Header({ lens, onLensChange, projectPath, error }: HeaderProps) {
  const tabs: { key: WorkspaceLens; label: string; accent: string }[] = [
    { key: "plan", label: "Plan", accent: "text-sketch" },
    { key: "build", label: "Build", accent: "text-paint" },
    { key: "live", label: "Live", accent: "text-live" },
  ];
  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white/80 px-4 py-2 backdrop-blur">
      <div className="flex items-center gap-4">
        <span className="text-sm font-semibold tracking-wide">SOLERA MAP</span>
        <span className="font-mono text-xs text-slate-500" title={projectPath}>
          {truncateMiddle(projectPath, 48)}
        </span>
      </div>
      <nav className="flex gap-1 rounded-lg bg-slate-100 p-1">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => onLensChange(t.key)}
            className={`rounded-md px-3 py-1 text-sm font-medium transition ${
              lens === t.key
                ? `bg-white shadow-sm ${t.accent}`
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>
      <div className="w-48 text-right text-xs text-rose-500">{error ?? ""}</div>
    </header>
  );
}

function truncateMiddle(s: string, max: number): string {
  if (s.length <= max) return s;
  const side = Math.floor((max - 1) / 2);
  return `${s.slice(0, side)}…${s.slice(-side)}`;
}
