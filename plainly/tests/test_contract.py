from __future__ import annotations

import json
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PLUGIN_ROOT.parent


class ContractTest(unittest.TestCase):
    def load_json(self, path: Path) -> dict[str, object]:
        return json.loads(path.read_text(encoding="utf-8"))

    def test_dual_manifests_share_name_and_version(self) -> None:
        claude = self.load_json(PLUGIN_ROOT / ".claude-plugin" / "plugin.json")
        codex = self.load_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json")

        self.assertEqual(claude["name"], "plainly")
        self.assertEqual(codex["name"], "plainly")
        self.assertEqual(claude["version"], codex["version"])
        self.assertRegex(str(claude["version"]), r"^\d+\.\d+\.\d+$")

    def test_hook_contract_has_no_post_answer_continuation(self) -> None:
        config = self.load_json(PLUGIN_ROOT / "hooks" / "hooks.json")
        hooks = config["hooks"]

        self.assertEqual(set(hooks), {"SessionStart", "UserPromptSubmit"})
        self.assertEqual(hooks["SessionStart"][0]["matcher"], "compact")
        self.assertNotIn("Stop", hooks)
        self.assertNotIn("SubagentStop", hooks)

    def test_profile_registry_is_complete(self) -> None:
        registry = self.load_json(PLUGIN_ROOT / "styles" / "profiles.json")

        self.assertEqual(registry["default"], "baseline")
        self.assertEqual(registry["baseline"], "baseline")
        self.assertEqual(registry["aliases"], {"plain": "baseline"})
        self.assertEqual(
            set(registry["profiles"]),
            {"baseline", "brief", "decision", "guided", "professional"},
        )
        for entry in registry["profiles"].values():
            style_path = PLUGIN_ROOT / "styles" / entry["file"]
            self.assertTrue(style_path.read_text(encoding="utf-8").strip())

    def test_baseline_owns_shared_principles_without_delta_duplication(self) -> None:
        styles = PLUGIN_ROOT / "styles"
        baseline = (styles / "baseline.md").read_text(encoding="utf-8")
        deltas = "\n".join(
            (styles / name).read_text(encoding="utf-8")
            for name in ("brief.md", "decision.md", "guided.md", "professional.md")
        )

        for principle in (
            "Lead with the answer",
            "plain language",
            "short sentences",
            "Distinguish facts from recommendations",
        ):
            self.assertIn(principle, baseline)
            self.assertNotIn(principle, deltas)
        self.assertFalse((styles / "plain.md").exists())

    def test_baseline_does_not_duplicate_fixed_honesty_rules(self) -> None:
        baseline = (PLUGIN_ROOT / "styles" / "baseline.md").read_text(encoding="utf-8")

        self.assertNotIn("Do not state guesses as facts", baseline)
        self.assertNotIn("Mark unverified claims as unverified", baseline)

    def test_styles_do_not_duplicate_fixed_register_rule(self) -> None:
        styles = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (PLUGIN_ROOT / "styles").glob("*.md")
        )

        self.assertNotIn("marks politeness grammatically", styles)
        self.assertNotIn("polite register", styles)

    def test_fixed_register_rule_carries_no_style_escape_clause(self) -> None:
        hook = (PLUGIN_ROOT / "hooks" / "inject_style.py").read_text(encoding="utf-8")

        for escape in (
            "different level of formality",
            "unless the",
            "explicitly directs",
        ):
            self.assertNotIn(escape, hook)

    def test_marketplace_registers_plainly(self) -> None:
        marketplace = self.load_json(REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json")
        entries = {entry["name"]: entry for entry in marketplace["plugins"]}

        self.assertEqual(entries["plainly"]["source"], "./plainly")
        self.assertNotIn("policy", entries["plainly"])
        self.assertNotIn("category", entries["plainly"])


if __name__ == "__main__":
    unittest.main()
