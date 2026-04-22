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
const TOP_LEVEL_ACTOR: StencilPreset = {
  id: "actor",
  labelHint: "Actor",
  shape: "circle",
  color: "#fecaca",
  width: 130,
  height: 130,
  icon: "user",
  label: "Actor",
  kind: "actor",
};

const TOP_LEVEL_SERVICE: StencilPreset = {
  id: "service",
  labelHint: "Service",
  shape: "rounded",
  color: "#bae6fd",
  width: 300,
  height: 200,
  icon: "zap",
  label: "Service",
  kind: "service",
};

// Core-canvas presets. The Project anchor at the centre is auto-seeded,
// not draggable — mission / core_value / identity are the user-placed
// pillars. In v0.5 Identity is flat N peers (one per aspect: Voice /
// Energy / Speech style / …); identity_facet was folded into identity.
const CORE_MISSION: StencilPreset = {
  id: "mission",
  labelHint: "Mission",
  shape: "rounded",
  color: "#fef3c7",
  width: 200,
  height: 90,
  icon: null,
  label: "Mission",
  kind: "mission",
};

const CORE_VALUE: StencilPreset = {
  id: "core-value",
  labelHint: "Core Value",
  shape: "rounded",
  color: "#fde68a",
  width: 160,
  height: 70,
  icon: null,
  label: "Core Value",
  kind: "core_value",
};

const CORE_IDENTITY: StencilPreset = {
  id: "identity",
  labelHint: "Identity",
  shape: "rounded",
  color: "#fed7aa",
  width: 200,
  height: 90,
  icon: null,
  label: "Voice",
  kind: "identity",
};

// Actor reference — places a pointer to an Actor-canvas node on a
// Service canvas. Lighter pink + a "→" prefix so it's visually distinct
// from the original. The ref_actor_id is filled in by the picker modal.
const ACTOR_REF: StencilPreset = {
  id: "actor-ref",
  labelHint: "Actor ref",
  shape: "ellipse",
  color: "#fce7f3",
  width: 140,
  height: 70,
  icon: "user",
  label: "→ actor",
  kind: "actor_ref",
};

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
  TOP_LEVEL_ACTOR,
  TOP_LEVEL_SERVICE,
  ...SERVICE_INTERNAL,
  ...ACTOR_INTERNAL,
  CORE_MISSION,
  CORE_VALUE,
  CORE_IDENTITY,
  ACTOR_REF,
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
                  : preset.shape === "octagon"
                    ? "polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)"
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

/** v0.2 multi-canvas: the tab that owns the presets shown in the stencil. */
export type StencilCanvas = "core" | "actors" | "services";

export function SketchStencil({ canvas }: { canvas: StencilCanvas }) {
  if (canvas === "core") {
    return (
      <div className="border-t border-slate-200 px-3 py-3">
        <Section
          title="Mission"
          presets={[CORE_MISSION]}
          note="add as many as you need"
        />
        <Section
          title="Core values"
          presets={[CORE_VALUE]}
          note="add as many as you need"
        />
        <Section
          title="Identity"
          presets={[CORE_IDENTITY]}
          note="one per aspect — Voice, Energy, Speech style, …"
        />
      </div>
    );
  }
  if (canvas === "actors") {
    return (
      <div className="border-t border-slate-200 px-3 py-3">
        <Section title="Top-level" presets={[TOP_LEVEL_ACTOR]} />
        <Section
          title="Actor hierarchy"
          presets={ACTOR_INTERNAL}
          note="drop on an Actor"
        />
      </div>
    );
  }
  // services
  return (
    <div className="border-t border-slate-200 px-3 py-3">
      <Section title="Top-level" presets={[TOP_LEVEL_SERVICE]} />
      <Section
        title="Service hierarchy"
        presets={SERVICE_INTERNAL}
        note="drop on a Service"
      />
      <Section
        title="Participants"
        presets={[ACTOR_REF]}
        note="pick from Actor canvas"
      />
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
