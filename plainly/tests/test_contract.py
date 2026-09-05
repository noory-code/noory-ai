from __future__ import annotations

import json
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PLUGIN_ROOT.parent
STYLES = PLUGIN_ROOT / "styles"
OUTPUT_STYLES = PLUGIN_ROOT / "output-styles"

PROFILES = ("baseline", "brief", "decision", "guided", "professional")


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

    def test_plugin_ships_no_hooks_and_no_codex_manifest(self) -> None:
        # The styles now reach the model through Claude Code's own output-style loader. A hook
        # left behind would put the same text into the session a second time.
        self.assertFalse((PLUGIN_ROOT / "hooks").exists())
        self.assertFalse((PLUGIN_ROOT / "src").exists())
        self.assertFalse((PLUGIN_ROOT / ".codex-plugin").exists())

    def test_marketplace_registers_plainly(self) -> None:
        marketplace = load_json(REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json")
        entries = {entry["name"]: entry for entry in marketplace["plugins"]}

        self.assertEqual(entries["plainly"]["source"], "./plainly")
        self.assertNotIn("policy", entries["plainly"])
        self.assertNotIn("category", entries["plainly"])


class SourceTest(unittest.TestCase):
    def test_profile_registry_is_complete(self) -> None:
        registry = load_json(STYLES / "profiles.json")

        self.assertEqual(registry["default"], "baseline")
        self.assertEqual(registry["baseline"], "baseline")
        self.assertEqual(set(registry["profiles"]), set(PROFILES))
        for entry in registry["profiles"].values():
            self.assertTrue((STYLES / entry["file"]).read_text(encoding="utf-8").strip())

    def test_baseline_owns_shared_principles_without_delta_duplication(self) -> None:
        baseline = (STYLES / "baseline.md").read_text(encoding="utf-8")
        deltas = "\n".join(
            (STYLES / f"{name}.md").read_text(encoding="utf-8")
            for name in PROFILES
            if name != "baseline"
        )

        for principle in (
            "Lead with the answer",
            "plain language",
            "short sentences",
            "Distinguish facts from recommendations",
        ):
            self.assertIn(principle, baseline)
            self.assertNotIn(principle, deltas)
        self.assertFalse((STYLES / "plain.md").exists())

    def test_only_the_fixed_rules_carry_the_fixed_rules(self) -> None:
        profile_sources = "\n".join(
            (STYLES / f"{name}.md").read_text(encoding="utf-8") for name in PROFILES
        )

        for rule in (
            "Do not state guesses as facts",
            "marks politeness grammatically",
            "polite register",
        ):
            self.assertNotIn(rule, profile_sources)

    def test_fixed_register_rule_carries_no_style_escape_clause(self) -> None:
        fixed = (STYLES / "fixed-rules.md").read_text(encoding="utf-8")

        for escape in (
            "different level of formality",
            "unless the",
            "explicitly directs",
        ):
            self.assertNotIn(escape, fixed)


class OutputStyleTest(unittest.TestCase):
    def shipped(self) -> dict[str, tuple[dict[str, str], str]]:
        return {
            name: split_frontmatter((OUTPUT_STYLES / f"{name}.md").read_text(encoding="utf-8"))
            for name in PROFILES
        }

    def test_one_shipped_style_per_profile(self) -> None:
        shipped = sorted(path.stem for path in OUTPUT_STYLES.glob("*.md"))

        self.assertEqual(shipped, sorted(PROFILES))

    def test_every_style_keeps_the_coding_instructions(self) -> None:
        # Claude Code removes its default coding instructions for any output style that does not
        # ask to keep them, and it discards an unknown key in silence — a misspelling here loads
        # fine and drops the instructions with no warning. So the spelling itself is the check.
        for name, (fields, _) in self.shipped().items():
            with self.subTest(style=name):
                self.assertEqual(fields.get("keep-coding-instructions"), "true")

    def test_frontmatter_carries_only_keys_claude_code_reads(self) -> None:
        allowed = {"name", "description", "keep-coding-instructions"}
        for name, (fields, _) in self.shipped().items():
            with self.subTest(style=name):
                self.assertEqual(set(fields), allowed)
                self.assertTrue(fields["name"])
                self.assertTrue(fields["description"])

    def test_every_style_carries_the_baseline_and_the_fixed_rules(self) -> None:
        baseline = (STYLES / "baseline.md").read_text(encoding="utf-8").strip()
        fixed = (STYLES / "fixed-rules.md").read_text(encoding="utf-8").strip()

        for name, (_, body) in self.shipped().items():
            with self.subTest(style=name):
                self.assertIn(baseline, body)
                self.assertIn(fixed, body)

    def test_each_style_carries_its_own_delta(self) -> None:
        for name, (_, body) in self.shipped().items():
            if name == "baseline":
                continue
            delta = (STYLES / f"{name}.md").read_text(encoding="utf-8").strip()
            with self.subTest(style=name):
                self.assertIn(delta, body)


class KoreanGuidanceTest(unittest.TestCase):
    def fixed_rules(self) -> str:
        return (STYLES / "fixed-rules.md").read_text(encoding="utf-8")

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
                self.assertIn(marker, self.fixed_rules())

    def test_rule_one_looks_past_the_suffixes_it_used_to_scan(self) -> None:
        fixed = self.fixed_rules()

        for required in (
            "그 답이 서술어에 없으면",
            '"X하다"가 말이 되는',
            "속이 빈 명사를 머리에 세운다",
        ):
            with self.subTest(required=required):
                self.assertIn(required, fixed)

        # The narrow triggers rule 1 used to carry. They passed a sentence whose action sat in an
        # ordinary noun, which is the shape a literal translation produces.
        for forbidden in (
            "`-이다`·`-있다`·`-하다`뿐이면",
            "명사가 세 개 넘게 이어지면",
            "읽는 쪽",
            "그 바닥",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, fixed)


if __name__ == "__main__":
    unittest.main()
