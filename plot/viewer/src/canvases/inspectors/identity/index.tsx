/**
 * Per-kind inspector for ``identity`` Foundation nodes. v0.15 Phase 2.3.
 */
import { useTranslation } from "react-i18next";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { DoDontFields } from "../shared/DoDontFields";
import type { KindInspectorProps } from "../types";

export function IdentityInspector(props: KindInspectorProps) {
  return (
    <BaseInspector {...props}>
      <IdentityFields node={props.node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface IdentityFieldsProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function IdentityFields({ node, onPatchNode }: IdentityFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-violet-200 bg-violet-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-violet-700">
        {t("kind.identity")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.description")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.description")}
        </span>
        <textarea
          rows={2}
          value={node.description ?? ""}
          onChange={(e) => onPatchNode({ description: e.target.value })}
          placeholder="이 속성이 어떻게 드러나는가"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
      <DoDontFields node={node} onPatchNode={onPatchNode} />
    </div>
  );
}
