/**
 * Plot v0.15 domain layer — per-kind entity classes + discriminated-union
 * dispatch (mirrors ``plot_mcp/models.py``).
 *
 * Phase 2.0: scaffolding only. Phase 2.1+ adds one entity class per
 * commit (Mission, CoreValue, Identity, Actor, Service, …); each class
 * registers itself via ``registerKindParser`` on module load.
 */
export { DomainParseError } from "./DomainParseError";
export type { BaseFields } from "./BaseFields";
export { parseBaseFields } from "./BaseFields";
export { parseEntity, registerKindParser, registeredKinds } from "./parseEntity";

// Wire-shape interfaces are GENERATED — single SSOT in ``wire.gen.ts``
// (Pydantic models, Phase A / D-2026-06-20-A). Re-exported here so the
// existing ``from "../domain"`` barrel import sites keep resolving.
export type {
  ActorJson,
  ActorRefJson,
  BaseFieldsJson,
  CategoryJson,
  ContentJson,
  CoreValueJson,
  DecisionJson,
  FeatureJson,
  IdentityJson,
  IdentityRefJson,
  MetricJson,
  MissionJson,
  MissionRefJson,
  NoteJson,
  ProjectJson,
  RuleJson,
  ServiceJson,
  StepJson,
  ValueRefJson,
} from "./wire.gen";

// Per-kind entity classes (Phase 2.1+). Importing this barrel registers
// every kind's parser with parseEntity via module-load side effects.
// Hand-written type aliases (not wire shapes) stay with their class.
export { Metric } from "./Metric";
export { Step } from "./Step";
export { Decision } from "./Decision";
export { Note } from "./Note";
export { CoreValue } from "./CoreValue";
export { Identity } from "./Identity";
export type { IdentityStatus } from "./Identity";
export { Mission } from "./Mission";
export { Project } from "./Project";
export { Category } from "./Category";
export { ActorRef } from "./ActorRef";
export { MissionRef } from "./MissionRef";
export { ValueRef } from "./ValueRef";
export { IdentityRef } from "./IdentityRef";
export { Actor } from "./Actor";
export { Service } from "./Service";
export { Feature } from "./Feature";
export { Rule } from "./Rule";
export { Content } from "./Content";

// v0.15 Phase 2.10 — discriminated-union SketchNode (replaces the
// god ``SketchNode`` interface that lived in ``viewer/src/types.ts``).
export type { SketchEntity, SketchNode } from "./SketchNode";

// v0.15 Phase 2.10 — node-creation factory (replaces the v0.14
// god-style inline default initialiser in useNodeCreation.ts).
export type { BlankNodeBase, CreateNodeOverrides } from "./createBlankNode";
export { createBlankNode } from "./createBlankNode";
