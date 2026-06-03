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

// v0.40.4 (D-2026-06-03-D) — mode-specific ⊞ glyphs so the user can tell
// what the auto-layout will produce. A hub-and-branches mark for the
// mind-map layout (Foundation / Actors / Services); a left→right node
// sequence for the flow layout (ServiceDetail). User 2026-06-03:
// *"어떤 모드인지 아이콘이 같으니 알 수가 없네"*.
const ICON = { fill: "none", stroke: "currentColor", strokeWidth: 2, strokeLinecap: "round", strokeLinejoin: "round" } as const;

function TreeIcon() {
  return (
    <svg viewBox="0 0 24 24" width="14" height="14" {...ICON}>
      <circle cx="4" cy="12" r="2.5" />
      <circle cx="19" cy="5" r="2" />
      <circle cx="19" cy="12" r="2" />
      <circle cx="19" cy="19" r="2" />
      <path d="M6.4 11 17 5.7 M6.5 12 17 12 M6.4 13 17 18.3" />
    </svg>
  );
}

function FlowIcon() {
  return (
    <svg viewBox="0 0 24 24" width="14" height="14" {...ICON}>
      <rect x="2" y="9" width="6" height="6" rx="1.5" />
      <rect x="16" y="9" width="6" height="6" rx="1.5" />
      <path d="M9 12 H15 M13 10 15 12 13 14" />
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
  // ⊞ runs the flow layout on ServiceDetail (the only canvas with a
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
        {flowMode ? <FlowIcon /> : <TreeIcon />}
      </ControlButton>
      {showDirectionSwitch && (
        <ControlButton onClick={() => onDirection(next)} aria-label={label} title={label}>
          {horizontal ? "↔" : "↕"}
        </ControlButton>
      )}
    </>
  );
}
