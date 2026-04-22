/**
 * Markdown H3 section helpers for node body fields.
 *
 * Inspector templates (Mission / Core Value / Identity) surface a handful
 * of typed fields — Tagline, Audience, Summary, Details, … — but the
 * underlying storage is still a single ``body`` string. Each field maps
 * to a ``### Heading\n<content>`` block so the document stays readable /
 * editable as plain Markdown and old notes round-trip untouched.
 *
 * Matching is case-insensitive on the heading; new sections are written
 * using the caller's display casing.
 */

export interface Section {
  /** Heading exactly as it appeared in the source (display casing). */
  heading: string;
  /** Section body, with leading/trailing blank lines trimmed. */
  content: string;
}

export interface ParsedBody {
  /** Text before the first ``### heading`` — kept verbatim. */
  lead: string;
  /** Sections in source order. */
  sections: Section[];
}

const H3_RE = /^###\s+(.+?)\s*$/;

export function parseBody(body: string): ParsedBody {
  if (!body) {
    return { lead: "", sections: [] };
  }
  const lines = body.split(/\r?\n/);
  const lead: string[] = [];
  const sections: Section[] = [];
  let current: { heading: string; buf: string[] } | null = null;

  for (const line of lines) {
    const m = H3_RE.exec(line);
    if (m) {
      if (current) {
        sections.push({
          heading: current.heading,
          content: trimBlank(current.buf).join("\n"),
        });
      }
      current = { heading: m[1], buf: [] };
    } else if (current) {
      current.buf.push(line);
    } else {
      lead.push(line);
    }
  }
  if (current) {
    sections.push({
      heading: current.heading,
      content: trimBlank(current.buf).join("\n"),
    });
  }
  return {
    lead: trimBlank(lead).join("\n"),
    sections,
  };
}

export function serializeBody(parsed: ParsedBody): string {
  const parts: string[] = [];
  if (parsed.lead.trim()) {
    parts.push(parsed.lead.trim());
  }
  for (const s of parsed.sections) {
    if (!s.heading.trim() && !s.content.trim()) continue;
    parts.push(`### ${s.heading.trim()}`);
    if (s.content.trim()) {
      parts.push(s.content.trim());
    }
  }
  return parts.join("\n\n");
}

/** Read a single section's content, or "" if the heading is absent. */
export function readSection(body: string, heading: string): string {
  const parsed = parseBody(body);
  const match = parsed.sections.find(
    (s) => s.heading.toLowerCase() === heading.toLowerCase(),
  );
  return match ? match.content : "";
}

/**
 * Write ``newContent`` into the section named ``heading``. Creates the
 * section (appended at the end) if it didn't exist, removes it when
 * ``newContent`` is blank (so empty fields don't leave stranded headings).
 */
export function writeSection(body: string, heading: string, newContent: string): string {
  const parsed = parseBody(body);
  const trimmed = newContent.replace(/\s+$/g, "");
  const idx = parsed.sections.findIndex(
    (s) => s.heading.toLowerCase() === heading.toLowerCase(),
  );
  if (!trimmed) {
    if (idx >= 0) {
      parsed.sections.splice(idx, 1);
    }
    return serializeBody(parsed);
  }
  if (idx >= 0) {
    parsed.sections[idx] = { heading: parsed.sections[idx].heading, content: trimmed };
  } else {
    parsed.sections.push({ heading, content: trimmed });
  }
  return serializeBody(parsed);
}

function trimBlank(lines: string[]): string[] {
  let start = 0;
  let end = lines.length;
  while (start < end && lines[start].trim() === "") start++;
  while (end > start && lines[end - 1].trim() === "") end--;
  return lines.slice(start, end);
}
