/**
 * Per-kind inspector for ``actor`` nodes — class of people in the
 * value economy. Carries side (operator vs user) + motivation + pain.
 *
 * v0.15 Phase 2.8. v0.30.4 (D-2026-05-31-G): shows fields **inherited**
 * from the actor's parent (via inheritance edges) as a greyed caption,
 * so the user sees what the actor effectively *is* without it being
 * baked in. Typing a value overrides the inheritance.
 */
import { useTranslation } from "react-i18next";
import type { ActorJson } from "../../../domain";
import {
  effectiveActorFields,
  type EffectiveField,
} from "../../../domain/actorInheritance";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import { MdTextarea } from "../shared/MdTextarea";
import type { KindInspectorProps } from "../types";

export function ActorInspector(props: KindInspectorProps) {
  if (props.node.kind !== "actor") return null;
  const node = props.node;
  const eff = effectiveActorFields(node.id, props.allNodes, props.allEdges);
  return (
    <BaseInspector {...props} hideDetailsSection>
      <ActorFields node={node} onPatchNode={props.onPatchNode} eff={eff} />
    </BaseInspector>
  );
}

interface ActorFieldsProps {
  node: ActorJson;
  onPatchNode: (patch: Partial<SketchNode>) => void;
  eff: ReturnType<typeof effectiveActorFields>;
}

/** Greyed caption shown when a field's value is inherited from a parent
 *  actor (own value empty). */
function Inherited({ field }: { field: EffectiveField }) {
  const { t } = useTranslation();
  if (field.source !== "inherited" || !field.value) return null;
  const preview = field.value.length > 60 ? `${field.value.slice(0, 60)}…` : field.value;
  return (
    <p className="mt-0.5 text-[10px] italic text-slate-400">
      ↳ {t("inspector.inheritedFrom", { from: field.fromLabel })}: {preview}
    </p>
  );
}

function ActorFields({ node, onPatchNode, eff }: ActorFieldsProps) {
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
        <Inherited field={eff.side} />
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
        <Inherited field={eff.motivation} />
      </label>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.pain")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.pain")}</span>
        <MdTextarea
          value={node.pain ?? ""}
          onChange={(v) => onPatchNode({ pain: v })}
          placeholder="겪는 어려움 / 좌절"
        />
        <Inherited field={eff.pain} />
      </label>
      <BodyField value={node.body ?? ""} onChange={(body) => onPatchNode({ body })} />
      <Inherited field={eff.body} />
    </div>
  );
}
