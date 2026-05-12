/**
 * Per-kind inspector for ``mission`` Foundation nodes. v0.15 Phase 2.4.
 */
import { useTranslation } from "react-i18next";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import type { KindInspectorProps } from "../types";

export function MissionInspector(props: KindInspectorProps) {
  return (
    <BaseInspector {...props}>
      <MissionFields node={props.node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface MissionFieldsProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function MissionFields({ node, onPatchNode }: MissionFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-indigo-200 bg-indigo-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-indigo-700">
        {t("kind.mission")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.whatWeDo")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.whatWeDo")}
        </span>
        <textarea
          rows={2}
          value={node.what_we_do ?? ""}
          onChange={(e) => onPatchNode({ what_we_do: e.target.value })}
          placeholder="우리는 매일 …"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.why")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.why")}</span>
        <textarea
          rows={2}
          value={node.why ?? ""}
          onChange={(e) => onPatchNode({ why: e.target.value })}
          placeholder="사람들이 … 하기를 바라서"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
      <label className="block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.direction")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.direction")}
        </span>
        <textarea
          rows={2}
          value={node.direction ?? ""}
          onChange={(e) => onPatchNode({ direction: e.target.value })}
          placeholder="누구나 … 인 일상으로"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
    </div>
  );
}
