/**
 * Chrome SSOT for every per-kind inspector. Wraps a per-kind body
 * component as ``children`` and renders the shared header (kind tag,
 * delete, width toggle, close), MD-warnings banner, label input,
 * long-form ``details.md`` section, and the actor-root toggle.
 *
 * Phase 2.0 introduces this shell. Phase 2.1+ per-kind wrappers
 * (``inspectors/{kind}/index.tsx``) drop their typed-field UI in via
 * the ``children`` slot.
 *
 * Width preference (narrow vs wide) persists across reloads via
 * localStorage — same key the legacy ``SketchInspector`` used so the
 * user's choice survives the migration.
 */
import { type ReactNode, useState } from "react";
import { useTranslation } from "react-i18next";
import type { CanvasKind, SketchNode } from "../../types";
import { DetailsSection } from "./DetailsSection";

const WIDTH_STORAGE_KEY = "plot.inspector.width";
type InspectorWidth = "narrow" | "wide";

function loadWidth(): InspectorWidth {
  if (typeof window === "undefined") return "narrow";
  const stored = window.localStorage.getItem(WIDTH_STORAGE_KEY);
  return stored === "wide" ? "wide" : "narrow";
}

export interface BaseInspectorProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
  onDeleteNode: (nodeId: string) => void;
  onClose: () => void;
  projectPath: string;
  projectId: string;
  canvasKind: CanvasKind;
  /** Per-kind body slot. Rendered between the label input and the
   *  DetailsSection — i.e. inside the scrollable body, after the
   *  shared chrome but before the long-form area. */
  children?: ReactNode;
}

export function BaseInspector({
  node,
  onPatchNode,
  onDeleteNode,
  onClose,
  projectPath,
  projectId,
  canvasKind,
  children,
}: BaseInspectorProps) {
  const { t } = useTranslation();
  const [width, setWidth] = useState<InspectorWidth>(loadWidth);
  const toggleWidth = () => {
    const next: InspectorWidth = width === "narrow" ? "wide" : "narrow";
    setWidth(next);
    try {
      window.localStorage.setItem(WIDTH_STORAGE_KEY, next);
    } catch {
      // ignore storage quota errors; width choice is a nicety, not essential.
    }
  };

  // v0.12.6 — service is a category leaf in v0.12; the "root" concept
  // no longer applies to it. Only actor still carries it.
  const canToggleRoot = !node.parent_id && node.kind === "actor";

  return (
    <aside
      className={
        "pointer-events-auto absolute right-0 top-0 z-10 flex h-full flex-col border-l border-slate-200 bg-white/95 shadow-sm backdrop-blur " +
        (width === "wide" ? "w-[min(720px,60vw)]" : "w-80")
      }
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 px-3 py-2">
        <div className="flex items-center gap-2">
          <span
            className="inline-block h-3 w-3 shrink-0 rounded border border-slate-300"
            style={{ backgroundColor: node.color || "#ffffff" }}
            aria-hidden
          />
          <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
            {node.kind === "project"
              ? t("kind.project")
              : node.is_root && node.kind === "actor"
                ? t("kind.actorRoot")
                : node.kind
                  ? t(`kind.${node.kind}`)
                  : t("kind.node")}
          </span>
        </div>
        <div className="flex items-center gap-1">
          {/* Delete — hidden for the Project anchor and for Actor/Service roots. */}
          {node.kind !== "project" && !node.is_root && (
            <button
              type="button"
              onClick={() => {
                if (
                  window.confirm(t("inspector.confirmDelete", { name: node.label || node.id }))
                ) {
                  onDeleteNode(node.id);
                }
              }}
              aria-label={t("inspector.deleteNode")}
              className="rounded px-2 text-[10px] text-rose-600 hover:bg-rose-50"
              title={t("inspector.deleteNode")}
            >
              {t("inspector.deleteShort")}
            </button>
          )}
          <button
            type="button"
            onClick={toggleWidth}
            aria-label={
              width === "wide" ? t("inspector.narrowInspector") : t("inspector.widenInspector")
            }
            title={width === "wide" ? t("inspector.narrow") : t("inspector.widen")}
            className="rounded px-2 text-slate-400 hover:bg-slate-100"
          >
            {width === "wide" ? "⇥" : "⇤"}
          </button>
          <button
            type="button"
            onClick={onClose}
            aria-label={t("inspector.closeInspector")}
            className="rounded px-2 text-slate-400 hover:bg-slate-100"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto p-3">
        {/* MD parse warnings — surfaced first so the user sees the problem
            before editing. */}
        {node._md_warnings && node._md_warnings.length > 0 && (
          <div className="mb-3 rounded border border-amber-300 bg-amber-50 p-2 text-[11px] text-amber-900">
            <div className="mb-1 font-semibold">{t("inspector.mdWarnings")}</div>
            <ul className="ml-4 list-disc">
              {node._md_warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
            {node.details_path && (
              <p
                className="mt-1 text-[10px] text-amber-800"
                dangerouslySetInnerHTML={{
                  __html: t("inspector.mdWarningsFixHint", { path: node.details_path }),
                }}
              />
            )}
          </div>
        )}

        {/* Label */}
        <label className="mb-3 block">
          <span className="text-xs font-semibold text-slate-600">{t("inspector.label")}</span>
          <input
            type="text"
            value={node.label}
            onChange={(e) => onPatchNode({ label: e.target.value })}
            className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
          />
        </label>

        {/* Per-kind body */}
        {children}

        {/* Long-form details.md (chrome SSOT — every kind gets it). */}
        <DetailsSection
          node={node}
          projectPath={projectPath}
          projectId={projectId}
          canvasKind={canvasKind}
          onPatchNode={onPatchNode}
        />

        {/* Actor-root toggle — only for top-level actor. */}
        {canToggleRoot && (
          <label className="mb-4 flex items-center gap-2 text-xs text-slate-700">
            <input
              type="checkbox"
              checked={node.is_root}
              onChange={(e) => onPatchNode({ is_root: e.target.checked })}
              className="accent-indigo-600"
            />
            <span>
              Mark as <strong>Actor Root</strong> (centre of its tree)
            </span>
          </label>
        )}
      </div>
    </aside>
  );
}
