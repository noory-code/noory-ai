/**
 * v0.17 Phase 1 (D-2026-05-16-A) — ``core_value`` Foundation entity.
 * JSON is the sole SSOT: every typed-text field value (``definition``
 * / ``do`` / ``dont`` / ``body``) is an MD-formatted string carried
 * inline. Per-node MD files are publish-output only (Phase 3+).
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
  body: string;
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
  readonly collapsed!: boolean;
  readonly is_root!: boolean;
  readonly details_path!: string | null;
  readonly owner!: string | null;
  readonly version!: string;

  readonly kind: "core_value" = "core_value";

  readonly definition: string;
  readonly do: string;
  readonly dont: string;
  readonly body: string;

  private constructor(
    base: BaseFields,
    definition: string,
    doField: string,
    dont: string,
    body: string,
  ) {
    Object.assign(this, base);
    this.definition = definition;
    this.do = doField;
    this.dont = dont;
    this.body = body;
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
      readOptionalString(obj.body, "body", raw),
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
      collapsed: this.collapsed,
      is_root: this.is_root,
      details_path: this.details_path,
      owner: this.owner,
      version: this.version,
      kind: "core_value",
      definition: this.definition,
      do: this.do,
      dont: this.dont,
      body: this.body,
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
