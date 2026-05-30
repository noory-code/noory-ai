/**
 * v0.29.0 (D-2026-05-30-I) — ``group`` entity class.
 *
 * A container that chunks a busy ServiceDetail flow (e.g. collapse the
 * three OAuth branches into one "OAuth path" node). Membership lives
 * here as ``member_ids`` — the SSOT, so step / decision carry no new
 * field. Collapsing the group (BaseFields ``collapsed``) hides its
 * members; ``member_ids`` drives the fold + count chrome.
 *
 * Mirrors ``plot_mcp/models.py::GroupNode``: BaseNodeFields +
 * ``member_ids`` + ``body``.
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface GroupJson extends BaseFieldsJson {
  kind: "group";
  member_ids: string[];
  body: string;
}

export class Group implements BaseFields {
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

  readonly kind: "group" = "group";

  readonly member_ids: string[];
  readonly body: string;

  private constructor(base: BaseFields, member_ids: string[], body: string) {
    Object.assign(this, base);
    this.member_ids = member_ids;
    this.body = body;
  }

  static fromJson(raw: unknown): Group {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "group") {
      throw new DomainParseError(
        `Group.fromJson expected kind="group", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    const member_ids = readStringArray(obj.member_ids, "member_ids", raw);
    const body = readOptionalString(obj.body, "body", raw);
    return new Group(base, member_ids, body);
  }

  toJson(): GroupJson {
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
      kind: "group",
      member_ids: this.member_ids,
      body: this.body,
    };
  }
}

function readStringArray(value: unknown, field: string, raw: unknown): string[] {
  if (value === undefined || value === null) return [];
  if (!Array.isArray(value) || value.some((v) => typeof v !== "string")) {
    throw new DomainParseError(
      `Group.${field} must be an array of strings, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value as string[];
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Group.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

registerKindParser("group", (raw) => Group.fromJson(raw) as never);
