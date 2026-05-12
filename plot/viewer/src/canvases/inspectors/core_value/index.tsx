/**
 * Per-kind inspector for ``core_value`` Foundation nodes. v0.15 Phase 2.3.
 */
import { useTranslation } from "react-i18next";
import type { CoreValueJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { DoDontFields } from "../shared/DoDontFields";
import type { KindInspectorProps } from "../types";

export function CoreValueInspector(props: KindInspectorProps) {
  if (props.node.kind !== "core_value") return null;
  const node = props.node;
  return (
    <BaseInspector {...props}>
      <CoreValueFields node={node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface CoreValueFieldsProps {
  node: CoreValueJson;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function CoreValueFields({ node, onPatchNode }: CoreValueFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-amber-200 bg-amber-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-amber-700">
        {t("kind.core_value")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.definition")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.definition")}
        </span>
        <textarea
          rows={2}
          value={node.definition ?? ""}
          onChange={(e) => onPatchNode({ definition: e.target.value })}
          placeholder="한두 문장으로"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
      <DoDontFields node={node} onPatchNode={onPatchNode} />
    </div>
  );
}
