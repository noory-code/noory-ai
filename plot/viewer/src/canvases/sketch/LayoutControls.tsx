/**
 * RF Control buttons for auto-layout. v0.28.3 (D-2026-05-30-F);
 * direction toggle v0.40.3 (D-2026-06-03-C).
 *
 * Rendered as children of React Flow's ``<Controls>``. Owns the ⊞
 * auto-layout button and — on ServiceDetail (``showDirectionSwitch``)
 * — a SINGLE direction toggle that shows the current layout direction
 * (↔ horizontal / ↕ vertical, derived from the subject edge handle via
 * ``detectAnchorDirection``) and flips horizontal ↔ vertical on click.
 * Replaces the two separate ↔/↕ buttons, which gave no indication of
 * the current direction (user 2026-06-03). Extracted out of SketchCanvas
 * so the wiring doesn't grow the god component past its LOC ceiling.
 */
import { ControlButton } from "reactflow";
import { useTranslation } from "react-i18next";
import type { CanvasDoc } from "../../types";
import {
  detectAnchorDirection,
  type AnchorDirection,
} from "../../flow/actorAnchoredLayout";

interface LayoutControlsProps {
  layoutAlgo: "tree" | "radial" | null | undefined;
  showDirectionSwitch?: boolean;
  /** Current canvas doc — read for the active layout direction (its
   *  subject edge handle is the SSOT). */
  doc?: CanvasDoc;
  onLayout: () => void;
  onDirection: (direction: AnchorDirection) => void;
}

export function LayoutControls({
  layoutAlgo,
  showDirectionSwitch,
  doc,
  onLayout,
  onDirection,
}: LayoutControlsProps) {
  const { t } = useTranslation();
  if (!layoutAlgo) return null;
  // Current direction from the subject edge handle (null = not yet
  // wired → treat as horizontal default). The toggle flips to the other
  // axis and always targets LR / TB (the two canonical directions).
  const current = doc ? detectAnchorDirection(doc) : null;
  const horizontal = current === null || current === "LR" || current === "RL";
  const next: AnchorDirection = horizontal ? "TB" : "LR";
  const label = horizontal ? t("canvas.layoutNowLR") : t("canvas.layoutNowTB");
  return (
    <>
      <ControlButton onClick={onLayout} aria-label={t("canvas.autoLayout")} title={t("canvas.autoLayout")}>
        ⊞
      </ControlButton>
      {showDirectionSwitch && (
        <ControlButton onClick={() => onDirection(next)} aria-label={label} title={label}>
          {horizontal ? "↔" : "↕"}
        </ControlButton>
      )}
    </>
  );
}
