/**
 * App-shell keyboard shortcuts: undo / redo / ``?`` help toggle / Esc.
 * Extracted from ``App.tsx`` (v0.16.5).
 *
 * Listens on ``window``; skips when focus is in an editable field.
 * The caller supplies handlers + the ``helpOpen`` state so Esc only
 * closes the help overlay when it's visible.
 */
import { useEffect } from "react";

interface UseAppKeyboardArgs {
  onUndo: () => void;
  onRedo: () => void;
  helpOpen: boolean;
  setHelpOpen: (next: boolean | ((prev: boolean) => boolean)) => void;
}

function isEditableTarget(target: EventTarget | null): boolean {
  const el = target as HTMLElement | null;
  if (!el) return false;
  return (
    el.tagName === "INPUT" ||
    el.tagName === "TEXTAREA" ||
    el.isContentEditable
  );
}

export function useAppKeyboard({
  onUndo,
  onRedo,
  helpOpen,
  setHelpOpen,
}: UseAppKeyboardArgs): void {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (isEditableTarget(e.target)) return;
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key === "z" && !e.shiftKey) {
        e.preventDefault();
        onUndo();
        return;
      }
      if (mod && ((e.key === "z" && e.shiftKey) || e.key === "y")) {
        e.preventDefault();
        onRedo();
        return;
      }
      // ``?`` without modifiers → toggle help.
      if (!mod && !e.altKey && (e.key === "?" || (e.shiftKey && e.key === "/"))) {
        e.preventDefault();
        setHelpOpen((v) => !v);
        return;
      }
      if (!mod && e.key === "Escape" && helpOpen) {
        e.preventDefault();
        setHelpOpen(false);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onUndo, onRedo, helpOpen, setHelpOpen]);
}
