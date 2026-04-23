"""body_sections — Python port of viewer's H3 section parser (v0.7)."""

from __future__ import annotations

from plot_mcp.body_sections import parse_body, pick_summary, read_section

SAMPLE = (
    "### Tagline\n"
    "The tagline line\n"
    "\n"
    "### Summary\n"
    "Multi-line summary\n"
    "second line\n"
    "\n"
    "### References\n"
    "[[workspace/foo.md]]\n"
)


def test_parse_returns_sections_in_order() -> None:
    parsed = parse_body(SAMPLE)
    assert [s.heading for s in parsed.sections] == ["Tagline", "Summary", "References"]
    assert parsed.sections[1].content == "Multi-line summary\nsecond line"


def test_parse_lead_text_preserved() -> None:
    parsed = parse_body("lead text\n\n### Summary\nbody")
    assert parsed.lead == "lead text"
    assert parsed.sections[0].content == "body"


def test_read_section_case_insensitive() -> None:
    assert read_section(SAMPLE, "tagline") == "The tagline line"
    assert read_section(SAMPLE, "SUMMARY") == "Multi-line summary\nsecond line"


def test_read_section_returns_blank_when_missing() -> None:
    assert read_section(SAMPLE, "goal") == ""


def test_pick_summary_mission_prefers_tagline() -> None:
    assert pick_summary(SAMPLE, "mission") == "The tagline line"


def test_pick_summary_other_kinds_prefer_summary() -> None:
    assert pick_summary(SAMPLE, "identity") == "Multi-line summary\nsecond line"


def test_pick_summary_skips_references_when_falling_back() -> None:
    body = "### References\n[[only-link]]\n"
    assert pick_summary(body, "identity") == ""


def test_pick_summary_uses_lead_when_no_sections() -> None:
    assert pick_summary("just lead text", "mission") == "just lead text"


def test_parse_handles_crlf() -> None:
    parsed = parse_body("### A\r\none\r\ntwo\r\n")
    assert parsed.sections[0].content == "one\ntwo"
