/**
 * RF Control buttons for auto-layout. v0.28.3 (D-2026-05-30-F);
 * direction toggle v0.40.3 (D-2026-06-03-C).
 *
 * Rendered as children of React Flow's ``<Controls>``. Owns the ⊞
 * auto-layout button and — on FeatureDetail (``showDirectionSwitch``)
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

// v0.40.5 (D-2026-06-04-A) — ONE mode-neutral "auto-arrange" mark. ⊞ is an
// ACTION (press → run the layout), not a mode toggle. v0.40.4 gave it a
// mode-shaped icon (tree vs flow) which made it look switchable like the
// direction toggle — user 2026-06-04: *"그걸 누르면 왜 정렬이 변하냐고"*.
// The mode now lives only in the tooltip TEXT (aria-label), never the icon.
// D-2026-06-13-F — fixed near-black stroke (not ``currentColor``). The RF
// Controls bar has a light background in every theme; inheriting the app's
// (light, in dark theme) text colour made the arrange icon invisible.
const ICON = { fill: "none", stroke: "#1a1a1a", strokeWidth: 2, strokeLinecap: "round", strokeLinejoin: "round" } as const;

function ArrangeIcon() {
  // Descending lines = a "tidy / auto-arrange" action mark, neutral to the
  // mind-map-vs-flow distinction (which the canvas decides, not the user).
  return (
    <svg viewBox="0 0 24 24" width="14" height="14" {...ICON}>
      <line x1="4" y1="7" x2="20" y2="7" />
      <line x1="4" y1="12" x2="15" y2="12" />
      <line x1="4" y1="17" x2="10" y2="17" />
    </svg>
  );
}

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
  // ⊞ runs the flow layout on FeatureDetail (the only canvas with a
  // direction switch) and the mind-map tree everywhere else. The icon +
  // label reflect that so the user can tell the mode at a glance.
  const flowMode = showDirectionSwitch === true;
  const layoutLabel = flowMode ? t("canvas.autoLayoutFlow") : t("canvas.autoLayoutTree");
  // Current direction from the subject edge handle (null = not yet
  // wired → treat as horizontal default). The toggle flips to the other
  // axis and always targets LR / TB (the two canonical directions).
  const current = doc ? detectAnchorDirection(doc) : null;
  const horizontal = current === null || current === "LR" || current === "RL";
  const next: AnchorDirection = horizontal ? "TB" : "LR";
  const label = horizontal ? t("canvas.layoutNowLR") : t("canvas.layoutNowTB");
  return (
    <>
      <ControlButton
        onClick={onLayout}
        aria-label={layoutLabel}
        title={layoutLabel}
        data-layout-mode={flowMode ? "flow" : "tree"}
      >
        <ArrangeIcon />
      </ControlButton>
      {showDirectionSwitch && (
        <ControlButton onClick={() => onDirection(next)} aria-label={label} title={label}>
          {horizontal ? "↔" : "↕"}
        </ControlButton>
      )}
    </>
  );
}
