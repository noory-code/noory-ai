/**
 * Semantic theme token SSOT (D-2026-06-12-C / ROADMAP Track 1.4 final).
 *
 * Three artefacts have to stay in lock-step or the theme silently desyncs:
 *   1. `src/theme/tokens.css` `:root` + `.dark` blocks declare CSS vars.
 *   2. `tailwind.config.js` `colors` map exposes them as utility classes
 *      (`bg-surface`, `text-fg-strong`, `border-line-strong`, …).
 *   3. TypeScript code references the utility names by hand.
 *
 * This file is the single source of truth for **which tokens exist**.
 * `tests/theme-tokens-ssot.test.ts` parses the other two files and asserts
 * the token name set matches `SEMANTIC_TOKENS` here. Add a new token by
 * (a) putting its name in the appropriate group below, then (b) adding the
 * `--name` declarations to both `:root` and `.dark` in `tokens.css`, then
 * (c) the `name: "rgb(var(--name) / <alpha-value>)"` entry in
 * `tailwind.config.js`. Skipping any of those three steps fails the guard.
 */

// Token name groups — kept on separate lines so a diff shows the actual
// shape of the palette (surfaces / foregrounds / lines / colour families).
const SURFACE = [
  "surface",
  "surface-muted",
  "surface-subtle",
  "surface-inverse",
  "overlay",
] as const;

const FG = [
  "fg",
  "fg-strong",
  "fg-secondary",
  "fg-muted",
  "fg-faint",
  "fg-inverse",
] as const;

const LINE = ["line", "line-strong"] as const;

const ACCENT = ["accent", "accent-fg", "accent-soft"] as const;

const WARN = ["warn", "warn-fg", "warn-soft", "warn-line"] as const;

const OK = ["ok", "ok-fg", "ok-soft", "ok-line"] as const;

const SPECIAL = ["special", "special-fg", "special-soft"] as const;

const DANGER = ["danger", "danger-fg", "danger-soft", "danger-line"] as const;

const INFO = ["info", "info-fg", "info-soft"] as const;

/** Every semantic token the viewer ships, in the same order they appear
 *  in `tokens.css`. Matches the `tailwind.config.js` `colors` map keys. */
export const SEMANTIC_TOKENS = [
  ...SURFACE,
  ...FG,
  ...LINE,
  ...ACCENT,
  ...WARN,
  ...OK,
  ...SPECIAL,
  ...DANGER,
  ...INFO,
] as const;

/** Compile-time union of every semantic token name. */
export type SemanticToken = (typeof SEMANTIC_TOKENS)[number];

/** Tailwind utility names that ride a semantic token. Components that
 *  accept a token through a typed prop should use these helpers so a
 *  rename in `SEMANTIC_TOKENS` flows through `tsc` errors. */
export type TokenTextClass = `text-${SemanticToken}`;
export type TokenBgClass = `bg-${SemanticToken}`;
export type TokenBorderClass = `border-${SemanticToken}`;
export type TokenRingClass = `ring-${SemanticToken}`;
