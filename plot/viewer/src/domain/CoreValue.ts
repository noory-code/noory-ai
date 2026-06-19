/**
 * v0.43.1 (D-2026-06-06-B) — ``core_value`` Foundation entity =
 * ``definition`` (the value as a decision-priority principle) + ``body``.
 * The ``do`` / ``dont`` fields were removed (``do`` was a restatement of
 * ``definition``; ``dont`` went unused). Legacy values fold into ``body``
 * on read (data-loss guard) — see ``foldLegacyDoDont``.
 */
import type { BaseFields } from "./BaseFields";
import type { CoreValueJson } from "./wire.gen";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

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

export class CoreValue implements BaseFields {
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

  readonly kind: "core_value" = "core_value";

  readonly definition: string;
  readonly body: string;

  private constructor(base: BaseFields, definition: string, body: string) {
    Object.assign(this, base);
    this.definition = definition;
    this.body = body;
  }

  static fromJson(raw: unknown): CoreValue {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "core_value") {
      throw new DomainParseError(
        `CoreValue.fromJson expected kind="core_value", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    const body = readOptionalString(obj.body, "body", raw);
    return new CoreValue(
      base,
      readOptionalString(obj.definition, "definition", raw),
      foldLegacyDoDont(obj, body),
    );
  }

  toJson(): CoreValueJson {
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
      kind: "core_value",
      definition: this.definition,
      body: this.body,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `CoreValue.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

registerKindParser("core_value", (raw) => CoreValue.fromJson(raw) as never);
