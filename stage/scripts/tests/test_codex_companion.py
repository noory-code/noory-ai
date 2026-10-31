from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
REPO_ROOT = SCRIPTS.parents[1]
CLI = SCRIPTS / "codex_companion.py"
sys.path.insert(0, str(SCRIPTS))
import codex_companion  # noqa: E402


def write_companion(directory: Path, body: str = "") -> Path:
    script = directory / "scripts" / "codex-companion.mjs"
    script.parent.mkdir(parents=True)
    script.write_text(body, encoding="utf-8")
    return script


def write_install_record(home: Path, entries: object) -> None:
    record = home / ".claude/plugins/installed_plugins.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(
        json.dumps({"version": 2, "plugins": {"codex@openai-codex": entries}}),
        encoding="utf-8",
    )


class ResolveCompanionTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        self.cache = self.home / ".claude/plugins/cache/openai-codex/codex"

    def test_override_wins_over_every_install(self):
        write_companion(self.cache / "1.0.6")
        override = self.home / "custom/companion.mjs"

        resolved = codex_companion.resolve_companion(
            {"STAGE_CODEX_COMPANION": str(override)}, self.home
        )

        self.assertEqual(override, resolved)

    def test_recorded_user_install_beats_project_install_and_cache(self):
        project_script = write_companion(self.home / "project-install")
        user_script = write_companion(self.home / "user-install")
        write_companion(self.cache / "9.9.9")
        write_install_record(
            self.home,
            [
                {"scope": "project", "installPath": str(project_script.parents[1])},
                {"scope": "user", "installPath": str(user_script.parents[1])},
            ],
        )

        self.assertEqual(user_script, codex_companion.resolve_companion({}, self.home))

    def test_recorded_install_without_the_script_falls_through(self):
        cached = write_companion(self.cache / "1.0.7")
        write_install_record(
            self.home,
            [{"scope": "user", "installPath": str(self.home / "removed-install")}],
        )

        self.assertEqual(cached, codex_companion.resolve_companion({}, self.home))

    def test_cache_fallback_picks_the_highest_version_numerically(self):
        write_companion(self.cache / "1.0.9")
        highest = write_companion(self.cache / "1.0.10")
        (self.cache / "2.0.0").mkdir(parents=True)

        self.assertEqual(highest, codex_companion.resolve_companion({}, self.home))

    def test_nothing_installed_resolves_to_none(self):
        write_install_record(self.home, "not a list")

        self.assertIsNone(codex_companion.resolve_companion({}, self.home))


class CompanionCliTest(unittest.TestCase):
    def run_cli(self, home: Path, extra_env: dict[str, str], *args: str):
        env = {
            key: value
            for key, value in os.environ.items()
            if key != "STAGE_CODEX_COMPANION"
        }
        env.update({"HOME": str(home), "USERPROFILE": str(home), **extra_env})
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def test_missing_companion_exits_127_and_names_what_it_searched(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self.run_cli(Path(tmp), {}, "task")

        self.assertEqual(127, proc.returncode)
        self.assertIn("no Codex companion script found", proc.stderr)
        self.assertIn("installed_plugins.json", proc.stderr)

    @unittest.skipUnless(shutil.which("node"), "node is not installed")
    def test_runs_the_companion_with_arguments_and_returns_its_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = write_companion(
                Path(tmp) / "install",
                "console.log(JSON.stringify(process.argv.slice(2))); process.exit(3);\n",
            )

            proc = self.run_cli(
                Path(tmp),
                {"STAGE_CODEX_COMPANION": str(script)},
                "task",
                "--model",
                "m",
                "two words",
            )

        self.assertEqual(3, proc.returncode, proc.stderr)
        self.assertEqual(["task", "--model", "m", "two words"], json.loads(proc.stdout))


class ProjectSettingsTest(unittest.TestCase):
    def test_codex_commands_resolve_the_companion_instead_of_a_fixed_path(self):
        settings = json.loads((REPO_ROOT / ".stage/settings.json").read_text(encoding="utf-8"))
        review = settings["review"]
        commands = {
            "executor.codex": settings["executors"]["codex"],
            "reviewer.codex": review["reviewers"]["codex"],
            **{
                f"strength.{name}": command
                for name, command in review["strengths"].items()
                if command
            },
        }

        self.assertEqual(6, len(commands))
        for name, command in commands.items():
            with self.subTest(name=name):
                self.assertIn("python3 stage/scripts/codex_companion.py task ", command)
                self.assertNotIn("codex-companion.mjs", command)
                self.assertNotIn("/Users/", command)

    def test_codex_reaper_lists_and_cancels_jobs_through_the_resolver(self):
        settings = json.loads((REPO_ROOT / ".stage/settings.json").read_text(encoding="utf-8"))
        reaper = settings["reapers"]["codex"]

        self.assertIn(
            "spawnSync('python3', ['stage/scripts/codex_companion.py', 'status', '--all', '--json']",
            reaper,
        )
        self.assertIn(
            "spawnSync('python3', ['stage/scripts/codex_companion.py', 'cancel', job.id]",
            reaper,
        )
        self.assertNotIn("codex-companion.mjs", reaper)
        self.assertNotIn("/Users/", reaper)


    @unittest.skipUnless(shutil.which("node"), "node is not installed")
    def test_codex_reaper_cancels_only_the_target_cards_jobs(self):
        settings = json.loads((REPO_ROOT / ".stage/settings.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            cancelled = Path(tmp) / "cancelled.txt"
            companion = write_companion(
                Path(tmp) / "install",
                "import { appendFileSync } from 'node:fs';\n"
                "const [command, jobId] = process.argv.slice(2);\n"
                "if (command === 'status') {\n"
                "  console.log(JSON.stringify({ running: [\n"
                "    { id: 'j1', request: { prompt: 'work on /cards/W-1.md now' } },\n"
                "    { id: 'j2', request: { prompt: 'work on /cards/W-2.md now' } },\n"
                "  ] }));\n"
                "} else if (command === 'cancel') {\n"
                "  appendFileSync(process.env.FAKE_CANCEL_LOG, jobId + '\\n');\n"
                "}\n",
            )
            env = {
                **os.environ,
                "STAGE_CODEX_COMPANION": str(companion),
                "STAGE_WORK_ITEM_PATH": "/cards/W-1.md",
                "FAKE_CANCEL_LOG": str(cancelled),
            }

            proc = subprocess.run(
                settings["reapers"]["codex"],
                shell=True,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                env=env,
            )
            cancelled_jobs = cancelled.read_text(encoding="utf-8").split()

        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(["j1"], cancelled_jobs)

if __name__ == "__main__":
    unittest.main()
