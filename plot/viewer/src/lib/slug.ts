/**
 * Folder-path slug for node → folder mapping (v0.7).
 *
 * Mirrors ``plot_mcp/slug.py`` so the viewer can compute the default
 * folder client-side without an extra round-trip. Server will still
 * uniquify on POST /api/folders if the name is already taken.
 */

// Preserve Latin letters/digits, Hangul + CJK, collapse the rest to dashes.
const PRESERVE_RE =
  /[^a-z0-9가-힯ᄀ-ᇿꥠ-꥿぀-ヿ一-鿿]+/gi;

export function slugify(text: string): string {
  const lowered = text.toLowerCase().trim();
  const replaced = lowered.replace(PRESERVE_RE, "-");
  return replaced.replace(/^-+|-+$/g, "");
}

export function folderSlug(kind: string, label: string, canvas = "foundation"): string {
  const kindSlug = slugify(kind) || "node";
  const labelSlug = slugify(label);
  const stem = labelSlug ? `${kindSlug}-${labelSlug}` : kindSlug;
  const canvasSlug = slugify(canvas) || "foundation";
  return `${canvasSlug}/${stem}`;
}
