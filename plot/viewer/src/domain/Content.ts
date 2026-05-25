/**
 * v0.15 Phase 2.9 — ``content`` composition entity. Lives inside a
 * service_detail canvas as a child of a service. Carries a format
 * hint + producer/consumer actor master ids.
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface ContentJson extends BaseFieldsJson {
  kind: "content";
  format: string;
  producer_actor_id: string | null;
  consumer_actor_id: string | null;
  body: string;
}

export class Content implements BaseFields {
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

  readonly kind: "content" = "content";

  readonly format: string;
  readonly producer_actor_id: string | null;
  readonly consumer_actor_id: string | null;
  readonly body: string;

  private constructor(
    base: BaseFields,
    format: string,
    producer_actor_id: string | null,
    consumer_actor_id: string | null,
    body: string,
  ) {
    Object.assign(this, base);
    this.format = format;
    this.producer_actor_id = producer_actor_id;
    this.consumer_actor_id = consumer_actor_id;
    this.body = body;
  }

  static fromJson(raw: unknown): Content {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "content") {
      throw new DomainParseError(
        `Content.fromJson expected kind="content", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    return new Content(
      base,
      readOptionalString(obj.format, "format", raw),
      readNullableString(obj.producer_actor_id, "producer_actor_id", raw),
      readNullableString(obj.consumer_actor_id, "consumer_actor_id", raw),
      readOptionalString(obj.body, "body", raw),
    );
  }

  toJson(): ContentJson {
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
      kind: "content",
      format: this.format,
      producer_actor_id: this.producer_actor_id,
      consumer_actor_id: this.consumer_actor_id,
      body: this.body,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Content.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

function readNullableString(value: unknown, field: string, raw: unknown): string | null {
  if (value === undefined || value === null) return null;
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Content.${field} must be a string or null, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

registerKindParser("content", (raw) => Content.fromJson(raw) as never);
