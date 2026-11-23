"""What a review at close left behind that its verdict does not say.

`close_work.reject_review_writes` fails a review whose commands left a repository file
changed. A reviewer may run any shell command (DE-00000101), so three things pass that
check (W-00000413, W-00000414):

- it changes a file and puts the old content back (`git checkout`, `git restore`);
- it, or the test code it runs, writes a file Git ignores;
- it reads records outside the repository: the session record folder (`~/.claude`) or
  GitHub.

This module looks for each of them. The first fails the review. The other two are told
to the person who closes and written on the card, because a cache write and a command
that only names a folder look the same as the real thing (`operations/review.md`,
"What the close sees of the reviewer").

Nothing here changes a file except `reject_restored_files`, which removes the verdict.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

STAGE_ROOT = Path(__file__).resolve().parents[2]
for import_dir in (STAGE_ROOT / "hooks", STAGE_ROOT / "scripts"):
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))

from driver_repository import (  # noqa: E402
    STAGE_RUNTIME_PREFIX,
    git_index_and_untracked,
    snapshot_from_listing,
)

# The reviewer command writes its tool calls to the file this variable names, one JSON
# object per line; `claude_review_companion.py` does. A command that writes none leaves
# the close with nothing to read.
TOOL_CALLS_ENV = "STAGE_REVIEW_TOOL_CALLS_FILE"
SESSION_RECORDS = "the session record folder (~/.claude)"
GITHUB = "GitHub"
LISTED = 10


@dataclass(frozen=True)
class ReviewSnapshot:
    """The repository as one review at close found it or left it."""

    # Tracked and untracked files by content, as the drivers compare them.
    paths: dict[str, str] = field(default_factory=dict)
    # The same files by identity and times: a restored file has its old content and new times.
    stats: dict[str, str] = field(default_factory=dict)
    # Files Git ignores, by size and modified time; their content is not read.
    ignored: dict[str, str] = field(default_factory=dict)


def _path_stat(path: Path) -> str:
    try:
        stat = path.lstat()
    except OSError as exc:
        return f"unreadable:{type(exc).__name__}"
    return f"{stat.st_ino}:{stat.st_mtime_ns}:{stat.st_ctime_ns}"


def _ignored_stat(path: Path) -> str:
    try:
        stat = path.lstat()
    except OSError as exc:
        return f"unreadable:{type(exc).__name__}"
    return f"{stat.st_mode:o}:{stat.st_size}:{stat.st_mtime_ns}"


def ignored_paths(project_root: Path) -> list[str]:
    """Every file Git ignores under the project, without Stage's runtime folder."""

    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--ignored", "--exclude-standard", "-z"],
            cwd=str(project_root),
            capture_output=True,
        )
    except OSError as exc:
        raise RuntimeError(str(exc)) from exc
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.decode(errors="replace").strip()
            or f"git ls-files --ignored failed with exit code {result.returncode}"
        )
    paths = (os.fsdecode(raw) for raw in result.stdout.split(b"\0") if raw)
    return [path for path in paths if not path.startswith(STAGE_RUNTIME_PREFIX)]


def review_snapshot(project_root: Path) -> ReviewSnapshot:
    """Snapshot what a review at close is compared against; empty outside a Git worktree."""

    listing = git_index_and_untracked(project_root)
    if listing is None:
        return ReviewSnapshot()
    index_entries, untracked_paths, listing_error = listing
    if listing_error:
        raise RuntimeError(listing_error)
    paths = snapshot_from_listing(project_root, index_entries, untracked_paths)
    return ReviewSnapshot(
        paths=paths,
        stats={relative: _path_stat(project_root / relative) for relative in paths},
        ignored={
            relative: _ignored_stat(project_root / relative)
            for relative in ignored_paths(project_root)
        },
    )


def _verdict_relative(project_root: Path, verdict_file: Path) -> str:
    try:
        return verdict_file.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return ""


def restored_paths(
    project_root: Path, before: ReviewSnapshot, after: ReviewSnapshot, verdict_file: Path
) -> list[str]:
    """Files whose content is what it was and whose identity or times are not."""

    verdict = _verdict_relative(project_root, verdict_file)
    return sorted(
        relative
        for relative, content in before.paths.items()
        if relative != verdict
        and after.paths.get(relative) == content
        and after.stats.get(relative) != before.stats.get(relative)
    )


def reject_restored_files(
    project_root: Path, before: ReviewSnapshot, after: ReviewSnapshot, verdict_file: Path
) -> str:
    """Fail a review that rewrote a repository file and left its old content there.

    A reviewer that restores a file its commands changed hides what they wrote, and the
    content comparison then sees nothing (W-00000413). The verdict is removed so no
    approval survives. Returns "" when no file was rewritten.
    """

    restored = restored_paths(project_root, before, after, verdict_file)
    if not restored:
        return ""
    verdict_file.unlink(missing_ok=True)
    return (
        "the review rewrote repository files and left their earlier content in place "
        "(changed and restored, for example with `git checkout` or `git restore`): "
        + ", ".join(restored)
        + "; verdict removed: a restored file hides what the review's commands wrote, so "
        "run the review again (anything else that rewrote these files during the review "
        "counts too)"
    )


def changed_ignored_paths(before: ReviewSnapshot, after: ReviewSnapshot) -> list[str]:
    """Ignored files that appeared, went away, or were written during the review."""

    return sorted(
        relative
        for relative in set(before.ignored) | set(after.ignored)
        if before.ignored.get(relative) != after.ignored.get(relative)
    )


def _input_text(tool_input: object) -> str:
    """The text of one tool call: the shell command, or every string the call carries."""

    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command")
    if isinstance(command, str):
        return command
    return "\n".join(value for value in tool_input.values() if isinstance(value, str))


def read_tool_calls(path: Path) -> tuple[list[str], bool] | None:
    """The reviewer's tool calls that ran, as text, and whether the record is whole.

    Returns None when the reviewer command wrote no record. A call the host refused did
    not read anything and is left out.
    """

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError):
        return [], False
    calls: list[tuple[str, str]] = []
    denied: set[str] = set()
    complete = False
    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        if entry.get("complete") is True:
            complete = True
            refused = entry.get("denied")
            denied.update(item for item in refused or [] if isinstance(item, str))
            continue
        text = _input_text(entry.get("input"))
        if text:
            calls.append((str(entry.get("id", "")), text))
    return [text for call_id, text in calls if call_id not in denied], complete


def _home_spellings(home: Path, environ: dict[str, str]) -> list[str]:
    """Every way a command can write the session record folder's path."""

    folder = (home / ".claude").as_posix()
    spellings = [folder]
    if len(home.drive) == 2 and home.drive[1] == ":":
        # Git Bash writes `C:/Users/me` as `/c/Users/me`.
        spellings.append("/" + home.drive[0].lower() + folder[2:])
    configured = environ.get("CLAUDE_CONFIG_DIR", "").strip()
    if configured:
        spellings.append(Path(configured).as_posix())
    return spellings


def outside_reach(
    calls: list[str], home: Path, environ: dict[str, str] | None = None
) -> dict[str, list[str]]:
    """The calls whose text names a record outside the repository, by what they name.

    This reads the text of a command, not what the command did: a folder reached through
    `cd`, or a command inside a script file, is not seen, and a command that only prints
    the folder's name is.
    """

    env = dict(os.environ) if environ is None else environ
    literal = "|".join(re.escape(spelling) for spelling in _home_spellings(home, env))
    session = re.compile(
        r"(?:(?:~|\$\{?HOME\}?|\$env:USERPROFILE|\$USERPROFILE|%USERPROFILE%)/\.claude"
        rf"|{literal})(?![\w-])",
        re.IGNORECASE,
    )
    github = re.compile(r"(?<![\w./-])gh(?:\.exe)?\s+[a-z]|api\.github\.com", re.IGNORECASE)
    found: dict[str, list[str]] = {}
    for text in calls:
        normalized = text.replace("\\", "/")
        if session.search(normalized):
            found.setdefault(SESSION_RECORDS, []).append(text)
        if github.search(normalized):
            found.setdefault(GITHUB, []).append(text)
    return found


def _listed(paths: list[str]) -> str:
    shown = ", ".join(paths[:LISTED])
    return shown if len(paths) <= LISTED else f"{shown}, +{len(paths) - LISTED} more"


def _one_line(text: str, limit: int = 200) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


@dataclass(frozen=True)
class ReviewTraces:
    """What the close tells the person about one review, beyond pass or fail."""

    ignored: list[str] = field(default_factory=list)
    reach: dict[str, list[str]] = field(default_factory=dict)
    # None: the reviewer command wrote no tool-call record. False: it wrote part of one.
    record_complete: bool | None = None

    def warnings(self) -> list[str]:
        """Lines for the person who closes; empty when the review left no trace."""

        lines = []
        if self.ignored:
            lines.append(
                "the review's commands wrote files Git ignores: " + _listed(self.ignored)
            )
        for what, commands in self.reach.items():
            lines.append(
                f"{len(commands)} reviewer command(s) name {what}; a verdict that rests on "
                "records outside the repository was not judged from this checkout:"
            )
            lines += [f"  {_one_line(command)}" for command in commands[:LISTED]]
        if self.record_complete is False:
            lines.append(
                "the reviewer's tool-call record is incomplete, so commands that reach "
                "outside the repository may be missing from it"
            )
        return lines

    def record_line(self, day: str) -> str:
        """One committed line for the card's `## Verification`, or "" when there is none."""

        parts = []
        if self.ignored:
            parts.append(f"ignored files written {len(self.ignored)} ({_listed(self.ignored)})")
        parts += [
            f"commands naming {what} {len(commands)}" for what, commands in self.reach.items()
        ]
        if self.record_complete is False:
            parts.append("tool-call record incomplete")
        return f"- Reviewer traces at close {day}: " + "; ".join(parts) if parts else ""


def review_traces(
    before: ReviewSnapshot,
    after: ReviewSnapshot,
    tool_calls_file: Path,
    home: Path | None = None,
) -> ReviewTraces:
    """Collect what one review left that does not fail it."""

    record = read_tool_calls(tool_calls_file)
    calls, complete = record if record is not None else ([], None)
    return ReviewTraces(
        ignored=changed_ignored_paths(before, after),
        reach=outside_reach(calls, home or Path.home()),
        record_complete=complete,
    )
