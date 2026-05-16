/**
 * v0.15 Phase 2.7 — ``mission_ref`` entity. References a Foundation
 * Mission master; lets a service declare which Mission it answers to.
 */
import type { BaseFields, BaseFieldsJson } from "./BaseFields";
import { parseBaseFields } from "./BaseFields";
import { DomainParseError } from "./DomainParseError";
import { registerKindParser } from "./parseEntity";

export interface MissionRefJson extends BaseFieldsJson {
  kind: "mission_ref";
  ref_mission_id: string | null;
}

export class MissionRef implements BaseFields {
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

  readonly kind: "mission_ref" = "mission_ref";

  readonly ref_mission_id: string | null;

  private constructor(base: BaseFields, ref_mission_id: string | null) {
    Object.assign(this, base);
    this.ref_mission_id = ref_mission_id;
  }

  static fromJson(raw: unknown): MissionRef {
    const base = parseBaseFields(raw);
    const obj = raw as Record<string, unknown>;
    if (obj.kind !== undefined && obj.kind !== "mission_ref") {
      throw new DomainParseError(
        `MissionRef.fromJson expected kind="mission_ref", got ${JSON.stringify(obj.kind)}`,
        raw,
      );
    }
    let ref_mission_id: string | null = null;
    if (obj.ref_mission_id !== undefined && obj.ref_mission_id !== null) {
      if (typeof obj.ref_mission_id !== "string") {
        throw new DomainParseError(
          `MissionRef.ref_mission_id must be a string or null, got ${JSON.stringify(obj.ref_mission_id)}`,
          raw,
        );
      }
      ref_mission_id = obj.ref_mission_id;
    }
    return new MissionRef(base, ref_mission_id);
  }

  toJson(): MissionRefJson {
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
      kind: "mission_ref",
      ref_mission_id: this.ref_mission_id,
    };
  }
}

registerKindParser("mission_ref", (raw) => MissionRef.fromJson(raw) as never);
