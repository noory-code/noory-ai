/**
 * Viewer→engine context bridge (D-2026-06-15-D).
 *
 * Reports the viewer's current canvas context (active scope + node selection)
 * to the engine so the external MCP agent can read it via
 * ``get_viewer_context``. One mount in ``App`` over the already-lifted
 * ``[activeScope, selection]`` — a single chokepoint rather than N call sites,
 * so a new selection / nav site can't silently miss the bridge.
 *
 * Two writes:
 *   - **on-change** (debounced ``DEBOUNCE_MS``) so rapid multi-select / nav
 *     coalesces into one POST;
 *   - **heartbeat** (``HEARTBEAT_MS``) so an idle-but-open viewer keeps its
 *     report fresh — the engine's staleness TTL then means "no live viewer",
 *     not merely "the user hasn't clicked recently".
 */
import { useEffect, useMemo, useRef } from "react";

import { reportViewerContext } from "../app/viewer";
import type { ChatScope, ChatSelectionNode } from "../types";

const DEBOUNCE_MS = 150;
const HEARTBEAT_MS = 30_000;

export function useViewerContextBridge(
  workspaceRoot: string | null | undefined,
  scope: ChatScope,
  selection: ChatSelectionNode[],
): void {
  // Content key so the change-effect fires on *what* is selected, not on the
  // new array identity React hands us every render.
  const selectionKey = useMemo(
    () => JSON.stringify(selection.map((n) => [n.id, n.kind, n.label])),
    [selection],
  );

  // Latest values for the heartbeat, which must not re-arm its interval on
  // every change.
  const latest = useRef({ workspaceRoot, scope, selection });
  latest.current = { workspaceRoot, scope, selection };

  // Debounced post on change.
  useEffect(() => {
    if (!workspaceRoot) return;
    const t = setTimeout(() => {
      void reportViewerContext(workspaceRoot, scope, selection).catch(() => {});
    }, DEBOUNCE_MS);
    return () => clearTimeout(t);
    // ``selection`` is represented by ``selectionKey``; depending on the array
    // itself would re-run every render and defeat the debounce.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceRoot, scope, selectionKey]);

  // Heartbeat while mounted.
  useEffect(() => {
    if (!workspaceRoot) return;
    const id = setInterval(() => {
      const l = latest.current;
      if (!l.workspaceRoot) return;
      void reportViewerContext(l.workspaceRoot, l.scope, l.selection).catch(
        () => {},
      );
    }, HEARTBEAT_MS);
    return () => clearInterval(id);
  }, [workspaceRoot]);
}
