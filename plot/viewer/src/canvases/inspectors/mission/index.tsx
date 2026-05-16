/**
 * Per-kind inspector for ``mission`` Foundation nodes. v0.17 Phase 1
 * (D-2026-05-16-A): every typed-text field value (``what_we_do`` /
 * ``why`` / ``direction`` / ``body``) is an MD-formatted string in
 * JSON. The DetailsSection MD-editor surface is hidden — JSON SSOT
 * means no MD file editing.
 */
import { useTranslation } from "react-i18next";
import type { MissionJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import type { KindInspectorProps } from "../types";

export function MissionInspector(props: KindInspectorProps) {
  if (props.node.kind !== "mission") return null;
  const node = props.node;
  return (
    <BaseInspector {...props} hideDetailsSection>
      <MissionFields node={node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface MissionFieldsProps {
  node: MissionJson;
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
          className="mt-1 w-full resize-y whitespace-pre-wrap rounded border border-slate-300 px-2 py-1 font-mono text-sm focus:border-indigo-600 focus:outline-none"
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
          className="mt-1 w-full resize-y whitespace-pre-wrap rounded border border-slate-300 px-2 py-1 font-mono text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
      <label className="mb-2 block">
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
          className="mt-1 w-full resize-y whitespace-pre-wrap rounded border border-slate-300 px-2 py-1 font-mono text-sm focus:border-indigo-600 focus:outline-none"
        />
      </label>
      <BodyField value={node.body ?? ""} onChange={(body) => onPatchNode({ body })} />
    </div>
  );
}
