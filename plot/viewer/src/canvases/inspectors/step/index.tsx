/**
 * Per-kind inspector for ``step`` nodes (procedural step inside a
 * service_detail canvas). v0.15 Phase 2.2.
 */
import { useTranslation } from "react-i18next";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import type { KindInspectorProps } from "../types";

export function StepInspector(props: KindInspectorProps) {
  return (
    <BaseInspector {...props}>
      <StepFields node={props.node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface StepFieldsProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function StepFields({ node, onPatchNode }: StepFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-indigo-200 bg-indigo-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-indigo-700">
        {t("kind.step")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.order")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.order")}</span>
        <input
          type="number"
          value={node.order ?? ""}
          onChange={(e) => {
            const raw = e.target.value;
            onPatchNode({ order: raw === "" ? null : Number(raw) });
          }}
          placeholder="1, 2, 3, …"
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
      <label className="block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.outcome")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.outcome")}
        </span>
        <textarea
          rows={2}
          value={node.outcome ?? ""}
          onChange={(e) => onPatchNode({ outcome: e.target.value })}
          placeholder="이 단계 끝나면 어떤 상태?"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
    </div>
  );
}
