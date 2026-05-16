/**
 * Shared MD-aware ``body`` field — long-form notes for the 10
 * publish-eligible kinds per D-2026-05-13-O #2 + D-2026-05-16-F.
 * Value is an MD-formatted string in JSON SSOT.
 * v0.19.0 (D-2026-05-17-B) — backed by CodeMirror 6 + markdown lang
 * (syntax highlight). raw MD remains the SSOT.
 */
import { useTranslation } from "react-i18next";
import { MdTextarea } from "./MdTextarea";

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
      <MdTextarea value={value} onChange={onChange} minLines={4} />
    </label>
  );
}
