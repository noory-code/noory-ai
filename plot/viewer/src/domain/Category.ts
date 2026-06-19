/**
 * v0.15 Phase 2.6 — ``category`` entity. v0.12 introduced as a
 * thematic grouping of services on the Services canvas; the only
 * typed field is ``theme`` — a one-line statement of the common
 * thread that ties this category's services together.
 */
import type { BaseFields } from "./BaseFields";
import type { CategoryJson } from "./wire.gen";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export class Category implements BaseFields {
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

  readonly kind: "category" = "category";

  readonly theme: string;
  readonly body: string;

  private constructor(base: BaseFields, theme: string, body: string) {
    Object.assign(this, base);
    this.theme = theme;
    this.body = body;
  }

  static fromJson(raw: unknown): Category {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "category") {
      throw new DomainParseError(
        `Category.fromJson expected kind="category", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    const readStr = (value: unknown, field: string): string => {
      if (value === undefined || value === null) return "";
      if (typeof value !== "string") {
        throw new DomainParseError(
          `Category.${field} must be a string, got ${JSON.stringify(value)}`,
          raw,
        );
      }
      return value;
    };
    return new Category(base, readStr(obj.theme, "theme"), readStr(obj.body, "body"));
  }

  toJson(): CategoryJson {
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
      kind: "category",
      theme: this.theme,
      body: this.body,
    };
  }
}

registerKindParser("category", (raw) => Category.fromJson(raw) as never);
