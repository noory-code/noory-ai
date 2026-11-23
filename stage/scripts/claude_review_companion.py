#!/usr/bin/env python3
"""Stand in for the Codex companion by running the same prompt through `claude -p`.

A session without Codex (a cloud session) can still run the project's configured
Codex review commands unchanged: point `STAGE_CODEX_COMPANION` at this script and
`codex_companion.py` hands it the companion's arguments. The prompt is the last
argument; the Codex-only flags before it are ignored. The result is a same-model
review, never a cross-venue one; the cloud-execution procedure requires the card to
say so.

The reviewer judges by running (DE-00000101), so it may run any shell command: the
card's stored checks (for example `audit_stage.py`) and probes it chooses itself, on
Windows through the PowerShell tool as well as Bash. Its file-edit tools may write
only `$STAGE_REVIEW_VERDICT_FILE`, and it gets `--add-dir` for the folder of
`$STAGE_CHANGED_PATHS_FILE`, which lives outside the project.

What still holds the reviewer back, and what does not:

- A shell command can write project files. `close_work.py` and the supervised driver
  compare the repository around every review command, this one included, and fail a
  review that changed anything but its verdict (`close_work.reject_review_writes`).
- `DENIED_COMMANDS` refuses the commands that publish or record a change (`git push`,
  `git commit`). Claude Code matches these rules against each command of a compound
  line, but a command hidden inside another program (`sh -c`, a script) is not seen:
  the rules stop a mistake, not a determined reviewer.
- Nothing here sees a change outside the repository (another checkout, the home
  folder, a remote service). DE-00000101 chose this weakness knowingly; one observed
  case is its stated reason to revisit the choice.

The project's own Claude reviewer command runs through this script as well, so both
review paths share these permissions.

Usage (from the project root):
    STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py \\
        python3 stage/skills/stage-retrospective/close_work.py ...
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path, PurePath

MODEL_ENV = "STAGE_CLAUDE_REVIEW_MODEL"
DEFAULT_MODEL = "opus[1m]"


def absolute_rule_path(path: PurePath) -> str:
    """Spell an absolute path the way an Edit(path) permission rule matches it.

    A leading `//` makes a rule path absolute. Claude Code matches a Windows path in
    its POSIX spelling, `/c/dir/file`, so `C:/dir/file` becomes `//c/dir/file`; a
    rule that keeps the `C:` matches nothing and the reviewer's write is denied.
    """
    posix = path.as_posix()
    drive = path.drive
    if len(drive) == 2 and drive[1] == ":":
        posix = "/" + drive[0].lower() + posix[2:]
    return "/" + posix


# Commands the reviewer never needs: they publish or record a change.
DENIED_COMMANDS = ("git push", "git commit")


def shell_tools(platform: str) -> list[str]:
    """Name every shell tool the reviewer runs commands through.

    On Windows Claude Code offers a PowerShell tool beside Bash, and a `Bash` rule
    does not cover it: a reviewer that picks PowerShell is denied and judges from
    records instead of a run.
    """
    tools = ["Bash"]
    if platform == "win32":
        tools.append("PowerShell")
    return tools


def denied_rules(platform: str) -> list[str]:
    """One deny rule per shell tool and denied command, with and without arguments."""

    rules = []
    for tool in shell_tools(platform):
        for command in DENIED_COMMANDS:
            rules += [f"{tool}({command})", f"{tool}({command}:*)"]
    return rules


def claude_command(
    argv: list[str], environ: dict[str, str], claude: str, platform: str = sys.platform
) -> list[str]:
    if not argv:
        raise ValueError("expected the review prompt as the last argument")
    verdict_file = environ.get("STAGE_REVIEW_VERDICT_FILE", "")
    if not verdict_file:
        raise ValueError("STAGE_REVIEW_VERDICT_FILE is required")
    command = [claude, "-p"]
    changed_paths = environ.get("STAGE_CHANGED_PATHS_FILE", "")
    if changed_paths:
        command += ["--add-dir", str(Path(changed_paths).parent)]
    # Only Edit(path) rules govern file writes; a Write(path) rule is ignored with a
    # warning.
    verdict_rule = absolute_rule_path(Path(verdict_file).resolve())
    command += [
        "--model",
        environ.get(MODEL_ENV) or DEFAULT_MODEL,
        "--allowedTools",
        f"Edit({verdict_rule})",
        *shell_tools(platform),
        # A deny rule wins over an allow rule.
        "--disallowedTools",
        *denied_rules(platform),
        # These options take several values; `--` ends them before the prompt.
        "--",
        argv[-1],
    ]
    return command


def main(argv: list[str]) -> int:
    claude = shutil.which("claude")
    if claude is None:
        print("claude_review_companion: `claude` is not on PATH", file=sys.stderr)
        return 127
    try:
        command = claude_command(argv, dict(os.environ), claude)
    except ValueError as exc:
        print(f"claude_review_companion: {exc}", file=sys.stderr)
        return 2
    return subprocess.run(command).returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
