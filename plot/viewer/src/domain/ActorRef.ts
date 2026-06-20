/**
 * ``actor_ref`` entity — a **read-only anchor** (D-2026-06-19-I). On the
 * Feature canvas it marks the flow's subject ("who starts / who can"); it is
 * NOT a value-exchange editor. Its former per-(actor×service) fields —
 * ``gives`` / ``receives`` / ``motivation`` / ``pain`` — are retired (role-level
 * value lives on Actors edges, aggregate value on the service "뭐가 좋아지나?").
 * Carries only ``ref_actor_id`` + ``side`` (denormalized from the master for
 * canvas-local colour coding, not authored here).
 */
import type { BaseFields } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";
import type { ActorRefJson } from "./wire.gen";

export class ActorRef implements BaseFields {
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

  readonly kind: "actor_ref" = "actor_ref";

  readonly ref_actor_id: string | null;
  readonly side: "operator" | "user" | null;

  private constructor(
    base: BaseFields,
    ref_actor_id: string | null,
    side: "operator" | "user" | null,
  ) {
    Object.assign(this, base);
    this.ref_actor_id = ref_actor_id;
    this.side = side;
  }

  static fromJson(raw: unknown): ActorRef {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "actor_ref") {
      throw new DomainParseError(
        `ActorRef.fromJson expected kind="actor_ref", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    return new ActorRef(
      base,
      readNullableString(obj.ref_actor_id, "ref_actor_id", raw),
      readSide(obj.side, raw),
    );
  }

  toJson(): ActorRefJson {
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
      kind: "actor_ref",
      ref_actor_id: this.ref_actor_id,
      side: this.side,
    };
  }
}

function readNullableString(value: unknown, field: string, raw: unknown): string | null {
  if (value === undefined || value === null) return null;
  if (typeof value !== "string") {
    throw new DomainParseError(
      `ActorRef.${field} must be a string or null, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

function readSide(value: unknown, raw: unknown): "operator" | "user" | null {
  if (value === undefined || value === null) return null;
  if (value === "operator" || value === "user") return value;
  throw new DomainParseError(
    `ActorRef.side must be "operator", "user", or null; got ${JSON.stringify(value)}`,
    raw,
  );
}

registerKindParser("actor_ref", (raw) => ActorRef.fromJson(raw) as never);
