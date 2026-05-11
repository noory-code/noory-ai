/**
 * i18n bootstrap for Plot viewer.
 *
 * - English is the primary locale; Korean is the first supported
 *   locale. Per `feedback_plot_global_service.md` and Plot CLAUDE.md
 *   anti-pattern (v0.14.4): every user-facing UI text must route
 *   through this resource bundle.
 * - Detection order: `localStorage["plot:lang"]` → `navigator.language`
 *   → fallback `en`.
 * - This module is imported for side effects from `main.tsx`. Do
 *   not call `init` again elsewhere.
 */
import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import en from "./locales/en.json";
import ko from "./locales/ko.json";

export const SUPPORTED_LOCALES = ["en", "ko"] as const;
export type Locale = (typeof SUPPORTED_LOCALES)[number];

export const LOCALE_LABELS: Record<Locale, string> = {
  en: "EN",
  ko: "KO",
};

export const LOCALE_STORAGE_KEY = "plot:lang";

void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      ko: { translation: ko },
    },
    fallbackLng: "en",
    supportedLngs: SUPPORTED_LOCALES,
    nonExplicitSupportedLngs: true,
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator"],
      lookupLocalStorage: LOCALE_STORAGE_KEY,
      caches: ["localStorage"],
    },
    returnNull: false,
  });

export default i18n;
