/**
 * v0.43.2 (D-2026-06-06-B) — ``identity`` Foundation entity =
 * ``description`` + ``body``. The ``do`` / ``dont`` fields were removed
 * (shared do/dont cut across the foundation triad). Legacy values fold
 * into ``body`` on read (data-loss guard). The output-value model
 * (provenance / evolution / status) is a separate future change.
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface IdentityJson extends BaseFieldsJson {
  kind: "identity";
  description: string;
  body: string;
}

const FOLD_LABELS: Record<string, string> = { do: "Do", dont: "Don't" };

/** Fold any non-empty pre-v0.43 ``do`` / ``dont`` into ``body`` as
 *  ``## {label}`` paragraphs, so migration loses no content. */
function foldLegacyDoDont(obj: Record<string, unknown>, body: string): string {
  const blocks: string[] = [];
  for (const [key, label] of Object.entries(FOLD_LABELS)) {
    const val = obj[key];
    if (typeof val === "string" && val.trim()) blocks.push(`## ${label}\n${val.trim()}`);
  }
  if (blocks.length === 0) return body;
  const folded = blocks.join("\n\n");
  const trimmed = body.replace(/\s+$/, "");
  return trimmed ? `${trimmed}\n\n${folded}` : folded;
}

export class Identity implements BaseFields {
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

  readonly kind: "identity" = "identity";

  readonly description: string;
  readonly body: string;

  private constructor(base: BaseFields, description: string, body: string) {
    Object.assign(this, base);
    this.description = description;
    this.body = body;
  }

  static fromJson(raw: unknown): Identity {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "identity") {
      throw new DomainParseError(
        `Identity.fromJson expected kind="identity", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    const body = readOptionalString(obj.body, "body", raw);
    return new Identity(
      base,
      readOptionalString(obj.description, "description", raw),
      foldLegacyDoDont(obj, body),
    );
  }

  toJson(): IdentityJson {
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
      kind: "identity",
      description: this.description,
      body: this.body,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Identity.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

registerKindParser("identity", (raw) => Identity.fromJson(raw) as never);
