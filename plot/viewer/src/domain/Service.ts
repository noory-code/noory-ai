/**
 * v0.15 Phase 2.9 — ``service`` entity. The value-creating hub
 * (PHILOSOPHY P5). Carries target_side + 6 typed fields (what /
 * value_created / scope / trigger / how / outcome) + do/dont.
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface ServiceJson extends BaseFieldsJson {
  kind: "service";
  target_side: "operator" | "user" | "both" | null;
  what: string;
  value_created: string;
  scope: string;
  trigger: string;
  how: string;
  outcome: string;
  do: string;
  dont: string;
}

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
  readonly parent_id!: string | null;
  readonly collapsed!: boolean;
  readonly is_root!: boolean;
  readonly details_path!: string | null;

  readonly kind: "service" = "service";

  readonly target_side: "operator" | "user" | "both" | null;
  readonly what: string;
  readonly value_created: string;
  readonly scope: string;
  readonly trigger: string;
  readonly how: string;
  readonly outcome: string;
  readonly do: string;
  readonly dont: string;

  private constructor(
    base: BaseFields,
    target_side: "operator" | "user" | "both" | null,
    typed: {
      what: string;
      value_created: string;
      scope: string;
      trigger: string;
      how: string;
      outcome: string;
      doField: string;
      dont: string;
    },
  ) {
    Object.assign(this, base);
    this.target_side = target_side;
    this.what = typed.what;
    this.value_created = typed.value_created;
    this.scope = typed.scope;
    this.trigger = typed.trigger;
    this.how = typed.how;
    this.outcome = typed.outcome;
    this.do = typed.doField;
    this.dont = typed.dont;
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
    return new Service(base, readTargetSide(obj.target_side, raw), {
      what: readOptionalString(obj.what, "what", raw),
      value_created: readOptionalString(obj.value_created, "value_created", raw),
      scope: readOptionalString(obj.scope, "scope", raw),
      trigger: readOptionalString(obj.trigger, "trigger", raw),
      how: readOptionalString(obj.how, "how", raw),
      outcome: readOptionalString(obj.outcome, "outcome", raw),
      doField: readOptionalString(obj.do, "do", raw),
      dont: readOptionalString(obj.dont, "dont", raw),
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
      parent_id: this.parent_id,
      collapsed: this.collapsed,
      is_root: this.is_root,
      details_path: this.details_path,
      kind: "service",
      target_side: this.target_side,
      what: this.what,
      value_created: this.value_created,
      scope: this.scope,
      trigger: this.trigger,
      how: this.how,
      outcome: this.outcome,
      do: this.do,
      dont: this.dont,
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

function readTargetSide(value: unknown, raw: unknown): "operator" | "user" | "both" | null {
  if (value === undefined || value === null) return null;
  if (value === "operator" || value === "user" || value === "both") return value;
  throw new DomainParseError(
    `Service.target_side must be "operator" / "user" / "both" / null; got ${JSON.stringify(value)}`,
    raw,
  );
}

registerKindParser("service", (raw) => Service.fromJson(raw) as never);
