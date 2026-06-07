/**
 * Theme pure helpers (D-2026-06-07-C).
 *
 * The viewer ships light + dark themes expressed through semantic
 * CSS-variable tokens (see `styles.css` / `tailwind.config.js`). This module
 * holds the framework-free core: which choices exist, how a choice + OS
 * preference resolve to an effective theme, how the persisted choice is read,
 * and how the resolved theme is written onto the document root (Tailwind runs
 * in `darkMode: "class"`, so the `.dark` class on `<html>` is the switch).
 *
 * The React wiring (state, matchMedia listener, persistence) lives in
 * `theme/ThemeProvider.tsx`; the toggle UI in `shell/ThemeToggle.tsx`.
 */

/** localStorage key for the explicit theme choice. Mirrors `plot:lang`. */
export const THEME_STORAGE_KEY = "plot:theme";

/** What the user can pick. `system` defers to the OS preference. */
export type ThemeChoice = "light" | "dark" | "system";

/** The effective theme actually applied to the document. */
export type ResolvedTheme = "light" | "dark";

const CHOICES: readonly ThemeChoice[] = ["light", "dark", "system"];

export function isThemeChoice(value: unknown): value is ThemeChoice {
  return typeof value === "string" && (CHOICES as readonly string[]).includes(value);
}

/** Resolve the effective theme from the user's choice + the OS preference. */
export function resolveTheme(choice: ThemeChoice, prefersDark: boolean): ResolvedTheme {
  if (choice === "system") return prefersDark ? "dark" : "light";
  return choice;
}

/**
 * Read the persisted choice. Absent or invalid → `system` (follow the OS).
 * Defaults to real `localStorage`; a stub may be injected for tests.
 */
export function readStoredChoice(storage: Pick<Storage, "getItem"> = localStorage): ThemeChoice {
  try {
    const stored = storage.getItem(THEME_STORAGE_KEY);
    return isThemeChoice(stored) ? stored : "system";
  } catch {
    return "system";
  }
}

/** Apply the resolved theme to the document root (Tailwind `darkMode: "class"`). */
export function applyTheme(
  resolved: ResolvedTheme,
  root: HTMLElement = document.documentElement,
): void {
  root.classList.toggle("dark", resolved === "dark");
}
