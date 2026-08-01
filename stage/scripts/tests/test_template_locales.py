"""Structural parity between canonical English templates and locale overlays.

DE-00000003: locale files translate prose only. Structure, machine tokens,
and token-table first cells must match the canonical English counterpart, so
hooks and the audit parse any locale identically.
"""

import re
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = PLUGIN_ROOT / "templates" / "project-stage"
LOCALE_ROOT = PLUGIN_ROOT / "templates" / "locales"
V4_TEMPLATE_ROOT = PLUGIN_ROOT / "templates" / "v4" / "project-stage"
V4_KO_ROOT = PLUGIN_ROOT / "templates" / "v4" / "locales" / "ko"
V4_LOCALE_INVARIANT_WORK_TEMPLATES = {
    Path("work/planned/_epic.md"),
    Path("work/planned/_story.md"),
    Path("work/current/_epic.md"),
    Path("work/current/_story.md"),
}

# Files whose markdown-table first column is a machine token set.
TOKEN_TABLE_FILES = {
    Path("operations/verification.md"),
    Path("past/canon/principles.md"),
}
# Literal markers audit_canon requires in every project's principles.md.
CANON_MARKERS = (
    "SSOT",
    "MECE",
    "Fail Fast",
    "AHA",
    "## Completion principle",
    "## Behavior principles",
)


def backtick_tokens(text: str) -> list[str]:
    return sorted(re.findall(r"`([^`]+)`", text))


def frontmatter_keys(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    keys = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^([A-Za-z_]+):", line)
        if match:
            keys.append(match.group(1))
    return keys


def table_first_cells(text: str) -> list[str]:
    cells = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        first = stripped.strip("|").split("|")[0].strip().strip("`")
        if first and not re.fullmatch(r":?-{2,}:?", first):
            cells.append(first)
    return cells


def heading_count(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.lstrip().startswith("#"))


class TemplateLocaleParityTest(unittest.TestCase):
    def locales(self) -> list[Path]:
        if not LOCALE_ROOT.is_dir():
            return []
        return [path for path in sorted(LOCALE_ROOT.iterdir()) if path.is_dir()]

    def locale_files(self, locale_dir: Path) -> list[Path]:
        return [path for path in sorted(locale_dir.rglob("*")) if path.is_file()]

    def test_ko_locale_is_bundled(self):
        self.assertIn("ko", [path.name for path in self.locales()])

    def test_locale_files_shadow_only_canonical_prose_files(self):
        for locale_dir in self.locales():
            for path in self.locale_files(locale_dir):
                relative = path.relative_to(locale_dir)
                with self.subTest(locale=locale_dir.name, file=str(relative)):
                    self.assertTrue(
                        (TEMPLATE_ROOT / relative).is_file(),
                        f"{relative} has no canonical counterpart",
                    )
                    self.assertNotEqual(
                        "_template.md",
                        relative.name,
                        "record skeletons are locale-invariant",
                    )
                    self.assertEqual(".md", relative.suffix, "only markdown is localized")

    def test_locale_files_preserve_structure_and_machine_tokens(self):
        for locale_dir in self.locales():
            for path in self.locale_files(locale_dir):
                relative = path.relative_to(locale_dir)
                canonical = (TEMPLATE_ROOT / relative).read_text(encoding="utf-8")
                localized = path.read_text(encoding="utf-8")
                with self.subTest(locale=locale_dir.name, file=str(relative)):
                    self.assertEqual(
                        frontmatter_keys(canonical),
                        frontmatter_keys(localized),
                        "frontmatter keys must match",
                    )
                    self.assertEqual(
                        backtick_tokens(canonical),
                        backtick_tokens(localized),
                        "backtick machine tokens must match",
                    )
                    self.assertEqual(
                        heading_count(canonical),
                        heading_count(localized),
                        "heading structure must match",
                    )
                    if relative in TOKEN_TABLE_FILES:
                        self.assertEqual(
                            table_first_cells(canonical),
                            table_first_cells(localized),
                            "token-table first cells must match",
                        )

    def test_locale_principles_keep_audit_markers(self):
        for locale_dir in self.locales():
            principles = locale_dir / "past" / "canon" / "principles.md"
            if not principles.is_file():
                continue
            text = principles.read_text(encoding="utf-8")
            for marker in CANON_MARKERS:
                with self.subTest(locale=locale_dir.name, marker=marker):
                    self.assertIn(marker, text)

    def test_ko_locale_covers_the_reader_facing_surface(self):
        """The ko overlay must localize at least every index and README the
        user reads; other prose files may fall back to English."""
        ko = LOCALE_ROOT / "ko"
        required = [
            path.relative_to(TEMPLATE_ROOT)
            for path in sorted(TEMPLATE_ROOT.rglob("*.md"))
            if path.name != "_template.md"
        ]
        for relative in required:
            with self.subTest(file=str(relative)):
                self.assertTrue((ko / relative).is_file(), f"ko overlay missing {relative}")


class TemplateV4LocaleParityTest(unittest.TestCase):
    def locale_files(self) -> list[Path]:
        return [path for path in sorted(V4_KO_ROOT.rglob("*")) if path.is_file()]

    def test_v4_locale_files_shadow_only_canonical_prose_files(self):
        for path in self.locale_files():
            relative = path.relative_to(V4_KO_ROOT)
            with self.subTest(file=str(relative)):
                self.assertTrue(
                    (V4_TEMPLATE_ROOT / relative).is_file(),
                    f"{relative} has no canonical counterpart",
                )
                self.assertNotEqual("_template.md", relative.name)
                self.assertEqual(".md", relative.suffix)

    def test_v4_locale_files_preserve_structure_and_machine_tokens(self):
        token_tables = {
            Path("operations/verification.md"),
            Path("official/canon/principles.md"),
        }
        for path in self.locale_files():
            relative = path.relative_to(V4_KO_ROOT)
            canonical = (V4_TEMPLATE_ROOT / relative).read_text(encoding="utf-8")
            localized = path.read_text(encoding="utf-8")
            with self.subTest(file=str(relative)):
                self.assertEqual(frontmatter_keys(canonical), frontmatter_keys(localized))
                self.assertEqual(backtick_tokens(canonical), backtick_tokens(localized))
                self.assertEqual(heading_count(canonical), heading_count(localized))
                if relative in token_tables:
                    self.assertEqual(table_first_cells(canonical), table_first_cells(localized))

    def test_v4_locale_principles_keep_audit_markers(self):
        text = (V4_KO_ROOT / "official/canon/principles.md").read_text(encoding="utf-8")
        for marker in CANON_MARKERS:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_v4_ko_locale_covers_the_reader_facing_surface(self):
        required = [
            path.relative_to(V4_TEMPLATE_ROOT)
            for path in sorted(V4_TEMPLATE_ROOT.rglob("*.md"))
            if path.name != "_template.md"
            and path.relative_to(V4_TEMPLATE_ROOT)
            not in V4_LOCALE_INVARIANT_WORK_TEMPLATES
        ]
        for relative in required:
            with self.subTest(file=str(relative)):
                self.assertTrue(
                    (V4_KO_ROOT / relative).is_file(),
                    f"ko overlay missing {relative}",
                )

    def test_v4_work_record_templates_are_locale_invariant(self):
        for relative in V4_LOCALE_INVARIANT_WORK_TEMPLATES:
            with self.subTest(file=str(relative)):
                self.assertFalse(
                    (V4_KO_ROOT / relative).exists(),
                    f"{relative} must use the canonical machine-token headings",
                )


if __name__ == "__main__":
    unittest.main()
