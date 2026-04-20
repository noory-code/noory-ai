import type { NodeKind } from "../types";
import type { NodePreset } from "./SketchCanvas";
import { getIcon } from "./SketchIcons";

export interface StencilPreset extends NodePreset {
  id: string;
  labelHint: string;
  /** Shown to the user as the reason why a drop was rejected (if non-null). */
  dropHint?: string;
}

/**
 * Top-level presets — land directly on the canvas, auto-snap to the
 * correct layer (upper = services, lower = actors).
 */
const TOP_LEVEL: StencilPreset[] = [
  {
    id: "actor",
    labelHint: "Actor",
    shape: "circle",
    color: "#fecaca",
    width: 130,
    height: 130,
    icon: "user",
    label: "Actor",
    kind: "actor",
  },
  {
    id: "service",
    labelHint: "Service",
    shape: "rounded",
    color: "#bae6fd",
    width: 300,
    height: 200,
    icon: "zap",
    label: "Service",
    kind: "service",
  },
];

/**
 * Service internals visible on the canvas = decomposition only.
 *
 * Composition kinds (rule, content) are edited via the right-hand
 * Inspector panel, not rendered as nodes. Keeping them out of the
 * stencil prevents users from dropping them onto the canvas by
 * accident.
 */
const SERVICE_INTERNAL: StencilPreset[] = [
  {
    id: "sub-service",
    labelHint: "Sub-Service",
    shape: "rounded",
    color: "#bae6fd",
    width: 160,
    height: 80,
    icon: "zap",
    label: "Sub-Service",
    kind: "service",
    dropHint: "Drop inside a Service container",
  },
];

/**
 * Actor internals — sub-actor only (decomposition). No composition kinds
 * yet; that's a v0.3 open question (permission / capability / goal / …).
 */
const ACTOR_INTERNAL: StencilPreset[] = [
  {
    id: "sub-actor",
    labelHint: "Sub-Actor",
    shape: "circle",
    color: "#fecaca",
    width: 100,
    height: 100,
    icon: "user",
    label: "Sub-Actor",
    kind: "actor",
    dropHint: "Drop inside an Actor container",
  },
];

export const STENCIL_PRESETS: StencilPreset[] = [
  ...TOP_LEVEL,
  ...SERVICE_INTERNAL,
  ...ACTOR_INTERNAL,
];

/**
 * Validation rule applied at drop-time. Returns the `parent_id` that the
 * new node should use, or `null` if the drop is top-level, or a string
 * error message if the drop is invalid.
 *
 * - Top-level kinds (actor, service with empty `dropHint`) land at top.
 * - Composition kinds (rule, content) require a Service parent.
 * - sub-service requires a Service parent (decomposition).
 * - sub-actor requires an Actor parent (decomposition).
 */
export function resolveDropTarget(
  preset: StencilPreset,
  containerAtDrop: { id: string; kind: NodeKind | null } | null,
): { parentId: string | null } | { error: string } {
  const isComposition = preset.kind === "rule" || preset.kind === "content";
  const isSubService = preset.id === "sub-service";
  const isSubActor = preset.id === "sub-actor";

  if (isComposition || isSubService) {
    if (!containerAtDrop || containerAtDrop.kind !== "service") {
      return { error: preset.dropHint ?? "Drop inside a Service container" };
    }
    return { parentId: containerAtDrop.id };
  }
  if (isSubActor) {
    if (!containerAtDrop || containerAtDrop.kind !== "actor") {
      return { error: preset.dropHint ?? "Drop inside an Actor container" };
    }
    return { parentId: containerAtDrop.id };
  }
  // Top-level — dropping inside a container is ambiguous for now, so
  // land at top regardless (user can still drag in afterwards).
  return { parentId: null };
}

function StencilItem({ preset }: { preset: StencilPreset }) {
  const Icon = getIcon(preset.icon);
  return (
    <li>
      <div
        draggable
        onDragStart={(e) => {
          const { id: _id, labelHint: _lh, dropHint: _dh, ...inner } = preset;
          e.dataTransfer.setData(
            "application/plot-preset",
            JSON.stringify(inner),
          );
          e.dataTransfer.effectAllowed = "copy";
        }}
        className="flex cursor-grab items-center gap-2 rounded border border-slate-200 bg-white px-2 py-1.5 text-xs text-slate-700 shadow-sm hover:bg-slate-50 active:cursor-grabbing"
        title={preset.dropHint ?? `Drag ${preset.labelHint} onto the canvas`}
      >
        <span
          className="flex h-6 w-6 shrink-0 items-center justify-center"
          style={{
            backgroundColor: preset.color,
            borderRadius:
              preset.shape === "circle" || preset.shape === "ellipse"
                ? "50%"
                : preset.shape === "rounded"
                  ? 4
                  : 0,
            clipPath:
              preset.shape === "diamond"
                ? "polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)"
                : preset.shape === "hexagon"
                  ? "polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)"
                  : undefined,
          }}
        >
          {Icon && <Icon size={12} className="text-slate-700" aria-hidden />}
        </span>
        <span className="truncate">{preset.labelHint}</span>
      </div>
    </li>
  );
}

export function SketchStencil() {
  return (
    <div className="border-t border-slate-200 px-3 py-3">
      <Section title="Top-level" presets={TOP_LEVEL} />
      <Section title="Service internals" presets={SERVICE_INTERNAL} note="drop into a Service" />
      <Section title="Actor internals" presets={ACTOR_INTERNAL} note="drop into an Actor" />
    </div>
  );
}

function Section({
  title,
  presets,
  note,
}: {
  title: string;
  presets: StencilPreset[];
  note?: string;
}) {
  return (
    <div className="mb-3">
      <div className="mb-1 flex items-baseline justify-between">
        <div className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
          {title}
        </div>
        {note && <div className="text-[9px] italic text-slate-400">{note}</div>}
      </div>
      <ul className="space-y-1">
        {presets.map((p) => (
          <StencilItem key={p.id} preset={p} />
        ))}
      </ul>
    </div>
  );
}
