/**
 * Graph-layer fields shared by every entity class. Mirrors
 * ``plot_mcp/models.py::BaseNodeFields`` 1:1.
 *
 * Each per-kind entity class composes these (via Object.assign in its
 * constructor) plus its own typed fields. There is no base class —
 * inheritance would re-introduce the god-object pattern by forcing
 * every subclass to call ``super.fromJson``.
 */
import type { Shape } from "../types";
import { DomainParseError } from "./DomainParseError";

/** Wire shape (what the server sends) — GENERATED. The canonical
 *  ``BaseFieldsJson`` now lives in ``wire.gen.ts`` (Pydantic SSOT, Phase A
 *  / D-2026-06-20-A); re-exported here so existing ``./BaseFields`` import
 *  sites keep resolving. The in-memory ``BaseFields`` (below) stays
 *  hand-written — it is the defaults-filled runtime shape, not the wire. */
export type { BaseFieldsJson } from "./wire.gen";

/** In-memory shape (defaults filled in). Every field present and typed.
 *  v0.26.0 (D-2026-05-25-A) — ``parent_id`` removed. */
export interface BaseFields {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  shape: Shape;
  icon: string | null;
  collapsed: boolean;
  is_root: boolean;
  details_path: string | null;
  /** v0.16.12 — owner identifier for multi-user prep. ``null`` when
   *  authored by an anonymous / single-user session. Server fills
   *  from session context once multi-user lands. */
  owner: string | null;
  /** v0.17.2 Phase 2 (D-2026-05-16-C) — see BaseFieldsJson. */
  version: string;
}

const VALID_SHAPES: ReadonlySet<Shape> = new Set<Shape>([
  "rectangle",
  "rounded",
  "circle",
  "ellipse",
  "diamond",
  "hexagon",
  "octagon",
]);

function asNumber(value: unknown, fallback: number, field: string, raw: unknown): number {
  if (value === undefined) return fallback;
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new DomainParseError(
      `entity.${field} must be a finite number, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

function asString(value: unknown, fallback: string, field: string, raw: unknown): string {
  if (value === undefined) return fallback;
  if (typeof value !== "string") {
    throw new DomainParseError(
      `entity.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

function asNullableString(
  value: unknown,
  field: string,
  raw: unknown,
): string | null {
  if (value === undefined || value === null) return null;
  if (typeof value !== "string") {
    throw new DomainParseError(
      `entity.${field} must be a string or null, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

function asBoolean(value: unknown, fallback: boolean, field: string, raw: unknown): boolean {
  if (value === undefined) return fallback;
  if (typeof value !== "boolean") {
    throw new DomainParseError(
      `entity.${field} must be a boolean, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

function asShape(value: unknown, raw: unknown): Shape {
  if (value === undefined) return "rounded";
  if (typeof value !== "string" || !VALID_SHAPES.has(value as Shape)) {
    throw new DomainParseError(
      `entity.shape must be one of ${[...VALID_SHAPES].join(", ")}, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value as Shape;
}

/** v0.17.2 Phase 2 (D-2026-05-16-C) — version regex contract mirroring
 *  ``plot_mcp/models.py::BaseNodeFields._version_is_valid``. Defaults
 *  to ``"v1.0"`` when omitted (pre-Phase-2 canvas back-compat). */
const VERSION_RE = /^v\d+\.\d+$/;

function asVersionString(value: unknown, raw: unknown): string {
  if (value === undefined) return "v1.0";
  if (typeof value !== "string" || !VERSION_RE.test(value)) {
    throw new DomainParseError(
      `entity.version must match ^v\\d+\\.\\d+$ (e.g. "v1.0"), got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

/** Parse + validate the BaseFields slice of any entity raw dict.
 *  Throws ``DomainParseError`` on any invariant violation; the entity
 *  constructor that calls this can rely on the result.
 */
export function parseBaseFields(raw: unknown): BaseFields {
  if (typeof raw !== "object" || raw === null) {
    throw new DomainParseError("entity raw must be a non-null object", raw);
  }
  const obj = raw as Record<string, unknown>;
  const id = obj.id;
  if (typeof id !== "string" || id.length === 0) {
    throw new DomainParseError("entity.id must be a non-empty string", raw);
  }
  return {
    id,
    label: asString(obj.label, "", "label", raw),
    x: asNumber(obj.x, 0, "x", raw),
    y: asNumber(obj.y, 0, "y", raw),
    width: asNumber(obj.width, 80, "width", raw),
    height: asNumber(obj.height, 36, "height", raw),
    color: asString(obj.color, "#ffffff", "color", raw),
    shape: asShape(obj.shape, raw),
    icon: asNullableString(obj.icon, "icon", raw),
    // v0.26.0 (D-2026-05-25-A) — parent_id removed; hierarchy is now
    // expressed via directed edges on the canvas, not per-node fields.
    collapsed: asBoolean(obj.collapsed, false, "collapsed", raw),
    is_root: asBoolean(obj.is_root, false, "is_root", raw),
    details_path: asNullableString(obj.details_path, "details_path", raw),
    owner: asNullableString(obj.owner, "owner", raw),
    version: asVersionString(obj.version, raw),
  };
}
