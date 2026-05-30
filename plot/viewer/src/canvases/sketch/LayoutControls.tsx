/**
 * RF Control buttons for auto-layout. v0.28.3 (D-2026-05-30-F).
 *
 * Rendered as children of React Flow's ``<Controls>``. Owns the ⊞
 * auto-layout button and — on ServiceDetail (``showDirectionSwitch``)
 * — the LR (↔) / TB (↕) direction-switch buttons. Extracted out of
 * SketchCanvas so the direction-switch wiring doesn't grow the god
 * component past its LOC ceiling (Gate 2).
 */
import { ControlButton } from "reactflow";
import { useTranslation } from "react-i18next";
import type { AnchorDirection } from "../../flow/actorAnchoredLayout";

interface LayoutControlsProps {
  layoutAlgo: "tree" | "radial" | null | undefined;
  showDirectionSwitch?: boolean;
  onLayout: () => void;
  onDirection: (direction: AnchorDirection) => void;
}

export function LayoutControls({
  layoutAlgo,
  showDirectionSwitch,
  onLayout,
  onDirection,
}: LayoutControlsProps) {
  const { t } = useTranslation();
  if (!layoutAlgo) return null;
  return (
    <>
      <ControlButton onClick={onLayout} aria-label={t("canvas.autoLayout")} title={t("canvas.autoLayout")}>
        ⊞
      </ControlButton>
      {showDirectionSwitch && (
        <>
          <ControlButton
            onClick={() => onDirection("LR")}
            aria-label={t("canvas.layoutLR")}
            title={t("canvas.layoutLR")}
          >
            ↔
          </ControlButton>
          <ControlButton
            onClick={() => onDirection("TB")}
            aria-label={t("canvas.layoutTB")}
            title={t("canvas.layoutTB")}
          >
            ↕
          </ControlButton>
        </>
      )}
    </>
  );
}
