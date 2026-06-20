/**
 * ``feature`` entity (D-2026-06-17-D / D-2026-06-19-H). A capability the
 * service offers (글쓰기 / 편집) — a **behaviour grouping under a service**,
 * NOT an independent value unit (value exchange is a property of the
 * *service*). The **sole drill target**: clicking a feature opens its Feature
 * canvas (a UX flowchart). ``proposed`` = the one-line "무엇을 할 수 있나?"
 * capability summary.
 */
import type { BaseFields } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";
import type { FeatureJson } from "./wire.gen";

export class Feature implements BaseFields {
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

  readonly kind: "feature" = "feature";

  readonly proposed: string;

  private constructor(base: BaseFields, proposed: string) {
    Object.assign(this, base);
    this.proposed = proposed;
  }

  static fromJson(raw: unknown): Feature {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "feature") {
      throw new DomainParseError(
        `Feature.fromJson expected kind="feature", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    return new Feature(base, readOptionalString(obj.proposed, "proposed", raw));
  }

  toJson(): FeatureJson {
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
      kind: "feature",
      proposed: this.proposed,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Feature.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

registerKindParser("feature", (raw) => Feature.fromJson(raw) as never);
