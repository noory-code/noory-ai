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
# Plainly ships Claude Code output styles, which Codex has no equivalent for. A Codex manifest
# would list it as installable and then do nothing.
CLAUDE_ONLY_PLUGINS = {"plainly"}
CODEX_PLUGIN_DIRECTORIES = {
    name: directory
    for name, directory in PLUGIN_DIRECTORIES.items()
    if name not in CLAUDE_ONLY_PLUGINS
}
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


class PluginContractTest(unittest.TestCase):
    def test_every_plugin_declares_a_claude_manifest(self) -> None:
        for plugin_name, directory in PLUGIN_DIRECTORIES.items():
            with self.subTest(plugin=plugin_name):
                claude = load_json(
                    REPOSITORY_ROOT / directory / ".claude-plugin" / "plugin.json"
                )
                self.assertEqual(claude["name"], plugin_name)
                self.assertRegex(str(claude["version"]), SEMVER)

    def test_dual_host_plugins_keep_their_manifests_in_step(self) -> None:
        for plugin_name, directory in CODEX_PLUGIN_DIRECTORIES.items():
            with self.subTest(plugin=plugin_name):
                plugin_root = REPOSITORY_ROOT / directory
                claude = load_json(plugin_root / ".claude-plugin" / "plugin.json")
                codex = load_json(plugin_root / ".codex-plugin" / "plugin.json")
                self.assertEqual(codex["name"], plugin_name)
                self.assertEqual(claude["version"], codex["version"])
                self.assertRegex(str(codex["version"]), SEMVER)

    def test_a_claude_only_plugin_ships_no_codex_manifest(self) -> None:
        for plugin_name in CLAUDE_ONLY_PLUGINS:
            with self.subTest(plugin=plugin_name):
                directory = PLUGIN_DIRECTORIES[plugin_name]
                self.assertFalse(
                    (REPOSITORY_ROOT / directory / ".codex-plugin").exists()
                )

    def test_each_host_marketplace_registers_the_plugins_that_host_can_run(self) -> None:
        claude = load_json(REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json")
        codex = load_json(REPOSITORY_ROOT / ".agents" / "plugins" / "marketplace.json")
        self.assertEqual(
            {entry["name"] for entry in claude["plugins"]}, set(PLUGIN_DIRECTORIES)
        )
        self.assertEqual(
            {entry["name"] for entry in codex["plugins"]}, set(CODEX_PLUGIN_DIRECTORIES)
        )

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
        for plugin_name, directory in CODEX_PLUGIN_DIRECTORIES.items():
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
