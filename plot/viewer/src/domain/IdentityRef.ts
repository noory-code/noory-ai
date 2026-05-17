/**
 * v0.15 Phase 2.7 — ``identity_ref`` entity. References a Foundation
 * Identity master.
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface IdentityRefJson extends BaseFieldsJson {
  kind: "identity_ref";
  ref_identity_id: string | null;
  /** v0.24.x (D-2026-05-17-M) — service-context notes (4-ref symmetry). */
  notes_in_context: string;
}

export class IdentityRef implements BaseFields {
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

  readonly kind: "identity_ref" = "identity_ref";

  readonly ref_identity_id: string | null;
  readonly notes_in_context: string;

  private constructor(
    base: BaseFields,
    ref_identity_id: string | null,
    notes_in_context: string,
  ) {
    Object.assign(this, base);
    this.ref_identity_id = ref_identity_id;
    this.notes_in_context = notes_in_context;
  }

  static fromJson(raw: unknown): IdentityRef {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "identity_ref") {
      throw new DomainParseError(
        `IdentityRef.fromJson expected kind="identity_ref", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    let ref_identity_id: string | null = null;
    if (obj.ref_identity_id !== undefined && obj.ref_identity_id !== null) {
      if (typeof obj.ref_identity_id !== "string") {
        throw new DomainParseError(
          `IdentityRef.ref_identity_id must be a string or null, got ${JSON.stringify(obj.ref_identity_id)}`,
          raw,
        );
      }
      ref_identity_id = obj.ref_identity_id;
    }
    const notes_in_context = readNotesInContext(obj.notes_in_context, raw);
    return new IdentityRef(base, ref_identity_id, notes_in_context);
  }

  toJson(): IdentityRefJson {
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
      kind: "identity_ref",
      ref_identity_id: this.ref_identity_id,
      notes_in_context: this.notes_in_context,
    };
  }
}

function readNotesInContext(value: unknown, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `IdentityRef.notes_in_context must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

registerKindParser("identity_ref", (raw) => IdentityRef.fromJson(raw) as never);
