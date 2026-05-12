// Window-level keyboard shortcuts for the canvas. SPEC §Keyboard
// shortcuts owns the canonical combo list; this hook implements
// it. The editable-target guard is load-bearing: without it,
// Cmd+Z inside an Inspector text field would undo the canvas
// document instead of the user's text edit.
//
// Reads ``docRef.current`` and ``selectedNodeIds.current`` directly
// because the listener is attached to ``window`` and fires across
// re-renders — ref-fresh reads are the only way to get the latest
// state without rebinding the listener on every render.
import { type MutableRefObject, useEffect } from "react";
import type { ReactFlowInstance } from "reactflow";
import type { CanvasDoc } from "../../types";
import type { SketchClipboard } from "../useSketchClipboard";

export interface UseKeyboardShortcutsArgs {
  docRef: MutableRefObject<CanvasDoc>;
  flowRef: MutableRefObject<ReactFlowInstance | null>;
  selectedNodeIds: MutableRefObject<string[]>;
  clipboard: SketchClipboard;
  onUndo: () => void;
  onRedo: () => void;
  onDocChange: (next: CanvasDoc) => void;
}

function isEditableTarget(t: EventTarget | null): boolean {
  if (!(t instanceof HTMLElement)) return false;
  const tag = t.tagName;
  return tag === "INPUT" || tag === "TEXTAREA" || t.isContentEditable;
}

export function useKeyboardShortcuts({
  docRef,
  flowRef,
  selectedNodeIds,
  clipboard,
  onUndo,
  onRedo,
  onDocChange,
}: UseKeyboardShortcutsArgs): void {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (isEditableTarget(e.target)) return;
      const meta = e.metaKey || e.ctrlKey;
      if (meta && !e.shiftKey && e.key.toLowerCase() === "z") {
        e.preventDefault();
        onUndo();
        return;
      }
      if (
        (meta && e.shiftKey && e.key.toLowerCase() === "z") ||
        (meta && e.key.toLowerCase() === "y")
      ) {
        e.preventDefault();
        onRedo();
        return;
      }
      if (meta && e.key.toLowerCase() === "c") {
        if (selectedNodeIds.current.length > 0) {
          e.preventDefault();
          clipboard.copy(docRef.current, selectedNodeIds.current);
        }
        return;
      }
      if (meta && e.key.toLowerCase() === "v") {
        if (clipboard.hasClip()) {
          e.preventDefault();
          onDocChange(clipboard.paste(docRef.current));
        }
        return;
      }
      if (meta && e.key.toLowerCase() === "d") {
        if (selectedNodeIds.current.length > 0) {
          e.preventDefault();
          onDocChange(clipboard.duplicate(docRef.current, selectedNodeIds.current));
        }
        return;
      }
      if (meta && e.key.toLowerCase() === "a") {
        e.preventDefault();
        // v0.16.17 (D-2026-05-12-S) — Cmd+A used to call only
        // ``setNodes``/``setEdges`` to flip RF's internal ``selected``
        // flag, which does NOT emit ``onSelectionChange`` → the App's
        // ``selectedNodeIds`` ref stayed stale → next Cmd+C / Cmd+D
        // copied the OLD selection. Fix: sync ``selectedNodeIds.current``
        // alongside the RF store mutation so the controlled-component
        // contract is preserved.
        if (flowRef.current) {
          const inst = flowRef.current;
          const allNodeIds = inst.getNodes().map((n) => n.id);
          inst.setNodes((ns) => ns.map((n) => ({ ...n, selected: true })));
          inst.setEdges((es) => es.map((edge) => ({ ...edge, selected: true })));
          selectedNodeIds.current = allNodeIds;
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [docRef, flowRef, selectedNodeIds, clipboard, onDocChange, onRedo, onUndo]);
}
