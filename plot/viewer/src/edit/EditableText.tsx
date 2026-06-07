import { useCallback, useEffect, useRef, useState } from "react";

export interface EditableTextProps {
  value: string;
  onCommit: (next: string) => void;
  placeholder?: string;
  className?: string;
  inputClassName?: string;
  ariaLabel: string;
  multiline?: boolean;
}

/**
 * Click to enter edit mode. Enter commits, Esc cancels, blur commits.
 *
 * When ``multiline`` is true, renders a textarea and Ctrl/Cmd+Enter commits
 * while plain Enter inserts a newline.
 */
export function EditableText({
  value,
  onCommit,
  placeholder,
  className,
  inputClassName,
  ariaLabel,
  multiline,
}: EditableTextProps) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value);
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement | null>(null);

  useEffect(() => {
    setDraft(value);
  }, [value]);

  useEffect(() => {
    if (editing && inputRef.current) {
      inputRef.current.focus();
      if (inputRef.current instanceof HTMLInputElement) {
        inputRef.current.select();
      }
    }
  }, [editing]);

  const commit = useCallback(() => {
    if (draft !== value) onCommit(draft);
    setEditing(false);
  }, [draft, value, onCommit]);

  const cancel = useCallback(() => {
    setDraft(value);
    setEditing(false);
  }, [value]);

  if (!editing) {
    const hasValue = value && value.trim().length > 0;
    // No ``nodrag`` here — React Flow's ``nodeDragThreshold`` on the canvas
    // distinguishes a click from a drag by mouse-move distance, so the user
    // can still drag from the label without losing the click-to-edit affordance.
    //
    // Cursor inherits from .react-flow__node (RF default = ``grab``)
    // per D-2026-05-10-C. Click activates the input below, which has
    // the browser-native ``text`` cursor.
    return (
      <span
        className={className ?? ""}
        role="button"
        tabIndex={0}
        aria-label={`${ariaLabel}. Click to edit.`}
        onClick={(e) => {
          e.stopPropagation();
          setEditing(true);
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            setEditing(true);
          }
        }}
      >
        {hasValue ? value : <span className="italic text-fg-faint">{placeholder ?? ""}</span>}
      </span>
    );
  }

  const shared = {
    value: draft,
    onChange: (e: { target: { value: string } }) => setDraft(e.target.value),
    onBlur: commit,
    onKeyDown: (e: React.KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        cancel();
      } else if (e.key === "Enter") {
        if (!multiline || e.metaKey || e.ctrlKey) {
          e.preventDefault();
          commit();
        }
      }
    },
    "aria-label": ariaLabel,
    className:
      inputClassName ??
      "w-full rounded border border-accent bg-surface px-1.5 py-0.5 text-sm focus:border-accent focus:outline-none",
  };

  if (multiline) {
    return (
      <textarea
        {...shared}
        ref={(el) => {
          inputRef.current = el;
        }}
        rows={3}
        onClick={(e) => e.stopPropagation()}
      />
    );
  }

  return (
    <input
      type="text"
      {...shared}
      ref={(el) => {
        inputRef.current = el;
      }}
      onClick={(e) => e.stopPropagation()}
    />
  );
}
