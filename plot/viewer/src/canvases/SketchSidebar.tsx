import { useState } from "react";
import { useTranslation } from "react-i18next";
import { LanguageToggle } from "../i18n/LanguageToggle";
import { ThemeToggle } from "../shell/ThemeToggle";
import type { ProjectDoc, ProjectTag, SketchNode } from "../types";
import { SketchStencil, type StencilCanvas } from "./SketchStencil";
import { useDialog } from "../shell/dialog/DialogProvider";

export interface SketchSidebarProps {
  projects: ProjectDoc[];
  activeId: string | null;
  /** v0.33.0 — a project's dir relative to the workspace root ("." = root).
   *  Rendered as a muted subtitle so the unified list shows where each
   *  project lives. */
  dirForId?: (id: string) => string;
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
  /** v0.24.14 (D-2026-05-21-C) — enter read-only snapshot view at this tag. */
  onViewTag: (name: string) => Promise<void> | void;
  /** Current tag being viewed (if any) — highlight the row. */
  viewingTag: string | null;
}

export function SketchSidebar({
  projects,
  activeId,
  dirForId,
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
  onViewTag,
  viewingTag,
}: SketchSidebarProps) {
  const { t } = useTranslation();
  const dialog = useDialog();
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [tagsOpen, setTagsOpen] = useState(true);

  // D-2026-06-14-E — width + collapse are owned by the resizable panel
  // (WorkspacePanels); the sidebar fills its panel. The old self-managed
  // w-8 rail / w-56 expand toggle is gone.
  return (
    <aside className="flex h-full w-full flex-col border-r border-line bg-surface">
      <div className="flex items-center justify-between border-b border-line px-3 py-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-fg-muted">
          {t("sidebar.projects")}
        </span>
      </div>
      <button
        type="button"
        onClick={() => onCreate()}
        className="mx-3 mt-3 rounded bg-surface-inverse px-2 py-1 text-xs font-medium text-fg-inverse hover:bg-surface-inverse"
      >
        {t("sidebar.newProject")}
      </button>
      <ul className="max-h-[30vh] overflow-y-auto px-2 py-3">
        {projects.length === 0 && (
          <li className="px-2 py-2 text-xs italic text-fg-faint">{t("sidebar.noProjects")}</li>
        )}
        {projects.map((p) => {
          const isActive = p.id === activeId;
          const isRenaming = renamingId === p.id;
          return (
            <li
              key={p.id}
              className={`group relative mb-1 rounded px-2 py-1.5 text-sm ${
                isActive
                  ? "bg-accent-soft text-accent-fg"
                  : "text-fg-strong hover:bg-surface-subtle"
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
                  className="w-full rounded border border-accent bg-surface px-1 py-0.5 text-xs focus:outline-none"
                  aria-label={t("sidebar.renameProject")}
                />
              ) : (
                <button
                  type="button"
                  onClick={() => onPick(p.id)}
                  className="block w-full text-left"
                  title={p.name || p.id}
                >
                  <span className="block truncate">{p.name || p.id}</span>
                  {dirForId && (
                    <span className="block truncate text-[10px] font-normal text-fg-faint">
                      {dirForId(p.id) === "." ? t("sidebar.rootDir") : dirForId(p.id)}
                    </span>
                  )}
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
                    className="rounded px-1 text-[10px] text-fg-muted hover:bg-line"
                    title={t("sidebar.rename")}
                  >
                    ✎
                  </button>
                  <button
                    type="button"
                    onClick={async (e) => {
                      e.stopPropagation();
                      if (
                        await dialog.confirm({
                          message: t("sidebar.confirmDeleteProject", { name: p.name || p.id }),
                          danger: true,
                        })
                      ) {
                        void onDelete(p.id);
                      }
                    }}
                    className="rounded px-1 text-[10px] text-danger hover:bg-danger-soft"
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
        <div className="border-t border-line px-3 py-2">
          <button
            type="button"
            onClick={() => setTagsOpen((v) => !v)}
            className="flex w-full items-center justify-between text-[10px] font-semibold uppercase tracking-wide text-fg-muted hover:text-fg"
          >
            <span>{t("sidebar.sessionTags")}</span>
            <span>{tagsOpen ? "▾" : "▸"}</span>
          </button>
          {tagsOpen && (
            <ul className="mt-1 max-h-32 overflow-y-auto">
              {tags.length === 0 && (
                <li className="px-1 py-1 text-[11px] italic text-fg-faint">
                  {t("sidebar.noTagsHint")}
                </li>
              )}
              {tags.map((tag) => {
                const isViewed = tag.name === viewingTag;
                return (
                  <li
                    key={tag.name}
                    className={`group flex items-center justify-between rounded px-1 py-0.5 text-[11px] hover:bg-surface-subtle ${
                      isViewed ? "bg-warn-soft text-warn-fg" : "text-fg"
                    }`}
                    title={`${tag.message}\n${tag.sha.slice(0, 8)} · ${tag.ts}`}
                  >
                    <button
                      type="button"
                      onClick={() => void onViewTag(tag.name)}
                      className="flex-1 truncate text-left font-medium"
                      title={t("sidebar.viewTag", { name: tag.name })}
                    >
                      {isViewed ? "👁 " : ""}
                      {tag.name}
                    </button>
                    <button
                      type="button"
                      onClick={async () => {
                        if (
                          await dialog.confirm({
                            message: t("sidebar.confirmDeleteTag", { name: tag.name }),
                            danger: true,
                          })
                        ) {
                          void onDeleteTag(tag.name);
                        }
                      }}
                      className="hidden px-1 text-[10px] text-danger hover:bg-danger-soft group-hover:inline"
                      title={t("sidebar.deleteTag")}
                    >
                      ✕
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}
      {/* Stencil is meaningful only with an active project to drop onto
          (D-2026-05-31-K) — gated like the session-tags block above. */}
      {activeId && (
        <div className="flex-1 overflow-y-auto">
          <SketchStencil
            canvas={stencilCanvas}
            availableActors={availableActors}
            availableMissions={availableMissions}
            availableValues={availableValues}
            availableIdentities={availableIdentities}
          />
        </div>
      )}
      <div className="flex items-center justify-end gap-2 border-t border-line px-3 py-2">
        <ThemeToggle />
        <LanguageToggle />
      </div>
    </aside>
  );
}
