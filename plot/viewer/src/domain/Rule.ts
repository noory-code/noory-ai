/**
 * v0.15 Phase 2.9 — ``rule`` composition entity. Lives inside a
 * service_detail canvas as a child of a service. Carries policy +
 * enforcement + an actor-id → permission-string map (e.g. RUD/CRUD).
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface RuleJson extends BaseFieldsJson {
  kind: "rule";
  policy?: string;
  enforcement?: string;
  actor_permissions?: Record<string, string>;
}

export class Rule implements BaseFields {
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

  readonly kind: "rule" = "rule";

  readonly policy: string;
  readonly enforcement: string;
  readonly actor_permissions: Record<string, string>;

  private constructor(
    base: BaseFields,
    policy: string,
    enforcement: string,
    actor_permissions: Record<string, string>,
  ) {
    Object.assign(this, base);
    this.policy = policy;
    this.enforcement = enforcement;
    this.actor_permissions = actor_permissions;
  }

  static fromJson(raw: unknown): Rule {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "rule") {
      throw new DomainParseError(
        `Rule.fromJson expected kind="rule", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    return new Rule(
      base,
      readOptionalString(obj.policy, "policy", raw),
      readOptionalString(obj.enforcement, "enforcement", raw),
      readPermissions(obj.actor_permissions, raw),
    );
  }

  toJson(): RuleJson {
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
      kind: "rule",
      policy: this.policy,
      enforcement: this.enforcement,
      actor_permissions: this.actor_permissions,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Rule.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

function readPermissions(value: unknown, raw: unknown): Record<string, string> {
  if (value === undefined || value === null) return {};
  if (typeof value !== "object" || Array.isArray(value)) {
    throw new DomainParseError(
      `Rule.actor_permissions must be an object, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(value)) {
    if (typeof v !== "string") {
      throw new DomainParseError(
        `Rule.actor_permissions[${JSON.stringify(k)}] must be a string, got ${JSON.stringify(v)}`,
        raw,
      );
    }
    out[k] = v;
  }
  return out;
}

registerKindParser("rule", (raw) => Rule.fromJson(raw) as never);
