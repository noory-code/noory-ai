/**
 * v0.15 Phase 2.10 — viewer-side ``SketchNode`` discriminated union.
 *
 * Mirrors the server-side ``plot_mcp/models.py::SketchNode`` 1:1.
 * Replaces the v0.14 god ``SketchNode`` interface that used to live
 * in ``viewer/src/types.ts``.
 *
 * Important: the union members are the **JSON shapes** (interfaces),
 * not the class instances. The classes (``Metric``, ``Service``, …)
 * own ``fromJson`` / ``toJson`` and are used at the wire boundary;
 * everywhere else in the viewer (React Flow node arrays, useState,
 * spread-merge) we work with plain JSON-shape objects so React Flow's
 * ``applyNodeChanges`` (which spreads via ``{...node, x: newX}``)
 * doesn't strip prototype methods and break structural typing.
 *
 * The intersection ``& { _md_warnings?: string[] }`` carries the
 * server-side MD-warning decoration that ``folder_io.py`` may attach
 * to a Foundation node on read. Optional on every kind (only
 * Foundation nodes ever carry warnings, but the wire shape is one
 * type). Pure response decoration — never serialised back.
 *
 * ``SketchEntity`` is the *class-instance* union, used by ``parseEntity``
 * return type and anywhere that holds fully-validated entities (rare
 * in the viewer; common in tests).
 */
// Class-instance imports (hand-written domain classes) stay per-file.
import type { Actor } from "./Actor";
import type { ActorRef } from "./ActorRef";
import type { Category } from "./Category";
import type { Content } from "./Content";
import type { CoreValue } from "./CoreValue";
import type { Decision } from "./Decision";
import type { Feature } from "./Feature";
import type { Identity } from "./Identity";
import type { IdentityRef } from "./IdentityRef";
import type { Metric } from "./Metric";
import type { Mission } from "./Mission";
import type { MissionRef } from "./MissionRef";
import type { Note } from "./Note";
import type { Project } from "./Project";
import type { Rule } from "./Rule";
import type { Service } from "./Service";
import type { Step } from "./Step";
import type { ValueRef } from "./ValueRef";
// Wire-shape interfaces are GENERATED — single SSOT in ``wire.gen.ts``.
import type {
  ActorJson,
  ActorRefJson,
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

/** Class-instance union — used by ``parseEntity`` and entity-class
 *  call sites (round-trip tests, fromJson validators). */
export type SketchEntity =
  | Project
  | Mission
  | CoreValue
  | Identity
  | Actor
  | ActorRef
  | Service
  | Feature
  | Category
  | MissionRef
  | ValueRef
  | IdentityRef
  | Metric
  | Step
  | Decision
  | Note
  | Rule
  | Content;

/** Wire-shape union (no class methods) — used by everything that
 *  treats nodes as plain data: React Flow state, Inspector props,
 *  api.ts response casts, undo/redo snapshots. Class instances
 *  satisfy this type structurally (extra methods allowed). */
export type SketchNode = (
  | ProjectJson
  | MissionJson
  | CoreValueJson
  | IdentityJson
  | ActorJson
  | ActorRefJson
  | ServiceJson
  | FeatureJson
  | CategoryJson
  | MissionRefJson
  | ValueRefJson
  | IdentityRefJson
  | MetricJson
  | StepJson
  | DecisionJson
  | NoteJson
  | RuleJson
  | ContentJson
) & {
  _md_warnings?: string[];
  /** v0.22.0 (D-2026-05-17-H) — server-decorated dirty signal.
   *  ``true`` when the node has content changes since the last publish
   *  (typed-text / label / body / incident edges) OR has never been
   *  published (no baseline yet). ``false`` when the node matches its
   *  baseline. Missing field ⇒ treat as ``true`` for back-compat. */
  _dirty?: boolean;
};
