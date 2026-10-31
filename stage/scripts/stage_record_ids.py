#!/usr/bin/env python3
"""Find record numbers already used in this checkout or on any known branch.

Parallel sessions work on different branches, and a number picked from one
checkout alone can already belong to a record on another branch: W-00000286 and
DE-00000076 collided that way. This counts one prefix (`W`, `DE`, `O`, ...)
across the working tree's `.stage/` and every local and remote-tracking branch,
and names the next free id. It reads only refs already fetched; it never
touches the network.

Usage:
    python3 stage/scripts/stage_record_ids.py --project-root . DE
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks"))
from stage_record_paths import record_paths  # noqa: E402

PREFIX_RE = re.compile(r"^[A-Z]{1,3}$")
RUNTIME_PART = ".runtime"


def id_line_re(prefix: str) -> re.Pattern[str]:
    return re.compile(rf"^id:[ \t]*{re.escape(prefix)}-(\d{{8}})[ \t]*\r?$", re.MULTILINE)


def local_record_numbers(stage_root: Path, prefix: str) -> set[int]:
    """Numbers named by `id:` lines in the working tree's `.stage/` records."""

    pattern = id_line_re(prefix)
    numbers: set[int] = set()
    if not stage_root.is_dir():
        return numbers
    for path in record_paths(stage_root):
        if RUNTIME_PART in path.relative_to(stage_root).parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        numbers.update(int(number) for number in pattern.findall(text))
    numbers.discard(0)  # templates carry the all-zero placeholder id
    return numbers


def git_output(project_root: Path, *args: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=str(project_root), capture_output=True, timeout=60
        )
    except (OSError, subprocess.TimeoutExpired):
        return -1, ""
    return proc.returncode, os.fsdecode(proc.stdout)


def branch_record_numbers(project_root: Path, prefix: str) -> dict[int, set[str]]:
    """Map each number used on a local or remote-tracking branch to those branches."""

    code, refs_text = git_output(
        project_root, "for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes"
    )
    if code != 0:
        return {}
    refs = [ref for ref in refs_text.split() if ref and not ref.endswith("/HEAD")]
    pattern = id_line_re(prefix)
    found: dict[int, set[str]] = {}
    for ref in refs:
        code, matches = git_output(
            project_root,
            "grep",
            "-h",
            "-I",
            "-E",
            rf"^id:[[:space:]]*{prefix}-[0-9]{{8}}",
            ref,
            "--",
            ".stage",
        )
        if code not in (0, 1):  # 1 means no match on this branch
            continue
        for number in pattern.findall(matches):
            if int(number):
                found.setdefault(int(number), set()).add(ref)
    return found


def next_record_id(project_root: Path, prefix: str) -> str:
    used = local_record_numbers(project_root / ".stage", prefix) | set(
        branch_record_numbers(project_root, prefix)
    )
    return f"{prefix}-{(max(used) + 1) if used else 1:08d}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project-root", default=".")
    parser.add_argument("prefix", help="Record id prefix, e.g. W, DE, or O.")
    args = parser.parse_args()
    if not PREFIX_RE.fullmatch(args.prefix):
        print(f"prefix must be 1-3 capital letters, got {args.prefix!r}", file=sys.stderr)
        return 2
    print(next_record_id(Path(args.project_root).expanduser().resolve(), args.prefix))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
