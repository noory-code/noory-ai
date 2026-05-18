/**
 * Per-kind inspector for ``actor`` nodes — class of people in the
 * value economy. Carries side (operator vs user) + motivation + pain.
 *
 * v0.15 Phase 2.8.
 */
import { useTranslation } from "react-i18next";
import type { ActorJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import { MdTextarea } from "../shared/MdTextarea";
import type { KindInspectorProps } from "../types";

export function ActorInspector(props: KindInspectorProps) {
  if (props.node.kind !== "actor") return null;
  const node = props.node;
  return (
    <BaseInspector {...props} hideDetailsSection>
      <ActorFields node={node} onPatchNode={props.onPatchNode} />
      {/* v0.24.11 (D-2026-05-19-D) — v0.3 ActorCompositionPlaceholder
          removed alongside actor.is_root deprecation; the message was a
          vague "coming in v0.3" notice that referenced the now-deleted
          is_root semantic. */}
    </BaseInspector>
  );
}

interface ActorFieldsProps {
  node: ActorJson;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function ActorFields({ node, onPatchNode }: ActorFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-rose-200 bg-rose-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-rose-700">
        {t("kind.actor")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.side")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.side")}</span>
        <select
          value={node.side ?? ""}
          onChange={(e) =>
            onPatchNode({
              side: e.target.value === "" ? null : (e.target.value as "operator" | "user"),
            })
          }
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-rose-600 focus:outline-none"
        >
          <option value="">{t("inspector.unset")}</option>
          <option value="operator">{t("inspector.operatorOption")}</option>
          <option value="user">{t("inspector.userOption")}</option>
        </select>
      </label>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.motivation")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.motivation")}
        </span>
        <MdTextarea
          value={node.motivation ?? ""}
          onChange={(v) => onPatchNode({ motivation: v })}
          placeholder="이 액터가 무엇을 얻으려 하는가"
        />
      </label>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.pain")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.pain")}</span>
        <MdTextarea
          value={node.pain ?? ""}
          onChange={(v) => onPatchNode({ pain: v })}
          placeholder="겪는 어려움 / 좌절"
        />
      </label>
      <BodyField value={node.body ?? ""} onChange={(body) => onPatchNode({ body })} />
    </div>
  );
}

