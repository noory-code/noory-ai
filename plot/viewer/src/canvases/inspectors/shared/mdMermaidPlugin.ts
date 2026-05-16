/**
 * v0.21.0 Live Preview Stage 2 (D-2026-05-17-D) — mermaid SVG
 * inline decoration for the MdTextarea.
 *
 * Renders ``` ```mermaid``` ``` fenced blocks as SVG widgets below
 * the closing fence. The user keeps editing the source above; the
 * SVG re-renders 200 ms after the last keystroke.
 *
 * Architecture
 * ------------
 *
 * CodeMirror 6 disallows block-level decorations sourced directly
 * from a ``ViewPlugin``. Block decorations must live in a
 * ``StateField`` so they get a chance to participate in the layout
 * pass. We split the work in two:
 *
 *   - ``mermaidDecoField`` — a ``StateField<DecorationSet>`` that
 *     holds the *current* set of widget decorations. It is updated
 *     by a ``setMermaidDecorations`` ``StateEffect`` dispatched
 *     externally (from the ViewPlugin below) and otherwise just
 *     maps over doc changes so existing widgets stay anchored to
 *     their fences.
 *   - ``mermaidDebouncer`` — a ``ViewPlugin`` that, on every
 *     doc-changing update, schedules a 200 ms rebuild that walks
 *     the syntax tree and dispatches a fresh decoration set via
 *     ``setMermaidDecorations``.
 *
 * SSOT invariant: neither piece writes to the document. The doc
 * stays the user's authoritative markdown source; widgets are
 * purely visual.
 */
import { syntaxTree } from "@codemirror/language";
import type { Extension, Range } from "@codemirror/state";
import { StateEffect, StateField } from "@codemirror/state";
import type { DecorationSet, ViewUpdate } from "@codemirror/view";
import { Decoration, EditorView, ViewPlugin, WidgetType } from "@codemirror/view";
import type { SyntaxNode } from "@lezer/common";

import { loadMermaid } from "../../../edit/mermaidLoader";

const DEBOUNCE_MS = 200;

let mermaidIdCounter = 0;
function nextMermaidId(): string {
  mermaidIdCounter += 1;
  return `mmd-${mermaidIdCounter}-${Date.now().toString(36)}`;
}

class MermaidWidget extends WidgetType {
  constructor(readonly code: string) {
    super();
  }

  eq(other: WidgetType): boolean {
    return other instanceof MermaidWidget && other.code === this.code;
  }

  toDOM(): HTMLElement {
    const wrap = document.createElement("div");
    wrap.className =
      "my-2 overflow-auto rounded border border-slate-200 bg-slate-50 p-2";
    wrap.style.maxHeight = "480px";
    wrap.setAttribute("role", "img");
    wrap.setAttribute("aria-label", deriveAriaLabel(this.code));
    wrap.setAttribute("data-mermaid", "pending");
    wrap.contentEditable = "false";

    void this.renderInto(wrap);
    return wrap;
  }

  ignoreEvent(): boolean {
    // The SVG widget must not steal focus / input from the editor.
    return true;
  }

  private async renderInto(wrap: HTMLElement): Promise<void> {
    try {
      const mermaid = await loadMermaid();
      const { svg } = await mermaid.render(nextMermaidId(), this.code);
      if (!wrap.isConnected) return;
      wrap.innerHTML = svg;
      wrap.setAttribute("data-mermaid", "ok");
    } catch (err) {
      if (!wrap.isConnected) return;
      wrap.innerHTML = "";
      wrap.setAttribute("data-mermaid", "error");
      wrap.className =
        "my-2 overflow-auto rounded border border-rose-200 bg-rose-50 p-2 text-[11px] text-rose-700";
      const pre = document.createElement("pre");
      pre.textContent =
        "mermaid error: " + (err instanceof Error ? err.message : String(err));
      wrap.appendChild(pre);
    }
  }
}

function deriveAriaLabel(code: string): string {
  const firstLine = code.split("\n").find((l) => l.trim().length > 0) ?? "diagram";
  return `mermaid diagram: ${firstLine.trim().slice(0, 80)}`;
}

function findChild(node: SyntaxNode, name: string): SyntaxNode | null {
  let child = node.firstChild;
  while (child) {
    if (child.name === name) return child;
    child = child.nextSibling;
  }
  return null;
}

function buildDecorations(view: EditorView): DecorationSet {
  const widgets: Range<Decoration>[] = [];
  const tree = syntaxTree(view.state);
  tree.iterate({
    enter(node) {
      if (node.name !== "FencedCode") return;
      const infoNode = findChild(node.node, "CodeInfo");
      if (!infoNode) return;
      const info = view.state.sliceDoc(infoNode.from, infoNode.to).trim();
      if (info !== "mermaid") return;
      const textNode = findChild(node.node, "CodeText");
      if (!textNode) return;
      const code = view.state.sliceDoc(textNode.from, textNode.to);
      widgets.push(
        Decoration.widget({
          widget: new MermaidWidget(code),
          side: 1,
          block: true,
        }).range(node.to),
      );
    },
  });
  return Decoration.set(widgets, true);
}

const setMermaidDecorations = StateEffect.define<DecorationSet>();

const mermaidDecoField = StateField.define<DecorationSet>({
  create(): DecorationSet {
    return Decoration.none;
  },
  update(value, tr): DecorationSet {
    let next = value;
    if (tr.docChanged) next = next.map(tr.changes);
    for (const effect of tr.effects) {
      if (effect.is(setMermaidDecorations)) {
        next = effect.value;
      }
    }
    return next;
  },
  provide: (f) => EditorView.decorations.from(f),
});

const mermaidDebouncer = ViewPlugin.fromClass(
  class {
    private pending: number | null = null;

    constructor(view: EditorView) {
      // Initial build: schedule asynchronously so the initial doc has a
      // parsed syntax tree by the time we walk it.
      this.scheduleRebuild(view, 0);
    }

    update(u: ViewUpdate): void {
      if (!u.docChanged) return;
      this.scheduleRebuild(u.view, DEBOUNCE_MS);
    }

    private scheduleRebuild(view: EditorView, ms: number): void {
      if (this.pending !== null) {
        window.clearTimeout(this.pending);
      }
      this.pending = window.setTimeout(() => {
        this.pending = null;
        const decos = buildDecorations(view);
        view.dispatch({ effects: setMermaidDecorations.of(decos) });
      }, ms);
    }

    destroy(): void {
      if (this.pending !== null) {
        window.clearTimeout(this.pending);
        this.pending = null;
      }
    }
  },
);

/**
 * Composite extension: register both the state field (which provides
 * the decorations to the editor) and the debouncer (which rebuilds
 * them on doc changes). Consumers spread this into their
 * ``EditorState.create({ extensions: [...] })`` array.
 */
export const mdMermaidPlugin: Extension = [mermaidDecoField, mermaidDebouncer];
