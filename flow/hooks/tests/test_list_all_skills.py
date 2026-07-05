"""Marketplace shape guard tests for scripts/list-all-skills.py.

The marketplace scan must emit only the exact layout
``marketplaces/<mp>/plugins/<plugin>/skills/<skill>/SKILL.md``. Stray SKILL.md
files elsewhere under a marketplace checkout (docs examples, marketplace
repo-root ``skills/``) must NOT be emitted with a bogus namespace — a
substring check (``'plugins' in parts``) is a no-op because every path under
``~/.claude/plugins/marketplaces`` contains ``plugins``.

Runs the script as a subprocess with HOME/USERPROFILE pointed at a tmp fixture
(cross-platform: ``Path.home()`` reads USERPROFILE on Windows, HOME on Unix).

Run: cd flow/hooks && python3 -m unittest tests.test_list_all_skills
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "list-all-skills.py"


def _make_skill(skill_dir: Path) -> None:
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text("# skill\n", encoding="utf-8")


class TestMarketplaceShapeGuard(unittest.TestCase):
    """Only the canonical marketplaces/<mp>/plugins/<plugin>/skills/<skill>/SKILL.md shape is emitted."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        mp = self.home / ".claude" / "plugins" / "marketplaces" / "mp"
        # canonical layout — must be emitted as "goodplugin:alpha"
        _make_skill(mp / "plugins" / "goodplugin" / "skills" / "alpha")
        # decoys — must NOT be emitted (would get bogus namespaces "docs:x" / "mp:y" / "docs:z")
        _make_skill(mp / "docs" / "skills" / "x")  # marketplace docs example
        _make_skill(mp / "skills" / "y")  # marketplace repo-root skills/
        _make_skill(mp / "plugins" / "goodplugin" / "docs" / "skills" / "z")  # plugin docs example
        # user-global skill (scan #1, separate from the marketplace scan) — emitted un-namespaced
        _make_skill(self.home / ".claude" / "skills" / "solo")
        _make_skill(self.home / ".codex" / "skills" / "solo-codex")
        codex_plugin = self.home / ".codex" / "plugins" / "cache" / "mp" / "goodcodex" / "1.0.0"
        (codex_plugin / ".codex-plugin").mkdir(parents=True, exist_ok=True)
        (codex_plugin / ".codex-plugin" / "plugin.json").write_text(
            '{"name":"goodcodex"}',
            encoding="utf-8",
        )
        _make_skill(codex_plugin / "skills" / "beta")

    def _run_script(self) -> list[str]:
        env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home))
        env.pop("CLAUDE_PROJECT_DIR", None)  # keep the project-local scan out of the fixture
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        return result.stdout.splitlines()

    def test_canonical_layout_emitted(self):
        self.assertIn("goodplugin:alpha", self._run_script())

    def test_user_global_skill_still_emitted(self):
        self.assertIn("solo", self._run_script())
        self.assertIn("solo-codex", self._run_script())

    def test_codex_plugin_skill_emitted(self):
        self.assertIn("goodcodex:beta", self._run_script())

    def test_decoy_docs_and_repo_root_skills_not_emitted(self):
        lines = self._run_script()
        joined = "\n".join(lines)
        self.assertNotIn("docs:x", lines, "marketplace docs example must not be emitted")
        self.assertNotIn("mp:y", lines, "marketplace repo-root skills/ must not be emitted")
        self.assertNotIn("docs:z", lines, "plugin docs example must not be emitted")
        # no decoy skill name may leak under any namespace
        for decoy in (":x", ":y", ":z"):
            self.assertNotIn(decoy, joined, f"decoy skill '{decoy}' leaked with a bogus namespace")

    def test_only_expected_lines(self):
        # exact output contract: the two fixtures above, nothing else
        self.assertEqual(
            sorted(self._run_script()),
            ["goodcodex:beta", "goodplugin:alpha", "solo", "solo-codex"],
        )


if __name__ == "__main__":
    unittest.main()
