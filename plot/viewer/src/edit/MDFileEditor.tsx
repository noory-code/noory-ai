import { useCallback, useEffect, useRef, useState } from "react";
import { readFile, writeFile } from "../api";
import { MDPreview } from "./MDPreview";

export interface MDFileEditorProps {
  projectPath: string;
  /** Relative path under ``projectPath`` — e.g. ``workspace/foundation/mission-mission/index.md``. */
  path: string;
  /** Hints so the server can refresh the on-canvas preview cache. */
  projectId: string;
  nodeId: string;
  canvasKind?: string;
}

type SaveState = "idle" | "saving" | "saved" | "error";

const DEBOUNCE_MS = 600;

/**
 * Raw Markdown editor backed by a single MD file. Mirrors the canvas
 * autosave rhythm (debounced PUT) but against the file API instead of
 * the canvas API.
 *
 * Intentionally a plain ``<textarea>`` for now — matches Solera's editor
 * style and keeps the bundle small. Swap for CodeMirror later if the UX
 * grows teeth.
 */
export function MDFileEditor({
  projectPath,
  path,
  projectId,
  nodeId,
  canvasKind,
}: MDFileEditorProps) {
  const [content, setContent] = useState<string>("");
  const [loadedPath, setLoadedPath] = useState<string>("");
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"edit" | "preview" | "split">("edit");
  const saveTimer = useRef<number | null>(null);
  // Track the latest path we fetched so stale fetch responses
  // (from rapid node switching) don't overwrite the current editor.
  const latestPath = useRef(path);
  latestPath.current = path;

  useEffect(() => {
    let cancelled = false;
    setSaveState("idle");
    setError(null);
    readFile(projectPath, projectId, path)
      .then((body) => {
        if (cancelled || latestPath.current !== path) return;
        setContent(body);
        setLoadedPath(path);
      })
      .catch((e: unknown) => {
        if (cancelled || latestPath.current !== path) return;
        setError(e instanceof Error ? e.message : String(e));
      });
    return () => {
      cancelled = true;
      if (saveTimer.current !== null) {
        window.clearTimeout(saveTimer.current);
        saveTimer.current = null;
      }
    };
  }, [projectPath, path]);

  const scheduleSave = useCallback(
    (next: string) => {
      if (saveTimer.current !== null) window.clearTimeout(saveTimer.current);
      setSaveState("saving");
      saveTimer.current = window.setTimeout(() => {
        saveTimer.current = null;
        writeFile(projectPath, projectId, path, next, {
          nodeId,
          canvasKind,
        })
          .then(() => {
            if (latestPath.current !== path) return;
            setSaveState("saved");
            setError(null);
            window.setTimeout(() => {
              if (latestPath.current === path) setSaveState("idle");
            }, 1500);
          })
          .catch((e: unknown) => {
            if (latestPath.current !== path) return;
            setError(e instanceof Error ? e.message : String(e));
            setSaveState("error");
          });
      }, DEBOUNCE_MS);
    },
    [projectPath, path, projectId, nodeId, canvasKind],
  );

  if (loadedPath !== path && error === null) {
    return (
      <div className="p-3 text-xs italic text-slate-400">Loading…</div>
    );
  }

  const editor = (
    <textarea
      value={content}
      onChange={(e) => {
        const next = e.target.value;
        setContent(next);
        scheduleSave(next);
      }}
      spellCheck={false}
      className="h-full w-full flex-1 resize-none border-none bg-white p-3 font-mono text-[12px] leading-relaxed text-slate-800 focus:outline-none"
      placeholder="Write freely. Use ### headings to mark Tagline / Summary / Details sections — the node preview picks up the first one. ```mermaid blocks render in Preview."
    />
  );

  const preview = (
    <div className="h-full w-full flex-1 overflow-auto p-3">
      <MDPreview content={content} />
    </div>
  );

  return (
    <div className="flex h-full w-full flex-col">
      <div className="flex items-center justify-between border-b border-slate-200 px-3 py-1.5 text-[10px] text-slate-500">
        <span className="truncate font-mono" title={path}>
          📁 {path}
        </span>
        <div className="flex items-center gap-2">
          <div className="flex rounded border border-slate-200 text-[10px]">
            {(["edit", "split", "preview"] as const).map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setMode(m)}
                className={
                  "px-2 py-0.5 " +
                  (mode === m
                    ? "bg-slate-900 text-white"
                    : "text-slate-500 hover:bg-slate-100")
                }
              >
                {m}
              </button>
            ))}
          </div>
          <span
            className={
              saveState === "saving"
                ? "text-slate-400"
                : saveState === "saved"
                  ? "text-emerald-600"
                  : saveState === "error"
                    ? "text-rose-600"
                    : "text-transparent"
            }
          >
            {saveState === "saving"
              ? "saving…"
              : saveState === "saved"
                ? "saved"
                : saveState === "error"
                  ? error ?? "save failed"
                  : "·"}
          </span>
        </div>
      </div>
      {mode === "edit" && editor}
      {mode === "preview" && preview}
      {mode === "split" && (
        <div className="flex min-h-0 flex-1">
          <div className="flex min-h-0 flex-1 border-r border-slate-200">{editor}</div>
          <div className="flex min-h-0 flex-1">{preview}</div>
        </div>
      )}
    </div>
  );
}
