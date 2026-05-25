/**
 * v0.17 Phase 1 (D-2026-05-16-A) — ``mission`` Foundation entity. JSON
 * is the sole SSOT: every typed-text field value (``what_we_do`` /
 * ``why`` / ``direction`` / ``body``) is an MD-formatted string,
 * carried inline in the wire shape. Per-node MD files are
 * publish-output only (Phase 3+).
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface MissionJson extends BaseFieldsJson {
  kind: "mission";
  what_we_do: string;
  why: string;
  direction: string;
  body: string;
}

export class Mission implements BaseFields {
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

  readonly kind: "mission" = "mission";

  readonly what_we_do: string;
  readonly why: string;
  readonly direction: string;
  readonly body: string;

  private constructor(
    base: BaseFields,
    what_we_do: string,
    why: string,
    direction: string,
    body: string,
  ) {
    Object.assign(this, base);
    this.what_we_do = what_we_do;
    this.why = why;
    this.direction = direction;
    this.body = body;
  }

  static fromJson(raw: unknown): Mission {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "mission") {
      throw new DomainParseError(
        `Mission.fromJson expected kind="mission", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    return new Mission(
      base,
      readOptionalString(obj.what_we_do, "what_we_do", raw),
      readOptionalString(obj.why, "why", raw),
      readOptionalString(obj.direction, "direction", raw),
      readOptionalString(obj.body, "body", raw),
    );
  }

  toJson(): MissionJson {
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
      kind: "mission",
      what_we_do: this.what_we_do,
      why: this.why,
      direction: this.direction,
      body: this.body,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Mission.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

registerKindParser("mission", (raw) => Mission.fromJson(raw) as never);
