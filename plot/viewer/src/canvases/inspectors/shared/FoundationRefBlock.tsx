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
import type { IdentityRefJson, MissionRefJson, ValueRefJson } from "../../../domain";
import type { SketchNode } from "../../../types";

export interface FoundationRefBlockProps {
  node: MissionRefJson | ValueRefJson | IdentityRefJson;
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
    tone = { fg: "text-warn-fg", bg: "border-warn-line bg-warn-soft/40" };
  } else if (node.kind === "value_ref") {
    label = t("kind.core_value");
    id = node.ref_value_id;
    masters = availableValues;
    tone = { fg: "text-warn-fg", bg: "border-warn-line bg-warn-soft/40" };
  } else {
    label = t("kind.identity");
    id = node.ref_identity_id;
    masters = availableIdentities;
    tone = { fg: "text-warn-fg", bg: "border-warn-line bg-warn-soft/40" };
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
          <div className="text-danger-fg">{t("inspector.masterNotFound")}</div>
          <div className="mb-2 font-mono text-[10px] text-fg-muted">id: {id ?? "—"}</div>
          {(onRepickFoundationRef || onDeleteNode) && (
            <div className="flex gap-2">
              {onRepickFoundationRef && (
                <button
                  type="button"
                  onClick={() => onRepickFoundationRef(node.id)}
                  className="rounded border border-danger bg-surface px-2 py-1 text-[11px] font-medium text-danger-fg hover:bg-danger-soft"
                >
                  {t("inspector.rePick")}
                </button>
              )}
              {onDeleteNode && (
                <button
                  type="button"
                  onClick={() => onDeleteNode(node.id)}
                  className="rounded px-2 py-1 text-[11px] text-fg-secondary hover:bg-surface-subtle"
                >
                  {t("common.delete")}
                </button>
              )}
            </div>
          )}
        </>
      ) : (
        <>
          <div className="text-fg">
            <span className="text-fg-muted">{label}:</span>{" "}
            <span className="font-medium">{target.label || target.id}</span>
          </div>
          <div className="mt-0.5 font-mono text-[10px] text-fg-faint">{id}</div>
        </>
      )}
    </div>
  );
}
