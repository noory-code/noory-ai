/**
 * ThemeProvider / useTheme (D-2026-06-07-C) — resolves choice + OS preference,
 * applies `.dark` on the document root, persists explicit choices to
 * localStorage, and tracks live OS changes while on `system`.
 */
import "@testing-library/jest-dom/vitest";
import { act, render, renderHook, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ThemeProvider, useTheme } from "../src/theme/ThemeProvider";
import { THEME_STORAGE_KEY } from "../src/theme/theme";

/** Stub window.matchMedia and return a controller to flip the OS preference. */
function stubMatchMedia(initialDark: boolean) {
  let dark = initialDark;
  const listeners = new Set<(e: MediaQueryListEvent) => void>();
  vi.stubGlobal("matchMedia", (query: string) => ({
    get matches() {
      return dark;
    },
    media: query,
    addEventListener: (_: string, cb: (e: MediaQueryListEvent) => void) => listeners.add(cb),
    removeEventListener: (_: string, cb: (e: MediaQueryListEvent) => void) => listeners.delete(cb),
    addListener: (cb: (e: MediaQueryListEvent) => void) => listeners.add(cb),
    removeListener: (cb: (e: MediaQueryListEvent) => void) => listeners.delete(cb),
    dispatchEvent: () => true,
  }));
  return {
    setDark(next: boolean) {
      dark = next;
      for (const cb of listeners) cb({ matches: next } as MediaQueryListEvent);
    },
  };
}

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider>{children}</ThemeProvider>
);

afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
  document.documentElement.classList.remove("dark");
});

describe("ThemeProvider", () => {
  it("with no stored choice, follows OS dark preference", () => {
    stubMatchMedia(true);
    const { result } = renderHook(() => useTheme(), { wrapper });
    expect(result.current.choice).toBe("system");
    expect(result.current.resolved).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("with no stored choice, follows OS light preference", () => {
    stubMatchMedia(false);
    const { result } = renderHook(() => useTheme(), { wrapper });
    expect(result.current.resolved).toBe("light");
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("hydrates an explicit stored choice over the OS preference", () => {
    localStorage.setItem(THEME_STORAGE_KEY, "light");
    stubMatchMedia(true); // OS prefers dark, but stored choice wins
    const { result } = renderHook(() => useTheme(), { wrapper });
    expect(result.current.choice).toBe("light");
    expect(result.current.resolved).toBe("light");
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("setChoice persists to localStorage and re-applies the class", () => {
    stubMatchMedia(false);
    const { result } = renderHook(() => useTheme(), { wrapper });
    act(() => result.current.setChoice("dark"));
    expect(result.current.resolved).toBe("dark");
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("tracks live OS changes while on system", () => {
    const mq = stubMatchMedia(false);
    const { result } = renderHook(() => useTheme(), { wrapper });
    expect(result.current.resolved).toBe("light");
    act(() => mq.setDark(true));
    expect(result.current.resolved).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("ignores live OS changes once an explicit choice is set", () => {
    const mq = stubMatchMedia(false);
    const { result } = renderHook(() => useTheme(), { wrapper });
    act(() => result.current.setChoice("light"));
    act(() => mq.setDark(true)); // OS goes dark, but choice is explicit light
    expect(result.current.resolved).toBe("light");
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("useTheme throws outside a provider", () => {
    // Suppress React's error-boundary console noise for this expected throw.
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => renderHook(() => useTheme())).toThrow(/ThemeProvider/);
    spy.mockRestore();
  });

  it("provides the toggle subtree to children", () => {
    stubMatchMedia(false);
    render(
      <ThemeProvider>
        <span>themed-child</span>
      </ThemeProvider>,
    );
    expect(screen.getByText("themed-child")).toBeInTheDocument();
  });
});
