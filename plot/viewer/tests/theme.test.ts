/**
 * Theme pure helpers (D-2026-06-07-C) — resolution, stored-choice parsing,
 * and the document-root class application that drives Tailwind `darkMode:
 * "class"`. No React; these are the testable core of the theme system.
 */
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  applyTheme,
  isThemeChoice,
  readStoredChoice,
  resolveTheme,
  THEME_STORAGE_KEY,
} from "../src/theme/theme";

describe("resolveTheme", () => {
  it("system follows OS preference", () => {
    expect(resolveTheme("system", true)).toBe("dark");
    expect(resolveTheme("system", false)).toBe("light");
  });
  it("explicit choice ignores OS preference", () => {
    expect(resolveTheme("light", true)).toBe("light");
    expect(resolveTheme("dark", false)).toBe("dark");
  });
});

describe("isThemeChoice", () => {
  it("accepts the three valid choices", () => {
    expect(isThemeChoice("light")).toBe(true);
    expect(isThemeChoice("dark")).toBe(true);
    expect(isThemeChoice("system")).toBe(true);
  });
  it("rejects anything else", () => {
    expect(isThemeChoice("auto")).toBe(false);
    expect(isThemeChoice("")).toBe(false);
    expect(isThemeChoice(null)).toBe(false);
    expect(isThemeChoice(undefined)).toBe(false);
  });
});

describe("readStoredChoice", () => {
  const store = (v: string | null) => ({ getItem: () => v });
  it("returns the stored choice when valid", () => {
    expect(readStoredChoice(store("dark"))).toBe("dark");
    expect(readStoredChoice(store("light"))).toBe("light");
    expect(readStoredChoice(store("system"))).toBe("system");
  });
  it("defaults to system when absent or invalid", () => {
    expect(readStoredChoice(store(null))).toBe("system");
    expect(readStoredChoice(store("nonsense"))).toBe("system");
  });
  it("uses the plot:theme key against real localStorage", () => {
    localStorage.setItem(THEME_STORAGE_KEY, "dark");
    expect(readStoredChoice()).toBe("dark");
    localStorage.removeItem(THEME_STORAGE_KEY);
    expect(readStoredChoice()).toBe("system");
  });
});

describe("applyTheme", () => {
  let root: HTMLElement;
  beforeEach(() => {
    root = document.createElement("html");
  });
  afterEach(() => {
    document.documentElement.classList.remove("dark");
  });
  it("adds the dark class for dark, removes it for light", () => {
    applyTheme("dark", root);
    expect(root.classList.contains("dark")).toBe(true);
    applyTheme("light", root);
    expect(root.classList.contains("dark")).toBe(false);
  });
  it("defaults to documentElement", () => {
    applyTheme("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
    applyTheme("light");
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });
});
