/**
 * v0.43.0 (D-2026-06-06-C) — ``mission`` Foundation entity = ``label``
 * (the declaration) + ``body`` (free Markdown). The former typed fields
 * ``what_we_do`` / ``why`` / ``direction`` were removed: a mission is one
 * indivisible declaration, not a bag of sliced angles. Legacy values fold
 * into ``body`` on read (data-loss guard) — see ``foldLegacyTypedFields``.
 */
import type { BaseFields } from "./BaseFields";
import type { MissionJson } from "./wire.gen";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

const FOLD_LABELS: Record<string, string> = { why: "Why", direction: "Direction" };

/** Migrate pre-v0.43 mission data: ``what_we_do`` → ``statement``;
 *  fold non-empty ``why`` / ``direction`` into ``body`` as ``## {label}``
 *  paragraphs. Loses no content. Returns the migrated {statement, body}. */
function migrateLegacy(
  obj: Record<string, unknown>,
  statement: string,
  body: string,
): { statement: string; body: string } {
  let nextStatement = statement;
  if (!nextStatement.trim() && typeof obj.what_we_do === "string" && obj.what_we_do.trim()) {
    nextStatement = obj.what_we_do.trim();
  }
  const blocks: string[] = [];
  for (const [key, label] of Object.entries(FOLD_LABELS)) {
    const val = obj[key];
    if (typeof val === "string" && val.trim()) blocks.push(`## ${label}\n${val.trim()}`);
  }
  let nextBody = body;
  if (blocks.length > 0) {
    const folded = blocks.join("\n\n");
    const trimmed = body.replace(/\s+$/, "");
    nextBody = trimmed ? `${trimmed}\n\n${folded}` : folded;
  }
  return { statement: nextStatement, body: nextBody };
}

export class Mission implements BaseFields {
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

  readonly kind: "mission" = "mission";

  readonly statement: string;
  readonly body: string;

  private constructor(base: BaseFields, statement: string, body: string) {
    Object.assign(this, base);
    this.statement = statement;
    this.body = body;
  }

  static fromJson(raw: unknown): Mission {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "mission") {
      throw new DomainParseError(
        `Mission.fromJson expected kind="mission", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    const migrated = migrateLegacy(
      obj,
      readOptionalString(obj.statement, "statement", raw),
      readOptionalString(obj.body, "body", raw),
    );
    return new Mission(base, migrated.statement, migrated.body);
  }

  toJson(): MissionJson {
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
      kind: "mission",
      statement: this.statement,
      body: this.body,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Mission.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

registerKindParser("mission", (raw) => Mission.fromJson(raw) as never);
