/**
 * Discriminator dispatch for the ``SketchNode`` discriminated union.
 *
 * Mirrors the server-side Pydantic dispatch on ``kind``. Each per-kind
 * entity class registers its ``fromJson`` parser via ``registerKindParser``
 * during module load; this central function picks the right parser at
 * runtime.
 *
 * Phase 2.0: registry starts empty. Phase 2.1+ populates one entry per
 * kind as the corresponding entity class lands.
 */
import type { SketchNode } from "../types";
import { DomainParseError } from "./DomainParseError";

type EntityFromJson = (raw: unknown) => SketchNode;

const REGISTRY: Map<string, EntityFromJson> = new Map();

/** Register a per-kind parser. Called from each entity-class module
 *  during import so the dispatch table assembles itself. */
export function registerKindParser(kind: string, parser: EntityFromJson): void {
  REGISTRY.set(kind, parser);
}

/** Dispatch on ``raw.kind`` to the matching entity class's ``fromJson``.
 *  Throws ``DomainParseError`` for missing / unknown kinds.
 */
export function parseEntity(raw: unknown): SketchNode {
  if (typeof raw !== "object" || raw === null) {
    throw new DomainParseError("entity raw must be a non-null object", raw);
  }
  const obj = raw as Record<string, unknown>;
  const kind = obj.kind;
  if (typeof kind !== "string" || kind.length === 0) {
    throw new DomainParseError(
      "entity raw requires a non-empty 'kind' discriminator string",
      raw,
    );
  }
  const parser = REGISTRY.get(kind);
  if (!parser) {
    throw new DomainParseError(`unknown entity kind: ${JSON.stringify(kind)}`, raw);
  }
  return parser(raw);
}

/** Test-only helper: which kinds currently have a registered parser. */
export function registeredKinds(): readonly string[] {
  return Array.from(REGISTRY.keys()).sort();
}
