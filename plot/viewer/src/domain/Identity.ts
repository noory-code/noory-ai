/**
 * v0.15 Phase 2.3 — ``identity`` entity class. Foundation kind. Carries
 * ``description`` + the shared ``do`` / ``dont`` pair; the typed text
 * lives in the per-node MD template, merged into the in-memory wire
 * shape by ``folder_io.py``.
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface IdentityJson extends BaseFieldsJson {
  kind: "identity";
  description: string;
  do: string;
  dont: string;
}

export class Identity implements BaseFields {
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

  readonly kind: "identity" = "identity";

  readonly description: string;
  readonly do: string;
  readonly dont: string;

  private constructor(base: BaseFields, description: string, doField: string, dont: string) {
    Object.assign(this, base);
    this.description = description;
    this.do = doField;
    this.dont = dont;
  }

  static fromJson(raw: unknown): Identity {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "identity") {
      throw new DomainParseError(
        `Identity.fromJson expected kind="identity", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    return new Identity(
      base,
      readOptionalString(obj.description, "description", raw),
      readOptionalString(obj.do, "do", raw),
      readOptionalString(obj.dont, "dont", raw),
    );
  }

  toJson(): IdentityJson {
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
      kind: "identity",
      description: this.description,
      do: this.do,
      dont: this.dont,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Identity.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

registerKindParser("identity", (raw) => Identity.fromJson(raw) as never);
