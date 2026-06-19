/**
 * v0.28.0 (D-2026-05-30-C) — ``decision`` entity class.
 *
 * A flowchart decision (diamond) inside a service_detail canvas: a
 * branch point between action steps, either a user choice (방식 선택)
 * or a system judgment (검증 성공/실패). The branches themselves are
 * user-drawn labelled edges; the node only carries the question
 * (``label``) + optional notes (``body``).
 *
 * Mirrors ``plot_mcp/models.py::DecisionNode``: BaseNodeFields +
 * ``body``. No ``order`` / ``outcome`` (those are ``step``'s) — a
 * decision has many labelled outcomes, expressed as outgoing edges,
 * not a single field.
 *
 * Self-registers its ``fromJson`` parser with ``parseEntity`` on
 * module load.
 */
import type { BaseFields } from "./BaseFields";
import type { DecisionJson } from "./wire.gen";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export class Decision implements BaseFields {
  // BaseFields slice — populated from ``parseBaseFields`` in fromJson.
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

  // Discriminator (always "decision" for instances of this class).
  readonly kind: "decision" = "decision";

  // Decision-specific typed field.
  readonly body: string;

  private constructor(base: BaseFields, body: string) {
    Object.assign(this, base);
    this.body = body;
  }

  /** Parse + validate a raw dict into a Decision instance. Throws
   *  ``DomainParseError`` on any invariant violation. */
  static fromJson(raw: unknown): Decision {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "decision") {
      throw new DomainParseError(
        `Decision.fromJson expected kind="decision", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    const body = readOptionalString(obj.body, "body", raw);
    return new Decision(base, body);
  }

  /** Wire-shape representation. ``kind`` is always emitted so the
   *  server-side discriminated union can dispatch. */
  toJson(): DecisionJson {
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
      kind: "decision",
      body: this.body,
    };
  }
}

function readOptionalString(value: unknown, field: string, raw: unknown): string {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") {
    throw new DomainParseError(
      `Decision.${field} must be a string, got ${JSON.stringify(value)}`,
      raw,
    );
  }
  return value;
}

// Self-register so ``parseEntity({kind: "decision", ...})`` dispatches here.
registerKindParser("decision", (raw) => Decision.fromJson(raw) as never);
