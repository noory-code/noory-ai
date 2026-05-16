/**
 * v0.15 Phase 2.5 — ``project`` Foundation anchor entity.
 *
 * v0.13 Phase 0 moved the project anchor from a per-canvas node to
 * ``ProjectDoc.anchors`` and renders it synthetically. This class
 * stays for symmetry with the other 14 kinds and to handle legacy
 * data that still carries a project node.
 *
 * No typed fields — only BaseFields + the kind discriminator.
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface ProjectJson extends BaseFieldsJson {
  kind: "project";
}

export class Project implements BaseFields {
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

  readonly kind: "project" = "project";

  private constructor(base: BaseFields) {
    Object.assign(this, base);
  }

  static fromJson(raw: unknown): Project {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "project") {
      throw new DomainParseError(
        `Project.fromJson expected kind="project", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    return new Project(base);
  }

  toJson(): ProjectJson {
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
      kind: "project",
    };
  }
}

registerKindParser("project", (raw) => Project.fromJson(raw) as never);
