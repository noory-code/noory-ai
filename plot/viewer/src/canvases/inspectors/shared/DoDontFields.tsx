/**
 * Shared do / dont pair (positive example + anti-pattern). Used by
 * CoreValue + Identity per-kind inspectors per ``CONCEPTS.md``
 * "AI-first" principle: every value / identity aspect carries a
 * concrete positive + negative example so an LLM can mimic the
 * persona deterministically.
 */
import { useTranslation } from "react-i18next";
import type { SketchNode } from "../../../types";
import { MdTextarea } from "./MdTextarea";

/** Any node that carries the do / dont AI-first pair (CoreValue,
 *  Identity, Service all do; the type-narrowed prop accepts any of
 *  them via a structural subset). Both fields are optional on the
 *  Json shape — the component coerces undefined to "". */
export interface DoDontCarrier {
  do?: string;
  dont?: string;
}

export interface DoDontFieldsProps {
  node: DoDontCarrier;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

export function DoDontFields({ node, onPatchNode }: DoDontFieldsProps) {
  const { t } = useTranslation();
  return (
    <>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-emerald-700">{t("inspector.field.do")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.do")}</span>
        <MdTextarea
          value={node.do ?? ""}
          onChange={(v) => onPatchNode({ do: v })}
          placeholder="이렇게 행동/표현한다"
        />
      </label>
      <label className="block">
        <span className="text-xs font-semibold text-rose-700">{t("inspector.field.dont")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.dont")}</span>
        <MdTextarea
          value={node.dont ?? ""}
          onChange={(v) => onPatchNode({ dont: v })}
          placeholder="이렇게는 안 한다"
        />
      </label>
    </>
  );
}
