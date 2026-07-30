from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PLUGIN_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from plainly.runtime import MAX_STYLE_BYTES, resolve_style  # noqa: E402


class RuntimeTest(unittest.TestCase):
    def test_baseline_is_the_default_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resolved = resolve_style(PLUGIN_ROOT, root, environ={}, home=root / "home")

        self.assertEqual(resolved.profile, "baseline")
        self.assertEqual(resolved.source, "builtin:baseline")
        self.assertIn("plain language", resolved.text.lower())

    def test_every_builtin_profile_includes_the_baseline_principles(self) -> None:
        baseline_phrases = (
            "Lead with the answer",
            "plain language",
            "short sentences",
            "Distinguish facts from recommendations",
        )
        for profile in ("baseline", "brief", "guided", "professional"):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                resolved = resolve_style(
                    PLUGIN_ROOT,
                    root,
                    environ={"NOORY_STYLE_PROFILE": profile},
                    home=root / "home",
                )

                self.assertEqual(resolved.profile, profile)
                for phrase in baseline_phrases:
                    self.assertIn(phrase, resolved.text)

    def test_plain_alias_resolves_from_environment_and_saved_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            from_environment = resolve_style(
                PLUGIN_ROOT,
                root,
                environ={"NOORY_STYLE_PROFILE": "plain"},
                home=root / "home",
            )
            settings = root / ".plainly" / "settings.json"
            settings.parent.mkdir(parents=True)
            settings.write_text(json.dumps({"profile": "plain"}), encoding="utf-8")
            from_settings = resolve_style(PLUGIN_ROOT, root, environ={}, home=root / "home")

        self.assertEqual(from_environment.profile, "baseline")
        self.assertEqual(from_environment.source, "env:NOORY_STYLE_PROFILE")
        self.assertEqual(from_settings.profile, "baseline")
        self.assertEqual(from_settings.source, f"settings:{settings.resolve()}")

    def test_environment_profile_overrides_saved_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = root / ".plainly" / "settings.json"
            settings.parent.mkdir(parents=True)
            settings.write_text(json.dumps({"profile": "guided"}), encoding="utf-8")

            resolved = resolve_style(
                PLUGIN_ROOT,
                root,
                environ={"NOORY_STYLE_PROFILE": "brief"},
                home=root / "home",
            )

        self.assertEqual(resolved.profile, "brief")
        self.assertEqual(resolved.source, "env:NOORY_STYLE_PROFILE")

    def test_environment_file_is_reloaded_for_each_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            style_file = root / "style.md"
            style_file.write_text("First external style.", encoding="utf-8")
            environ = {"NOORY_STYLE_FILE": str(style_file)}

            first = resolve_style(PLUGIN_ROOT, root, environ=environ, home=root / "home")
            style_file.write_text("Updated external style.", encoding="utf-8")
            second = resolve_style(PLUGIN_ROOT, root, environ=environ, home=root / "home")

        self.assertEqual(first.text, "First external style.")
        self.assertEqual(second.text, "Updated external style.")
        self.assertEqual(second.source, f"file:{style_file.resolve()}")
        self.assertIsNone(second.profile)

    def test_project_settings_are_the_only_persisted_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            user_settings = home / ".noory" / "plainly" / "settings.json"
            project_settings = root / ".plainly" / "settings.json"
            user_settings.parent.mkdir(parents=True)
            project_settings.parent.mkdir(parents=True)
            user_settings.write_text(json.dumps({"profile": "professional"}), encoding="utf-8")
            project_settings.write_text(json.dumps({"profile": "guided"}), encoding="utf-8")

            resolved = resolve_style(PLUGIN_ROOT, root, environ={}, home=home)

        self.assertEqual(resolved.profile, "guided")
        self.assertEqual(resolved.source, f"settings:{project_settings.resolve()}")

    def test_legacy_noory_settings_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            project_legacy = root / ".noory" / "plainly" / "settings.json"
            user_legacy = home / ".noory" / "plainly" / "settings.json"
            project_legacy.parent.mkdir(parents=True)
            user_legacy.parent.mkdir(parents=True)
            project_legacy.write_text(json.dumps({"profile": "guided"}), encoding="utf-8")
            user_legacy.write_text(json.dumps({"profile": "professional"}), encoding="utf-8")

            resolved = resolve_style(
                PLUGIN_ROOT,
                root,
                environ={},
                home=home,
            )

        self.assertEqual(resolved.profile, "baseline")
        self.assertEqual(resolved.source, "builtin:baseline")

    def test_project_relative_style_file_is_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = root / ".plainly" / "settings.json"
            style_file = root / ".plainly" / "style.md"
            settings.parent.mkdir(parents=True)
            settings.write_text(
                json.dumps({"style_file": ".plainly/style.md"}),
                encoding="utf-8",
            )
            style_file.write_text("Explain decisions in plain language.", encoding="utf-8")

            resolved = resolve_style(
                PLUGIN_ROOT,
                root,
                environ={},
                home=root / "home",
            )

        self.assertEqual(resolved.text, "Explain decisions in plain language.")
        self.assertEqual(resolved.source, f"file:{style_file.resolve()}")
        self.assertIsNone(resolved.profile)

    def test_missing_custom_file_falls_back_to_profile_in_the_same_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = root / ".plainly" / "settings.json"
            settings.parent.mkdir(parents=True)
            settings.write_text(
                json.dumps({"style_file": "missing.md", "profile": "guided"}),
                encoding="utf-8",
            )

            resolved = resolve_style(PLUGIN_ROOT, root, environ={}, home=root / "home")

        self.assertEqual(resolved.profile, "guided")
        self.assertTrue(any("missing.md" in message for message in resolved.diagnostics))

    def test_oversized_external_file_falls_back_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            style_file = root / "large.md"
            style_file.write_text("x" * (MAX_STYLE_BYTES + 1), encoding="utf-8")

            resolved = resolve_style(
                PLUGIN_ROOT,
                root,
                environ={"NOORY_STYLE_FILE": str(style_file)},
                home=root / "home",
            )

        self.assertEqual(resolved.profile, "baseline")
        self.assertTrue(any("8192" in message for message in resolved.diagnostics))

    def test_malformed_project_settings_fall_back_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = root / ".plainly" / "settings.json"
            settings.parent.mkdir(parents=True)
            settings.write_text("{not-json", encoding="utf-8")

            resolved = resolve_style(PLUGIN_ROOT, root, environ={}, home=root / "home")

        self.assertEqual(resolved.profile, "baseline")
        self.assertTrue(any("settings" in message for message in resolved.diagnostics))

    def test_non_utf8_external_file_falls_back_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            style_file = root / "invalid.md"
            style_file.write_bytes(b"\xff\xfe")

            resolved = resolve_style(
                PLUGIN_ROOT,
                root,
                environ={"NOORY_STYLE_FILE": str(style_file)},
                home=root / "home",
            )

        self.assertEqual(resolved.profile, "baseline")
        self.assertTrue(any("UTF-8" in message for message in resolved.diagnostics))

    def test_relative_environment_file_resolves_from_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            style_file = root / "styles" / "relative.md"
            style_file.parent.mkdir()
            style_file.write_text("Use relative style.", encoding="utf-8")

            resolved = resolve_style(
                PLUGIN_ROOT,
                root,
                environ={"NOORY_STYLE_FILE": "styles/relative.md"},
                home=root / "home",
            )

        self.assertEqual(resolved.text, "Use relative style.")
        self.assertEqual(resolved.source, f"file:{style_file.resolve()}")

    def test_project_settings_cannot_read_outside_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "project"
            root.mkdir()
            outside = base / "private.md"
            outside.write_text("Private local content.", encoding="utf-8")
            settings = root / ".plainly" / "settings.json"
            settings.parent.mkdir(parents=True)
            settings.write_text(
                json.dumps({"style_file": "../private.md"}),
                encoding="utf-8",
            )

            resolved = resolve_style(PLUGIN_ROOT, root, environ={}, home=base / "home")

        self.assertEqual(resolved.profile, "baseline")
        self.assertNotIn("Private local content.", resolved.text)
        self.assertTrue(any("project root" in message for message in resolved.diagnostics))

    def test_project_settings_cannot_escape_through_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "project"
            root.mkdir()
            outside = base / "private.md"
            outside.write_text("Private symlink content.", encoding="utf-8")
            link = root / "style.md"
            try:
                link.symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"Symlink creation is unavailable: {exc}")
            settings = root / ".plainly" / "settings.json"
            settings.parent.mkdir(parents=True)
            settings.write_text(json.dumps({"style_file": "style.md"}), encoding="utf-8")

            resolved = resolve_style(PLUGIN_ROOT, root, environ={}, home=base / "home")

        self.assertEqual(resolved.profile, "baseline")
        self.assertNotIn("Private symlink content.", resolved.text)
        self.assertTrue(any("project root" in message for message in resolved.diagnostics))


if __name__ == "__main__":
    unittest.main()
