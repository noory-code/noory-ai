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
import type { SketchNode } from "../../../types";
import { BaseInspector } from "../BaseInspector";
import type { KindInspectorProps } from "../types";

export function MetricInspector(props: KindInspectorProps) {
  return (
    <BaseInspector {...props}>
      <MetricFields node={props.node} onPatchNode={props.onPatchNode} />
    </BaseInspector>
  );
}

interface MetricFieldsProps {
  node: SketchNode;
  onPatchNode: (patch: Partial<SketchNode>) => void;
}

function MetricFields({ node, onPatchNode }: MetricFieldsProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4 rounded border border-lime-200 bg-lime-50/40 p-2">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-lime-700">
        {t("kind.metric")}
      </div>
      <label className="mb-2 block">
        <span className="text-xs font-semibold text-slate-700">{t("inspector.field.target")}</span>
        <span className="ml-1 text-[10px] text-slate-500">— {t("inspector.fieldHint.target")}</span>
        <input
          type="text"
          value={node.target ?? ""}
          onChange={(e) => onPatchNode({ target: e.target.value })}
          placeholder=">99% / under 200ms / …"
          className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-lime-600 focus:outline-none"
        />
      </label>
      <label className="block">
        <span className="text-xs font-semibold text-slate-700">
          {t("inspector.field.measurement")}
        </span>
        <span className="ml-1 text-[10px] text-slate-500">
          — {t("inspector.fieldHint.measurement")}
        </span>
        <textarea
          rows={2}
          value={node.measurement ?? ""}
          onChange={(e) => onPatchNode({ measurement: e.target.value })}
          placeholder="어떤 신호를 어떻게 집계?"
          className="mt-1 w-full resize-y rounded border border-slate-300 px-2 py-1 text-sm focus:border-lime-600 focus:outline-none"
        />
      </label>
    </div>
  );
}
