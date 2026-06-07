/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      // Semantic theme tokens (D-2026-06-07-C). Values are CSS variables
      // defined in `styles.css` (`:root` = light, `.dark` = dark); each holds
      // space-separated RGB channels so Tailwind's <alpha-value> still works
      // (e.g. `bg-overlay/40`). Components use these names, never raw palette
      // colours — `tests/structural-guards.test.tsx` enforces it.
      colors: {
        // surfaces (bg-*)
        surface: "rgb(var(--surface) / <alpha-value>)",
        "surface-muted": "rgb(var(--surface-muted) / <alpha-value>)",
        "surface-subtle": "rgb(var(--surface-subtle) / <alpha-value>)",
        "surface-inverse": "rgb(var(--surface-inverse) / <alpha-value>)",
        overlay: "rgb(var(--overlay) / <alpha-value>)",
        // foreground / text (text-fg*)
        fg: "rgb(var(--fg) / <alpha-value>)",
        "fg-strong": "rgb(var(--fg-strong) / <alpha-value>)",
        "fg-secondary": "rgb(var(--fg-secondary) / <alpha-value>)",
        "fg-muted": "rgb(var(--fg-muted) / <alpha-value>)",
        "fg-faint": "rgb(var(--fg-faint) / <alpha-value>)",
        "fg-inverse": "rgb(var(--fg-inverse) / <alpha-value>)",
        // borders (border-line*)
        line: "rgb(var(--line) / <alpha-value>)",
        "line-strong": "rgb(var(--line-strong) / <alpha-value>)",
        // semantic accents (selection / warning / success / special)
        accent: "rgb(var(--accent) / <alpha-value>)",
        "accent-fg": "rgb(var(--accent-fg) / <alpha-value>)",
        "accent-soft": "rgb(var(--accent-soft) / <alpha-value>)",
        warn: "rgb(var(--warn) / <alpha-value>)",
        "warn-fg": "rgb(var(--warn-fg) / <alpha-value>)",
        "warn-soft": "rgb(var(--warn-soft) / <alpha-value>)",
        "warn-line": "rgb(var(--warn-line) / <alpha-value>)",
        ok: "rgb(var(--ok) / <alpha-value>)",
        "ok-fg": "rgb(var(--ok-fg) / <alpha-value>)",
        "ok-soft": "rgb(var(--ok-soft) / <alpha-value>)",
        "ok-line": "rgb(var(--ok-line) / <alpha-value>)",
        special: "rgb(var(--special) / <alpha-value>)",
        "special-fg": "rgb(var(--special-fg) / <alpha-value>)",
        "special-soft": "rgb(var(--special-soft) / <alpha-value>)",
        danger: "rgb(var(--danger) / <alpha-value>)",
        "danger-fg": "rgb(var(--danger-fg) / <alpha-value>)",
        "danger-soft": "rgb(var(--danger-soft) / <alpha-value>)",
        "danger-line": "rgb(var(--danger-line) / <alpha-value>)",
        info: "rgb(var(--info) / <alpha-value>)",
        "info-fg": "rgb(var(--info-fg) / <alpha-value>)",
        "info-soft": "rgb(var(--info-soft) / <alpha-value>)",
      },
    },
  },
  plugins: [],
};
