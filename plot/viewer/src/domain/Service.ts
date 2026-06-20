/**
 * ``service`` entity — the value-creating hub (PHILOSOPHY P5).
 *
 * D-2026-06-17-B / D-2026-06-20-F — 5 question-titled inspector fields:
 * 2 typed-text (``problem`` = 왜 필요한가?, ``value_created`` = 뭐가 좋아지나?)
 * + 3 multi-select reference lists rendered as chips (``ref_actor_ids`` /
 * ``ref_value_ids`` / ``ref_identity_ids`` — ids of master nodes, Option B).
 * The old 9 free-text fields (target_side / what / scope / trigger / how /
 * outcome / do / dont / body) were deleted (discard, no production data yet).
 */
import type { BaseFields } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";
import type { ServiceJson } from "./wire.gen";

export class Service implements BaseFields {
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

  readonly kind: "service" = "service";

  readonly problem: string;
  readonly value_created: string;
  readonly ref_actor_ids: string[];
  readonly ref_value_ids: string[];
  readonly ref_identity_ids: string[];

  private constructor(
    base: BaseFields,
    typed: {
      problem: string;
      value_created: string;
      ref_actor_ids: string[];
      ref_value_ids: string[];
      ref_identity_ids: string[];
    },
  ) {
    Object.assign(this, base);
    this.problem = typed.problem;
    this.value_created = typed.value_created;
    this.ref_actor_ids = typed.ref_actor_ids;
    this.ref_value_ids = typed.ref_value_ids;
    this.ref_identity_ids = typed.ref_identity_ids;
  }

  static fromJson(raw: unknown): Service {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "service") {
      throw new DomainParseError(
        `Service.fromJson expected kind="service", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    return new Service(base, {
      problem: readOptionalString(obj.problem, "problem", raw),
      value_created: readOptionalString(obj.value_created, "value_created", raw),
      ref_actor_ids: readStringArray(obj.ref_actor_ids, "ref_actor_ids", raw),
      ref_value_ids: readStringArray(obj.ref_value_ids, "ref_value_ids", raw),
      ref_identity_ids: readStringArray(obj.ref_identity_ids, "ref_identity_ids", raw),
    });
  }

  toJson(): ServiceJson {
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
      kind: "service",
      problem: this.problem,
      value_created: this.value_created,
      ref_actor_ids: this.ref_actor_ids,
      ref_value_ids: this.ref_value_ids,
      ref_identity_ids: this.ref_identity_ids,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Service.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

function readStringArray(value: unknown, field: string, raw: unknown): string[] {
  if (value === undefined || value === null) return [];
  if (!Array.isArray(value) || value.some((v) => typeof v !== "string")) {
    throw new DomainParseError(
      `Service.${field} must be an array of strings, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value as string[];
}

registerKindParser("service", (raw) => Service.fromJson(raw) as never);
