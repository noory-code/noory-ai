"""Per-workspace git repo for session-bookmark tags + per-node publish commits.

D-2026-06-11-C/D — the workspace is the user's opened folder, and that folder
IS the git repo. Plot never silently runs ``git init``; the first tag/publish
on a workspace without ``.git/`` raises :class:`GitNotInitializedError` and
the endpoint surfaces a structured 409 the viewer turns into a modal. Only an
explicit ``init_workspace_repo`` call (driven by the user's Yes) actually
creates the repo.

Identity for Plot-authored commits is passed **inline** (``git -c
user.name=Plot -c user.email=plot@noory-ai.local …``) so the user's
repo-level config stays untouched even when Plot initialised the repo
itself. Staging is **path-scoped to** ``.noory/plot/`` so the user's
working-tree edits outside Plot's data root are never folded into a
Plot commit.

Implementation notes
--------------------

- ``subprocess.run(["git", …])`` end-to-end — no third-party git binding,
  keeps the plugin install lean and works on any platform with git.
- The repo starts with zero commits; ``git rev-parse HEAD`` fails until
  the first ``tag_snapshot``.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class TagAlreadyExistsError(ValueError):
    """Raised when ``tag_snapshot`` is called with a name that's already taken."""


class GitNotInitializedError(Exception):
    """Raised when a git op runs on a workspace without ``.git/``.

    Endpoints catch this and respond ``409 {needs_git_init: true,
    workspace_root: …}`` so the viewer can offer to initialise the repo.
    """


# Plot-authored commits carry their identity inline so the user's repo-level
# ``user.name`` / ``user.email`` stay untouched, even on a workspace Plot
# initialised itself.
_PLOT_IDENTITY = (
    "-c", "user.name=Plot",
    "-c", "user.email=plot@noory-ai.local",
)

# Plot's tag/publish commits stage ONLY the Plot data root. The user's
# working-tree edits outside this path are never folded into a Plot commit.
_PLOT_PATHSPEC = ".noory/plot"


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


def _git_as_plot(*args: str, cwd: Path) -> _RunResult:
    """Run a git subcommand with Plot's inline identity. Used for commit/tag."""
    return _git(*_PLOT_IDENTITY, *args, cwd=cwd)


# ---------------------------------------------------------------------------
# repo lifecycle
# ---------------------------------------------------------------------------


def is_workspace_repo(workspace_root: Path) -> bool:
    """True iff ``workspace_root/.git/`` already exists."""
    return (workspace_root / ".git").is_dir()


def assert_repo_initialized(workspace_root: Path) -> None:
    """Raise :class:`GitNotInitializedError` when ``workspace_root`` has no
    ``.git/``. Endpoint code calls this before any git op that would
    otherwise fail with an inscrutable subprocess error."""
    if not is_workspace_repo(workspace_root):
        raise GitNotInitializedError(
            f"git not initialized at workspace root {workspace_root}"
        )


def init_workspace_repo(workspace_root: Path) -> bool:
    """Run ``git init`` at the workspace root. Idempotent — returns False
    when a repo already exists, True when one was newly created. Never
    writes ``.gitignore`` / ``.gitattributes`` / repo-level ``user.name`` /
    ``user.email`` (the user's territory).

    Plot calls this only in response to an explicit user "Yes" on the
    "Initialize git repo at <workspace>?" modal (D-2026-06-11-D).
    """
    if is_workspace_repo(workspace_root):
        return False
    workspace_root.mkdir(parents=True, exist_ok=True)
    _git("init", "--quiet", cwd=workspace_root)
    return True


# ---------------------------------------------------------------------------
# tag_snapshot
# ---------------------------------------------------------------------------


def _tag_exists(workspace_root: Path, name: str) -> bool:
    result = _git(
        "rev-parse",
        "--verify",
        "--quiet",
        f"refs/tags/{name}",
        cwd=workspace_root,
        check=False,
    )
    return result.returncode == 0


def tag_snapshot(workspace_root: Path, name: str, message: str | None = None) -> dict[str, Any]:
    """Snapshot the Plot data root under an annotated git tag.

    Flow:
      1. ``git add -A -- .noory/plot/`` (path-scoped: only Plot's data)
      2. ``git -c user.name=Plot … commit --allow-empty -m <message>``
         (inline identity; ``--allow-empty`` covers end-of-session tags on
         an otherwise untouched project)
      3. ``git tag -a <name> -m <message>``

    Raises:
      :class:`GitNotInitializedError` — when the workspace has no ``.git/``.
        Endpoints catch this and reply 409 ``needs_git_init=true``.
      :class:`TagAlreadyExistsError` — when ``name`` already exists.
    """
    assert_repo_initialized(workspace_root)
    if _tag_exists(workspace_root, name):
        raise TagAlreadyExistsError(f"tag already exists: {name!r}")

    commit_message = message or name

    _git("add", "-A", "--", _PLOT_PATHSPEC, cwd=workspace_root)
    # ``--allow-empty`` covers the "nothing changed since last snapshot" case.
    _git_as_plot(
        "commit",
        "--allow-empty",
        "-m",
        commit_message,
        cwd=workspace_root,
    )
    _git_as_plot(
        "tag",
        "-a",
        name,
        "-m",
        commit_message,
        cwd=workspace_root,
    )
    sha = _git("rev-parse", "HEAD", cwd=workspace_root).stdout.strip()
    return {
        "name": name,
        "sha": sha,
        "message": commit_message,
    }


# ---------------------------------------------------------------------------
# publish_snapshot — v0.18.0 Phase 3 (D-2026-05-16-E)
# ---------------------------------------------------------------------------


def publish_snapshot(
    workspace_root: Path,
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
    appended per ancestor. Empty list / None → no propagation trailers.

    Flow:
      1. ``git add -A -- .noory/plot/`` — picks up the canvas.json bump(s)
         and the new ``published/<file>.md``; user edits elsewhere stay
         out.
      2. ``git -c user.name=Plot … commit -m <subject>\\n\\n<trailers>``
         (no ``--allow-empty``; a publish must change the version field
         so an empty diff is a bug).
    """
    assert_repo_initialized(workspace_root)

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

    _git("add", "-A", "--", _PLOT_PATHSPEC, cwd=workspace_root)
    _git_as_plot("commit", "-m", message, cwd=workspace_root)
    sha = _git("rev-parse", "HEAD", cwd=workspace_root).stdout.strip()
    return {
        "sha": sha,
        "subject": subject,
        "trailers": trailers,
    }


# ---------------------------------------------------------------------------
# v0.23.x (D-2026-05-17-J) — unpublish
# ---------------------------------------------------------------------------


def ensure_clean_working_tree(workspace_root: Path) -> None:
    """Capture any pre-publish dirty state in ``.noory/plot/`` in its own commit.

    Without this, a publish that runs against an untracked / dirty Plot
    data root (e.g. the very first publish in a fresh project, or after an
    offline-edit session) would bundle unrelated Plot files into the
    publish commit. A later ``git revert`` of that publish would then wipe
    canvas.json + every other untracked Plot file, leaving the project
    broken.

    Path-scoped to ``.noory/plot/`` so the user's working-tree edits
    elsewhere stay where they are. Idempotent: no-op when the Plot data
    root is already clean. Quietly returns when the workspace has no
    ``.git/`` (caller's job to gate via the endpoint flow).
    """
    if not is_workspace_repo(workspace_root):
        return
    result = _git(
        "status", "--porcelain", "--", _PLOT_PATHSPEC,
        cwd=workspace_root, check=False,
    )
    if not result.stdout.strip():
        return
    _git("add", "-A", "--", _PLOT_PATHSPEC, cwd=workspace_root)
    _git_as_plot(
        "commit", "-m", "chore(plot): seed pre-publish state", cwd=workspace_root,
    )


def find_latest_publish_commit(workspace_root: Path, node_id: str) -> str | None:
    """Return the short sha of the most recent publish commit for a node,
    or None when the node has never been published.

    Greps the git log for the ``Publish-Node-Id: <node_id>`` trailer line.
    Most-recent-first; we take the first match.
    """
    if not is_workspace_repo(workspace_root):
        return None
    result = _git(
        "log",
        "--grep=^Publish-Node-Id: " + node_id + "$",
        "--extended-regexp",
        "-1",
        "--format=%H",
        cwd=workspace_root,
        check=False,
    )
    sha = result.stdout.strip()
    return sha or None


def revert_publish(workspace_root: Path, sha: str) -> str:
    """Revert a publish commit and return the new HEAD sha.

    ``git revert <sha> --no-edit`` creates a new commit that undoes
    the canvas.json bump(s) + the published MD file in a single step.
    Caller is responsible for verifying the commit was a publish
    (via the trailer) before invoking — this is a pure git op.
    """
    assert_repo_initialized(workspace_root)
    _git_as_plot("revert", "--no-edit", sha, cwd=workspace_root)
    return _git("rev-parse", "HEAD", cwd=workspace_root).stdout.strip()


# ---------------------------------------------------------------------------
# list_tags / delete_tag / read_file_at_tag
# ---------------------------------------------------------------------------


_LIST_FORMAT = "%(refname:short)%09%(objectname)%09%(taggerdate:iso-strict)%09%(contents:subject)"


def read_file_at_tag(workspace_root: Path, tag: str, relative_path: str) -> bytes:
    """v0.24.14 (D-2026-05-21-C) — read a file's bytes at the given tag.

    Uses ``git show <tag>:<relative_path>`` so we never touch the working
    tree (no checkout). ``relative_path`` is **repo-root-relative** (e.g.
    ``.noory/plot/{project_id}/foundation/canvas.json``).

    Raises:
        FileNotFoundError — when the tag or path doesn't exist at that tag,
          OR when the workspace has no ``.git/`` (no tags possible).
    """
    if not is_workspace_repo(workspace_root):
        raise FileNotFoundError(f"git not initialized at workspace {workspace_root}")
    if not _tag_exists(workspace_root, tag):
        raise FileNotFoundError(f"tag not found: {tag!r}")
    # git show outputs the blob to stdout; check=False so we can craft a
    # readable error when the path is missing at that tag.
    spec = f"{tag}:{relative_path}"
    result = subprocess.run(
        ["git", "show", spec],
        cwd=workspace_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise FileNotFoundError(
            f"file not at tag {tag!r}: {relative_path} "
            f"(git show {spec} exited {result.returncode})"
        )
    return result.stdout


def list_tags(workspace_root: Path) -> list[dict[str, Any]]:
    """Return all annotated tags, newest first by tagger date.

    Each entry: ``{name, sha, ts, message}``. ``sha`` is the commit sha
    the tag points at (not the tag object's own sha), so it's the same
    sha ``tag_snapshot`` returned. Returns ``[]`` when the workspace has
    no ``.git/`` (no tags possible).
    """
    if not is_workspace_repo(workspace_root):
        return []
    result = _git(
        "for-each-ref",
        "--sort=-taggerdate",
        f"--format={_LIST_FORMAT}",
        "refs/tags/",
        cwd=workspace_root,
        check=False,
    )
    tags: list[dict[str, Any]] = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 4:
            continue
        name, _tag_sha, ts, message = parts
        commit_sha = _git(
            "rev-list", "-n", "1", name, cwd=workspace_root, check=False,
        ).stdout.strip()
        tags.append(
            {
                "name": name,
                "sha": commit_sha or _tag_sha,
                "ts": ts,
                "message": message,
            }
        )
    return tags


def delete_tag(workspace_root: Path, name: str) -> None:
    """Delete an annotated tag by name.

    Raises:
        KeyError — when no such tag exists (or the workspace has no repo).
    """
    if not is_workspace_repo(workspace_root) or not _tag_exists(workspace_root, name):
        raise KeyError(name)
    _git("tag", "-d", name, cwd=workspace_root)
