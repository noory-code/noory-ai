import { useEffect, useRef } from "react";

export interface ContextMenuItem {
  label: string;
  onSelect: () => void;
  disabled?: boolean;
  danger?: boolean;
  divider?: boolean;
}

export interface SketchContextMenuProps {
  x: number;
  y: number;
  items: ContextMenuItem[];
  onClose: () => void;
}

/**
 * Floating menu anchored at (x, y). Closes on outside click or Esc.
 */
export function SketchContextMenu({ x, y, items, onClose }: SketchContextMenuProps) {
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const onDown = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as globalThis.Node)) {
        onClose();
      }
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [onClose]);

  return (
    <div
      ref={menuRef}
      role="menu"
      // ``fixed`` anchors to the viewport; the ``event.clientX/Y`` we were
      // handed is already viewport-relative, so ``absolute`` (which inherits
      // the nearest positioned ancestor's origin) drifted when the canvas
      // wrapper wasn't at (0,0).
      //
      // ``select-none`` kills the residual text selection that the browser
      // leaves behind when a right-click opens the menu — otherwise item
      // labels can appear pre-highlighted as if the user had dragged across
      // them.
      className="fixed z-50 min-w-[180px] select-none rounded-md border border-line bg-surface py-1 shadow-lg"
      style={{ left: x, top: y }}
      onMouseDown={(e) => {
        // Swallow the mousedown so the underlying pane never starts a box
        // selection or loses the node focus we just used to open the menu.
        e.preventDefault();
      }}
    >
      {items.map((item, idx) =>
        item.divider ? (
          <div key={`div-${idx}`} className="my-1 border-t border-line" />
        ) : (
          <button
            key={item.label}
            type="button"
            role="menuitem"
            disabled={item.disabled}
            onClick={() => {
              if (item.disabled) return;
              item.onSelect();
              onClose();
            }}
            className={`block w-full px-3 py-1.5 text-left text-xs ${
              item.disabled
                ? "cursor-not-allowed text-fg-faint"
                : item.danger
                  ? "text-danger-fg hover:bg-danger-soft"
                  : "text-fg hover:bg-surface-subtle"
            }`}
          >
            {item.label}
          </button>
        ),
      )}
    </div>
  );
}
