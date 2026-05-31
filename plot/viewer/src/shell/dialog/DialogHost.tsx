/**
 * Presentational modal for the dialog system (v0.35.0, D-2026-05-31-W).
 * Matches the DirTreePickerModal chrome (slate backdrop, white rounded
 * panel) so dialogs feel native to the app. ``z-[60]`` sits above other
 * modals (z-50) — a delete confirm fired from inside SketchBodyModal must
 * render on top of it.
 */
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import type { DialogRequest, DialogResult } from "./DialogProvider";

/** Escape / backdrop / cancel value: prompt→null, confirm & alert→false. */
function cancelValue(req: DialogRequest): DialogResult {
  return req.kind === "prompt" ? null : false;
}

export function DialogHost({
  request,
  onSettle,
}: {
  request: DialogRequest | null;
  onSettle: (value: DialogResult) => void;
}) {
  const { t } = useTranslation();
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (request?.kind === "prompt") setValue(request.defaultValue ?? "");
  }, [request]);

  useEffect(() => {
    if (!request) return;
    if (request.kind === "prompt") {
      // Focus + select on the next tick so the input is mounted.
      const id = window.setTimeout(() => inputRef.current?.select(), 0);
      return () => window.clearTimeout(id);
    }
  }, [request]);

  useEffect(() => {
    if (!request) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onSettle(cancelValue(request));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [request, onSettle]);

  if (!request) return null;

  const accept = () =>
    onSettle(request.kind === "prompt" ? value : true);
  const cancel = () => onSettle(cancelValue(request));

  const acceptLabel =
    request.confirmLabel ??
    (request.kind === "alert"
      ? t("common.ok")
      : request.danger
        ? t("common.delete")
        : t("common.confirm"));

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={request.title ?? request.message}
      className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-900/40"
      onClick={cancel}
    >
      <div
        data-testid="dialog-panel"
        className="flex w-[360px] flex-col gap-3 rounded-lg bg-white p-4 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {request.title && (
          <h2 className="text-sm font-semibold text-slate-800">{request.title}</h2>
        )}
        <p className="whitespace-pre-line text-sm text-slate-600">{request.message}</p>
        {request.kind === "prompt" && (
          <input
            ref={inputRef}
            data-testid="dialog-input"
            value={value}
            placeholder={request.placeholder}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") accept();
            }}
            className="rounded border border-slate-300 px-2 py-1 text-sm outline-none focus:border-slate-500"
          />
        )}
        <div className="mt-1 flex items-center justify-end gap-2">
          {request.kind !== "alert" && (
            <button
              type="button"
              data-testid="dialog-cancel"
              onClick={cancel}
              className="rounded px-3 py-1.5 text-sm text-slate-500 hover:bg-slate-100"
            >
              {request.cancelLabel ?? t("common.cancel")}
            </button>
          )}
          <button
            type="button"
            data-testid="dialog-accept"
            onClick={accept}
            className={
              "rounded px-3 py-1.5 text-sm font-medium text-white " +
              (request.danger
                ? "bg-rose-600 hover:bg-rose-500"
                : "bg-slate-900 hover:bg-slate-700")
            }
          >
            {acceptLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
