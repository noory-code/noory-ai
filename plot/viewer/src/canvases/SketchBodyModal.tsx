import { useEffect, useState } from "react";
import type { SketchNode } from "../types";

const PALETTE = ["#ffffff", "#fecaca", "#fed7aa", "#fef08a", "#bbf7d0", "#bae6fd", "#ddd6fe"];

export interface SketchBodyModalProps {
  node: SketchNode;
  onCommit: (patch: Partial<SketchNode>) => void;
  onClose: () => void;
  onDelete: () => void;
}

/**
 * Double-click a node to open — full editor for label, body, color, size.
 */
export function SketchBodyModal({
  node,
  onCommit,
  onClose,
  onDelete,
}: SketchBodyModalProps) {
  const [label, setLabel] = useState(node.label);
  const [body, setBody] = useState(node.body);
  const [color, setColor] = useState(node.color);
  const [width, setWidth] = useState(node.width);
  const [height, setHeight] = useState(node.height);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        onCommit({ label, body, color, width, height });
        onClose();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [label, body, color, width, height, onCommit, onClose]);

  const commit = () => {
    onCommit({ label, body, color, width, height });
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-30 flex items-center justify-center bg-slate-900/40"
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <div
        className="w-[480px] rounded-lg bg-white p-5 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-800">Edit node</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="rounded px-2 text-slate-400 hover:bg-slate-100"
          >
            ✕
          </button>
        </div>

        <label className="mb-3 block">
          <span className="text-xs font-semibold text-slate-600">Label</span>
          <input
            type="text"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
            autoFocus
          />
        </label>

        <label className="mb-3 block">
          <span className="text-xs font-semibold text-slate-600">Body (markdown)</span>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            rows={6}
            className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm focus:border-indigo-600 focus:outline-none"
            placeholder="Longer note — supports line breaks"
          />
          <span className="text-[10px] text-slate-400">Cmd/Ctrl+Enter to save</span>
        </label>

        <div className="mb-3">
          <span className="mb-1 block text-xs font-semibold text-slate-600">Color</span>
          <div className="flex gap-2">
            {PALETTE.map((hex) => (
              <button
                key={hex}
                type="button"
                onClick={() => setColor(hex)}
                aria-label={`Color ${hex}`}
                className={`h-6 w-6 rounded border ${
                  color === hex ? "border-indigo-600 ring-2 ring-indigo-300" : "border-slate-300"
                }`}
                style={{ backgroundColor: hex }}
              />
            ))}
          </div>
        </div>

        <div className="mb-4 flex gap-3">
          <label className="flex-1">
            <span className="text-xs font-semibold text-slate-600">Width</span>
            <input
              type="number"
              min={100}
              max={600}
              value={width}
              onChange={(e) => setWidth(Number(e.target.value) || 180)}
              className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm"
            />
          </label>
          <label className="flex-1">
            <span className="text-xs font-semibold text-slate-600">Height</span>
            <input
              type="number"
              min={40}
              max={400}
              value={height}
              onChange={(e) => setHeight(Number(e.target.value) || 80)}
              className="mt-1 w-full rounded border border-slate-300 px-2 py-1 text-sm"
            />
          </label>
        </div>

        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => {
              if (window.confirm("Delete this node?")) {
                onDelete();
                onClose();
              }
            }}
            className="rounded px-3 py-1 text-xs text-rose-700 hover:bg-rose-50"
          >
            Delete node
          </button>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded border border-slate-300 px-3 py-1 text-xs text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={commit}
              className="rounded bg-slate-900 px-3 py-1 text-xs font-medium text-white hover:bg-slate-700"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
