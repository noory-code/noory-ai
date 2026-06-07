import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useTranslation } from "react-i18next";

/**
 * ⓘ button + click popover showing a stencil section's concept definition.
 * D-2026-06-06-A — Foundation stencil concept info. Always-visible icon
 * (discoverable); opens on click (works on touch, unlike hover). Concept
 * SSOT = docs/FOUNDATION_CONCEPT.md.
 *
 * The popover is portaled to ``document.body`` and positioned with fixed
 * coords from the button rect, so the stencil's ``overflow-y-auto`` scroll
 * container cannot clip it (the narrow sidebar would otherwise cut it off).
 */
const POPOVER_WIDTH = 224; // w-56

export function SectionInfo({ text }: { text: string }) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState<{ top: number; left: number } | null>(null);
  const btnRef = useRef<HTMLButtonElement>(null);
  const popRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDocMouseDown = (e: MouseEvent): void => {
      const tgt = e.target as Node;
      if (btnRef.current?.contains(tgt) || popRef.current?.contains(tgt)) return;
      setOpen(false);
    };
    document.addEventListener("mousedown", onDocMouseDown);
    return () => document.removeEventListener("mousedown", onDocMouseDown);
  }, [open]);

  const toggle = (): void => {
    if (open) {
      setOpen(false);
      return;
    }
    const r = btnRef.current?.getBoundingClientRect();
    if (r) {
      // Clamp so the popover never runs off the right viewport edge.
      const left = Math.min(r.left, window.innerWidth - POPOVER_WIDTH - 8);
      setPos({ top: r.bottom + 4, left: Math.max(8, left) });
    }
    setOpen(true);
  };

  return (
    <>
      <button
        ref={btnRef}
        type="button"
        aria-label={t("stencil.infoAria")}
        onClick={toggle}
        className="flex h-3.5 w-3.5 items-center justify-center rounded-full border border-line-strong text-[8px] font-bold leading-none text-fg-faint hover:border-line-strong hover:text-fg-secondary"
      >
        i
      </button>
      {open &&
        pos &&
        createPortal(
          <div
            ref={popRef}
            role="dialog"
            style={{ position: "fixed", top: pos.top, left: pos.left, width: POPOVER_WIDTH }}
            className="z-[100] rounded-md border border-line bg-surface p-2 text-[10px] font-normal normal-case leading-snug tracking-normal text-fg-secondary shadow-lg"
          >
            {text}
          </div>,
          document.body,
        )}
    </>
  );
}
