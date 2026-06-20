/**
 * Per-kind inspector for ``entity`` nodes (D-2026-06-17-I / D-2026-06-17-K).
 * An entity is a product data object the services act on — symmetric to an
 * actor. Lean, conceptual inspector (B5): the name (edited via the shared
 * header) + a one-line ``summary`` ("무엇을 담나?"). Both are writable.
 *
 * The read-only "어디서 쓰이나" (back-reference) + "거친 관계" views pinned by
 * D-2026-06-17-K are OUT OF SCOPE here — they wire in step 6 (blocked on the
 * feature→entity reference + a cross-canvas reverse index). This scope =
 * 2 writable fields only.
 */
import { useTranslation } from "react-i18next";
import type { EntityJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { MdTextarea } from "../shared/MdTextarea";
import type { KindInspectorProps } from "../types";

export function EntityInspector(props: KindInspectorProps) {
  if (props.node.kind !== "entity") return null;
  const node = props.node;
  return (
    <BaseInspector {...props} hideDetailsSection>
      <EntityFields node={node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface EntityFieldsProps {
  node: EntityJson;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function EntityFields({ node, onPatchNode }: EntityFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-line bg-surface-muted/60 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-fg">
        {t("kind.entity")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-fg">
          {t("inspector.entity.field.summary")}
        </span>
        <span className="ml-1 text-[10px] text-fg-muted">
          — {t("inspector.entity.field.summaryHint")}
        </span>
        <MdTextarea
          value={node.summary ?? ""}
          onChange={(v) => onPatchNode({ summary: v })}
          placeholder={t("inspector.entity.field.summaryPlaceholder")}
        />
      </label>
    </div>
  );
}
