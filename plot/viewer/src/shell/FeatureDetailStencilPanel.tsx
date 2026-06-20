/**
 * FeatureDetailStencilPanel — modal-internal stencil column.
 *
 * Per D-2026-05-26-D: the FeatureDetail modal is self-contained.
 * Its left column is this component (drag sources for actors / refs /
 * composition). The main app sidebar no longer swaps to the
 * feature stencil when the modal is open — the modal owns
 * its own controls so it can sit on top of the main canvas without
 * fighting for the same sidebar real estate.
 *
 * v0.27.11 (D-2026-05-28-F): the main sidebar is inert while the
 * modal is open, so its EN/KO toggle is unreachable. The modal hosts
 * its own ``<LanguageToggle/>`` at the bottom of this panel so the
 * user can flip locale without closing the modal.
 *
 * Width / chrome mirror the main ``SketchSidebar``'s stencil region
 * (``w-56 border-r border-line bg-surface``) so the two stencil
 * columns read as the same component family.
 */
import { LanguageToggle } from "../i18n/LanguageToggle";
import { ThemeToggle } from "./ThemeToggle";
import { SketchStencil } from "../canvases/SketchStencil";
import type { SketchNode } from "../types";

interface FeatureDetailStencilPanelProps {
  availableActors: SketchNode[];
}

export function FeatureDetailStencilPanel({ availableActors }: FeatureDetailStencilPanelProps) {
  return (
    <aside className="flex h-full w-56 shrink-0 flex-col overflow-y-auto border-r border-line bg-surface">
      <div className="flex-1">
        <SketchStencil canvas="feature" availableActors={availableActors} />
      </div>
      <div className="flex items-center justify-end gap-2 border-t border-line px-3 py-2">
        <ThemeToggle />
        <LanguageToggle />
      </div>
    </aside>
  );
}
