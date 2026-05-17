/**
 * v0.24.0 Live Preview Stage 3 (D-2026-05-17-L) — list bullet glyph
 * decoration for the MdTextarea.
 *
 * Replaces the leading ``-`` / ``*`` / ``+`` of bullet list items with
 * a styled bullet ``•`` via a Mark decoration. The ``ListMark`` node
 * span in the markdown syntax tree carries exactly the raw marker
 * (1 char), so this is a 1-char replacement per item.
 *
 * Ordered lists (``1.``) are not touched — their numerals already read
 * as list markers visually.
 *
 * SSOT invariant — the doc is never mutated; the bullet is rendered via
 * a CSS ``::before`` injected by a class on the mark.
 */
import { syntaxTree } from "@codemirror/language";
import { type Extension, RangeSetBuilder } from "@codemirror/state";
import type { DecorationSet, ViewUpdate } from "@codemirror/view";
import { Decoration, EditorView, ViewPlugin } from "@codemirror/view";

class BulletWidget {
  // Mark decoration just adds a class on the original character; we
  // hide the raw marker via CSS and paint a bullet glyph via ::before.
}
void BulletWidget; // referenced for symmetry; not exported

function buildListDecorations(view: EditorView): DecorationSet {
  const builder = new RangeSetBuilder<Decoration>();
  const tree = syntaxTree(view.state);
  tree.iterate({
    enter(node) {
      if (node.name !== "ListMark") return;
      // Parent BulletList = unordered. Parent OrderedList = numerals;
      // skip those (1. / 2. read naturally).
      const parent = node.node.parent;
      if (!parent || parent.name !== "BulletList") return;
      const text = view.state.sliceDoc(node.from, node.to);
      if (text !== "-" && text !== "*" && text !== "+") return;
      builder.add(
        node.from,
        node.to,
        Decoration.mark({ class: "cm-md-bullet" }),
      );
    },
  });
  return builder.finish();
}

const listViewPlugin = ViewPlugin.fromClass(
  class {
    decorations: DecorationSet;
    constructor(view: EditorView) {
      this.decorations = buildListDecorations(view);
    }
    update(u: ViewUpdate): void {
      if (u.docChanged || u.viewportChanged) {
        this.decorations = buildListDecorations(u.view);
      }
    }
  },
  { decorations: (v) => v.decorations },
);

const listTheme = EditorView.theme({
  ".cm-md-bullet": {
    color: "transparent",
    position: "relative",
  },
  ".cm-md-bullet::before": {
    content: "'•'",
    color: "rgb(100 116 139)" /* slate-500 */,
    position: "absolute",
    left: "0",
    top: "0",
    fontWeight: "700",
  },
});

export const mdListPlugin: Extension = [listViewPlugin, listTheme];
