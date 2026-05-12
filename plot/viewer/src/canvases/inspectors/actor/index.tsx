/**
 * Per-kind inspector for ``actor`` nodes — class of people in the
 * value economy. Carries side (operator vs user) + motivation + pain.
 *
 * v0.15 Phase 2.8.
 */
import { useTranslation } from "react-i18next";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import type { KindInspectorProps } from "../types";

export function ActorInspector(props: KindInspectorProps) {
  return (
    <BaseInspector {...props}>
      <ActorFields node={props.node} onPatchNode={props.onPatchNode} />
      {/* v0.3 placeholder — actor composition still deferred for non-root. */}
      {!props.node.is_root && <ActorCompositionPlaceholder />}
    </BaseInspector>
  );
}

interface ActorFieldsProps {
  node: SketchNode;
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
        <textarea
          rows={2}
          value={node.motivation ?? ""}
          onChange={(e) => onPatchNode({ motivation: e.target.value })}
          placeholder="이 액터가 무엇을 얻으려 하는가"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-rose-600 focus:outline-none"
        />
      </label>
      <label className="block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.pain")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.pain")}</span>
        <textarea
          rows={2}
          value={node.pain ?? ""}
          onChange={(e) => onPatchNode({ pain: e.target.value })}
          placeholder="겪는 어려움 / 좌절"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-rose-600 focus:outline-none"
        />
      </label>
    </div>
  );
}

function ActorCompositionPlaceholder() {
  const { t } = useTranslation();
  return (
    <div className="rounded border border-dashed border-slate-300 p-3 text-xs italic text-slate-400">
      {t("inspector.actorCompositionDeferred")}
    </div>
  );
}
