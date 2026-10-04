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
            "Use the\nreader's stated knowledge",
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
        # These assertions guard the shipped guidance, not the quality of generated Korean.
        for marker in (
            "한국어로 쓸 때만 아래를 따른다",
            "원칙 1. 행동과 상태를 파악한 뒤 문장을 다시 쓴다",
            "원칙 2. 독자에게 익숙하면서 뜻이 정확한 말을 고른다",
            "원칙 3. 짧게 나누고 반복을 덜어낸다",
            "처음 보는 문장에도 같은 원칙을 적용한다",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.body())

    def test_rewriting_checks_meaning_without_printing_the_checklist(self) -> None:
        # Fluent wording can still change an actor, a condition, or an unmeasured effect.
        body = self.body()

        for required in (
            "주체와 대상:",
            "행동과 조건:",
            "확실성과 범위:",
            "추가와 누락:",
            "검사 과정은 출력하지 않는다",
        ):
            with self.subTest(required=required):
                self.assertIn(required, body)

    def test_shortening_keeps_relations_and_allows_ui_labels(self) -> None:
        body = self.body()

        for required in (
            "세는 대상과 단위를 분명히 한다",
            "조건과 그 조건이 걸리는 행동은 함께 둔다",
            "본문 문장은 서술어와 종결어미로 끝맺는다",
            "버튼·제목·표의 이름은 명사로 짧게 쓸 수 있다",
            "엠대시(—)로 앞뒤 관계를 함축하지 말고",
            "'~의'를 거듭 쓰면",
        ):
            with self.subTest(required=required):
                self.assertIn(required, body)

    def test_sino_korean_words_are_kept_not_paraphrased(self) -> None:
        # 0.6.0 told the writer to replace a Sino-Korean term with a native paraphrase and shipped
        # `"평가기" → "재는 쪽"` as the worked example. Following it produced a phrase no Korean
        # speaker uses, and in one project the coined replacement spread through nine files.
        body = self.body()

        self.assertIn("한자어를 순우리말로 억지로\n바꾸지 않는다", body)
        self.assertIn("정확하고 익숙한 전문 용어는 유지한다", body)
        self.assertIn("다른 행동으로 읽히면 바꾼다", body)
        self.assertNotIn("재는 쪽", body)

    def test_the_korean_section_obeys_its_own_principles(self) -> None:
        body = self.body()

        # Principle 2 forbids coining a phrase to explain something. The rules used to explain
        # grammar through exactly such phrases.
        for coined in (
            "명사 자리에 앉고",
            "문장을 끌고 간다",
            "달고 앉는다",
            "머리에 세운다",
            "밀어 넣고",
            "동작이 숨는",
        ):
            with self.subTest(coined=coined):
                self.assertNotIn(coined, body)

        # The guidance requires a counter word when counting. The rules used to write these while
        # demanding the opposite one paragraph away.
        for uncounted in ("둘이다", "둘 이상"):
            with self.subTest(uncounted=uncounted):
                self.assertNotIn(uncounted, body)

        # Grammar jargon the reader is not given. 서술어 / 명사 are school grammar; 관형절 is not.
        self.assertNotIn("관형절", body)

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
