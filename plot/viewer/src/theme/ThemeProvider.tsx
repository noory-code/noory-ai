/**
 * ThemeProvider / useTheme (D-2026-06-07-C).
 *
 * Single source of truth for the active theme. Holds the user's choice
 * (`light` | `dark` | `system`), resolves it against the live OS preference,
 * writes the `.dark` class onto `<html>`, and persists explicit choices to
 * `localStorage["plot:theme"]`. Mounted once at the app root (`main.tsx`);
 * the header/sidebar `ThemeToggle` consumes it via `useTheme()`.
 */
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import {
  applyTheme,
  readStoredChoice,
  resolveTheme,
  THEME_STORAGE_KEY,
  type ResolvedTheme,
  type ThemeChoice,
} from "./theme";

interface ThemeContextValue {
  /** The user's stored selection. */
  choice: ThemeChoice;
  /** The effective theme after resolving `system` against the OS. */
  resolved: ResolvedTheme;
  /** Set + persist an explicit choice (or `system` to follow the OS again). */
  setChoice: (choice: ThemeChoice) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

const COLOR_SCHEME_QUERY = "(prefers-color-scheme: dark)";

function prefersDark(): boolean {
  return typeof window !== "undefined" && typeof window.matchMedia === "function"
    ? window.matchMedia(COLOR_SCHEME_QUERY).matches
    : false;
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [choice, setChoiceState] = useState<ThemeChoice>(() => readStoredChoice());
  const [systemDark, setSystemDark] = useState<boolean>(() => prefersDark());

  // Track the OS preference. Kept current always; it only feeds the resolved
  // theme while `choice === "system"`, but the listener is cheap to keep live.
  useEffect(() => {
    if (typeof window === "undefined" || typeof window.matchMedia !== "function") return;
    const mq = window.matchMedia(COLOR_SCHEME_QUERY);
    const onChange = (e: MediaQueryListEvent) => setSystemDark(e.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  const resolved = resolveTheme(choice, systemDark);

  // Reflect the resolved theme onto <html> whenever it changes.
  useEffect(() => {
    applyTheme(resolved);
  }, [resolved]);

  const setChoice = (next: ThemeChoice) => {
    setChoiceState(next);
    try {
      localStorage.setItem(THEME_STORAGE_KEY, next);
    } catch {
      /* private mode / disabled storage — choice still applies for the session */
    }
  };

  return (
    <ThemeContext.Provider value={{ choice, resolved, setChoice }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (ctx === null) {
    throw new Error("useTheme must be used within a <ThemeProvider>");
  }
  return ctx;
}
