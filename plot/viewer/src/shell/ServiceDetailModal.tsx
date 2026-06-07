/**
 * Service-detail modal — overlay that mounts the ServiceDetailCanvas
 * on top of the still-mounted services canvas (v0.12 drill-in pattern).
 * Extracted from ``App.tsx`` (v0.16.3).
 *
 * v0.27.1 (D-2026-05-26-D) — modal body is now a 2-column flex row:
 * ``stencilSlot`` on the left (self-contained drag sources), canvas
 * (``children``) on the right. The main app sidebar no longer swaps
 * its stencil when the modal opens; the modal owns its own controls.
 *
 * Esc / backdrop click / × button all call ``onClose``.
 */
import { useEffect, type ReactNode } from "react";
import { useTranslation } from "react-i18next";

interface ServiceDetailModalProps {
  serviceLabel: string;
  categoryLabel: string | null;
  onClose: () => void;
  /** v0.27.1 (D-2026-05-26-D) — left stencil column rendered inside
   *  the modal so the modal is fully self-contained. */
  stencilSlot: ReactNode;
  children: ReactNode;
}

export function ServiceDetailModal({
  serviceLabel,
  categoryLabel,
  onClose,
  stencilSlot,
  children,
}: ServiceDetailModalProps) {
  const { t } = useTranslation();
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={
        categoryLabel
          ? t("serviceDetail.ariaWithCategory", {
              category: categoryLabel,
              service: serviceLabel,
            })
          : t("serviceDetail.ariaWithoutCategory", { service: serviceLabel })
      }
      className="fixed inset-0 z-40 flex items-center justify-center bg-overlay/40"
      onClick={onClose}
    >
      <div
        className="flex h-[92vh] w-[94vw] max-w-[1600px] flex-col overflow-hidden rounded-lg bg-surface shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex items-center justify-between border-b border-line bg-surface-muted px-4 py-2">
          <div className="flex items-baseline gap-2">
            <span className="text-[10px] font-semibold uppercase tracking-wide text-fg-muted">
              {t("serviceDetail.label")}
            </span>
            {/* v0.12.6 — show parent category context so users always know
                which group a service belongs to even inside the modal. */}
            {categoryLabel && (
              <>
                <span className="text-xs text-fg-muted">{categoryLabel}</span>
                <span className="text-xs text-fg-faint">›</span>
              </>
            )}
            <span className="text-sm font-medium text-fg-strong">{serviceLabel}</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded px-2 py-1 text-xs text-fg-secondary hover:bg-surface-subtle"
            aria-label={t("shell.closeEsc")}
            title={t("shell.closeEsc")}
          >
            ✕
          </button>
        </header>
        <div className="flex flex-1 overflow-hidden">
          {stencilSlot}
          <div className="relative flex-1 overflow-hidden">{children}</div>
        </div>
      </div>
    </div>
  );
}
