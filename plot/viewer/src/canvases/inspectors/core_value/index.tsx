/**
 * Per-kind inspector for ``core_value`` Foundation nodes. v0.17 Phase 1
 * (D-2026-05-16-A): every typed-text field value (``definition`` /
 * ``do`` / ``dont`` / ``body``) is an MD-formatted string in JSON.
 * The DetailsSection MD-editor surface is hidden — JSON SSOT means
 * no MD file editing.
 */
import { useTranslation } from "react-i18next";
import type { CoreValueJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import { DoDontFields } from "../shared/DoDontFields";
import { MdTextarea } from "../shared/MdTextarea";
import type { KindInspectorProps } from "../types";

export function CoreValueInspector(props: KindInspectorProps) {
  if (props.node.kind !== "core_value") return null;
  const node = props.node;
  return (
    <BaseInspector {...props} hideDetailsSection>
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
        <MdTextarea
          value={node.definition ?? ""}
          onChange={(v) => onPatchNode({ definition: v })}
          placeholder="한두 문장으로"
        />
      </label>
      <DoDontFields node={node} onPatchNode={onPatchNode} />
      <BodyField value={node.body ?? ""} onChange={(body) => onPatchNode({ body })} />
    </div>
  );
}
