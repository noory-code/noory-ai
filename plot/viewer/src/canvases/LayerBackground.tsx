import { useViewport } from "reactflow";

/**
 * Two-layer background overlay. See PHILOSOPHY.md P7.
 *
 * Upper band (flow y < 0) — sky, for Services.
 * Lower band (flow y > 0) — rose, for Actors.
 *
 * The divider line follows the viewport's transform so flow coordinates
 * line up with on-screen colour zones regardless of pan or zoom.
 *
 * Rendered behind nodes/edges (pointer-events: none) so it never
 * intercepts clicks.
 */
export function LayerBackground() {
  const viewport = useViewport();
  // Flow y = 0 maps to screen y = viewport.y (after React Flow's transform).
  const dividerScreenY = viewport.y;

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {/* Upper band — Services */}
      <div
        className="absolute inset-x-0 bg-sky-50/70"
        style={{ top: 0, height: Math.max(dividerScreenY, 0) }}
      />
      {/* Divider */}
      <div
        className="absolute inset-x-0 border-t border-dashed border-slate-300"
        style={{ top: dividerScreenY }}
      />
      {/* Lower band — Actors */}
      <div
        className="absolute inset-x-0 bg-rose-50/70"
        style={{ top: Math.max(dividerScreenY, 0), bottom: 0 }}
      />
      {/* Vertical labels (fixed to viewport edge, don't transform) */}
      <div className="absolute left-2 top-6 text-[10px] font-semibold uppercase tracking-[0.25em] text-sky-700">
        <div style={{ writingMode: "vertical-rl", transform: "rotate(180deg)" }}>
          Services
        </div>
      </div>
      <div className="absolute bottom-6 left-2 text-[10px] font-semibold uppercase tracking-[0.25em] text-rose-700">
        <div style={{ writingMode: "vertical-rl", transform: "rotate(180deg)" }}>
          Actors
        </div>
      </div>
    </div>
  );
}
