/**
 * v0.15 Phase 2.2 — ``step`` entity class.
 *
 * Mirrors ``plot_mcp/models.py::StepNode``: BaseNodeFields + ``order``
 * (int | null) + ``outcome``. ``order`` is null for unordered /
 * parallel branches.
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface StepJson extends BaseFieldsJson {
  kind: "step";
  order: number | null;
  outcome: string;
}

export class Step implements BaseFields {
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

  readonly kind: "step" = "step";

  readonly order: number | null;
  readonly outcome: string;

  private constructor(base: BaseFields, order: number | null, outcome: string) {
    Object.assign(this, base);
    this.order = order;
    this.outcome = outcome;
  }

  static fromJson(raw: unknown): Step {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "step") {
      throw new DomainParseError(
        `Step.fromJson expected kind="step", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    const order = readNullableInt(obj.order, "order", raw);
    const outcome = readOptionalString(obj.outcome, "outcome", raw);
    return new Step(base, order, outcome);
  }

  toJson(): StepJson {
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
      kind: "step",
      order: this.order,
      outcome: this.outcome,
    };
  }
}

function readNullableInt(value: unknown, field: string, raw: unknown): number | null {
  if (value === undefined || value === null) return null;
  if (typeof value !== "number" || !Number.isFinite(value) || !Number.isInteger(value)) {
    throw new DomainParseError(
      `Step.${field} must be an integer or null, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Step.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

registerKindParser("step", (raw) => Step.fromJson(raw) as never);
