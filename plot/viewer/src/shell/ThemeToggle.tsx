/**
 * Plot theme toggle (D-2026-06-07-C).
 *
 * Compact Light / Dark / System pill, rendered next to `LanguageToggle`
 * (sidebar footer + ServiceDetail stencil panel). Reads + writes the choice
 * through `useTheme`; `system` follows the OS `prefers-color-scheme`. Labels
 * route through i18n (`theme.*`). Styled with semantic theme tokens so the
 * pill itself themes correctly in both modes.
 */
import { useTranslation } from "react-i18next";

import { useTheme } from "../theme/ThemeProvider";
import type { ThemeChoice } from "../theme/theme";

const OPTIONS: { value: ThemeChoice; icon: string }[] = [
  { value: "light", icon: "☀" },
  { value: "dark", icon: "☾" },
  { value: "system", icon: "◐" },
];

export function ThemeToggle() {
  const { t } = useTranslation();
  const { choice, setChoice } = useTheme();

  return (
    <div
      role="group"
      aria-label={t("theme.label")}
      className="flex items-center gap-0.5 rounded-md border border-line bg-surface p-0.5 text-[10px] font-medium"
    >
      {OPTIONS.map(({ value, icon }) => {
        const active = value === choice;
        return (
          <button
            key={value}
            type="button"
            data-testid={`theme-opt-${value}`}
            onClick={() => setChoice(value)}
            aria-pressed={active}
            aria-label={t(`theme.${value}`)}
            title={t(`theme.${value}`)}
            className={`rounded px-1.5 py-0.5 ${
              active
                ? "bg-surface-inverse text-fg-inverse"
                : "text-fg-muted hover:bg-surface-subtle"
            }`}
          >
            <span aria-hidden>{icon}</span>
          </button>
        );
      })}
    </div>
  );
}
