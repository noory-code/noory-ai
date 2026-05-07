import type { NodeKind, SketchNode } from "../types";
import type { NodePreset } from "./sketch/types";
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

const TOP_LEVEL_CATEGORY: StencilPreset = {
  id: "category",
  labelHint: "Category",
  shape: "rounded",
  color: "#e2e8f0",
  width: 220,
  height: 120,
  icon: null,
  label: "Category",
  kind: "category",
};

const SERVICE_INSIDE_CATEGORY: StencilPreset = {
  id: "service-in-category",
  labelHint: "Service",
  shape: "rounded",
  color: "#bae6fd",
  width: 160,
  height: 80,
  icon: "zap",
  label: "Service",
  kind: "service",
  dropHint: "Drop inside a Category container",
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

// v0.10 Step 3: Foundation references — symbol/component instances of a
// Mission / Core Value / Identity master from the Foundation canvas.
// Distinct hue per kind so the canvas reads at a glance: yellow = Mission,
// amber = Value, orange = Identity (matching the Foundation stencil tints).
// Each carries its specific ref_*_id once the picker resolves the target.
const MISSION_REF: StencilPreset = {
  id: "mission-ref",
  labelHint: "Mission ref",
  shape: "ellipse",
  color: "#fef3c7",
  width: 160,
  height: 60,
  icon: "flag",
  label: "→ Mission",
  kind: "mission_ref",
};

const VALUE_REF: StencilPreset = {
  id: "value-ref",
  labelHint: "Value ref",
  shape: "ellipse",
  color: "#fde68a",
  width: 160,
  height: 60,
  icon: "star",
  label: "→ Value",
  kind: "value_ref",
};

const IDENTITY_REF: StencilPreset = {
  id: "identity-ref",
  labelHint: "Identity ref",
  shape: "ellipse",
  color: "#fed7aa",
  width: 160,
  height: 60,
  icon: "heart",
  label: "→ Identity",
  kind: "identity_ref",
};

const FOUNDATION_REFS: StencilPreset[] = [MISSION_REF, VALUE_REF, IDENTITY_REF];

/**
 * Service internals visible on the canvas = decomposition only.
 *
 * rule / content remain Inspector-only (they're small structured items
 * edited via the "+ Add" button, not dragged), but v0.10 Step 5 adds
 * metric / step as canvas-first composition: an ordered procedural
 * flow (steps) and explicit success indicators (metrics) make more
 * sense visually on the Service-Detail canvas than buried in a list.
 */
// v0.12 — sub-service is gone. Service is a leaf inside a category;
// nothing nests inside a service on the Services canvas.

const SERVICE_COMPOSITION: StencilPreset[] = [
  {
    id: "metric",
    labelHint: "Metric",
    shape: "rounded",
    color: "#d9f99d",
    width: 150,
    height: 60,
    icon: "target",
    label: "Metric",
    kind: "metric",
    dropHint: "Drop inside a Service container",
  },
  {
    id: "step",
    labelHint: "Step",
    shape: "rectangle",
    color: "#e0e7ff",
    width: 150,
    height: 60,
    icon: "clipboard-list",
    label: "Step",
    kind: "step",
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
  TOP_LEVEL_CATEGORY,
  SERVICE_INSIDE_CATEGORY,
  ...SERVICE_COMPOSITION,
  ...ACTOR_INTERNAL,
  CORE_MISSION,
  CORE_VALUE,
  CORE_IDENTITY,
  ACTOR_REF,
  ...FOUNDATION_REFS,
];

/**
 * Validation rule applied at drop-time. Returns the `parent_id` that the
 * new node should use, or `null` if the drop is top-level, or a string
 * error message if the drop is invalid.
 *
 * - Top-level kinds (actor, category) land at top.
 * - service (v0.12) requires a Category parent on the Services canvas.
 * - Composition kinds (rule, content, metric, step) require a Service
 *   parent on the Service Detail modal.
 * - sub-actor requires an Actor parent (decomposition).
 */
export function resolveDropTarget(
  preset: StencilPreset,
  containerAtDrop: { id: string; kind: NodeKind | null } | null,
): { parentId: string | null } | { error: string } {
  // v0.10 Step 5: metric + step join rule + content as composition kinds
  // — they all require a service parent.
  const isComposition =
    preset.kind === "rule" ||
    preset.kind === "content" ||
    preset.kind === "metric" ||
    preset.kind === "step";
  const isSubActor = preset.id === "sub-actor";
  // v0.12: a service preset on the Services canvas drops *inside a
  // category* (services are leaves nested under a category).
  const isServiceInsideCategory = preset.id === "service-in-category";

  if (isComposition) {
    if (!containerAtDrop || containerAtDrop.kind !== "service") {
      return { error: preset.dropHint ?? "Drop inside a Service container" };
    }
    return { parentId: containerAtDrop.id };
  }
  if (isServiceInsideCategory) {
    if (!containerAtDrop || containerAtDrop.kind !== "category") {
      return { error: preset.dropHint ?? "Drop inside a Category container" };
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

/** v0.2 multi-canvas: the tab that owns the presets shown in the stencil.
 *  v0.12 — services-side surfaces:
 *  ``services`` (top view: project + categories + their service leaves) and
 *  ``service_detail`` (per-service modal: composition + dynamic refs). */
export type StencilCanvas = "foundation" | "actors" | "services" | "service_detail";

interface SketchStencilProps {
  canvas: StencilCanvas;
  /** v0.11.5 — masters for the dynamic ref presets shown on the
   *  service_detail stencil. Each master becomes its own draggable
   *  preset that drops directly (no picker round-trip). */
  availableActors?: SketchNode[];
  availableMissions?: SketchNode[];
  availableValues?: SketchNode[];
  availableIdentities?: SketchNode[];
}

export function SketchStencil({
  canvas,
  availableActors = [],
  availableMissions = [],
  availableValues = [],
  availableIdentities = [],
}: SketchStencilProps) {
  if (canvas === "foundation") {
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
  if (canvas === "services") {
    // v0.12 — services canvas: project + category + services-inside-category.
    // The category is the top-level grouping; services are leaves.
    return (
      <div className="border-t border-slate-200 px-3 py-3">
        <Section title="Top-level" presets={[TOP_LEVEL_CATEGORY]} />
        <Section
          title="Service"
          presets={[SERVICE_INSIDE_CATEGORY]}
          note="drop inside a Category"
        />
      </div>
    );
  }
  // service_detail (v0.12 modal) — composition + dynamic refs. Each ref
  // preset is generated per master so drops skip the picker and the
  // stencil reads as the project's actual cast (10 missions = 10 mission
  // ref entries with their real labels).
  const actorRefPresets = availableActors.map((a) => actorRefPresetFor(a));
  const missionRefPresets = availableMissions.map((m) => missionRefPresetFor(m));
  const valueRefPresets = availableValues.map((v) => valueRefPresetFor(v));
  const identityRefPresets = availableIdentities.map((i) => identityRefPresetFor(i));
  return (
    <div className="border-t border-slate-200 px-3 py-3">
      <Section
        title="Composition"
        presets={SERVICE_COMPOSITION}
        note="metrics + steps inside this service"
      />
      {actorRefPresets.length > 0 && (
        <Section
          title="Actors"
          presets={actorRefPresets}
          note="drag any actor onto this service"
        />
      )}
      {missionRefPresets.length > 0 && (
        <Section
          title="Missions"
          presets={missionRefPresets}
          note="drag a mission this service answers to"
        />
      )}
      {valueRefPresets.length > 0 && (
        <Section
          title="Core values"
          presets={valueRefPresets}
          note="drag a value this service embodies"
        />
      )}
      {identityRefPresets.length > 0 && (
        <Section
          title="Identity aspects"
          presets={identityRefPresets}
          note="drag an identity aspect this service expresses"
        />
      )}
    </div>
  );
}

// v0.11.5 dynamic ref presets — each master becomes its own draggable.
// The preset already carries the master id, so SketchCanvas's drop
// handler creates the ref instance directly without opening a picker.

function actorRefPresetFor(a: SketchNode): StencilPreset {
  return {
    id: `actor-ref:${a.id}`,
    labelHint: a.label || a.id,
    shape: "ellipse",
    color: a.side === "operator" ? "#bae6fd" : "#fce7f3",
    width: 140,
    height: 70,
    icon: "user",
    label: `→ ${a.label || a.id}`,
    kind: "actor_ref",
    ref_actor_id: a.id,
  };
}

function missionRefPresetFor(m: SketchNode): StencilPreset {
  return {
    id: `mission-ref:${m.id}`,
    labelHint: m.label || m.id,
    shape: "ellipse",
    color: "#fef3c7",
    width: 160,
    height: 60,
    icon: "flag",
    label: `→ ${m.label || m.id}`,
    kind: "mission_ref",
    ref_mission_id: m.id,
  };
}

function valueRefPresetFor(v: SketchNode): StencilPreset {
  return {
    id: `value-ref:${v.id}`,
    labelHint: v.label || v.id,
    shape: "ellipse",
    color: "#fde68a",
    width: 160,
    height: 60,
    icon: "star",
    label: `→ ${v.label || v.id}`,
    kind: "value_ref",
    ref_value_id: v.id,
  };
}

function identityRefPresetFor(i: SketchNode): StencilPreset {
  return {
    id: `identity-ref:${i.id}`,
    labelHint: i.label || i.id,
    shape: "ellipse",
    color: "#fed7aa",
    width: 160,
    height: 60,
    icon: "heart",
    label: `→ ${i.label || i.id}`,
    kind: "identity_ref",
    ref_identity_id: i.id,
  };
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
