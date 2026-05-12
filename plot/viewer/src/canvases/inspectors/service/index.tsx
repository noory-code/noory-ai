/**
 * Per-kind inspector for ``service`` nodes — the value-creating hub
 * (PHILOSOPHY P5). Renders Service typed fields + two CompositionList
 * panels (rules + contents) for the service's children.
 *
 * v0.15 Phase 2.9 — final per-kind vertical slice. Phase 2.10 then
 * deletes the legacy ``SketchInspector`` and retires the god types.ts
 * interface.
 */
import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { DoDontFields } from "../shared/DoDontFields";
import type { KindInspectorProps } from "../types";
import { CompositionList } from "./CompositionList";

export function ServiceInspector(props: KindInspectorProps) {
  const { node, allNodes, onPatchNode, onAddChild, onPatchChild, onRemoveChild, availableActors } =
    props;
  const { t } = useTranslation();
  const rules = useMemo(
    () => allNodes.filter((n) => n.parent_id === node.id && n.kind === "rule"),
    [allNodes, node.id],
  );
  const contents = useMemo(
    () => allNodes.filter((n) => n.parent_id === node.id && n.kind === "content"),
    [allNodes, node.id],
  );
  return (
    <BaseInspector {...props}>
      <ServiceFields node={node} onPatchNode={onPatchNode} />
      {onAddChild && onPatchChild && onRemoveChild && (
        <>
          <CompositionList
            title={t("composition.rules")}
            subtitle={t("composition.rulesSubtitle")}
            items={rules}
            onAdd={() => onAddChild(node.id, "rule")}
            onPatch={onPatchChild}
            onRemove={onRemoveChild}
            kind="rule"
            availableActors={availableActors}
          />
          <CompositionList
            title={t("composition.contents")}
            subtitle={t("composition.contentsSubtitle")}
            items={contents}
            onAdd={() => onAddChild(node.id, "content")}
            onPatch={onPatchChild}
            onRemove={onRemoveChild}
            kind="content"
            availableActors={availableActors}
          />
        </>
      )}
    </BaseInspector>
  );
}

interface ServiceFieldsProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function ServiceFields({ node, onPatchNode }: ServiceFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-sky-200 bg-sky-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-sky-700">
        {t("kind.service")}
      </div>
      <label className="mb-3 block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.targetSide")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.targetSide")}
        </span>
        <select
          value={node.target_side ?? ""}
          onChange={(e) => {
            const v = e.target.value;
            onPatchNode({
              target_side: v === "operator" || v === "user" || v === "both" ? v : null,
            });
          }}
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-sky-600 focus:outline-none"
        >
          <option value="">{t("inspector.unset")}</option>
          <option value="operator">{t("inspector.operatorSideOption")}</option>
          <option value="user">{t("inspector.userSideOption")}</option>
          <option value="both">{t("inspector.bothSideOption")}</option>
        </select>
      </label>
      <ServiceTextarea
        label={t("inspector.field.what")}
        hint={t("inspector.fieldHint.what")}
        value={node.what}
        onChange={(v) => onPatchNode({ what: v })}
        placeholder="이 서비스는…"
      />
      <ServiceTextarea
        label={t("inspector.field.valueCreated")}
        hint={t("inspector.fieldHint.valueCreated")}
        value={node.value_created}
        onChange={(v) => onPatchNode({ value_created: v })}
        placeholder="만들어내는 가치"
      />
      <ServiceTextarea
        label={t("inspector.field.scope")}
        hint={t("inspector.fieldHint.scope")}
        value={node.scope}
        onChange={(v) => onPatchNode({ scope: v })}
        placeholder="포함/제외 범위"
      />
      <ServiceTextarea
        label={t("inspector.field.trigger")}
        hint={t("inspector.fieldHint.trigger")}
        value={node.trigger}
        onChange={(v) => onPatchNode({ trigger: v })}
        placeholder="언제/무엇으로 시작?"
      />
      <ServiceTextarea
        label={t("inspector.field.how")}
        hint={t("inspector.fieldHint.how")}
        value={node.how}
        onChange={(v) => onPatchNode({ how: v })}
        placeholder="어떻게 동작?"
      />
      <ServiceTextarea
        label={t("inspector.field.outcome")}
        hint={t("inspector.fieldHint.outcome")}
        value={node.outcome}
        onChange={(v) => onPatchNode({ outcome: v })}
        placeholder="끝나면 어떤 상태?"
      />
      <DoDontFields node={node} onPatchNode={onPatchNode} />
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
      <span className="text-xs font-semibold text-slate-700">{label}</span>
      <span className="ml-1 text-[10px] text-slate-500">— {hint}</span>
      <textarea
        rows={2}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-sky-600 focus:outline-none"
      />
    </label>
  );
}
