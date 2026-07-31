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
        for profile in ("baseline", "brief", "guided", "professional"):
            self.assertIn(profile, result.stdout)
        self.assertIn("plain -> baseline", result.stdout)

    def test_set_profile_and_reset_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            settings = root / ".plainly" / "settings.json"

            configured = self.run_cli(
                "set-profile",
                "guided",
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
                "--project-root",
                str(root),
                home=home,
            )
            self.assertEqual(reset.returncode, 0, reset.stderr)
            self.assertFalse(settings.exists())

    def test_set_profile_normalizes_plain_compatibility_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = root / ".plainly" / "settings.json"

            result = self.run_cli(
                "set-profile",
                "plain",
                "--project-root",
                str(root),
                home=root / "home",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(settings.read_text(encoding="utf-8")),
                {"profile": "baseline"},
            )

    def test_interview_exact_match_selects_a_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.run_cli(
                "apply-interview",
                "--length",
                "standard",
                "--structure",
                "step-by-step",
                "--tone",
                "conversational",
                "--project-root",
                str(root),
                home=root / "home",
            )
            settings = root / ".plainly" / "settings.json"

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(settings.read_text(encoding="utf-8")),
                {"profile": "guided"},
            )
            self.assertFalse((root / ".plainly" / "interview-style.md").exists())

    def test_interview_conflict_writes_composed_in_root_style(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.run_cli(
                "apply-interview",
                "--length",
                "shortest",
                "--structure",
                "direct",
                "--tone",
                "formal",
                "--project-root",
                str(root),
                home=root / "home",
            )
            style_file = root / ".plainly" / "interview-style.md"
            settings = root / ".plainly" / "settings.json"

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(settings.read_text(encoding="utf-8")),
                {"style_file": ".plainly/interview-style.md"},
            )
            style = style_file.read_text(encoding="utf-8")
            self.assertIn("Lead with the answer", style)
            self.assertNotIn("Do not state guesses as facts", style)
            self.assertIn("Use as few words as the task allows", style)
            self.assertIn("neutral workplace register", style)
            self.assertNotIn("ordered steps", style)

            shown = self.run_cli("show", "--project-root", str(root), home=root / "home")
            self.assertEqual(shown.returncode, 0, shown.stderr)
            self.assertIn(f"source: file:{style_file.resolve()}", shown.stdout)

    def test_interview_custom_file_cannot_escape_through_plainly_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "project"
            outside = base / "outside"
            root.mkdir()
            outside.mkdir()
            try:
                (root / ".plainly").symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"Symlink creation is unavailable: {exc}")

            result = self.run_cli(
                "apply-interview",
                "--length",
                "shortest",
                "--structure",
                "direct",
                "--tone",
                "formal",
                "--project-root",
                str(root),
                home=base / "home",
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("project root", result.stderr)
            self.assertFalse((outside / "interview-style.md").exists())

    def test_set_file_stores_a_project_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            style_file = root / "custom.md"
            style_file.write_text("Use short sentences.", encoding="utf-8")

            result = self.run_cli(
                "set-file",
                str(style_file),
                "--project-root",
                str(root),
                home=home,
            )
            settings = root / ".plainly" / "settings.json"
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(settings.read_text(encoding="utf-8")),
                {"style_file": "custom.md"},
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
                "--project-root",
                str(root),
                home=home,
            )
            settings = root / ".plainly" / "settings.json"

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
                "--project-root",
                str(root),
                home=home,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("project root", result.stderr)
            self.assertFalse((root / ".plainly" / "settings.json").exists())

    def test_scope_option_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli(
                "set-profile",
                "plain",
                "--scope",
                "user",
                "--project-root",
                tmp,
                home=Path(tmp) / "home",
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments", result.stderr)

    def test_user_flag_writes_the_home_default_and_leaves_the_project_alone(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            home.mkdir()

            result = self.run_cli(
                "set-profile",
                "decision",
                "--user",
                "--project-root",
                str(root),
                home=home,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("user profile set to decision", result.stdout)
            self.assertFalse((root / ".plainly" / "settings.json").exists())
            self.assertEqual(
                json.loads((home / ".plainly" / "settings.json").read_text(encoding="utf-8")),
                {"profile": "decision"},
            )

    def test_user_default_can_be_reset_without_touching_the_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            user_settings = home / ".plainly" / "settings.json"
            user_settings.parent.mkdir(parents=True)
            user_settings.write_text(json.dumps({"profile": "brief"}), encoding="utf-8")
            project_settings = root / ".plainly" / "settings.json"
            project_settings.parent.mkdir(parents=True)
            project_settings.write_text(json.dumps({"profile": "guided"}), encoding="utf-8")

            result = self.run_cli("reset", "--user", "--project-root", str(root), home=home)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("user settings removed", result.stdout)
            self.assertFalse(user_settings.exists())
            self.assertTrue(project_settings.exists())

    def test_set_file_has_no_user_form(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            style = root / "style.md"
            style.write_text("Use one short paragraph.", encoding="utf-8")

            result = self.run_cli(
                "set-file",
                str(style),
                "--user",
                "--project-root",
                str(root),
                home=root / "home",
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments", result.stderr)


if __name__ == "__main__":
    unittest.main()
