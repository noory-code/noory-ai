/**
 * Owns the "Add a Project" directory-picker modal open-state so App.tsx
 * stays flat (v0.34.0, D-2026-05-31-N). Returns the trigger + the modal
 * element; App renders the element once and wires the trigger to the
 * sidebar / empty-state "Add a Project" buttons.
 */
import { useCallback, useState } from "react";
import { DirTreePickerModal } from "../shell/DirTreePickerModal";

export function useDirPicker(args: {
  workspaceRoot: string | null;
  onCreateInDir: (dir: string) => void;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const open = useCallback(() => setIsOpen(true), []);
  const modal = (
    <DirTreePickerModal
      open={isOpen}
      workspaceRoot={args.workspaceRoot}
      onClose={() => setIsOpen(false)}
      onPick={(dir) => {
        setIsOpen(false);
        args.onCreateInDir(dir);
      }}
    />
  );
  return { open, modal };
}
