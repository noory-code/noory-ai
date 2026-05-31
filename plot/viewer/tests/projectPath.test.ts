/**
 * joinWorkspaceDir — effective project-path derivation (D-2026-05-31-M).
 */
import { describe, expect, it } from "vitest";
import { joinWorkspaceDir } from "../src/lib/projectPath";

describe("joinWorkspaceDir", () => {
  it("returns the root unchanged for a root-level project ('.')", () => {
    expect(joinWorkspaceDir("/repo", ".")).toBe("/repo");
    expect(joinWorkspaceDir("/repo", "")).toBe("/repo");
  });

  it("joins a nested dir onto the root", () => {
    expect(joinWorkspaceDir("/repo", "plot")).toBe("/repo/plot");
    expect(joinWorkspaceDir("/repo", "packages/ui")).toBe("/repo/packages/ui");
  });

  it("normalizes trailing/leading slashes", () => {
    expect(joinWorkspaceDir("/repo/", "plot")).toBe("/repo/plot");
    expect(joinWorkspaceDir("/repo", "/plot")).toBe("/repo/plot");
  });
});
