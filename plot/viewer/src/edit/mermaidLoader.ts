/**
 * v0.21.0 Live Preview Stage 2 (D-2026-05-17-D) — lazy mermaid loader.
 *
 * Mermaid is a ~140 KB gzip dependency that only matters when the
 * user has at least one ``` ```mermaid``` ``` fenced block in their
 * data. Both surfaces that render mermaid — the MDPreview tab and
 * the live MdTextarea decoration — go through this singleton so the
 * library is downloaded **once**, on first demand, and Vite emits it
 * as its own lazy chunk.
 *
 * SSOT note: this loader never sees the markdown source itself. It
 * just hands out a render function. Callers compose the source.
 */

interface MermaidRenderResult {
  svg: string;
}

interface MermaidApi {
  render(id: string, code: string): Promise<MermaidRenderResult>;
}

let cached: Promise<MermaidApi> | null = null;

/**
 * Return the mermaid render API. The library is dynamically imported
 * on first call and initialised once with the same options the legacy
 * ``MDPreview`` previously hardcoded at module level (security =
 * ``loose`` so users can paste real-world diagrams; theme =
 * ``default`` to match the Preview tab).
 */
export function loadMermaid(): Promise<MermaidApi> {
  if (cached) return cached;
  cached = import("mermaid").then((mod) => {
    const mermaid = mod.default;
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "loose",
      theme: "default",
    });
    return {
      render: (id: string, code: string) => mermaid.render(id, code),
    };
  });
  return cached;
}
