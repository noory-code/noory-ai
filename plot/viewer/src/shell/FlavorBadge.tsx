/**
 * Build-flavor badge. Renders a "DEBUG" chip next to the PLOT wordmark
 * ONLY in the debug flavor; the release bundle shows nothing.
 *
 * Gated by the same BUILD-TIME flag as the debug probe
 * (``debugEnabled()`` → ``VITE_PLOT_DEBUG === "1"``, D-2026-06-09-D), so
 * there is no runtime escape hatch — a release build can never light it up.
 * Mirrors the hardcoded technical labels next to it (PLOT / "MCP: live"):
 * a build identifier, not localizable product copy, so it stays out of i18n.
 */
import { debugEnabled } from "../lib/debugProbe";

export function FlavorBadge() {
  if (!debugEnabled()) return null;
  return (
    <span
      className="rounded border border-warn-line bg-warn-soft px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-warn-fg"
      title="Debug build — not a release flavor"
    >
      DEBUG
    </span>
  );
}
