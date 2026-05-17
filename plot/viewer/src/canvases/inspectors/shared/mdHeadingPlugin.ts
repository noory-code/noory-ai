/**
 * v0.24.0 Live Preview Stage 3 (D-2026-05-17-L) — heading font-size
 * decoration for the MdTextarea.
 *
 * Walks the markdown syntax tree for ATXHeading1-6 nodes and tags each
 * line with a ``cm-md-h{N}`` class. A theme rule scales font-size
 * proportionally so headings look like headings while the user keeps
 * editing the raw ``#`` markers. SSOT invariant — line decorations are
 * visual-only, the document is never mutated.
 *
 * Heading N>3 inherits the base font-size (the SPEC says #-### are the
 * common levels; h4-h6 still pick up bold from the markdown highlight
 * style, just not scaled).
 */
import { syntaxTree } from "@codemirror/language";
import { type Extension, RangeSetBuilder } from "@codemirror/state";
import type { DecorationSet, ViewUpdate } from "@codemirror/view";
import { Decoration, EditorView, ViewPlugin } from "@codemirror/view";

const HEADING_LINE_CLASS: Record<string, string> = {
  ATXHeading1: "cm-md-h1",
  ATXHeading2: "cm-md-h2",
  ATXHeading3: "cm-md-h3",
  ATXHeading4: "cm-md-h4",
  ATXHeading5: "cm-md-h5",
  ATXHeading6: "cm-md-h6",
};

function buildHeadingDecorations(view: EditorView): DecorationSet {
  const builder = new RangeSetBuilder<Decoration>();
  const tree = syntaxTree(view.state);
  tree.iterate({
    enter(node) {
      const cls = HEADING_LINE_CLASS[node.name];
      if (!cls) return;
      const line = view.state.doc.lineAt(node.from);
      builder.add(line.from, line.from, Decoration.line({ class: cls }));
    },
  });
  return builder.finish();
}

const headingViewPlugin = ViewPlugin.fromClass(
  class {
    decorations: DecorationSet;
    constructor(view: EditorView) {
      this.decorations = buildHeadingDecorations(view);
    }
    update(u: ViewUpdate): void {
      if (u.docChanged || u.viewportChanged) {
        this.decorations = buildHeadingDecorations(u.view);
      }
    }
  },
  { decorations: (v) => v.decorations },
);

const headingTheme = EditorView.theme({
  ".cm-md-h1": { fontSize: "1.5em", lineHeight: "1.3", fontWeight: "700" },
  ".cm-md-h2": { fontSize: "1.3em", lineHeight: "1.3", fontWeight: "700" },
  ".cm-md-h3": { fontSize: "1.15em", lineHeight: "1.3", fontWeight: "700" },
  ".cm-md-h4": { fontWeight: "700" },
  ".cm-md-h5": { fontWeight: "700" },
  ".cm-md-h6": { fontWeight: "700" },
});

export const mdHeadingPlugin: Extension = [headingViewPlugin, headingTheme];
