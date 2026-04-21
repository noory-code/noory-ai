import { useState } from "react";
import type { ProjectDoc, ProjectTag } from "../types";
import { SketchStencil, type StencilCanvas } from "./SketchStencil";

export interface SketchSidebarProps {
  projects: ProjectDoc[];
  activeId: string | null;
  stencilCanvas: StencilCanvas;
  tags: ProjectTag[];
  onPick: (id: string) => void;
  onCreate: () => Promise<void> | void;
  onRename: (id: string, name: string) => Promise<void> | void;
  onDelete: (id: string) => Promise<void> | void;
  onDeleteTag: (name: string) => Promise<void> | void;
}

export function SketchSidebar({
  projects,
  activeId,
  stencilCanvas,
  tags,
  onPick,
  onCreate,
  onRename,
  onDelete,
  onDeleteTag,
}: SketchSidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [tagsOpen, setTagsOpen] = useState(true);

  if (collapsed) {
    return (
      <aside className="flex h-full w-8 flex-col items-center border-r border-slate-200 bg-white py-2">
        <button
          type="button"
          onClick={() => setCollapsed(false)}
          aria-label="Expand project list"
          className="rounded px-1 py-2 text-slate-500 hover:bg-slate-100"
          title="Show projects"
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
          Projects
        </span>
        <button
          type="button"
          onClick={() => setCollapsed(true)}
          aria-label="Collapse project list"
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
        + New project
      </button>
      <ul className="max-h-[30vh] overflow-y-auto px-2 py-3">
        {projects.length === 0 && (
          <li className="px-2 py-2 text-xs italic text-slate-400">(none yet)</li>
        )}
        {projects.map((p) => {
          const isActive = p.id === activeId;
          const isRenaming = renamingId === p.id;
          return (
            <li
              key={p.id}
              className={`group relative mb-1 rounded px-2 py-1.5 text-sm ${
                isActive
                  ? "bg-indigo-50 text-indigo-900"
                  : "text-slate-800 hover:bg-slate-100"
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
                    if (v && v !== p.name) void onRename(p.id, v);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") (e.target as HTMLInputElement).blur();
                    if (e.key === "Escape") setRenamingId(null);
                  }}
                  className="w-full rounded border border-indigo-400 bg-white px-1 py-0.5 text-xs focus:outline-none"
                  aria-label="Rename project"
                />
              ) : (
                <button
                  type="button"
                  onClick={() => onPick(p.id)}
                  className="block w-full truncate text-left"
                  title={p.name || p.id}
                >
                  {p.name || p.id}
                </button>
              )}
              {!isRenaming && (
                <div className="absolute right-1 top-1 hidden gap-1 group-hover:flex">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setRenamingId(p.id);
                      setDraft(p.name);
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
                      if (window.confirm(`Delete project "${p.name || p.id}"?`)) {
                        void onDelete(p.id);
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
      {activeId && (
        <div className="border-t border-slate-200 px-3 py-2">
          <button
            type="button"
            onClick={() => setTagsOpen((v) => !v)}
            className="flex w-full items-center justify-between text-[10px] font-semibold uppercase tracking-wide text-slate-500 hover:text-slate-700"
          >
            <span>Session tags</span>
            <span>{tagsOpen ? "▾" : "▸"}</span>
          </button>
          {tagsOpen && (
            <ul className="mt-1 max-h-32 overflow-y-auto">
              {tags.length === 0 && (
                <li className="px-1 py-1 text-[11px] italic text-slate-400">
                  (no tags — click "Mark session…" to plant one)
                </li>
              )}
              {tags.map((t) => (
                <li
                  key={t.name}
                  className="group flex items-center justify-between rounded px-1 py-0.5 text-[11px] text-slate-700 hover:bg-slate-100"
                  title={`${t.message}\n${t.sha.slice(0, 8)} · ${t.ts}`}
                >
                  <span className="truncate font-medium">{t.name}</span>
                  <button
                    type="button"
                    onClick={() => {
                      if (window.confirm(`Delete tag "${t.name}"?`)) {
                        void onDeleteTag(t.name);
                      }
                    }}
                    className="hidden px-1 text-[10px] text-rose-600 hover:bg-rose-100 group-hover:inline"
                    title="Delete tag (commit stays)"
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      <div className="flex-1 overflow-y-auto">
        <SketchStencil canvas={stencilCanvas} />
      </div>
    </aside>
  );
}
