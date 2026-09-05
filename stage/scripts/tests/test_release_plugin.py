from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

CLI_PATH = Path(__file__).resolve().parents[1] / "release_plugin.py"


class ReleasePluginCliTest(unittest.TestCase):
    def make_repository(
        self,
        *,
        unreleased_body: str = "- Ship the queued Stage changes.\n",
        changelog_version: str = "0.54.4",
        claude_version: str = "0.54.4",
        codex_version: str = "0.54.4",
    ) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary_directory = tempfile.TemporaryDirectory()
        repository_root = Path(temporary_directory.name)
        plugin_root = repository_root / "stage"
        (plugin_root / ".claude-plugin").mkdir(parents=True)
        (plugin_root / ".codex-plugin").mkdir(parents=True)
        (plugin_root / "CHANGELOG.md").write_text(
            (
                "# Changelog\n\n"
                "## Unreleased\n\n"
                f"{unreleased_body}"
                f"\n## {changelog_version} — 2026-07-28\n\n"
                "- Previous release.\n"
            ),
            encoding="utf-8",
        )
        self.write_manifest(
            plugin_root / ".claude-plugin/plugin.json",
            claude_version,
        )
        self.write_manifest(
            plugin_root / ".codex-plugin/plugin.json",
            codex_version,
        )
        return temporary_directory, repository_root

    @staticmethod
    def write_manifest(path: Path, version: str) -> None:
        path.write_text(
            json.dumps({"name": "stage", "version": version}, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def snapshot_plugin(repository_root: Path) -> dict[str, str]:
        plugin_root = repository_root / "stage"
        relative_paths = (
            "CHANGELOG.md",
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
        )
        return {
            relative_path: (plugin_root / relative_path).read_text(encoding="utf-8")
            for relative_path in relative_paths
        }

    def run_cli(
        self,
        repository_root: Path,
        bump: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(CLI_PATH),
                "stage",
                "--bump",
                bump,
                "--repository-root",
                str(repository_root),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_release_reopens_unreleased_section_and_updates_both_manifests(self):
        temporary_directory, repository_root = self.make_repository()
        with temporary_directory:
            result = self.run_cli(repository_root, "minor")

            self.assertEqual(0, result.returncode, result.stderr)
            plugin_root = repository_root / "stage"
            changelog = (plugin_root / "CHANGELOG.md").read_text(encoding="utf-8")
            claude_manifest = json.loads(
                (plugin_root / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
            )
            codex_manifest = json.loads(
                (plugin_root / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
            )

        self.assertIn(f"## 0.55.0 — {date.today().isoformat()}", changelog)
        self.assertIn("## Unreleased\n\n", changelog)
        self.assertEqual("0.55.0", claude_manifest["version"])
        self.assertEqual("0.55.0", codex_manifest["version"])
        self.assertIn("Released stage 0.55.0", result.stdout)

    def test_next_queued_change_can_be_released_after_the_first_release(self):
        temporary_directory, repository_root = self.make_repository()
        with temporary_directory:
            first_result = self.run_cli(repository_root, "patch")
            changelog_path = repository_root / "stage" / "CHANGELOG.md"
            after_first = changelog_path.read_text(encoding="utf-8")
            changelog_path.write_text(
                after_first.replace(
                    "## Unreleased\n\n",
                    "## Unreleased\n\n- Ship the next queued change.\n\n",
                    1,
                ),
                encoding="utf-8",
            )

            second_result = self.run_cli(repository_root, "patch")
            after_second = changelog_path.read_text(encoding="utf-8")

        self.assertEqual(0, first_result.returncode, first_result.stderr)
        self.assertEqual(0, second_result.returncode, second_result.stderr)
        self.assertIn("## Unreleased\n\n", after_second)
        self.assertIn(
            f"## 0.54.6 — {date.today().isoformat()}",
            after_second,
        )
        self.assertIn(
            f"## 0.54.5 — {date.today().isoformat()}",
            after_second,
        )

    def test_release_preserves_manifest_formatting_except_for_version(self):
        temporary_directory, repository_root = self.make_repository()
        plugin_root = repository_root / "stage"
        claude_path = plugin_root / ".claude-plugin/plugin.json"
        codex_path = plugin_root / ".codex-plugin/plugin.json"
        claude_before = (
            "{\n"
            '    "name": "stage",\n'
            '    "version": "0.54.4",\n'
            '    "description": "Claude manifest"\n'
            "}\n"
        )
        codex_before = (
            "{\n"
            '\t"name": "stage",\n'
            '\t"version": "0.54.4",\n'
            '\t"description": "Codex manifest"\n'
            "}\n"
        )
        claude_path.write_text(claude_before, encoding="utf-8")
        codex_path.write_text(codex_before, encoding="utf-8")

        with temporary_directory:
            result = self.run_cli(repository_root, "patch")
            claude_after = claude_path.read_text(encoding="utf-8")
            codex_after = codex_path.read_text(encoding="utf-8")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            claude_before.replace('"0.54.4"', '"0.54.5"', 1),
            claude_after,
        )
        self.assertEqual(
            codex_before.replace('"0.54.4"', '"0.54.5"', 1),
            codex_after,
        )

    def test_empty_unreleased_section_is_rejected_without_changes(self):
        temporary_directory, repository_root = self.make_repository(unreleased_body="")
        with temporary_directory:
            before = self.snapshot_plugin(repository_root)
            result = self.run_cli(repository_root, "patch")
            after = self.snapshot_plugin(repository_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("Unreleased section is empty", result.stderr)
        self.assertEqual(before, after)

    def test_changelog_and_manifest_version_mismatch_is_rejected_without_changes(self):
        temporary_directory, repository_root = self.make_repository(
            changelog_version="0.54.3"
        )
        with temporary_directory:
            before = self.snapshot_plugin(repository_root)
            result = self.run_cli(repository_root, "patch")
            after = self.snapshot_plugin(repository_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn(
            "latest changelog version 0.54.3 does not match manifest version 0.54.4",
            result.stderr,
        )
        self.assertEqual(before, after)

    def test_a_single_host_plugin_releases_from_the_manifest_it_has(self):
        # A plugin can target one host only. Requiring both manifests would leave it unreleasable.
        temporary_directory, repository_root = self.make_repository()
        with temporary_directory:
            plugin_root = repository_root / "stage"
            (plugin_root / ".codex-plugin/plugin.json").unlink()
            (plugin_root / ".codex-plugin").rmdir()

            result = self.run_cli(repository_root, "patch")

            self.assertEqual(0, result.returncode, result.stderr)
            claude_manifest = json.loads(
                (plugin_root / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
            )
            changelog = (plugin_root / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertEqual("0.54.5", claude_manifest["version"])
        self.assertIn(f"## 0.54.5 — {date.today().isoformat()}", changelog)

    def test_release_refuses_a_directory_with_no_manifest_at_all(self):
        temporary_directory, repository_root = self.make_repository()
        with temporary_directory:
            plugin_root = repository_root / "stage"
            before = (plugin_root / "CHANGELOG.md").read_text(encoding="utf-8")
            for host in (".claude-plugin", ".codex-plugin"):
                (plugin_root / host / "plugin.json").unlink()
                (plugin_root / host).rmdir()

            result = self.run_cli(repository_root, "patch")
            after = (plugin_root / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("no plugin manifest found", result.stderr)
        self.assertEqual(before, after)

    def test_bump_must_be_an_explicit_supported_argument(self):
        temporary_directory, repository_root = self.make_repository()
        with temporary_directory:
            before = self.snapshot_plugin(repository_root)
            result = self.run_cli(repository_root, "feature")
            after = self.snapshot_plugin(repository_root)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid choice", result.stderr)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
