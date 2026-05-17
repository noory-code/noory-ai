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


def tag_snapshot(project_dir: Path, name: str, message: str | None = None) -> dict[str, Any]:
    """Snapshot the current working tree under an annotated git tag.

    Flow:
      1. ``git add -A``
      2. ``git commit -m <message or name>`` (``--allow-empty`` so we can
         tag even when nothing changed between snapshots — end-of-session
         markers on an otherwise untouched project).
      3. ``git tag -a <name> -m <message or name>``

    Raises ``TagAlreadyExistsError`` if ``name`` already exists as a tag.
    """
    # Self-heal projects that were created before ``ensure_repo`` was wired
    # into ``create_project`` — lets old projects still plant their first tag.
    if not (project_dir / ".git").is_dir():
        ensure_repo(project_dir)

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
# publish_snapshot — v0.18.0 Phase 3 (D-2026-05-16-E)
# ---------------------------------------------------------------------------


def publish_snapshot(
    project_dir: Path,
    *,
    node_id: str,
    kind: str,
    canvas: str,
    label: str,
    from_v: str,
    to_v: str,
    propagated: list[tuple[str, str, str]] | None = None,
) -> dict[str, Any]:
    """Snapshot a per-node publish as a git commit with machine-readable
    ``Publish-*:`` trailers.

    Five base trailers (``Publish-Node-Id`` / ``Publish-Kind`` /
    ``Publish-Canvas`` / ``Publish-Version-From`` / ``Publish-Version-To``)
    describe the user-driven MAJOR bump.

    ``propagated`` carries Phase 4 (D-2026-05-17-C) MINOR propagation
    records as ``(ancestor_id, from_v, to_v)`` tuples; one
    ``Publish-Propagated-Ancestor: <id> <from>→<to>`` trailer is
    appended per ancestor. Empty list / None → no propagation trailers
    (the publish target had no parent chain to bump).

    Flow:
      1. ``git add -A`` — picks up the canvas.json bump(s) and the new
         ``published/<file>.md``.
      2. ``git commit -m <subject>\\n\\n<trailers>`` — no
         ``--allow-empty``; a publish must change the version field
         so an empty diff is a bug.

    Returns ``{sha, subject, trailers}``. ``trailers`` is a dict for
    the 5 base trailers; propagation trailers (which can repeat the
    same key) are not surfaced in the returned dict — read the commit
    via ``git interpret-trailers`` instead.
    """
    if not (project_dir / ".git").is_dir():
        ensure_repo(project_dir)

    subject = f'publish: {kind} "{label}" → {to_v}'
    trailers = {
        "Publish-Node-Id": node_id,
        "Publish-Kind": kind,
        "Publish-Canvas": canvas,
        "Publish-Version-From": from_v,
        "Publish-Version-To": to_v,
    }
    lines = [f"{k}: {v}" for k, v in trailers.items()]
    for ancestor_id, anc_from, anc_to in propagated or []:
        lines.append(f"Publish-Propagated-Ancestor: {ancestor_id} {anc_from}→{anc_to}")
    body = "\n".join(lines)
    message = f"{subject}\n\n{body}"

    _git("add", "-A", cwd=project_dir)
    _git("commit", "-m", message, cwd=project_dir)
    sha = _git("rev-parse", "HEAD", cwd=project_dir).stdout.strip()
    return {
        "sha": sha,
        "subject": subject,
        "trailers": trailers,
    }


# ---------------------------------------------------------------------------
# v0.23.x (D-2026-05-17-J) — unpublish
# ---------------------------------------------------------------------------


def ensure_clean_working_tree(project_dir: Path) -> None:
    """Capture any pre-publish dirty state in its own commit.

    Without this, a publish that runs against an untracked / dirty
    working tree (e.g. the very first publish in a fresh project, or
    after an offline-edit session) would bundle unrelated files into
    the publish commit. A later ``git revert`` of that publish would
    then wipe canvas.json + every other untracked file, leaving the
    project broken.

    Idempotent: no-op when the working tree is already clean.
    """
    if not (project_dir / ".git").is_dir():
        return
    result = _git("status", "--porcelain", cwd=project_dir, check=False)
    if not result.stdout.strip():
        return
    _git("add", "-A", cwd=project_dir)
    _git("commit", "-m", "chore(plot): seed pre-publish state", cwd=project_dir)


def find_latest_publish_commit(project_dir: Path, node_id: str) -> str | None:
    """Return the short sha of the most recent publish commit for a node,
    or None when the node has never been published.

    Greps the git log for the ``Publish-Node-Id: <node_id>`` trailer line.
    Most-recent-first; we take the first match.
    """
    if not (project_dir / ".git").is_dir():
        return None
    result = _git(
        "log",
        "--grep=^Publish-Node-Id: " + node_id + "$",
        "--extended-regexp",
        "-1",
        "--format=%H",
        cwd=project_dir,
        check=False,
    )
    sha = result.stdout.strip()
    return sha or None


def revert_publish(project_dir: Path, sha: str) -> str:
    """Revert a publish commit and return the new HEAD sha.

    ``git revert <sha> --no-edit`` creates a new commit that undoes
    the canvas.json bump(s) + the published MD file in a single step.
    Caller is responsible for verifying the commit was a publish
    (via the trailer) before invoking — this is a pure git op.
    """
    _git("revert", "--no-edit", sha, cwd=project_dir)
    return _git("rev-parse", "HEAD", cwd=project_dir).stdout.strip()


# ---------------------------------------------------------------------------
# list_tags / delete_tag
# ---------------------------------------------------------------------------


_LIST_FORMAT = "%(refname:short)%09%(objectname)%09%(taggerdate:iso-strict)%09%(contents:subject)"


def list_tags(project_dir: Path) -> list[dict[str, Any]]:
    """Return all annotated tags, newest first by tagger date.

    Each entry: ``{name, sha, ts, message}``. ``sha`` is the commit sha
    the tag points at (not the tag object's own sha), so it's the same
    sha ``tag_snapshot`` returned.

    Returns ``[]`` if the project has no git repo yet (e.g. folder was
    created by an old backend before ``ensure_repo`` was wired in, or
    the user deleted ``.git/`` by hand).
    """
    if not (project_dir / ".git").is_dir():
        return []
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
        commit_sha = _git("rev-list", "-n", "1", name, cwd=project_dir).stdout.strip()
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
