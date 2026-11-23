"""What `close_work.py` hands a reviewer besides the card: changed paths and check output.

Two things a reviewer at close could not see before (W-00000413):

- The paths it is told to read came from the HEAD commit only, so a records-only commit
  on top of the code left it reading `.stage/` files (O-00000058). `committed_paths` lists
  the paths of the commits the closer names, and `records_only_warning` says so when the
  default list holds nothing but Stage records.
- `close_work.py` ran the card's checks and kept their output to itself. `check_output_section`
  renders that output, bounded, as a `### Checks at close` section of the shared work log,
  which every review command already reads (`$STAGE_WORK_LOG_PATH`).
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

CHECK_OUTPUT_HEADING = "### Checks at close"
# The tail of one check's output that reaches the reviewer. A passing suite ends with its
# summary, so the tail is the part that says what ran.
CHECK_OUTPUT_MAX_LINES = 60
CHECK_OUTPUT_MAX_BYTES = 6000
# All checks of one close together; with many checks each gets an equal share of it.
SECTION_MAX_BYTES = 30000
# Output lines are indented so that a line of output starting with `### ` or with a report
# label (`What changed:`) is never read as a work-log heading or field.
OUTPUT_INDENT = "    "
STAGE_RECORD_PREFIX = ".stage/"

_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def committed_paths(project_root: Path, revisions: list[str], timeout: int) -> list[str]:
    """Sorted paths changed by the commits `revisions` name, each path once.

    Raises RuntimeError when git cannot list one of them.
    """
    found: set[str] = set()
    for revision in revisions:
        command = [
            "git",
            "show",
            "--format=",
            "--name-only",
            "--no-renames",
            "-z",
            f"{revision}^{{commit}}",
        ]
        try:
            proc = subprocess.run(
                command, capture_output=True, timeout=timeout, cwd=str(project_root)
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError(f"cannot list paths in commit {revision}: {exc}") from exc
        if proc.returncode != 0:
            detail = os.fsdecode(proc.stderr).strip() or f"git exited {proc.returncode}"
            raise RuntimeError(f"cannot list paths in commit {revision}: {detail}")
        found.update(os.fsdecode(raw) for raw in proc.stdout.split(b"\0") if raw)
    return sorted(found)


def records_only_warning(paths: list[str]) -> str:
    """A warning when the reviewer would read Stage records only; "" otherwise."""

    if not paths or any(not path.startswith(STAGE_RECORD_PREFIX) for path in paths):
        return ""
    return (
        "WARNING the review receives only `.stage/` paths, the ones the HEAD commit changed. "
        "When the card's code is in an earlier commit, close again with "
        "`--review-commit <code-commit>` (repeatable) so the reviewer reads the code."
    )


def output_tail(output: str, max_lines: int, max_bytes: int) -> tuple[str, int]:
    """The end of `output` within both limits, and how many earlier lines were left out."""

    lines = _CTRL_RE.sub("", output).splitlines()
    kept = lines[-max_lines:] if max_lines > 0 else []
    while kept and len("\n".join(kept).encode("utf-8")) > max_bytes:
        kept = kept[1:]
    if not kept and lines and max_lines > 0:
        # One line longer than the whole budget: keep its end.
        kept = [lines[-1].encode("utf-8")[-max_bytes:].decode("utf-8", "ignore")]
    return "\n".join(kept), len(lines) - len(kept)


def check_output_section(results: list[tuple[str, str]], day: str) -> str:
    """The work-log section that shows a reviewer what the checks at close printed.

    `results` holds one `(command, output)` per check that passed, in the order run. Each
    output is cut to its last `CHECK_OUTPUT_MAX_LINES` lines and `CHECK_OUTPUT_MAX_BYTES`
    bytes, or to an equal share of `SECTION_MAX_BYTES` when that is smaller; a cut output
    says how many earlier lines were left out. Returns "" when no check ran.
    """
    if not results:
        return ""
    budget = min(CHECK_OUTPUT_MAX_BYTES, SECTION_MAX_BYTES // len(results))
    lines = [
        CHECK_OUTPUT_HEADING,
        f"Run by close_work.py on {day}, before this review, on the tree under review. "
        f"All {len(results)} passed (exit 0). Each output is its end only: at most "
        f"{CHECK_OUTPUT_MAX_LINES} lines and {budget} bytes. Running one of these again shows "
        "nothing new; this is what they printed.",
    ]
    for command, output in results:
        tail, omitted = output_tail(output, CHECK_OUTPUT_MAX_LINES, budget)
        lines.append("")
        lines.append(f"{OUTPUT_INDENT}$ {' '.join(_CTRL_RE.sub('', command).split())}")
        if omitted:
            lines.append(f"{OUTPUT_INDENT}... ({omitted} earlier lines omitted)")
        lines += [f"{OUTPUT_INDENT}{line}".rstrip() for line in tail.splitlines()]
        if not tail.strip():
            lines.append(f"{OUTPUT_INDENT}(no output)")
    return "\n".join(lines) + "\n"


def append_check_output(log_path: Path, section: str) -> None:
    """Append the section to the work log; raises RuntimeError when it cannot be written."""

    if not section:
        return
    try:
        # Bytes, so the log keeps its line endings and encoding on every platform.
        with log_path.open("ab") as handle:
            handle.write(f"\n{section}".encode("utf-8"))
    except OSError as exc:
        raise RuntimeError(f"cannot write check output to the work log {log_path}: {exc}") from exc
