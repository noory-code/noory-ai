/**
 * Base-fields parser tests for the v0.15 viewer domain layer.
 *
 * Phase 2.0 ships ``parseBaseFields`` + ``DomainParseError`` +
 * ``parseEntity`` + ``registerKindParser``. Per-kind entity classes
 * arrive in Phase 2.1+ and each registers its own parser; this file
 * covers the shared base-field validation used by every entity class.
 */
import { describe, expect, it } from "vitest";
import {
  DomainParseError,
  parseBaseFields,
  parseEntity,
  registeredKinds,
  registerKindParser,
} from "../../src/domain";

describe("parseBaseFields", () => {
  it("populates defaults for an id-only payload", () => {
    const fields = parseBaseFields({ id: "n1" });
    expect(fields.id).toBe("n1");
    expect(fields.label).toBe("");
    expect(fields.x).toBe(0);
    expect(fields.y).toBe(0);
    expect(fields.width).toBe(180);
    expect(fields.height).toBe(80);
    expect(fields.color).toBe("#ffffff");
    expect(fields.shape).toBe("rounded");
    expect(fields.icon).toBeNull();
    expect(fields.parent_id).toBeNull();
    expect(fields.collapsed).toBe(false);
    expect(fields.is_root).toBe(false);
    expect(fields.details_path).toBeNull();
  });

  it("preserves provided overrides", () => {
    const fields = parseBaseFields({
      id: "n1",
      label: "Hi",
      x: 10,
      y: -5,
      width: 200,
      height: 90,
      color: "#fef3c7",
      shape: "circle",
      icon: "star",
      parent_id: "p1",
      collapsed: true,
      is_root: true,
      details_path: "foundation/mission-1/details.md",
    });
    expect(fields.label).toBe("Hi");
    expect(fields.x).toBe(10);
    expect(fields.color).toBe("#fef3c7");
    expect(fields.shape).toBe("circle");
    expect(fields.icon).toBe("star");
    expect(fields.parent_id).toBe("p1");
    expect(fields.collapsed).toBe(true);
    expect(fields.is_root).toBe(true);
    expect(fields.details_path).toBe("foundation/mission-1/details.md");
  });

  it("throws DomainParseError on missing id", () => {
    expect(() => parseBaseFields({})).toThrow(DomainParseError);
    expect(() => parseBaseFields({ id: "" })).toThrow(DomainParseError);
  });

  it("throws DomainParseError on non-string id", () => {
    expect(() => parseBaseFields({ id: 42 })).toThrow(DomainParseError);
  });

  it("throws DomainParseError on non-object input", () => {
    expect(() => parseBaseFields(null)).toThrow(DomainParseError);
    expect(() => parseBaseFields("not an object")).toThrow(DomainParseError);
    expect(() => parseBaseFields(123)).toThrow(DomainParseError);
  });

  it("throws DomainParseError on non-numeric position", () => {
    expect(() => parseBaseFields({ id: "n1", x: "10" })).toThrow(DomainParseError);
    expect(() => parseBaseFields({ id: "n1", x: NaN })).toThrow(DomainParseError);
  });

  it("throws DomainParseError on unknown shape", () => {
    expect(() => parseBaseFields({ id: "n1", shape: "triangle" })).toThrow(DomainParseError);
  });

  it("attaches the raw input to the error for debugging", () => {
    const raw = { x: 5 };
    try {
      parseBaseFields(raw);
      throw new Error("expected DomainParseError");
    } catch (err) {
      expect(err).toBeInstanceOf(DomainParseError);
      expect((err as DomainParseError).raw).toBe(raw);
    }
  });
});

describe("parseEntity dispatch", () => {
  it("rejects raw without a kind discriminator", () => {
    expect(() => parseEntity({ id: "n1" })).toThrow(DomainParseError);
  });

  it("rejects raw with a non-string kind", () => {
    expect(() => parseEntity({ id: "n1", kind: 42 })).toThrow(DomainParseError);
  });

  it("rejects unknown kinds while the registry is partial", () => {
    expect(() => parseEntity({ id: "n1", kind: "ghost" })).toThrow(DomainParseError);
  });

  it("dispatches to a registered parser when one exists", () => {
    // Sanity wiring test using a test-only kind so we don't collide
    // with the auto-registered per-kind classes (metric, etc.).
    const FAKE_KIND = "__test_only_kind__";
    let called = false;
    registerKindParser(FAKE_KIND, (raw) => {
      called = true;
      const obj = raw as Record<string, unknown>;
      // Cast to SketchNode for the test — real parsers return per-kind classes.
      return { id: obj.id as string, kind: FAKE_KIND } as never;
    });
    parseEntity({ id: "n1", kind: FAKE_KIND });
    expect(called).toBe(true);
    expect(registeredKinds()).toContain(FAKE_KIND);
  });

  it("registers per-kind parsers as their entity-class modules import", () => {
    // Importing the domain barrel side-effect-loads every per-kind
    // entity class (Metric, in Phase 2.1). The registry should reflect
    // that without the test having to call ``registerKindParser`` itself.
    expect(registeredKinds()).toContain("metric");
  });
});
