#!/usr/bin/env python3
"""Run a reviewer command and append its output to the work log, without shell syntax.

A review command has to do three things: run the reviewer, add its output to the
shared work log as a `### Reviewer report`, and exit with the reviewer's status.
Written in the command string itself, that takes POSIX shell syntax
(`OUT=$(...); STATUS=$?; printf ... >> "$STAGE_WORK_LOG_PATH"`), which `cmd.exe`
cannot run, so a project using it could not close a reviewed card on Windows. This
script does the same three things, so the command string is one plain invocation
that every shell runs.

`close_work.py` and the drivers pass the review inputs as `STAGE_*` environment
variables, and the prompt names them as `$STAGE_...`. A POSIX shell expands those
before this script starts; `cmd.exe` does not, so this script expands `$STAGE_NAME`
and `${STAGE_NAME}` in every argument itself. An unset variable expands to an empty
string, as it does in a POSIX shell.

Usage (from the project root):
    python3 stage/scripts/run_review.py --label codex -- \\
        python3 stage/scripts/codex_companion.py task --model <model> "<prompt>"

`--env NAME=VALUE` (repeatable) sets a variable for the reviewer, replacing the POSIX
`NAME=VALUE command` prefix. A reviewer named `python3` or `python` runs with this
interpreter, so the command does not depend on a `python3` executable on PATH.

`--timeout SECONDS` (default: close_work's review timeout) bounds the reviewer. When it
runs out, the reviewer's whole process tree ends on every platform, the partial output and
a timeout line go to the work log, and the script exits with status 124, so the review fails.
The reviewer's stdout comes first in the report and its stderr after it.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (STAGE_ROOT / "hooks", STAGE_ROOT / "skills" / "stage-retrospective"):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from close_work import DEFAULT_REVIEW_TIMEOUT  # noqa: E402
from stage_process import run_bounded  # noqa: E402

TIMEOUT_STATUS = 124
WORK_LOG_ENV = "STAGE_WORK_LOG_PATH"
STAGE_VARIABLE = re.compile(r"\$(?:\{(STAGE_[A-Z0-9_]+)\}|(STAGE_[A-Z0-9_]+))")
PYTHON_NAMES = {"python3", "python"}


def expand_stage_variables(text: str, environ: dict[str, str]) -> str:
    """Replace `$STAGE_NAME` and `${STAGE_NAME}` with their values, or nothing when unset."""

    return STAGE_VARIABLE.sub(lambda match: environ.get(match.group(1) or match.group(2), ""), text)


def parse_assignments(pairs: list[str]) -> dict[str, str]:
    assignments: dict[str, str] = {}
    for pair in pairs:
        name, separator, value = pair.partition("=")
        if not separator or not name:
            raise ValueError(f"--env expects NAME=VALUE, got {pair!r}")
        assignments[name] = value
    return assignments


def reviewer_command(command: list[str], environ: dict[str, str]) -> list[str]:
    if not command:
        raise ValueError("expected the reviewer command after `--`")
    expanded = [expand_stage_variables(argument, environ) for argument in command]
    if expanded[0] in PYTHON_NAMES:
        expanded[0] = sys.executable
    return expanded


def positive_seconds(text: str) -> int:
    try:
        seconds = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected whole seconds, got {text!r}") from None
    if seconds <= 0:
        raise argparse.ArgumentTypeError(f"expected a positive number of seconds, got {text}")
    return seconds


def reviewer_output(stdout: object, stderr: object) -> str:
    # TimeoutExpired carries str | bytes | None; run_bounded always hands over text.
    parts = [part.rstrip("\n") for part in (stdout, stderr) if isinstance(part, str)]
    return "\n".join(part for part in parts if part)


def append_report(log_path: Path, output: str) -> None:
    # Append bytes so the log keeps its line endings and encoding on every platform.
    with log_path.open("ab") as handle:
        handle.write(f"\n### Reviewer report\n{output}\n".encode("utf-8"))


def write_output(output: str) -> None:
    # The caller reads this as UTF-8; a locale-encoded stream could not hold every character.
    stream = getattr(sys.stdout, "buffer", None)
    if stream is None:
        sys.stdout.write(output + "\n")
    else:
        stream.write((output + "\n").encode("utf-8"))
        stream.flush()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Run a reviewer command and append its output to the work log."
    )
    parser.add_argument("--label", default="reviewer", help="Reviewer name used in messages.")
    parser.add_argument("--env", action="append", default=[], metavar="NAME=VALUE")
    parser.add_argument(
        "--timeout",
        type=positive_seconds,
        default=DEFAULT_REVIEW_TIMEOUT,
        help=f"Reviewer time limit in seconds (default: {DEFAULT_REVIEW_TIMEOUT}).",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command

    environ = dict(os.environ)
    try:
        environ.update(parse_assignments(args.env))
        command = reviewer_command(command, environ)
    except ValueError as exc:
        print(f"run_review: {exc}", file=sys.stderr)
        return 2
    log_path = environ.get(WORK_LOG_ENV, "")
    if not log_path:
        print(f"BLOCK: {WORK_LOG_ENV} is not set; cannot record the {args.label} review")
        return 1

    try:
        result = run_bounded(command, env=environ, timeout=args.timeout)
    except subprocess.TimeoutExpired as exc:
        partial = reviewer_output(exc.output, exc.stderr)
        note = f"run_review: {args.label} review timed out after {args.timeout}s"
        output = f"{partial}\n{note}" if partial else note
        status = TIMEOUT_STATUS
    except OSError as exc:
        output, status = f"run_review: cannot run {command[0]}: {exc}", 127
    else:
        output, status = reviewer_output(result.stdout, result.stderr), result.returncode

    try:
        append_report(Path(log_path), output)
    except OSError:
        print(f"BLOCK: cannot append {args.label} review to work log")
        return 1
    write_output(output)
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
