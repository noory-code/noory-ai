/**
 * v0.15 Phase 2.3 — ``core_value`` entity class. Foundation kind whose
 * typed text (``definition`` / ``do`` / ``dont``) lives in the per-node
 * MD template; the wire-shape representation here mirrors what
 * folder_io.py merges back into the in-memory CanvasDoc.
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface CoreValueJson extends BaseFieldsJson {
  kind: "core_value";
  definition: string;
  do: string;
  dont: string;
}

export class CoreValue implements BaseFields {
  readonly id!: string;
  readonly label!: string;
  readonly x!: number;
  readonly y!: number;
  readonly width!: number;
  readonly height!: number;
  readonly color!: string;
  readonly shape!: BaseFields["shape"];
  readonly icon!: string | null;
  readonly parent_id!: string | null;
  readonly collapsed!: boolean;
  readonly is_root!: boolean;
  readonly details_path!: string | null;

  readonly kind: "core_value" = "core_value";

  readonly definition: string;
  readonly do: string;
  readonly dont: string;

  private constructor(base: BaseFields, definition: string, doField: string, dont: string) {
    Object.assign(this, base);
    this.definition = definition;
    this.do = doField;
    this.dont = dont;
  }

  static fromJson(raw: unknown): CoreValue {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "core_value") {
      throw new DomainParseError(
        `CoreValue.fromJson expected kind="core_value", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    return new CoreValue(
      base,
      readOptionalString(obj.definition, "definition", raw),
      readOptionalString(obj.do, "do", raw),
      readOptionalString(obj.dont, "dont", raw),
    );
  }

  toJson(): CoreValueJson {
    return {
      id: this.id,
      label: this.label,
      x: this.x,
      y: this.y,
      width: this.width,
      height: this.height,
      color: this.color,
      shape: this.shape,
      icon: this.icon,
      parent_id: this.parent_id,
      collapsed: this.collapsed,
      is_root: this.is_root,
      details_path: this.details_path,
      kind: "core_value",
      definition: this.definition,
      do: this.do,
      dont: this.dont,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `CoreValue.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

registerKindParser("core_value", (raw) => CoreValue.fromJson(raw) as never);
