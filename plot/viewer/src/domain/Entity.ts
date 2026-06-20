/**
 * ``entity`` entity (D-2026-06-17-I). A product data object the services act
 * on (글 / 댓글 / 사용자) — symmetric to ``actor`` (Actors = *who* acts,
 * Entities = *what* is acted on). Lives on the project-level **Entities**
 * canvas, an AI-maintained conceptual map (NOT a physical ERD).
 *
 * ``label`` (BaseFields) is the entity name. ``summary`` = the one-line
 * "무엇을 담나?" — what the entity holds, in a sentence. NO ERD fields (FK /
 * cardinality / field types are below Plot's altitude); relationships between
 * entities are edges, not fields here.
 */
import type { BaseFields } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";
import type { EntityJson } from "./wire.gen";

export class Entity implements BaseFields {
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

  readonly kind: "entity" = "entity";

  readonly summary: string;

  private constructor(base: BaseFields, summary: string) {
    Object.assign(this, base);
    this.summary = summary;
  }

  static fromJson(raw: unknown): Entity {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "entity") {
      throw new DomainParseError(
        `Entity.fromJson expected kind="entity", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    return new Entity(base, readOptionalString(obj.summary, "summary", raw));
  }

  toJson(): EntityJson {
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
      kind: "entity",
      summary: this.summary,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Entity.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

registerKindParser("entity", (raw) => Entity.fromJson(raw) as never);
