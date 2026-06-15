/**
 * D-2026-06-15-K — service.problem (the need the service solves).
 *
 * A service is the process of solving a problem (PHILOSOPHY P5 + user,
 * 2026-06-15). The existing fields (what / value_created / outcome) are
 * all solution-side; `problem` is the one-line need they answer. Distinct
 * from an "overview" (≈ `what`) and from per-actor `actor_ref.pain`.
 */
import { describe, expect, it } from "vitest";
import { Service } from "../src/domain/Service";

describe("D-2026-06-15-K — service.problem", () => {
  it("Service carries + round-trips problem", () => {
    const s = Service.fromJson({
      id: "s1",
      kind: "service",
      problem: "팬이 좋아하는 창작자를 따라갈 방법이 없다",
    });
    expect((s as unknown as { problem: string }).problem).toBe(
      "팬이 좋아하는 창작자를 따라갈 방법이 없다",
    );
    const j = s.toJson() as unknown as { problem: string };
    expect(j.problem).toBe("팬이 좋아하는 창작자를 따라갈 방법이 없다");
  });

  it("Service defaults problem to empty string", () => {
    const s = Service.fromJson({ id: "s1", kind: "service" });
    expect((s as unknown as { problem: string }).problem).toBe("");
  });
});
