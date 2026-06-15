/**
 * Regression: on-card inline editors must use a node-card-locked surface
 * (`bg-surface-subtle`, slate-100 in BOTH themes) for their background,
 * NOT the theme-following `bg-surface`. Inside `.node-card`, `text-fg-strong`
 * is locked to slate-900 in both themes (tokens.css), so a theme-following
 * `bg-surface` goes dark in dark mode → dark-text-on-dark = invisible.
 *
 * D-2026-06-15-I fixed light mode (bg-surface = white) but missed dark mode;
 * this guard pins the real invariant. (Root cause: workflow diagnosis,
 * 2026-06-15 — the user's "라벨 편집할 때 글씨가 안 보인다".)
 */
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EditableText } from "../src/edit/EditableText";

describe("EditableText on-card contrast (dark + light)", () => {
  it("edit input uses node-card-locked bg-surface-subtle + text-fg-strong, not bare bg-surface", () => {
    render(<EditableText value="hello" onCommit={() => {}} ariaLabel="Node label" />);
    // Enter edit mode (the display span is a role=button).
    fireEvent.click(screen.getByRole("button"));
    const input = screen.getByLabelText("Node label") as HTMLInputElement;
    expect(input.className).toContain("bg-surface-subtle");
    expect(input.className).toContain("text-fg-strong");
    // Must NOT use the theme-following bare `bg-surface` (would be dark-on-dark).
    expect(input.className).not.toMatch(/bg-surface(?!-subtle)/);
  });
});
