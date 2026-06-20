/**
 * Multi-select reference chips for the Service inspector (D-2026-06-17-B /
 * D-2026-06-20-F, Option B). Renders the service's picked master ids as
 * removable chips (label derived from the master node) + an "add" dropdown
 * of the not-yet-picked masters. Pick-only for now; the pick-OR-create
 * affordance (D-2026-06-19-C) is a tracked follow-up.
 */
import { useTranslation } from "react-i18next";
import type { SketchNode } from "../../../types";

interface RefChipsProps {
  /** The question this field asks (its title). */
  label: string;
  /** One-line hint shown next to the title. */
  hint: string;
  /** Currently picked master ids. */
  ids: string[];
  /** Master candidates to pick from (e.g. availableActors). */
  available: SketchNode[];
  onChange: (ids: string[]) => void;
}

export function RefChips({ label, hint, ids, available, onChange }: RefChipsProps) {
  const { t } = useTranslation();
  const byId = new Map(available.map((n) => [n.id, n]));
  const unpicked = available.filter((n) => !ids.includes(n.id));

  return (
    <div className="mb-3 block">
      <span className="text-xs font-semibold text-fg">{label}</span>
      <span className="ml-1 text-[10px] text-fg-muted">— {hint}</span>
      <div className="mt-1 flex flex-wrap gap-1">
        {ids.length === 0 && (
          <span className="text-[11px] italic text-fg-faint">{t("inspector.refChips.empty")}</span>
        )}
        {ids.map((id) => {
          const master = byId.get(id);
          const text = master?.label?.trim() || t("inspector.refChips.missing");
          return (
            <span
              key={id}
              className="inline-flex items-center gap-1 rounded-full border border-line-strong bg-surface-muted px-2 py-0.5 text-[11px] text-fg"
              title={master ? undefined : id}
            >
              {text}
              <button
                type="button"
                aria-label={t("inspector.refChips.remove")}
                className="text-fg-muted hover:text-warn-fg"
                onClick={() => onChange(ids.filter((x) => x !== id))}
              >
                ✕
              </button>
            </span>
          );
        })}
      </div>
      {unpicked.length > 0 && (
        <select
          value=""
          onChange={(e) => {
            if (e.target.value) onChange([...ids, e.target.value]);
          }}
          className="mt-1 w-full rounded border border-line-strong px-2 py-1 text-sm focus:border-info focus:outline-none"
        >
          <option value="">{t("inspector.refChips.add")}</option>
          {unpicked.map((n) => (
            <option key={n.id} value={n.id}>
              {n.label?.trim() || n.id}
            </option>
          ))}
        </select>
      )}
    </div>
  );
}
