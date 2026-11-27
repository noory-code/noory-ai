#!/usr/bin/env python3
"""Run an independent Stage review through Antigravity (`agy -p`).

Modeled after `claude_review_companion.py`, this companion builds an attached
`--print=<prompt>` command for `agy`, relays `stream-json` tool calls into
`$STAGE_REVIEW_TOOL_CALLS_FILE` so close containment can inspect them, and prints
the final `result.response`.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import IO, Iterable

MODEL_ENV = "STAGE_AGY_REVIEW_MODEL"
FALLBACK_MODEL_ENV = "STAGE_MODEL"
EFFORT_ENV = "STAGE_EFFORT"
# `review_containment.TOOL_CALLS_ENV`; this script imports nothing from the plugin.
TOOL_CALLS_ENV = "STAGE_REVIEW_TOOL_CALLS_FILE"
REVIEWER_RULES = (
    "\n\nRules of this review, checked after you finish:\n"
    "- The repository is compared before and after you. If one of your commands, or the "
    "tests it runs, changes a project file, leave the file as it is and name it in that "
    "criterion's reason. Do not restore it (`git checkout`, `git restore`, `git stash`, "
    "copying a backup over it) and do not delete what your commands created: a restored "
    "file fails the review.\n"
    "- Judge from this checkout. Do not read the session record folder (`~/.claude`, "
    "`~/.gemini/antigravity`, `~/.gemini/antigravity-cli`) or GitHub (`gh`, api.github.com); "
    "the commands you run are recorded. When a criterion can only be judged from there, its "
    "method is `unable`.\n"
)


def agy_command(
    argv: list[str], environ: dict[str, str], agy: str
) -> list[str]:
    if not argv:
        raise ValueError("expected the review prompt as the last argument")
    verdict_file = environ.get("STAGE_REVIEW_VERDICT_FILE", "")
    if not verdict_file:
        raise ValueError("STAGE_REVIEW_VERDICT_FILE is required")

    command = [
        agy,
        "--output-format",
        "stream-json",
        "--sandbox",
        "--disable-slash-commands",
        "--mode",
        "accept-edits",
    ]
    add_dirs: list[str] = []
    for raw_path in (verdict_file, environ.get("STAGE_CHANGED_PATHS_FILE", "")):
        if not raw_path:
            continue
        parent = str(Path(raw_path).parent)
        if parent not in add_dirs:
            add_dirs.append(parent)
    for folder in add_dirs:
        command += ["--add-dir", folder]

    model = environ.get(MODEL_ENV) or environ.get(FALLBACK_MODEL_ENV) or ""
    if model:
        command += ["--model", model]
    effort = environ.get(EFFORT_ENV, "")
    if effort:
        command += ["--effort", effort]

    # `agy -p` / `--print` consumes its prompt as an attached flag value (`--print=<prompt>`).
    command.append(f"--print={argv[-1] + REVIEWER_RULES}")
    return command


def relay_stream(lines: Iterable[str], record: IO[str] | None, out: IO[str]) -> None:
    """Print the reviewer's answer from an agy stream-json run and record its tool calls."""

    def write(entry: dict[str, object]) -> None:
        if record is not None:
            record.write(json.dumps(entry, ensure_ascii=False) + "\n")
            record.flush()

    answered = False
    recorded_ids: set[str] = set()
    denied: list[str] = []

    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            event = None
        if not isinstance(event, dict):
            out.write(line if line.endswith("\n") else line + "\n")
            continue

        kind = event.get("event")
        if kind == "step_update":
            step = event.get("step_update")
            if not isinstance(step, dict) or step.get("step_type") != "tool":
                continue
            step_index = step.get("step_index")
            call_id = f"step-{step_index}" if step_index is not None else ""
            tool_info = step.get("tool_info")
            info = tool_info if isinstance(tool_info, dict) else {}
            name = str(step.get("tool_name") or info.get("name") or "")
            params = info.get("parameters")
            if call_id and call_id not in recorded_ids:
                recorded_ids.add(call_id)
                write({"id": call_id, "tool": name, "input": params})
            if step.get("state") in {"DONE", "ERROR"}:
                output = str(info.get("output") or "")
                error_info = info.get("error")
                error_message = (
                    str(error_info.get("message") or "")
                    if isinstance(error_info, dict)
                    else str(error_info or "")
                )
                combined = output or error_message
                if call_id and combined.lower().startswith("tool call denied"):
                    if call_id not in denied:
                        denied.append(call_id)
        elif kind == "result":
            answered = True
            result = event.get("result")
            if isinstance(result, dict):
                response = result.get("response")
                if isinstance(response, str) and response:
                    out.write(response.rstrip("\n") + "\n")
            write({"complete": True, "denied": denied})

    if not answered:
        out.write("agy_review_companion: the reviewer ended without a result event\n")
    out.flush()


def run_reviewer(command: list[str], environ: dict[str, str]) -> int:
    record_path = environ.get(TOOL_CALLS_ENV, "")
    record = open(record_path, "a", encoding="utf-8") if record_path else None
    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace"
        )
        assert process.stdout is not None
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        relay_stream(process.stdout, record, sys.stdout)
        return process.wait()
    finally:
        if record is not None:
            record.close()


def main(argv: list[str]) -> int:
    agy = shutil.which("agy")
    if agy is None:
        print("agy_review_companion: `agy` is not on PATH", file=sys.stderr)
        return 127
    environ = dict(os.environ)
    try:
        command = agy_command(argv, environ, agy)
    except ValueError as exc:
        print(f"agy_review_companion: {exc}", file=sys.stderr)
        return 2
    return run_reviewer(command, environ)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
