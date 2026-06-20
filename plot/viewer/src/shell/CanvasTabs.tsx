/**
 * Top-of-canvas tab strip — Foundation / Actors / Services.
 * Extracted from ``App.tsx`` (v0.16.2).
 *
 * v0.24.13 (D-2026-05-21-B) — right-side "Mark session…" button replaced
 * with the BlueprintPublishButton. Project versioning (semver) takes
 * over the user-facing "freeze the design" surface; ad-hoc git tags via
 * the API still work but are no longer the primary UX.
 *
 * The ``CanvasTab`` discriminator + ``CANVAS_TAB_IDS`` SSOT live here
 * because every consumer (App.tsx, the URL-sync hook, this strip)
 * imports them from one place.
 */
import { useTranslation } from "react-i18next";
import type { BlueprintBump } from "../api";
import { BlueprintPublishButton } from "./BlueprintPublishButton";

export type CanvasTab = "foundation" | "actors" | "services";

export const CANVAS_TAB_IDS: readonly CanvasTab[] = [
  "foundation",
  "actors",
  "services",
];

interface CanvasTabsProps {
  active: CanvasTab;
  onSelect: (tab: CanvasTab) => void;
  blueprintVersion: string;
  onPublishBlueprint: (bump: BlueprintBump) => void | Promise<void>;
  publishDisabled?: boolean;
  /** Active project NAME, shown centered in the tab bar (v0.34.3,
   *  D-2026-05-31-Q). The workspace root path lives in the header instead. */
  projectName: string | null;
  /** Dynamic feature tab (D-2026-06-15-H). When a service node is
   *  selected on the Services canvas, a ``{label}`` tab is appended after
   *  Services; ``detailActive`` says it's the current view, and the × removes
   *  it. Omitted / ``null`` id = no detail tab. */
  detailFeatureId?: string | null;
  detailLabel?: string | null;
  detailActive?: boolean;
  onSelectDetail?: () => void;
  onCloseDetail?: () => void;
}

export function CanvasTabs({
  active,
  onSelect,
  blueprintVersion,
  onPublishBlueprint,
  publishDisabled,
  projectName,
  detailFeatureId,
  detailLabel,
  detailActive,
  onSelectDetail,
  onCloseDetail,
}: CanvasTabsProps) {
  const { t } = useTranslation();
  return (
    <div
      role="tablist"
      aria-label={t("canvas.aria")}
      className="flex items-center justify-between border-b border-line bg-surface px-3"
    >
      <div className="flex items-center gap-1">
        {CANVAS_TAB_IDS.map((id) => {
          // An F/A/S tab is selected only when the detail tab isn't the
          // active view (D-2026-06-15-H).
          const selected = id === active && !detailActive;
          return (
            <button
              key={id}
              type="button"
              role="tab"
              aria-selected={selected}
              onClick={() => onSelect(id)}
              className={
                selected
                  ? "border-b-2 border-fg-strong px-4 py-2 text-sm font-medium text-fg-strong"
                  : "border-b-2 border-transparent px-4 py-2 text-sm text-fg-muted hover:text-fg-strong"
              }
            >
              {t(`canvas.tabs.${id}`)}
            </button>
          );
        })}
        {detailFeatureId && (
          <span
            className={
              detailActive
                ? "flex items-center gap-1 border-b-2 border-fg-strong pl-4 pr-2 py-2 text-sm font-medium text-fg-strong"
                : "flex items-center gap-1 border-b-2 border-transparent pl-4 pr-2 py-2 text-sm text-fg-muted hover:text-fg-strong"
            }
          >
            <button
              type="button"
              role="tab"
              aria-selected={detailActive}
              onClick={onSelectDetail}
              className="max-w-[12rem] truncate"
              title={detailLabel ?? undefined}
            >
              {detailLabel || t("canvas.tabs.services")}
            </button>
            <button
              type="button"
              aria-label={t("canvas.closeDetailTab")}
              onClick={onCloseDetail}
              className="shrink-0 rounded px-1 text-xs text-fg-muted hover:bg-surface-muted hover:text-fg-strong"
            >
              ✕
            </button>
          </span>
        )}
      </div>
      {/* v0.34.7 (D-2026-05-31-U) — project name + its blueprint version
          (version belongs to the PROJECT, not the repo path in the header). */}
      <span className="flex min-w-0 flex-1 items-center justify-center gap-2 px-4">
        <span className="truncate text-sm font-medium text-fg">{projectName ?? ""}</span>
        {projectName && (
          <span
            className="shrink-0 rounded bg-surface-subtle px-1.5 py-0.5 font-mono text-[10px] tabular-nums text-fg-secondary"
            title="Blueprint version"
          >
            {blueprintVersion}
          </span>
        )}
      </span>
      <BlueprintPublishButton
        currentVersion={blueprintVersion}
        onPublish={onPublishBlueprint}
        disabled={publishDisabled}
      />
    </div>
  );
}
