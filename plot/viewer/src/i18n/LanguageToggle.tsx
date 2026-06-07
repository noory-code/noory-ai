/**
 * Plot language toggle.
 *
 * Compact EN / KO pill rendered at the bottom of `SketchSidebar`.
 * Persists the choice in localStorage via the language detector
 * configured in `i18n/index.ts` (key = `plot:lang`).
 *
 * Per `feedback_plot_global_service.md` — English is primary, Korean
 * is the first locale. Adding a third locale: extend
 * `SUPPORTED_LOCALES` + `LOCALE_LABELS` + add a JSON file +
 * `import` in `i18n/index.ts`. No change to this component.
 */
import { useTranslation } from "react-i18next";
import { LOCALE_LABELS, SUPPORTED_LOCALES, type Locale } from ".";

export function LanguageToggle() {
  const { t, i18n } = useTranslation();
  const current = (i18n.resolvedLanguage ?? "en") as Locale;

  return (
    <div
      role="group"
      aria-label={t("common.language")}
      className="flex items-center gap-0.5 rounded-md border border-line bg-surface p-0.5 text-[10px] font-medium"
    >
      {SUPPORTED_LOCALES.map((locale) => {
        const active = locale === current;
        return (
          <button
            key={locale}
            type="button"
            onClick={() => void i18n.changeLanguage(locale)}
            aria-pressed={active}
            className={`rounded px-1.5 py-0.5 ${
              active
                ? "bg-surface-inverse text-fg-inverse"
                : "text-fg-muted hover:bg-surface-subtle"
            }`}
          >
            {LOCALE_LABELS[locale]}
          </button>
        );
      })}
    </div>
  );
}
