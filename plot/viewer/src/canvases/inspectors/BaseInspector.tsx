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
import { canPublish } from "../../domain/publishEligibility";
import type { CanvasKind, SketchNode } from "../../types";
import { DetailsSection } from "./DetailsSection";
import { PublishedVersionsSection } from "./shared/PublishedVersionsSection";
import { useDialog } from "../../shell/dialog/DialogProvider";

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
  /** v0.18.0 Phase 3 (D-2026-05-16-E): publish the selected node.
   *  Returning a promise allows the caller to surface errors as
   *  toasts; the button stays enabled, the confirm dialog is the
   *  user-side debounce. Optional so legacy callers compile. */
  onPublishNode?: (nodeId: string) => void;
  /** v0.23.x (D-2026-05-17-J): unpublish — git revert the most recent
   *  publish commit for this node. Only surfaced when
   *  ``node.version !== "v1.0"`` (i.e. there's something to undo). */
  onUnpublishNode?: (nodeId: string) => void;
  projectPath: string;
  projectId: string;
  canvasKind: CanvasKind;
  /** v0.27.13 (D-2026-05-28-H): service_id for service_detail canvas.
   *  Required for the published-versions fetch; the backend returns
   *  500 without it (read_canvas raises ValueError on service_detail
   *  without service_id). */
  serviceId?: string;
  /** Per-kind body slot. Rendered between the label input and the
   *  DetailsSection — i.e. inside the scrollable body, after the
   *  shared chrome but before the long-form area. */
  children?: ReactNode;
  /** v0.17 Phase 1 (D-2026-05-16-A): hide the DetailsSection (MD
   *  file editor + "Create details" button) for kinds whose long-form
   *  content has been absorbed into JSON SSOT typed fields (currently
   *  Foundation mission / core_value / identity). Default false. */
  hideDetailsSection?: boolean;
  /** D-2026-06-15-O — render the shared chrome read-only: label input
   *  becomes non-editable, and the delete / close / publish / details
   *  affordances are hidden. The per-kind body slot is responsible for
   *  rendering its own fields read-only. Default false. */
  readOnly?: boolean;
}

export function BaseInspector({
  node,
  onPatchNode,
  onDeleteNode,
  onClose,
  onPublishNode,
  onUnpublishNode,
  projectPath,
  projectId,
  canvasKind,
  serviceId,
  children,
  hideDetailsSection = false,
  readOnly = false,
}: BaseInspectorProps) {
  const { t } = useTranslation();
  const dialog = useDialog();
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

  // v0.24.11 (D-2026-05-19-D) — actor.is_root semantically deprecated.
  // Every actor is a Symbol candidate (referenceable from Service canvas
  // via actor_ref); the boolean toggle no longer distinguishes anything
  // for the user. Toggle removed entirely. Service.is_root stays as the
  // ServiceDetail anchor marker (set by create flow, not user toggle).
  const canToggleRoot = false;

  return (
    <aside
      className={
        "pointer-events-auto absolute right-0 top-0 z-10 flex h-full flex-col border-l border-line bg-surface/95 shadow-sm backdrop-blur " +
        (width === "wide" ? "w-[min(720px,60vw)]" : "w-80")
      }
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-line px-3 py-2">
        <div className="flex items-center gap-2">
          <span
            className="inline-block h-3 w-3 shrink-0 rounded border border-line-strong"
            style={{ backgroundColor: node.color || "#ffffff" }}
            aria-hidden
          />
          <span className="text-[10px] font-semibold uppercase tracking-wide text-fg-muted">
            {/* v0.24.11 (D-2026-05-19-D) — actor.is_root is no longer a
                user-visible distinction; badge is always "액터" / "Actor". */}
            {node.kind === "project"
              ? t("kind.project")
              : node.kind
                ? t(`kind.${node.kind}`)
                : t("kind.node")}
          </span>
          {/* v0.18.0 Phase 3 (D-2026-05-16-E) — per-node version badge.
              Code value (literal vMAJOR.MINOR); no i18n. */}
          {node.kind !== "project" && (
            <span
              className="font-mono text-[10px] tabular-nums text-fg-faint"
              aria-label={`version ${node.version}`}
            >
              {node.version}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          {/* v0.23.2 (D-2026-05-17-K) — publish/unpublish buttons moved
              from this header cluster to the sticky footer below.
              Header now only carries chrome (delete / widen / close). */}
          {/* Delete — hidden for the Project anchor and for Actor/Service roots.
              Also hidden in read-only mode (D-2026-06-15-O). */}
          {!readOnly && node.kind !== "project" && !node.is_root && (
            <button
              type="button"
              onClick={async () => {
                if (
                  await dialog.confirm({
                    message: t("inspector.confirmDelete", { name: node.label || node.id }),
                    danger: true,
                  })
                ) {
                  onDeleteNode(node.id);
                }
              }}
              aria-label={t("inspector.deleteNode")}
              className="rounded px-2 text-[10px] text-danger hover:bg-danger-soft"
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
            className="rounded px-2 text-fg-faint hover:bg-surface-subtle"
          >
            {width === "wide" ? "⇥" : "⇤"}
          </button>
          {/* Close — hidden in read-only mode: the fallback inspector is the
              detail canvas's default panel, so there is nothing to close
              (D-2026-06-15-O). */}
          {!readOnly && (
            <button
              type="button"
              onClick={onClose}
              aria-label={t("inspector.closeInspector")}
              className="rounded px-2 text-fg-faint hover:bg-surface-subtle"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto p-3">
        {/* MD parse warnings — surfaced first so the user sees the problem
            before editing. */}
        {node._md_warnings && node._md_warnings.length > 0 && (
          <div className="mb-3 rounded border border-warn-line bg-warn-soft p-2 text-[11px] text-warn-fg">
            <div className="mb-1 font-semibold">{t("inspector.mdWarnings")}</div>
            <ul className="ml-4 list-disc">
              {node._md_warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
            {node.details_path && (
              <p
                className="mt-1 text-[10px] text-warn-fg"
                dangerouslySetInnerHTML={{
                  __html: t("inspector.mdWarningsFixHint", { path: node.details_path }),
                }}
              />
            )}
          </div>
        )}

        {/* Label */}
        <label className="mb-3 block">
          <span className="text-xs font-semibold text-fg-secondary">{t("inspector.label")}</span>
          <input
            type="text"
            value={node.label}
            onChange={(e) => onPatchNode({ label: e.target.value })}
            readOnly={readOnly}
            className={
              "mt-1 w-full rounded border border-line-strong px-2 py-1 text-sm focus:border-accent focus:outline-none" +
              (readOnly ? " cursor-default bg-surface-subtle text-fg-secondary" : "")
            }
          />
        </label>

        {/* Per-kind body */}
        {children}

        {/* Long-form details.md (chrome SSOT — every kind gets it,
            except Foundation typed-text kinds whose long-form content
            lives in JSON SSOT typed fields since v0.17 Phase 1). Hidden in
            read-only mode — the MD editor is an editing surface
            (D-2026-06-15-O). */}
        {!hideDetailsSection && !readOnly && (
          <DetailsSection
            node={node}
            projectPath={projectPath}
            projectId={projectId}
            canvasKind={canvasKind}
            onPatchNode={onPatchNode}
          />
        )}

        {/* v0.23.0 (D-2026-05-17-I) — Published versions list +
            click-to-open MD modal. Only for publish-eligible kinds. Hidden
            in read-only mode — keeps the always-mounted ServiceDetail
            fallback panel from firing a publish-history fetch (D-2026-06-15-O). */}
        {!readOnly && canPublish(node) && (
          <PublishedVersionsSection
            projectPath={projectPath}
            projectId={projectId}
            canvasKind={canvasKind}
            nodeId={node.id}
            serviceId={serviceId}
            refreshKey={node.version}
          />
        )}

        {/* Actor-root toggle — only for top-level actor. */}
        {canToggleRoot && (
          <label className="mb-4 flex items-center gap-2 text-xs text-fg">
            <input
              type="checkbox"
              checked={node.is_root}
              onChange={(e) => onPatchNode({ is_root: e.target.checked })}
              className="accent-accent"
            />
            <span>
              Mark as <strong>Actor Root</strong> (centre of its tree)
            </span>
          </label>
        )}
      </div>

      {/* v0.23.2 (D-2026-05-17-K) — sticky publish footer. Primary CTA
          surface for publish; unpublish is a small text link beneath
          when there's something to revert. Only rendered for
          publish-eligible kinds; the footer disappears entirely for
          project / is_root / *_ref nodes. */}
      {!readOnly && onPublishNode && canPublish(node) && (() => {
        const isDirty = node._dirty ?? true;
        const fromVersion = node.version;
        const nextMajor =
          parseInt(fromVersion.slice(1).split(".")[0], 10) + 1;
        const toVersion = `v${nextMajor}.0`;
        const kindLabel = t(`kind.${node.kind}`);
        const hasPublishToRevert = fromVersion !== "v1.0";
        return (
          <div className="shrink-0 border-t border-line bg-surface p-3">
            <button
              type="button"
              disabled={!isDirty}
              onClick={
                isDirty
                  ? async () => {
                      if (
                        await dialog.confirm({
                          message: t("inspector.confirmPublish", {
                            kind: kindLabel,
                            label: node.label || node.id,
                            fromVersion,
                            toVersion,
                          }),
                        })
                      ) {
                        onPublishNode(node.id);
                      }
                    }
                  : undefined
              }
              aria-label={t("inspector.publish")}
              title={
                isDirty
                  ? t("inspector.publishHint")
                  : t("inspector.publishDisabledHint", { version: fromVersion })
              }
              className={
                "w-full rounded-md px-3 py-2 text-sm font-semibold " +
                (isDirty
                  ? "bg-ok text-fg-inverse shadow-sm hover:bg-ok"
                  : "cursor-not-allowed bg-surface-subtle text-fg-faint")
              }
            >
              {t("inspector.publishShort")} → {toVersion}
            </button>
            {onUnpublishNode && hasPublishToRevert && (
              <div className="mt-2 text-center">
                <button
                  type="button"
                  onClick={async () => {
                    const prevMajor =
                      parseInt(fromVersion.slice(1).split(".")[0], 10) - 1;
                    const prevVersion = `v${prevMajor}.0`;
                    if (
                      await dialog.confirm({
                        message: t("inspector.confirmUnpublish", {
                          kind: kindLabel,
                          label: node.label || node.id,
                          fromVersion,
                          toVersion: prevVersion,
                        }),
                        danger: true,
                      })
                    ) {
                      onUnpublishNode(node.id);
                    }
                  }}
                  aria-label={t("inspector.unpublish")}
                  title={t("inspector.unpublishHint")}
                  className="text-[11px] text-warn-fg hover:underline"
                >
                  {t("inspector.unpublishShort")} {fromVersion}
                </button>
              </div>
            )}
          </div>
        );
      })()}
    </aside>
  );
}
