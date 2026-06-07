/**
 * Keyboard-shortcut cheat sheet overlay. Toggled with ``?``; closed
 * with Esc / backdrop click / × button. Extracted from ``App.tsx``
 * (v0.16.2).
 */
export function HelpCheatsheet({ onClose }: { onClose: () => void }) {
  const items: [string, string][] = [
    ["⌘/Ctrl + Z", "Undo (project-wide, auto-switches tab)"],
    ["⌘/Ctrl + Shift + Z", "Redo"],
    ["⌘/Ctrl + Y", "Redo (alt)"],
    ["⌘/Ctrl + C", "Copy selection"],
    ["⌘/Ctrl + V", "Paste"],
    ["⌘/Ctrl + D", "Duplicate selection"],
    ["⌘/Ctrl + A", "Select all"],
    ["Delete / Backspace", "Delete selected nodes"],
    ["Double-click service", "Drill into Service Detail (Overview)"],
    ["Double-click actor_ref", "Jump to Actor canvas target"],
    ["?", "Toggle this help"],
    ["Esc", "Close help"],
  ];
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Keyboard shortcuts"
      className="fixed inset-0 z-50 flex items-center justify-center bg-overlay/40"
      onClick={onClose}
    >
      <div
        className="w-[28rem] max-w-[90vw] overflow-hidden rounded-lg bg-surface shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <h2 className="text-sm font-semibold text-fg-strong">
            Keyboard shortcuts
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded px-2 text-fg-faint hover:bg-surface-subtle"
          >
            ✕
          </button>
        </div>
        <dl className="divide-y divide-line text-xs">
          {items.map(([combo, desc]) => (
            <div key={combo} className="flex items-center gap-3 px-4 py-1.5">
              <dt className="w-36 shrink-0 font-mono text-[11px] text-fg">
                {combo}
              </dt>
              <dd className="text-fg-secondary">{desc}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
}
