/**
 * Per-kind inspector for ``category`` nodes (v0.12 thematic grouping
 * of services). Reads ``allNodes`` to count nested services so the
 * empty-category warning fires when ``childCount === 0``.
 *
 * v0.15 Phase 2.6.
 */
import { useTranslation } from "react-i18next";
import type { CategoryJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import { MdTextarea } from "../shared/MdTextarea";
import type { KindInspectorProps } from "../types";

export function CategoryInspector(props: KindInspectorProps) {
  if (props.node.kind !== "category") return null;
  const node = props.node;
  // v0.26.0 (D-2026-05-25-A) — child count is now derived from
  // directed edges (this node → service child).
  const childIds = new Set(
    props.allEdges
      .filter((e) => e.directed && e.source === node.id)
      .map((e) => e.target),
  );
  const childCount = props.allNodes.filter(
    (n) => childIds.has(n.id) && n.kind === "service",
  ).length;
  return (
    <BaseInspector {...props} hideDetailsSection>
      <CategoryFields node={node} childCount={childCount} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface CategoryFieldsProps {
  node: CategoryJson;
  childCount: number;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function CategoryFields({ node, childCount, onPatchNode }: CategoryFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-line bg-surface-muted/60 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-fg">
        {t("kind.category")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-fg">{t("inspector.field.theme")}</span>
        <span className="ml-1 text-[10px] text-fg-muted">
          — {t("inspector.fieldHint.theme")}
        </span>
        <MdTextarea
          value={node.theme ?? ""}
          onChange={(v) => onPatchNode({ theme: v })}
          placeholder="이 카테고리의 공통 주제 / 묶음의 본질"
        />
      </label>
      <BodyField value={node.body ?? ""} onChange={(body) => onPatchNode({ body })} />
      {childCount === 0 && (
        <p className="mt-2 rounded border border-warn-line bg-warn-soft px-2 py-1 text-[11px] text-warn-fg">
          이 카테고리에 service 가 없습니다. category 는 service 를 묶기 위해
          존재 — 비어있으면 시각 노이즈입니다. service 를 추가하거나 카테고리를
          삭제하세요.
        </p>
      )}
    </div>
  );
}
