import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { open } from "@tauri-apps/plugin-dialog";

declare global {
  interface Window {
    __TAURI_INTERNALS__?: unknown;
  }
}

export function ProjectPicker() {
  const { t } = useTranslation();
  const inTauri = typeof window.__TAURI_INTERNALS__ !== "undefined";

  const handleOpen = useCallback(async () => {
    const selected = await open({ directory: true, multiple: false });
    if (typeof selected === "string") {
      window.location.href = `/?project_path=${encodeURIComponent(selected)}`;
    }
  }, []);

  return (
    <div className="flex h-full items-center justify-center p-8 text-center">
      <div className="space-y-4">
        <h1 className="text-2xl font-semibold">{t("shell.projectPicker.title")}</h1>
        {inTauri ? (
          <button
            data-testid="open-folder-btn"
            onClick={handleOpen}
            className="rounded-md bg-slate-800 px-4 py-2 text-sm text-white hover:bg-slate-700"
          >
            {t("shell.projectPicker.openFolder")}
          </button>
        ) : (
          <p className="text-slate-500">{t("shell.projectPicker.hint")}</p>
        )}
      </div>
    </div>
  );
}
