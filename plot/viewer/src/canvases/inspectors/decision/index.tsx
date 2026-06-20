/**
 * Per-kind inspector for ``decision`` nodes (flowchart decision /
 * branch point inside a feature canvas). v0.28.0
 * (D-2026-05-30-C).
 *
 * A decision carries only the question (``label``, edited via the
 * shared header) + optional notes (``body``). The branches live on the
 * outgoing edges, not on the node — so there are no per-kind typed
 * fields beyond ``body``.
 */
import { useTranslation } from "react-i18next";
import type { DecisionJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import type { KindInspectorProps } from "../types";

export function DecisionInspector(props: KindInspectorProps) {
  if (props.node.kind !== "decision") return null;
  const node = props.node;
  return (
    <BaseInspector {...props} hideDetailsSection>
      <DecisionFields node={node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface DecisionFieldsProps {
  node: DecisionJson;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function DecisionFields({ node, onPatchNode }: DecisionFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-warn-line bg-warn-soft/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-warn-fg">
        {t("kind.decision")}
      </div>
      <p className="mb-2 text-[11px] leading-snug text-fg-muted">
        {t("inspector.decision.branchHint")}
      </p>
      <BodyField value={node.body ?? ""} onChange={(body) => onPatchNode({ body })} />
    </div>
  );
}
