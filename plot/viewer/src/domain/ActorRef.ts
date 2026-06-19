/**
 * v0.15 Phase 2.7 — ``actor_ref`` entity. References an actor master on
 * the Actors canvas. Carries the actor's **per-service stake**: gives +
 * receives (value flow) and — D-2026-06-15-J — motivation + pain (why
 * this actor participates in THIS service / what hurts here; PHILOSOPHY
 * P3, participation is asymmetric). side mirrors the referenced actor's
 * identity side for canvas-local colour coding (not authored here).
 */
import type { BaseFields } from "./BaseFields";
import type { ActorRefJson } from "./wire.gen";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

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
  readonly gives: string;
  readonly receives: string;
  readonly motivation: string;
  readonly pain: string;
  readonly side: "operator" | "user" | null;

  private constructor(
    base: BaseFields,
    ref_actor_id: string | null,
    gives: string,
    receives: string,
    motivation: string,
    pain: string,
    side: "operator" | "user" | null,
  ) {
    Object.assign(this, base);
    this.ref_actor_id = ref_actor_id;
    this.gives = gives;
    this.receives = receives;
    this.motivation = motivation;
    this.pain = pain;
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
      readOptionalString(obj.gives, "gives", raw),
      readOptionalString(obj.receives, "receives", raw),
      readOptionalString(obj.motivation, "motivation", raw),
      readOptionalString(obj.pain, "pain", raw),
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
      gives: this.gives,
      receives: this.receives,
      motivation: this.motivation,
      pain: this.pain,
      side: this.side,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `ActorRef.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
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
