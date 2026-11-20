"""Hook commands pick the interpreter name the host actually provides.

A python.org install on Windows ships `python.exe` and no `python3.exe`, so every command selects
`python` when `OS` is `Windows_NT` and `python3` everywhere else.
"""

from __future__ import annotations

import json
from pathlib import Path

HOOKS_JSON = Path(__file__).parent.parent / "hooks" / "hooks.json"
SELECTOR = 'case "$OS" in Windows_NT) p=python;; *) p=python3;; esac; "$p" '


def test_every_hook_command_selects_the_interpreter_by_host() -> None:
    config = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    commands = [
        hook["command"]
        for groups in config["hooks"].values()
        for group in groups
        for hook in group["hooks"]
        if hook.get("type") == "command"
    ]
    assert commands
    for command in commands:
        assert command.startswith(SELECTOR), command
        assert "python3 " not in command[len(SELECTOR) :], command
