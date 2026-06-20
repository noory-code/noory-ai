/**
 * ``note`` entity (D-2026-06-17-F). A canvas-global ambient memo on the
 * Feature canvas ("모바일 우선·본문 500자") — a human-read guide AND context the
 * AI always lays under its work. **Edgeless invariant:** a note NEVER
 * participates in an edge (enforced in ``handleConnect`` + the server
 * ``CanvasDoc`` validator). ``body`` = the memo text; ``label`` is its title.
 */
import type { BaseFields } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";
import type { NoteJson } from "./wire.gen";

export class Note implements BaseFields {
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

  readonly kind: "note" = "note";

  readonly body: string;

  private constructor(base: BaseFields, body: string) {
    Object.assign(this, base);
    this.body = body;
  }

  static fromJson(raw: unknown): Note {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "note") {
      throw new DomainParseError(
        `Note.fromJson expected kind="note", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    return new Note(base, readOptionalString(obj.body, "body", raw));
  }

  toJson(): NoteJson {
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
      kind: "note",
      body: this.body,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Note.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

registerKindParser("note", (raw) => Note.fromJson(raw) as never);
