import type { NodeKind, SketchNode } from "../types";
import { getIcon } from "./SketchIcons";

/**
 * v0.10 Step 3 — picker modal for the three Foundation ref kinds
 * (mission_ref / value_ref / identity_ref).
 *
 * Mirrors ``ActorRefPicker`` but is parameterised by the master kind. The
 * caller supplies the candidate masters (already filtered) and a callback;
 * picking either spawns a new ref node (``create``) or repoints an
 * existing orphan (``rewire``).
 */

export type FoundationRefMasterKind = "mission" | "core_value" | "identity";

const TITLE_BY_KIND: Record<FoundationRefMasterKind, string> = {
  mission: "mission",
  core_value: "core value",
  identity: "identity aspect",
};

const ABSENT_BY_KIND: Record<FoundationRefMasterKind, string> = {
  mission: "No missions yet. Add one on the Foundation canvas first.",
  core_value: "No core values yet. Add one on the Foundation canvas first.",
  identity: "No identity aspects yet. Add one on the Foundation canvas first.",
};

export interface FoundationRefPickerProps {
  /** Which master kind the picker selects from. */
  masterKind: FoundationRefMasterKind;
  /** Foundation-canvas nodes filtered to ``masterKind``. Caller-supplied so
   *  this component never reaches across the canvas boundary itself. */
  masters: SketchNode[];
  mode?: "create" | "rewire";
  onPick: (master: SketchNode) => void;
  onCancel: () => void;
}

export function FoundationRefPicker({
  masterKind,
  masters,
  mode = "create",
  onPick,
  onCancel,
}: FoundationRefPickerProps) {
  const noun = TITLE_BY_KIND[masterKind];
  const heading = mode === "rewire" ? `Re-pick ${noun}` : `Reference a ${noun}`;
  const sub =
    mode === "rewire"
      ? "Choose a replacement; the symbol on this canvas will update."
      : `The canvas will show a symbol pointing at the original ${noun} on the Foundation canvas.`;
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={heading}
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40"
      onClick={onCancel}
    >
      <div
        className="flex max-h-[70vh] w-96 flex-col overflow-hidden rounded-lg bg-white shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="border-b border-slate-200 px-4 py-3">
          <h2 className="text-sm font-semibold text-slate-900">{heading}</h2>
          <p className="text-xs text-slate-500">{sub}</p>
        </div>
        {masters.length === 0 ? (
          <div className="flex-1 px-4 py-8 text-center text-sm text-slate-500">
            {ABSENT_BY_KIND[masterKind]}
          </div>
        ) : (
          <ul className="flex-1 divide-y divide-slate-100 overflow-y-auto">
            {masters.map((m) => {
              const Icon = getIcon(m.icon);
              return (
                <li key={m.id}>
                  <button
                    type="button"
                    onClick={() => onPick(m)}
                    className="flex w-full items-center gap-3 px-4 py-2.5 text-left hover:bg-slate-50"
                  >
                    <span
                      className="flex h-6 w-6 shrink-0 items-center justify-center rounded"
                      style={{ backgroundColor: m.color || "#fef3c7" }}
                    >
                      {Icon && <Icon size={12} className="text-slate-700" aria-hidden />}
                    </span>
                    <span className="flex min-w-0 flex-col">
                      <span className="truncate text-sm text-slate-900">
                        {m.label || m.id}
                      </span>
                      <span className="truncate text-[10px] text-slate-400">
                        {m.id}
                      </span>
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
        <div className="flex justify-end border-t border-slate-200 px-4 py-2">
          <button
            type="button"
            onClick={onCancel}
            className="rounded px-3 py-1 text-xs text-slate-600 hover:bg-slate-100"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

/** Map a ref node kind to the master kind it points at. */
export function masterKindForRef(refKind: NodeKind | null): FoundationRefMasterKind | null {
  if (refKind === "mission_ref") return "mission";
  if (refKind === "value_ref") return "core_value";
  if (refKind === "identity_ref") return "identity";
  return null;
}

/** Map a ref node kind to the SketchNode field that stores its target id. */
export function refIdFieldForKind(
  refKind: NodeKind | null,
): "ref_mission_id" | "ref_value_id" | "ref_identity_id" | null {
  if (refKind === "mission_ref") return "ref_mission_id";
  if (refKind === "value_ref") return "ref_value_id";
  if (refKind === "identity_ref") return "ref_identity_id";
  return null;
}
