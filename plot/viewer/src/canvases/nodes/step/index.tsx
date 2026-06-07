/**
 * Step composition node renderer.
 *
 * v0.15 Phase 3.1 — bare BaseNode + kind tag.
 * v0.27.19 (D-2026-05-30-A / -B) — ServiceDetail step authoring:
 *  - ``outcome`` (system-side end state) renders below the label and
 *    is inline-editable, so the user-interaction sequence reads
 *    naturally in-canvas without opening the Inspector (SPEC §"step =
 *    user interaction": system work lives in ``step.outcome``).
 *  - a derived branch badge appears when the step has ≥ 2 outgoing
 *    directed edges (a branch point per the composition model). No
 *    new field — the edge count is the source of truth.
 */
import type { NodeProps } from "reactflow";
import { useTranslation } from "react-i18next";
import { BaseNode, type BaseNodeData, shouldShowKindTag } from "../BaseNode";
import { EditableText } from "../../../edit/EditableText";

function StepBody({ data }: { data: BaseNodeData }) {
  const { t } = useTranslation();
  const isBranch = (data.branchCount ?? 0) >= 2;
  const hasOutcome = (data.outcome ?? "").trim().length > 0;
  if (!isBranch && !hasOutcome && !data.onOutcomeChange) return null;
  const outcomeRow = (inner: React.ReactNode) => (
    <div className="flex items-start gap-1 text-left text-[11px] leading-snug text-fg-muted">
      <span className="select-none text-fg-faint" aria-hidden>
        ↳
      </span>
      {inner}
    </div>
  );
  return (
    <div className="flex flex-col items-stretch gap-1">
      {isBranch && (
        <span
          className="nodrag mx-auto inline-flex items-center gap-1 rounded-full bg-warn-soft px-2 text-[10px] font-semibold uppercase tracking-wide text-warn-fg ring-1 ring-warn"
          aria-label={t("node.step.branchAria", { count: data.branchCount ?? 0 })}
          title={t("node.step.branchAria", { count: data.branchCount ?? 0 })}
        >
          ⑂ {t("node.step.branchLabel")}
        </span>
      )}
      {data.onOutcomeChange
        ? outcomeRow(
            <EditableText
              value={data.outcome ?? ""}
              onCommit={data.onOutcomeChange}
              placeholder={t("node.step.outcomePlaceholder")}
              ariaLabel={t("inspector.field.outcome")}
              className="flex-1"
              inputClassName="w-full rounded border border-accent bg-surface px-1 py-0.5 text-[11px] focus:border-accent focus:outline-none"
              multiline
            />,
          )
        : hasOutcome && outcomeRow(<span className="flex-1">{data.outcome}</span>)}
    </div>
  );
}

export function StepNode(props: NodeProps<BaseNodeData>) {
  return (
    <BaseNode
      {...props}
      chrome={{
        showKindTag: shouldShowKindTag(props.data.shape),
        bodyOverride: <StepBody data={props.data} />,
      }}
    />
  );
}
