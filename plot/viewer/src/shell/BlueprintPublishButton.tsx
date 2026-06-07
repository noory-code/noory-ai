/**
 * v0.24.13 (D-2026-05-21-B) — "설계도 발행" button + bump dialog.
 *
 * Replaces the older "Mark session…" button in CanvasTabs. Clicking opens
 * a small popover with three options (Major / Minor / Patch). Each shows
 * the resulting version (current → next) so the user can choose without
 * memorising semver rules. Confirm fires ``POST /api/projects/{id}/publish``
 * via the parent's ``onPublish`` callback.
 */
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import type { BlueprintBump } from "../api";
import { useDialog } from "./dialog/DialogProvider";

interface BlueprintPublishButtonProps {
  currentVersion: string;
  onPublish: (bump: BlueprintBump, message?: string) => void | Promise<void>;
  disabled?: boolean;
}

function bumpPreview(current: string, bump: BlueprintBump): string {
  if (!current.startsWith("v")) return current;
  const parts = current.slice(1).split(".");
  if (parts.length !== 3 || !parts.every((p) => /^\d+$/.test(p))) return current;
  const [maj, min, pat] = parts.map((p) => parseInt(p, 10));
  if (bump === "major") return `v${maj + 1}.0.0`;
  if (bump === "minor") return `v${maj}.${min + 1}.0`;
  return `v${maj}.${min}.${pat + 1}`;
}

export function BlueprintPublishButton({
  currentVersion,
  onPublish,
  disabled,
}: BlueprintPublishButtonProps) {
  const { t } = useTranslation();
  const dialog = useDialog();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    const onDocClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  const handlePick = async (bump: BlueprintBump) => {
    const next = bumpPreview(currentVersion, bump);
    if (
      !(await dialog.confirm({
        message: t("publishProject.confirm", { from: currentVersion, to: next }),
      }))
    )
      return;
    setOpen(false);
    void onPublish(bump);
  };

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        disabled={disabled}
        className="rounded border border-line-strong bg-surface px-3 py-1 text-xs text-fg hover:bg-surface-muted disabled:opacity-50"
        title={t("publishProject.hint")}
      >
        📤 {t("publishProject.label")} ▾
      </button>
      {open && (
        <div className="absolute right-0 z-20 mt-1 min-w-[220px] rounded border border-line bg-surface p-1 text-xs shadow-lg">
          <div className="px-2 py-1 text-[10px] uppercase tracking-wide text-fg-faint">
            {t("publishProject.bumpHeader", { current: currentVersion })}
          </div>
          {(["major", "minor", "patch"] as const).map((bump) => (
            <button
              key={bump}
              type="button"
              onClick={() => handlePick(bump)}
              className="flex w-full items-center justify-between gap-3 rounded px-2 py-1.5 text-left text-fg hover:bg-surface-subtle"
            >
              <span>{t(`publishProject.${bump}`)}</span>
              <span className="font-mono text-[10px] text-fg-muted">
                → {bumpPreview(currentVersion, bump)}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
