/**
 * Shared MD-aware ``body`` field — long-form notes for the 3 Foundation
 * typed-text kinds (mission / core_value / identity) per v0.17 Phase 1
 * (D-2026-05-16-A). The value is an MD-formatted string in JSON SSOT;
 * the textarea preserves newlines and uses monospace so the user can
 * edit raw MD syntax. No render preview in Phase 1.
 */
import { useTranslation } from "react-i18next";

export interface BodyFieldProps {
  value: string;
  onChange: (value: string) => void;
}

export function BodyField({ value, onChange }: BodyFieldProps) {
  const { t } = useTranslation();
  return (
    <label className="mt-2 block">
      <span className="text-xs font-semibold text-slate-700">{t("inspector.field.body")}</span>
      <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.body")}</span>
      <textarea
        rows={4}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full resize-y whitespace-pre-wrap rounded border border-slate-300 px-2 py-1 font-mono text-sm focus:border-indigo-600 focus:outline-none"
      />
    </label>
  );
}
