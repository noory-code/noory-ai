from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIRECTORIES = {
    "evonest": "evonest",
    "flutter-cask": "flutter-cask",
    "pencil-m3-flutter": "pencil_m3_flutter",
    "plainly": "plainly",
    "rag": "rag",
    "stage": "stage",
}
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


class PluginContractTest(unittest.TestCase):
    def test_every_plugin_has_matching_host_manifests(self) -> None:
        for plugin_name, directory in PLUGIN_DIRECTORIES.items():
            with self.subTest(plugin=plugin_name):
                plugin_root = REPOSITORY_ROOT / directory
                claude = load_json(plugin_root / ".claude-plugin" / "plugin.json")
                codex = load_json(plugin_root / ".codex-plugin" / "plugin.json")
                self.assertEqual(claude["name"], plugin_name)
                self.assertEqual(codex["name"], plugin_name)
                self.assertEqual(claude["version"], codex["version"])
                self.assertRegex(str(codex["version"]), SEMVER)

    def test_host_marketplaces_register_the_same_plugins(self) -> None:
        claude = load_json(REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json")
        codex = load_json(REPOSITORY_ROOT / ".agents" / "plugins" / "marketplace.json")
        expected = set(PLUGIN_DIRECTORIES)
        self.assertEqual({entry["name"] for entry in claude["plugins"]}, expected)
        self.assertEqual({entry["name"] for entry in codex["plugins"]}, expected)

    def test_codex_marketplace_entries_resolve_and_include_policy(self) -> None:
        marketplace = load_json(
            REPOSITORY_ROOT / ".agents" / "plugins" / "marketplace.json"
        )
        for entry in marketplace["plugins"]:
            with self.subTest(plugin=entry["name"]):
                source = entry["source"]
                self.assertEqual(source["source"], "local")
                path = source["path"]
                self.assertTrue(path.startswith("./"))
                self.assertTrue((REPOSITORY_ROOT / path).is_dir())
                self.assertIn(
                    entry["policy"]["installation"],
                    {"AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"},
                )
                self.assertIn(
                    entry["policy"]["authentication"], {"ON_INSTALL", "ON_USE"}
                )
                self.assertIsInstance(entry["category"], str)

    def test_codex_manifests_do_not_depend_on_fictitious_project_env(self) -> None:
        for plugin_name, directory in PLUGIN_DIRECTORIES.items():
            with self.subTest(plugin=plugin_name):
                manifest = (
                    REPOSITORY_ROOT / directory / ".codex-plugin" / "plugin.json"
                ).read_text(encoding="utf-8")
                self.assertNotIn("CODEX_PROJECT_DIR", manifest)

    def test_evonest_package_version_matches_both_manifests(self) -> None:
        pyproject = (REPOSITORY_ROOT / "evonest" / "pyproject.toml").read_text(
            encoding="utf-8"
        )
        match = re.search(r'^version = "([^"]+)"$', pyproject, re.MULTILINE)
        self.assertIsNotNone(match)
        version = match.group(1)
        for host in (".claude-plugin", ".codex-plugin"):
            manifest = load_json(REPOSITORY_ROOT / "evonest" / host / "plugin.json")
            self.assertEqual(manifest["version"], version)


if __name__ == "__main__":
    unittest.main()
