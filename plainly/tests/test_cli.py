from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = PLUGIN_ROOT / "scripts" / "configure.py"


class ConfigureCliTest(unittest.TestCase):
    def run_cli(self, *args: str, home: Path) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        env["HOME"] = str(home)
        env["USERPROFILE"] = str(home)
        env.pop("HOMEDRIVE", None)
        env.pop("HOMEPATH", None)
        return subprocess.run(
            [sys.executable, str(CLI_PATH), *args],
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

    def test_list_shows_all_builtin_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("list", home=Path(tmp) / "home")

        self.assertEqual(result.returncode, 0, result.stderr)
        for profile in ("brief", "plain", "guided", "professional"):
            self.assertIn(profile, result.stdout)

    def test_set_profile_and_reset_project_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            settings = root / ".noory" / "plainly" / "settings.json"

            configured = self.run_cli(
                "set-profile",
                "guided",
                "--scope",
                "project",
                "--project-root",
                str(root),
                home=home,
            )
            self.assertEqual(configured.returncode, 0, configured.stderr)
            self.assertEqual(
                json.loads(settings.read_text(encoding="utf-8")),
                {"profile": "guided"},
            )

            reset = self.run_cli(
                "reset",
                "--scope",
                "project",
                "--project-root",
                str(root),
                home=home,
            )
            self.assertEqual(reset.returncode, 0, reset.stderr)
            self.assertFalse(settings.exists())

    def test_set_file_stores_a_valid_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            style_file = root / "custom.md"
            style_file.write_text("Use short sentences.", encoding="utf-8")

            result = self.run_cli(
                "set-file",
                str(style_file),
                "--scope",
                "user",
                "--project-root",
                str(root),
                home=home,
            )
            settings = home / ".noory" / "plainly" / "settings.json"
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(settings.read_text(encoding="utf-8")),
                {"style_file": str(style_file.resolve())},
            )

    def test_project_file_inside_project_is_stored_relative_to_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            style_file = root / "styles" / "team.md"
            style_file.parent.mkdir()
            style_file.write_text("Use the team voice.", encoding="utf-8")

            result = self.run_cli(
                "set-file",
                str(style_file),
                "--scope",
                "project",
                "--project-root",
                str(root),
                home=home,
            )
            settings = root / ".noory" / "plainly" / "settings.json"

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(settings.read_text(encoding="utf-8")),
                {"style_file": "styles/team.md"},
            )

            shown = self.run_cli("show", "--project-root", str(root), home=home)
            self.assertEqual(shown.returncode, 0, shown.stderr)
            self.assertIn(f"source: file:{style_file.resolve()}", shown.stdout)

    def test_project_file_outside_project_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "project"
            root.mkdir()
            home = base / "home"
            outside = base / "private.md"
            outside.write_text("Do not expose this file.", encoding="utf-8")

            result = self.run_cli(
                "set-file",
                str(outside),
                "--scope",
                "project",
                "--project-root",
                str(root),
                home=home,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("project root", result.stderr)
            self.assertFalse((root / ".noory" / "plainly" / "settings.json").exists())


if __name__ == "__main__":
    unittest.main()
