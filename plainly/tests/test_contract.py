from __future__ import annotations

import json
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PLUGIN_ROOT.parent
STYLE = PLUGIN_ROOT / "output-styles" / "plainly.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse the leading `---` block the way Claude Code reads a style file."""
    if not text.startswith("---\n"):
        raise AssertionError("style file does not open with a frontmatter block")
    _, block, body = text.split("---\n", 2)
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise AssertionError(f"frontmatter line is not a key/value pair: {line!r}")
        fields[key.strip()] = value.strip()
    return fields, body


class ManifestTest(unittest.TestCase):
    def test_manifest_declares_a_semantic_version(self) -> None:
        manifest = load_json(PLUGIN_ROOT / ".claude-plugin" / "plugin.json")

        self.assertEqual(manifest["name"], "plainly")
        self.assertRegex(str(manifest["version"]), r"^\d+\.\d+\.\d+$")

    def test_plugin_ships_the_style_and_nothing_that_runs(self) -> None:
        # The style reaches the model through Claude Code's own output-style loader. A hook left
        # behind would put the same text into the session a second time.
        for absent in ("hooks", "src", "scripts", "skills", "styles", ".codex-plugin"):
            with self.subTest(path=absent):
                self.assertFalse((PLUGIN_ROOT / absent).exists())

    def test_one_style_ships(self) -> None:
        shipped = sorted(path.name for path in (PLUGIN_ROOT / "output-styles").glob("*.md"))

        self.assertEqual(shipped, ["plainly.md"])

    def test_marketplace_registers_plainly(self) -> None:
        marketplace = load_json(REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json")
        entries = {entry["name"]: entry for entry in marketplace["plugins"]}

        self.assertEqual(entries["plainly"]["source"], "./plainly")
        self.assertNotIn("policy", entries["plainly"])
        self.assertNotIn("category", entries["plainly"])


class FrontmatterTest(unittest.TestCase):
    def fields(self) -> dict[str, str]:
        return split_frontmatter(STYLE.read_text(encoding="utf-8"))[0]

    def test_the_style_keeps_the_coding_instructions(self) -> None:
        # Claude Code removes its default coding instructions for any output style that does not
        # ask to keep them, and it discards an unknown key in silence — a misspelling here loads
        # fine and drops the instructions with no warning. So the spelling itself is the check.
        self.assertEqual(self.fields().get("keep-coding-instructions"), "true")

    def test_frontmatter_carries_only_keys_claude_code_reads(self) -> None:
        fields = self.fields()

        self.assertEqual(set(fields), {"name", "description", "keep-coding-instructions"})
        self.assertEqual(fields["name"], "Plainly")
        self.assertTrue(fields["description"])


class RulesTest(unittest.TestCase):
    def body(self) -> str:
        return split_frontmatter(STYLE.read_text(encoding="utf-8"))[1]

    def test_the_style_states_its_own_scope(self) -> None:
        body = self.body()

        for required in (
            "every sentence you write for a person to read",
            "never what a file must contain",
        ):
            with self.subTest(required=required):
                self.assertIn(required, body)

        # Nothing sits above these rules any more, so an instruction to apply "the style above"
        # would point at nothing.
        self.assertNotIn("the style above", body)
        self.assertNotIn("no matter which style is selected", body)

    def test_the_fixed_rules_are_all_present(self) -> None:
        body = self.body()

        for rule in (
            "Do not state guesses as facts",
            "compose in the reader's language",
            "means nothing to the reader",
            "shorten by cutting repetition",
            "marks politeness grammatically",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, body)

    def test_the_register_rule_carries_no_escape_clause(self) -> None:
        body = self.body()

        for escape in ("different level of formality", "unless the", "explicitly directs"):
            with self.subTest(escape=escape):
                self.assertNotIn(escape, body)


class KoreanGuidanceTest(unittest.TestCase):
    def body(self) -> str:
        return split_frontmatter(STYLE.read_text(encoding="utf-8"))[1]

    def test_korean_guidance_is_written_in_korean(self) -> None:
        # The markers are Korean because the guidance itself is. Stating Korean rules in English
        # asks the reader to build an English sentence and swap Korean words into it — the very
        # habit the section exists to break — so an English marker here would pass while the
        # section had drifted back to the shape it warns against.
        for marker in (
            "한국어로 답할 때만 아래 규칙을 따른다",
            "동작을 서술어에 둔다",
            "새 용어를 함부로 만들지 않는다",
            "수를 세면 세는 말을 붙인다",
            "처음 보는 문장에도 같은 유형의 문제가 있으면 이 규칙을",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.body())

    def test_rule_one_looks_past_the_suffixes_it_used_to_scan(self) -> None:
        body = self.body()

        for required in (
            "그 답이 서술어에 없으면",
            '"X하다"가 말이 되는',
            "속이 빈 명사를 머리에 세운다",
        ):
            with self.subTest(required=required):
                self.assertIn(required, body)

        # The narrow triggers rule 1 used to carry. They passed a sentence whose action sat in an
        # ordinary noun, which is the shape a literal translation produces.
        for forbidden in (
            "`-이다`·`-있다`·`-하다`뿐이면",
            "명사가 세 개 넘게 이어지면",
            "읽는 쪽",
            "그 바닥",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, body)


if __name__ == "__main__":
    unittest.main()
