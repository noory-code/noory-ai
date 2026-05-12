/**
 * Service-detail modal — overlay that mounts the ServiceDetailCanvas
 * on top of the still-mounted services canvas (v0.12 drill-in pattern).
 * Extracted from ``App.tsx`` (v0.16.3).
 *
 * Esc / backdrop click / × button all call ``onClose``.
 */
import { useEffect, type ReactNode } from "react";
import { useTranslation } from "react-i18next";

interface ServiceDetailModalProps {
  serviceLabel: string;
  categoryLabel: string | null;
  onClose: () => void;
  children: ReactNode;
}

export function ServiceDetailModal({
  serviceLabel,
  categoryLabel,
  onClose,
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
      className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/40"
      onClick={onClose}
    >
      <div
        className="flex h-[90vh] w-[92vw] max-w-[1600px] flex-col overflow-hidden rounded-lg bg-white shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-2">
          <div className="flex items-baseline gap-2">
            <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">
              {t("serviceDetail.label")}
            </span>
            {/* v0.12.6 — show parent category context so users always know
                which group a service belongs to even inside the modal. */}
            {categoryLabel && (
              <>
                <span className="text-xs text-slate-500">{categoryLabel}</span>
                <span className="text-xs text-slate-300">›</span>
              </>
            )}
            <span className="text-sm font-medium text-slate-900">{serviceLabel}</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded px-2 py-1 text-xs text-slate-600 hover:bg-slate-100"
            aria-label={t("shell.closeEsc")}
            title={t("shell.closeEsc")}
          >
            ✕
          </button>
        </header>
        <div className="relative flex-1 overflow-hidden">{children}</div>
      </div>
    </div>
  );
}
