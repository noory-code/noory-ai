#!/usr/bin/env python3
"""Move an executor report from a commit message into the item's work log.

A session without the shared work log (a cloud session, for one) writes its
`### Executor report` in the commit body instead, and the report must reach the
work log before `close_work.py` copies it onto the card. Commit bodies are
usually wrapped, so a field the contract keeps on one line arrives split across
several. This joins every field back onto one line, rewrites the report in
contract order, validates it with the executor-report contract against the
paths that commit changed, and appends it only when it passes.

Usage:
    python3 stage/scripts/import_executor_report.py --project-root . W-00000001 [--commit <rev>]...

Pass --commit once per attempt when a card took several: the report is read from the
last commit and checked against every path those commits changed, because the
contract's Changed paths (JSON) covers all attempts.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

STAGE_ROOT = Path(__file__).resolve().parents[1]
for import_dir in (
    STAGE_ROOT / "hooks",
    STAGE_ROOT / "scripts",
    STAGE_ROOT / "skills" / "stage-retrospective",
):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from close_work import (  # noqa: E402
    EXECUTOR_REPORT_MARKER,
    WORK_LOG_PREAMBLE,
    ensure_work_log,
    executor_report_error,
    section_marker_starts,
    work_log_path,
    work_log_reference,
)

# Contract order; the two JSON fields carry their value on the following line.
REPORT_LABELS = (
    "What changed",
    "Why",
    "Decisions made",
    "Work not done",
    "Changed paths (JSON)",
    "Review dispositions (JSON)",
    "Review request",
)
JSON_LABELS = {"Changed paths (JSON)", "Review dispositions (JSON)"}
LABEL_RE = re.compile(
    r"^(" + "|".join(re.escape(label) for label in REPORT_LABELS) + r"):[ \t]*(.*?)[ \t]*$"
)
TRAILER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9-]*:[ \t]")


def git(project_root: Path, *args: str) -> bytes:
    proc = subprocess.run(["git", *args], cwd=str(project_root), capture_output=True)
    if proc.returncode != 0:
        detail = os.fsdecode(proc.stderr).strip() or f"git exited {proc.returncode}"
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return proc.stdout


def parse_report(message: str) -> dict[str, str]:
    """Return the report's fields with wrapped continuation lines joined by spaces."""

    starts = section_marker_starts(message, EXECUTOR_REPORT_MARKER)
    if not starts:
        raise ValueError(f"commit message has no `{EXECUTOR_REPORT_MARKER}` section")
    _marker, _newline, body = message[starts[-1] :].partition("\n")
    fields: dict[str, list[str]] = {}
    current: str | None = None
    for raw_line in body.splitlines():
        line = raw_line.strip()
        match = LABEL_RE.match(line)
        if match:
            current = match.group(1)
            if current in fields:
                raise ValueError(f"executor report repeats `{current}:`")
            fields[current] = [match.group(2)] if match.group(2) else []
        elif not line:
            current = None
        elif current is not None and not TRAILER_RE.match(line):
            fields[current].append(line)
        else:
            break
    return {label: " ".join(parts) for label, parts in fields.items()}


def render_report(fields: dict[str, str]) -> str:
    lines = [EXECUTOR_REPORT_MARKER]
    for label in REPORT_LABELS:
        if label not in fields:
            continue
        if label in JSON_LABELS:
            lines += [f"{label}:", fields[label]]
        else:
            lines.append(f"{label}: {fields[label]}".rstrip())
    return "\n".join(lines) + "\n"


def import_report(project_root: Path, item_id: str, revisions: list[str]) -> Path:
    stage_root = project_root / ".stage"
    message = os.fsdecode(git(project_root, "log", "-1", "--format=%B", revisions[-1]))
    report = render_report(parse_report(message))
    observed = sorted(
        {
            os.fsdecode(path)
            for revision in revisions
            for path in git(
                project_root, "show", "--format=", "--name-only", "--no-renames", "-z", revision
            ).split(b"\0")
            if path
        }
    )
    log_path = work_log_path(stage_root, item_id)
    previous = (
        log_path.read_text(encoding="utf-8")
        if log_path.is_file()
        else WORK_LOG_PREAMBLE.format(item_id=item_id)
    )
    addition = f"\n{report}"
    error = executor_report_error(
        previous,
        previous + addition,
        observed,
        ignored_paths=[work_log_reference(item_id)],
    )
    if error:
        raise ValueError(error)
    log_path = ensure_work_log(stage_root, item_id)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(addition)
    return log_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project-root", default=".")
    parser.add_argument("item", help="Work item id, e.g. W-00000001.")
    parser.add_argument(
        "--commit",
        action="append",
        help="Commit of one attempt, repeatable; the last one holds the report (default: HEAD).",
    )
    args = parser.parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    try:
        log_path = import_report(project_root, args.item, args.commit or ["HEAD"])
    except (RuntimeError, ValueError) as exc:
        print(f"{args.item}: {exc}; work log unchanged", file=sys.stderr)
        return 1
    revisions = ", ".join(args.commit or ["HEAD"])
    print(f"{args.item}: imported the executor report from {revisions} into {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
