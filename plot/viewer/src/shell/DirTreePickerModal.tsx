/**
 * Directory-tree picker for "Add a Project" (v0.34.0, D-2026-05-31-N).
 *
 * Rooted at the workspace root, the user drills the folder tree and picks a
 * target directory. Choosing a dir that already holds a project lands in it
 * (the caller's ``onPick`` → ``useProject.create`` decides); choosing an
 * empty dir creates a new project there. Tree-only (no free-text folder).
 */
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { createWorkspaceDir, getDirTree, type DirTreeNode } from "../app/workspace";
import { useDialog } from "./dialog/DialogProvider";

interface DirTreePickerModalProps {
  open: boolean;
  workspaceRoot: string | null;
  onClose: () => void;
  onPick: (dir: string) => void;
}

export function DirTreePickerModal({
  open,
  workspaceRoot,
  onClose,
  onPick,
}: DirTreePickerModalProps) {
  const { t } = useTranslation();
  const [tree, setTree] = useState<DirTreeNode | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open || !workspaceRoot) return;
    setTree(null);
    setError(null);
    let cancelled = false;
    getDirTree(workspaceRoot).then(
      (res) => !cancelled && setTree(res.root),
      (e) => !cancelled && setError(e instanceof Error ? e.message : String(e)),
    );
    return () => {
      cancelled = true;
    };
  }, [open, workspaceRoot]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={t("dirPicker.title")}
      className="fixed inset-0 z-50 flex items-center justify-center bg-overlay/40"
      onClick={onClose}
    >
      <div
        className="flex max-h-[80vh] w-[480px] flex-col overflow-hidden rounded-lg bg-surface shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex items-center justify-between border-b border-line px-4 py-2">
          <span className="text-sm font-semibold text-fg-strong">{t("dirPicker.title")}</span>
          <button
            type="button"
            onClick={onClose}
            aria-label={t("dirPicker.cancel")}
            className="rounded px-1.5 text-fg-faint hover:bg-surface-subtle"
          >
            ×
          </button>
        </header>
        <div className="flex-1 overflow-y-auto p-2 text-sm">
          {error && <p className="px-2 py-1 text-danger">{error}</p>}
          {!tree && !error && (
            <p className="px-2 py-1 italic text-fg-faint">{t("dirPicker.loading")}</p>
          )}
          {tree && (
            <TreeRow node={tree} depth={0} onPick={onPick} workspaceRoot={workspaceRoot} />
          )}
        </div>
      </div>
    </div>
  );
}

function TreeRow({
  node,
  depth,
  onPick,
  workspaceRoot,
}: {
  node: DirTreeNode;
  depth: number;
  onPick: (dir: string) => void;
  workspaceRoot: string | null;
}) {
  const { t } = useTranslation();
  const dialog = useDialog();
  const [expanded, setExpanded] = useState(depth === 0);
  const hasChildren = node.children.length > 0;

  // v0.37.0 (D-2026-05-31-AC) — create a brand-new subdirectory under this
  // node, then pick it (the caller flows it into create() → name prompt).
  const handleNewFolder = async () => {
    if (!workspaceRoot) return;
    const name = await dialog.prompt({ message: t("dirPicker.newFolderPrompt") });
    if (name === null) return;
    const trimmed = name.trim();
    if (!trimmed) return;
    const childRel = node.rel === "." ? trimmed : `${node.rel}/${trimmed}`;
    const { rel } = await createWorkspaceDir(workspaceRoot, childRel);
    onPick(rel);
  };
  return (
    <div>
      <div
        className="flex items-center gap-1 rounded px-1 py-0.5 hover:bg-surface-muted"
        style={{ paddingLeft: depth * 14 + 4 }}
      >
        {hasChildren ? (
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="w-4 text-fg-faint"
            aria-label={expanded ? "collapse" : "expand"}
          >
            {expanded ? "▾" : "▸"}
          </button>
        ) : (
          <span className="w-4" />
        )}
        <span className="flex-1 truncate text-fg">
          {node.rel === "." ? t("dirPicker.root") : node.name}
        </span>
        {node.has_plot && (
          <span className="rounded bg-ok-soft px-1 text-[10px] text-ok-fg">
            {t("dirPicker.hasProject")}
          </span>
        )}
        <button
          type="button"
          onClick={handleNewFolder}
          className="rounded border border-line-strong px-1.5 py-0.5 text-[10px] font-medium text-fg-secondary hover:bg-surface-subtle"
        >
          {t("dirPicker.newFolder")}
        </button>
        <button
          type="button"
          onClick={() => onPick(node.rel)}
          className="rounded bg-surface-inverse px-1.5 py-0.5 text-[10px] font-medium text-fg-inverse hover:bg-surface-inverse"
        >
          {node.has_plot ? t("dirPicker.open") : t("dirPicker.createHere")}
        </button>
      </div>
      {expanded &&
        node.children.map((c) => (
          <TreeRow
            key={c.rel}
            node={c}
            depth={depth + 1}
            onPick={onPick}
            workspaceRoot={workspaceRoot}
          />
        ))}
    </div>
  );
}
