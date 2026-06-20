/**
 * Pointer-based stencil drag channel (D-2026-06-13-C).
 *
 * WHY THIS EXISTS. The stencil used HTML5 drag-and-drop (`draggable` +
 * `dataTransfer` + `onDrop`). WKWebView — the bundled Tauri `.app`, which
 * is Plot's only product surface now — does not fire `dragstart` / `drop`,
 * so stencil drops created no node on ANY canvas. Confirmed in-app via the
 * debug channel (nodeCount never changed on a top-level drop). This channel
 * replaces HTML5 DnD with `pointerdown` on the stencil item + a window-level
 * `pointerup` that routes to whichever registered canvas pane the pointer
 * was released over. Works identically in WKWebView and Chromium.
 *
 * WHAT IS UNCHANGED. The "what happens on drop" logic (hit-test, nudge,
 * resolveDropTarget, addNodeAt / addNestedNodeAt, ref picker) stays in
 * `useDragAndDrop`; this only changes how the drag gesture is captured.
 * The drop target registers a `place(preset, clientX, clientY)` callback.
 */
import {
  createContext,
  type PointerEvent as ReactPointerEvent,
  type ReactNode,
  type RefObject,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import type { StencilPreset } from "../SketchStencil";

type PlaceFn = (preset: StencilPreset, clientX: number, clientY: number) => void;

interface DropTarget {
  paneRef: RefObject<HTMLElement | null>;
  place: PlaceFn;
}

interface StencilDragApi {
  beginDrag: (preset: StencilPreset, event: ReactPointerEvent) => void;
  registerDropTarget: (target: DropTarget) => () => void;
}

const StencilDragCtx = createContext<StencilDragApi | null>(null);

interface ActiveDrag {
  preset: StencilPreset;
  x: number;
  y: number;
}

export function StencilDragProvider({ children }: { children: ReactNode }) {
  // Registered drop targets, in registration order. Last-registered (e.g.
  // the feature modal, mounted over the main canvas) is tried first.
  const targetsRef = useRef<DropTarget[]>([]);
  // ``active`` drives the ghost render; ``activeRef`` is the synchronous
  // source of truth for the window pointerup handler. The ref is set in the
  // SAME tick as ``beginDrag`` (not via the render that ``setActive``
  // schedules) so a release that lands before React re-renders still reads
  // the dragged preset.
  const [active, setActive] = useState<ActiveDrag | null>(null);
  const activeRef = useRef<ActiveDrag | null>(null);

  const registerDropTarget = useCallback((target: DropTarget) => {
    targetsRef.current = [...targetsRef.current, target];
    return () => {
      targetsRef.current = targetsRef.current.filter((t) => t !== target);
    };
  }, []);

  const beginDrag = useCallback(
    (preset: StencilPreset, event: ReactPointerEvent) => {
      // Left button only; ignore secondary / touch-contextmenu starts.
      if (event.button !== 0) return;
      event.preventDefault();
      const drag: ActiveDrag = { preset, x: event.clientX, y: event.clientY };
      activeRef.current = drag;
      setActive(drag);

      const onMove = (e: PointerEvent) => {
        setActive((prev) => (prev ? { ...prev, x: e.clientX, y: e.clientY } : prev));
      };
      const cleanup = () => {
        window.removeEventListener("pointermove", onMove);
        window.removeEventListener("pointerup", onUp);
        window.removeEventListener("pointercancel", onCancel);
        activeRef.current = null;
        setActive(null);
      };
      // ``pointercancel`` (OS gesture takeover, context menu, lost capture)
      // ends the drag with no placement — without it the listeners + ghost
      // would leak.
      const onCancel = () => cleanup();
      const onUp = (e: PointerEvent) => {
        const dragged = activeRef.current;
        // Two candidate drop nodes, because neither is reliable alone:
        //   - WebKit (WKWebView — Plot's only product surface) implicitly
        //     captures the pointer to the stencil item, so ``e.target`` is
        //     the SOURCE, not the element under the release point;
        //     ``elementFromPoint`` ignores capture and gives the real one.
        //   - jsdom's ``elementFromPoint`` returns ``<body>`` (not the
        //     pane), so the unit tests rely on ``e.target``.
        // A pane matches if it contains EITHER candidate (D-2026-06-13-C).
        const fromPoint =
          typeof document.elementFromPoint === "function"
            ? (document.elementFromPoint(e.clientX, e.clientY) as Node | null)
            : null;
        const tgt = e.target as Node | null;
        cleanup();
        if (!dragged) return;
        // Reverse order: a pane mounted later (modal) wins over the main
        // canvas behind it.
        for (let i = targetsRef.current.length - 1; i >= 0; i--) {
          const pane = targetsRef.current[i].paneRef.current;
          if (!pane) continue;
          if ((fromPoint && pane.contains(fromPoint)) || (tgt && pane.contains(tgt))) {
            targetsRef.current[i].place(dragged.preset, e.clientX, e.clientY);
            return;
          }
        }
      };
      window.addEventListener("pointermove", onMove);
      window.addEventListener("pointerup", onUp);
      window.addEventListener("pointercancel", onCancel);
    },
    [],
  );

  return (
    <StencilDragCtx.Provider value={{ beginDrag, registerDropTarget }}>
      {children}
      {active && (
        <div
          aria-hidden
          className="pointer-events-none fixed z-[1000] -translate-x-1/2 -translate-y-1/2 rounded border border-line bg-surface px-2 py-1 text-xs text-fg shadow-md"
          style={{ left: active.x, top: active.y }}
        >
          {active.preset.labelHint ?? active.preset.kind ?? "node"}
        </div>
      )}
    </StencilDragCtx.Provider>
  );
}

// No-op fallback so the shared stencil / canvas leaves render in isolation
// (unit tests, Storybook-style harnesses) without a provider. The real app
// always mounts <StencilDragProvider> at the App root, so drag is live there.
const NOOP_API: StencilDragApi = {
  beginDrag: () => {},
  registerDropTarget: () => () => {},
};

function useStencilDragApi(): StencilDragApi {
  return useContext(StencilDragCtx) ?? NOOP_API;
}

/** Drag source — call ``beginDrag(preset, e)`` from a stencil item's
 *  ``onPointerDown``. */
export function useStencilDrag(): { beginDrag: StencilDragApi["beginDrag"] } {
  const { beginDrag } = useStencilDragApi();
  return { beginDrag };
}

/** Drop target — register a canvas pane + its placement callback. The
 *  channel calls ``place(preset, clientX, clientY)`` when a drag is
 *  released with the pointer over ``paneRef``. */
export function useStencilDropTarget(
  paneRef: RefObject<HTMLElement | null>,
  place: PlaceFn,
): void {
  const { registerDropTarget } = useStencilDragApi();
  // Keep the latest place callback without re-registering every render.
  const placeRef = useRef(place);
  placeRef.current = place;
  useEffect(() => {
    const unregister = registerDropTarget({
      paneRef,
      place: (preset, x, y) => placeRef.current(preset, x, y),
    });
    return unregister;
  }, [registerDropTarget, paneRef]);
}
