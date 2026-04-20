import type { NodePreset } from "./SketchCanvas";
import { getIcon } from "./SketchIcons";

/**
 * Stencil presets shown in the sidebar. Users drag one onto the canvas to
 * create a new node with that shape / color / icon. These are suggestive —
 * labels are editable right after drop, and the user can deviate freely.
 */
export const STENCIL_PRESETS: (NodePreset & { id: string; labelHint: string })[] = [
  {
    id: "role",
    labelHint: "Role",
    shape: "circle",
    color: "#fecaca",
    width: 120,
    height: 120,
    icon: "user",
    label: "Role",
    kind: "actor",
  },
  {
    id: "service",
    labelHint: "Service",
    shape: "rounded",
    color: "#bae6fd",
    width: 180,
    height: 80,
    icon: "box",
    label: "Service",
    kind: "service",
  },
  {
    id: "narrative",
    labelHint: "Narrative",
    shape: "diamond",
    color: "#fef08a",
    width: 160,
    height: 120,
    icon: "message-circle",
    label: "Narrative",
  },
  {
    id: "actor",
    labelHint: "Actor",
    shape: "hexagon",
    color: "#fed7aa",
    width: 160,
    height: 100,
    icon: "users",
    label: "Actor",
    kind: "actor",
  },
  {
    id: "concept",
    labelHint: "Concept",
    shape: "ellipse",
    color: "#ddd6fe",
    width: 180,
    height: 100,
    icon: "star",
    label: "Concept",
  },
  {
    id: "note",
    labelHint: "Note",
    shape: "rectangle",
    color: "#ffffff",
    width: 180,
    height: 80,
    icon: null,
    label: "",
  },
];

export function SketchStencil() {
  return (
    <div className="border-t border-slate-200 px-3 py-3">
      <div className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-slate-500">
        Shapes · drag to canvas
      </div>
      <ul className="space-y-1">
        {STENCIL_PRESETS.map((p) => {
          const Icon = getIcon(p.icon);
          return (
            <li key={p.id}>
              <div
                draggable
                onDragStart={(e) => {
                  const { id: _id, labelHint: _lh, ...preset } = p;
                  e.dataTransfer.setData(
                    "application/plot-preset",
                    JSON.stringify(preset),
                  );
                  e.dataTransfer.effectAllowed = "copy";
                }}
                className="flex cursor-grab items-center gap-2 rounded border border-slate-200 bg-white px-2 py-1.5 text-xs text-slate-700 shadow-sm hover:bg-slate-50 active:cursor-grabbing"
                title={`Drag ${p.labelHint} onto the canvas`}
              >
                <span
                  className="flex h-6 w-6 shrink-0 items-center justify-center"
                  style={{
                    backgroundColor: p.color,
                    borderRadius:
                      p.shape === "circle" || p.shape === "ellipse"
                        ? "50%"
                        : p.shape === "rounded"
                          ? 4
                          : 0,
                    clipPath:
                      p.shape === "diamond"
                        ? "polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)"
                        : p.shape === "hexagon"
                          ? "polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)"
                          : undefined,
                  }}
                >
                  {Icon && <Icon size={12} className="text-slate-700" aria-hidden />}
                </span>
                <span className="truncate">{p.labelHint}</span>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
