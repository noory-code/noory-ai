/**
 * Registry mapping ``NodeKind`` → its per-kind inspector component.
 *
 * Phase 2.0 starts empty. Phase 2.1+ adds one entry per commit as each
 * ``inspectors/{kind}/index.tsx`` lands. Phase 2.10 closes the loop —
 * every kind is registered, the legacy ``SketchInspector`` is deleted,
 * and ``KindInspector`` becomes the sole inspector entry point.
 *
 * The map is intentionally ``Partial<...>`` during the migration so a
 * kind without a registered inspector returns ``undefined`` and the
 * caller can fall back to the legacy implementation.
 */
import type { FC } from "react";
import type { NodeKind } from "../../types";
import { ActorRefInspector } from "./actor_ref";
import { CategoryInspector } from "./category";
import { CoreValueInspector } from "./core_value";
import { IdentityInspector } from "./identity";
import { IdentityRefInspector } from "./identity_ref";
import { MetricInspector } from "./metric";
import { MissionInspector } from "./mission";
import { MissionRefInspector } from "./mission_ref";
import { ProjectInspector } from "./project";
import { StepInspector } from "./step";
import type { KindInspectorProps } from "./types";
import { ValueRefInspector } from "./value_ref";

export type KindInspectorComponent = FC<KindInspectorProps>;

export const KIND_INSPECTORS: Partial<Record<NodeKind, KindInspectorComponent>> = {
  // Phase 2.1+ per-kind entries land here.
  metric: MetricInspector,
  step: StepInspector,
  core_value: CoreValueInspector,
  identity: IdentityInspector,
  mission: MissionInspector,
  project: ProjectInspector,
  category: CategoryInspector,
  actor_ref: ActorRefInspector,
  mission_ref: MissionRefInspector,
  value_ref: ValueRefInspector,
  identity_ref: IdentityRefInspector,
};

/** Look up the registered inspector for a kind, or ``undefined`` while
 *  the migration is mid-flight. */
export function lookupKindInspector(
  kind: NodeKind | undefined | null,
): KindInspectorComponent | undefined {
  if (!kind) return undefined;
  return KIND_INSPECTORS[kind];
}
