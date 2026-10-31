#!/usr/bin/env python3
"""Stand in for the Codex companion by running the same prompt through `claude -p`.

A session without Codex (a cloud session) can still run the project's configured
Codex review commands unchanged: point `STAGE_CODEX_COMPANION` at this script and
`codex_companion.py` hands it the companion's arguments. The prompt is the last
argument; the Codex-only flags before it are ignored. The reviewer gets
`--permission-mode acceptEdits` so it can write `$STAGE_REVIEW_VERDICT_FILE`, and
`--add-dir` for the folder of `$STAGE_CHANGED_PATHS_FILE`, which lives outside the
project. The result is a same-model review, never a cross-venue one; the
cloud-execution procedure requires the card to say so.

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

MODEL_ENV = "STAGE_CLAUDE_REVIEW_MODEL"
DEFAULT_MODEL = "opus[1m]"


def claude_command(argv: list[str], environ: dict[str, str], claude: str) -> list[str]:
    if not argv:
        raise ValueError("expected the review prompt as the last argument")
    command = [claude, "-p"]
    changed_paths = environ.get("STAGE_CHANGED_PATHS_FILE", "")
    if changed_paths:
        # --add-dir takes several values, so it must not sit right before the prompt.
        command += ["--add-dir", str(Path(changed_paths).parent)]
    command += [
        "--model",
        environ.get(MODEL_ENV) or DEFAULT_MODEL,
        "--permission-mode",
        "acceptEdits",
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
