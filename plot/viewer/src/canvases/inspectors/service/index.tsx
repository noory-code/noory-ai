/**
 * Per-kind inspector for ``service`` nodes — the value-creating hub
 * (PHILOSOPHY P5). D-2026-06-17-B / D-2026-06-20-F: **5 question-titled
 * fields** — 2 typed-text (왜 필요한가? / 뭐가 좋아지나?) + 3 multi-select
 * reference chip lists (누가 참여하나? = actors, 뭘 양보 못 하나? = core_values,
 * 어떤 결로 다가가나? = identities). The old 9 free-text fields + the
 * composition (rules / contents) panels are gone — composition lives on the
 * Feature canvas, value-exchange detail is the service's 5 fields.
 */
import { useTranslation } from "react-i18next";
import type { ServiceJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { MdTextarea } from "../shared/MdTextarea";
import type { KindInspectorProps } from "../types";
import { RefChips } from "./RefChips";

export function ServiceInspector(props: KindInspectorProps) {
  if (props.node.kind !== "service") return null;
  const node = props.node;
  const {
    onPatchNode,
    readOnly,
    availableActors = [],
    availableValues = [],
    availableIdentities = [],
  } = props;
  return (
    <BaseInspector {...props} hideDetailsSection>
      {readOnly ? (
        <ServiceFieldsReadonly
          node={node}
          availableActors={availableActors}
          availableValues={availableValues}
          availableIdentities={availableIdentities}
        />
      ) : (
        <ServiceFields
          node={node}
          onPatchNode={onPatchNode}
          availableActors={availableActors}
          availableValues={availableValues}
          availableIdentities={availableIdentities}
        />
      )}
    </BaseInspector>
  );
}

interface ServiceFieldsProps {
  node: ServiceJson;
  onPatchNode: (patch: Partial<SketchNode>) => void;
  availableActors: SketchNode[];
  availableValues: SketchNode[];
  availableIdentities: SketchNode[];
}

function ServiceFields({
  node,
  onPatchNode,
  availableActors,
  availableValues,
  availableIdentities,
}: ServiceFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-info bg-info-soft/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-info-fg">
        {t("kind.service")}
      </div>
      {/* ① 누가 참여하나? — actors */}
      <RefChips
        label={t("inspector.service.q.participants")}
        hint={t("inspector.service.q.participantsHint")}
        ids={node.ref_actor_ids ?? []}
        available={availableActors}
        onChange={(ids) => onPatchNode({ ref_actor_ids: ids })}
      />
      {/* ② 왜 필요한가? — problem (typed) */}
      <ServiceTextarea
        label={t("inspector.service.q.problem")}
        hint={t("inspector.service.q.problemHint")}
        value={node.problem ?? ""}
        onChange={(v) => onPatchNode({ problem: v })}
        placeholder={t("inspector.service.q.problemPlaceholder")}
      />
      {/* ③ 뭐가 좋아지나? — value_created (typed) */}
      <ServiceTextarea
        label={t("inspector.service.q.valueCreated")}
        hint={t("inspector.service.q.valueCreatedHint")}
        value={node.value_created ?? ""}
        onChange={(v) => onPatchNode({ value_created: v })}
        placeholder={t("inspector.service.q.valueCreatedPlaceholder")}
      />
      {/* ④ 뭘 양보 못 하나? — core_values */}
      <RefChips
        label={t("inspector.service.q.values")}
        hint={t("inspector.service.q.valuesHint")}
        ids={node.ref_value_ids ?? []}
        available={availableValues}
        onChange={(ids) => onPatchNode({ ref_value_ids: ids })}
      />
      {/* ⑤ 어떤 결로 다가가나? — identities */}
      <RefChips
        label={t("inspector.service.q.identities")}
        hint={t("inspector.service.q.identitiesHint")}
        ids={node.ref_identity_ids ?? []}
        available={availableIdentities}
        onChange={(ids) => onPatchNode({ ref_identity_ids: ids })}
      />
    </div>
  );
}

interface ServiceFieldsReadonlyProps {
  node: ServiceJson;
  availableActors: SketchNode[];
  availableValues: SketchNode[];
  availableIdentities: SketchNode[];
}

/** Read-only summary of the 5 fields (D-2026-06-15-O) — the ServiceDetail
 *  fallback inspector. Shows only fields that carry content. */
function ServiceFieldsReadonly({
  node,
  availableActors,
  availableValues,
  availableIdentities,
}: ServiceFieldsReadonlyProps) {
  const { t } = useTranslation();
  const names = (ids: string[], pool: SketchNode[]): string => {
    const byId = new Map(pool.map((n) => [n.id, n]));
    return ids
      .map((id) => byId.get(id)?.label?.trim() || id)
      .filter(Boolean)
      .join(", ");
  };
  const rows = (
    [
      [t("inspector.service.q.participants"), names(node.ref_actor_ids ?? [], availableActors)],
      [t("inspector.service.q.problem"), node.problem ?? ""],
      [t("inspector.service.q.valueCreated"), node.value_created ?? ""],
      [t("inspector.service.q.values"), names(node.ref_value_ids ?? [], availableValues)],
      [
        t("inspector.service.q.identities"),
        names(node.ref_identity_ids ?? [], availableIdentities),
      ],
    ] as Array<[string, string]>
  ).filter(([, v]) => v.trim() !== "");
  return (
    <div className="mb-4 rounded border border-info bg-info-soft/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-info-fg">
        {t("kind.service")}
      </div>
      {rows.length === 0 ? (
        <div className="text-xs text-fg-muted">{t("inspector.readOnlyEmpty")}</div>
      ) : (
        rows.map(([label, value]) => (
          <div key={label} className="mb-2">
            <div className="text-xs font-semibold text-fg">{label}</div>
            <div className="mt-0.5 whitespace-pre-wrap text-sm text-fg-secondary">{value}</div>
          </div>
        ))
      )}
    </div>
  );
}

interface ServiceTextareaProps {
  label: string;
  hint: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}

function ServiceTextarea({ label, hint, value, onChange, placeholder }: ServiceTextareaProps) {
  return (
    <label className="mb-2 block">
      <span className="text-xs font-semibold text-fg">{label}</span>
      <span className="ml-1 text-[10px] text-fg-muted">— {hint}</span>
      <MdTextarea value={value ?? ""} onChange={onChange} placeholder={placeholder} />
    </label>
  );
}
