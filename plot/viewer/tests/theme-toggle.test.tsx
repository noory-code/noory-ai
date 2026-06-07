/**
 * ThemeToggle (D-2026-06-07-C) — three-way Light / Dark / System pill that
 * mirrors LanguageToggle. Reflects the current choice (aria-pressed) and
 * writes the chosen value through useTheme. Labels are i18n-routed; assertions
 * key off data-testid + aria-pressed so they don't couple to locale text.
 */
import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import "../src/i18n";
import { ThemeProvider } from "../src/theme/ThemeProvider";
import { ThemeToggle } from "../src/shell/ThemeToggle";
import { THEME_STORAGE_KEY } from "../src/theme/theme";

function stubMatchMedia(dark: boolean) {
  vi.stubGlobal("matchMedia", (query: string) => ({
    matches: dark,
    media: query,
    addEventListener: () => {},
    removeEventListener: () => {},
    addListener: () => {},
    removeListener: () => {},
    dispatchEvent: () => true,
  }));
}

function renderToggle() {
  return render(
    <ThemeProvider>
      <ThemeToggle />
    </ThemeProvider>,
  );
}

beforeEach(() => stubMatchMedia(false));
afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
  document.documentElement.classList.remove("dark");
});

describe("ThemeToggle", () => {
  it("renders a button for each of light / dark / system", () => {
    renderToggle();
    expect(screen.getByTestId("theme-opt-light")).toBeInTheDocument();
    expect(screen.getByTestId("theme-opt-dark")).toBeInTheDocument();
    expect(screen.getByTestId("theme-opt-system")).toBeInTheDocument();
  });

  it("marks the current choice as pressed (default system)", () => {
    renderToggle();
    expect(screen.getByTestId("theme-opt-system")).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByTestId("theme-opt-dark")).toHaveAttribute("aria-pressed", "false");
  });

  it("selecting dark sets the choice, persists, and applies the class", () => {
    renderToggle();
    fireEvent.click(screen.getByTestId("theme-opt-dark"));
    expect(screen.getByTestId("theme-opt-dark")).toHaveAttribute("aria-pressed", "true");
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });
});
