import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import type { Shape, SketchNode } from "../types";
import { ICON_KEYS, getIcon } from "./SketchIcons";
import { useDialog } from "../shell/dialog/DialogProvider";

const PALETTE = ["#ffffff", "#fecaca", "#fed7aa", "#fef08a", "#bbf7d0", "#bae6fd", "#ddd6fe"];

const SHAPES: { id: Shape; label: string; preview: string }[] = [
  { id: "rectangle", label: "Rectangle", preview: "▭" },
  { id: "rounded", label: "Rounded", preview: "▢" },
  { id: "circle", label: "Circle", preview: "●" },
  { id: "ellipse", label: "Ellipse", preview: "⬭" },
  { id: "diamond", label: "Diamond", preview: "◆" },
  { id: "hexagon", label: "Hexagon", preview: "⬢" },
];

export interface SketchBodyModalProps {
  node: SketchNode;
  onCommit: (patch: Partial<SketchNode>) => void;
  onClose: () => void;
  onDelete: () => void;
}

export function SketchBodyModal({
  node,
  onCommit,
  onClose,
  onDelete,
}: SketchBodyModalProps) {
  const { t } = useTranslation();
  const dialog = useDialog();
  const [label, setLabel] = useState(node.label);
  const [color, setColor] = useState(node.color);
  const [width, setWidth] = useState(node.width);
  const [height, setHeight] = useState(node.height);
  const [shape, setShape] = useState<Shape>(node.shape);
  const [icon, setIcon] = useState<string | null>(node.icon);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        onCommit({ label, color, width, height, shape, icon });
        onClose();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [label, color, width, height, shape, icon, onCommit, onClose]);

  const commit = () => {
    onCommit({ label, color, width, height, shape, icon });
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
        className="max-h-[90vh] w-[520px] overflow-y-auto rounded-lg bg-surface p-5 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-fg-strong">Edit node</h2>
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
          <span className="text-xs font-semibold text-fg-secondary">Label</span>
          <input
            type="text"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            className="mt-1 w-full rounded border border-line-strong px-2 py-1 text-sm focus:border-accent focus:outline-none"
            autoFocus
          />
        </label>

        <p className="mb-3 text-[11px] text-fg-muted">
          Long-form text lives in the Inspector's <code>details.md</code> editor.
          This modal handles the visual properties only.
        </p>

<div className="mb-3">
          <span className="mb-1 block text-xs font-semibold text-fg-secondary">Shape</span>
          <div className="flex flex-wrap gap-1">
            {SHAPES.map((s) => (
              <button
                key={s.id}
                type="button"
                onClick={() => setShape(s.id)}
                aria-label={s.label}
                title={s.label}
                className={`rounded border px-2 py-1 text-lg leading-none ${
                  shape === s.id
                    ? "border-accent bg-accent-soft text-accent-fg"
                    : "border-line-strong text-fg hover:bg-surface-muted"
                }`}
              >
                {s.preview}
              </button>
            ))}
          </div>
        </div>

        <div className="mb-3">
          <span className="mb-1 block text-xs font-semibold text-fg-secondary">Color</span>
          <div className="flex gap-2">
            {PALETTE.map((hex) => (
              <button
                key={hex}
                type="button"
                onClick={() => setColor(hex)}
                aria-label={`Color ${hex}`}
                className={`h-6 w-6 rounded border ${
                  color === hex ? "border-accent ring-2 ring-accent" : "border-line-strong"
                }`}
                style={{ backgroundColor: hex }}
              />
            ))}
          </div>
        </div>

        <div className="mb-3">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-xs font-semibold text-fg-secondary">Icon</span>
            {icon && (
              <button
                type="button"
                onClick={() => setIcon(null)}
                className="text-[10px] text-fg-muted hover:text-danger-fg"
              >
                Clear
              </button>
            )}
          </div>
          <div className="grid grid-cols-9 gap-1">
            {ICON_KEYS.map((key) => {
              const Icon = getIcon(key);
              if (!Icon) return null;
              const active = icon === key;
              return (
                <button
                  key={key}
                  type="button"
                  onClick={() => setIcon(key)}
                  aria-label={key}
                  title={key}
                  className={`flex h-7 w-7 items-center justify-center rounded border ${
                    active
                      ? "border-accent bg-accent-soft text-accent-fg"
                      : "border-line text-fg hover:bg-surface-muted"
                  }`}
                >
                  <Icon size={14} />
                </button>
              );
            })}
          </div>
        </div>

        <div className="mb-4 flex gap-3">
          <label className="flex-1">
            <span className="text-xs font-semibold text-fg-secondary">Width</span>
            <input
              type="number"
              min={80}
              max={600}
              value={width}
              onChange={(e) => setWidth(Number(e.target.value) || 180)}
              className="mt-1 w-full rounded border border-line-strong px-2 py-1 text-sm"
            />
          </label>
          <label className="flex-1">
            <span className="text-xs font-semibold text-fg-secondary">Height</span>
            <input
              type="number"
              min={40}
              max={400}
              value={height}
              onChange={(e) => setHeight(Number(e.target.value) || 80)}
              className="mt-1 w-full rounded border border-line-strong px-2 py-1 text-sm"
            />
          </label>
        </div>

        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={async () => {
              if (await dialog.confirm({ message: t("node.confirmDelete"), danger: true })) {
                onDelete();
                onClose();
              }
            }}
            className="rounded px-3 py-1 text-xs text-danger-fg hover:bg-danger-soft"
          >
            Delete node
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
