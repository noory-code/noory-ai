/**
 * Plot v0.15 domain layer — per-kind entity classes + discriminated-union
 * dispatch (mirrors ``plot_mcp/models.py``).
 *
 * Phase 2.0: scaffolding only. Phase 2.1+ adds one entity class per
 * commit (Mission, CoreValue, Identity, Actor, Service, …); each class
 * registers itself via ``registerKindParser`` on module load.
 */
export { DomainParseError } from "./DomainParseError";
export type { BaseFields, BaseFieldsJson } from "./BaseFields";
export { parseBaseFields } from "./BaseFields";
export { parseEntity, registerKindParser, registeredKinds } from "./parseEntity";

// Per-kind entity classes (Phase 2.1+). Importing this barrel registers
// every kind's parser with parseEntity via module-load side effects.
export { Metric } from "./Metric";
export type { MetricJson } from "./Metric";
export { Step } from "./Step";
export type { StepJson } from "./Step";
export { CoreValue } from "./CoreValue";
export type { CoreValueJson } from "./CoreValue";
export { Identity } from "./Identity";
export type { IdentityJson } from "./Identity";
export { Mission } from "./Mission";
export type { MissionJson } from "./Mission";
export { Project } from "./Project";
export type { ProjectJson } from "./Project";
export { Category } from "./Category";
export type { CategoryJson } from "./Category";
export { ActorRef } from "./ActorRef";
export type { ActorRefJson } from "./ActorRef";
export { MissionRef } from "./MissionRef";
export type { MissionRefJson } from "./MissionRef";
export { ValueRef } from "./ValueRef";
export type { ValueRefJson } from "./ValueRef";
export { IdentityRef } from "./IdentityRef";
export type { IdentityRefJson } from "./IdentityRef";
export { Actor } from "./Actor";
export type { ActorJson } from "./Actor";
export { Service } from "./Service";
export type { ServiceJson } from "./Service";
export { Rule } from "./Rule";
export type { RuleJson } from "./Rule";
export { Content } from "./Content";
export type { ContentJson } from "./Content";

// v0.15 Phase 2.10 — discriminated-union SketchNode (replaces the
// god ``SketchNode`` interface that lived in ``viewer/src/types.ts``).
export type { SketchEntity, SketchNode } from "./SketchNode";

// v0.15 Phase 2.10 — node-creation factory (replaces the v0.14
// god-style inline default initialiser in useNodeCreation.ts).
export type { BlankNodeBase, CreateNodeOverrides } from "./createBlankNode";
export { createBlankNode } from "./createBlankNode";
