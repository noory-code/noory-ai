/**
 * Shared display block for the 3 Foundation reference kinds
 * (mission_ref / value_ref / identity_ref). Resolves the referenced
 * master from the available-list prop, shows the master's label, and
 * surfaces orphan state (master not found) with re-pick + delete
 * actions when the parent inspector wires them up.
 *
 * Extracted from the legacy ``SketchInspector`` so the per-kind
 * inspectors share one implementation.
 */
import { useTranslation } from "react-i18next";
import type { SketchNode } from "../../../types";

export interface FoundationRefBlockProps {
  node: SketchNode;
  availableMissions: SketchNode[];
  availableValues: SketchNode[];
  availableIdentities: SketchNode[];
  /** v0.11.1 — opens FoundationRefPicker in rewire mode for the given node. */
  onRepickFoundationRef?: (nodeId: string) => void;
  /** v0.11.1 — delete the orphan ref outright. */
  onDeleteNode?: (nodeId: string) => void;
}

export function FoundationRefBlock({
  node,
  availableMissions,
  availableValues,
  availableIdentities,
  onRepickFoundationRef,
  onDeleteNode,
}: FoundationRefBlockProps) {
  const { t } = useTranslation();
  let label: string;
  let id: string | null;
  let masters: SketchNode[];
  let tone: { fg: string; bg: string };
  if (node.kind === "mission_ref") {
    label = t("kind.mission");
    id = node.ref_mission_id;
    masters = availableMissions;
    tone = { fg: "text-amber-700", bg: "border-amber-200 bg-amber-50/40" };
  } else if (node.kind === "value_ref") {
    label = t("kind.core_value");
    id = node.ref_value_id;
    masters = availableValues;
    tone = { fg: "text-yellow-700", bg: "border-yellow-200 bg-yellow-50/40" };
  } else {
    label = t("kind.identity");
    id = node.ref_identity_id;
    masters = availableIdentities;
    tone = { fg: "text-orange-700", bg: "border-orange-200 bg-orange-50/40" };
  }
  const target = id ? masters.find((m) => m.id === id) ?? null : null;
  const orphan = !id || target === null;
  return (
    <div className={`mb-4 rounded border p-2 text-[11px] ${tone.bg}`}>
      <div className={`mb-1 font-semibold uppercase tracking-wide ${tone.fg}`}>
        {t("inspector.referencesHeader", { label })}
      </div>
      {orphan ? (
        <>
          <div className="text-rose-700">{t("inspector.masterNotFound")}</div>
          <div className="mb-2 font-mono text-[10px] text-slate-500">id: {id ?? "—"}</div>
          {(onRepickFoundationRef || onDeleteNode) && (
            <div className="flex gap-2">
              {onRepickFoundationRef && (
                <button
                  type="button"
                  onClick={() => onRepickFoundationRef(node.id)}
                  className="rounded border border-rose-300 bg-white px-2 py-1 text-[11px] font-medium text-rose-700 hover:bg-rose-100"
                >
                  {t("inspector.rePick")}
                </button>
              )}
              {onDeleteNode && (
                <button
                  type="button"
                  onClick={() => onDeleteNode(node.id)}
                  className="rounded px-2 py-1 text-[11px] text-slate-600 hover:bg-slate-100"
                >
                  {t("common.delete")}
                </button>
              )}
            </div>
          )}
        </>
      ) : (
        <>
          <div className="text-slate-700">
            <span className="text-slate-500">{label}:</span>{" "}
            <span className="font-medium">{target.label || target.id}</span>
          </div>
          <div className="mt-0.5 font-mono text-[10px] text-slate-400">{id}</div>
        </>
      )}
    </div>
  );
}
