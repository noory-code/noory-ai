"""Per-project git repo used only for session-bookmark tags.

The repo is quiet by design: no automatic commits happen during
day-to-day editing. A commit is created only when the user (or an MCP
tool) asks for a tagged snapshot — typically at the start or end of a
work session. The tag gives them a durable name to jump back to later
with ``git checkout <tag>`` or a future viewer UI.

Undo/redo inside a session is handled in-memory on the viewer and does
not touch git.

Implementation notes
--------------------

- ``subprocess.run(["git", …])`` end-to-end — no third-party git binding,
  keeps the plugin install lean and works on any platform with git.
- ``user.name`` / ``user.email`` are configured **locally** (per-repo)
  so the project doesn't inherit the user's global identity.
- The repo starts with zero commits; ``git rev-parse HEAD`` fails
  until the first ``tag_snapshot``.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class TagAlreadyExistsError(ValueError):
    """Raised when ``tag_snapshot`` is called with a name that's already taken."""


@dataclass
class _RunResult:
    stdout: str
    stderr: str
    returncode: int


def _git(*args: str, cwd: Path, check: bool = True) -> _RunResult:
    """Run a git subcommand inside ``cwd``.

    ``check=True`` raises ``subprocess.CalledProcessError`` on non-zero
    exit; set ``check=False`` when a non-zero is the expected / checkable
    signal (e.g. ``rev-parse --verify HEAD`` on a brand-new repo).
    """
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
    )
    return _RunResult(result.stdout, result.stderr, result.returncode)


# ---------------------------------------------------------------------------
# ensure_repo
# ---------------------------------------------------------------------------


def ensure_repo(project_dir: Path) -> None:
    """Create the per-project git repo on first access.

    Idempotent: if ``.git/`` already exists, only the author config
    is re-asserted (cheap), and ``.gitignore`` stays as-is.
    """
    dot_git = project_dir / ".git"
    if not dot_git.exists():
        _git("init", "--quiet", cwd=project_dir)
    # Always (re)assert identity so a later git version change can't drop it.
    _git("config", "--local", "user.name", "Plot", cwd=project_dir)
    _git("config", "--local", "user.email", "plot@noory-ai.local", cwd=project_dir)
    # Write .gitignore only if not already present — don't clobber user edits.
    gi = project_dir / ".gitignore"
    if not gi.exists():
        gi.write_text("*.tmp\n_archive/\n", encoding="utf-8")
    # Force LF line endings for JSON so cross-platform diffs stay clean.
    attrs = project_dir / ".gitattributes"
    if not attrs.exists():
        attrs.write_text("*.json text eol=lf\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# tag_snapshot
# ---------------------------------------------------------------------------


def _tag_exists(project_dir: Path, name: str) -> bool:
    result = _git(
        "rev-parse",
        "--verify",
        "--quiet",
        f"refs/tags/{name}",
        cwd=project_dir,
        check=False,
    )
    return result.returncode == 0


def tag_snapshot(
    project_dir: Path, name: str, message: str | None = None
) -> dict[str, Any]:
    """Snapshot the current working tree under an annotated git tag.

    Flow:
      1. ``git add -A``
      2. ``git commit -m <message or name>`` (``--allow-empty`` so we can
         tag even when nothing changed between snapshots — end-of-session
         markers on an otherwise untouched project).
      3. ``git tag -a <name> -m <message or name>``

    Raises ``TagAlreadyExistsError`` if ``name`` already exists as a tag.
    """
    if _tag_exists(project_dir, name):
        raise TagAlreadyExistsError(f"tag already exists: {name!r}")

    commit_message = message or name

    _git("add", "-A", cwd=project_dir)
    # ``--allow-empty`` covers the "nothing changed since last snapshot" case.
    _git(
        "commit",
        "--allow-empty",
        "-m",
        commit_message,
        cwd=project_dir,
    )
    _git(
        "tag",
        "-a",
        name,
        "-m",
        commit_message,
        cwd=project_dir,
    )
    sha = _git("rev-parse", "HEAD", cwd=project_dir).stdout.strip()
    return {
        "name": name,
        "sha": sha,
        "message": commit_message,
    }


# ---------------------------------------------------------------------------
# list_tags / delete_tag
# ---------------------------------------------------------------------------


_LIST_FORMAT = (
    "%(refname:short)%09%(objectname)%09%(taggerdate:iso-strict)%09%(contents:subject)"
)


def list_tags(project_dir: Path) -> list[dict[str, Any]]:
    """Return all annotated tags, newest first by tagger date.

    Each entry: ``{name, sha, ts, message}``. ``sha`` is the commit sha
    the tag points at (not the tag object's own sha), so it's the same
    sha ``tag_snapshot`` returned.
    """
    result = _git(
        "for-each-ref",
        "--sort=-taggerdate",
        f"--format={_LIST_FORMAT}",
        "refs/tags",
        cwd=project_dir,
    )
    out: list[dict[str, Any]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        # ``objectname`` on a tag ref is the tag-object sha; we want the
        # commit sha instead so it matches the sha returned by
        # ``tag_snapshot``. Resolve via rev-list.
        name = parts[0]
        ts = parts[2] if len(parts) > 2 else ""
        message = parts[3] if len(parts) > 3 else ""
        commit_sha = _git(
            "rev-list", "-n", "1", name, cwd=project_dir
        ).stdout.strip()
        out.append(
            {
                "name": name,
                "sha": commit_sha,
                "ts": ts,
                "message": message,
            }
        )
    return out


def delete_tag(project_dir: Path, name: str) -> None:
    """Drop a tag. The commit it pointed at stays reachable via reflog."""
    if not _tag_exists(project_dir, name):
        raise KeyError(name)
    _git("tag", "-d", name, cwd=project_dir)
