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
import type { Actor, ActorJson } from "./Actor";
import type { ActorRef, ActorRefJson } from "./ActorRef";
import type { Category, CategoryJson } from "./Category";
import type { Content, ContentJson } from "./Content";
import type { CoreValue, CoreValueJson } from "./CoreValue";
import type { Decision, DecisionJson } from "./Decision";
import type { Identity, IdentityJson } from "./Identity";
import type { IdentityRef, IdentityRefJson } from "./IdentityRef";
import type { Metric, MetricJson } from "./Metric";
import type { Mission, MissionJson } from "./Mission";
import type { MissionRef, MissionRefJson } from "./MissionRef";
import type { Project, ProjectJson } from "./Project";
import type { Rule, RuleJson } from "./Rule";
import type { Service, ServiceJson } from "./Service";
import type { Step, StepJson } from "./Step";
import type { ValueRef, ValueRefJson } from "./ValueRef";

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
  | Category
  | MissionRef
  | ValueRef
  | IdentityRef
  | Metric
  | Step
  | Decision
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
  | CategoryJson
  | MissionRefJson
  | ValueRefJson
  | IdentityRefJson
  | MetricJson
  | StepJson
  | DecisionJson
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
