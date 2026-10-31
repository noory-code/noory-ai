#!/usr/bin/env python3
"""Stand in for the Codex companion by running the same prompt through `claude -p`.

A session without Codex (a cloud session) can still run the project's configured
Codex review commands unchanged: point `STAGE_CODEX_COMPANION` at this script and
`codex_companion.py` hands it the companion's arguments. The prompt is the last
argument; the Codex-only flags before it are ignored. The reviewer may write only
`$STAGE_REVIEW_VERDICT_FILE` and run `python3 -m unittest`, and gets `--add-dir` for
the folder of `$STAGE_CHANGED_PATHS_FILE`, which lives outside the project; it may
not edit project files. The result is a same-model review, never a cross-venue one;
the cloud-execution procedure requires the card to say so.

Permission rules govern only the reviewer's own tool calls: code that `python3 -m
unittest` imports and runs can still write anywhere. So the repository is
snapshotted before and after the review (tracked files plus untracked, non-ignored
ones, the driver's view). When anything other than the verdict file changed, the
verdict file is removed, the changed paths are reported, and the exit status is
REVIEW_WROTE_FILES, so the review fails visibly instead of approving a tree the
review itself altered. Changed files are left in place for the person to inspect.

The project's own Claude reviewer command runs through this script as well, so both
review paths share these permissions and this check.

Usage (from the project root):
    STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py \\
        python3 stage/skills/stage-retrospective/close_work.py ...
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
for import_dir in (SCRIPTS_DIR.parent / "hooks", SCRIPTS_DIR):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from driver_repository import (  # noqa: E402
    changed_repository_paths,
    repository_path_snapshot,
)

MODEL_ENV = "STAGE_CLAUDE_REVIEW_MODEL"
DEFAULT_MODEL = "opus[1m]"
REVIEW_WROTE_FILES = 3


def claude_command(argv: list[str], environ: dict[str, str], claude: str) -> list[str]:
    if not argv:
        raise ValueError("expected the review prompt as the last argument")
    verdict_file = environ.get("STAGE_REVIEW_VERDICT_FILE", "")
    if not verdict_file:
        raise ValueError("STAGE_REVIEW_VERDICT_FILE is required")
    command = [claude, "-p"]
    changed_paths = environ.get("STAGE_CHANGED_PATHS_FILE", "")
    if changed_paths:
        command += ["--add-dir", str(Path(changed_paths).parent)]
    # A leading `//` makes a permission rule path absolute. Only Edit(path) rules
    # govern file writes; a Write(path) rule is ignored with a warning.
    verdict_rule = "/" + Path(verdict_file).resolve().as_posix()
    command += [
        "--model",
        environ.get(MODEL_ENV) or DEFAULT_MODEL,
        "--allowedTools",
        f"Edit({verdict_rule})",
        "Bash(python3 -m unittest:*)",
        # --add-dir and --allowedTools take several values; `--` ends them before the prompt.
        "--",
        argv[-1],
    ]
    return command


def paths_written_by_review(
    before: dict[str, str],
    after: dict[str, str],
    project_root: Path,
    verdict_file: Path,
) -> list[str]:
    """Return repository paths the review changed, other than its verdict file."""

    try:
        verdict = verdict_file.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        verdict = ""
    return [path for path in changed_repository_paths(before, after) if path != verdict]


def report(message: str) -> None:
    # stdout too: the project reviewer command copies stdout into the work log.
    print(f"claude_review_companion: {message}")
    print(f"claude_review_companion: {message}", file=sys.stderr)


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
    project_root = Path.cwd()
    verdict_file = Path(environ["STAGE_REVIEW_VERDICT_FILE"])
    try:
        before = repository_path_snapshot(project_root)
    except RuntimeError as exc:
        report(f"cannot snapshot the repository before review: {exc}; review not run")
        return 2
    returncode = subprocess.run(command).returncode
    try:
        after = repository_path_snapshot(project_root)
    except RuntimeError as exc:
        verdict_file.unlink(missing_ok=True)
        report(f"cannot snapshot the repository after review: {exc}; verdict removed")
        return REVIEW_WROTE_FILES
    written = paths_written_by_review(before, after, project_root, verdict_file)
    if written:
        verdict_file.unlink(missing_ok=True)
        report(
            "the review changed repository files other than its verdict file: "
            + ", ".join(written)
            + "; verdict removed, files left in place for inspection"
        )
        return REVIEW_WROTE_FILES
    return returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
