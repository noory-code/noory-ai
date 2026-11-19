"""Hook commands pick the interpreter name the host actually provides.

A python.org install on Windows ships `python.exe` and no `python3.exe`, and a hook that cannot
start is a non-blocking error: the tool call goes ahead with no gate. Every command therefore
selects `python` when `OS` is `Windows_NT` and `python3` everywhere else.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOKS_JSON = Path(__file__).resolve().parents[1] / "hooks.json"
SELECTOR = 'case "$OS" in Windows_NT) p=python;; *) p=python3;; esac; "$p" '


def hook_commands() -> list[str]:
    config = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    return [
        hook["command"]
        for groups in config["hooks"].values()
        for group in groups
        for hook in group["hooks"]
        if hook.get("type") == "command"
    ]


class HookCommandInterpreterTest(unittest.TestCase):
    def test_every_command_selects_the_interpreter_by_host(self) -> None:
        commands = hook_commands()
        self.assertTrue(commands)
        for command in commands:
            with self.subTest(command=command):
                self.assertTrue(
                    command.startswith(SELECTOR),
                    "hook command must start with the host interpreter selector",
                )
                self.assertNotIn("python3 ", command[len(SELECTOR) :])

    @unittest.skipUnless(shutil.which("sh"), "needs a POSIX shell")
    def test_selector_runs_the_name_the_host_provides(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            bin_dir = Path(raw)
            for name in ("python", "python3"):
                fake = bin_dir / name
                fake.write_text(f"#!/bin/sh\necho {name}\n", encoding="utf-8")
                fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            base_env = {
                key: value for key, value in os.environ.items() if key not in {"OS", "PATH"}
            }
            base_env["PATH"] = f"{bin_dir}{os.pathsep}{os.environ['PATH']}"
            base_env["CLAUDE_PLUGIN_ROOT"] = str(HOOKS_JSON.parent.parent)
            cases = (({}, "python3"), ({"OS": "Windows_NT"}, "python"))
            for command in hook_commands():
                for extra, expected in cases:
                    with self.subTest(command=command, os=extra.get("OS")):
                        result = subprocess.run(
                            ["sh", "-c", command],
                            env={**base_env, **extra},
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            check=False,
                        )
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(result.stdout.strip(), expected)


if __name__ == "__main__":
    unittest.main()
