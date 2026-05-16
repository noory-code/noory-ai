/**
 * v0.15 Phase 2.8 — ``actor`` entity. A class of people in the value
 * economy. Carries motivation + pain (persona-design pair) + side
 * (operator vs user, partitioning the value exchange).
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface ActorJson extends BaseFieldsJson {
  kind: "actor";
  motivation: string;
  pain: string;
  side: "operator" | "user" | null;
  body: string;
}

export class Actor implements BaseFields {
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
  readonly owner!: string | null;
  readonly version!: string;

  readonly kind: "actor" = "actor";

  readonly motivation: string;
  readonly pain: string;
  readonly side: "operator" | "user" | null;
  readonly body: string;

  private constructor(
    base: BaseFields,
    motivation: string,
    pain: string,
    side: "operator" | "user" | null,
    body: string,
  ) {
    Object.assign(this, base);
    this.motivation = motivation;
    this.pain = pain;
    this.side = side;
    this.body = body;
  }

  static fromJson(raw: unknown): Actor {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "actor") {
      throw new DomainParseError(
        `Actor.fromJson expected kind="actor", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    return new Actor(
      base,
      readOptionalString(obj.motivation, "motivation", raw),
      readOptionalString(obj.pain, "pain", raw),
      readSide(obj.side, raw),
      readOptionalString(obj.body, "body", raw),
    );
  }

  toJson(): ActorJson {
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
      owner: this.owner,
      version: this.version,
      kind: "actor",
      motivation: this.motivation,
      pain: this.pain,
      side: this.side,
      body: this.body,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Actor.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

function readSide(value: unknown, raw: unknown): "operator" | "user" | null {
  if (value === undefined || value === null) return null;
  if (value === "operator" || value === "user") return value;
  throw new DomainParseError(
    `Actor.side must be "operator", "user", or null; got ${JSON.stringify(value)}`,
    raw,
  );
}

registerKindParser("actor", (raw) => Actor.fromJson(raw) as never);
