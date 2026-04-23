"""Markdown H3 section helpers — Python port of viewer's ``lib/bodySections.ts``.

The server uses these to read a summary-line out of a node's ``index.md``
whenever it's written, so the canvas node preview can keep a short cache
without the viewer having to fetch the full MD file per node.

Kept intentionally close to the TypeScript version (same semantics, same
trim rules) so round-tripping between editor and preview is stable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_H3_RE = re.compile(r"^###\s+(.+?)\s*$")


@dataclass
class Section:
    heading: str
    content: str


@dataclass
class ParsedBody:
    lead: str
    sections: list[Section]


def _trim_blank(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)
    while start < end and lines[start].strip() == "":
        start += 1
    while end > start and lines[end - 1].strip() == "":
        end -= 1
    return lines[start:end]


def parse_body(body: str) -> ParsedBody:
    if not body:
        return ParsedBody(lead="", sections=[])
    lines = body.replace("\r\n", "\n").split("\n")
    lead: list[str] = []
    sections: list[Section] = []
    current: tuple[str, list[str]] | None = None
    for line in lines:
        m = _H3_RE.match(line)
        if m:
            if current is not None:
                heading, buf = current
                sections.append(
                    Section(heading=heading, content="\n".join(_trim_blank(buf)))
                )
            current = (m.group(1), [])
        elif current is not None:
            current[1].append(line)
        else:
            lead.append(line)
    if current is not None:
        heading, buf = current
        sections.append(
            Section(heading=heading, content="\n".join(_trim_blank(buf)))
        )
    return ParsedBody(lead="\n".join(_trim_blank(lead)), sections=sections)


def read_section(body: str, heading: str) -> str:
    """Return the named section's content, or ``""`` if missing.
    Heading match is case-insensitive."""
    parsed = parse_body(body)
    target = heading.strip().lower()
    for s in parsed.sections:
        if s.heading.strip().lower() == target:
            return s.content
    return ""


def pick_summary(body: str, kind: str | None) -> str:
    """Mirror of ``SketchNode``'s on-canvas preview rule:
    Mission → ``### Tagline`` first, everything else → ``### Summary``,
    otherwise the first non-References section, otherwise the lead text."""
    if not body:
        return ""
    # Mission priorities Tagline; other kinds prioritise Summary. If the
    # preferred section is missing, fall back to the opposite so a Mission
    # written with Summary-first still surfaces something.
    primary = ["Tagline", "Summary"] if kind == "mission" else ["Summary", "Tagline"]
    for h in primary:
        value = read_section(body, h)
        if value.strip():
            return value
    parsed = parse_body(body)
    for s in parsed.sections:
        if s.heading.strip().lower() == "references":
            continue
        if s.content.strip():
            return s.content
    return parsed.lead
