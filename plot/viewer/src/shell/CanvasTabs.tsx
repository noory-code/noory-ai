/**
 * Top-of-canvas tab strip — Foundation / Actors / Services.
 * Extracted from ``App.tsx`` (v0.16.2).
 *
 * The ``CanvasTab`` discriminator + ``CANVAS_TAB_IDS`` SSOT live here
 * because every consumer (App.tsx, the URL-sync hook, this strip)
 * imports them from one place.
 */
import { useTranslation } from "react-i18next";

export type CanvasTab = "foundation" | "actors" | "services";

export const CANVAS_TAB_IDS: readonly CanvasTab[] = [
  "foundation",
  "actors",
  "services",
];

interface CanvasTabsProps {
  active: CanvasTab;
  onSelect: (tab: CanvasTab) => void;
  onMarkSession: () => void;
}

export function CanvasTabs({ active, onSelect, onMarkSession }: CanvasTabsProps) {
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
      <button
        type="button"
        onClick={onMarkSession}
        className="rounded border border-slate-300 bg-white px-3 py-1 text-xs text-slate-700 hover:bg-slate-50"
        title={t("header.markSessionHint")}
      >
        {t("header.markSession")}
      </button>
    </div>
  );
}
