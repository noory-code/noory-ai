/**
 * v0.24.0 Live Preview Stage 3 (D-2026-05-17-L) — image embed decoration
 * for the MdTextarea.
 *
 * For every ``![alt](url)`` image link in the doc, render an inline
 * image widget on the line below. The user keeps editing the markdown
 * source above; the image renders / re-renders 200 ms after edits.
 *
 * Source forms handled:
 *   - HTTP(S) URLs: ``![alt](https://...)``
 *   - Relative paths: ``![alt](./img.png)`` — resolved against the
 *     ``project_path`` query param of the dev / runtime server so that
 *     ``/api/files`` can serve the bytes.
 *
 * Broken images / 404s show a red-bordered "image not loaded" block.
 *
 * SSOT invariant — the doc is never mutated; the image is a block
 * widget placed *after* the image's line (similar to mermaid's
 * decoration). CodeMirror 6 disallows block decorations from a plain
 * ``ViewPlugin``, so this uses the same StateField + ViewPlugin split
 * the mermaid plugin established.
 */
import { syntaxTree } from "@codemirror/language";
import type { Extension, Range } from "@codemirror/state";
import { StateEffect, StateField } from "@codemirror/state";
import type { DecorationSet, ViewUpdate } from "@codemirror/view";
import { Decoration, EditorView, ViewPlugin, WidgetType } from "@codemirror/view";

import { rawFileUrl } from "../../../app/files";

const DEBOUNCE_MS = 200;

class ImageWidget extends WidgetType {
  constructor(readonly url: string, readonly alt: string) {
    super();
  }

  eq(other: WidgetType): boolean {
    return (
      other instanceof ImageWidget &&
      other.url === this.url &&
      other.alt === this.alt
    );
  }

  toDOM(): HTMLElement {
    const wrap = document.createElement("div");
    wrap.className =
      "my-2 overflow-hidden rounded border border-line bg-surface-muted";
    wrap.contentEditable = "false";
    const img = document.createElement("img");
    img.src = resolveImageUrl(this.url);
    img.alt = this.alt;
    img.loading = "lazy";
    img.style.display = "block";
    img.style.maxWidth = "100%";
    img.style.maxHeight = "480px";
    img.style.margin = "0 auto";
    img.onerror = () => {
      wrap.innerHTML = "";
      const err = document.createElement("pre");
      err.className =
        "rounded border border-danger bg-danger-soft p-2 text-xs text-danger-fg";
      err.textContent = `image not loaded: ${this.url}`;
      wrap.appendChild(err);
    };
    wrap.appendChild(img);
    return wrap;
  }

  ignoreEvent(): boolean {
    return true;
  }
}

/** Resolve an MD-link ``url`` against the runtime origin.
 *
 * - Absolute http(s) URLs pass through.
 * - Relative paths (``./img.png`` / ``img.png`` / ``../foo.png``) are
 *   served through ``/api/files`` against the current viewer's
 *   ``project_path`` + ``project_id`` query params.
 */
function resolveImageUrl(url: string): string {
  if (/^https?:\/\//i.test(url) || url.startsWith("data:")) return url;
  const params = new URLSearchParams(window.location.search);
  const projectPath = params.get("project_path");
  const projectId = params.get("project");
  if (!projectPath || !projectId) return url;
  // /api/files/raw serves binary bytes for <img> embeds (the JSON /api/files
  // returns text). Built via the files use-case so it goes through the
  // API_BASE engine seam, not a hardcoded same-origin path — required for a
  // bundled desktop frontend (tauri://). (D-2026-06-08-A step 4)
  return rawFileUrl(projectPath, projectId, url.startsWith("./") ? url.slice(2) : url);
}

function buildImageDecorations(view: EditorView): DecorationSet {
  const widgets: Range<Decoration>[] = [];
  const tree = syntaxTree(view.state);
  tree.iterate({
    enter(node) {
      if (node.name !== "Image") return;
      const text = view.state.sliceDoc(node.from, node.to);
      const match = /^!\[([^\]]*)\]\(([^)]+)\)$/.exec(text);
      if (!match) return;
      const alt = match[1];
      const url = match[2].trim();
      // Server returns JSON {content: "..."} for /api/files; that's
      // not an image. We pre-check URL extension to avoid 404s on
      // arbitrary refs. Allowed: common image extensions OR remote URL.
      if (!isLikelyImageUrl(url)) return;
      const lineEnd = view.state.doc.lineAt(node.to).to;
      widgets.push(
        Decoration.widget({
          widget: new ImageWidget(url, alt),
          side: 1,
          block: true,
        }).range(lineEnd),
      );
    },
  });
  return Decoration.set(widgets, true);
}

const IMAGE_EXT_RE = /\.(png|jpe?g|gif|webp|avif|svg)(\?|#|$)/i;

function isLikelyImageUrl(url: string): boolean {
  if (/^https?:\/\//i.test(url)) return IMAGE_EXT_RE.test(url);
  if (url.startsWith("data:image/")) return true;
  return IMAGE_EXT_RE.test(url);
}

const setImageDecorations = StateEffect.define<DecorationSet>();

const imageDecoField = StateField.define<DecorationSet>({
  create(): DecorationSet {
    return Decoration.none;
  },
  update(value, tr): DecorationSet {
    let next = value;
    if (tr.docChanged) next = next.map(tr.changes);
    for (const effect of tr.effects) {
      if (effect.is(setImageDecorations)) next = effect.value;
    }
    return next;
  },
  provide: (f) => EditorView.decorations.from(f),
});

const imageDebouncer = ViewPlugin.fromClass(
  class {
    private pending: number | null = null;

    constructor(view: EditorView) {
      this.scheduleRebuild(view, 0);
    }
    update(u: ViewUpdate): void {
      if (!u.docChanged) return;
      this.scheduleRebuild(u.view, DEBOUNCE_MS);
    }
    private scheduleRebuild(view: EditorView, ms: number): void {
      if (this.pending !== null) window.clearTimeout(this.pending);
      this.pending = window.setTimeout(() => {
        this.pending = null;
        const decos = buildImageDecorations(view);
        view.dispatch({ effects: setImageDecorations.of(decos) });
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

export const mdImagePlugin: Extension = [imageDecoField, imageDebouncer];
