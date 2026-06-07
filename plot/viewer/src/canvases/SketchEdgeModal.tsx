import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import type { SketchEdge, ValueForm } from "../types";
import { useDialog } from "../shell/dialog/DialogProvider";

const VALUE_FORMS: { id: ValueForm; label: string; hint: string; color: string }[] = [
  { id: "economic", label: "Economic", hint: "money, payment, fees", color: "#16a34a" },
  { id: "attention", label: "Attention", hint: "interest, traffic", color: "#eab308" },
  { id: "social", label: "Social", hint: "name, reputation, relationships", color: "#a855f7" },
  { id: "cognitive", label: "Cognitive", hint: "information, data, know-how", color: "#64748b" },
  { id: "experience", label: "Experience", hint: "joy, convenience, accomplishment", color: "#f97316" },
  { id: "access", label: "Access", hint: "opportunity, membership, exclusivity", color: "#0d9488" },
  { id: "effort", label: "Effort", hint: "time, creative labour", color: "#db2777" },
];

const VERB_SUGGESTIONS = [
  "create",
  "produce",
  "deliver",
  "provide",
  "share",
  "mediate",
  "match",
  "consume",
  "use",
  "receive",
  "pay",
  "exchange",
  "earn",
  "build reputation",
  "leave",
];

export interface SketchEdgeModalProps {
  edge: SketchEdge;
  onCommit: (patch: Partial<SketchEdge>) => void;
  onClose: () => void;
  onDelete: () => void;
}

/**
 * Modal for editing a single edge's action_verb + value_form + label +
 * style. See PHILOSOPHY.md P6 (arrows carry both action and value).
 */
export function SketchEdgeModal({
  edge,
  onCommit,
  onClose,
  onDelete,
}: SketchEdgeModalProps) {
  const { t } = useTranslation();
  const dialog = useDialog();
  const [actionVerb, setActionVerb] = useState(edge.action_verb ?? "");
  const [valueForm, setValueForm] = useState<ValueForm[]>(edge.value_form ?? []);
  const [label, setLabel] = useState(edge.label);
  const [style, setStyle] = useState<"solid" | "dashed">(edge.style);

  // Auto-suggest label whenever verb / value-form changes AND user hasn't typed a custom one.
  const [labelWasManual, setLabelWasManual] = useState(edge.label.length > 0);

  useEffect(() => {
    if (labelWasManual) return;
    const verbStr = actionVerb.trim();
    const valStr = valueForm.join("·");
    if (verbStr && valStr) setLabel(`${verbStr}: ${valStr}`);
    else if (verbStr) setLabel(verbStr);
    else if (valStr) setLabel(valStr);
    else setLabel("");
  }, [actionVerb, valueForm, labelWasManual]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        commit();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [actionVerb, valueForm, label, style]);

  const toggleValue = (v: ValueForm) => {
    setValueForm((prev) =>
      prev.includes(v) ? prev.filter((x) => x !== v) : [...prev, v],
    );
  };

  const commit = () => {
    onCommit({
      action_verb: actionVerb.trim() || null,
      value_form: valueForm,
      label,
      style,
    });
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-30 flex items-center justify-center bg-overlay/40"
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <div
        className="w-[520px] rounded-lg bg-surface p-5 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-fg-strong">Edit arrow</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="rounded px-2 text-fg-faint hover:bg-surface-subtle"
          >
            ✕
          </button>
        </div>

        <label className="mb-3 block">
          <span className="text-xs font-semibold text-fg-secondary">Action (verb)</span>
          <input
            list="plot-verb-suggestions"
            type="text"
            value={actionVerb}
            onChange={(e) => setActionVerb(e.target.value)}
            placeholder="create · pay · deliver …"
            className="mt-1 w-full rounded border border-line-strong px-2 py-1 text-sm focus:border-accent focus:outline-none"
            autoFocus
          />
          <datalist id="plot-verb-suggestions">
            {VERB_SUGGESTIONS.map((v) => (
              <option key={v} value={v} />
            ))}
          </datalist>
        </label>

        <div className="mb-3">
          <span className="mb-1 block text-xs font-semibold text-fg-secondary">
            Value form (what flows)
          </span>
          <div className="grid grid-cols-2 gap-1">
            {VALUE_FORMS.map((v) => {
              const active = valueForm.includes(v.id);
              return (
                <label
                  key={v.id}
                  className={`flex items-center gap-2 rounded border px-2 py-1 text-xs cursor-pointer ${
                    active
                      ? "border-accent bg-accent-soft"
                      : "border-line bg-surface hover:bg-surface-muted"
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={active}
                    onChange={() => toggleValue(v.id)}
                    className="accent-accent"
                  />
                  <span
                    className="inline-block h-2 w-2 rounded-full"
                    style={{ backgroundColor: v.color }}
                    aria-hidden
                  />
                  <span className="font-medium text-fg-strong">{v.label}</span>
                  <span className="truncate text-[10px] text-fg-muted">{v.hint}</span>
                </label>
              );
            })}
          </div>
        </div>

        <label className="mb-3 block">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-fg-secondary">Label</span>
            <button
              type="button"
              onClick={() => {
                setLabelWasManual(false);
                setLabel("");
              }}
              className="text-[10px] text-fg-muted hover:text-accent-fg"
            >
              Reset auto
            </button>
          </div>
          <input
            type="text"
            value={label}
            onChange={(e) => {
              setLabelWasManual(true);
              setLabel(e.target.value);
            }}
            placeholder="Auto-suggested from verb + values"
            className="mt-1 w-full rounded border border-line-strong px-2 py-1 text-sm focus:border-accent focus:outline-none"
          />
        </label>

        <div className="mb-4">
          <span className="mb-1 block text-xs font-semibold text-fg-secondary">Style</span>
          <div className="flex gap-2">
            {(["solid", "dashed"] as const).map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setStyle(s)}
                className={`rounded border px-3 py-1 text-xs ${
                  style === s
                    ? "border-accent bg-accent-soft text-accent-fg"
                    : "border-line-strong text-fg"
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={async () => {
              if (await dialog.confirm({ message: t("node.confirmDeleteArrow"), danger: true })) {
                onDelete();
                onClose();
              }
            }}
            className="rounded px-3 py-1 text-xs text-danger-fg hover:bg-danger-soft"
          >
            Delete arrow
          </button>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded border border-line-strong px-3 py-1 text-xs text-fg hover:bg-surface-muted"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={commit}
              className="rounded bg-surface-inverse px-3 py-1 text-xs font-medium text-fg-inverse hover:bg-surface-inverse"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/** Export colour map for canvas to colour edges by value_form. */
export const VALUE_FORM_COLORS: Record<ValueForm, string> = Object.fromEntries(
  VALUE_FORMS.map((v) => [v.id, v.color]),
) as Record<ValueForm, string>;
