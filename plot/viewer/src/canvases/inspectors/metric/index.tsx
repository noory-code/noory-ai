/**
 * Per-kind inspector for ``metric`` nodes (KPI / success rate / latency
 * targets inside a service_detail canvas). Composed of the shared
 * ``BaseInspector`` chrome + the metric-specific typed-field form
 * (``target`` + ``measurement``).
 *
 * v0.15 Phase 2.1 — first kind to migrate out of the legacy god
 * ``SketchInspector``. Lays the pattern Phase 2.2+ kinds repeat.
 */
import { useTranslation } from "react-i18next";
import type { MetricJson } from "../../../domain";
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import { BodyField } from "../shared/BodyField";
import { MdTextarea } from "../shared/MdTextarea";
import type { KindInspectorProps } from "../types";

export function MetricInspector(props: KindInspectorProps) {
  if (props.node.kind !== "metric") return null;
  const node = props.node;
  return (
    <BaseInspector {...props} hideDetailsSection>
      <MetricFields node={node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface MetricFieldsProps {
  node: MetricJson;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function MetricFields({ node, onPatchNode }: MetricFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-ok-line bg-ok-soft/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-ok-fg">
        {t("kind.metric")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-fg">{t("inspector.field.target")}</span>
        <span className="ml-1 text-[10px] text-fg-muted">— {t("inspector.fieldHint.target")}</span>
        <MdTextarea
          value={node.target ?? ""}
          onChange={(v) => onPatchNode({ target: v })}
          placeholder=">99% / under 200ms / …"
        />
      </label>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-fg">
          {t("inspector.field.measurement")}
        </span>
        <span className="ml-1 text-[10px] text-fg-muted">
          — {t("inspector.fieldHint.measurement")}
        </span>
        <MdTextarea
          value={node.measurement ?? ""}
          onChange={(v) => onPatchNode({ measurement: v })}
          placeholder="어떤 신호를 어떻게 집계?"
        />
      </label>
      <BodyField value={node.body ?? ""} onChange={(body) => onPatchNode({ body })} />
    </div>
  );
}
