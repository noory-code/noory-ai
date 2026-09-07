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
            "한국어로 쓸 때만 아래를 따른다",
            "원칙 1. 관계를 생략하지 않는다",
            "원칙 2. 남들이 실제로 쓰는 말을 쓴다",
            "원칙 3. 줄일 때도 조사와 어미는 남긴다",
            "처음 보는 문장이라도 같은 잘못이 보이면 똑같이 고친다",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.body())

    def test_the_section_names_the_one_cause_before_the_principles(self) -> None:
        # Four separate rules invited the reader to satisfy each in isolation. Naming the cause
        # once — Korean marks relations with particles and endings, English with word order —
        # is what lets a principle cover an omission nobody wrote an example for.
        body = self.body()

        for required in (
            "낱말 사이의 관계를 조사와 어미로 나타내고, 영어는 어순으로 나타낸다",
            "관계를 적을 자리가 빈 채로 남는다",
        ):
            with self.subTest(required=required):
                self.assertIn(required, body)

    def test_the_omissions_rule_one_covers_stay_listed(self) -> None:
        # Each of these was a standalone rule, or missing entirely, before the principles landed.
        # Rule 1 only replaces them while it still names them.
        body = self.body()

        for required in (
            "숫자 뒤에는 단위를 붙인다",
            "명사구나 연결어미로 끝내지 않는다",
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

        self.assertIn("한자어를 순우리말로 억지로 바꾸지 않는다", body)
        self.assertIn("고칠 것은 어휘가 아니라 빠진 조사와 어미다", body)
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

        # Principle 1 requires a counter word after a number. The rules used to write these while
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
