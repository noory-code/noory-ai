import { useState } from "react";
import { useTranslation } from "react-i18next";
import { LanguageToggle } from "../i18n/LanguageToggle";
import type { ProjectDoc, ProjectTag, SketchNode } from "../types";
import { SketchStencil, type StencilCanvas } from "./SketchStencil";

export interface SketchSidebarProps {
  projects: ProjectDoc[];
  activeId: string | null;
  stencilCanvas: StencilCanvas;
  tags: ProjectTag[];
  /** v0.11.5 — masters for the dynamic ref presets on the
   *  service_detail stencil (each master = its own draggable). */
  availableActors?: SketchNode[];
  availableMissions?: SketchNode[];
  availableValues?: SketchNode[];
  availableIdentities?: SketchNode[];
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
  availableActors,
  availableMissions,
  availableValues,
  availableIdentities,
  onPick,
  onCreate,
  onRename,
  onDelete,
  onDeleteTag,
}: SketchSidebarProps) {
  const { t } = useTranslation();
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
          aria-label={t("sidebar.expandProjectList")}
          className="rounded px-1 py-2 text-slate-500 hover:bg-slate-100"
          title={t("sidebar.showProjects")}
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
          {t("sidebar.projects")}
        </span>
        <button
          type="button"
          onClick={() => setCollapsed(true)}
          aria-label={t("sidebar.collapseProjectList")}
          className="rounded px-1 text-slate-400 hover:bg-slate-100"
          title={t("sidebar.hideProjects")}
        >
          ◂
        </button>
      </div>
      <button
        type="button"
        onClick={() => onCreate()}
        className="mx-3 mt-3 rounded bg-slate-900 px-2 py-1 text-xs font-medium text-white hover:bg-slate-700"
      >
        {t("sidebar.newProject")}
      </button>
      <ul className="max-h-[30vh] overflow-y-auto px-2 py-3">
        {projects.length === 0 && (
          <li className="px-2 py-2 text-xs italic text-slate-400">{t("sidebar.noProjects")}</li>
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
                  aria-label={t("sidebar.renameProject")}
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
                    title={t("sidebar.rename")}
                  >
                    ✎
                  </button>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (
                        window.confirm(
                          t("sidebar.confirmDeleteProject", { name: p.name || p.id }),
                        )
                      ) {
                        void onDelete(p.id);
                      }
                    }}
                    className="rounded px-1 text-[10px] text-rose-600 hover:bg-rose-100"
                    title={t("sidebar.delete")}
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
            <span>{t("sidebar.sessionTags")}</span>
            <span>{tagsOpen ? "▾" : "▸"}</span>
          </button>
          {tagsOpen && (
            <ul className="mt-1 max-h-32 overflow-y-auto">
              {tags.length === 0 && (
                <li className="px-1 py-1 text-[11px] italic text-slate-400">
                  {t("sidebar.noTagsHint")}
                </li>
              )}
              {tags.map((tag) => (
                <li
                  key={tag.name}
                  className="group flex items-center justify-between rounded px-1 py-0.5 text-[11px] text-slate-700 hover:bg-slate-100"
                  title={`${tag.message}\n${tag.sha.slice(0, 8)} · ${tag.ts}`}
                >
                  <span className="truncate font-medium">{tag.name}</span>
                  <button
                    type="button"
                    onClick={() => {
                      if (window.confirm(t("sidebar.confirmDeleteTag", { name: tag.name }))) {
                        void onDeleteTag(tag.name);
                      }
                    }}
                    className="hidden px-1 text-[10px] text-rose-600 hover:bg-rose-100 group-hover:inline"
                    title={t("sidebar.deleteTag")}
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
        <SketchStencil
          canvas={stencilCanvas}
          availableActors={availableActors}
          availableMissions={availableMissions}
          availableValues={availableValues}
          availableIdentities={availableIdentities}
        />
      </div>
      <div className="flex items-center justify-end border-t border-slate-200 px-3 py-2">
        <LanguageToggle />
      </div>
    </aside>
  );
}
