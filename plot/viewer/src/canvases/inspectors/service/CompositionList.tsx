/**
 * Composition list — used by ServiceInspector to display + manage the
 * rule / content children of the selected service. Each row expands
 * to show the kind-specific typed fields (RuleFields / ContentFields).
 *
 * v0.15 Phase 2.9 — extracted from SketchInspector.tsx so the
 * Service inspector stays focused on Service-level fields.
 */
import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { SketchNode } from "../../../types";
import { ContentFields } from "./ContentFields";
import { RuleFields } from "./RuleFields";

export interface CompositionListProps {
  title: string;
  subtitle: string;
  items: SketchNode[];
  onAdd: () => void;
  onPatch: (childId: string, patch: Partial<SketchNode>) => void;
  onRemove: (childId: string) => void;
  /** v0.10 Step 6: which kind this list is for. */
  kind: "rule" | "content";
  /** v0.10 Step 6: actor masters used by rule's permission editor and
   *  by content's producer/consumer pickers. */
  availableActors?: SketchNode[];
}

export function CompositionList({
  title,
  subtitle,
  items,
  onAdd,
  onPatch,
  onRemove,
  kind,
  availableActors,
}: CompositionListProps) {
  const { t } = useTranslation();
  return (
    <div className="mb-4">
      <div className="mb-1 flex items-baseline justify-between">
        <div>
          <div className="text-xs font-semibold text-slate-700">{title}</div>
          <div className="text-[10px] italic text-slate-400">{subtitle}</div>
        </div>
        <button
          type="button"
          onClick={onAdd}
          className="rounded bg-slate-900 px-2 py-0.5 text-[10px] font-medium text-white hover:bg-slate-700"
        >
          {t("composition.add")}
        </button>
      </div>
      {items.length === 0 ? (
        <div className="rounded border border-dashed border-slate-200 p-2 text-[11px] italic text-slate-400">
          {t("inspector.empty")}
        </div>
      ) : (
        <ul className="space-y-1">
          {items.map((item) => (
            <CompositionRow
              key={item.id}
              item={item}
              kind={kind}
              availableActors={availableActors}
              onPatch={onPatch}
              onRemove={onRemove}
            />
          ))}
        </ul>
      )}
    </div>
  );
}

interface CompositionRowProps {
  item: SketchNode;
  kind: "rule" | "content";
  availableActors?: SketchNode[];
  onPatch: (childId: string, patch: Partial<SketchNode>) => void;
  onRemove: (childId: string) => void;
}

function CompositionRow({
  item,
  kind,
  availableActors,
  onPatch,
  onRemove,
}: CompositionRowProps) {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);
  return (
    <li className="group rounded border border-slate-200 bg-white">
      <div className="flex items-start gap-1 px-2 py-1">
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="rounded px-1 text-[10px] text-slate-500 hover:bg-slate-100"
          aria-label={expanded ? t("composition.collapse") : t("composition.expand")}
          title={expanded ? t("composition.collapse") : t("composition.expand")}
        >
          {expanded ? "▾" : "▸"}
        </button>
        <div className="flex-1">
          <input
            type="text"
            value={item.label}
            onChange={(e) => onPatch(item.id, { label: e.target.value })}
            placeholder={t("composition.namePlaceholder")}
            className="w-full border-none bg-transparent text-xs font-medium text-slate-800 focus:outline-none"
          />
        </div>
        <button
          type="button"
          onClick={() => {
            if (
              window.confirm(
                t("composition.confirmRemove", {
                  name: item.label || t("composition.untitled"),
                }),
              )
            ) {
              onRemove(item.id);
            }
          }}
          className="rounded px-1 text-[10px] text-rose-600 opacity-0 hover:bg-rose-50 group-hover:opacity-100"
          aria-label={t("composition.remove")}
        >
          ✕
        </button>
      </div>
      {expanded && (
        <div className="border-t border-slate-100 px-2 py-2">
          {kind === "rule" ? (
            <RuleFields
              node={item}
              availableActors={availableActors ?? []}
              onPatchNode={(patch) => onPatch(item.id, patch)}
            />
          ) : (
            <ContentFields
              node={item}
              availableActors={availableActors ?? []}
              onPatchNode={(patch) => onPatch(item.id, patch)}
            />
          )}
        </div>
      )}
    </li>
  );
}
