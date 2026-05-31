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
}

export function CanvasTabs({
  active,
  onSelect,
  blueprintVersion,
  onPublishBlueprint,
  publishDisabled,
  projectName,
}: CanvasTabsProps) {
  const { t } = useTranslation();
  return (
    <div
      role="tablist"
      aria-label={t("canvas.aria")}
      className="flex items-center justify-between border-b border-slate-200 bg-white px-3"
    >
      <div className="flex items-center gap-1">
        {CANVAS_TAB_IDS.map((id) => {
          const selected = id === active;
          return (
            <button
              key={id}
              type="button"
              role="tab"
              aria-selected={selected}
              onClick={() => onSelect(id)}
              className={
                selected
                  ? "border-b-2 border-slate-900 px-4 py-2 text-sm font-medium text-slate-900"
                  : "border-b-2 border-transparent px-4 py-2 text-sm text-slate-500 hover:text-slate-800"
              }
            >
              {t(`canvas.tabs.${id}`)}
            </button>
          );
        })}
      </div>
      <span className="min-w-0 flex-1 truncate px-4 text-center text-sm font-medium text-slate-700">
        {projectName ?? ""}
      </span>
      <BlueprintPublishButton
        currentVersion={blueprintVersion}
        onPublish={onPublishBlueprint}
        disabled={publishDisabled}
      />
    </div>
  );
}
