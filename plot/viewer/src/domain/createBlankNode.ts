/**
 * Factory: build a blank wire-shape node for a given kind, using the
 * per-kind entity class so every default is the canonical one.
 *
 * Used by node-creation flows (drag-and-drop from the stencil, +child
 * actions in the Inspector, the "addNodeAt" canvas hook). Replaces
 * the v0.14 god-style inline initialiser that populated all 47 fields
 * for every kind.
 */
import { Actor } from "./Actor";
import { ActorRef } from "./ActorRef";
import type { BaseFields } from "./BaseFields";
import { Category } from "./Category";
import { Content } from "./Content";
import { CoreValue } from "./CoreValue";
import { Decision } from "./Decision";
import { Group } from "./Group";
import { Identity } from "./Identity";
import { IdentityRef } from "./IdentityRef";
import { Metric } from "./Metric";
import { Mission } from "./Mission";
import { MissionRef } from "./MissionRef";
import { Project } from "./Project";
import { Rule } from "./Rule";
import { Service } from "./Service";
import type { SketchNode } from "./SketchNode";
import { Step } from "./Step";
import { ValueRef } from "./ValueRef";

export type BlankNodeBase = Pick<
  BaseFields,
  | "id"
  | "label"
  | "x"
  | "y"
  | "width"
  | "height"
  | "color"
  | "shape"
  | "icon"
>;

/** Optional kind-specific overrides at creation time (e.g. drag-and-drop
 *  presets that pre-fill ``ref_actor_id`` for an actor_ref preset). */
export interface CreateNodeOverrides {
  ref_actor_id?: string | null;
  ref_mission_id?: string | null;
  ref_value_id?: string | null;
  ref_identity_id?: string | null;
}

/** Build a wire-shape node for the given kind. Every per-kind typed
 *  field is initialised to its canonical default (the entity class's
 *  ``fromJson`` populates them via ``parseBaseFields`` + the kind's
 *  own helpers).
 *
 *  Returns a plain JSON object (not a class instance) so React Flow's
 *  ``applyNodeChanges`` can spread it without losing prototype methods.
 */
export function createBlankNode(
  kind: SketchNode["kind"],
  base: BlankNodeBase,
  overrides: CreateNodeOverrides = {},
): SketchNode {
  // Build the kind-discriminated raw, then run it through the matching
  // entity class's fromJson + toJson so all defaults land canonically.
  const raw = { ...base, kind, ...overrides };
  switch (kind) {
    case "project":
      return Project.fromJson(raw).toJson();
    case "mission":
      return Mission.fromJson(raw).toJson();
    case "core_value":
      return CoreValue.fromJson(raw).toJson();
    case "identity":
      return Identity.fromJson(raw).toJson();
    case "actor":
      return Actor.fromJson(raw).toJson();
    case "actor_ref":
      return ActorRef.fromJson(raw).toJson();
    case "service":
      return Service.fromJson(raw).toJson();
    case "category":
      return Category.fromJson(raw).toJson();
    case "mission_ref":
      return MissionRef.fromJson(raw).toJson();
    case "value_ref":
      return ValueRef.fromJson(raw).toJson();
    case "identity_ref":
      return IdentityRef.fromJson(raw).toJson();
    case "metric":
      return Metric.fromJson(raw).toJson();
    case "step":
      return Step.fromJson(raw).toJson();
    case "decision":
      return Decision.fromJson(raw).toJson();
    case "group":
      return Group.fromJson(raw).toJson();
    case "rule":
      return Rule.fromJson(raw).toJson();
    case "content":
      return Content.fromJson(raw).toJson();
  }
}
