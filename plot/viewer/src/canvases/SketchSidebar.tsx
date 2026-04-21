import { useState } from "react";
import type { SketchSummary } from "../types";
import { SketchStencil, type StencilCanvas } from "./SketchStencil";

export interface SketchSidebarProps {
  sketches: SketchSummary[];
  activeId: string | null;
  stencilCanvas: StencilCanvas;
  onPick: (id: string) => void;
  onCreate: () => Promise<void> | void;
  onRename: (id: string, name: string) => Promise<void> | void;
  onDelete: (id: string) => Promise<void> | void;
}

export function SketchSidebar({
  sketches,
  activeId,
  stencilCanvas,
  onPick,
  onCreate,
  onRename,
  onDelete,
}: SketchSidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [draft, setDraft] = useState("");

  if (collapsed) {
    return (
      <aside className="flex h-full w-8 flex-col items-center border-r border-slate-200 bg-white py-2">
        <button
          type="button"
          onClick={() => setCollapsed(false)}
          aria-label="Expand sketch list"
          className="rounded px-1 py-2 text-slate-500 hover:bg-slate-100"
          title="Show sketches"
        >
          ▸
        </button>
      </aside>
    );
  }

  return (
    <aside className="flex h-full w-56 flex-col border-r border-slate-200 bg-white">
      <div className="flex items-center justify-between border-b border-slate-200 px-3 py-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Sketches
        </span>
        <button
          type="button"
          onClick={() => setCollapsed(true)}
          aria-label="Collapse sketch list"
          className="rounded px-1 text-slate-400 hover:bg-slate-100"
          title="Hide"
        >
          ◂
        </button>
      </div>
      <button
        type="button"
        onClick={() => onCreate()}
        className="mx-3 mt-3 rounded bg-slate-900 px-2 py-1 text-xs font-medium text-white hover:bg-slate-700"
      >
        + New sketch
      </button>
      <ul className="max-h-[40vh] overflow-y-auto px-2 py-3">
        {sketches.length === 0 && (
          <li className="px-2 py-2 text-xs italic text-slate-400">(none yet)</li>
        )}
        {sketches.map((s) => {
          const isActive = s.id === activeId;
          const isRenaming = renamingId === s.id;
          return (
            <li
              key={s.id}
              className={`group relative mb-1 rounded px-2 py-1.5 text-sm ${
                isActive ? "bg-indigo-50 text-indigo-900" : "text-slate-800 hover:bg-slate-100"
              }`}
            >
              {isRenaming ? (
                <input
                  autoFocus
                  type="text"
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  onBlur={() => {
                    const v = draft.trim();
                    setRenamingId(null);
                    if (v && v !== s.name) void onRename(s.id, v);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") (e.target as HTMLInputElement).blur();
                    if (e.key === "Escape") setRenamingId(null);
                  }}
                  className="w-full rounded border border-indigo-400 bg-white px-1 py-0.5 text-xs focus:outline-none"
                  aria-label="Rename sketch"
                />
              ) : (
                <button
                  type="button"
                  onClick={() => onPick(s.id)}
                  className="block w-full truncate text-left"
                  title={s.name || s.id}
                >
                  {s.name || s.id}
                  <span className="ml-2 text-[10px] text-slate-400">
                    {s.node_count}n·{s.edge_count}e
                  </span>
                </button>
              )}
              {!isRenaming && (
                <div className="absolute right-1 top-1 hidden gap-1 group-hover:flex">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setRenamingId(s.id);
                      setDraft(s.name);
                    }}
                    className="rounded px-1 text-[10px] text-slate-500 hover:bg-slate-200"
                    title="Rename"
                  >
                    ✎
                  </button>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (window.confirm(`Delete sketch "${s.name || s.id}"?`)) {
                        void onDelete(s.id);
                      }
                    }}
                    className="rounded px-1 text-[10px] text-rose-600 hover:bg-rose-100"
                    title="Delete"
                  >
                    ✕
                  </button>
                </div>
              )}
            </li>
          );
        })}
      </ul>
      <div className="flex-1 overflow-y-auto">
        <SketchStencil canvas={stencilCanvas} />
      </div>
    </aside>
  );
}
