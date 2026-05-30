/**
 * v0.28.2 (D-2026-05-30-E) — negative-case (failure) tint.
 *
 * A `step.polarity` of "negative" tints the node red, "positive"
 * green; "neutral" returns null so the caller keeps the user's colour.
 */
import { describe, expect, it } from "vitest";
import { polarityTint } from "../src/canvases/sketch/polarityTint";
import { Step } from "../src/domain/Step";

describe("polarityTint (D-2026-05-30-E)", () => {
  it("returns a red tint for negative", () => {
    expect(polarityTint("negative")).toBe("#fee2e2");
  });
  it("returns a green tint for positive", () => {
    expect(polarityTint("positive")).toBe("#dcfce7");
  });
  it("returns null for neutral (keep user colour)", () => {
    expect(polarityTint("neutral")).toBeNull();
  });
  it("returns null for undefined / unknown (back-compat)", () => {
    expect(polarityTint(undefined)).toBeNull();
    expect(polarityTint("bogus")).toBeNull();
  });
});

describe("Step.polarity parse (D-2026-05-30-E)", () => {
  const base = {
    id: "s1",
    label: "Submit",
    x: 0,
    y: 0,
    width: 150,
    height: 60,
    color: "#fff",
    shape: "rectangle" as const,
    icon: null,
    kind: "step" as const,
  };
  it("defaults to neutral when omitted", () => {
    expect(Step.fromJson(base).polarity).toBe("neutral");
  });
  it("preserves a negative polarity through round-trip", () => {
    const s = Step.fromJson({ ...base, polarity: "negative" });
    expect(s.polarity).toBe("negative");
    expect(s.toJson().polarity).toBe("negative");
  });
});
