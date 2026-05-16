/**
 * Per-kind inspector for ``step`` nodes (procedural step inside a
 * service_detail canvas). v0.15 Phase 2.2.
 */
import { useTranslation } from "react-i18next";
import type { StepJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import { MdTextarea } from "../shared/MdTextarea";
import type { KindInspectorProps } from "../types";

export function StepInspector(props: KindInspectorProps) {
  if (props.node.kind !== "step") return null;
  const node = props.node;
  return (
    <BaseInspector {...props} hideDetailsSection>
      <StepFields node={node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface StepFieldsProps {
  node: StepJson;
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
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.outcome")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.outcome")}
        </span>
        <MdTextarea
          value={node.outcome ?? ""}
          onChange={(v) => onPatchNode({ outcome: v })}
          placeholder="이 단계 끝나면 어떤 상태?"
        />
      </label>
      <BodyField value={node.body ?? ""} onChange={(body) => onPatchNode({ body })} />
    </div>
  );
}
