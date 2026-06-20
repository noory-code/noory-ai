/**
 * Per-kind React Flow node renderer registry.
 *
 * v0.15 Phase 3.1 — replaces the single ``{ sketch: SketchNode }``
 * map that had every kind go through one god renderer. Phase 3.2+
 * canvas wrappers each expose a SUBSET of this registry to React Flow
 * (e.g. FoundationCanvas only registers project/mission/core_value/
 * identity), so a node of an unknown kind never reaches the canvas.
 *
 * The registry keys mirror the React-Flow ``data.kind`` literal that
 * each node carries; ``SketchNode`` (the discriminated union from
 * ``../../domain``) and the kind names from ``viewer/src/types.ts``
 * are the SSOT.
 */
import type { ComponentType } from "react";
import type { NodeProps } from "reactflow";
import type { NodeKind } from "../../types";
import type { BaseNodeData } from "./BaseNode";
import { ActorNode } from "./actor";
import { ActorRefNode } from "./actor_ref";
import { CategoryNode } from "./category";
import { CoreValueNode } from "./core_value";
import { DecisionNode } from "./decision";
import { EntityNode } from "./entity";
import { FeatureNode } from "./feature";
import { IdentityNode } from "./identity";
import { MissionNode } from "./mission";
import { NoteNode } from "./note";
import { ProjectNode } from "./project";
import { RuleNode } from "./rule";
import { ServiceNode } from "./service";
import { StepNode } from "./step";

export type NodeRendererComponent = ComponentType<NodeProps<BaseNodeData>>;

/** Full kind registry. Canvas wrappers (Phase 3.2+) construct React Flow
 *  ``nodeTypes`` maps from a SUBSET of these keys. */
export const NODE_RENDERERS: Record<NodeKind, NodeRendererComponent> = {
  project: ProjectNode,
  mission: MissionNode,
  core_value: CoreValueNode,
  identity: IdentityNode,
  actor: ActorNode,
  actor_ref: ActorRefNode,
  service: ServiceNode,
  feature: FeatureNode,
  category: CategoryNode,
  step: StepNode,
  decision: DecisionNode,
  note: NoteNode,
  rule: RuleNode,
  entity: EntityNode,
};
