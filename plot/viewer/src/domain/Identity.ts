/**
 * v0.44.0 (D-2026-06-07-A) — ``identity`` Foundation entity =
 * ``description`` + ``body`` plus the **output-model** structural fields
 * ``status`` + ``provenance``. identity is an output kind (AI-derived from
 * mission + core_value), so it tracks its derivation lineage + a
 * derive→confirm lifecycle the input kinds lack:
 *
 *   - ``status``     — ``manual`` (hand-authored; graceful-degradation
 *                      default) / ``derived`` (AI draft) / ``confirmed``.
 *   - ``provenance`` — ids of the source nodes this identity was derived from.
 *
 * ``evolution`` (revision history) is deferred — overlaps git + ``version``,
 * no writer yet. v0.43.2 (D-2026-06-06-B) removed the legacy ``do`` / ``dont``
 * (folded into ``body`` on read, data-loss guard).
 */
import type { BaseFields } from "./BaseFields";
import type { IdentityJson } from "./wire.gen";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export type IdentityStatus = "manual" | "derived" | "confirmed";

const IDENTITY_STATUSES: readonly IdentityStatus[] = ["manual", "derived", "confirmed"];

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
  readonly status: IdentityStatus;
  readonly provenance: string[];

  private constructor(
    base: BaseFields,
    description: string,
    body: string,
    status: IdentityStatus,
    provenance: string[],
  ) {
    Object.assign(this, base);
    this.description = description;
    this.body = body;
    this.status = status;
    this.provenance = provenance;
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
      readStatus(obj.status, raw),
      readStringArray(obj.provenance, "provenance", raw),
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
      status: this.status,
      provenance: this.provenance,
    };
  }
}

/** ``status`` defaults to ``manual`` (graceful degradation — hand-authored
 *  nodes carry no status); any other non-enum value is a hard parse error. */
function readStatus(value: unknown, raw: unknown): IdentityStatus {
  if (value === undefined || value === null) return "manual";
  if (typeof value !== "string" || !IDENTITY_STATUSES.includes(value as IdentityStatus)) {
    throw new DomainParseError(
      `Identity.status must be one of ${JSON.stringify(IDENTITY_STATUSES)}, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value as IdentityStatus;
}

function readStringArray(value: unknown, field: string, raw: unknown): string[] {
  if (value === undefined || value === null) return [];
  if (!Array.isArray(value) || value.some((v) => typeof v !== "string")) {
    throw new DomainParseError(
      `Identity.${field} must be an array of strings, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value as string[];
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
