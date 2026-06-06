import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

/**
 * ⓘ button + click popover showing a stencil section's concept definition.
 * D-2026-06-06-A — Foundation stencil concept info. Always-visible icon
 * (discoverable); opens on click (works on touch, unlike hover). Concept
 * SSOT = docs/FOUNDATION_CONCEPT.md.
 */
export function SectionInfo({ text }: { text: string }) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDocMouseDown = (e: MouseEvent): void => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDocMouseDown);
    return () => document.removeEventListener("mousedown", onDocMouseDown);
  }, [open]);

  return (
    <div ref={ref} className="relative inline-flex">
      <button
        type="button"
        aria-label={t("stencil.infoAria")}
        onClick={() => setOpen((o) => !o)}
        className="flex h-3.5 w-3.5 items-center justify-center rounded-full border border-slate-300 text-[8px] font-bold leading-none text-slate-400 hover:border-slate-400 hover:text-slate-600"
      >
        i
      </button>
      {open && (
        <div
          role="dialog"
          className="absolute left-0 top-5 z-50 w-56 rounded-md border border-slate-200 bg-white p-2 text-[10px] font-normal normal-case leading-snug tracking-normal text-slate-600 shadow-lg"
        >
          {text}
        </div>
      )}
    </div>
  );
}
