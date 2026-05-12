/**
 * Per-kind inspector for ``category`` nodes (v0.12 thematic grouping
 * of services). Reads ``allNodes`` to count nested services so the
 * empty-category warning fires when ``childCount === 0``.
 *
 * v0.15 Phase 2.6.
 */
import { useTranslation } from "react-i18next";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import type { KindInspectorProps } from "../types";

export function CategoryInspector(props: KindInspectorProps) {
  const childCount = props.allNodes.filter(
    (n) => n.parent_id === props.node.id && n.kind === "service",
  ).length;
  return (
    <BaseInspector {...props}>
      <CategoryFields
        node={props.node}
        childCount={childCount}
        onPatchNode={props.onPatchNode}
      />
    </BaseInspector>
  );
}

interface CategoryFieldsProps {
  node: SketchNode;
  childCount: number;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function CategoryFields({ node, childCount, onPatchNode }: CategoryFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-slate-200 bg-slate-50/60 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-slate-700">
        {t("kind.category")}
      </div>
      <label className="block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.theme")}</span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.theme")}
        </span>
        <textarea
          rows={2}
          value={node.theme ?? ""}
          onChange={(e) => onPatchNode({ theme: e.target.value })}
          placeholder="이 카테고리의 공통 주제 / 묶음의 본질"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-slate-600 focus:outline-none"
        />
      </label>
      {childCount === 0 && (
        <p className="mt-2 rounded border border-amber-300 bg-amber-50 px-2 py-1 text-[11px] text-amber-800">
          이 카테고리에 service 가 없습니다. category 는 service 를 묶기 위해
          존재 — 비어있으면 시각 노이즈입니다. service 를 추가하거나 카테고리를
          삭제하세요.
        </p>
      )}
    </div>
  );
}
