import { useTranslation } from "react-i18next";
import type { NodeKind, SketchNode } from "../types";
import type { NodePreset } from "./sketch/types";
import { useStencilDrag } from "./sketch/StencilDragContext";
import { getIcon } from "./SketchIcons";
import { SectionInfo } from "./stencil/SectionInfo";

export interface StencilPreset extends NodePreset {
  id: string;
  labelHint: string;
  /** Shown to the user as the reason why a drop was rejected (if non-null). */
  dropHint?: string;
  /** v0.14.11: i18n key for the stencil sidebar label. Falls back to
   *  ``kind.${kind}`` when undefined; falls back to ``labelHint`` when
   *  explicitly ``null`` (used by dynamic ref presets where the
   *  master's name is the SSOT — see D-2026-05-26-E). The drop-time
   *  node label (``label``) stays language-pinned because it becomes
   *  user data the instant the drop lands. */
  labelI18nKey?: string | null;
  /** v0.14.11: i18n key for the ``dropHint`` tooltip line. Falls back
   *  to ``dropHint`` when absent. */
  dropHintI18nKey?: string;
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
  // v0.26.1 (D-2026-05-25-B) — non-Symbol kinds default to rectangle.
  shape: "rectangle",
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
  shape: "rectangle",
  color: "#bae6fd",
  width: 160,
  height: 80,
  icon: "zap",
  label: "Service",
  kind: "service",
  dropHint: "Drop inside a Category container",
  dropHintI18nKey: "stencil.dropHintIntoCategory",
};

// D-2026-06-17-D — a ``feature`` is a capability nested under a service (the
// sole drill target). Lighter tint than a service; drops inside a Service.
const FEATURE_INSIDE_SERVICE: StencilPreset = {
  id: "feature-in-service",
  labelHint: "Feature",
  labelI18nKey: "kind.feature",
  shape: "rectangle",
  color: "#e0f2fe",
  width: 150,
  height: 64,
  icon: null,
  label: "Feature",
  kind: "feature",
  dropHint: "Drop inside a Service",
  dropHintI18nKey: "stencil.dropHintIntoService",
};

// Core-canvas presets. The Project anchor at the centre is auto-seeded,
// not draggable — mission / core_value / identity are the user-placed
// pillars. In v0.5 Identity is flat N peers (one per aspect: Voice /
// Energy / Speech style / …); identity_facet was folded into identity.
// v0.27.11 (D-2026-05-28-D) — Symbol kinds default to circle.
// D-2026-05-19-D defines Symbol = mission / core_value / identity / actor
// (+ their refs in the consumer plane). Per user 2026-05-28, all Symbol
// presets should drop as circles, not rounded rectangles, so the
// producer/consumer plane reading is visually consistent.

const CORE_MISSION: StencilPreset = {
  id: "mission",
  labelHint: "Mission",
  shape: "circle",
  color: "#fef3c7",
  width: 160,
  height: 160,
  icon: null,
  label: "Mission",
  kind: "mission",
};

const CORE_VALUE: StencilPreset = {
  id: "core-value",
  labelHint: "Core Value",
  shape: "circle",
  color: "#fde68a",
  width: 140,
  height: 140,
  icon: null,
  label: "Core Value",
  kind: "core_value",
};

const CORE_IDENTITY: StencilPreset = {
  id: "identity",
  labelHint: "Identity",
  shape: "circle",
  color: "#fed7aa",
  width: 160,
  height: 160,
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
  // v0.27.11 (D-2026-05-28-D) — ref kinds inherit the Symbol shape
  // (circle). Pre-v0.27.11 they were rectangle per D-2026-05-25-B but
  // that made the Symbol-vs-non-Symbol reading inconsistent on the
  // consumer plane.
  shape: "circle",
  color: "#fce7f3",
  width: 120,
  height: 120,
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
  // v0.27.11 (D-2026-05-28-D) — Symbol ref → circle.
  shape: "circle",
  color: "#fef3c7",
  width: 120,
  height: 120,
  icon: "flag",
  label: "→ Mission",
  kind: "mission_ref",
};

const VALUE_REF: StencilPreset = {
  id: "value-ref",
  labelHint: "Value ref",
  shape: "circle",
  color: "#fde68a",
  width: 120,
  height: 120,
  icon: "star",
  label: "→ Value",
  kind: "value_ref",
};

const IDENTITY_REF: StencilPreset = {
  id: "identity-ref",
  labelHint: "Identity ref",
  shape: "circle",
  color: "#fed7aa",
  width: 120,
  height: 120,
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
    // v0.26.1 (D-2026-05-25-B) — non-Symbol kind, rectangle default.
    shape: "rectangle",
    color: "#d9f99d",
    width: 150,
    height: 60,
    icon: "target",
    label: "Metric",
    kind: "metric",
    dropHint: "Drop inside a Service container",
    dropHintI18nKey: "stencil.dropHintIntoService",
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
    dropHintI18nKey: "stencil.dropHintIntoService",
  },
  {
    // v0.28.0 (D-2026-05-30-C) — flowchart decision (diamond). Shape is
    // forced to diamond at the renderer (BaseNode.effectiveShape), so the
    // stored shape here is cosmetic; kept "diamond" for honesty.
    id: "decision",
    labelHint: "Decision",
    shape: "diamond",
    color: "#fde68a",
    width: 130,
    height: 90,
    icon: "git-fork",
    label: "Decision",
    kind: "decision",
    dropHint: "Drop inside a Service container",
    dropHintI18nKey: "stencil.dropHintIntoService",
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
    labelI18nKey: "stencil.subActor",
    shape: "circle",
    color: "#fecaca",
    width: 100,
    height: 100,
    icon: "user",
    label: "Sub-Actor",
    kind: "actor",
    dropHint: "Drop inside an Actor container",
    dropHintI18nKey: "stencil.dropHintIntoActor",
  },
];

export const STENCIL_PRESETS: StencilPreset[] = [
  TOP_LEVEL_ACTOR,
  TOP_LEVEL_CATEGORY,
  SERVICE_INSIDE_CATEGORY,
  FEATURE_INSIDE_SERVICE,
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
 * - Composition kinds (metric, step):
 *     - On the Services canvas (rare; not in stencil today) they would
 *       require a Service parent.
 *     - On the ServiceDetail canvas (D-2026-05-28-A) they are FREE-FORM
 *       — the user is authoring an interaction graph: actors / value
 *       nodes / interaction nodes live as peers, wired by edges, not
 *       nested under the service container. Dropping inside a service
 *       container still nests (backwards-compat) so the prior model
 *       keeps working; dropping on empty space lands as a top-level peer.
 * - sub-actor requires an Actor parent (decomposition).
 */
export function resolveDropTarget(
  preset: StencilPreset,
  containerAtDrop: { id: string; kind: NodeKind | null } | null,
  /** v0.27.10 (D-2026-05-28-A) — the canvas where the drop happens.
   *  When undefined, behaves as pre-v0.27.10 (composition requires a
   *  service parent unconditionally). */
  canvasKind?: StencilCanvas,
): { parentId: string | null } | { error: string } {
  const isComposition =
    preset.kind === "metric" || preset.kind === "step" || preset.kind === "decision";
  const isSubActor = preset.id === "sub-actor";
  // v0.12: a service preset on the Services canvas drops *inside a
  // category* (services are leaves nested under a category).
  const isServiceInsideCategory = preset.id === "service-in-category";
  // D-2026-06-17-D — a feature nests under a service (the drill target lives
  // one level below its service).
  const isFeatureInsideService = preset.id === "feature-in-service";

  if (isComposition) {
    // D-2026-05-28-A: ServiceDetail is a user-authored interaction
    // graph — composition kinds (metric / step, re-purposed as
    // value / interaction nodes by the user) drop freely. Nesting
    // inside a service container is still honoured when the user
    // explicitly drops on one.
    if (canvasKind === "service_detail") {
      return { parentId: containerAtDrop?.kind === "service" ? containerAtDrop.id : null };
    }
    if (!containerAtDrop || containerAtDrop.kind !== "service") {
      return { error: preset.dropHint ?? "Drop inside a Service container" };
    }
    return { parentId: containerAtDrop.id };
  }
  if (isServiceInsideCategory) {
    // D-2026-06-13-D — category is an OPTIONAL grouping. A service dropped
    // onto a category nests under it; dropped anywhere else it lands
    // top-level (no longer rejected). User: "카테고리는 옵셔널 할 수 있습니다".
    // Supersedes the D-2026-05-28-A "service must nest in a Category" rule.
    return {
      parentId: containerAtDrop?.kind === "category" ? containerAtDrop.id : null,
    };
  }
  if (isFeatureInsideService) {
    // D-2026-06-17-D — a feature dropped onto a service nests under it
    // (directed edge service→feature); dropped elsewhere it lands top-level.
    return {
      parentId: containerAtDrop?.kind === "service" ? containerAtDrop.id : null,
    };
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
  const { t } = useTranslation();
  const { beginDrag } = useStencilDrag();
  const Icon = getIcon(preset.icon);
  // v0.14.11 / v0.27.2 (D-2026-05-26-E): label resolution order:
  //   1. explicit ``labelI18nKey === null`` → labelHint wins (dynamic
  //      ref presets carry the master's name in labelHint; we must
  //      NOT fall through to ``kind.${kind}`` which would replace
  //      every "Hero" / "Fan" / "관용" stencil item with the generic
  //      "Actor (ref)" / "Core value (ref)" — the pre-v0.27.2 bug).
  //   2. explicit ``labelI18nKey`` string → use it.
  //   3. has ``kind`` → ``kind.${kind}``.
  //   4. fallback → labelHint.
  const labelKey =
    preset.labelI18nKey === null
      ? ""
      : (preset.labelI18nKey ?? (preset.kind ? `kind.${preset.kind}` : ""));
  const label = labelKey ? t(labelKey, { defaultValue: preset.labelHint }) : preset.labelHint;
  const dropHintText = preset.dropHintI18nKey
    ? t(preset.dropHintI18nKey)
    : preset.dropHint;
  return (
    <li>
      <div
        data-stencil-item={preset.id}
        onPointerDown={(e) => beginDrag(preset, e)}
        className="flex cursor-grab touch-none select-none items-center gap-2 rounded border border-line bg-surface px-2 py-1.5 text-xs text-fg shadow-sm hover:bg-surface-muted active:cursor-grabbing"
        title={dropHintText ?? t("stencil.dragOntoCanvas", { name: label })}
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
          {Icon && <Icon size={12} className="text-fg" aria-hidden />}
        </span>
        <span className="truncate">{label}</span>
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
  const { t } = useTranslation();
  if (canvas === "foundation") {
    return (
      <div className="border-t border-line px-3 py-3">
        <Section
          title={t("stencil.section.mission")}
          presets={[CORE_MISSION]}
          info={t("stencil.info.mission")}
        />
        <Section
          title={t("stencil.section.coreValues")}
          presets={[CORE_VALUE]}
          info={t("stencil.info.coreValues")}
        />
        <Section
          title={t("stencil.section.identity")}
          presets={[CORE_IDENTITY]}
          info={t("stencil.info.identity")}
        />
      </div>
    );
  }
  if (canvas === "actors") {
    return (
      <div className="border-t border-line px-3 py-3">
        <Section title={t("stencil.section.topLevel")} presets={[TOP_LEVEL_ACTOR]} />
        <Section
          title={t("stencil.section.actorHierarchy")}
          presets={ACTOR_INTERNAL}
          note={t("stencil.note.dropOnActor")}
        />
      </div>
    );
  }
  if (canvas === "services") {
    // v0.12 — services canvas: project + category + services-inside-category.
    // The category is the top-level grouping; services are leaves.
    return (
      <div className="border-t border-line px-3 py-3">
        <Section title={t("stencil.section.topLevel")} presets={[TOP_LEVEL_CATEGORY]} />
        <Section
          title={t("stencil.section.service")}
          presets={[SERVICE_INSIDE_CATEGORY]}
          note={t("stencil.note.dropInsideCategory")}
        />
        <Section
          title={t("stencil.section.feature")}
          presets={[FEATURE_INSIDE_SERVICE]}
          note={t("stencil.note.dropInsideService")}
        />
      </div>
    );
  }
  // service_detail (v0.12 modal) — D-2026-05-28-C re-frames Composition
  // into the user's design model: "인터랙션" (step, between actors) +
  // "가치" (metric, exchanged via interactions). The underlying kinds
  // stay step / metric (no new domain kinds, D-2026-05-26-C YAGNI), but
  // the stencil section + item labels read as the user's mental model.
  const stepPreset = SERVICE_COMPOSITION.find((p) => p.id === "step");
  const metricPreset = SERVICE_COMPOSITION.find((p) => p.id === "metric");
  const decisionRaw = SERVICE_COMPOSITION.find((p) => p.id === "decision");
  const decisionPreset: StencilPreset | null = decisionRaw
    ? { ...decisionRaw, labelI18nKey: "kind.decision", labelHint: "Decision" }
    : null;
  const interactionPreset: StencilPreset | null = stepPreset
    ? { ...stepPreset, labelI18nKey: "kind.interaction", labelHint: "Interaction" }
    : null;
  const valuePreset: StencilPreset | null = metricPreset
    ? { ...metricPreset, labelI18nKey: "kind.value", labelHint: "Value" }
    : null;
  const actorRefPresets = availableActors.map((a) => actorRefPresetFor(a));
  const missionRefPresets = availableMissions.map((m) => missionRefPresetFor(m));
  const valueRefPresets = availableValues.map((v) => valueRefPresetFor(v));
  const identityRefPresets = availableIdentities.map((i) => identityRefPresetFor(i));
  // v0.28.5 (D-2026-05-30-H) — the stencil mirrors the 2-layer essence
  // model (VISION 3-phase): ① the concrete flow the user designs
  // (Execution: actor → interaction → decision → value), then ② the
  // essence injected onto it (Retention: mission / core value /
  // identity refs). Reading top-to-bottom = "build the flow, then
  // inject the essence."
  return (
    <div className="border-t border-line px-3 py-3">
      <LayerHeader label={t("stencil.layer.flow")} hint={t("stencil.layer.flowHint")} />
      {actorRefPresets.length > 0 && (
        <Section
          title={t("stencil.section.actors")}
          presets={actorRefPresets}
          note={t("stencil.note.dragActorOntoService")}
        />
      )}
      {interactionPreset && (
        <Section
          title={t("stencil.section.interactions")}
          presets={decisionPreset ? [interactionPreset, decisionPreset] : [interactionPreset]}
          note={t("stencil.note.interactionsBetweenActors")}
        />
      )}
      {valuePreset && (
        <Section
          title={t("stencil.section.values")}
          presets={[valuePreset]}
          note={t("stencil.note.valuesExchanged")}
        />
      )}
      <LayerHeader label={t("stencil.layer.essence")} hint={t("stencil.layer.essenceHint")} />
      {missionRefPresets.length > 0 && (
        <Section
          title={t("stencil.section.missions")}
          presets={missionRefPresets}
          note={t("stencil.note.dragMissionThisServiceAnswersTo")}
        />
      )}
      {valueRefPresets.length > 0 && (
        <Section
          title={t("stencil.section.coreValues")}
          presets={valueRefPresets}
          note={t("stencil.note.dragValueThisServiceEmbodies")}
        />
      )}
      {identityRefPresets.length > 0 && (
        <Section
          title={t("stencil.section.identityAspects")}
          presets={identityRefPresets}
          note={t("stencil.note.dragIdentityAspectThisServiceExpresses")}
        />
      )}
    </div>
  );
}

/** v0.28.5 (D-2026-05-30-H) — a layer divider above a stencil group.
 *  Heavier than a Section title: it names one of the two essence
 *  layers (① concrete flow / ② essence injection). */
function LayerHeader({ label, hint }: { label: string; hint?: string }) {
  return (
    <div className="mb-2 mt-1 border-b-2 border-line-strong pb-1">
      <div className="text-[11px] font-bold tracking-wide text-fg">{label}</div>
      {hint && <div className="text-[9px] italic text-fg-faint">{hint}</div>}
    </div>
  );
}

// v0.11.5 dynamic ref presets — each master becomes its own draggable.
// The preset already carries the master id, so SketchCanvas's drop
// handler creates the ref instance directly without opening a picker.

// v0.27.11 (D-2026-05-28-D) — dynamic Symbol-ref presets inherit the
// Symbol shape (circle), matching the static MISSION_REF / VALUE_REF /
// IDENTITY_REF / ACTOR_REF presets above.

function actorRefPresetFor(a: SketchNode): StencilPreset {
  // v0.15: only actor kind has ``side``; narrow before reading.
  const side = a.kind === "actor" ? a.side : null;
  return {
    id: `actor-ref:${a.id}`,
    labelHint: a.label || a.id,
    labelI18nKey: null,
    shape: "circle",
    color: side === "operator" ? "#bae6fd" : "#fce7f3",
    width: 120,
    height: 120,
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
    labelI18nKey: null,
    shape: "circle",
    color: "#fef3c7",
    width: 120,
    height: 120,
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
    labelI18nKey: null,
    shape: "circle",
    color: "#fde68a",
    width: 120,
    height: 120,
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
    labelI18nKey: null,
    shape: "circle",
    color: "#fed7aa",
    width: 120,
    height: 120,
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
  info,
}: {
  title: string;
  presets: StencilPreset[];
  note?: string;
  info?: string;
}) {
  return (
    <div className="mb-3">
      <div className="mb-1 flex items-baseline justify-between">
        <div className="flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide text-fg-muted">
          {title}
          {info && <SectionInfo text={info} />}
        </div>
        {note && <div className="text-[9px] italic text-fg-faint">{note}</div>}
      </div>
      <ul className="space-y-1">
        {presets.map((p) => (
          <StencilItem key={p.id} preset={p} />
        ))}
      </ul>
    </div>
  );
}
