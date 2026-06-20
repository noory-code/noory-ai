/**
 * Per-kind inspector for ``feature`` nodes (D-2026-06-17-D /
 * D-2026-06-19-H). A feature is a capability the service offers — a
 * behaviour grouping, the sole drill target. Lean inspector: the name
 * (edited via the shared header) + a one-line ``proposed`` "무엇을 할 수
 * 있나?" summary. The behaviour flow itself lives one level down (the
 * Feature canvas, opened by drilling).
 */
import { useTranslation } from "react-i18next";
import type { FeatureJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { MdTextarea } from "../shared/MdTextarea";
import type { KindInspectorProps } from "../types";

export function FeatureInspector(props: KindInspectorProps) {
  if (props.node.kind !== "feature") return null;
  const node = props.node;
  return (
    <BaseInspector {...props} hideDetailsSection>
      <FeatureFields node={node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface FeatureFieldsProps {
  node: FeatureJson;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function FeatureFields({ node, onPatchNode }: FeatureFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-line bg-surface-muted/60 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-fg">
        {t("kind.feature")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-fg">
          {t("inspector.feature.proposed")}
        </span>
        <span className="ml-1 text-[10px] text-fg-muted">
          — {t("inspector.feature.proposedHint")}
        </span>
        <MdTextarea
          value={node.proposed ?? ""}
          onChange={(v) => onPatchNode({ proposed: v })}
          placeholder={t("inspector.feature.proposedPlaceholder")}
        />
      </label>
      <p className="mt-1 text-[11px] leading-snug text-fg-muted">
        {t("inspector.feature.drillHint")}
      </p>
    </div>
  );
}
