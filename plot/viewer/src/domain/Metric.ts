/**
 * v0.15 Phase 2.1 — ``metric`` entity class.
 *
 * Mirrors ``plot_mcp/models.py::MetricNode``: BaseNodeFields + ``target``
 * + ``measurement``. Composition over inheritance — no base class; the
 * constructor folds the parsed BaseFields into ``this`` plus the
 * metric-specific fields.
 *
 * Self-registers its ``fromJson`` parser with ``parseEntity`` on module
 * load, so any code path that imports ``parseEntity`` (or its barrel
 * via ``../domain``) automatically picks up metric-kind dispatch.
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface MetricJson extends BaseFieldsJson {
  kind: "metric";
  target: string;
  measurement: string;
}

export class Metric implements BaseFields {
  // BaseFields slice — populated from ``parseBaseFields`` in fromJson.
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

  // Discriminator (always "metric" for instances of this class).
  readonly kind: "metric" = "metric";

  // Metric-specific typed fields.
  readonly target: string;
  readonly measurement: string;

  private constructor(base: BaseFields, target: string, measurement: string) {
    Object.assign(this, base);
    this.target = target;
    this.measurement = measurement;
  }

  /** Parse + validate a raw dict into a Metric instance. Throws
   *  ``DomainParseError`` on any invariant violation. */
  static fromJson(raw: unknown): Metric {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "metric") {
      throw new DomainParseError(
        `Metric.fromJson expected kind="metric", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    const target = readOptionalString(obj.target, "target", raw);
    const measurement = readOptionalString(obj.measurement, "measurement", raw);
    return new Metric(base, target, measurement);
  }

  /** Wire-shape representation. ``kind`` is always emitted so the
   *  server-side discriminated union can dispatch. */
  toJson(): MetricJson {
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
      kind: "metric",
      target: this.target,
      measurement: this.measurement,
    };
  }
}

function readOptionalString(
  value: unknown,
  field: string,
  raw: unknown,
): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Metric.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

// Self-register so ``parseEntity({kind: "metric", ...})`` dispatches here.
registerKindParser("metric", (raw) => Metric.fromJson(raw) as never);
