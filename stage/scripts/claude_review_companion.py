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
  At close a file that was changed and restored fails the review too, and a write to a
  file Git ignores is told to the person who closes (`review_containment.py`).
- `DENIED_COMMANDS` refuses the commands that publish or record a change (`git push`,
  `git commit`). Claude Code matches these rules against each command of a compound
  line, but a command hidden inside another program (`sh -c`, a script) is not seen:
  the rules stop a mistake, not a determined reviewer.
- Nothing here stops a read or a change outside the repository (another checkout, the
  home folder, a remote service). The reviewer's tool calls are written to
  `$STAGE_REVIEW_TOOL_CALLS_FILE`, and the close tells the person which of them name
  the session record folder (`~/.claude`) or GitHub. A change outside the repository
  is still unseen; DE-00000101 chose this weakness knowingly, and one observed case is
  its stated reason to revisit the choice.
- `REVIEWER_RULES` is added to every prompt, so a reviewer knows what fails its review
  before it tidies up after its own commands.

The project's own Claude reviewer command runs through this script as well, so both
review paths share these permissions.

Usage (from the project root):
    STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py \\
        python3 stage/skills/stage-retrospective/close_work.py ...
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path, PurePath
from typing import IO, Iterable

MODEL_ENV = "STAGE_CLAUDE_REVIEW_MODEL"
DEFAULT_MODEL = "opus[1m]"
# `review_containment.TOOL_CALLS_ENV`; this script imports nothing from the plugin.
TOOL_CALLS_ENV = "STAGE_REVIEW_TOOL_CALLS_FILE"
REVIEWER_RULES = (
    "\n\nRules of this review, checked after you finish:\n"
    "- The repository is compared before and after you. If one of your commands, or the "
    "tests it runs, changes a project file, leave the file as it is and name it in that "
    "criterion's reason. Do not restore it (`git checkout`, `git restore`, `git stash`, "
    "copying a backup over it) and do not delete what your commands created: a restored "
    "file fails the review.\n"
    "- Judge from this checkout. Do not read the session record folder (`~/.claude`) or "
    "GitHub (`gh`, api.github.com); the commands you run are recorded. When a criterion "
    "can only be judged from there, its method is `unable`.\n"
)


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
    # stream-json prints every tool call; `run_reviewer` turns it back into the answer.
    command = [claude, "-p", "--output-format", "stream-json", "--verbose"]
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
        argv[-1] + REVIEWER_RULES,
    ]
    return command


def tool_calls(event: dict[str, object]) -> list[dict[str, object]]:
    """The tool calls one `assistant` event of the stream carries."""

    message = event.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    return [
        {"id": block.get("id", ""), "tool": block.get("name", ""), "input": block.get("input")}
        for block in (content if isinstance(content, list) else [])
        if isinstance(block, dict) and block.get("type") == "tool_use"
    ]


def relay_stream(lines: Iterable[str], record: IO[str] | None, out: IO[str]) -> None:
    """Print the reviewer's answer from a stream-json run and record its tool calls.

    Each call is written as it is seen, so a reviewer stopped at its time limit leaves
    the calls it made. The last record line says the record is whole and names the calls
    the host refused. A line that is not a stream event is printed as it came.
    """

    def write(entry: dict[str, object]) -> None:
        if record is not None:
            record.write(json.dumps(entry, ensure_ascii=False) + "\n")
            record.flush()

    answered = False
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            event = None
        if not isinstance(event, dict):
            out.write(line if line.endswith("\n") else line + "\n")
            continue
        if event.get("type") == "assistant":
            for call in tool_calls(event):
                write(call)
        elif event.get("type") == "result":
            answered = True
            result = event.get("result")
            if isinstance(result, str) and result:
                out.write(result.rstrip("\n") + "\n")
            denials = event.get("permission_denials")
            write(
                {
                    "complete": True,
                    "denied": [
                        denial.get("tool_use_id", "")
                        for denial in (denials if isinstance(denials, list) else [])
                        if isinstance(denial, dict)
                    ],
                }
            )
    if not answered:
        out.write("claude_review_companion: the reviewer ended without a result event\n")
    out.flush()


def run_reviewer(command: list[str], environ: dict[str, str]) -> int:
    record_path = environ.get(TOOL_CALLS_ENV, "")
    record = open(record_path, "a", encoding="utf-8") if record_path else None
    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace"
        )
        assert process.stdout is not None
        # The caller reads this as UTF-8; a locale-encoded stream could not hold every character.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        relay_stream(process.stdout, record, sys.stdout)
        return process.wait()
    finally:
        if record is not None:
            record.close()


def main(argv: list[str]) -> int:
    claude = shutil.which("claude")
    if claude is None:
        print("claude_review_companion: `claude` is not on PATH", file=sys.stderr)
        return 127
    environ = dict(os.environ)
    try:
        command = claude_command(argv, environ, claude)
    except ValueError as exc:
        print(f"claude_review_companion: {exc}", file=sys.stderr)
        return 2
    return run_reviewer(command, environ)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
