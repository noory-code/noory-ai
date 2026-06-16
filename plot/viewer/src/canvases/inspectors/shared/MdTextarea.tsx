/**
 * v0.19.0 Phase MD-editor stage 1 (D-2026-05-17-B) — drop-in MD-aware
 * editor for typed-text fields in the Inspector.
 *
 * CodeMirror 6 + ``@codemirror/lang-markdown`` provides syntax highlight
 * for headings / lists / bold / italic / code / links / blockquotes.
 * raw MD remains the SSOT in JSON — this component never transforms
 * the value, only re-paints it. Decoration widgets (mermaid SVG /
 * heading font-size / list bullet styling) are reserved for v0.20.0
 * (mermaid) and v0.21.0 (live-preview-complete).
 *
 * Mirrors the prop signature of the previous monospace ``<textarea>``
 * so callers swap in via one-line substitution.
 */
import { defaultKeymap, history, historyKeymap, indentWithTab } from "@codemirror/commands";
import { markdown } from "@codemirror/lang-markdown";
import { syntaxHighlighting, defaultHighlightStyle } from "@codemirror/language";
import { EditorState } from "@codemirror/state";
import { EditorView, highlightSpecialChars, keymap } from "@codemirror/view";
import { useEffect, useRef } from "react";

import { mdHeadingPlugin } from "./mdHeadingPlugin";
import { mdImagePlugin } from "./mdImagePlugin";
import { mdListPlugin } from "./mdListPlugin";
import { mdMermaidPlugin } from "./mdMermaidPlugin";

export interface MdTextareaProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  minLines?: number;
}

// D-2026-06-16-E — theme via Plot's CSS tokens (``rgb(var(--…))``) so the
// editor follows light/dark like the rest of the app. A hardcoded white
// surface + slate/indigo border literals made it a white island in dark mode.
// CSS vars resolve against the element's computed style, which inherits the
// ``.dark`` class on <html>.
const baseTheme = EditorView.theme({
  "&": {
    fontSize: "13px",
    fontFamily:
      "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace",
    borderRadius: "0.25rem",
    border: "1px solid rgb(var(--line-strong))",
    backgroundColor: "rgb(var(--surface))",
    color: "rgb(var(--fg))",
  },
  "&.cm-focused": {
    outline: "none",
    borderColor: "rgb(var(--accent))",
  },
  ".cm-content": {
    padding: "0.25rem 0.5rem",
    caretColor: "rgb(var(--fg))",
  },
  ".cm-cursor, .cm-dropCursor": {
    borderLeftColor: "rgb(var(--fg))",
  },
  "&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection":
    {
      backgroundColor: "rgb(var(--accent-soft))",
    },
  ".cm-line": {
    padding: "0 2px",
  },
  ".cm-scroller": {
    fontFamily: "inherit",
  },
});

export function MdTextarea({
  value,
  onChange,
  placeholder,
  minLines = 2,
}: MdTextareaProps) {
  const parentRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  // Mount: create EditorView once.
  useEffect(() => {
    if (!parentRef.current) return;
    const state = EditorState.create({
      doc: value,
      extensions: [
        history(),
        markdown(),
        EditorView.lineWrapping,
        syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
        highlightSpecialChars(),
        keymap.of([...defaultKeymap, ...historyKeymap, indentWithTab]),
        mdMermaidPlugin,
        mdHeadingPlugin,
        mdListPlugin,
        mdImagePlugin,
        baseTheme,
        EditorView.contentAttributes.of({
          "aria-label": placeholder ?? "Markdown editor",
        }),
        EditorView.updateListener.of((u) => {
          if (u.docChanged) {
            onChangeRef.current(u.state.doc.toString());
          }
        }),
      ],
    });
    const view = new EditorView({ state, parent: parentRef.current });
    viewRef.current = view;
    return () => {
      view.destroy();
      viewRef.current = null;
    };
    // The placeholder + minLines are static-on-mount; we re-mount only
    // when the consumer re-mounts the MdTextarea (e.g. switching to a
    // different node id in the Inspector tree, which is the natural
    // unit of reset).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // External value-prop sync: if the parent re-renders MdTextarea with
  // a new ``value`` that differs from the editor's current doc, dispatch
  // a replace transaction. Skip when they match to avoid the update
  // loop (every onChange already feeds the parent → re-renders with
  // the same value).
  useEffect(() => {
    const view = viewRef.current;
    if (!view) return;
    const current = view.state.doc.toString();
    if (current === value) return;
    view.dispatch({
      changes: { from: 0, to: current.length, insert: value },
    });
  }, [value]);

  const minHeightPx = Math.max(minLines, 1) * 20 + 8;

  return (
    <div
      className="mt-1 w-full"
      style={{ minHeight: `${minHeightPx}px` }}
      data-md-textarea
    >
      <div ref={parentRef} />
      {/* RTL ``getByDisplayValue`` mirror — CodeMirror renders its
       *  editor as ``<div contenteditable>`` which RTL form-field
       *  queries don't index. The hidden read-only textarea keeps the
       *  testing surface intact without affecting visible behaviour
       *  (sr-only hides it from sight + screen readers; tabIndex=-1
       *  removes it from keyboard navigation). */}
      <textarea
        value={value}
        readOnly
        tabIndex={-1}
        aria-hidden
        className="sr-only"
        onFocus={() => {
          /* If focus lands here (e.g. Playwright synthetic click quirk or
           * browser fallback), redirect it to the CM editor immediately. */
          viewRef.current?.focus();
        }}
        onChange={() => {
          /* read-only mirror; CodeMirror owns input */
        }}
      />
    </div>
  );
}
