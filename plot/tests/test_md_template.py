"""v0.13 Phase 3: parse + render the heading-section MD format used by
Foundation node files. Lenient on read; strict on write."""

from __future__ import annotations

import pytest

from plot_mcp.md_template import parse_md_template, render_md_template


class TestRenderRoundTrip:
    def test_core_value_round_trip(self) -> None:
        original_typed = {
            "definition": "관용. 다양한 의견 존중.",
        }
        rendered = render_md_template(
            "core_value",
            "Tolerance",
            original_typed,
            free_prose="추가 설명 영역.",
        )
        parsed = parse_md_template(rendered, "core_value")
        assert parsed.label == "Tolerance"
        assert parsed.typed_fields == original_typed
        assert parsed.free_prose.strip() == "추가 설명 영역."
        assert parsed.warnings == []

    def test_mission_round_trip(self) -> None:
        typed = {
            "statement": "We run a community where everyone becomes a hero.",
        }
        rendered = render_md_template("mission", "Our Mission", typed)
        parsed = parse_md_template(rendered, "mission")
        assert parsed.typed_fields == typed
        assert parsed.label == "Our Mission"

    def test_identity_round_trip(self) -> None:
        typed = {
            "description": "Warm casual honorifics.",
            "do": "Greet first.",
            "dont": "Use ㅋㅋ-style emoji.",
        }
        rendered = render_md_template("identity", "Voice", typed)
        parsed = parse_md_template(rendered, "identity")
        assert parsed.typed_fields == typed


class TestLenientRead:
    def test_missing_sections_become_empty(self) -> None:
        # uses identity (still has description/do/dont) for multi-section coverage
        text = "# Voice\n\n## Description\n관용\n\n---\n"
        parsed = parse_md_template(text, "identity")
        assert parsed.typed_fields["description"] == "관용"
        assert parsed.typed_fields["do"] == ""
        assert parsed.typed_fields["dont"] == ""
        assert any("missing" in w and "do" in w for w in parsed.warnings)
        assert any("missing" in w and "dont" in w for w in parsed.warnings)

    def test_unknown_section_is_warning(self) -> None:
        text = "# T\n\n## Wrong heading\nfoo\n"
        parsed = parse_md_template(text, "identity")
        assert parsed.typed_fields == {"description": "", "do": "", "dont": ""}
        assert any("Wrong heading" in w for w in parsed.warnings)

    def test_missing_h1_is_warning(self) -> None:
        text = "## Definition\n관용\n"
        parsed = parse_md_template(text, "core_value")
        assert parsed.label == ""
        assert any("missing H1" in w for w in parsed.warnings)
        assert parsed.typed_fields["definition"] == "관용"

    def test_section_headings_case_insensitive(self) -> None:
        text = "# T\n\n## DESCRIPTION\nfoo\n\n## do\nbar\n\n## DON'T\nbaz\n"
        parsed = parse_md_template(text, "identity")
        assert parsed.typed_fields == {"description": "foo", "do": "bar", "dont": "baz"}

    def test_no_hr_treats_whole_file_as_typed(self) -> None:
        text = "# T\n\n## Definition\n관용\n"
        parsed = parse_md_template(text, "core_value")
        assert parsed.typed_fields["definition"] == "관용"
        assert parsed.free_prose == ""

    def test_html_comments_in_section_body_stripped(self) -> None:
        text = "# T\n\n## Definition\n<!-- placeholder -->\n관용\n"
        parsed = parse_md_template(text, "core_value")
        assert parsed.typed_fields["definition"] == "관용"


class TestStrictRender:
    def test_canonical_section_order_per_kind(self) -> None:
        # Render passes typed in any order; output uses the kind's canonical order.
        rendered = render_md_template(
            "identity",
            "X",
            {"dont": "z", "do": "y", "description": "x"},
        )
        # The literal section order in output mirrors SECTION_LABELS:
        # description, do, don't.
        assert rendered.index("## Description") < rendered.index("## Do")
        assert rendered.index("## Do") < rendered.index("## Don't")

    def test_empty_typed_fields_render_empty_sections(self) -> None:
        rendered = render_md_template("identity", "X", {})
        assert "## Description" in rendered
        assert "## Do" in rendered
        assert "## Don't" in rendered

    def test_free_prose_preserved_below_hr(self) -> None:
        rendered = render_md_template(
            "mission",
            "M",
            {"statement": "x"},
            free_prose="A long thing.\n\nMore prose.",
        )
        assert "A long thing." in rendered
        assert rendered.index("---") < rendered.index("A long thing.")

    def test_label_appears_as_h1(self) -> None:
        rendered = render_md_template("core_value", "Tolerance", {})
        assert rendered.splitlines()[0] == "# Tolerance"


class TestProjectKindHasNoTypedSections:
    def test_project_render_has_no_h2(self) -> None:
        rendered = render_md_template("project", "Banas", {})
        assert "##" not in rendered
        assert rendered.startswith("# Banas")

    def test_project_parse_returns_empty_typed_dict(self) -> None:
        parsed = parse_md_template("# Banas\n\nFree prose.\n", "project")
        assert parsed.typed_fields == {}
        assert parsed.label == "Banas"


@pytest.mark.parametrize(
    "kind, fields",
    [
        ("mission", {"statement": "a"}),
        ("core_value", {"definition": "a"}),
        ("identity", {"description": "a", "do": "b", "dont": "c"}),
    ],
)
def test_round_trip_all_foundation_kinds(kind: str, fields: dict[str, str]) -> None:
    rendered = render_md_template(kind, "Test", fields, free_prose="prose")
    parsed = parse_md_template(rendered, kind)
    assert parsed.typed_fields == fields
    assert parsed.label == "Test"
    assert parsed.free_prose.strip() == "prose"
    assert parsed.warnings == []
